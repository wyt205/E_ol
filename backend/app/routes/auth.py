"""
认证相关路由
提供登录、注册、登出、获取当前用户信息、更新个人信息等接口
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
import time
from app.database import get_db
from app.models import User

# 创建路由器
router = APIRouter(
    prefix="/api/auth",
    tags=["auth"]
)


# ===== 请求体格式定义 =====
class LoginRequest(BaseModel):
    """登录请求体（使用邮箱 + 密码）"""
    email: str      # 邮箱（作为登录账号）
    password: str   # 密码


class RegisterRequest(BaseModel):
    """注册请求体"""
    nickname: str   # 昵称
    email: str      # 邮箱（作为登录账号）
    password: str   # 密码


@router.post("/login")
def login(body: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """
    用户登录接口
    验证邮箱和密码，返回用户信息（不含密码）
    """
    # 1. 根据邮箱查找用户是否存在
    user = db.query(User).filter(User.email == body.email).first()
    if not user:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    # 2. 验证密码是否正确
    if user.password != body.password:
        raise HTTPException(status_code=401, detail="邮箱或密码错误")

    # 3. 检查账号状态
    if user.status != "active":
        raise HTTPException(status_code=403, detail="账号已被禁用，请联系管理员")

    # 4. 返回用户信息（to_dict 已排除密码字段）
    return {
        "message": "登录成功",
        "user": user.to_dict()
    }


@router.post("/register")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """
    用户注册接口
    使用昵称、邮箱、密码注册新账号，邮箱作为登录账号
    """
    # 1. 校验邮箱格式（简单校验）
    if "@" not in body.email or "." not in body.email:
        raise HTTPException(status_code=400, detail="邮箱格式不正确")

    # 2. 校验密码长度
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="密码长度不能少于6位")

    # 3. 校验昵称不能为空
    if not body.nickname.strip():
        raise HTTPException(status_code=400, detail="昵称不能为空")

    # 4. 检查邮箱是否已被注册
    existing_user = db.query(User).filter(User.email == body.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="该邮箱已被注册")

    # 5. 自动生成唯一用户名（格式：user_时间戳）
    auto_username = f"user_{int(time.time())}"

    # 6. 创建新用户并写入数据库
    new_user = User(
        username=auto_username,
        password=body.password,
        nickname=body.nickname.strip(),
        email=body.email.strip(),
        role="user",
        status="active"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 7. 返回注册成功的用户信息（不含密码）
    return {
        "message": "注册成功",
        "user": new_user.to_dict()
    }


class ProfileUpdate(BaseModel):
    """更新个人信息请求体（仅支持昵称和密码修改）"""
    nickname: Optional[str] = None      # 昵称
    password: Optional[str] = None      # 新密码


@router.get("/me")
def get_current_user(username: str, db: Session = Depends(get_db)):
    """
    获取当前用户信息
    前端通过 localStorage 中保存的 username 来查询
    """
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user.to_dict()


@router.put("/profile/{user_id}")
def update_profile(user_id: int, body: ProfileUpdate, db: Session = Depends(get_db)):
    """
    更新个人信息
    用户仅可修改自己的昵称和密码（邮箱不可修改）
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 仅更新昵称和密码
    if body.nickname is not None:
        user.nickname = body.nickname
    if body.password is not None and body.password.strip():
        user.password = body.password

    db.commit()
    db.refresh(user)
    return user.to_dict()

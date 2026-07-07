"""
用户管理路由
提供用户的增删改查接口（仅管理员可用）
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import User

# 创建路由器
router = APIRouter(
    prefix="/api/management/users",
    tags=["users"]
)


# ===== 请求体格式定义 =====
class UserCreate(BaseModel):
    """创建用户的请求体"""
    username: str       # 登录用户名
    password: str       # 密码
    nickname: str = ""  # 昵称
    email: str = ""     # 邮箱（可用于登录）
    role: str = "user"  # 角色：admin/user


class UserUpdate(BaseModel):
    """更新用户的请求体（所有字段可选）"""
    nickname: Optional[str] = None      # 昵称
    password: Optional[str] = None      # 密码
    role: Optional[str] = None          # 角色
    status: Optional[str] = None        # 状态
    email: Optional[str] = None         # 邮箱


# ========== 用户列表 ==========
@router.get("")
def get_all_users(db: Session = Depends(get_db)):
    """
    获取所有用户列表
    返回用户信息（不含密码）
    """
    users = db.query(User).order_by(User.id.asc()).all()
    return [u.to_dict() for u in users]


# ========== 创建用户 ==========
@router.post("")
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户
    """
    # 检查用户名是否已存在
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="用户名已存在")

    # 校验角色值
    if body.role not in ("admin", "user"):
        raise HTTPException(status_code=400, detail="角色只能是 admin 或 user")

    # 创建用户并保存到数据库（含邮箱字段）
    new_user = User(
        username=body.username,
        password=body.password,
        nickname=body.nickname or "",
        email=body.email or "",
        role=body.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user.to_dict()


# ========== 更新用户 ==========
@router.put("/{user_id}")
def update_user(user_id: int, body: UserUpdate, db: Session = Depends(get_db)):
    """
    更新用户信息
    可修改：昵称、密码、角色、状态、邮箱
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 逐字段更新（只更新非 None 的字段）
    if body.nickname is not None:
        user.nickname = body.nickname
    if body.password is not None:
        user.password = body.password
    if body.role is not None:
        if body.role not in ("admin", "user"):
            raise HTTPException(status_code=400, detail="角色只能是 admin 或 user")
        user.role = body.role
    if body.status is not None:
        if body.status not in ("active", "disabled"):
            raise HTTPException(status_code=400, detail="状态只能是 active 或 disabled")
        user.status = body.status
    if body.email is not None:
        user.email = body.email

    db.commit()
    db.refresh(user)
    return user.to_dict()


# ========== 删除用户 ==========
@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    删除用户
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不允许删除自己（防止管理员误删自己）
    if user.role == "admin":
        # 检查是否只有一个管理员
        admin_count = db.query(User).filter(User.role == "admin").count()
        if admin_count <= 1:
            raise HTTPException(status_code=400, detail="系统至少需要保留一个管理员账号")

    db.delete(user)
    db.commit()
    return {"message": f"用户 '{user.username}' 已删除"}

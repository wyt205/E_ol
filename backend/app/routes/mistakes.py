"""
错题本相关的路由（API 接口）
提供用户错题本的功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Mistake, Word

# 创建路由器
router = APIRouter(
    prefix="/api/mistakes",
    tags=["mistakes"]
)


# ===== 请求体数据格式定义 =====
class AddMistakeRequest(BaseModel):
    """添加错题请求"""
    user_id: int    # 用户ID
    word_id: int    # 单词ID


class UpdateMistakeRequest(BaseModel):
    """更新错题计数请求"""
    user_id: int    # 用户ID
    word_id: int    # 单词ID


@router.post("/add")
def add_mistake(req: AddMistakeRequest, db: Session = Depends(get_db)):
    """
    添加错题或增加错误次数
    
    如果单词已在错题本中，则错误次数+1
    如果单词不在错题本中，则添加新记录（次数为1）
    
    参数：
    - user_id: 用户ID
    - word_id: 单词ID
    
    返回：
    - mistake_count: 当前错误次数
    - message: 操作提示信息
    """
    # 检查单词是否存在
    word = db.query(Word).filter(Word.id == req.word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="单词不存在")
    
    # 查找是否已有错题记录
    mistake = db.query(Mistake).filter(
        Mistake.user_id == req.user_id,
        Mistake.word_id == req.word_id
    ).first()
    
    if mistake:
        # 已有记录，错误次数+1
        mistake.mistake_count += 1
        db.commit()
        db.refresh(mistake)
        return {"mistake_count": mistake.mistake_count, "message": "错误次数+1"}
    else:
        # 新记录，添加错题
        new_mistake = Mistake(user_id=req.user_id, word_id=req.word_id, mistake_count=1)
        db.add(new_mistake)
        db.commit()
        db.refresh(new_mistake)
        return {"mistake_count": 1, "message": "已添加到错题本"}


@router.post("/reduce")
def reduce_mistake(req: UpdateMistakeRequest, db: Session = Depends(get_db)):
    """
    减少错误次数
    
    如果错误次数减到0，则自动删除该错题记录
    
    参数：
    - user_id: 用户ID
    - word_id: 单词ID
    
    返回：
    - mistake_count: 当前错误次数（0表示已删除）
    - is_removed: 是否已从错题本中移除
    - message: 操作提示信息
    """
    # 查找错题记录
    mistake = db.query(Mistake).filter(
        Mistake.user_id == req.user_id,
        Mistake.word_id == req.word_id
    ).first()
    
    if not mistake:
        # 没有记录，直接返回
        return {"mistake_count": 0, "is_removed": True, "message": "该单词不在错题本中"}
    
    # 错误次数-1
    mistake.mistake_count -= 1
    
    if mistake.mistake_count <= 0:
        # 次数归零，删除记录
        db.delete(mistake)
        db.commit()
        return {"mistake_count": 0, "is_removed": True, "message": "已掌握，自动移出错题本"}
    else:
        # 更新记录
        db.commit()
        db.refresh(mistake)
        return {"mistake_count": mistake.mistake_count, "is_removed": False, "message": f"错误次数-1，剩余{mistake.mistake_count}次"}


@router.get("/list/{user_id}")
def get_user_mistakes(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户的错题本列表
    
    参数：
    - user_id: 用户ID
    
    返回：
    - 错题列表（包含单词详细信息和错误次数）
    """
    # 联表查询：获取用户的所有错题
    mistakes = db.query(Mistake).filter(Mistake.user_id == user_id).order_by(Mistake.updated_at.desc()).all()
    
    result = []
    for m in mistakes:
        word = db.query(Word).filter(Word.id == m.word_id).first()
        if word:
            word_dict = word.to_dict()
            word_dict["mistake_count"] = m.mistake_count
            word_dict["first_mistake_at"] = m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else None
            word_dict["last_mistake_at"] = m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else None
            result.append(word_dict)
    
    return {"mistakes": result, "total": len(result)}


@router.delete("/{mistake_id}")
def delete_mistake(mistake_id: int, db: Session = Depends(get_db)):
    """
    删除指定的错题记录
    
    参数：
    - mistake_id: 错题记录ID
    
    返回：
    - message: 删除成功提示
    """
    mistake = db.query(Mistake).filter(Mistake.id == mistake_id).first()
    if not mistake:
        raise HTTPException(status_code=404, detail="错题记录不存在")
    
    db.delete(mistake)
    db.commit()
    return {"message": "删除错题成功"}


@router.post("/remove")
def remove_mistake(req: UpdateMistakeRequest, db: Session = Depends(get_db)):
    """
    移除错题（手动删除）
    
    参数：
    - user_id: 用户ID
    - word_id: 单词ID
    
    返回：
    - message: 操作提示信息
    """
    mistake = db.query(Mistake).filter(
        Mistake.user_id == req.user_id,
        Mistake.word_id == req.word_id
    ).first()
    
    if not mistake:
        return {"message": "该单词不在错题本中"}
    
    db.delete(mistake)
    db.commit()
    return {"message": "已从错题本中移除"}
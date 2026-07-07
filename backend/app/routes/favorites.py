"""
收藏相关的路由（API 接口）
提供用户收藏单词的功能
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.database import get_db
from app.models import Favorite, Word

# 创建路由器
router = APIRouter(
    prefix="/api/favorites",
    tags=["favorites"]
)


# ===== 请求体数据格式定义 =====
class ToggleFavoriteRequest(BaseModel):
    """收藏/取消收藏请求"""
    user_id: int    # 用户ID
    word_id: int    # 单词ID


class CheckFavoriteRequest(BaseModel):
    """检查收藏状态请求"""
    user_id: int    # 用户ID
    word_id: int    # 单词ID


@router.post("/toggle")
def toggle_favorite(req: ToggleFavoriteRequest, db: Session = Depends(get_db)):
    """
    收藏/取消收藏单词
    
    如果单词已收藏则取消收藏，如果未收藏则添加收藏
    
    参数：
    - user_id: 用户ID
    - word_id: 单词ID
    
    返回：
    - is_favorited: 操作后的收藏状态（True=已收藏，False=未收藏）
    - message: 操作提示信息
    """
    # 检查单词是否存在
    word = db.query(Word).filter(Word.id == req.word_id).first()
    if not word:
        raise HTTPException(status_code=404, detail="单词不存在")
    
    # 查找是否已收藏
    favorite = db.query(Favorite).filter(
        Favorite.user_id == req.user_id,
        Favorite.word_id == req.word_id
    ).first()
    
    if favorite:
        # 已收藏，执行取消收藏
        db.delete(favorite)
        db.commit()
        return {"is_favorited": False, "message": "已取消收藏"}
    else:
        # 未收藏，执行收藏
        new_favorite = Favorite(user_id=req.user_id, word_id=req.word_id)
        db.add(new_favorite)
        db.commit()
        db.refresh(new_favorite)
        return {"is_favorited": True, "message": "收藏成功"}


@router.post("/check")
def check_favorite(req: CheckFavoriteRequest, db: Session = Depends(get_db)):
    """
    检查单词是否已被收藏
    
    参数：
    - user_id: 用户ID
    - word_id: 单词ID
    
    返回：
    - is_favorited: 是否已收藏（True/False）
    """
    favorite = db.query(Favorite).filter(
        Favorite.user_id == req.user_id,
        Favorite.word_id == req.word_id
    ).first()
    
    return {"is_favorited": favorite is not None}


@router.get("/list/{user_id}")
def get_user_favorites(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户的收藏列表
    
    参数：
    - user_id: 用户ID
    
    返回：
    - 收藏的单词列表（包含单词详细信息）
    """
    # 联表查询：获取用户收藏的所有单词
    favorites = db.query(Favorite).filter(Favorite.user_id == user_id).order_by(Favorite.created_at.desc()).all()
    
    result = []
    for fav in favorites:
        word = db.query(Word).filter(Word.id == fav.word_id).first()
        if word:
            word_dict = word.to_dict()
            word_dict["favorited_at"] = fav.created_at.strftime("%Y-%m-%d %H:%M:%S") if fav.created_at else None
            result.append(word_dict)
    
    return {"favorites": result, "total": len(result)}


@router.delete("/{favorite_id}")
def delete_favorite(favorite_id: int, db: Session = Depends(get_db)):
    """
    删除指定的收藏记录
    
    参数：
    - favorite_id: 收藏记录ID
    
    返回：
    - message: 删除成功提示
    """
    favorite = db.query(Favorite).filter(Favorite.id == favorite_id).first()
    if not favorite:
        raise HTTPException(status_code=404, detail="收藏记录不存在")
    
    db.delete(favorite)
    db.commit()
    return {"message": "删除收藏成功"}
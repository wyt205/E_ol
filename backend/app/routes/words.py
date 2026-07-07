"""
单词相关的路由（API 接口）
这里定义了前端可以调用的所有单词相关的接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models import Word

# 创建路由路由器
router = APIRouter(
    prefix="/api/words",  # 所有路由都以 /api/words 开头
    tags=["words"]  # 在 API 文档中的标签
)

@router.get("/current")
def get_current_word(db: Session = Depends(get_db)):
    """
    获取当前要显示的单词（默认第一个单词）
    
    这个接口返回数据库中的第一个单词
    前端可以通过这个接口获取初始显示的单词
    """
    word = db.query(Word).order_by(Word.id.asc()).first()
    
    if not word:
        raise HTTPException(status_code=404, detail="没有找到单词")
    
    return word.to_dict()

@router.get("/count")
def get_word_count(db: Session = Depends(get_db)):
    """
    获取单词总数
    
    返回：
    - 数据库中单词的总数量
    """
    count = db.query(Word).count()
    return {"total": count}

@router.get("/first-last")
def get_first_and_last_word(db: Session = Depends(get_db)):
    """
    获取第一个和最后一个单词的 ID
    
    用于前端判断按钮是否应该禁用
    """
    first_word = db.query(Word).order_by(Word.id.asc()).first()
    last_word = db.query(Word).order_by(Word.id.desc()).first()
    
    if not first_word or not last_word:
        raise HTTPException(status_code=404, detail="没有找到单词")
    
    return {
        "first_id": first_word.id,
        "last_id": last_word.id
    }

@router.get("/next/{current_id}")
def get_next_word(current_id: int, db: Session = Depends(get_db)):
    """
    获取下一个单词（ID 更大的单词）
    
    参数：
    - current_id: 当前单词的 ID
    
    返回：
    - 下一个单词的信息，如果没有则返回 None
    """
    next_word = db.query(Word).filter(Word.id > current_id).order_by(Word.id.asc()).first()
    
    if not next_word:
        return None
    
    return next_word.to_dict()

@router.get("/prev/{current_id}")
def get_prev_word(current_id: int, db: Session = Depends(get_db)):
    """
    获取上一个单词（ID 更小的单词）
    
    参数：
    - current_id: 当前单词的 ID
    
    返回：
    - 上一个单词的信息，如果没有则返回 None
    """
    prev_word = db.query(Word).filter(Word.id < current_id).order_by(Word.id.desc()).first()
    
    if not prev_word:
        return None
    
    return prev_word.to_dict()

@router.get("/random")
def get_random_word(exclude: str = Query(default="", description="排除的单词ID，逗号分隔"), db: Session = Depends(get_db)):
    """
    随机获取一个单词
    
    参数：
    - exclude: 需要排除的单词ID列表（逗号分隔），用于排除已刷过的单词
    
    返回数据库中随机选择的一个单词信息（排除指定ID）
    """
    query = db.query(Word)
    
    if exclude:
        try:
            exclude_ids = [int(id.strip()) for id in exclude.split(",") if id.strip()]
            if exclude_ids:
                query = query.filter(~Word.id.in_(exclude_ids))
        except ValueError:
            pass
    
    word = query.order_by(func.rand()).first()
    
    if not word:
        raise HTTPException(status_code=404, detail="没有找到未刷过的单词")
    
    return word.to_dict()

@router.get("/random/seen")
def get_random_seen_word(seen: str = Query(default="", description="已刷过的单词ID，逗号分隔"), db: Session = Depends(get_db)):
    """
    从已刷过的单词中随机获取一个
    
    参数：
    - seen: 已刷过的单词ID列表（逗号分隔）
    
    返回已刷单词中随机选择的一个
    """
    if not seen:
        raise HTTPException(status_code=400, detail="没有已刷过的单词")
    
    try:
        seen_ids = [int(id.strip()) for id in seen.split(",") if id.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="ID格式错误")
    
    if not seen_ids:
        raise HTTPException(status_code=400, detail="没有已刷过的单词")
    
    word = db.query(Word).filter(Word.id.in_(seen_ids)).order_by(func.rand()).first()
    
    if not word:
        raise HTTPException(status_code=404, detail="没有找到单词")
    
    return word.to_dict()

@router.get("/{word_id}")
def get_word_by_id(word_id: int, db: Session = Depends(get_db)):
    """
    根据 ID 获取指定单词
    
    参数：
    - word_id: 单词的 ID
    
    返回：
    - 单词的详细信息
    """
    word = db.query(Word).filter(Word.id == word_id).first()
    
    if not word:
        raise HTTPException(status_code=404, detail=f"未找到 ID 为 {word_id} 的单词")
    
    return word.to_dict()

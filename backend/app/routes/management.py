"""
管理端 API 路由
提供单词表和单词的增删改查接口
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Word, WordList

# 创建路由
router = APIRouter(
    prefix="/api/management",
    tags=["management"]
)


# ========== Pydantic 请求体模型 ==========

class WordListCreate(BaseModel):
    """创建词表的请求体"""
    name: str
    description: Optional[str] = ""


class WordListUpdate(BaseModel):
    """更新词表的请求体"""
    name: Optional[str] = None
    description: Optional[str] = None


class WordCreate(BaseModel):
    """创建单词的请求体"""
    list_id: int
    word: str
    phonetic: Optional[str] = ""
    meaning: str
    example: Optional[str] = ""
    example_translation: Optional[str] = ""


class WordUpdate(BaseModel):
    """更新单词的请求体"""
    word: Optional[str] = None
    phonetic: Optional[str] = None
    meaning: Optional[str] = None
    example: Optional[str] = None
    example_translation: Optional[str] = None


# ========== 词表相关接口 ==========

@router.get("/lists")
def get_all_lists(db: Session = Depends(get_db)):
    """
    获取所有单词表
    返回词表列表，每个词表附带单词数量
    """
    lists = db.query(WordList).order_by(WordList.id.asc()).all()
    result = []
    for wl in lists:
        data = wl.to_dict()
        data["word_count"] = db.query(Word).filter(Word.list_id == wl.id).count()
        result.append(data)
    return result


@router.post("/lists")
def create_list(body: WordListCreate, db: Session = Depends(get_db)):
    """
    创建新词表
    """
    # 检查名称是否重复
    existing = db.query(WordList).filter(WordList.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="词表名称已存在")

    new_list = WordList(name=body.name, description=body.description or "")
    db.add(new_list)
    db.commit()
    db.refresh(new_list)

    result = new_list.to_dict()
    result["word_count"] = 0
    return result


@router.put("/lists/{list_id}")
def update_list(list_id: int, body: WordListUpdate, db: Session = Depends(get_db)):
    """
    更新词表信息
    """
    wl = db.query(WordList).filter(WordList.id == list_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="词表不存在")

    if body.name is not None:
        # 检查新名称是否与其他词表重复
        dup = db.query(WordList).filter(WordList.name == body.name, WordList.id != list_id).first()
        if dup:
            raise HTTPException(status_code=400, detail="词表名称已存在")
        wl.name = body.name
    if body.description is not None:
        wl.description = body.description

    db.commit()
    db.refresh(wl)

    result = wl.to_dict()
    result["word_count"] = db.query(Word).filter(Word.list_id == wl.id).count()
    return result


@router.delete("/lists/{list_id}")
def delete_list(list_id: int, db: Session = Depends(get_db)):
    """
    删除词表（同时删除该词表下的所有单词）
    """
    wl = db.query(WordList).filter(WordList.id == list_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="词表不存在")

    # 先删除该词表下的所有单词
    db.query(Word).filter(Word.list_id == list_id).delete()
    db.delete(wl)
    db.commit()
    return {"message": f"词表 '{wl.name}' 已删除"}


# ========== 单词相关接口 ==========

@router.get("/lists/{list_id}/words")
def get_words_by_list(list_id: int, db: Session = Depends(get_db)):
    """
    获取指定词表下的所有单词
    """
    wl = db.query(WordList).filter(WordList.id == list_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="词表不存在")

    words = db.query(Word).filter(Word.list_id == list_id).order_by(Word.id.asc()).all()
    return [w.to_dict() for w in words]


@router.post("/words")
def create_word(body: WordCreate, db: Session = Depends(get_db)):
    """
    在指定词表下添加新单词
    """
    # 检查词表是否存在
    wl = db.query(WordList).filter(WordList.id == body.list_id).first()
    if not wl:
        raise HTTPException(status_code=404, detail="词表不存在")

    new_word = Word(
        list_id=body.list_id,
        word=body.word,
        phonetic=body.phonetic or "",
        meaning=body.meaning,
        example=body.example or "",
        example_translation=body.example_translation or ""
    )
    db.add(new_word)
    db.commit()
    db.refresh(new_word)
    return new_word.to_dict()


@router.put("/words/{word_id}")
def update_word(word_id: int, body: WordUpdate, db: Session = Depends(get_db)):
    """
    更新单词信息
    """
    w = db.query(Word).filter(Word.id == word_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="单词不存在")

    if body.word is not None:
        w.word = body.word
    if body.phonetic is not None:
        w.phonetic = body.phonetic
    if body.meaning is not None:
        w.meaning = body.meaning
    if body.example is not None:
        w.example = body.example
    if body.example_translation is not None:
        w.example_translation = body.example_translation

    db.commit()
    db.refresh(w)
    return w.to_dict()


@router.delete("/words/{word_id}")
def delete_word(word_id: int, db: Session = Depends(get_db)):
    """
    删除指定单词
    """
    w = db.query(Word).filter(Word.id == word_id).first()
    if not w:
        raise HTTPException(status_code=404, detail="单词不存在")

    db.delete(w)
    db.commit()
    return {"message": f"单词 '{w.word}' 已删除"}


@router.post("/words/batch")
def batch_create_words(words: list[WordCreate], db: Session = Depends(get_db)):
    """
    批量添加单词
    """
    if not words:
        raise HTTPException(status_code=400, detail="单词列表不能为空")

    created = []
    for body in words:
        wl = db.query(WordList).filter(WordList.id == body.list_id).first()
        if not wl:
            raise HTTPException(status_code=404, detail=f"词表 ID {body.list_id} 不存在")

        new_word = Word(
            list_id=body.list_id,
            word=body.word,
            phonetic=body.phonetic or "",
            meaning=body.meaning,
            example=body.example or "",
            example_translation=body.example_translation or ""
        )
        db.add(new_word)
        created.append(new_word)

    db.commit()
    for w in created:
        db.refresh(w)
    return [w.to_dict() for w in created]

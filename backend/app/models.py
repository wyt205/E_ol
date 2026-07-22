"""
数据模型定义
这里定义了与数据库表对应的 Python 类
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    用户模型类
    对应数据库中的 users 表
    包含管理员和普通用户
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), nullable=False, unique=True, comment="登录用户名")
    password = Column(String(255), nullable=False, comment="登录密码")
    nickname = Column(String(100), default="", comment="用户昵称")
    role = Column(String(20), nullable=False, default="user", comment="角色：admin/user")
    status = Column(String(20), nullable=False, default="active", comment="状态：active/disabled")
    avatar = Column(String(500), default="", comment="头像URL")
    email = Column(String(100), default="", comment="邮箱")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")

    def to_dict(self):
        """将模型对象转换为字典（不包含密码）"""
        return {
            "id": self.id,
            "username": self.username,
            "nickname": self.nickname,
            "role": self.role,
            "status": self.status,
            "avatar": self.avatar,
            "email": self.email,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }


class WordList(Base):
    """
    单词表模型类
    对应数据库中的 word_lists 表
    每个单词表可以包含多个单词
    """
    __tablename__ = "word_lists"

    id = Column(Integer, primary_key=True, index=True, comment="词表ID")
    name = Column(String(100), nullable=False, unique=True, comment="词表名称")
    description = Column(String(500), comment="词表描述")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def to_dict(self):
        """将模型对象转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class Word(Base):
    """
    单词模型类
    对应数据库中的 words 表
    """
    __tablename__ = "words"  # 指定对应的数据库表名

    id = Column(Integer, primary_key=True, index=True, comment="单词ID")
    list_id = Column(Integer, ForeignKey("word_lists.id"), nullable=False, default=1, comment="所属词表ID")
    word = Column(String(100), nullable=False, comment="单词")
    phonetic_uk = Column(String(100), comment="UK音标")
    phonetic_us = Column(String(100), comment="US音标")
    audio_url_uk = Column(String(500), comment="UK语音URL")
    audio_url_us = Column(String(500), comment="US语音URL")
    meaning = Column(Text, nullable=False, comment="释义")
    example = Column(Text, comment="例句")
    example_translation = Column(Text, comment="例句翻译")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")

    def to_dict(self):
        """将模型对象转换为字典，方便返回给前端"""
        return {
            "id": self.id,
            "list_id": self.list_id,
            "word": self.word,
            "phonetic_uk": self.phonetic_uk,
            "phonetic_us": self.phonetic_us,
            "audio_url_uk": self.audio_url_uk,
            "audio_url_us": self.audio_url_us,
            "meaning": self.meaning,
            "example": self.example,
            "example_translation": self.example_translation,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class Favorite(Base):
    """
    用户收藏模型类
    对应数据库中的 favorites 表
    记录用户收藏的单词
    """
    __tablename__ = "favorites"
    
    # 联合唯一约束：同一用户不能重复收藏同一单词
    __table_args__ = (
        UniqueConstraint('user_id', 'word_id', name='unique_user_word_favorite'),
    )

    id = Column(Integer, primary_key=True, index=True, comment="收藏ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    word_id = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False, comment="单词ID")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="收藏时间")

    def to_dict(self):
        """将模型对象转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "word_id": self.word_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None
        }


class Mistake(Base):
    """
    用户错题本模型类
    对应数据库中的 mistakes 表
    记录用户的错题及错误次数
    """
    __tablename__ = "mistakes"
    
    # 联合唯一约束：同一用户不能重复记录同一单词
    __table_args__ = (
        UniqueConstraint('user_id', 'word_id', name='unique_user_word_mistake'),
    )

    id = Column(Integer, primary_key=True, index=True, comment="错题ID")
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, comment="用户ID")
    word_id = Column(Integer, ForeignKey("words.id", ondelete="CASCADE"), nullable=False, comment="单词ID")
    mistake_count = Column(Integer, default=1, nullable=False, comment="错误次数")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="首次错误时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="最后错误时间")

    def to_dict(self):
        """将模型对象转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "word_id": self.word_id,
            "mistake_count": self.mistake_count,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else None,
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else None
        }

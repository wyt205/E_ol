"""
数据库配置模块
使用 SQLAlchemy ORM 连接 MySQL 数据库
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接配置
# 格式：mysql+pymysql://用户名:密码@主机:端口/数据库名
DATABASE_URL = "mysql+pymysql://root:root@localhost:3306/word_learning"

# 创建数据库引擎
# engine 是 SQLAlchemy 的核心，负责管理数据库连接
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # 自动检测并重新连接断开的连接
    pool_recycle=3600,   # 连接回收时间（秒）
)

# 创建会话工厂
# SessionLocal 用于创建数据库会话，每个请求都会使用一个新的会话
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
# Base 是所有模型类的父类，提供 ORM 功能
Base = declarative_base()

def get_db():
    """
    获取数据库会话的依赖函数
    这个函数会被 FastAPI 的依赖注入系统调用
    确保每个请求结束后都关闭数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

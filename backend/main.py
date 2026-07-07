"""
FastAPI 主应用
这是整个后端的入口文件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import text
from app.database import engine, Base
from app.routes import words, management, ai, auth, users, favorites, mistakes  # 导入所有路由

# 创建数据库表（如果不存在）
# 注意：需要先导入 models 以确保所有模型都被注册到 Base.metadata
from app import models  # noqa: F401
Base.metadata.create_all(bind=engine)


# ===== 自动迁移：为已有数据库添加新表和字段 =====
def auto_migrate():
    """
    自动迁移逻辑：
    1. 创建 word_lists 表（如果不存在）
    2. 给 words 表添加 list_id 字段（如果不存在）
    3. 插入默认词表（如果不存在）
    """
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        # 检查 word_lists 表是否存在
        result = db.execute(text("SHOW TABLES LIKE 'word_lists'"))
        if not result.fetchone():
            db.execute(text("""
                CREATE TABLE word_lists (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL UNIQUE,
                    description VARCHAR(500) DEFAULT '',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """))
            db.commit()
            print("[迁移] 已创建 word_lists 表")

        # 确保默认词表存在
        result = db.execute(text("SELECT id FROM word_lists WHERE name = '默认词表'"))
        if not result.fetchone():
            db.execute(text("INSERT INTO word_lists (name, description) VALUES ('默认词表', '系统默认单词表')"))
            db.commit()
            print("[迁移] 已插入默认词表")

        # 检查 words 表是否有 list_id 字段
        result = db.execute(text("SHOW COLUMNS FROM words LIKE 'list_id'"))
        if not result.fetchone():
            db.execute(text("ALTER TABLE words ADD COLUMN list_id INT NOT NULL DEFAULT 1 AFTER id"))
            db.commit()
            print("[迁移] 已给 words 表添加 list_id 字段")

        # 检查 words 表是否有 example_translation 字段
        result = db.execute(text("SHOW COLUMNS FROM words LIKE 'example_translation'"))
        if not result.fetchone():
            db.execute(text("ALTER TABLE words ADD COLUMN example_translation TEXT AFTER example"))
            db.commit()
            print("[迁移] 已给 words 表添加 example_translation 字段")

        # 检查 words 表是否有 list_id 外键
        result = db.execute(text("""
            SELECT CONSTRAINT_NAME FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = 'word_learning' AND TABLE_NAME = 'words'
            AND COLUMN_NAME = 'list_id' AND REFERENCED_TABLE_NAME = 'word_lists'
        """))
        if not result.fetchone():
            try:
                db.execute(text("ALTER TABLE words ADD FOREIGN KEY (list_id) REFERENCES word_lists(id) ON DELETE CASCADE"))
                db.commit()
                print("[迁移] 已给 words 表添加 list_id 外键")
            except Exception as fk_err:
                print(f"[迁移] 添加外键失败（可忽略）: {fk_err}")

        # ===== 用户表迁移 =====
        result = db.execute(text("SHOW TABLES LIKE 'users'"))
        if not result.fetchone():
            db.execute(text("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
                    username VARCHAR(50) NOT NULL UNIQUE COMMENT '登录用户名',
                    password VARCHAR(255) NOT NULL COMMENT '登录密码',
                    nickname VARCHAR(100) DEFAULT '' COMMENT '用户昵称',
                    role VARCHAR(20) NOT NULL DEFAULT 'user' COMMENT '角色：admin/user',
                    status VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态：active/disabled',
                    avatar VARCHAR(500) DEFAULT '' COMMENT '头像URL',
                    email VARCHAR(100) DEFAULT '' COMMENT '邮箱',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表'
            """))
            db.commit()
            print("[迁移] 已创建 users 表")

        # 确保默认管理员存在
        result = db.execute(text("SELECT id FROM users WHERE username = 'admin'"))
        if not result.fetchone():
            db.execute(text("INSERT INTO users (username, password, nickname, role, status) VALUES ('admin', '123456', '系统管理员', 'admin', 'active')"))
            db.commit()
            print("[迁移] 已插入默认管理员账号")

        # ===== 收藏表迁移 =====
        result = db.execute(text("SHOW TABLES LIKE 'favorites'"))
        if not result.fetchone():
            db.execute(text("""
                CREATE TABLE favorites (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '收藏ID',
                    user_id INT NOT NULL COMMENT '用户ID',
                    word_id INT NOT NULL COMMENT '单词ID',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间',
                    UNIQUE KEY unique_user_word_favorite (user_id, word_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏表'
            """))
            db.commit()
            print("[迁移] 已创建 favorites 表")

        # ===== 错题本表迁移 =====
        result = db.execute(text("SHOW TABLES LIKE 'mistakes'"))
        if not result.fetchone():
            db.execute(text("""
                CREATE TABLE mistakes (
                    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '错题ID',
                    user_id INT NOT NULL COMMENT '用户ID',
                    word_id INT NOT NULL COMMENT '单词ID',
                    mistake_count INT NOT NULL DEFAULT 1 COMMENT '错误次数',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '首次错误时间',
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后错误时间',
                    UNIQUE KEY unique_user_word_mistake (user_id, word_id),
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    FOREIGN KEY (word_id) REFERENCES words(id) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户错题本表'
            """))
            db.commit()
            print("[迁移] 已创建 mistakes 表")

    except Exception as e:
        print(f"[迁移] 迁移过程中出现错误: {e}")
    finally:
        db.close()


auto_migrate()


# 创建 FastAPI 应用实例
app = FastAPI(
    title="英语单词学习系统",
    description="基于 FastAPI 的英语单词在线学习平台",
    version="1.0.0"
)

# 配置跨域资源共享（CORS）
# 允许前端访问后端 API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 开发环境允许所有来源，生产环境应该指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(words.router)       # 单词学习接口
app.include_router(management.router)   # 单词管理接口
app.include_router(ai.router)          # AI 功能接口
app.include_router(auth.router)        # 登录认证接口
app.include_router(users.router)       # 用户管理接口
app.include_router(favorites.router)   # 收藏功能接口
app.include_router(mistakes.router)    # 错题本功能接口


@app.get("/")
def read_root():
    """根路径，返回欢迎信息"""
    return {
        "message": "欢迎使用英语单词学习系统",
        "version": "1.0.0",
        "docs": "/docs"  # FastAPI 自动生成的 API 文档
    }


@app.get("/management")
def management_page():
    """管理后台 - 选择中心"""
    return FileResponse("static/management.html")


@app.get("/login")
def login_page():
    """管理员登录页面"""
    return FileResponse("static/login.html")


@app.get("/management/words")
def management_words_page():
    """管理后台 - 单词管理"""
    return FileResponse("static/management_words.html")


@app.get("/management/users")
def management_users_page():
    """管理后台 - 用户管理"""
    return FileResponse("static/management_users.html")

# 英语单词学习系统

基于 **FastAPI + Vue.js 3** 的英语单词在线学习平台，支持多模式学习、AI 辅助、用户管理、后台管理等功能。

---

## 项目结构

```
网页测试/
├── backend/                    # 后端目录
│   ├── app/                    # 应用代码
│   │   ├── routes/             # API 路由模块
│   │   │   ├── ai.py           # AI 功能接口
│   │   │   ├── auth.py         # 认证（登录/注册）接口
│   │   │   ├── favorites.py    # 收藏功能接口
│   │   │   ├── management.py   # 后台管理接口（词表/单词 CRUD）
│   │   │   ├── mistakes.py     # 错题本接口
│   │   │   ├── users.py        # 用户管理接口
│   │   │   └── words.py        # 单词学习接口
│   │   ├── ai_service.py       # AI 服务封装（智谱 GLM）
│   │   ├── database.py         # 数据库连接配置
│   │   └── models.py           # SQLAlchemy 数据模型
│   ├── static/                 # 管理端页面
│   │   ├── login.html          # 管理员登录页
│   │   ├── management.html     # 管理后台首页
│   │   ├── management_users.html
│   │   └── management_words.html
│   ├── main.py                 # FastAPI 主应用入口
│   ├── requirements.txt        # Python 依赖
│   └── start.py                # 后端启动脚本
├── frontend/                   # 前端目录
│   ├── index.html              # 主学习页面（Vue.js 单页应用）
│   └── start.py                # 前端启动脚本
└── w_init.sql                  # 数据库初始化脚本
```

---

## 前置要求

- **Python 3.8+**
- **MySQL 5.7+**（推荐 8.0）
- **现代浏览器**（Chrome / Firefox / Edge）

---

## 安装步骤

### 1. 初始化数据库

```bash
mysql -u root -p < w_init.sql
```

或在 MySQL 客户端中直接运行 `w_init.sql` 文件内容。

### 2. 配置数据库连接

编辑 `backend/app/database.py`，修改连接字符串：

```python
DATABASE_URL = "mysql+pymysql://用户名:密码@主机:端口/word_learning"
```

默认配置：用户名 `root`，密码 `root`，主机 `localhost`，端口 `3306`

### 3. 安装后端依赖

```bash
cd backend
pip install -r requirements.txt
```

### 4. 启动后端服务

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

或使用启动脚本：

```bash
cd backend
python start.py
```

### 5. 启动前端

```bash
cd frontend
python start.py
```

或直接用浏览器打开 `frontend/index.html`。

---

## 功能说明

### 学习端（用户）

| 功能 | 说明 |
|------|------|
| 卡片模式 | 展示单词、音标、释义、例句，支持上下导航 |
| 拼写模式 | 交互式字母格拼写，支持逐字母揭示 |
| 随机模式 | 随机打乱单词顺序练习 |
| 单词收藏 | 一键收藏/取消收藏，查看收藏列表 |
| 错题本 | 自动记录错误次数，答对自动减少，归零后移出 |
| AI 讲解 | 调用智谱 GLM 大模型，支持词根分析、例句生成、自由问答 |
| 用户注册/登录 | 邮箱注册，支持个人信息修改 |

### 管理端（管理员）

| 功能 | 说明 |
|------|------|
| 词表管理 | 创建/编辑/删除词表，查看词表单词数量 |
| 单词管理 | 单词增删改查，支持批量添加 |
| 用户管理 | 查看用户列表，启禁用账号，修改角色 |

---

## API 接口

FastAPI 自动生成 Swagger 文档：http://localhost:8000/docs

### 接口分组

| 前缀 | 说明 |
|------|------|
| `/api/words` | 单词学习（获取当前/上/下一个单词、单词总数等） |
| `/api/auth` | 认证（登录、注册、获取/更新个人信息） |
| `/api/favorites` | 收藏（切换收藏、检查状态、收藏列表） |
| `/api/mistakes` | 错题本（添加/减少错误、错题列表、移除错题） |
| `/api/ai` | AI 功能（单词解释、生成例句、自由问答） |
| `/api/management` | 后台管理（词表 CRUD、单词 CRUD、批量添加） |
| `/api/management/users` | 用户管理（增删改查） |

---

## 技术栈

### 后端
- **FastAPI** — 高性能 Python Web 框架，自动生成 API 文档
- **SQLAlchemy** — ORM 模型层，支持外键关联与级联删除
- **PyMySQL** — MySQL 数据库驱动
- **Uvicorn** — ASGI 服务器

### 前端
- **Vue.js 3** — 渐进式前端框架（CDN 引入）
- **Axios** — HTTP 请求客户端
- **原生 CSS** — 响应式布局，三栏设计

### AI
- **智谱 GLM-4-Flash** — 大语言模型，提供单词讲解与问答能力

### 数据库
- **MySQL** — 6 张核心表：users、word_lists、words、favorites、mistakes

---

## 数据库设计

```
users           用户表（账号、角色、状态）
word_lists      词表分类表
words           单词表（词、音标、释义、例句、例句翻译）
favorites       用户收藏表（user_id + word_id 联合唯一）
mistakes        错题本表（user_id + word_id 联合唯一，记录错误次数）
```

---

## 默认账号

| 账号           | 密码 | 角色 |
|--------------|------|------|
| admin | 123456 | 管理员 |
| zhangsan@qq.com| 123456 | 普通用户 |
| lisi@qq.com  | 123456 | 普通用户 |

---

## 常见问题

**数据库连接失败**：检查 `database.py` 配置，确保 MySQL 服务正在运行。

**跨域问题**：后端已配置 CORS 允许所有来源，生产环境请限制为具体域名。

**模块导入错误**：确保在 `backend` 目录下运行。

**自动迁移**：后端启动时会自动检测并创建缺失的表和字段，无需手动执行 SQL。

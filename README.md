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
│   └── b_start.py              # 后端启动脚本
├── frontend/                   # 前端目录
    ├── js/                     # JS目录
    │   ├── app.js
    ├── css/                    # CSS目录
    │   ├── style.css           
│   ├── index.html              # 主学习页面（Vue.js 单页应用）
│   └── f_start.py              # 前端启动脚本
├── crawl_dictionary.py         # 单词数据爬虫
├── word_learning.sql           # 数据库初始化脚本
├── words_insert.sql            # 单词数据 SQL（爬虫生成）
└── README.md                   # 项目说明文档
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
mysql -u root -p < word_learning.sql
```

或在 MySQL 客户端中直接运行 `word_learning.sql` 文件内容。

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
uvicorn main:app --reload --host 127.0.0.1 --port 3000
```

或使用启动脚本：

```bash
cd backend
python b_start.py
```

### 5. 启动前端

```bash
cd frontend
python f_start.py
```
---

## 功能说明

### 学习端（用户）

| 功能 | 说明 |
|------|------|
| 阅读模式 | 展示单词、音标、释义、例句，支持上下导航 |
| 拼写模式 | 交互式字母格拼写，支持逐字母揭示 |
| 随机模式 | 随机打乱单词顺序练习，完成后显示祝贺横幅 |
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

FastAPI 自动生成 Swagger 文档：http://localhost:8080/docs

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
words           单词表（词、UK/US音标、释义、例句、例句翻译）
favorites       用户收藏表（user_id + word_id 联合唯一，外键引用 words）
mistakes        错题本表（user_id + word_id 联合唯一，记录错误次数，外键引用 words）
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

---

# 单词数据爬虫

## 功能说明

`crawl_dictionary.py` 是一个用于爬取 Dictionary.net 网站单词数据的 Python 爬虫脚本，自动提取单词的音标（UK 和 US）、释义和例句，生成可直接执行的 SQL 文件。

### 核心特性

- ✅ 自动爬取单词列表和详情页
- ✅ 提取单词音标（UK 和 US 分开存储）
- ✅ 提取单词释义
- ✅ 提取例句及其中文翻译
- ✅ 自动过滤"误拼"单词
- ✅ 只保留有音标和例句的单词
- ✅ 生成可直接运行的 SQL 文件（自动处理外键约束）
- ✅ 支持自定义爬取页数和起始页
- ✅ 自动检测最后一页并停止

### 安装依赖

```bash
pip install requests beautifulsoup4
```

### 使用方法

**基本用法**

```bash
# 爬取默认的100页（从第1页开始）
python crawl_dictionary.py
```

**指定页数**

```bash
# 爬取前5页
python crawl_dictionary.py 5

# 从第3页开始爬取10页
python crawl_dictionary.py 10 3

# 爬取全部页面（设置较大页数，脚本会自动检测最后一页）
python crawl_dictionary.py 1000
```

**参数说明**

```bash
python crawl_dictionary.py [页数] [起始页]
```

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 页数 | 要爬取的总页数 | 100 |
| 起始页 | 从第几页开始爬取 | 1 |

### 输出文件

运行成功后，会生成 `words_insert.sql` 文件，格式如下：

```sql
-- Dictionary.net 单词数据
-- 自动生成时间: 2026-07-21 10:30:00
-- 总计: 500 个单词
-- 注意：已更新为UK/US音标分开存储
-- 临时禁用外键检查，以允许TRUNCATE被引用的表
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE words;
SET FOREIGN_KEY_CHECKS = 1;

INSERT INTO words (list_id, word, phonetic_uk, phonetic_us, audio_url_uk, audio_url_us, meaning, example, example_translation) 
VALUES (1, 'example', '/ɪɡˈzɑːmpl/', '/ɪɡˈzæmpl/', '/ɪɡˈzɑːmpl/', '/ɪɡˈzæmpl/', '例子，范例', 'This is a good example.', '这是一个很好的例子。');
```

### 字段说明

| 字段 | 说明 |
|------|------|
| word | 单词名称 |
| phonetic_uk | 英式音标 |
| phonetic_us | 美式音标 |
| audio_url_uk | 英式发音音频 URL |
| audio_url_us | 美式发音音频 URL |
| meaning | 单词释义 |
| example | 英文例句 |
| example_translation | 中文例句翻译 |

### 注意事项

1. **爬取速度**：建议每次爬取不超过 100 页，避免对服务器造成过大压力
2. **数据验证**：爬虫会自动跳过没有音标或例句的单词
3. **误拼过滤**：自动跳过标注为"误拼"的单词（如 response -> reponse）
4. **重复检查**：已访问的单词不会被重复爬取
5. **网络要求**：需要网络连接才能正常工作
6. **数据覆盖**：生成的 SQL 文件会先执行 `TRUNCATE TABLE words`，会清空表中原有数据
7. **外键处理**：SQL 文件开头会自动禁用外键检查，避免 `favorites` 和 `mistakes` 表的外键约束导致 TRUNCATE 失败

### 运行 SQL 文件

```bash
mysql -u root -p word_learning < words_insert.sql
```

---

## 更新日志

- **2026-07-21**：
  - 修复随机模式完成横幅布局问题（悬浮显示，不挤压内容）
  - 增大阅读模式音标间距
  - 修复爬虫 SQL 外键约束问题（添加 FOREIGN_KEY_CHECKS 控制）
  - 更新 README 文档

- **2026-07-12**：
  - 初始版本
  - 支持爬取单词列表和详情页
  - 提取音标、释义和例句
  - 生成 SQL 文件
  - 支持分页爬取
  - 自动过滤误拼单词
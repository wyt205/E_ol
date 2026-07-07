# 英语单词学习系统

这是一个基于 FastAPI + Vue.js 的英语单词在线学习网站。

## 项目结构

```
网页测试/
├── backend/                 # 后端目录
│   ├── app/                # 应用代码
│   │   ├── routes/         # API 路由
│   │   ├── database.py     # 数据库配置
│   │   └── models.py       # 数据模型
│   ├── main.py             # 主应用入口
│   └── requirements.txt    # Python 依赖包
├── frontend/               # 前端目录
│   ├── index.html          # 主页面
│   └── static/             # 静态资源
└── w_init.sql              # 数据库初始化脚本
```

## 前置要求

1. **Python 3.8+**
2. **MySQL 数据库**
3. **现代浏览器**（Chrome、Firefox、Edge 等）

## 安装步骤

### 1. 初始化数据库

在 MySQL 中执行初始化脚本：

```bash
mysql -u root -p < w_init.sql
```

或者在 MySQL 客户端中直接运行 `w_init.sql` 文件的内容。

### 2. 配置数据库连接

编辑 `backend/app/database.py` 文件，修改数据库连接字符串：

```python
DATABASE_URL = "mysql+pymysql://用户名:密码@主机:端口/word_learning"
```

将 `用户名`、`密码`、`主机`、`端口` 替换为你的 MySQL 配置。

默认配置：
- 用户名：root
- 密码：root
- 主机：localhost
- 端口：3306

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

后端将在 `http://localhost:8000` 运行。

### 5. 访问前端

直接在浏览器中打开 `frontend/index.html` 文件即可。

或者使用简单的 HTTP 服务器：

```bash
cd frontend
python -m http.server 3000
```

然后在浏览器中访问 `http://localhost:3000`

## API 接口说明

FastAPI 会自动生成交互式 API 文档，访问以下地址查看：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要接口

1. **获取当前单词**
   - GET `/api/words/current`
   - 返回第一个单词

2. **根据 ID 获取单词**
   - GET `/api/words/{word_id}`
   - 参数：word_id - 单词 ID

3. **获取下一个单词**
   - GET `/api/words/next/{current_id}`
   - 参数：current_id - 当前单词 ID

4. **获取上一个单词**
   - GET `/api/words/prev/{current_id}`
   - 参数：current_id - 当前单词 ID

5. **获取单词总数**
   - GET `/api/words/count`
   - 返回：{total: 数量}

6. **获取首尾单词 ID**
   - GET `/api/words/first-last`
   - 返回：{first_id: 第一个ID, last_id: 最后一个ID}

## 技术栈

### 后端
- **FastAPI**: 高性能 Python Web 框架
- **SQLAlchemy**: Python ORM 框架
- **PyMySQL**: MySQL 数据库驱动
- **Uvicorn**: ASGI 服务器

### 前端
- **Vue.js 3**: 渐进式 JavaScript 框架
- **Axios**: HTTP 客户端
- **原生 CSS**: 样式设计

## 功能特点

✅ 显示单词、音标、释义和例句
✅ 通过左右按钮切换单词
✅ 第一个单词时禁用"上一个"按钮
✅ 最后一个单词时禁用"下一个"按钮
✅ 显示当前进度（第 X / 总数 个单词）
✅ 响应式设计，适配移动端
✅ 美观的渐变背景设计

## 开发说明

### FastAPI 核心概念

1. **路由（Router）**: 定义 URL 和处理函数的映射关系
2. **依赖注入（Dependency Injection）**: 通过 `Depends()` 实现，如数据库会话
3. **自动文档**: FastAPI 自动生成 OpenAPI 文档
4. **异步支持**: 原生支持 async/await

### 项目架构

```
请求流程：
前端 (Vue.js) 
  ↓ HTTP 请求
后端 API (FastAPI)
  ↓ 路由处理
业务逻辑 (routes/)
  ↓ 数据库操作
ORM 模型 (models.py)
  ↓ SQL 查询
MySQL 数据库
```

## 常见问题

### 1. 数据库连接失败

检查 `database.py` 中的连接配置是否正确，确保 MySQL 服务正在运行。

### 2. 跨域问题

后端已配置 CORS，允许所有来源访问。生产环境应该限制为具体域名。

### 3. 模块导入错误

确保在 `backend` 目录下运行，或者将 `backend` 添加到 Python 路径。

## 下一步扩展

- [ ] 记录学习进度
- [ ] 添加单词发音功能
- [ ] 实现单词搜索
- [ ] 添加收藏功能
- [ ] 统计学习数据

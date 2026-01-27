# Stock News Backend

金融事件分析系统后端服务。

## 环境要求

- Python 3.10+
- MongoDB
- uv (Python 包管理器)

## 安装

### 1. 安装 uv

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 安装依赖

```bash
cd backend
uv sync
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写：
- `MONGODB_URL`: MongoDB 连接地址
- `DATABASE_NAME`: 数据库名称
- `ZHIPU_API_KEY`: 智谱 AI API 密钥

## 运行

### 启动 API 服务

```bash
# 使用 uv 运行
uv run python -m app.main

# 或者激活虚拟环境后运行
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS
python -m app.main
```

API 将在 `http://localhost:8000` 启动。

API 文档：`http://localhost:8000/docs`

### 初始化数据

```bash
# 方式 1：使用批处理文件（Windows）
init_data.bat --days 30

# 方式 2：使用 uv 命令
uv run python spider/init/init_events.py --days 30

# 方式 3：使用 Python 脚本
uv run python init_data.py --days 30

# 启用 AI 分析（会很慢）
uv run python spider/init/init_events.py --days 30 --ai
```

### 增量更新数据

```bash
# 方式 1：使用批处理文件（Windows）
update_data.bat --days 1

# 方式 2：使用 uv 命令
uv run python spider/update/update_events.py --days 1

# 方式 3：使用 Python 脚本
uv run python update_data.py --days 1

# 启用 AI 分析
uv run python spider/update/update_events.py --days 1 --ai
```

## 项目结构

```
backend/
├── app/
│   ├── main.py              # FastAPI 应用入口
│   ├── config.py            # 配置管理
│   ├── core/                # 核心模块
│   │   └── database.py      # MongoDB 连接
│   ├── models/              # 数据模型
│   │   ├── event.py         # 事件模型
│   │   ├── sector.py        # 板块模型
│   │   └── stock.py         # 股票模型
│   ├── routers/             # API 路由
│   │   ├── events.py        # 事件路由
│   │   ├── sectors.py       # 板块路由
│   │   ├── stocks.py        # 股票路由
│   │   └── dashboard.py     # 仪表板路由
│   └── services/            # 业务逻辑
│       ├── ai_service.py         # AI 分析服务
│       └── database_service.py   # 数据库服务
├── spider/                  # 爬虫模块
│   ├── init/                # 初始化爬虫
│   │   └── init_events.py
│   └── update/              # 更新爬虫
│       └── update_events.py
├── init_data.py             # 便捷初始化脚本
├── update_data.py           # 便捷更新脚本
├── init_data.bat            # Windows 批处理文件
├── update_data.bat          # Windows 批处理文件
├── pyproject.toml           # 项目依赖
└── .env                     # 环境变量
```

## API 端点

- `GET /` - 根路径
- `GET /health` - 健康检查
- `GET /api/events` - 获取事件列表
- `GET /api/events/{id}` - 获取事件详情
- `POST /api/events` - 创建事件
- `PUT /api/events/{id}` - 更新事件
- `DELETE /api/events/{id}` - 删除事件
- `POST /api/events/{id}/analyze` - 对事件进行 AI 分析
- `GET /api/sectors` - 获取板块列表
- `GET /api/stocks` - 获取股票列表
- `GET /api/dashboard` - 获取仪表板统计数据

```bash
uv run black app/
uv run ruff check app/
```

### 运行测试

```bash
uv run pytest
```

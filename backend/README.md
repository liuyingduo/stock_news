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

## 数据采集与AI分析

系统采用**分离架构**：数据采集和AI分析完全独立，可以分步运行。

### 数据采集（不含AI分析）

#### 1. 初始化历史数据

```bash
# 初始化所有A股最近30天的数据（约40分钟）
uv run python spider/init/init_events.py --all --days 30

# 或初始化热门股票数据（更快，约2分钟）
uv run python spider/init/init_events.py --stocks 20 --days 30

# 便捷脚本
uv run python run_init.py --all --days 30
```

#### 2. 增量更新最新数据

```bash
# 更新所有A股最近1天的数据
uv run python spider/update/update_events.py --all --days 1

# 或更新热门股票数据
uv run python spider/update/update_events.py --stocks 10 --days 1

# 便捷脚本
uv run python run_update.py --all --days 1
```

**参数说明**：
- `--stocks N`: 获取前N只热门股票（默认：init为20，update为10）
- `--all`: 获取所有A股股票（约5000只）
- `--days N`: 只保存最近N天的数据（不指定则保存全部）

### AI 分析（独立运行）

```bash
# 分析所有待分析的事件
uv run python spider/analyze/analyze_events.py

# 分析最近7天的事件
uv run python spider/analyze/analyze_events.py --days 7

# 只分析核心驱动类别的事件
uv run python spider/analyze/analyze_events.py --category core_driver

# 最多分析100条事件
uv run python spider/analyze/analyze_events.py --limit 100

# 组合使用：分析最近3天的核心驱动事件，最多50条
uv run python spider/analyze/analyze_events.py --days 3 --category core_driver --limit 50

# 高速模式（并发15个）
uv run python spider/analyze/analyze_events.py --days 7 --concurrency 15

# 便捷脚本
uv run python run_analysis.py --days 7
```

**AI分析参数**：
- `--limit N`: 最多分析N条事件（默认：1000）
- `--days N`: 只分析最近N天的事件
- `--category CAT`: 按事件类别筛选（core_driver, special_situation等）
- `--event-type TYPE`: 按事件类型筛选（dividend, ma等）
- `--concurrency N` 或 `-c N`: 并发分析数量（默认：5）

### 检查工具

```bash
# 查看待分析的事件统计
uv run python spider/analyze/check_pending_events.py

# 检查并重试失败的事件
uv run python spider/analyze/check_failed_events.py
```

### 典型工作流程

```bash
# 第一次使用
uv run python spider/init/init_events.py --all --days 30    # 采集数据
uv run python spider/analyze/check_pending_events.py         # 检查状态
uv run python spider/analyze/analyze_events.py --days 30    # AI分析
uv run python spider/analyze/check_failed_events.py         # 处理失败事件

# 日常更新
uv run python spider/update/update_events.py --all --days 1 # 采集最新数据
uv run python spider/analyze/check_pending_events.py         # 检查状态
uv run python spider/analyze/analyze_events.py --days 1 --concurrency 10  # AI分析
uv run python spider/analyze/check_failed_events.py         # 定期检查失败事件
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
├── spider/                  # 爬虫和AI分析模块
│   ├── init/                # 初始化爬虫
│   │   └── init_events.py   # 获取历史数据
│   ├── update/              # 更新爬虫
│   │   └── update_events.py # 增量更新数据
│   ├── analyze/             # AI 分析脚本
│   │   ├── analyze_events.py      # 批量AI分析
│   │   ├── check_pending_events.py # 检查待分析事件
│   │   └── check_failed_events.py # 检查并重试失败事件
│   ├── run_init.py          # 便捷初始化脚本
│   ├── run_update.py        # 便捷更新脚本
│   ├── run_analysis.py      # 便捷分析脚本
│   └── README.md            # 详细使用文档
├── pyproject.toml           # 项目依赖
└── .env                     # 环境变量
```

## API 端点

### 事件相关
- `GET /api/events` - 获取事件列表（支持分页、筛选、搜索）
- `GET /api/events/{id}` - 获取事件详情
- `POST /api/events` - 创建事件
- `PUT /api/events/{id}` - 更新事件
- `DELETE /api/events/{id}` - 删除事件
- `POST /api/events/{id}/analyze` - 对单个事件进行 AI 分析
- `GET /api/events/sector/{sector_code}` - 获取影响指定板块的事件
- `GET /api/events/stock/{stock_code}` - 获取影响指定股票的事件

### 板块和股票
- `GET /api/sectors` - 获取板块列表
- `GET /api/stocks` - 获取股票列表

### 仪表板
- `GET /api/dashboard/stats` - 获取仪表板统计数据

### 系统
- `GET /` - 根路径
- `GET /health` - 健康检查

## 开发工具

### 代码格式化

```bash
uv run black app/
```

### 代码检查

```bash
uv run ruff check app/
```

### 运行测试

```bash
uv run pytest
```

## 注意事项

1. **数据采集和AI分析分离**：爬虫脚本不会自动进行AI分析，需要单独运行分析脚本
2. **API限流**：爬虫脚本每只股票之间有0.5秒延迟，避免请求过快被限制
3. **大量数据处理**：使用 `--all` 参数会处理所有A股（约5000只），请确保有足够时间
4. **数据库连接**：确保MongoDB服务正在运行
5. **AI服务配置**：使用AI分析功能前，请确保 `.env` 文件中配置了 `ZHIPU_API_KEY`

## 详细文档

更多爬虫和AI分析的详细用法，请参考 [spider/README.md](./spider/README.md)


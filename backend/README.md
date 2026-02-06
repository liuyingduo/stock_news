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

### 数据来源

| 交易所 | 说明 | 特性 |
|--------|------|------|
| **上交所** (SSE) | 上海证券交易所公告 | PDF自动下载，支持多类别 |
| **深交所** (SZSE) | 深圳证券交易所公告 | PDF自动下载，支持多类别 |
| **北交所** (BSE) | 北京证券交易所公告 | PDF自动下载，13个类别 |
| **财联社电报** | 实时快讯 | 需AI分类 |

### PDF处理

系统会自动：
- 下载交易所公告PDF文件
- 解析PDF内容为文本
- **自动清理本地文件**（仅保留文本和远程链接）

### 数据采集

启动全自动监控服务：

```bash
# 包含：三大交易所公告（30分钟/次）+ 财联社电报（10秒/次）
uv run python spider/update/update_events.py
```

### AI 分析

分析脚本会自动进行分类和分析（一次调用完成）：

```bash
# 分析所有待分析的事件
uv run python spider/analyze/analyze_events.py

# 分析最近7天的事件
uv run python spider/analyze/analyze_events.py --days 7

# 高速模式（并发10个）
uv run python spider/analyze/analyze_events.py --concurrency 10

# 只分析特定类别
uv run python spider/analyze/analyze_events.py --category company_updates
```

**AI分析参数**：
- `--limit N`: 最多分析N条事件（默认：1000）
- `--days N`: 只分析最近N天的事件
- `--category CAT`: 按事件类别筛选（global_events, policy_trends, industry_trends, company_updates）
- `--event-type TYPE`: 按事件类型筛选
- `--concurrency N` 或 `-c N`: 并发分析数量（默认：5）

### 典型工作流程

```bash
# 启动监控服务（后台运行）
uv run python spider/update/update_events.py

# 定期运行分析
uv run python spider/analyze/analyze_events.py --days 1
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
│       ├── database_service.py   # 数据库服务
│       └── pdf_service.py        # PDF处理服务
├── spider/                  # 爬虫和AI分析模块
│   ├── common/              # 交易所爬虫
│   │   ├── sse_notice_fetcher.py   # 上交所爬虫
│   │   ├── szse_notice_fetcher.py  # 深交所爬虫
│   │   └── bse_notice_fetcher.py   # 北交所爬虫
│   ├── update/              # 更新爬虫
│   │   └── update_events.py        # 监控主程序
│   ├── analyze/             # AI 分析脚本
│   │   └── analyze_events.py       # 批量AI分析（含分类）
│   └── README.md            # 爬虫使用文档
├── static/pdfs/             # (已弃用) PDF临时存储
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

### 静态文件
- `/static/pdfs/{filename}` - 访问本地PDF文件

### 系统
- `GET /` - 根路径
- `GET /health` - 健康检查

## 注意事项

1. **AI分析优化**：系统将分类、评分、实体提取合并为一次 LLM 调用，降低成本并提高速度
2. **数据采集和AI分析分离**：爬虫脚本不会自动进行AI分析，需要单独运行分析脚本
3. **数据库连接**：确保MongoDB服务正在运行
4. **AI服务配置**：使用AI分析功能前，请确保 `.env` 文件中配置了 `ZHIPU_API_KEY`
5. **PDF存储**：PDF文件会占用磁盘空间，定期清理 `static/pdfs/` 目录
6. **网络稳定**：PDF下载需要稳定的网络连接，如遇问题可使用 `--no-pdf` 跳过

## 详细文档

更多爬虫和AI分析的详细用法，请参考 [spider/README.md](./spider/README.md)

## AI Analysis Commands (Updated)

Run from `backend/` directory.

```bash
# 1) Start API service
uv run python -m app.main

# 2) Batch analyze latest 7 days
uv run python spider/analyze/analyze_events.py --days 7 --concurrency 10

# 3) Batch analyze with explicit limit
uv run python spider/analyze/analyze_events.py --limit 500 --concurrency 10

# 4) Re-analyze existing AI results
uv run python spider/analyze/analyze_events.py --limit 500 --force --concurrency 10

# 5) Analyze by category
uv run python spider/analyze/analyze_events.py --category policy --days 30 --concurrency 10
```

API-based analysis:

```bash
# Single event AI analysis
curl -X POST "http://localhost:8000/api/events/{event_id}/analyze"

# Batch AI analysis (new endpoint)
curl -X POST "http://localhost:8000/api/events/analyze/batch?limit=200&days=7"
```

Radar result checks:

```bash
curl "http://localhost:8000/api/opportunity-radar/overview"
curl "http://localhost:8000/api/opportunity-radar/signals?signal_type=opportunity&limit=10"
curl "http://localhost:8000/api/opportunity-radar/top-events?limit=20"
```

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

| 接口 | 来源 | 说明 |
|------|------|------|
| `stock_notice_report` | 东方财富 | 沪深京A股公告，类型已知 |
| `stock_info_global_cls` | 财联社 | 电报快讯，需AI分类 |

### 数据采集

```bash
# 初始化数据（获取最近7天公告）
uv run python spider/run_init.py

# 获取最近30天公告
uv run python spider/run_init.py --days 30

# 增量更新（获取今日公告）
uv run python spider/run_update.py
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
# 第一次使用
uv run python spider/run_init.py --days 30           # 采集数据
uv run python spider/analyze/analyze_events.py       # AI分析

# 日常更新
uv run python spider/run_update.py                   # 采集最新数据
uv run python spider/analyze/analyze_events.py --days 1  # 分析新数据
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
│   │   └── analyze_events.py    # 批量AI分析（含分类）
│   ├── run_init.py          # 便捷初始化脚本
│   ├── run_update.py        # 便捷更新脚本
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

## 注意事项

1. **AI分析优化**：系统将分类、评分、实体提取合并为一次 LLM 调用，降低成本并提高速度
2. **数据采集和AI分析分离**：爬虫脚本不会自动进行AI分析，需要单独运行分析脚本
3. **数据库连接**：确保MongoDB服务正在运行
4. **AI服务配置**：使用AI分析功能前，请确保 `.env` 文件中配置了 `ZHIPU_API_KEY`

## 详细文档

更多爬虫和AI分析的详细用法，请参考 [spider/README.md](./spider/README.md)

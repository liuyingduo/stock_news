# Stock News Analysis System

金融事件获取与分析系统 - 基于事件驱动策略的量化交易工具

## 项目简介

这是一个可以获取金融事件，并展示分析金融事件的系统。采用暗色"作战室"主题，提供专业的监控界面风格。系统采用事件采集和AI分析分离的架构，支持灵活的数据处理流程。

## 功能特性

### 核心功能
- **事件采集**：使用 Akshare 获取财经新闻、公告、研报等金融事件
  - 沪深京A股公告（东方财富）
  - 财联社电报（实时快讯）
  - 支持初始化历史数据和增量更新
- **AI 分析**：基于智谱 GLM-4-Flash 模型进行智能分析
  - 自动分类（全球大事、政策风向、行业动向、公司动态）
  - 提取影响的原材料、板块、股票
  - 对事件影响进行打分（0-10分）并给出理由
  - **一次调用完成所有分析**，降低成本并提高速度
- **可视化展示**：
  - 仪表板：分类标签、搜索、筛选、事件卡片
  - 板块视图：交互式板块图，标记风险程度
  - 实时统计和分析结果展示

### 事件分类体系

| 大类 | 子类型 |
|-----|--------|
| **全球大事** | 宏观地缘 |
| **政策风向** | 监管政策、市场情绪 |
| **行业动向** | 产业链驱动、核心板块 |
| **公司动态** | 重大事项、财务报告、融资公告、风险提示、资产重组、信息变更、持股变动 |

## 技术栈

### 后端
- **框架**：FastAPI
- **数据库**：MongoDB + Motor（异步驱动）
- **AI**：智谱 GLM-4-Flash
- **数据源**：Akshare
- **包管理**：uv

### 前端
- **框架**：Vue 3 + TypeScript
- **构建工具**：Vite
- **UI 组件**：Element Plus（暗色主题）
- **状态管理**：Pinia
- **路由**：Vue Router

## 快速开始

### 前置要求

- Python 3.10+
- MongoDB
- Node.js 18+
- uv（Python 包管理器）

### 1. 安装 uv

```bash
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. 配置环境变量

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，填写：
- `MONGODB_URL`: MongoDB 连接地址
- `DATABASE_NAME`: 数据库名称
- `ZHIPU_API_KEY`: 智谱 AI API 密钥

### 3. 启动后端

```bash
cd backend
uv sync
uv run python -m app.main
```

API: http://localhost:8000
文档: http://localhost:8000/docs

### 4. 数据采集

```bash
cd backend

# 初始化数据（获取最近7天的公告）
uv run python spider/run_init.py

# 或指定天数
uv run python spider/run_init.py --days 30
```

### 5. AI 分析

```bash
cd backend

# 分析所有待分析的事件（自动包含分类）
uv run python spider/analyze/analyze_events.py

# 分析最近7天的事件
uv run python spider/analyze/analyze_events.py --days 7

# 高速模式（并发10个）
uv run python spider/analyze/analyze_events.py --concurrency 10
```

### 6. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端: http://localhost:5173

## 日常使用

### 更新最新数据

```bash
cd backend

# 1. 增量更新数据
uv run python spider/run_update.py

# 2. 分析新数据
uv run python spider/analyze/analyze_events.py --days 1
```

## API 端点

- `GET /api/events` - 获取事件列表
- `POST /api/events/{id}/analyze` - AI 分析单个事件
- `GET /api/sectors` - 获取板块列表
- `GET /api/dashboard/stats` - 仪表板统计

详细 API 文档：http://localhost:8000/docs

## 项目结构

```
stock_news/
├── backend/                 # FastAPI 后端
│   ├── app/                 # 应用代码
│   │   ├── routers/         # API 路由
│   │   ├── services/        # 业务逻辑
│   │   │   ├── ai_service.py          # AI 分析服务
│   │   │   └── database_service.py    # 数据库服务
│   │   └── models/          # 数据模型
│   ├── spider/              # 数据爬虫和分析
│   │   ├── init/            # 初始化爬虫
│   │   ├── update/          # 增量更新爬虫
│   │   ├── analyze/         # AI 分析脚本
│   │   └── README.md        # 爬虫详细文档
│   └── pyproject.toml       # 项目依赖
├── frontend/                # Vue 3 前端
│   ├── src/
│   │   ├── components/      # Vue 组件
│   │   ├── views/           # 页面视图
│   │   └── api/             # API 调用
│   └── package.json
└── README.md
```

## 数据流程

1. **数据采集阶段**
   - 运行初始化/更新脚本获取公告和电报数据
   - 公告数据自动分类为"公司动态"
   - 电报数据标记为待AI分类

2. **AI分析阶段**
   - 运行分析脚本对事件进行批量分析
   - **一次调用完成**：分类、评分、实体提取
   - 更新事件记录

3. **前端展示**
   - 查询已分析的事件
   - 展示AI分析结果
   - 支持筛选、搜索、排序

## 常见问题

### Q: AI分析如何实现高效率？
A: 系统将分类、评分、实体提取合并为一次 LLM 调用，相比分开调用减少了 2/3 的 API 请求，显著降低成本并提高速度。

### Q: 如何提高AI分析速度？
A:
- 使用 `--concurrency 10` 或更高的并发数
- 使用 `--days` 参数只分析最近的数据
- 使用 `--category` 参数只分析特定类别的事件

## 许可证

MIT License

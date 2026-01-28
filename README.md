# Stock News Analysis System

金融事件获取与分析系统 - 基于事件驱动策略的量化交易工具

## 项目简介

这是一个可以获取金融事件，并展示分析金融事件的系统。采用暗色"作战室"主题，提供专业的监控界面风格。系统采用事件采集和AI分析分离的架构，支持灵活的数据处理流程。

## 功能特性

### 核心功能
- **事件采集**：使用 Akshare 获取财经新闻、公告、研报等金融事件
  - 支持初始化所有A股历史数据
  - 支持增量更新最新数据
  - 按天数过滤数据
- **AI 分析**：基于智谱 GLM-4.7-Flash 模型进行智能分析（独立运行）
  - 提取影响的原材料、板块、股票
  - 对事件影响进行打分（0-10分）并给出理由
  - 支持批量分析、按类别筛选
- **可视化展示**：
  - 仪表板：分类标签、搜索、筛选、事件卡片
  - 板块视图：交互式板块图，标记风险程度
  - 实时统计和分析结果展示

### 事件类型覆盖

1. **核心驱动板块**（硬催化剂）
   - 监管与政策风向标
   - 财务与权益事件

2. **特殊机遇板块**
   - 并购重组
   - 资本结构调整
   - 管理层异动

3. **产业链与微观驱动**
   - 价格传导
   - 产能变化
   - 供需缺口

4. **市场情绪与资金流**
   - 异常异动监控
   - 舆情热度
   - 指数成分股变动

5. **宏观叙事与地缘政治**
   - 货币政策与流动性
   - 地缘风险脉冲
   - 关键宏观指标

## 技术栈

### 后端
- **框架**：FastAPI
- **数据库**：MongoDB + Motor（异步驱动）
- **AI**：智谱 GLM-4.7-Flash
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

### 4. 数据采集（第一步）

```bash
cd backend

# 初始化所有A股最近30天的数据
uv run python spider/init/init_events.py --all --days 30

# 或初始化热门股票数据（更快）
uv run python spider/init/init_events.py --stocks 20 --days 30
```

### 5. AI 分析（第二步）

```bash
cd backend

# 分析所有待分析的事件
uv run python spider/analyze/analyze_events.py

# 分析最近7天的事件
uv run python spider/analyze/analyze_events.py --days 7

# 只分析特定类别的事件
uv run python spider/analyze/analyze_events.py --category core_driver --days 7

# 高速模式（并发15个）
uv run python spider/analyze/analyze_events.py --days 7 --concurrency 15
```

**重要**：数据采集和AI分析完全分离，建议先完成所有数据采集，再统一运行AI分析。

### 6. 检查工具（可选）

```bash
cd backend

# 查看待分析的事件统计
uv run python spider/analyze/check_pending_events.py

# 检查并重试失败的事件
uv run python spider/analyze/check_failed_events.py
```

### 7. 启动前端

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

# 1. 更新数据（不含AI分析）
uv run python spider/update/update_events.py --all --days 1

# 2. 分析新数据
uv run python spider/analyze/analyze_events.py --days 1
```

### 便捷脚本

```bash
# 使用便捷脚本（更短的命令）
cd backend

# 初始化
uv run python run_init.py --all --days 30

# 更新
uv run python run_update.py --all --days 1

# AI分析
uv run python run_analysis.py --days 7
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
   - 运行初始化脚本获取历史数据
   - 运行更新脚本获取最新数据
   - 数据保存在 MongoDB，不含AI分析结果

2. **AI分析阶段**
   - 运行分析脚本对事件进行批量分析
   - 提取影响的板块、股票、原材料
   - 生成影响评分和理由
   - 更新事件记录

3. **前端展示**
   - 查询已分析的事件
   - 展示AI分析结果
   - 支持筛选、搜索、排序

## 常见问题

### Q: 数据采集和AI分析为什么要分离？
A: 分离架构带来以下好处：
- 数据采集可以快速完成，不需要等待AI分析
- 可以根据需要选择性地分析数据（如只分析重要事件）
- AI分析可以分批、分时段进行，避免一次性处理大量数据
- 便于调试和维护

### Q: 如何提高AI分析速度？
A:
- 使用 `--limit` 参数限制每次分析的条数
- 使用 `--days` 参数只分析最近的数据
- 使用 `--category` 参数只分析特定类别的事件

### Q: 采集所有A股数据需要多久？
A:
- 数据采集：约5000只股票 × 0.5秒延迟 ≈ 40分钟
- AI分析：取决于事件数量，约1000条事件/小时

建议先使用 `--stocks 50` 测试，确认效果后再使用 `--all`。

## 许可证

MIT License

# Stock News Analysis System

金融事件获取与分析系统 - 基于事件驱动策略的量化交易工具

## 项目简介

这是一个可以获取金融事件，并展示分析金融事件的系统。采用暗色"作战室"主题，提供专业的监控界面风格。

## 功能特性

### 核心功能
- **事件采集**：使用 Akshare 获取财经新闻、公告、研报等金融事件
- **AI 分析**：基于智谱 GLM-4.7-Flash 模型进行智能分析
  - 提取影响的原材料、板块、股票
  - 对事件影响进行打分（0-10分）并给出理由
- **可视化展示**：
  - 仪表板：分类标签、搜索、筛选、事件卡片
  - 板块视图：交互式板块图，标记风险程度

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

### 4. 初始化数据（可选）

```bash
# 方式 1：使用批处理文件（Windows）
cd backend
init_data.bat --days 30

# 方式 2：使用 uv 命令
cd backend
uv run python spider/init/init_events.py --days 30

# 方式 3：使用 Python 脚本
cd backend
uv run python init_data.py --days 30
```

### 5. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端: http://localhost:5173

## API 端点

- `GET /api/events` - 获取事件列表
- `POST /api/events/{id}/analyze` - AI 分析事件
- `GET /api/sectors` - 获取板块列表
- `GET /api/dashboard/stats` - 仪表板统计

详细 API 文档：http://localhost:8000/docs

## 项目结构

```
stock_news/
├── backend/       # FastAPI 后端
│   ├── app/       # 应用代码
│   ├── spider/    # 数据爬虫
│   └── pyproject.toml
├── frontend/      # Vue 3 前端
└── README.md
```

## 许可证

MIT License

# Stock News Frontend

金融事件分析系统前端。

## 技术栈

- Vue 3
- TypeScript
- Vite
- Element Plus（UI 组件库，支持暗色主题）
- Pinia（状态管理）
- Vue Router（路由）
- Axios（HTTP 客户端）

## 安装

```bash
cd frontend
npm install
```

## 运行

```bash
npm run dev
```

应用将在 `http://localhost:5173` 启动。

## 构建

```bash
npm run build
```

## 特性

- 暗色"作战室"主题
- 事件仪表板
  - 按大类筛选（全球大事、政策风向、行业动向、公司动态）
  - 按事件类型筛选（分组下拉菜单）
  - 搜索功能
- 事件卡片
  - 分类标签显示
  - AI分析结果展示（评分、影响板块/股票）
  - 点击查看PDF原文
- 板块视图（交互式板块图）
- 响应式设计

## 数据来源

前端展示的数据来自：
- **上交所** (SSE)：上海证券交易所公告
- **深交所** (SZSE)：深圳证券交易所公告
- **北交所** (BSE)：北京证券交易所公告
- **财联社电报**：实时快讯

所有公告PDF文件自动下载到后端，点击公告时可直接查看。

## 事件分类体系

| 大类 | 子类型 |
|-----|--------|
| 全球大事 | 宏观地缘 |
| 政策风向 | 监管政策、市场情绪 |
| 行业动向 | 产业链驱动、核心板块 |
| 公司动态 | 重大事项、财务报告、融资公告、风险提示、资产重组、信息变更、持股变动 |

## API集成

前端通过以下API与后端通信：

- `GET /api/events` - 获取事件列表
- `GET /api/events/{id}` - 获取事件详情
- `POST /api/events/{id}/analyze` - AI分析事件
- `GET /api/sectors` - 获取板块列表
- `GET /api/dashboard/stats` - 获取仪表板统计
- `/static/pdfs/{filename}` - 查看PDF文件

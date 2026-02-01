# 金融事件数据更新系统

## 功能说明

本系统整合了三大交易所（上交所、深交所、北交所）的公告数据和财联社电报数据，提供完整的市场信息采集功能。

### 主要特性

1. **三大交易所公告采集**
   - 上海证券交易所 (SSE)
   - 深圳证券交易所 (SZSE)
   - 北京证券交易所 (BSE)

2. **PDF自动处理**
   - 自动下载交易所公告PDF文件
   - 解析PDF内容为文本
   - 存储到本地 `static/pdfs/` 目录
   - 前端可查看本地PDF文件

3. **财联社电报**
   - 实时获取财联社电报快讯
   - 补充市场热点信息

4. **智能分类**
   - 自动将公告分类到对应的事件类型
   - 支持多种事件类型（财务报告、重大事项、融资公告等）

5. **去重机制**
   - 基于标题和日期自动去重
   - 避免重复数据

## 使用方法

### 基本用法

获取最近1天的数据（包含PDF处理）：

```bash
cd backend
uv run python spider/update/update_events.py
```

### 高级选项

获取最近N天的数据：

```bash
uv run python spider/update/update_events.py --days 3
```

跳过PDF处理（仅获取基本信息，更快）：

```bash
uv run python spider/update/update_events.py --no-pdf
```

组合使用：

```bash
# 获取最近3天数据，但不处理PDF
uv run python spider/update/update_events.py --days 3 --no-pdf
```

## 数据流程

```
1. 获取三大交易所公告列表
   ↓
2. 下载并解析PDF文件（可选）
   - 保存到 static/pdfs/
   - 解析文本内容
   ↓
3. 获取财联社电报
   ↓
4. 转换为统一格式
   - 映射事件类型
   - 提取股票信息
   ↓
5. 保存到数据库
   - 去重检查
   - 批量保存
```

## 输出说明

### PDF文件

- 存储位置: `backend/static/pdfs/`
- 文件命名: `{MD5_HASH}.pdf`
- 访问URL: `/static/pdfs/{filename}`
- 前端点击时跳转到本地PDF

### 数据库字段

- `title`: 公告标题
- `content`: PDF解析的文本内容（或标题）
- `announcement_date`: 公告日期
- `source`: 数据来源（三大交易所/财联社）
- `original_url`: 本地PDF路径（或原始链接）
- `event_type`: 事件类型
- `event_category`: 事件分类
- `stock_code`: 股票代码
- `stock_name`: 股票名称

## 性能优化

1. **并发下载**: PDF下载支持并发（默认10个）
2. **增量更新**: 只处理新数据，跳过已存在的记录
3. **错误恢复**: 单个失败不影响整体流程

## 依赖项

新增依赖已添加到 `pyproject.toml`:

- `PyPDF2`: PDF解析
- `aiohttp`: 异步HTTP客户端
- `aiofiles`: 异步文件操作

## 注意事项

1. **首次运行**: 第一次运行会下载大量PDF，需要较长时间
2. **磁盘空间**: PDF文件会占用存储空间，定期清理 `static/pdfs/` 目录
3. **网络稳定**: PDF下载需要稳定的网络连接
4. **并发限制**: 如果网络不稳定，可以修改 `max_concurrent` 参数降低并发数

## 定时任务

建议配置定时任务自动更新：

### Linux (crontab)

```bash
# 每天凌晨2点更新
0 2 * * * cd /path/to/stock_news/backend && uv run python spider/update/update_events.py
```

### Windows (任务计划程序)

创建定时任务，每天运行：

```
程序: uv
参数: run python spider/update/update_events.py
工作目录: D:\study\stock_news\backend
```

## 监控和日志

运行时会显示详细进度：

- ✓ 成功操作
- ✗ 失败操作
- 进度条（tqdm）
- 统计信息（新增/跳过数量）

## 故障排查

### PDF下载失败

- 检查网络连接
- 检查URL是否有效
- 查看"下载失败"日志

### 数据库连接错误

- 确认MongoDB正在运行
- 检查 `MONGODB_URL` 配置

### 内存不足

- 使用 `--no-pdf` 跳过PDF处理
- 减少 `--days` 参数
- 降低并发数（修改代码中的 `max_concurrent`）

# Spider Scripts 使用说明

本目录包含用于数据采集和AI分析的脚本。

## 数据来源

| 数据源 | 说明 | 特性 |
|--------|------|------|
| **上交所** (SSE) | 上海证券交易所公告 | PDF自动下载，支持多类别，自动分页 |
| **深交所** (SZSE) | 深圳证券交易所公告 | PDF自动下载，支持多类别，POST请求 |
| **北交所** (BSE) | 北京证券交易所公告 | PDF自动下载，13个类别，JSONP格式 |
| **财联社电报** | 实时快讯 | 需AI分类 |

## 脚本说明

### 1. 整合更新脚本 (`update/update_events.py`)

整合三大交易所公告和财联社电报，支持PDF自动下载和解析。

```bash
# 基本用法（获取1天数据，包含PDF）
uv run python spider/update/update_events.py

# 获取最近7天的数据
uv run python spider/update/update_events.py --days 7

# 快速模式（不下载PDF）
uv run python spider/update/update_events.py --days 7 --no-pdf
```

**输出示例**：
```
============================================================
开始更新事件数据 (最近7天)
============================================================

##############################################################
# 日期: 2026-01-30
##############################################################

============================================================
获取 2026-01-30 的三大交易所公告
============================================================

[1/3] 获取上交所公告...
  ✓ 上交所: 492 条

[2/3] 获取深交所公告...
  ✓ 深交所: 1203 条

[3/3] 获取北交所公告...
  ✓ 北交所: 40 条

总计获取 1735 条公告

============================================================
批量处理PDF文件
============================================================

上海证券交易所:
  开始下载并解析 492 个PDF文件（并发数: 10）...
  PDF处理完成: 成功 490/492

...
```

**参数说明**：
- `--days N`: 获取最近N天的数据（默认：1）
- `--no-pdf`: 跳过PDF下载和解析

### 2. AI分析脚本 (`analyze/analyze_events.py`)

对已采集的事件进行AI分析。**一次调用完成分类、评分和实体提取**。

```bash
# 分析所有待分析的事件（默认并发5个）
uv run python spider/analyze/analyze_events.py

# 提高并发数以加快速度（并发10个）
uv run python spider/analyze/analyze_events.py --concurrency 10

# 分析最近7天的事件
uv run python spider/analyze/analyze_events.py --days 7

# 只分析特定类别的事件
uv run python spider/analyze/analyze_events.py --category company_updates

# 最多分析100条事件
uv run python spider/analyze/analyze_events.py --limit 100

# 组合使用
uv run python spider/analyze/analyze_events.py --days 3 --category company_updates --concurrency 10
```

**并发建议**：
- 默认并发：5（稳定，适合大多数情况）
- 快速分析：10（速度提升2倍）
- 高速模式：15-20（速度提升3-4倍，注意API限流）

**AI分析参数**：
- `--limit N`: 最多分析N条事件（默认：1000）
- `--days N`: 只分析最近N天的事件
- `--category CAT`: 按事件类别筛选：
  - `global_events` - 全球大事
  - `policy_trends` - 政策风向
  - `industry_trends` - 行业动向
  - `company_updates` - 公司动态
- `--event-type TYPE`: 按事件类型筛选
- `--concurrency N` 或 `-c N`: 并发分析数量（默认：5）

## 交易所爬虫

### 上交所爬虫 (`common/sse_notice_fetcher.py`)

```python
from spider.common.sse_notice_fetcher import SSENoticeFetcher

fetcher = SSENoticeFetcher()
notices = fetcher.fetch_notices_by_date(date)  # 获取指定日期的公告
```

**特点**：
- JSONP格式响应
- 2D数组数据结构
- 自动分页处理
- PDF URL提取

### 深交所爬虫 (`common/szse_notice_fetcher.py`)

```python
from spider.common.szse_notice_fetcher import SZSENoticeFetcher

fetcher = SZSENoticeFetcher()
notices = fetcher.fetch_notices_by_date(date)  # 获取指定日期的公告
```

**特点**：
- POST请求，JSON格式
- 支持大类别筛选
- 自动分页处理
- PDF URL提取

### 北交所爬虫 (`common/bse_notice_fetcher.py`)

```python
from spider.common.bse_notice_fetcher import BSENoticeFetcher

fetcher = BSENoticeFetcher()

# 获取所有类别
all_subtypes = []
for category_name, subtypes in fetcher.categories.items():
    all_subtypes.extend(subtypes)

notices = fetcher.fetch_notices_by_date(date, disclosure_subtypes=all_subtypes)
```

**特点**：
- JSONP格式响应
- 13个公告类别
- 支持类别筛选
- PDF URL提取

## PDF处理服务

PDF处理服务 (`app/services/pdf_service.py`) 提供以下功能：

### 自动下载

- 异步并发下载（默认10个并发）
- 自动去重（MD5哈希命名）
- 错误重试机制

### 文本解析

- 使用PyPDF2提取文本
- 支持多页PDF
- 自动处理换行和空格

### 存储

- 存储位置：`backend/static/pdfs/`
- 文件命名：`{MD5_HASH}.pdf`
- 访问URL：`/static/pdfs/{filename}`

## 典型工作流程

### 首次使用

```bash
# 1. 采集数据（获取30天公告和PDF）
uv run python spider/update/update_events.py --days 30

# 2. AI分析（自动包含分类）
uv run python spider/analyze/analyze_events.py --concurrency 10
```

### 日常更新

```bash
# 1. 增量更新数据
uv run python spider/update/update_events.py

# 2. 分析新数据
uv run python spider/analyze/analyze_events.py --days 1 --concurrency 10
```

## 事件分类体系

### 交易所公告分类

系统会根据公告标题和类型自动分类：

| 交易所 | 公告类型 | 映射到事件类型 |
|--------|----------|---------------|
| 上交所 | 年报、半年报、季报 | FINANCIAL_REPORT |
| 深交所 | 财务报告、业绩预告 | FINANCIAL_REPORT |
| 北交所 | 年度报告、半年度报告 | FINANCIAL_REPORT |
| 三大所 | 董事会、监事会、股东大会 | MAJOR_EVENT |
| 三大所 | 分红、增发、配股 | FINANCING_ANNOUNCEMENT |
| 三大所 | 股权变动、减持、增持 | SHAREHOLDING_CHANGE |
| 三大所 | 资产重组、收购 | ASSET_RESTRUCTURING |
| 三大所 | 风险提示、退市风险 | RISK_WARNING |
| 三大所 | 人事变动、名称变更 | INFO_CHANGE |

### AI分类（财联社电报）

| 大类 | 英文标识 | 子类型 |
|-----|---------|--------|
| 全球大事 | `global_events` | 宏观地缘 |
| 政策风向 | `policy_trends` | 监管政策、市场情绪 |
| 行业动向 | `industry_trends` | 产业链驱动、核心板块 |
| 公司动态 | `company_updates` | 重大事项、财务报告、融资公告、风险提示、资产重组、信息变更、持股变动 |

## 数据流程

```
1. 获取三大交易所公告列表
   ↓
2. 下载PDF文件到本地
   ↓
3. 解析PDF文本内容
   ↓
4. 映射公告类型到事件类型
   ↓
5. 获取财联社电报
   ↓
6. 统一格式保存到数据库
   ↓
7. AI分析（分类、评分、实体提取）
```

## 注意事项

1. **AI分析优化**：系统将分类、评分、实体提取合并为一次 LLM 调用，降低成本并提高速度
2. **PDF存储**：PDF文件会占用磁盘空间，定期清理 `static/pdfs/` 目录
3. **网络稳定**：PDF下载需要稳定的网络连接，如遇问题可使用 `--no-pdf` 跳过
4. **并发限制**：如果网络不稳定，可以修改代码中的 `max_concurrent` 参数降低并发数
5. **分离运行**：爬虫和AI分析完全独立，可以先完成所有数据采集，再统一进行AI分析
6. **自动去重**：基于标题和日期自动去重，避免重复数据

## 详细文档

更多更新脚本的详细用法，请参考 [update/README.md](./update/README.md)

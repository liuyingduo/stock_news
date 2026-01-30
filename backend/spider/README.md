# Spider Scripts 使用说明

本目录包含用于数据采集和AI分析的脚本。

## 数据来源

| 接口 | 来源 | 分类方式 |
|------|------|----------|
| `stock_notice_report` | 东方财富-沪深京A股公告 | 类型已知，直接映射 |
| `stock_info_global_cls` | 财联社电报 | 需要AI分类 |

## 脚本说明

### 1. 初始化脚本 (`init/init_events.py`)
首次使用时运行，获取历史金融事件数据。

```bash
# 获取最近7天的公告和电报
uv run python spider/run_init.py

# 获取最近30天的数据
uv run python spider/run_init.py --days 30

# 不清空已有数据
uv run python spider/run_init.py --no-clear
```

### 2. 更新脚本 (`update/update_events.py`)
增量更新最新的事件数据。

```bash
# 更新今日数据
uv run python spider/run_update.py

# 更新最近3天数据
uv run python spider/run_update.py --days 3
```

### 3. 实时监控脚本 (`update/telegraph_monitor.py`)
实时监听财联社电报，自动入库并触发AI分析。适合长期运行。

```bash
uv run python spider/update/telegraph_monitor.py
```
* 按 `Ctrl+C` 停止监控


### 3. AI分析脚本 (`analyze/analyze_events.py`)
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

## 参数说明

### 数据采集参数
- `--days N` - 获取最近N天的数据（默认：7）
- `--no-clear` - 不清空已有数据（仅初始化脚本）

### AI分析参数
- `--limit N` - 最多分析N条事件（默认：1000）
- `--days N` - 只分析最近N天的事件
- `--category CAT` - 按事件类别筛选：
  - `global_events` - 全球大事
  - `policy_trends` - 政策风向
  - `industry_trends` - 行业动向
  - `company_updates` - 公司动态
- `--event-type TYPE` - 按事件类型筛选
- `--concurrency N` 或 `-c N` - 并发分析数量（默认：5）

## 典型工作流程

### 首次使用

```bash
# 1. 初始化数据
uv run python spider/run_init.py --days 30

# 2. AI分析（自动包含分类）
uv run python spider/analyze/analyze_events.py --concurrency 10
```

### 日常更新

```bash
# 1. 增量更新数据
uv run python spider/run_update.py

# 2. 分析新数据
uv run python spider/analyze/analyze_events.py --days 1 --concurrency 10
```

## 事件分类体系

| 大类 | 英文标识 | 子类型 |
|-----|---------|--------|
| 全球大事 | `global_events` | 宏观地缘 |
| 政策风向 | `policy_trends` | 监管政策、市场情绪 |
| 行业动向 | `industry_trends` | 产业链驱动、核心板块 |
| 公司动态 | `company_updates` | 重大事项、财务报告、融资公告、风险提示、资产重组、信息变更、持股变动 |

## 注意事项

1. **AI分析优化**：系统将分类、评分、实体提取合并为一次 LLM 调用，降低成本并提高速度
2. **自动分类**：财联社电报等需要分类的事件会自动进行AI分类
3. **AI分析配置**：需要配置 `ZHIPU_API_KEY` 环境变量
4. **数据库**：确保MongoDB服务正在运行
5. **分离运行**：爬虫和AI分析完全独立，可以先完成所有数据采集，再统一进行AI分析

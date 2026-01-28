# Spider Scripts 使用说明

本目录包含用于数据采集和AI分析的脚本。

## 脚本说明

### 1. 初始化脚本 (`init/init_events.py`)
首次使用时运行，获取历史金融事件数据。

```bash
# 获取热门股票的最近30天新闻
uv run python spider/init/init_events.py --stocks 20 --days 30

# 获取所有A股的最近30天新闻（注意：可能需要较长时间）
uv run python spider/init/init_events.py --all --days 30
```

### 2. 更新脚本 (`update/update_events.py`)
增量更新最新的事件数据。

```bash
# 更新热门股票的最近1天新闻
uv run python spider/update/update_events.py --stocks 10 --days 1

# 更新所有A股的最近1天新闻
uv run python spider/update/update_events.py --all --days 1
```

### 3. AI分析脚本 (`analyze/analyze_events.py`)
对已采集的事件进行AI分析，提取影响的板块、股票、原材料等信息。

**性能优化**：支持并发分析，大幅提升速度！

```bash
# 分析所有待分析的事件（默认并发5个）
uv run python spider/analyze/analyze_events.py

# 提高并发数以加快速度（并发10个）
uv run python spider/analyze/analyze_events.py --concurrency 10

# 高速模式（并发20个，快速分析大量数据）
uv run python spider/analyze/analyze_events.py -c 20

# 分析最近7天的事件
uv run python spider/analyze/analyze_events.py --days 7

# 只分析核心驱动类别的事件
uv run python spider/analyze/analyze_events.py --category core_driver

# 最多分析100条事件
uv run python spider/analyze/analyze_events.py --limit 100

# 组合使用：高速分析最近3天的核心驱动事件
uv run python spider/analyze/analyze_events.py --days 3 --category core_driver --concurrency 15
```

**并发建议**：
- 默认并发：5（稳定，适合大多数情况）
- 快速分析：10（速度提升2倍）
- 高速模式：15-20（速度提升3-4倍，注意API限流）
- 超高并发：30+（可能触发API限流，慎用）

### 4. 检查工具脚本 (`analyze/check_*.py`)

#### 检查待分析事件 (`check_pending_events.py`)
查看数据库中有多少待分析的事件，以及最近的事件情况。

```bash
# 查看待分析的事件统计
uv run python spider/analyze/check_pending_events.py
```

输出信息：
- 数据库中总事件数
- 已分析/未分析的事件数量
- 最近7天的事件数量
- 列出前5个待分析的事件

#### 检查并重试失败事件 (`check_failed_events.py`)
查找AI分析失败的事件，并可以重新分析它们。

```bash
# 检查失败的事件并可选择重新分析
uv run python spider/analyze/check_failed_events.py
```

功能：
- 统计失败的分析数量
- 列出前10个失败的事件
- 交互式确认是否重新分析
- 并发重新分析（并发数5）
- 显示重新分析的结果统计

## 便捷脚本

为了方便使用，提供了以下便捷脚本：

- `spider/run_init.py` - 运行初始化
- `spider/run_update.py` - 运行更新
- `spider/run_analysis.py` - 运行AI分析

使用方法与直接运行对应脚本相同。

## 参数说明

### 通用参数

- `--stocks N` - 获取前N只热门股票的新闻（默认：init为20，update为10）
- `--all` - 获取所有A股股票的新闻（注意：数据量大，耗时长）
- `--days N` - 只处理/保存最近N天的数据（不指定则保存全部）

### AI分析专用参数

- `--limit N` - 最多分析N条事件（默认：1000）
- `--days N` - 只分析最近N天的事件
- `--category CAT` - 按事件类别筛选：
  - `core_driver` - 核心驱动
  - `special_situation` - 特殊机遇
  - `industrial_chain` - 产业链
  - `sentiment_flows` - 市场情绪
  - `macro_geopolitics` - 宏观地缘
- `--event-type TYPE` - 按事件类型筛选（如：dividend, ma, repurchase等）
- `--concurrency N` 或 `-c N` - 并发分析数量（默认：5）

## 典型工作流程

1. **首次使用**：初始化数据
   ```bash
   uv run python spider/init/init_events.py --all --days 30
   ```

2. **检查状态**：查看待分析的事件
   ```bash
   uv run python spider/analyze/check_pending_events.py
   ```

3. **AI分析**：对采集的事件进行分析（支持并发加速）
   ```bash
   # 标准速度（并发5个）
   uv run python spider/analyze/analyze_events.py --days 30

   # 高速模式（并发15个）
   uv run python spider/analyze/analyze_events.py --days 30 --concurrency 15
   ```

4. **处理失败事件**：检查并重试分析失败的事件
   ```bash
   uv run python spider/analyze/check_failed_events.py
   # 脚本会询问是否重新分析，输入 y 确认
   ```

5. **日常更新**：增量更新最新数据
   ```bash
   # 更新数据
   uv run python spider/update/update_events.py --all --days 1

   # 检查待分析事件
   uv run python spider/analyze/check_pending_events.py

   # 快速分析新数据（并发10个）
   uv run python spider/analyze/analyze_events.py --days 1 --concurrency 10

   # 定期检查失败事件
   uv run python spider/analyze/check_failed_events.py
   ```

## 注意事项

1. **API限制**：爬虫脚本每只股票之间有0.5秒延迟，避免请求过快被限制
2. **AI分析并发**：
   - 增加并发数可显著提升速度，但可能触发API限流
   - 建议从并发5开始，逐步增加到10、15、20
   - 如果遇到限流错误，降低并发数即可
3. **AI分析配置**：需要配置 `ZHIPU_API_KEY` 环境变量
4. **数据量**：使用 `--all` 参数会处理所有A股（约5000+只），请确保有足够时间
5. **数据库**：确保MongoDB服务正在运行
6. **分离运行**：爬虫和AI分析完全独立，可以先完成所有数据采集，再统一进行AI分析
7. **失败处理**：
   - 定期运行 `check_failed_events.py` 检查失败的分析
   - 使用修复后的代码重新分析失败的事件
   - 失败通常是由于API临时问题或JSON解析错误，重试通常会成功

# 金融事件数据采集与分析系统

本目录包含用于自动采集、处理和分析金融市场事件的脚本集合。系统支持从上交所、深交所、北交所及财联社电报获取数据，并利用 AI 进行深度分析。

## 核心功能

1.  **全自动监控服务** (`update/update_events.py`)
    *   **7x24小时运行**：作为后台服务持续运行。
    *   **双路并发**：
        *   **交易所公告**：每 30 分钟轮询一次（上交所、深交所、北交所）。
        *   **财联社电报**：每 10 秒刷新一次。
    *   **智能 PDF 处理**：
        *   自动绕过 WAF 防爬验证（如上交所）。
        *   自动下载并解析 PDF 内容。
        *   **自动清理**：解析完成后立即删除临时文件，不占用磁盘空间。
    *   **数据入库**：自动去重并存入 MongoDB。

2.  **AI 智能分析** (`analyze/analyze_events.py`)
    *   对采集到的事件进行分类、评分和实体提取。
    *   支持按日期、类别筛选分析。

## 快速开始

### 1. 启动监控服务

这是最常用的运行方式。服务启动后将持续采集最新数据。

```bash
uv run python spider/update/update_events.py
```

**输出示例**：
```text
============================================================
Stock News Monitor Service Started
============================================================
启动证券交易所监控 (间隔: 30分钟)
启动财联社电报监控 (间隔: 10秒)

[11:00:00] 开始检查交易所公告...
[11:00:05] 批量处理PDF文件...
  WAF detected (SSE). Attempting to bypass...
  Cookie calculated: 698015...
  WAF bypass successful.
  已清理本地PDF文件: xxxxx.pdf
[11:00:10] 交易所更新完成: 新增 5 条

[11:00:20] 财联社更新: 新增 2 条
```

### 2. 运行 AI 分析

建议配合监控服务使用，定期或按需对新入库的事件进行分析。

```bash
# 基本用法：分析等待处理的事件
uv run python spider/analyze/analyze_events.py

# 高级选项
uv run python spider/analyze/analyze_events.py --days 1       # 只分析最近1天
uv run python spider/analyze/analyze_events.py --concurrency 10 # 提高并发数
```

## 系统架构与数据源

| 数据源 | 特性 | 处理逻辑 |
|--------|------|----------|
| **上交所** (SSE) | WAF防护，JSONP | 自动计算 `acw_sc__v2` Cookie 绕过防护 |
| **深交所** (SZSE) | POST请求 | 模拟浏览器 headers |
| **北交所** (BSE) | 多类别 | 聚合13个子类别公告 |
| **财联社** | 实时流 | 需后端 AI 进行二次分类 |

### 目录结构

*   `update/update_events.py`: **监控主程序**。
*   `analyze/analyze_events.py`: AI 分析脚本。
*   `common/`: 爬虫底层实现及工具库。
    *   `sse_waf_solver.py`: 上交所 WAF 解算器。
    *   `*_notice_fetcher.py`: 各交易所抓取器。
*   `app/services/pdf_service.py`: PDF 下载、解析与清理服务。

## PDF 处理机制

系统内置了高效的 PDF 处理流程：
1.  **检测**：识别公告中的 PDF 链接。
2.  **下载**：使用 `aiohttp` 异步下载，自动处理反爬（WAF）。
3.  **解析**：提取文本内容用于后续 AI 分析。
4.  **清理**：**解析后立即删除本地文件**，数据库仅保留原文链接 (`url`) 和解析出的文本 (`content`)，`local_pdf_url` 字段将为空。

## 依赖项

项目依赖 `uv` 进行包管理，核心依赖包括：
*   `aiohttp`, `aiofiles`: 异步网络与文件与操作。
*   `PyPDF2`: PDF 文本提取。
*   `akshare`: 金融数据接口。
*   `selenium` (可选): 仅用于调试复杂反爬。

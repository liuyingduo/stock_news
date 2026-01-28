"""
便捷脚本：使用 backend 环境运行 AI 分析

使用示例:
    # 分析所有待分析的事件（默认并发5个）
    uv run python spider/run_analysis.py

    # 分析最近7天的事件
    uv run python spider/run_analysis.py --days 7

    # 只分析核心驱动类别的事件
    uv run python spider/run_analysis.py --category core_driver

    # 最多分析100条事件
    uv run python spider/run_analysis.py --limit 100

    # 提高并发数以加快速度（并发10个）
    uv run python spider/run_analysis.py --concurrency 10

    # 高速模式（并发20个，适合快速分析大量数据）
    uv run python spider/run_analysis.py -c 20
"""
import subprocess
import sys
import os

# 切换到 backend 目录
# 当前文件在 backend/spider/run_analysis.py
# 需要切换到 backend 目录
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
os.chdir(backend_dir)

# 运行分析脚本
# 脚本位于 backend/spider/analyze/analyze_events.py
analyze_script = os.path.join('spider', 'analyze', 'analyze_events.py')
result = subprocess.run([sys.executable, analyze_script] + sys.argv[1:])

sys.exit(result.returncode)

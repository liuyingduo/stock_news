"""
便捷脚本：使用 backend 环境运行 AI 分析
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

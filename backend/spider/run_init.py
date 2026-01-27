"""
便捷脚本：使用 backend 环境运行初始化爬虫
"""
import subprocess
import sys
import os

# 切换到 backend 目录
# 当前文件在 backend/spider/run_init.py
# 需要切换到 backend 目录
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
os.chdir(backend_dir)

# 运行初始化脚本
# 脚本位于 backend/spider/init/init_events.py
init_script = os.path.join('spider', 'init', 'init_events.py')
result = subprocess.run([sys.executable, init_script] + sys.argv[1:])

sys.exit(result.returncode)

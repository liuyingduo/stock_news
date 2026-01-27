"""
便捷初始化脚本 - 在 backend 目录运行
"""
import sys
import os

# 添加 spider/init 到路径
spider_init = os.path.join(os.path.dirname(__file__), 'spider', 'init')
sys.path.insert(0, spider_init)

# 导入并运行
import init_events

if __name__ == "__main__":
    import asyncio
    asyncio.run(init_events.main())

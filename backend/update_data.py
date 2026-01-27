"""
便捷更新脚本 - 在 backend 目录运行
"""
import sys
import os

# 添加 spider/update 到路径
spider_update = os.path.join(os.path.dirname(__file__), 'spider', 'update')
sys.path.insert(0, spider_update)

# 导入并运行
import update_events

if __name__ == "__main__":
    import asyncio
    asyncio.run(update_events.main())

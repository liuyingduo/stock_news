"""
检查数据库中待分析的事件
"""
import sys
import os
import asyncio

# 添加 backend 目录到 Python 路径
# 当前脚本在 backend/spider/analyze/ 目录下
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_dir)

from app.services.database_service import db_service
from app.core.database import connect_to_mongo, close_mongo_connection
from datetime import datetime, timedelta


async def check_pending_events():
    """检查待分析的事件"""
    print("=" * 60)
    print("检查待分析的事件")
    print("=" * 60)

    await connect_to_mongo()

    # 获取所有事件
    events, total = await db_service.get_events(limit=1000)

    print(f"\n数据库中总共有 {total} 个事件\n")

    # 统计已分析和未分析的数量
    analyzed_count = 0
    pending_count = 0

    pending_events = []
    recent_events = []

    cutoff_date = datetime.now() - timedelta(days=7)

    for event in events:
        has_analysis = event.get("ai_analysis") is not None
        if has_analysis:
            analyzed_count += 1
        else:
            pending_count += 1
            pending_events.append(event)

        # 检查最近7天的事件
        announcement_date = event.get("announcement_date")
        if announcement_date:
            if isinstance(announcement_date, str):
                try:
                    announcement_date = datetime.fromisoformat(announcement_date.replace('Z', '+00:00'))
                except:
                    pass

            if hasattr(announcement_date, 'timestamp'):
                if announcement_date > cutoff_date:
                    recent_events.append(event)
                    if not has_analysis:
                        pending_events.append(event)

    print(f"已分析的事件: {analyzed_count}")
    print(f"未分析的事件: {pending_count}")
    print(f"最近7天的事件: {len(recent_events)}")

    if pending_count > 0:
        print(f"\n找到 {pending_count} 个待分析的事件")
        print("\n前5个待分析的事件：")
        for i, event in enumerate(pending_events[:5], 1):
            print(f"{i}. {event['title'][:60]}...")
            print(f"   日期: {event.get('announcement_date')}")
            print(f"   类别: {event.get('event_category')}")
            print()
    else:
        print("\n✓ 所有事件都已被分析！")

    if recent_events:
        print(f"\n最近7天的事件示例：")
        for i, event in enumerate(recent_events[:3], 1):
            print(f"{i}. {event['title'][:60]}...")
            has_analysis = event.get("ai_analysis") is not None
            print(f"   已分析: {'是' if has_analysis else '否'}")
            print()

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(check_pending_events())

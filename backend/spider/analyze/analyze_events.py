"""
AI 分析脚本 - 对未分析的事件进行 AI 分析
"""
import sys
import os
import asyncio

# 添加 backend 目录到 Python 路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_dir)

from app.services.database_service import db_service
from app.services.ai_service import get_ai_service
from app.models import EventUpdate
from app.core.database import connect_to_mongo, close_mongo_connection

async def analyze_events():
    """对未分析的事件进行 AI 分析"""
    print("=" * 50)
    print("Starting AI analysis...")
    print("=" * 50)

    # 连接数据库
    await connect_to_mongo()

    ai_service = get_ai_service()
    if not ai_service:
        print("Error: AI service not available. Check API key.")
        return

    # 获取未分析的事件
    # 注意：这里假设 ai_analysis 为 null 的事件需要分析
    # 也可以根据需要修改查询条件
    events, count = await db_service.get_events(limit=1000) # 先获取一部分，避免内存爆炸
    
    # 过滤出没有 AI 分析结果的事件
    # 这里的过滤逻辑可能不够高效，如果数据量大，应该在数据库层面筛选
    # 但由于 get_events 接口限制，我们先这样处理
    pending_events = []
    for event in events:
        if not event.get("ai_analysis"):
             pending_events.append(event)
    
    print(f"Found {len(pending_events)} events pending analysis")

    processed_count = 0
    for event_data in pending_events:
        try:
            print(f"Analyzing event: {event_data['title'][:50]}...")
            
            # 调用 AI 服务进行分析
            ai_analysis = await ai_service.analyze_event(
                event_data["title"], 
                event_data["content"]
            )

            # 更新数据库
            event_id = event_data["id"]
            await db_service.update_event(event_id, EventUpdate(ai_analysis=ai_analysis))

            # 更新关联的板块和股票
            if ai_analysis.affected_sectors:
                for sector in ai_analysis.affected_sectors:
                    await db_service.create_or_update_sector(
                        name=sector.name,
                        code=sector.code if sector.code else f"SECTOR_{sector.name}",
                    )

            if ai_analysis.affected_stocks:
                for stock in ai_analysis.affected_stocks:
                    await db_service.create_or_update_stock(
                        name=stock.name,
                        code=stock.code if stock.code else f"STOCK_{stock.name}",
                    )
            
            processed_count += 1
            print(f"Successfully analyzed event: {event_data['title'][:20]}...")

        except Exception as e:
            print(f"Error analyzing event {event_data.get('title', 'Unknown')}: {str(e)}")
            continue

    print("=" * 50)
    print(f"Analysis completed. Processed {processed_count} events.")
    print("=" * 50)

    # 关闭数据库连接
    await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(analyze_events())

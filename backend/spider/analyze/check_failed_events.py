"""
检查并重新分析AI失败的事件
"""
import sys
import os
import asyncio

# 添加 backend 目录到 Python 路径
# 当前脚本在 backend/spider/analyze/ 目录下
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_dir)

from app.services.database_service import db_service
from app.services.ai_service import get_ai_service
from app.models import EventUpdate
from app.core.database import connect_to_mongo, close_mongo_connection
from datetime import datetime


async def check_and_retry_failed_events():
    """检查并重试失败的事件"""
    print("=" * 60)
    print("检查AI分析失败的事件")
    print("=" * 60)

    await connect_to_mongo()

    # 获取所有事件
    events, total = await db_service.get_events(limit=2000)

    print(f"\n数据库中总共有 {total} 个事件\n")

    # 查找分析失败的事件
    failed_events = []
    successful_events = []
    no_analysis_events = []

    for event in events:
        ai_analysis = event.get("ai_analysis")

        if ai_analysis is None:
            no_analysis_events.append(event)
        elif isinstance(ai_analysis, dict):
            # 检查是否是失败的分析
            reason = ai_analysis.get("impact_reason", "")
            score = ai_analysis.get("impact_score", 0)

            if "AI 分析失败" in reason or "无法生成打分理由" in reason:
                failed_events.append(event)
            else:
                successful_events.append(event)

    print(f"统计结果：")
    print(f"  - 未分析的事件: {len(no_analysis_events)}")
    print(f"  - 分析成功的事件: {len(successful_events)}")
    print(f"  - 分析失败的事件: {len(failed_events)}")

    if failed_events:
        print(f"\n找到 {len(failed_events)} 个分析失败的事件：")
        print("\n前10个失败的事件：")
        for i, event in enumerate(failed_events[:10], 1):
            print(f"{i}. {event['title'][:60]}...")
            ai_analysis = event.get("ai_analysis", {})
            if isinstance(ai_analysis, dict):
                print(f"   评分: {ai_analysis.get('impact_score', 'N/A')}")
                print(f"   理由: {ai_analysis.get('impact_reason', 'N/A')[:60]}...")
            print()

    if no_analysis_events:
        print(f"\n还有 {len(no_analysis_events)} 个未分析的事件")

    # 询问是否要重新分析失败的事件
    if failed_events:
        print("\n" + "=" * 60)
        choice = input(f"是否要重新分析这 {len(failed_events)} 个失败的事件？(y/n): ").strip().lower()

        if choice == 'y':
            ai_service = get_ai_service()
            if not ai_service:
                print("\nError: AI service not configured. Please set ZHIPU_API_KEY in .env")
                await close_mongo_connection()
                return

            print(f"\n开始重新分析 {len(failed_events)} 个失败的事件...")
            print("并发数: 5\n")

            semaphore = asyncio.Semaphore(5)

            async def retry_analyze(event_data: dict, index: int):
                async with semaphore:
                    try:
                        print(f"[{index}/{len(failed_events)}] 重试: {event_data['title'][:50]}...")

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

                        score = ai_analysis.impact_score if ai_analysis.impact_score else 0
                        reason = ai_analysis.impact_reason[:40] if ai_analysis.impact_reason else "No reason"
                        print(f"  ✓ Score: {score}/10 | Reason: {reason}...")
                        return True

                    except Exception as e:
                        print(f"  ✗ Error: {str(e)}")
                        return False

            # 创建所有任务
            tasks = [
                retry_analyze(event_data, idx)
                for idx, event_data in enumerate(failed_events, 1)
            ]

            # 并发执行所有任务
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 统计结果
            success_count = sum(1 for r in results if r is True)
            fail_count = sum(1 for r in results if r is False or isinstance(r, Exception))

            print("\n" + "=" * 60)
            print("重新分析完成")
            print("=" * 60)
            print(f"总数: {len(failed_events)}")
            print(f"成功: {success_count}")
            print(f"失败: {fail_count}")
            print("=" * 60)

    await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(check_and_retry_failed_events())

"""
AI 分析脚本 - 对事件进行 AI 分析
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional

# 添加 backend 目录到 Python 路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_dir)

from app.services.database_service import db_service
from app.services.ai_service import get_ai_service
from app.models import EventUpdate, EventCategory, EventType
from app.core.database import connect_to_mongo, close_mongo_connection


class EventAnalyzer:
    """事件分析器"""

    def __init__(self):
        """初始化分析器"""
        self.ai_service = None

    async def get_pending_events(self, limit: int = 1000, days: Optional[int] = None,
                                 category: Optional[str] = None,
                                 event_type: Optional[str] = None) -> list:
        """
        获取待分析的事件列表

        Args:
            limit: 最多获取多少条事件
            days: 只分析最近N天的事件
            category: 按事件类别筛选
            event_type: 按事件类型筛选

        Returns:
            待分析的事件列表
        """
        events, total = await db_service.get_events(
            limit=limit,
            category=category,
            event_type=event_type
        )

        # 过滤出没有 AI 分析结果的事件
        pending_events = []
        cutoff_date = None

        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)
            print(f"Filtering events newer than {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")

        for event in events:
            # 跳过已有分析的事件
            if event.get("ai_analysis"):
                continue

            # 检查日期过滤
            if cutoff_date is not None:
                announcement_date = event.get("announcement_date")
                if announcement_date:
                    # 处理字符串格式的日期
                    if isinstance(announcement_date, str):
                        try:
                            announcement_date = datetime.fromisoformat(announcement_date.replace('Z', '+00:00'))
                        except:
                            continue

                    # 转换为datetime对象（如果是其他格式）
                    if hasattr(announcement_date, 'timestamp'):
                        if announcement_date < cutoff_date:
                            continue

            pending_events.append(event)

        return pending_events

    async def analyze_event(self, event_data: dict, index: int, total: int) -> bool:
        """
        分析单个事件

        Args:
            event_data: 事件数据
            index: 当前索引
            total: 总数

        Returns:
            是否分析成功
        """
        try:
            print(f"[{index}/{total}] Analyzing: {event_data['title'][:60]}...")

            # 调用 AI 服务进行分析
            ai_analysis = await self.ai_service.analyze_event(
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

            # 显示分析结果摘要
            score = ai_analysis.impact_score if ai_analysis.impact_score else 0
            reason = ai_analysis.impact_reason[:50] if ai_analysis.impact_reason else "No reason"
            print(f"  ✓ Score: {score}/10 | Reason: {reason}...")

            return True

        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return False

    async def analyze(self, limit: int = 1000, days: Optional[int] = None,
                     category: Optional[str] = None, event_type: Optional[str] = None,
                     concurrency: int = 5):
        """
        批量分析事件

        Args:
            limit: 最多分析多少条事件
            days: 只分析最近N天的事件
            category: 按事件类别筛选
            event_type: 按事件类型筛选
            concurrency: 并发分析数量（默认：5）
        """
        print("=" * 60)
        print("Event AI Analysis")
        print("=" * 60)

        # 连接数据库
        await connect_to_mongo()

        # 获取 AI 服务
        self.ai_service = get_ai_service()
        if not self.ai_service:
            print("Error: AI service not configured. Please set ZHIPU_API_KEY in .env")
            await close_mongo_connection()
            return

        # 获取待分析的事件
        print("\nFetching pending events...")
        pending_events = await self.get_pending_events(
            limit=limit,
            days=days,
            category=category,
            event_type=event_type
        )

        if not pending_events:
            print("No pending events found.")
            await close_mongo_connection()
            return

        print(f"Found {len(pending_events)} events pending analysis")
        print(f"Concurrency level: {concurrency}\n")

        # 使用信号量控制并发数量
        semaphore = asyncio.Semaphore(concurrency)

        async def analyze_with_semaphore(event_data: dict, index: int):
            async with semaphore:
                return await self.analyze_event(event_data, index, len(pending_events))

        # 创建所有任务
        tasks = [
            analyze_with_semaphore(event_data, idx)
            for idx, event_data in enumerate(pending_events, 1)
        ]

        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计结果
        success_count = sum(1 for r in results if r is True)
        fail_count = sum(1 for r in results if r is False or isinstance(r, Exception))

        # 显示统计信息
        print("\n" + "=" * 60)
        print("Analysis Summary")
        print("=" * 60)
        print(f"Total events:  {len(pending_events)}")
        print(f"Successful:    {success_count}")
        print(f"Failed:        {fail_count}")
        print("=" * 60)

        # 关闭数据库连接
        await close_mongo_connection()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="对事件进行 AI 分析")
    parser.add_argument("--limit", type=int, default=1000, help="最多分析多少条事件（默认：1000）")
    parser.add_argument("--days", type=int, default=None, help="只分析最近N天的事件（默认：全部）")
    parser.add_argument("--category", type=str, default=None,
                       choices=["core_driver", "special_situation", "industrial_chain", "sentiment_flows", "macro_geopolitics"],
                       help="按事件类别筛选")
    parser.add_argument("--event-type", type=str, default=None, help="按事件类型筛选")
    parser.add_argument("--concurrency", "-c", type=int, default=5,
                       help="并发分析数量（默认：5，增加可提高速度但会占用更多API资源）")

    args = parser.parse_args()

    analyzer = EventAnalyzer()
    await analyzer.analyze(
        limit=args.limit,
        days=args.days,
        category=args.category,
        event_type=args.event_type,
        concurrency=args.concurrency
    )


if __name__ == "__main__":
    asyncio.run(main())

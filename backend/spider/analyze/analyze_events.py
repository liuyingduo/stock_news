"""
AI 分析脚本 - 对事件进行 AI 分析（包含分类、评分、提取）
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor
import time

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
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.completed_count = 0
        self.failed_count = 0
        self.start_time = None
        self.lock = asyncio.Lock()
        
        # 分类映射
        self.category_mapping = {
            "global_events": EventCategory.GLOBAL_EVENTS,
            "policy_trends": EventCategory.POLICY_TRENDS,
            "industry_trends": EventCategory.INDUSTRY_TRENDS,
            "company_updates": EventCategory.COMPANY_UPDATES,
        }
        
        self.type_mapping = {
            "macro_geopolitics": EventType.MACRO_GEOPOLITICS,
            "regulatory_policy": EventType.REGULATORY_POLICY,
            "market_sentiment": EventType.MARKET_SENTIMENT,
            "industrial_chain": EventType.INDUSTRIAL_CHAIN,
            "core_sector": EventType.CORE_SECTOR,
            "major_event": EventType.MAJOR_EVENT,
            "financial_report": EventType.FINANCIAL_REPORT,
            "financing_announcement": EventType.FINANCING_ANNOUNCEMENT,
            "risk_warning": EventType.RISK_WARNING,
            "asset_restructuring": EventType.ASSET_RESTRUCTURING,
            "info_change": EventType.INFO_CHANGE,
            "shareholding_change": EventType.SHAREHOLDING_CHANGE,
            "other": EventType.OTHER,
        }

    async def get_pending_events(self, limit: Optional[int] = None, days: Optional[int] = None,
                                 category: Optional[str] = None,
                                 event_type: Optional[str] = None) -> list:
        """
        获取待分析的事件列表
        """
        # 获取基础列表
        if limit is None:
            limit = 1000000
            
        events, total = await db_service.get_events(
            limit=limit,
            category=category,
            event_type=event_type
        )

        pending_events = []
        cutoff_date = None

        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)
            print(f"Filtering events newer than {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")

        for event in events:
            # 跳过已有分析且已分类的事件
            has_analysis = bool(event.get("ai_analysis"))
            has_category = bool(event.get("event_category"))
            
            # 如果已经分析过且有分类，跳过
            if has_analysis and has_category:
                continue

            # 检查日期过滤
            if cutoff_date is not None:
                announcement_date = event.get("announcement_date")
                if announcement_date:
                     try:
                        if isinstance(announcement_date, str):
                             announcement_date = datetime.fromisoformat(announcement_date.replace('Z', '+00:00'))
                        if hasattr(announcement_date, 'timestamp'):
                            if announcement_date < cutoff_date:
                                continue
                     except:
                        continue

            pending_events.append(event)

        return pending_events

    async def analyze_event(self, event_data: dict, index: int, total: int) -> Tuple[bool, Optional[dict], Optional[dict]]:
        """
        分析单个事件
        """
        try:
            # 检查是否需要分类
            current_category = event_data.get("event_category")
            needs_classification = (current_category is None) or event_data.get("needs_ai_classification", False)
            
            # 调用 AI 服务进行分析和分类（如果需要）
            result = await self.ai_service.analyze_and_classify(
                event_data["title"],
                event_data["content"],
                needs_classification=needs_classification
            )

            ai_analysis = result["ai_analysis"]
            
            # 准备更新数据
            update_dict = {"ai_analysis": ai_analysis}
            
            # 如果进行了分类，更新分类信息
            if needs_classification:
                cat_str = result.get("event_category")
                type_str = result.get("event_type")
                
                if cat_str and type_str:
                    new_category = self.category_mapping.get(cat_str, EventCategory.COMPANY_UPDATES)
                    new_type = self.type_mapping.get(type_str, EventType.OTHER)
                    
                    update_dict["event_category"] = new_category
                    update_dict["event_type"] = new_type

            return True, event_data, ai_analysis

        except Exception as e:
            print(f"Error analyzing event: {e}")
            return False, event_data, None

    async def process_pending_events(self, limit: Optional[int] = None, days: Optional[int] = None,
                     category: Optional[str] = None, event_type: Optional[str] = None,
                     concurrency: int = 20):
        """
        批量分析事件
        """
        print("=" * 60)
        print("Event AI Analysis & Classification")
        print("=" * 60)

        # 连接数据库
        # await connect_to_mongo()

        # 获取 AI 服务
        self.ai_service = get_ai_service()
        if not self.ai_service:
            print("Error: AI service not configured. Please set ZHIPU_API_KEY in .env")
            # await close_mongo_connection()
            return

        # 获取待分析的事件
        print("\nFetching pending events...")
        if limit:
            print(f"Limit: {limit} events")
        if days:
            print(f"Filtering events from the last {days} days")

        pending_events = await self.get_pending_events(
            limit=limit,
            days=days,
            category=category,
            event_type=event_type
        )

        if not pending_events:
            print("No pending events found.")
            # await close_mongo_connection()
            return

        print(f"Found {len(pending_events)} events pending analysis")
        print(f"Concurrency level: {concurrency}\n")

        # 记录开始时间
        self.start_time = time.time()
        self.completed_count = 0
        self.failed_count = 0

        # 使用信号量控制并发数量
        semaphore = asyncio.Semaphore(concurrency)

        async def analyze_with_semaphore(event_data: dict, index: int):
            async with semaphore:
                success, event, analysis = await self.analyze_event(event_data, index, len(pending_events))

                # 实时更新进度
                async with self.lock:
                    if success:
                        self.completed_count += 1
                    else:
                        self.failed_count += 1

                    total_processed = self.completed_count + self.failed_count
                    elapsed = time.time() - self.start_time
                    rate = total_processed / elapsed if elapsed > 0 else 0
                    eta = (len(pending_events) - total_processed) / rate if rate > 0 else 0

                    # 显示进度
                    print(f"\r[{total_processed}/{len(pending_events)}] "
                          f"✓{self.completed_count} ✗{self.failed_count} | "
                          f"Rate: {rate:.1f}/s | ETA: {eta:.0f}s", end="", flush=True)

                return success, event, analysis

        # 创建所有任务
        tasks = [
            analyze_with_semaphore(event_data, idx)
            for idx, event_data in enumerate(pending_events, 1)
        ]

        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        print()  # 换行

        # 批量更新数据库
        print("Updating database...")
        bulk_update_tasks = []
        sectors_to_update = set()
        stocks_to_update = set()

        for result in results:
            if isinstance(result, Exception):
                continue

            success, event, analysis = result
            if not success or not analysis:
                continue

            # 收集更新任务
            event_id = event["id"]
            bulk_update_tasks.append(
                db_service.update_event(event_id, EventUpdate(ai_analysis=analysis))
            )

            # 收集板块和股票（去重）
            if analysis.affected_sectors:
                for sector in analysis.affected_sectors:
                    sectors_to_update.add((sector.name, sector.code if sector.code else f"SECTOR_{sector.name}"))

            if analysis.affected_stocks:
                for stock in analysis.affected_stocks:
                    stocks_to_update.add((stock.name, stock.code if stock.code else f"STOCK_{stock.name}"))

        # 批量执行事件更新
        if bulk_update_tasks:
            # 使用批量并发更新，但限制并发数避免数据库压力过大
            batch_semaphore = asyncio.Semaphore(50)
            async def update_with_semaphore(task):
                async with batch_semaphore:
                    return await task

            batch_tasks = [update_with_semaphore(t) for t in bulk_update_tasks]
            await asyncio.gather(*batch_tasks, return_exceptions=True)

        # 批量更新板块和股票
        for sector_name, sector_code in sectors_to_update:
            await db_service.create_or_update_sector(name=sector_name, code=sector_code)

        for stock_name, stock_code in stocks_to_update:
            await db_service.create_or_update_stock(name=stock_name, code=stock_code)

        # 统计结果
        success_count = self.completed_count
        fail_count = self.failed_count

        # 显示统计信息
        print("\n" + "=" * 60)
        print("Analysis Summary")
        print("=" * 60)
        print(f"Total events:  {len(pending_events)}")
        print(f"Successful:    {success_count}")
        print(f"Failed:        {fail_count}")
        print("=" * 60)

        # 关闭数据库连接
        # await close_mongo_connection()

    async def analyze(self, limit: Optional[int] = None, days: Optional[int] = None,
                     category: Optional[str] = None, event_type: Optional[str] = None,
                     concurrency: int = 20):
        """
        批量分析事件（包含数据库连接管理）
        """
        # 连接数据库
        await connect_to_mongo()
        
        try:
            await self.process_pending_events(limit, days, category, event_type, concurrency)
        finally:
            # 关闭数据库连接
            await close_mongo_connection()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="对事件进行 AI 分析")
    parser.add_argument("--limit", type=int, default=None, help="最多分析多少条事件（默认：不限制）")
    parser.add_argument("--days", type=int, default=None, help="只分析最近N天的事件")
    parser.add_argument("--category", type=str, default=None,
                       choices=["global_events", "policy_trends", "industry_trends", "company_updates"],
                       help="按事件类别筛选")
    parser.add_argument("--event-type", type=str, default=None, help="按事件类型筛选")
    parser.add_argument("--concurrency", "-c", type=int, default=20,
                       help="并发分析数量（默认：20）")

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

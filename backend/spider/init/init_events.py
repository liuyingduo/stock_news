"""
初始化爬虫 - 获取历史金融事件数据
使用 akshare 获取数据并存储到 MongoDB
"""
import sys
import os

# 添加 backend 目录到 Python 路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_dir)

import akshare as ak
import asyncio
from datetime import datetime, timedelta
from typing import List, Optional
from app.models import EventCreate, EventCategory, EventType
from app.services.database_service import db_service
from app.core.database import connect_to_mongo, close_mongo_connection
from spider.common.notice_fetcher import fetch_notices_batch

from tqdm import tqdm



class EventInitializer:
    """事件初始化器"""

    def __init__(self):
        """初始化事件初始化器"""
        # 公告类型到 EventType 的映射
        self.notice_type_mapping = {
            "全部": EventType.OTHER,
            "重大事项": EventType.MAJOR_EVENT,
            "财务报告": EventType.FINANCIAL_REPORT,
            "融资公告": EventType.FINANCING_ANNOUNCEMENT,
            "风险提示": EventType.RISK_WARNING,
            "资产重组": EventType.ASSET_RESTRUCTURING,
            "信息变更": EventType.INFO_CHANGE,
            "持股变动": EventType.SHAREHOLDING_CHANGE,
        }

    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y%m%d",
            "%Y/%m/%d",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except (ValueError, TypeError):
                continue

        return datetime.now()

    async def fetch_stock_notices(self, days: int = 7, fetch_content: bool = True) -> List[dict]:
        """
        获取沪深京 A 股公告数据

        Args:
            days: 获取最近N天的公告
            fetch_content: 是否抓取公告详情页内容

        Returns:
            公告列表
        """
        all_notices = []
        notice_types = ["重大事项", "财务报告", "融资公告", "风险提示", "资产重组", "信息变更", "持股变动"]

        # 生成日期列表
        dates = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            dates.append(date.strftime("%Y%m%d"))

        print(f"Fetching notices for {len(dates)} days, {len(notice_types)} types...")

        # 第一步：收集所有公告基本信息
        for notice_type in tqdm(notice_types, desc="Fetching notice list"):
            event_type = self.notice_type_mapping.get(notice_type, EventType.OTHER)

            for date_str in dates:
                try:
                    df = ak.stock_notice_report(symbol=notice_type, date=date_str)
                    if df is None or df.empty:
                        continue

                    for _, row in df.iterrows():
                        title = row.get("公告标题", "")
                        url = row.get("网址", "")
                        
                        notice = {
                            "title": title,
                            "content": title,  # 先用标题，稍后批量抓取
                            "stock_code": row.get("代码", ""),
                            "stock_name": row.get("名称", ""),
                            "announcement_date": self._parse_date(row.get("公告日期", str(datetime.now()))),
                            "source": "东方财富-公告大全",
                            "original_url": url,
                            "event_type": event_type,
                            "event_category": EventCategory.COMPANY_UPDATES,
                        }
                        all_notices.append(notice)

                except Exception as e:
                    continue

        print(f"Fetched {len(all_notices)} notices")
        
        # 第二步：并发批量抓取详情页内容
        if fetch_content and all_notices:
            print(f"Fetching content from detail pages (concurrent, max 20 workers)...")
            all_notices = fetch_notices_batch(all_notices, max_workers=20)
            print("Content fetching completed")

        return all_notices

    async def fetch_cls_telegraph(self) -> List[dict]:
        """
        获取财联社电报数据

        Returns:
            电报列表
        """
        all_telegraphs = []

        try:
            print("Fetching CLS telegraph...")
            df = ak.stock_info_global_cls(symbol="全部")

            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    # 合并日期和时间
                    date_str = str(row.get("发布日期", ""))
                    time_str = str(row.get("发布时间", ""))
                    datetime_str = f"{date_str} {time_str}"

                    telegraph = {
                        "title": row.get("标题", ""),
                        "content": row.get("内容", row.get("标题", "")),
                        "announcement_date": self._parse_date(datetime_str),
                        "source": "财联社电报",
                        "original_url": "",
                        "event_type": EventType.OTHER,  # 需要 AI 分析
                        "event_category": None,  # 需要 AI 分析
                        "needs_ai_classification": True,  # 标记需要 AI 分类
                    }
                    all_telegraphs.append(telegraph)

            print(f"Fetched {len(all_telegraphs)} telegraphs")

        except Exception as e:
            print(f"Error fetching CLS telegraph: {str(e)}")

        return all_telegraphs

    async def process_and_save_events(self, events_data: List[dict]) -> int:
        """
        处理并保存事件到数据库

        Args:
            events_data: 事件数据列表

        Returns:
            保存的事件数量
        """
        saved_count = 0

        pbar = tqdm(events_data, desc="Saving events", unit="event")

        for event_data in pbar:
            try:
                event_type = event_data.get("event_type", EventType.OTHER)
                event_category = event_data.get("event_category")

                # 如果没有分类，默认归类为公司动态-其他
                if event_category is None:
                    event_category = EventCategory.COMPANY_UPDATES

                # 创建事件
                event_create = EventCreate(
                    title=event_data["title"],
                    content=event_data["content"],
                    event_category=event_category,
                    event_type=event_type,
                    announcement_date=event_data["announcement_date"],
                    source=event_data.get("source"),
                    original_url=event_data.get("original_url"),
                )

                # 保存到数据库
                await db_service.create_event(event_create)
                saved_count += 1

                if saved_count % 100 == 0:
                    pbar.set_description(f"Saved {saved_count} events")

            except Exception as e:
                continue

        return saved_count

    async def initialize(self, days: int = 7, clear_existing: bool = True):
        """
        初始化事件数据

        Args:
            days: 获取最近N天的公告数据
            clear_existing: 是否清空已有数据
        """
        print("=" * 50)
        print("Starting event initialization...")
        print("=" * 50)

        # 连接数据库
        await connect_to_mongo()

        # 创建数据库索引
        print("Creating database indexes...")
        await db_service.create_indexes()

        if clear_existing:
            # 清空已有数据
            print("Clearing existing events...")
            deleted_count = await db_service.delete_all_events()
            print(f"Deleted {deleted_count} existing events.")

        # 获取公告数据
        print("\n" + "=" * 50)
        print("Fetching stock notices...")
        print("=" * 50)
        notices = await self.fetch_stock_notices(days=days)

        # 获取财联社电报
        print("\n" + "=" * 50)
        print("Fetching CLS telegraph...")
        print("=" * 50)
        telegraphs = await self.fetch_cls_telegraph()

        # 合并所有数据
        all_events = notices + telegraphs

        if all_events:
            print("\n" + "=" * 50)
            print("Saving events to database...")
            print("=" * 50)
            saved_count = await self.process_and_save_events(all_events)
            print(f"\nSaved {saved_count} events total")

        print("\n" + "=" * 50)
        print("Event initialization completed!")
        print("=" * 50)

        # 关闭数据库连接
        await close_mongo_connection()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="初始化金融事件数据")
    parser.add_argument("--days", type=int, default=7, help="获取最近N天的公告数据（默认：7）")
    parser.add_argument("--no-clear", action="store_true", help="不清空已有数据")

    args = parser.parse_args()

    initializer = EventInitializer()
    await initializer.initialize(days=args.days, clear_existing=not args.no_clear)


if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")

"""
增量更新爬虫 - 获取最新的金融事件数据
使用 akshare 获取最新数据并存储到 MongoDB
"""
import sys
import os

# 添加 backend 目录到 Python 路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_dir)

import akshare as ak
import asyncio
from datetime import datetime, timedelta
from typing import List
from app.models import EventCreate, EventCategory, EventType
from app.services.database_service import db_service
from app.core.database import connect_to_mongo, close_mongo_connection
from spider.common.notice_fetcher import fetch_notice_content

from tqdm import tqdm


class EventUpdater:
    """事件更新器"""

    def __init__(self):
        """初始化事件更新器"""
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
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except (ValueError, TypeError):
                continue
        return datetime.now()

    async def fetch_stock_notices(self, days: int = 1, fetch_content: bool = True) -> List[dict]:
        """
        获取沪深京 A 股公告数据

        Args:
            days: 获取最近N天的公告

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
        if fetch_content:
            print("Note: Fetching full content from detail pages (this may take longer)")

        for notice_type in tqdm(notice_types, desc="Notice types"):
            event_type = self.notice_type_mapping.get(notice_type, EventType.OTHER)

            for date_str in dates:
                try:
                    df = ak.stock_notice_report(symbol=notice_type, date=date_str)
                    if df is None or df.empty:
                        continue

                    for _, row in df.iterrows():
                        title = row.get("公告标题", "")
                        url = row.get("网址", "")
                        
                        # 尝试获取完整内容
                        if fetch_content and url:
                            content = fetch_notice_content(url)
                            if not content:
                                content = title
                        else:
                            content = title
                        
                        notice = {
                            "title": title,
                            "content": content,
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

        print(f"Fetched {len(all_notices)} notices total")
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
                    date_str = str(row.get("发布日期", ""))
                    time_str = str(row.get("发布时间", ""))
                    datetime_str = f"{date_str} {time_str}"

                    telegraph = {
                        "title": row.get("标题", ""),
                        "content": row.get("内容", row.get("标题", "")),
                        "announcement_date": self._parse_date(datetime_str),
                        "source": "财联社电报",
                        "original_url": "",
                        "event_type": EventType.OTHER,
                        "event_category": None,
                        "needs_ai_classification": True,
                    }
                    all_telegraphs.append(telegraph)

            print(f"Fetched {len(all_telegraphs)} telegraphs")

        except Exception as e:
            print(f"Error fetching CLS telegraph: {str(e)}")

        return all_telegraphs

    async def check_event_exists(self, title: str) -> bool:
        """检查事件是否已存在"""
        events, _ = await db_service.get_events(limit=1, search=title)
        for event in events:
            if event["title"] == title:
                return True
        return False

    async def process_and_save_events(self, events_data: List[dict]) -> int:
        """
        处理并保存事件到数据库

        Args:
            events_data: 事件数据列表

        Returns:
            保存的事件数量
        """
        saved_count = 0
        skipped_count = 0

        pbar = tqdm(events_data, desc="Saving events", unit="event")

        for event_data in pbar:
            try:
                # 检查是否已存在
                if await self.check_event_exists(event_data["title"]):
                    skipped_count += 1
                    continue

                event_type = event_data.get("event_type", EventType.OTHER)
                event_category = event_data.get("event_category")

                if event_category is None:
                    event_category = EventCategory.COMPANY_UPDATES

                event_create = EventCreate(
                    title=event_data["title"],
                    content=event_data["content"],
                    event_category=event_category,
                    event_type=event_type,
                    announcement_date=event_data["announcement_date"],
                    source=event_data.get("source"),
                    original_url=event_data.get("original_url"),
                )

                await db_service.create_event(event_create)
                saved_count += 1

                if saved_count % 10 == 0:
                    pbar.set_description(f"Saved {saved_count}, Skipped {skipped_count}")

            except Exception as e:
                continue

        print(f"\nSummary: Saved {saved_count} new events, skipped {skipped_count} existing events")
        return saved_count

    async def update(self, days: int = 1):
        """
        更新事件数据

        Args:
            days: 获取最近N天的公告数据
        """
        print("=" * 50)
        print("Starting event update...")
        print("=" * 50)

        await connect_to_mongo()

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
            await self.process_and_save_events(all_events)

        print("\n" + "=" * 50)
        print("Event update completed!")
        print("=" * 50)

        await close_mongo_connection()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="增量更新金融事件数据")
    parser.add_argument("--days", type=int, default=1, help="获取最近N天的公告数据（默认：1）")

    args = parser.parse_args()

    updater = EventUpdater()
    await updater.update(days=args.days)


if __name__ == "__main__":
    asyncio.run(main())

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


class EventUpdater:
    """事件更新器"""

    def __init__(self):
        """初始化事件更新器"""
        pass

    async def fetch_stock_news(self, stock_codes: List[str]) -> List[dict]:
        """获取指定股票的新闻"""
        all_news = []
        
        for code in stock_codes:
            try:
                print(f"Fetching news for stock {code}...")
                df = ak.stock_news_em(symbol=code)
                
                if df is None or df.empty:
                    continue
                
                for _, row in df.iterrows():
                    news_item = {
                        "title": row.get("新闻标题", ""),
                        "content": row.get("新闻内容", row.get("新闻标题", "")),
                        "announcement_date": self._parse_date(row.get("发布时间", str(datetime.now()))),
                        "source": row.get("文章来源", "东方财富网"),
                        "original_url": row.get("新闻链接", ""),
                        "event_type": EventType.OTHER,
                    }
                    all_news.append(news_item)
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error fetching news for {code}: {str(e)}")
                continue
        
        print(f"Fetched {len(all_news)} news items total")
        return all_news

    async def fetch_hot_stocks(self, limit: int = 10) -> List[str]:
        """获取热门股票代码列表"""
        try:
            df = ak.stock_zh_a_spot_em()
            if df is None or df.empty:
                return []
            df = df.sort_values(by="成交额", ascending=False)
            return df["代码"].head(limit).tolist()
        except Exception as e:
            print(f"Error fetching hot stocks: {str(e)}")
            return ["000001", "600519", "300750", "601318", "000858"]

    def _classify_by_title(self, title: str) -> EventType:
        """根据标题分类事件类型"""
        if any(keyword in title for keyword in ["诉讼", "仲裁"]):
            return EventType.LITIGATION
        if any(keyword in title for keyword in ["股权转让", "股份划转"]):
            return EventType.SHAREHOLDER_CHANGE
        if "回购" in title:
            return EventType.REPURCHASE
        if any(keyword in title for keyword in ["年度报告", "年报"]):
            return EventType.ANNUAL_REPORT
        if any(keyword in title for keyword in ["业绩预告", "业绩快报"]):
            return EventType.EARNINGS_PREVIEW
        if any(keyword in title for keyword in ["分红", "送转", "利润分配"]):
            return EventType.DIVIDEND
        if any(keyword in title for keyword in ["并购", "重组", "资产重组"]):
            return EventType.MA
        if any(keyword in title for keyword in ["定增", "非公开发行", "配股"]):
            return EventType.REFINANCING
        if any(keyword in title for keyword in ["辞职", "聘任", "任命"]):
            return EventType.MANAGEMENT_CHANGE
        if any(keyword in title for keyword in ["立案", "调查", "处罚", "问询"]):
            return EventType.REGULATORY_PENALTY
        if any(keyword in title for keyword in ["获批", "审批", "核准"]):
            return EventType.APPROVAL
        return EventType.OTHER

    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except (ValueError, TypeError):
                continue
        return datetime.now()

    async def check_event_exists(self, title: str) -> bool:
        """检查事件是否已存在"""
        events, _ = await db_service.get_events(limit=1, search=title)
        for event in events:
            if event["title"] == title:
                return True
        return False

    async def process_and_save_events(self, events_data: List[dict]) -> int:
        """处理并保存事件到数据库（跳过已存在的）"""
        saved_count = 0
        skipped_count = 0

        for event_data in events_data:
            try:
                if await self.check_event_exists(event_data["title"]):
                    skipped_count += 1
                    continue

                event_type = self._classify_by_title(event_data["title"])
                
                if event_type in [EventType.MA, EventType.RESTRUCTURING, EventType.MANAGEMENT_CHANGE]:
                    event_category = EventCategory.SPECIAL_SITUATION
                else:
                    event_category = EventCategory.CORE_DRIVER

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
                print(f"Saved new event: {event_data['title'][:50]}...")

            except Exception as e:
                print(f"Error saving event: {str(e)}")
                continue

        print(f"\nSummary: Saved {saved_count} new events, skipped {skipped_count} existing events")
        return saved_count

    async def update(self, num_stocks: int = 10):
        """更新事件数据"""
        print("=" * 50)
        print("Starting event update...")
        print("=" * 50)

        await connect_to_mongo()

        print("\n" + "=" * 50)
        print(f"Fetching top {num_stocks} hot stocks...")
        print("=" * 50)
        stock_codes = await self.fetch_hot_stocks(limit=num_stocks)
        print(f"Got {len(stock_codes)} stock codes")

        print("\n" + "=" * 50)
        print("Fetching latest news...")
        print("=" * 50)
        news = await self.fetch_stock_news(stock_codes)
        if news:
            await self.process_and_save_events(news)

        print("\n" + "=" * 50)
        print("Event update completed!")
        print("=" * 50)

        await close_mongo_connection()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="增量更新金融事件数据")
    parser.add_argument("--stocks", type=int, default=10, help="获取多少只股票的新闻（默认：10）")

    args = parser.parse_args()

    updater = EventUpdater()
    await updater.update(num_stocks=args.stocks)


if __name__ == "__main__":
    asyncio.run(main())

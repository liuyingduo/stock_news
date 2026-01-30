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


from spider.common.stock_provider import stock_provider
from tqdm import tqdm
import requests
import concurrent.futures

class EventUpdater:
    """事件更新器"""

    def __init__(self):
        """初始化事件更新器"""
        pass

    def _fetch_stock_news_safe(self, code: str):
        """单只股票新闻获取"""
        return ak.stock_news_em(symbol=code)

    def _process_single_stock(self, code: str) -> List[dict]:
        """处理单个股票的新闻获取"""
        try:
            df = self._fetch_stock_news_safe(code)
            if df is None or df.empty:
                return []
            
            news_items = []
            for _, row in df.iterrows():
                news_item = {
                    "title": row.get("新闻标题", ""),
                    "content": row.get("新闻内容", row.get("新闻标题", "")),
                    "announcement_date": self._parse_date(row.get("发布时间", str(datetime.now()))),
                    "source": row.get("文章来源", "东方财富网"),
                    "original_url": row.get("新闻链接", ""),
                    "event_type": EventType.OTHER,
                }
                news_items.append(news_item)
            return news_items
        except Exception as e:
             # 只有非代理错误才打印详细日志
            if not isinstance(e, requests.exceptions.ProxyError):
                 pass
            return []

    async def fetch_stock_news(self, stock_codes: List[str]) -> List[dict]:
        """
        获取指定股票的新闻 (并发版)

        Args:
            stock_codes: 股票代码列表

        Returns:
            新闻列表
        """
        all_news = []
        
        # 限制并发数
        MAX_WORKERS = 10
        
        print(f"Fetching news for {len(stock_codes)} stocks with {MAX_WORKERS} workers...")
        
        # 使用 tqdm 显示进度条
        pbar = tqdm(total=len(stock_codes), desc="Fetching news", unit="stock")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            # 提交所有任务
            future_to_code = {executor.submit(self._process_single_stock, code): code for code in stock_codes}
            
            for future in concurrent.futures.as_completed(future_to_code):
                try:
                    news_items = future.result()
                    if news_items:
                        all_news.extend(news_items)
                except Exception as e:
                    pass
                finally:
                    pbar.update(1)
        
        pbar.close()
        print(f"\nFetched {len(all_news)} news items total")
        return all_news

    async def fetch_all_stocks(self) -> List[str]:
        """
        获取所有A股股票代码列表
        优先从数据库获取，无需频繁请求API
        """
        try:
            print("Fetching all A-share stock codes...")
            
            # 1. 尝试从数据库获取
            stocks = await db_service.get_all_stocks()
            if stocks:
                print(f"Found {len(stocks)} stocks in database. Using cached data.")
                return [s["code"] for s in stocks]

            # 2. 如果数据库为空，才去请求API
            print("Database is empty. Fetching from API...")
            # 使用自定义 stock_provider
            df = stock_provider.get_stock_zh_a_spot_em()
            
            if df is None or df.empty:
                return []

            codes = df["代码"].tolist()
            print(f"Found {len(codes)} A-share stocks from API")
            return codes
        except Exception as e:
            print(f"Error fetching all stocks: {str(e)}")
            return []

    async def fetch_hot_stocks(self, limit: int = 10) -> List[str]:
        """获取热门股票代码列表"""
        try:
            # 使用自定义 stock_provider
            df = stock_provider.get_stock_zh_a_spot_em()
            
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

    async def process_and_save_events(self, events_data: List[dict], days: int = None) -> int:
        """
        处理并保存事件到数据库（批量版本）

        Args:
            events_data: 事件数据列表
            days: 只保存最近N天的事件，None表示保存全部
        """
        # 1. 过滤日期
        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)
            print(f"Filtering events newer than {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")

            filtered_events = [
                event for event in events_data
                if event.get("announcement_date") and event["announcement_date"] >= cutoff_date
            ]
            print(f"Filtered {len(events_data) - len(filtered_events)} old events")
            events_data = filtered_events

        if not events_data:
            print("No events to save after filtering")
            return 0

        # 2. 批量获取已存在的事件标题（一次性查询）
        print("Checking for existing events...")
        try:
            # 获取所有已存在事件的标题（只返回标题字段）
            existing_events, _ = await db_service.get_events(limit=1000000)
            existing_titles = {event["title"] for event in existing_events}
            print(f"Found {len(existing_titles)} existing events in database")
        except Exception as e:
            print(f"Warning: Could not fetch existing events: {e}")
            existing_titles = set()

        # 3. 过滤新事件
        new_events = []
        skipped_count = 0

        for event_data in events_data:
            title = event_data["title"]
            if title in existing_titles:
                skipped_count += 1
                continue

            # 分类事件
            event_type = self._classify_by_title(title)
            if event_type in [EventType.MA, EventType.RESTRUCTURING, EventType.MANAGEMENT_CHANGE]:
                event_category = EventCategory.SPECIAL_SITUATION
            else:
                event_category = EventCategory.SENTIMENT_FLOWS

            new_events.append({
                "title": title,
                "content": event_data["content"],
                "event_category": event_category,
                "event_type": event_type,
                "announcement_date": event_data["announcement_date"],
                "source": event_data.get("source"),
                "original_url": event_data.get("original_url"),
            })

        print(f"Found {len(new_events)} new events to save")

        if not new_events:
            print("No new events to save")
            return 0

        # 4. 批量保存新事件（每批1000条）
        BATCH_SIZE = 1000
        saved_count = 0
        total_batches = (len(new_events) + BATCH_SIZE - 1) // BATCH_SIZE

        for i in range(0, len(new_events), BATCH_SIZE):
            batch = new_events[i:i + BATCH_SIZE]
            batch_num = i // BATCH_SIZE + 1

            # 转换为 EventCreate 对象
            event_creates = [EventCreate(**event_data) for event_data in batch]

            # 批量插入
            try:
                inserted = await db_service.create_events_bulk(event_creates)
                saved_count += inserted
                print(f"Batch {batch_num}/{total_batches}: Inserted {inserted} events")
            except Exception as e:
                # 如果批量插入失败，降级为单条插入
                print(f"Batch insert failed: {e}, falling back to single inserts...")
                for event_create in event_creates:
                    try:
                        await db_service.create_event(event_create)
                        saved_count += 1
                    except Exception:
                        continue

        print(f"\nSummary: Saved {saved_count} new events, skipped {skipped_count} existing events")
        return saved_count

    async def update(self, num_stocks: int = 10, days: int = None, all_stocks: bool = False):
        """
        更新事件数据

        Args:
            num_stocks: 获取多少只股票的新闻（当 all_stocks=False 时使用）
            days: 只保存最近N天的事件，None表示保存全部
            all_stocks: 是否获取所有A股股票的新闻
        """
        print("=" * 50)
        print("Starting event update...")
        print("=" * 50)

        await connect_to_mongo()

        # 获取股票
        print("\n" + "=" * 50)
        if all_stocks:
            print("Fetching all A-share stocks...")
            print("=" * 50)
            stock_codes = await self.fetch_all_stocks()
        else:
            print(f"Fetching top {num_stocks} hot stocks...")
            print("=" * 50)
            stock_codes = await self.fetch_hot_stocks(limit=num_stocks)
        print(f"Got {len(stock_codes)} stock codes")

        print("\n" + "=" * 50)
        print("Fetching latest news...")
        print("=" * 50)
        news = await self.fetch_stock_news(stock_codes)
        if news:
            await self.process_and_save_events(news, days=days)

        print("\n" + "=" * 50)
        print("Event update completed!")
        print("=" * 50)

        await close_mongo_connection()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="增量更新金融事件数据")
    parser.add_argument("--stocks", type=int, default=10, help="获取多少只股票的新闻（默认：10，使用 --all 时此参数无效）")
    parser.add_argument("--days", type=int, default=None, help="只保存最近N天的新闻，不指定则保存全部（默认：None）")
    parser.add_argument("--all", action="store_true", help="获取所有A股股票的新闻（注意：可能需要较长时间）")

    args = parser.parse_args()

    updater = EventUpdater()
    await updater.update(num_stocks=args.stocks, days=args.days, all_stocks=args.all)


if __name__ == "__main__":
    asyncio.run(main())

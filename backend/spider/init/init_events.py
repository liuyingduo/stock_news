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
import pandas as pd
from datetime import datetime, timedelta
from typing import List
from app.models import EventCreate, EventCategory, EventType
from app.services.database_service import db_service
from app.core.database import connect_to_mongo, close_mongo_connection


from tqdm import tqdm
import requests




from spider.common.stock_provider import stock_provider

class EventInitializer:
    """事件初始化器"""

    def __init__(self):
        """初始化事件初始化器"""
        pass

    def _fetch_stock_news_safe(self, code: str):
        """单只股票新闻获取（已移除重试）"""
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
        import concurrent.futures
        
        # 限制并发数，防止被封IP
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
                    # code = future_to_code[future]
                    # print(f"Error processing stock {code}: {e}")
                    pass
                finally:
                    pbar.update(1)
        
        pbar.close()
        print(f"\nFetched {len(all_news)} news items total")
        return all_news

    def _fetch_all_stocks_safe(self):
         """所有股票列表获取（已移除重试）"""
         # 使用自定义方法替代 akshare
         return stock_provider.get_stock_zh_a_spot_em()

    async def fetch_all_stocks(self) -> List[str]:

        """
        获取所有A股股票代码列表

        Returns:
            股票代码列表
        """
    async def fetch_all_stocks(self) -> List[str]:
        """
        获取所有A股股票代码列表
        优先从数据库获取，如果为空则从接口获取并保存
        """
        try:
            print("Fetching all A-share stock codes...")
            
            # 1. 尝试先从API获取最新列表（初始化时通常需要最新的）
            df = self._fetch_all_stocks_safe()
            
            if df is not None and not df.empty:
                print(f"Fetched {len(df)} stocks from API. Saving to database...")
                # 保存到数据库
                saved_count = 0
                for _, row in tqdm(df.iterrows(), total=len(df), desc="Saving stocks"):
                    try:
                        await db_service.create_or_update_stock(
                            code=str(row["代码"]),
                            name=str(row["名称"]),
                            price=float(row["最新价"]) if pd.notna(row["最新价"]) else 0.0,
                            volume=float(row["成交额"]) if pd.notna(row["成交额"]) else 0.0
                        )
                        saved_count += 1
                    except Exception:
                        continue
                print(f"Saved {saved_count} stocks to database.")
                return df["代码"].tolist()

            # 2. 如果API失败，尝试从数据库获取作为备选
            print("API fetch failed or empty. Trying to load from database...")
            stocks = await db_service.get_all_stocks()
            if stocks:
                print(f"Found {len(stocks)} stocks in database.")
                return [s["code"] for s in stocks]
            
            return []
            
        except Exception as e:
            print(f"Error fetching all stocks: {str(e)}")
            # 出错时尝试读库
            stocks = await db_service.get_all_stocks()
            if stocks:
                 return [s["code"] for s in stocks]
            return []

    async def fetch_hot_stocks(self, limit: int = 20) -> List[str]:
        """
        获取热门股票代码列表（用于获取新闻）

        Returns:
            股票代码列表
        """
        try:
            # 获取涨幅榜前N只股票
            df = self._fetch_all_stocks_safe()
            if df is None or df.empty:
                return []

            # 取成交额最大的股票
            df = df.sort_values(by="成交额", ascending=False)
            codes = df["代码"].head(limit).tolist()
            return codes
        except Exception as e:
            print(f"Error fetching hot stocks: {str(e)}")
            # 返回一些默认的热门股票代码
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

        # print(f"Warning: Could not parse date '{date_str}', using current time")
        return datetime.now()

    async def process_and_save_events(self, events_data: List[dict], days: int = None) -> int:
        """
        处理并保存事件到数据库

        Args:
            events_data: 事件数据列表
            days: 只保存最近N天的事件，None表示保存全部
        """
        saved_count = 0
        cutoff_date = None

        if days is not None:
            cutoff_date = datetime.now() - timedelta(days=days)
            print(f"Filtering events newer than {cutoff_date.strftime('%Y-%m-%d %H:%M:%S')}")

        # 同样给数据库保存加个进度条
        pbar = tqdm(events_data, desc="Saving events", unit="event")
        
        for event_data in pbar:
            try:
                # 检查日期是否在范围内
                if cutoff_date is not None:
                    announcement_date = event_data.get("announcement_date")
                    if announcement_date and announcement_date < cutoff_date:
                        continue

                event_type = event_data.get("event_type", EventType.OTHER)

                # 根据标题重新分类
                if event_type == EventType.OTHER:
                    event_type = self._classify_by_title(event_data["title"])

                # 根据事件类型确定事件大类
                if event_type in [EventType.MA, EventType.RESTRUCTURING, EventType.MANAGEMENT_CHANGE]:
                    event_category = EventCategory.SPECIAL_SITUATION
                else:
                    event_category = EventCategory.SENTIMENT_FLOWS

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
                
                # 偶尔更新一下描述
                if saved_count % 100 == 0:
                    pbar.set_description(f"Saved {saved_count} events")

            except Exception as e:
                # print(f"Error saving event: {str(e)}")
                continue

        return saved_count

    async def initialize(self, num_stocks: int = 20, days: int = None, all_stocks: bool = False):
        """
        初始化事件数据

        Args:
            num_stocks: 获取多少只股票的新闻（当 all_stocks=False 时使用）
            days: 只保存最近N天的事件，None表示保存全部
            all_stocks: 是否获取所有A股股票的新闻
        """
        print("=" * 50)
        print("Starting event initialization...")
        print("=" * 50)

        # 连接数据库
        await connect_to_mongo()

        # 创建数据库索引
        print("Creating database indexes...")
        await db_service.create_indexes()

        # 清空已有数据
        print("Clearing existing events...")
        deleted_count = await db_service.delete_all_events()
        print(f"Deleted {deleted_count} existing events.")

        # 获取股票
        try:
            print("\n" + "=" * 50)
            if all_stocks:
                # print("Fetching all A-share stocks...")
                # print("=" * 50)
                stock_codes = await self.fetch_all_stocks()
            else:
                print(f"Fetching top {num_stocks} hot stocks...")
                print("=" * 50)
                stock_codes = await self.fetch_hot_stocks(limit=num_stocks)
            
            if not stock_codes:
                 print("No stocks found or network error occurred.")
                 return

            print(f"Got {len(stock_codes)} stock codes")

            # 获取并处理新闻
            print("\n" + "=" * 50)
            print("Fetching stock news...")
            print("=" * 50)
            news = await self.fetch_stock_news(stock_codes)
            
            if news:
                await self.process_and_save_events(news, days=days)
                
        except Exception as e:
             print(f"An unexpected error occurred during initialization: {str(e)}")
        finally:
            print("\n" + "=" * 50)
            print("Event initialization completed!")
            print("=" * 50)

            # 关闭数据库连接
            await close_mongo_connection()


async def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="初始化金融事件数据")
    parser.add_argument("--stocks", type=int, default=20, help="获取多少只股票的新闻（默认：20，使用 --all 时此参数无效）")
    parser.add_argument("--days", type=int, default=None, help="只保存最近N天的新闻，不指定则保存全部（默认：None）")
    parser.add_argument("--all", action="store_true", help="获取所有A股股票的新闻（注意：可能需要较长时间）")

    args = parser.parse_args()

    initializer = EventInitializer()
    await initializer.initialize(num_stocks=args.stocks, days=args.days, all_stocks=args.all)


if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")

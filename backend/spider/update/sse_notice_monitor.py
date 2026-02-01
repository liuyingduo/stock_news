"""
上交所公告监控
定时轮询获取前一天的所有公告，并进行 AI 分析和入库
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta
from typing import List

# 添加 backend 目录到 Python 路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_dir)

from app.models import EventCreate, EventCategory, EventType
from app.services.database_service import db_service
from app.core.database import connect_to_mongo, close_mongo_connection
from spider.analyze.analyze_events import EventAnalyzer
from spider.common.sse_notice_fetcher import SSENoticeFetcher


class SSENoticeMonitor:
    """上交所公告监控类"""

    def __init__(self):
        """初始化监控器"""
        self.fetcher = SSENoticeFetcher()
        self.analyzer = EventAnalyzer()
        # 记录已处理的公告 ID，避免重复
        self.processed_ids = set()
        # 上次处理的日期
        self.last_processed_date = None

    async def fetch_yesterday_notices(self) -> List[dict]:
        """
        获取前一天的所有公告

        Returns:
            公告列表
        """
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_str = yesterday.strftime("%Y-%m-%d")

        # 检查是否已经处理过这一天的数据
        if self.last_processed_date == yesterday_str:
            print(f"Date {yesterday_str} already processed, skipping...")
            return []

        print(f"Fetching SSE notices for {yesterday_str}...")

        try:
            # 使用爬虫获取公告
            notices = self.fetcher.fetch_notices_by_date(yesterday)

            # 过滤已处理的公告
            new_notices = []
            for notice in notices:
                # 使用股票代码 + 标题作为唯一标识
                notice_id = f"{notice['stock_code']}_{notice['title']}"
                if notice_id not in self.processed_ids:
                    notice['_id'] = notice_id
                    new_notices.append(notice)
                    self.processed_ids.add(notice_id)

            print(f"Fetched {len(notices)} notices, {len(new_notices)} are new.")
            return new_notices

        except Exception as e:
            print(f"Error fetching notices: {e}")
            return []

    async def save_notices_to_db(self, notices: List[dict]) -> int:
        """
        将公告保存到数据库

        Args:
            notices: 公告列表

        Returns:
            保存的数量
        """
        if not notices:
            return 0

        saved_count = 0

        for notice in notices:
            try:
                # 构建 EventCreate 对象
                # 根据公告类型映射到 EventType
                bulletin_type = notice.get("bulletin_type", "")
                event_type = self._map_bulletin_type_to_event_type(bulletin_type)

                event_data = EventCreate(
                    title=notice["title"],
                    content=notice["title"],  # 暂时使用标题作为内容，后续可抓取详情
                    announcement_date=notice["announcement_date"],
                    source=notice["source"],
                    original_url=notice["url"],
                    event_type=event_type,
                    event_category=EventCategory.COMPANY_UPDATES,  # 上交所公告归类为公司动态
                    stock_code=notice.get("stock_code", ""),
                    stock_name=notice.get("stock_name", ""),
                )

                # 查重：根据标题和日期去重
                existing = await db_service.get_event_by_title_date(
                    event_data.title,
                    event_data.announcement_date
                )

                if not existing:
                    await db_service.create_event(event_data)
                    saved_count += 1

            except Exception as e:
                print(f"Error saving notice: {e}")
                continue

        return saved_count

    def _map_bulletin_type_to_event_type(self, bulletin_type: str) -> EventType:
        """
        将上交所公告类型映射到 EventType

        Args:
            bulletin_type: 公告类型描述

        Returns:
            EventType 枚举值
        """
        # 常见公告类型映射
        type_mapping = {
            "财务报告": EventType.FINANCIAL_REPORT,
            "业绩预告、业绩快报和盈利预测": EventType.FINANCIAL_REPORT,
            "业绩预告": EventType.FINANCIAL_REPORT,
            "业绩快报": EventType.FINANCIAL_REPORT,
            "利润分配、公积金转增股本": EventType.FINANCING_ANNOUNCEMENT,
            "分红": EventType.FINANCING_ANNOUNCEMENT,
            "配股": EventType.FINANCING_ANNOUNCEMENT,
            "增发": EventType.FINANCING_ANNOUNCEMENT,
            "可转债": EventType.FINANCING_ANNOUNCEMENT,
            "公司债券": EventType.FINANCING_ANNOUNCEMENT,
            "融资": EventType.FINANCING_ANNOUNCEMENT,
            "募集资金使用与管理": EventType.FINANCING_ANNOUNCEMENT,
            "重大事项": EventType.MAJOR_EVENT,
            "重组": EventType.ASSET_RESTRUCTURING,
            "资产重组": EventType.ASSET_RESTRUCTURING,
            "收购兼并": EventType.ASSET_RESTRUCTURING,
            "股权变动": EventType.SHAREHOLDING_CHANGE,
            "持股变动": EventType.SHAREHOLDING_CHANGE,
            "减持": EventType.SHAREHOLDING_CHANGE,
            "增持": EventType.SHAREHOLDING_CHANGE,
            "股权转让": EventType.SHAREHOLDING_CHANGE,
            "董事会和监事会": EventType.MAJOR_EVENT,
            "股东大会": EventType.MAJOR_EVENT,
            "公司治理": EventType.OTHER,
            "高管变动": EventType.INFO_CHANGE,
            "人事变动": EventType.INFO_CHANGE,
            "辞职": EventType.INFO_CHANGE,
            "聘任": EventType.INFO_CHANGE,
            "公司重要基本信息变化": EventType.INFO_CHANGE,
            "信息变更": EventType.INFO_CHANGE,
            "名称变更": EventType.INFO_CHANGE,
            "经营范围变更": EventType.INFO_CHANGE,
            "风险提示": EventType.RISK_WARNING,
            "暂停上市": EventType.RISK_WARNING,
            "终止上市": EventType.RISK_WARNING,
            "退市风险": EventType.RISK_WARNING,
            "诉讼": EventType.RISK_WARNING,
            "仲裁": EventType.RISK_WARNING,
            "处罚": EventType.RISK_WARNING,
            "监管": EventType.OTHER,
            "其他": EventType.OTHER,
        }

        # 尝试精确匹配
        if bulletin_type in type_mapping:
            return type_mapping[bulletin_type]

        # 尝试模糊匹配
        for key, value in type_mapping.items():
            if key in bulletin_type:
                return value

        # 默认返回 OTHER
        return EventType.OTHER

    async def run(self):
        """运行监控循环"""
        print("=" * 60)
        print("Starting SSE Notice Monitor...")
        print("=" * 60)
        print("Configuration:")
        print("  - Fetch: Previous day's all notices")
        print("  - Interval: 1 hour")
        print("  - Source: Shanghai Stock Exchange")
        print("=" * 60)
        print("Press Ctrl+C to stop.")
        print()

        # 连接数据库
        await connect_to_mongo()

        try:
            while True:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{current_time}] Checking for yesterday's notices...")

                # 获取前一天的公告
                new_notices = await self.fetch_yesterday_notices()

                if new_notices:
                    print(f"Found {len(new_notices)} new notices. Saving to database...")

                    # 保存到数据库
                    saved_count = await self.save_notices_to_db(new_notices)

                    if saved_count > 0:
                        print(f"Successfully saved {saved_count} new events to DB.")
                        print("Triggering AI analysis...")

                        # 触发 AI 分析
                        await self.analyzer.process_pending_events(limit=50)

                        # 更新已处理日期
                        yesterday = datetime.now() - timedelta(days=1)
                        self.last_processed_date = yesterday.strftime("%Y-%m-%d")
                    else:
                        print("No new unique events saved (duplicates filtered).")
                else:
                    print("No new notices found or date already processed.")

                # 限制内存集合大小
                if len(self.processed_ids) > 5000:
                    print("Clearing processed IDs cache to free memory...")
                    self.processed_ids.clear()

                # 计算下次运行时间（整点运行）
                now = datetime.now()
                next_hour = (now.replace(minute=0, second=0, microsecond=0) +
                            timedelta(hours=1))
                wait_seconds = (next_hour - now).total_seconds()

                if wait_seconds > 0:
                    next_time_str = next_hour.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"Next check at {next_time_str} (waiting {int(wait_seconds)} seconds)...")
                    print()
                    await asyncio.sleep(wait_seconds)
                else:
                    # 如果已经过了整点，等待1小时
                    print(f"Waiting 1 hour until next check...")
                    print()
                    await asyncio.sleep(3600)

        except KeyboardInterrupt:
            print("\n" + "=" * 60)
            print("Stopping SSE Notice Monitor...")
            print("=" * 60)
        except Exception as e:
            print(f"\nMonitor crashed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await close_mongo_connection()


async def main():
    """主函数"""
    monitor = SSENoticeMonitor()
    await monitor.run()


if __name__ == "__main__":
    # Windows 下使用 WindowsSelectorEventLoopPolicy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    asyncio.run(main())

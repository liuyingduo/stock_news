"""
财联社电报实时监控
定时轮询 API 获取最新电报，并进行 AI 分析和入库
"""
import sys
import os
import time
import asyncio
import akshare as ak
from datetime import datetime
from typing import List

# 添加 backend 目录到 Python 路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_dir)

from app.models import EventCreate, EventCategory, EventType
from app.services.database_service import db_service
from app.core.database import connect_to_mongo, close_mongo_connection
from spider.analyze.analyze_events import EventAnalyzer

class TelegraphMonitor:
    def __init__(self):
        self.analyzer = EventAnalyzer()
        self.last_check_time = datetime.now()
        # 记录已处理的电报标题，避免重复（简单的内存去重，重启后失效，但数据库有唯一索引兜底）
        self.processed_titles = set()

    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return datetime.now()

    async def fetch_latest_telegraphs(self) -> List[dict]:
        """获取最新的电报数据"""
        new_telegraphs = []
        try:
            # 获取最新一页电报
            df = ak.stock_info_global_cls(symbol="全部")
            
            if df is not None and not df.empty:
                for _, row in df.iterrows():
                    title = row.get("标题", "")
                    content = row.get("内容", title)
                    date_str = str(row.get("发布日期", ""))
                    time_str = str(row.get("发布时间", ""))
                    datetime_str = f"{date_str} {time_str}"
                    publish_time = self._parse_date(datetime_str)

                    # 仅处理最近 1 小时内的数据，最初启动时可能会有一批
                    # 也可以根据 last_check_time 来过滤，但考虑到抓取间隔，用时间窗口更稳健
                    if (datetime.now() - publish_time).total_seconds() > 3600:
                        continue

                    # 内存去重
                    if title in self.processed_titles:
                        continue

                    telegraph = {
                        "title": title,
                        "content": content,
                        "announcement_date": publish_time,
                        "source": "财联社电报",
                        "original_url": "",
                        "event_type": EventType.OTHER,
                        "event_category": None,
                        "needs_ai_classification": True,
                    }
                    new_telegraphs.append(telegraph)
                    self.processed_titles.add(title)

        except Exception as e:
            print(f"Error fetching telegraphs: {e}")
        
        return new_telegraphs

    async def run(self):
        """运行监控循环"""
        print("Starting Telegraph Monitor...")
        print("Press Ctrl+C to stop.")
        
        await connect_to_mongo()
        
        try:
            while True:
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"[{current_time}] Checking for new telegraphs...")
                
                new_items = await self.fetch_latest_telegraphs()
                
                if new_items:
                    print(f"Found {len(new_items)} new telegraphs. Analyzing...")
                    
                    # 1. 保存原始数据（process_and_save_events 会处理去重）
                    # 但我们需要先转换为 EventCreate 对象或者直接存字典？
                    # 初始化脚本里是 process_and_save_events，但这里我们可以直接复用 analyzer 的逻辑
                    # 不过 analyzer 是从数据库读未分析的。
                    # 为了流程统一，我们先存入数据库，然后调用 analyze_events 处理
                    
                    # 简化的入库逻辑，参考 init_events.py 的 process_and_save_events
                    saved_count = 0
                    for item in new_items:
                        # 临时构建字典以适应 EventCreate，
                        # 注意：EventCreate 需要 event_category，我们暂时设为 GLOBAL_EVENTS 或其他默认值
                        # 因为 analyzer 会重新分类并更新它。
                        event_data = EventCreate(
                            title=item["title"],
                            content=item["content"],
                            announcement_date=item["announcement_date"],
                            source=item["source"],
                            original_url=item["original_url"],
                            event_type=item["event_type"],
                            event_category=EventCategory.GLOBAL_EVENTS, # 默认值，后续 AI 会修正
                        )
                        
                        # 查重
                        existing = await db_service.get_event_by_title_date(event_data.title, event_data.announcement_date)
                        if not existing:
                            # 插入数据库
                            # 注意：我们需要确保插入的数据包含 requires_ai_classification 字段
                            # 但 EventCreate 模型没有这个字段。
                            # 我们可以先转换为 dict，然后手动添加字段再插入 DB吗？
                            # db_service.create_event 接受 EventCreate 对象。
                            # 让我们查看 db_service.create_event 的实现。
                            
                            # 如果 EventCreate模型确实不包含 requires_ai_classification，
                            # 那么我们无法通过 event_data 传递它。
                            # 但是，我们可以直接操作数据库或者修改 create_event 方法。
                            # 简单起见，我们先按标准流程插入，
                            # 然后 analyzer 会扫描所有事件。
                            # 但是 analyzer 怎么知道哪些需要分类？
                            # analyzer.process_pending_events 查找 conditions:
                            # {"$or": [{"ai_analysis": None}, {"ai_analysis.impact_score": None}]}
                            # 所以只要插入时 ai_analysis 为空，它就会被处理。
                            
                            await db_service.create_event(event_data)
                            saved_count += 1
                    
                    if saved_count > 0:
                        print(f"Saved {saved_count} new events to DB. Triggering AI analysis...")
                        # 触发 AI 分析
                        # 分析器会查找所有 pending 的事件，所以刚存进去的会被处理
                        await self.analyzer.process_pending_events(limit=10) # 限制每次处理数量，防止积压
                    else:
                        print("No new unique events saved.")
                
                # 限制集合大小，防止无限增长
                if len(self.processed_titles) > 1000:
                    self.processed_titles.clear()

                # 休眠 10 秒
                await asyncio.sleep(10)

        except KeyboardInterrupt:
            print("\nStopping monitor...")
        except Exception as e:
            print(f"\nMonitor crashed: {e}")
        finally:
            await close_mongo_connection()

if __name__ == "__main__":
    monitor = TelegraphMonitor()
    asyncio.run(monitor.run())  

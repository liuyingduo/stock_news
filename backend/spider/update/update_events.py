"""
增量更新爬虫 - 获取最新的金融事件数据
整合三大交易所公告和财联社电报
"""
import sys
import os

# 添加 backend 目录到 Python 路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, backend_dir)

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict
from tqdm import tqdm

from app.models import EventCreate, EventCategory, EventType
from app.services.database_service import db_service
from app.core.database import connect_to_mongo, close_mongo_connection
from app.services.pdf_service import pdf_service

# 导入三大交易所爬虫
from spider.common.sse_notice_fetcher import SSENoticeFetcher
from spider.common.szse_notice_fetcher import SZSENoticeFetcher
from spider.common.bse_notice_fetcher import BSENoticeFetcher


class EventUpdater:
    """事件更新器"""

    def __init__(self):
        """初始化事件更新器"""
        self.sse_fetcher = SSENoticeFetcher()
        self.szse_fetcher = SZSENoticeFetcher()
        self.bse_fetcher = BSENoticeFetcher()

    async def fetch_exchange_notices(self, date: datetime) -> Dict[str, List[dict]]:
        """
        获取三大交易所的公告数据

        Args:
            date: 目标日期

        Returns:
            {"交易所名称": 公告列表}
        """
        results = {}
        date_str = date.strftime("%Y-%m-%d")

        print(f"\n{'='*60}")
        print(f"获取 {date_str} 的三大交易所公告")
        print(f"{'='*60}")

        # 1. 上交所
        print(f"\n[1/3] 获取上交所公告...")
        try:
            sse_notices = self.sse_fetcher.fetch_notices_by_date(date)
            results["上海证券交易所"] = sse_notices
            print(f"  ✓ 上交所: {len(sse_notices)} 条")
        except Exception as e:
            print(f"  ✗ 上交所获取失败: {e}")
            results["上海证券交易所"] = []

        # 2. 深交所
        print(f"\n[2/3] 获取深交所公告...")
        try:
            szse_notices = self.szse_fetcher.fetch_notices_by_date(date)
            results["深圳证券交易所"] = szse_notices
            print(f"  ✓ 深交所: {len(szse_notices)} 条")
        except Exception as e:
            print(f"  ✗ 深交所获取失败: {e}")
            results["深圳证券交易所"] = []

        # 3. 北交所
        print(f"\n[3/3] 获取北交所公告...")
        try:
            # 收集所有子类型ID
            all_subtypes = []
            for category_name, subtypes in self.bse_fetcher.categories.items():
                all_subtypes.extend(subtypes)

            bse_notices = self.bse_fetcher.fetch_notices_by_date(date, disclosure_subtypes=all_subtypes)
            results["北京证券交易所"] = bse_notices
            print(f"  ✓ 北交所: {len(bse_notices)} 条")
        except Exception as e:
            print(f"  ✗ 北交所获取失败: {e}")
            results["北京证券交易所"] = []

        total = sum(len(notices) for notices in results.values())
        print(f"\n总计获取 {total} 条公告")

        return results

    async def process_pdfs_for_notices(self, notices: List[dict], max_concurrent: int = 10, headers: Dict[str, str] = None) -> List[dict]:
        """
        批量下载并解析PDF

        Args:
            notices: 公告列表
            max_concurrent: 最大并发下载数
            headers: 自定义HTTP头

        Returns:
            处理后的公告列表（包含本地PDF路径和解析内容）
        """
        # 收集所有PDF URL
        pdf_urls = []
        url_to_notice = {}

        for notice in notices:
            url = notice.get("url", "")
            # Check if URL path ends with .pdf (case insensitive, ignoring query params)
            if url and url.lower().split('?')[0].endswith(".pdf"):
                pdf_urls.append(url)
                url_to_notice[url] = notice

        if not pdf_urls:
            print(f"  没有需要下载的PDF文件")
            return notices

        print(f"  开始下载并解析 {len(pdf_urls)} 个PDF文件（并发数: {max_concurrent}）...")

        # 批量下载并解析PDF
        pdf_results = await pdf_service.process_pdf_batch(pdf_urls, max_concurrent=max_concurrent, headers=headers, cleanup=True)

        print(f"  PDF处理完成: 成功 {len(pdf_results)}/{len(pdf_urls)}")

        # 更新公告数据
        updated_notices = []
        for notice in notices:
            url = notice.get("url", "")
            if url in pdf_results:
                local_url, text_content = pdf_results[url]
                # cleanup=True时，local_url 为 None，但这符合用户要求（不存本地）
                notice["local_pdf_url"] = local_url 
                notice["content"] = text_content if text_content else notice.get("title", "")
            else:
                notice["content"] = notice.get("title", "")
            updated_notices.append(notice)

        return updated_notices

    async def fetch_cls_telegraph(self) -> List[dict]:
        """
        获取财联社电报数据

        Returns:
            电报列表
        """
        all_telegraphs = []

        try:
            print(f"\n{'='*60}")
            print("获取财联社电报")
            print(f"{'='*60}")

            import akshare as ak
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

                print(f"  ✓ 财联社电报: {len(all_telegraphs)} 条")

        except Exception as e:
            print(f"  ✗ 财联社电报获取失败: {str(e)}")

        return all_telegraphs

    def _parse_date(self, date_str: str) -> datetime:
        """解析日期字符串"""
        formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%Y%m%d", "%Y/%m/%d"]
        for fmt in formats:
            try:
                return datetime.strptime(str(date_str), fmt)
            except (ValueError, TypeError):
                continue
        return datetime.now()

    def _map_bulletin_type_to_event_type(self, source: str, bulletin_type: str) -> EventType:
        """
        将公告类型映射到EventType

        Args:
            source: 交易所来源
            bulletin_type: 公告类型

        Returns:
            EventType枚举值
        """
        # 北交所映射 (使用文本描述精准匹配)
        if "北京" in source or "北交所" in source:
            bse_mapping = {
                "年度报告": EventType.FINANCIAL_REPORT,
                "半年度报告": EventType.FINANCIAL_REPORT,
                "一季度报告": EventType.FINANCIAL_REPORT,
                "三季度报告": EventType.FINANCIAL_REPORT,
                "业绩预告、业绩快报类": EventType.FINANCIAL_REPORT,
                "董事会决议": EventType.MAJOR_EVENT,
                "监事会决议": EventType.MAJOR_EVENT,
                "股东大会决议": EventType.MAJOR_EVENT,
                "权益分派": EventType.FINANCING_ANNOUNCEMENT,
                "股权激励类": EventType.SHAREHOLDING_CHANGE,
                "员工持股计划类": EventType.SHAREHOLDING_CHANGE,
                "公开发行类": EventType.FINANCING_ANNOUNCEMENT,
                "募集资金管理类": EventType.FINANCING_ANNOUNCEMENT,
                "股份回购类": EventType.SHAREHOLDING_CHANGE,
                "公司经营类": EventType.INFO_CHANGE,
            }
            return bse_mapping.get(bulletin_type, EventType.OTHER)

        # 深交所映射 (使用文本描述精准匹配)
        elif "深圳" in source or "深交所" in source:
            szse_mapping = {
                "年度报告": EventType.FINANCIAL_REPORT,
                "半年度报告": EventType.FINANCIAL_REPORT,
                "一季度报告": EventType.FINANCIAL_REPORT,
                "三季度报告": EventType.FINANCIAL_REPORT,
                "首次公开发行及上市": EventType.FINANCING_ANNOUNCEMENT,
                "配股": EventType.FINANCING_ANNOUNCEMENT,
                "增发": EventType.FINANCING_ANNOUNCEMENT,
                "可转换债券": EventType.FINANCING_ANNOUNCEMENT,
                "权证相关公告": EventType.FINANCING_ANNOUNCEMENT,
                "其它融资": EventType.FINANCING_ANNOUNCEMENT,
                "权益分派与限制出售股份上市": EventType.FINANCING_ANNOUNCEMENT,
                "股权变动": EventType.SHAREHOLDING_CHANGE,
                "交易": EventType.MAJOR_EVENT,
                "股东会": EventType.MAJOR_EVENT,
                "澄清、风险提示、业绩预告事项": EventType.MAJOR_EVENT,
                "特别处理和退市": EventType.RISK_WARNING,
                "补充及更正": EventType.INFO_CHANGE,
                "中介机构报告": EventType.OTHER,
                "上市公司制度": EventType.OTHER,
                "债券公告": EventType.FINANCING_ANNOUNCEMENT,
                "其它重大事项": EventType.MAJOR_EVENT,
                "董事会公告": EventType.MAJOR_EVENT,
                "监事会公告": EventType.MAJOR_EVENT,
            }
            return szse_mapping.get(bulletin_type, EventType.OTHER)
        # 上交所映射 (使用原始文字描述精准匹配)
        else:  # 上海证券交易所
            sse_mapping = {
                # 1. 定期报告
                "定期报告": EventType.FINANCIAL_REPORT,
                # 2. 董事会和监事会
                "董事会和监事会": EventType.MAJOR_EVENT,
                # 3. 股东会
                "股东会": EventType.MAJOR_EVENT,
                # 4. 应当披露的交易
                "应当披露的交易": EventType.MAJOR_EVENT,
                # 5. 首次公开发行
                "首次公开发行": EventType.FINANCING_ANNOUNCEMENT,
                # 6. 关联交易
                "关联交易": EventType.MAJOR_EVENT,
                # 7. 对外担保
                "对外担保": EventType.MAJOR_EVENT,
                # 8. 募集资金使用与管理
                "募集资金使用与管理": EventType.FINANCING_ANNOUNCEMENT,
                # 9. 业绩预告、业绩快报和盈利预测
                "业绩预告、业绩快报和盈利预测": EventType.FINANCIAL_REPORT,
                # 10. 利润分配和资本公积金转增股本
                "利润分配和资本公积金转增股本": EventType.FINANCING_ANNOUNCEMENT,
                # 11. 股票交易异常波动和澄清
                "股票交易异常波动和澄清": EventType.RISK_WARNING,
                # 12. 股份上市流通与股本变动
                "股份上市流通与股本变动": EventType.SHAREHOLDING_CHANGE,
                # 13. 股东增持或减持股份
                "股东增持或减持股份": EventType.SHAREHOLDING_CHANGE,
                # 14. 权益变动报告书和（要约）收购
                "权益变动报告书和（要约）收购": EventType.ASSET_RESTRUCTURING,
                # 15. 股权型再融资
                "股权型再融资": EventType.FINANCING_ANNOUNCEMENT,
                # 16. 其他再融资
                "其他再融资": EventType.FINANCING_ANNOUNCEMENT,
                # 17. 重大资产重组
                "重大资产重组": EventType.ASSET_RESTRUCTURING,
                # 18. 吸收合并
                "吸收合并": EventType.ASSET_RESTRUCTURING,
                # 19. 回购股份
                "回购股份": EventType.SHAREHOLDING_CHANGE,
                # 20. 可转换公司债
                "可转换公司债": EventType.FINANCING_ANNOUNCEMENT,
                # 21. 股权激励及员工持股计划
                "股权激励及员工持股计划": EventType.SHAREHOLDING_CHANGE,
                # 22. 诉讼和仲裁
                "诉讼和仲裁": EventType.RISK_WARNING,
                # 23. 股东股份被质押冻结或司法拍卖
                "股东股份被质押冻结或司法拍卖": EventType.RISK_WARNING,
                # 24. 破产与重整
                "破产与重整": EventType.RISK_WARNING,
                # 25. 其他重大事项
                "其他重大事项": EventType.MAJOR_EVENT,
                # 26. 公司重要基本信息变化
                "公司重要基本信息变化": EventType.INFO_CHANGE,
                # 27. 风险警示
                "风险警示": EventType.RISK_WARNING,
                # 28. 暂停、恢复和终止上市
                "暂停、恢复和终止上市": EventType.RISK_WARNING,
                # 29. 补充更正公告
                "补充更正公告": EventType.INFO_CHANGE,
                # 30. 规范运作
                "规范运作": EventType.OTHER,
                # 31. 中介机构报告
                "中介机构报告": EventType.OTHER,
                # 32. 停复牌提示性公告
                "停复牌提示性公告": EventType.INFO_CHANGE,
                # 33. 优先股
                "优先股": EventType.FINANCING_ANNOUNCEMENT,
                # 34. 特别表决权
                "特别表决权": EventType.MAJOR_EVENT,
                # 35. 超额配售选择权
                "超额配售选择权": EventType.FINANCING_ANNOUNCEMENT,
                # 36. 存托凭证相关公告
                "存托凭证相关公告": EventType.FINANCING_ANNOUNCEMENT,
                # 37. 询价转让及配售
                "询价转让及配售": EventType.FINANCING_ANNOUNCEMENT,
                # 38. 境内外同步披露
                "境内外同步披露": EventType.OTHER,
                # 39. 其他
                "其他": EventType.OTHER
            }

            return sse_mapping.get(bulletin_type, EventType.OTHER)



    async def check_event_exists(self, title: str, announcement_date: datetime, stock_code: str = None) -> bool:
        """检查事件是否已存在"""
        try:
            existing = await db_service.get_event_by_title_date(title, announcement_date, stock_code)
            return existing is not None
        except:
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

        pbar = tqdm(events_data, desc="保存事件", unit="条")

        for event_data in pbar:
            try:
                title = event_data.get("title", "")
                announcement_date = event_data.get("announcement_date", datetime.now())

                # 检查是否已存在
                if await self.check_event_exists(title, announcement_date, stock_code=event_data.get("stock_code")):
                    skipped_count += 1
                    continue

                event_type = event_data.get("event_type", EventType.OTHER)
                event_category = event_data.get("event_category")

                if event_category is None:
                    event_category = EventCategory.COMPANY_UPDATES

                # 使用本地PDF URL（如果有）
                original_url = event_data.get("local_pdf_url") or event_data.get("original_url", "")

                event_create = EventCreate(
                    title=title,
                    content=event_data.get("content", ""),
                    event_category=event_category,
                    event_type=event_type,
                    announcement_date=announcement_date,
                    source=event_data.get("source", ""),
                    original_url=original_url,
                    stock_code=event_data.get("stock_code", ""),
                    stock_name=event_data.get("stock_name", ""),
                )

                await db_service.create_event(event_create)
                saved_count += 1

                if saved_count % 10 == 0:
                    pbar.set_description(f"已保存 {saved_count}, 跳过 {skipped_count}")

            except Exception as e:
                print(f"\n保存事件失败: {e}")
                continue

        print(f"\n统计: 新增 {saved_count} 条, 跳过 {skipped_count} 条")
        return saved_count

    async def monitor_exchanges(self):
        """
        持续监控证券交易所公告 (30分钟一次)
        """
        print(f"启动证券交易所监控 (间隔: 30分钟)")
        
        # 交易所配置
        exchange_config = {
            "深圳证券交易所": {
                "concurrent": 3,
                "headers": {
                    "Referer": "https://www.szse.cn/disclosure/listed/notice/index.html",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
                }
            },
            "上海证券交易所": {
                "concurrent": 3,
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    "Accept": "application/pdf,application/json,text/plain,*/*"
                }
            },
            "北京证券交易所": {
                "concurrent": 5,
                "headers": {
                    "Referer": "https://www.bse.cn/disclosure/announcement.html"
                }
            }
        }

        while True:
            try:
                date = datetime.now()
                print(f"\n[{date.strftime('%H:%M:%S')}] 开始检查交易所公告...")

                # 1. 获取公告
                exchange_notices = await self.fetch_exchange_notices(date)

                # 2. 预处理：过滤已存在的公告，避免重复下载PDF
                new_exchange_notices = {}
                skipped_total = 0
                
                print(f"[{date.strftime('%H:%M:%S')}] 检查数据库重复项...")
                
                for exchange_name, notices in exchange_notices.items():
                    if not notices:
                        continue
                        
                    new_notices = []
                    for notice in notices:
                        title = notice.get("title", "")
                        notice_date = notice.get("announcement_date", date)
                        stock_code = notice.get("stock_code")
                        
                        # 检查数据库
                        if await self.check_event_exists(title, notice_date, stock_code):
                            skipped_total += 1
                            continue
                            
                        new_notices.append(notice)
                    
                    if new_notices:
                        new_exchange_notices[exchange_name] = new_notices
                        print(f"  {exchange_name}: 发现 {len(new_notices)} 条新公告 (跳过 {len(notices) - len(new_notices)} 条重复)")
                    elif len(notices) > 0:
                        print(f"  {exchange_name}: 所有 {len(notices)} 条公告均已存在，全部跳过")

                if skipped_total > 0:
                     print(f"[{date.strftime('%H:%M:%S')}] 总计跳过 {skipped_total} 条重复公告，无需下载PDF")

                # 3. 处理PDF (只处理新公告)
                if new_exchange_notices:
                    print(f"[{date.strftime('%H:%M:%S')}] 批量处理新公告的PDF文件...")
                    for exchange_name, notices in new_exchange_notices.items():
                        config = exchange_config.get(exchange_name, {"concurrent": 10, "headers": None})
                        processed_notices = await self.process_pdfs_for_notices(
                            notices, 
                            max_concurrent=config["concurrent"], 
                            headers=config["headers"]
                        )
                        new_exchange_notices[exchange_name] = processed_notices
                else:
                    print(f"[{date.strftime('%H:%M:%S')}] 没有需要处理的新公告")

                # 4. 转换并保存
                all_events = []
                # 注意：这里我们只保存 new_exchange_notices 中的数据
                # 之前的逻辑是遍历所有的 exchange_notices，但这会导致重复尝试保存（虽然保存层也有去重）
                # 既然我们在前面已经过滤了，这里只处理 new_exchange_notices 即可高效入库
                for exchange_name, notices in new_exchange_notices.items():
                    for notice in notices:
                        try:
                            bulletin_type = notice.get("bulletin_type", "其他")
                            event_type = self._map_bulletin_type_to_event_type(exchange_name, bulletin_type)

                            event_data = {
                                "title": notice.get("title", ""),
                                "content": notice.get("content", notice.get("title", "")),
                                "announcement_date": notice.get("announcement_date", date),
                                "source": exchange_name,
                                "original_url": notice.get("url", ""),
                                "local_pdf_url": notice.get("local_pdf_url", ""),
                                "event_type": event_type,
                                "event_category": EventCategory.COMPANY_UPDATES,
                                "stock_code": notice.get("stock_code", ""),
                                "stock_name": notice.get("stock_name", ""),
                            }
                            all_events.append(event_data)
                        except Exception as e:
                            print(f"转换事件失败: {e}")

                if all_events:
                    print(f"[{date.strftime('%H:%M:%S')}] 保存 {len(all_events)} 条公告到数据库...")
                    saved_count = await self.process_and_save_events(all_events)
                    print(f"[{date.strftime('%H:%M:%S')}] 交易所更新完成: 新增 {saved_count} 条")
                else:
                    print(f"[{date.strftime('%H:%M:%S')}] 没有新公告")

            except Exception as e:
                print(f"交易所监控发生错误: {e}")
                import traceback
                traceback.print_exc()

            # 等待 30 分钟
            await asyncio.sleep(1800)

    async def monitor_telegraph(self):
        """
        持续监控财联社电报 (10秒一次)
        """
        print(f"启动财联社电报监控 (间隔: 10秒)")
        while True:
            try:
                # 获取电报
                telegraphs = await self.fetch_cls_telegraph()
                
                if telegraphs:
                    # 直接保存（fetch_cls_telegraph已经返回了正确的格式吗？
                    # 查看 fetch_cls_telegraph 实现: Returns list[dict]
                    # process_and_save_events 需要 list[dict] 且包含 event_category 等字段
                    # fetch_cls_telegraph 应该已经处理好了格式? 
                    # 之前的代码直接调用 self.process_and_save_events(all_events) 其中all_events包含telegraphs
                    # 所以格式应该是兼容的。
                    
                    # 为了不刷屏，只在有数据时打印？或者定期打印心跳?
                    # 只保存新增的
                    saved_count = await self.process_and_save_events(telegraphs)
                    if saved_count > 0:
                         print(f"[{datetime.now().strftime('%H:%M:%S')}] 财联社更新: 新增 {saved_count} 条")
                
            except Exception as e:
                print(f"财联社监控发生错误: {e}")
            
            # 等待 10 秒
            await asyncio.sleep(10)


async def main():
    """主程序：启动监控"""
    print(f"{'='*60}")
    print("Stock News Monitor Service Started")
    print(f"{'='*60}")

    updater = EventUpdater()
    
    # 连接数据库 (全局只需一次)
    await connect_to_mongo()
    
    try:
        # 并发运行两个监控任务
        await asyncio.gather(
            updater.monitor_exchanges(),
            updater.monitor_telegraph()
        )
    except asyncio.CancelledError:
        print("监控服务已停止")
    except KeyboardInterrupt:
        print("用户中断")
    finally:
        await close_mongo_connection()
        print("数据库连接已关闭")


if __name__ == "__main__":
    # Windows 下使用 WindowsSelectorEventLoopPolicy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass

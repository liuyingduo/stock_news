"""
深交所公告爬虫
从深圳证券交易所官网获取公告信息
"""
import requests
import re
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class SZSENoticeFetcher:
    """深交所公告爬虫类"""

    def __init__(self):
        """初始化爬虫"""
        self.base_url = "https://www.szse.cn/api/disc/announcement/annList"
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json",
            "Origin": "https://www.szse.cn",
            "Pragma": "no-cache",
            "Referer": "https://www.szse.cn/disclosure/listed/notice/index.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0",
            "X-Request-Type": "ajax",
            "X-Requested-With": "XMLHttpRequest",
        })

    def _fetch_page(
        self,
        start_date: str,
        end_date: str,
        page_no: int = 1,
        page_size: int = 50,
        big_category_ids: Optional[List[str]] = None
    ) -> Optional[dict]:
        """
        获取指定日期范围的公告列表（单页）

        Args:
            start_date: 开始日期，格式: YYYY-MM-DD
            end_date: 结束日期，格式: YYYY-MM-DD
            page_no: 页码（从 1 开始）
            page_size: 每页数量
            big_category_ids: 大类ID列表（可选，不传则获取所有类别）

        Returns:
            公告列表数据，失败返回 None
        """
        try:
            # 添加随机延时，避免请求过快
            time.sleep(random.uniform(0.3, 0.8))

            # 构建请求参数
            payload = {
                "seDate": [start_date, end_date],
                "channelCode": ["listedNotice_disc"],
                "pageSize": page_size,
                "pageNum": page_no
            }

            # 添加类别过滤
            if big_category_ids:
                payload["bigCategoryId"] = big_category_ids

            # 添加 random 参数
            params = {"random": str(random.random())}

            response = self.session.post(
                self.base_url,
                params=params,
                json=payload,
                timeout=15
            )

            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                return None

            data = response.json()

            # 检查返回的数据是否有效
            if "data" not in data:
                print("Invalid response: missing 'data' field")
                return None

            return data

        except requests.exceptions.Timeout:
            print(f"Request timeout for page {page_no}")
            return None
        except Exception as e:
            print(f"Error fetching page {page_no}: {e}")
            return None

    def fetch_notices_by_date(
        self,
        date: datetime,
        big_category_ids: Optional[List[str]] = None
    ) -> List[dict]:
        """
        获取指定日期的所有公告（支持自动翻页）

        Args:
            date: 日期对象
            big_category_ids: 大类ID列表（可选）

        Returns:
            公告列表，每个公告包含:
                - title: 公告标题
                - url: 公告详情页 URL
                - stock_code: 股票代码
                - stock_name: 股票名称
                - announcement_date: 公告日期
                - bulletin_type: 公告类型（从标题推断）
        """
        date_str = date.strftime("%Y-%m-%d")
        all_notices = []
        page_no = 1
        page_size = 50

        category_info = f" (category: {big_category_ids})" if big_category_ids else ""
        print(f"Fetching SZSE notices for {date_str}{category_info}...")

        while True:
            # 获取当前页数据
            data = self._fetch_page(
                date_str,
                date_str,
                page_no,
                page_size,
                big_category_ids
            )

            if not data:
                # 如果第一页就失败，返回空列表
                if page_no == 1:
                    print(f"No data found for {date_str}")
                    return []
                # 否则认为已经获取完所有页
                break

            # 获取公告总数
            total_count = data.get("announceCount", 0)
            if page_no == 1 and total_count > 0:
                print(f"Total records: {total_count}")

            # 解析公告数据
            records = data.get("data", [])

            if not records:
                print(f"No records found on page {page_no}")
                break

            # 处理公告数据
            for record in records:
                try:
                    # 获取相对路径并拼接完整 URL
                    attach_path = record.get("attachPath", "")
                    if attach_path.startswith("/"):
                        full_url = "https://disc.static.szse.cn/download" + attach_path
                    else:
                        full_url = attach_path

                    # 获取股票代码和名称（可能是数组）
                    sec_codes = record.get("secCode", [])
                    sec_names = record.get("secName", [])

                    if sec_codes:
                        stock_code = sec_codes[0] if sec_codes else ""
                    else:
                        stock_code = ""

                    if sec_names:
                        stock_name = sec_names[0] if sec_names else ""
                    else:
                        stock_name = ""

                    # 解析发布时间
                    publish_time_str = record.get("publishTime", "")
                    try:
                        publish_time = datetime.strptime(publish_time_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        publish_time = date

                    # 从标题推断公告类型
                    bulletin_type = self._infer_bulletin_type_from_title(record.get("title", ""))

                    notice = {
                        "title": record.get("title", ""),
                        "url": full_url,
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "announcement_date": publish_time,
                        "bulletin_type": bulletin_type,
                        "source": "深圳证券交易所",
                        "ann_id": record.get("annId", ""),
                    }

                    # 只返回有效公告（有标题和 URL）
                    if notice["title"] and notice["url"]:
                        all_notices.append(notice)

                except Exception as e:
                    print(f"Error parsing record: {e}")
                    continue

            print(f"Fetched page {page_no}, got {len(records)} records (total: {len(all_notices)})")

            # 检查是否需要继续翻页
            # 如果返回的记录数少于 page_size，说明已经是最后一页
            if len(records) < page_size:
                break

            # 如果已经获取了所有记录，停止翻页
            if total_count and len(all_notices) >= total_count:
                break

            page_no += 1

            # 添加页间延时
            time.sleep(random.uniform(0.5, 1.0))

        print(f"Total fetched {len(all_notices)} notices for {date_str}")
        return all_notices

    def fetch_notices_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        big_category_ids: Optional[List[str]] = None
    ) -> List[dict]:
        """
        获取日期范围内的所有公告

        Args:
            start_date: 开始日期
            end_date: 结束日期
            big_category_ids: 大类ID列表（可选）

        Returns:
            公告列表
        """
        all_notices = []
        current_date = start_date

        while current_date <= end_date:
            daily_notices = self.fetch_notices_by_date(current_date, big_category_ids)
            all_notices.extend(daily_notices)
            current_date += timedelta(days=1)

        return all_notices

    def _infer_bulletin_type_from_title(self, title: str) -> str:
        """
        从标题推断公告类型

        Args:
            title: 公告标题

        Returns:
            公告类型描述
        """
        # 定义关键词映射
        type_keywords = {
            "财务报告": ["年度报告", "半年度报告", "季度报告", "业绩报告", "财务报表"],
            "业绩预告": ["业绩预告", "业绩预报", "业绩预测"],
            "业绩快报": ["业绩快报"],
            "分红": ["分红", "利润分配", "派息", "股利"],
            "增发": ["增发", "非公开发行", "定向发行"],
            "配股": ["配股"],
            "可转债": ["可转债", "转债"],
            "公司债券": ["公司债券", "公司债"],
            "重大事项": ["重大事项", "重大合同", "重大投资", "重大资产"],
            "资产重组": ["重组", "资产重组", "重大资产重组", "发行股份购买资产"],
            "收购兼并": ["收购", "兼并", "并购"],
            "股权变动": ["股权变动", "持股变动", "股份变动"],
            "减持": ["减持"],
            "增持": ["增持"],
            "董事会": ["董事会", "董事会决议"],
            "监事会": ["监事会", "监事会决议"],
            "股东大会": ["股东大会", "股东会决议"],
            "高管变动": ["高级管理人员", "高管", "辞职", "聘任"],
            "人事变动": ["人事变动", "人事调整"],
            "名称变更": ["名称变更", "更名"],
            "经营范围变更": ["经营范围", "营业范围"],
            "风险提示": ["风险提示", "风险警示"],
            "退市风险": ["退市风险", "终止上市", "暂停上市"],
            "诉讼": ["诉讼", "仲裁"],
            "处罚": ["处罚", "行政处罚", "监管"],
        }

        # 检查标题中的关键词
        for bulletin_type, keywords in type_keywords.items():
            for keyword in keywords:
                if keyword in title:
                    return bulletin_type

        return "其他"


def fetch_szse_notices_by_date(
    date: datetime,
    big_category_ids: Optional[List[str]] = None
) -> List[dict]:
    """
    便捷函数：获取指定日期的深交所公告

    Args:
        date: 日期对象
        big_category_ids: 大类ID列表（可选）

    Returns:
        公告列表
    """
    fetcher = SZSENoticeFetcher()
    return fetcher.fetch_notices_by_date(date, big_category_ids)


# 测试代码（完成后删除）
if __name__ == "__main__":
    # 测试获取最近的公告
    test_date = datetime.now() - timedelta(days=1)
    print(f"Testing SZSE notice fetcher for {test_date.strftime('%Y-%m-%d')}")

    fetcher = SZSENoticeFetcher()

    # 测试获取所有类别
    print("\n=== 测试1: 获取所有类别 ===")
    notices = fetcher.fetch_notices_by_date(test_date)

    print(f"\n=== Test Results ===")
    print(f"Total notices: {len(notices)}")

    if notices:
        print("\nFirst 5 notices:")
        for i, notice in enumerate(notices[:5], 1):
            print(f"\n{i}. {notice['title'][:50]}...")
            print(f"   Code: {notice['stock_code']}")
            print(f"   Name: {notice['stock_name']}")
            print(f"   Type: {notice['bulletin_type']}")
            print(f"   Date: {notice['announcement_date'].strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   URL: {notice['url'][:80]}..." if len(notice['url']) > 80 else f"   URL: {notice['url']}")

    # 测试获取特定类别
    print("\n\n=== 测试2: 获取特定类别 (0129) ===")
    notices_category = fetcher.fetch_notices_by_date(test_date, big_category_ids=["0129"])
    print(f"Total notices (category 0129): {len(notices_category)}")

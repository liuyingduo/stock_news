"""
上交所公告爬虫
从上海证券交易所官网获取公告信息
"""
import requests
import re
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class SSENoticeFetcher:
    """上交所公告爬虫类"""

    def __init__(self):
        """初始化爬虫"""
        self.base_url = "https://query.sse.com.cn/security/stock/queryCompanyBulletinNew.do"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Connection": "keep-alive",
            "Referer": "https://www.sse.com.cn/",
        })

    def _parse_jsonp(self, jsonp_str: str) -> Optional[dict]:
        """
        解析 JSONP 响应

        Args:
            jsonp_str: JSONP 格式的字符串

        Returns:
            解析后的字典，失败返回 None
        """
        if not jsonp_str:
            return None

        try:
            # 移除 jsonpCallback 前缀和括号
            # 格式: jsonpCallback12345({...});
            match = re.search(r'jsonpCallback\d+\((.+)\);?', jsonp_str)
            if match:
                json_str = match.group(1)
                return json.loads(json_str)
            else:
                # 尝试直接解析
                return json.loads(jsonp_str)
        except Exception as e:
            print(f"Error parsing JSONP: {e}")
            return None

    def _fetch_page(self, date_str: str, page_no: int = 1, page_size: int = 25) -> Optional[dict]:
        """
        获取指定日期的公告列表（单页）

        Args:
            date_str: 日期字符串，格式: YYYY-MM-DD
            page_no: 页码（从 1 开始）
            page_size: 每页数量

        Returns:
            公告列表数据，失败返回 None
        """
        try:
            # 添加随机延时，避免请求过快
            time.sleep(random.uniform(0.3, 0.8))

            params = {
                "jsonCallBack": f"jsonpCallback{int(time.time() * 1000)}",
                "isPagination": "true",
                "pageHelp.pageSize": str(page_size),
                "pageHelp.cacheSize": "1",
                "START_DATE": date_str,
                "END_DATE": date_str,
                "SECURITY_CODE": "",
                "TITLE": "",
                "BULLETIN_TYPE": "",
                "stockType": "",
                "pageHelp.pageNo": str(page_no),
                "pageHelp.beginPage": str(page_no),
                "pageHelp.endPage": str(page_no),
                "_": str(int(time.time() * 1000))
            }

            response = self.session.get(self.base_url, params=params, timeout=15)

            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                return None

            # 解析 JSONP 响应
            data = self._parse_jsonp(response.text)
            if not data:
                print("Failed to parse JSONP response")
                return None

            return data

        except requests.exceptions.Timeout:
            print(f"Request timeout for page {page_no}")
            return None
        except Exception as e:
            print(f"Error fetching page {page_no}: {e}")
            return None

    def fetch_notices_by_date(self, date: datetime) -> List[dict]:
        """
        获取指定日期的所有公告（支持自动翻页）

        Args:
            date: 日期对象

        Returns:
            公告列表，每个公告包含:
                - title: 公告标题
                - url: 公告详情页 URL
                - stock_code: 股票代码
                - stock_name: 股票名称
                - announcement_date: 公告日期
                - bulletin_type: 公告类型
        """
        date_str = date.strftime("%Y-%m-%d")
        all_notices = []
        page_no = 1
        page_size = 25
        total_count = 0  # 总记录数

        print(f"Fetching SSE notices for {date_str}...")

        while True:
            # 获取当前页数据
            data = self._fetch_page(date_str, page_no, page_size)

            if not data:
                # 如果第一页就失败，返回空列表
                if page_no == 1:
                    print(f"No data found for {date_str}")
                    return []
                # 否则认为已经获取完所有页
                break

            # 获取总记录数（从 pageHelp 中）
            if "pageHelp" in data:
                page_help = data["pageHelp"]
                if not total_count:
                    total_count = page_help.get("total", 0)
                    print(f"Total records: {total_count}")

            # 解析返回的数据
            # 上交所 API 返回的数据结构：result 是一个二维数组 [[{公告1}, {公告2}], [{公告3}, {公告4}]]
            page_records = []

            if "result" in data and isinstance(data["result"], list):
                # result 是一个列表，每个元素又是一个列表
                for inner_list in data["result"]:
                    if isinstance(inner_list, list):
                        page_records.extend(inner_list)
                    elif isinstance(inner_list, dict):
                        page_records.append(inner_list)
            elif "pageHelp" in data and "data" in data["pageHelp"]:
                # 也可以从 pageHelp.data 中获取
                page_help_data = data["pageHelp"]["data"]
                if isinstance(page_help_data, list):
                    for inner_list in page_help_data:
                        if isinstance(inner_list, list):
                            page_records.extend(inner_list)
                        elif isinstance(inner_list, dict):
                            page_records.append(inner_list)

            if not page_records:
                print(f"No records found on page {page_no}")
                break

            # 处理公告数据
            for record in page_records:
                try:
                    # 获取相对 URL
                    relative_url = record.get("URL", "")
                    # 拼接完整 URL
                    if relative_url.startswith("/"):
                        full_url = "https://static.sse.com.cn" + relative_url
                    else:
                        full_url = relative_url

                    notice = {
                        "title": record.get("TITLE", ""),
                        "url": full_url,
                        "stock_code": record.get("SECURITY_CODE", ""),
                        "stock_name": record.get("SECURITY_NAME", ""),
                        "announcement_date": date,
                        "bulletin_type": record.get("BULLETIN_TYPE_DESC", ""),
                        "source": "上海证券交易所",
                    }

                    # 只返回有效公告（有标题和 URL）
                    if notice["title"] and notice["url"]:
                        all_notices.append(notice)

                except Exception as e:
                    print(f"Error parsing record: {e}")
                    continue

            print(f"Fetched page {page_no}, got {len(page_records)} records (total: {len(all_notices)})")

            # 检查是否需要继续翻页
            # 如果已经获取了所有记录，停止翻页
            if total_count and len(all_notices) >= total_count:
                break

            # 如果返回的记录数少于 page_size，说明已经是最后一页
            if len(page_records) < page_size:
                break

            page_no += 1

            # 添加页间延时
            time.sleep(random.uniform(0.5, 1.0))

        print(f"Total fetched {len(all_notices)} notices for {date_str}")
        return all_notices

    def fetch_notices_by_date_range(self, start_date: datetime, end_date: datetime) -> List[dict]:
        """
        获取日期范围内的所有公告

        Args:
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            公告列表
        """
        all_notices = []
        current_date = start_date

        while current_date <= end_date:
            daily_notices = self.fetch_notices_by_date(current_date)
            all_notices.extend(daily_notices)
            current_date += timedelta(days=1)

        return all_notices


def fetch_sse_notices_by_date(date: datetime) -> List[dict]:
    """
    便捷函数：获取指定日期的上交所公告

    Args:
        date: 日期对象

    Returns:
        公告列表
    """
    fetcher = SSENoticeFetcher()
    return fetcher.fetch_notices_by_date(date)


# 测试代码（完成后删除）
if __name__ == "__main__":
    # 测试获取今天的公告
    test_date = datetime.now() - timedelta(days=1)  # 测试昨天的数据
    print(f"Testing SSE notice fetcher for {test_date.strftime('%Y-%m-%d')}")

    fetcher = SSENoticeFetcher()
    notices = fetcher.fetch_notices_by_date(test_date)

    print(f"\n=== Test Results ===")
    print(f"Total notices: {len(notices)}")

    if notices:
        print("\nFirst 5 notices:")
        for i, notice in enumerate(notices[:5], 1):
            print(f"\n{i}. {notice['title']}")
            print(f"   Code: {notice['stock_code']}")
            print(f"   Name: {notice['stock_name']}")
            print(f"   Type: {notice['bulletin_type']}")
            print(f"   URL: {notice['url']}")

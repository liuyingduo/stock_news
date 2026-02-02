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

        # 公告类别定义 (代码 -> 名称)
        self.categories = {
            "010301": "年度报告",
            "010303": "半年度报告",
            "010305": "一季度报告",
            "010307": "三季度报告",
            "0102": "首次公开发行及上市",
            "0105": "配股",
            "0107": "增发",
            "0109": "可转换债券",
            "0110": "权证相关公告",
            "0111": "其它融资",
            "0113": "权益分派与限制出售股份上市",
            "0115": "股权变动",
            "0117": "交易",
            "0119": "股东会",
            "0121": "澄清、风险提示、业绩预告事项",
            "0125": "特别处理和退市",
            "0127": "补充及更正",
            "0129": "中介机构报告",
            "0131": "上市公司制度",
            "0139": "债券公告",
            "0123": "其它重大事项",
            "01239901": "董事会公告",
            "01239910": "监事会公告",
        }

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
        注意：如果不指定 big_category_ids，将遍历所有已知类别以获取准确的分类代码

        Args:
            date: 日期对象
            big_category_ids: 大类ID列表（可选）

        Returns:
            公告列表
        """
        date_str = date.strftime("%Y-%m-%d")
        all_notices = []
        
        # 确定要获取的类别列表
        target_categories = big_category_ids if big_category_ids else list(self.categories.keys())
        
        print(f"Fetching SZSE notices for {date_str} (iterating {len(target_categories)} categories)...")

        # 遍历每个类别进行获取
        for category_id in target_categories:
            category_name = self.categories.get(category_id, category_id)
            # print(f"  Fetching category: {category_name} ({category_id})")
            
            page_no = 1
            page_size = 50
            
            while True:
                # 获取当前页数据
                data = self._fetch_page(
                    date_str,
                    date_str,
                    page_no,
                    page_size,
                    [category_id]
                )

                if not data:
                    break

                # 获取公告总数
                total_count = data.get("announceCount", 0)
                
                # 解析公告数据
                records = data.get("data", [])

                if not records:
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

                        # 使用当前遍历的类别名称作为 bulletin_type
                        bulletin_type = category_name

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

                # 检查是否需要继续翻页
                if len(records) < page_size:
                    break
                
                # 防止死循环
                if page_no > 50:
                    break

                page_no += 1
                time.sleep(random.uniform(0.2, 0.5))

        print(f"Total fetched {len(all_notices)} notices for {date_str}")
        return all_notices


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




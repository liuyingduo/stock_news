"""
北交所公告爬虫
从北京证券交易所官网获取公告信息
"""
import requests
import re
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json


class BSENoticeFetcher:
    """北交所公告爬虫类"""

    def __init__(self):
        """初始化爬虫"""
        self.base_url = "https://www.bse.cn/disclosureInfoController/companyAnnouncement.do"
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.bse.cn",
            "Pragma": "no-cache",
            "Referer": "https://www.bse.cn/disclosure/announcement.html",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36 Edg/144.0.0.0",
            "X-Requested-With": "XMLHttpRequest",
        })

        # 公告类别定义
        self.categories = {
            "年度报告": ["9503-1001", "9503-1005"],
            "半年度报告": ["9503-1002", "9503-1006"],
            "一季度报告": ["9503-1003", "9504-8001"],
            "三季度报告": ["9503-1004", "9504-2106"],
            "业绩预告、业绩快报类": ["9504-0301", "9504-0302", "9504-0303", "9504-0304"],
            "公开发行类": [
                "9504-2006", "9504-2007", "9504-2008", "9504-2722", "9504-2723",
                "9504-4003", "9504-4004", "9504-4005",
                "9533-1001", "9533-1002", "9533-1005", "9533-1006", "9533-1007",
                "9533-1008", "9533-1003", "9533-1004", "9533-1018", "9533-1010",
                "9533-1011", "9533-1012", "9533-1013", "9533-1014", "9533-1015",
                "9533-1016", "9533-1017", "9533-1019", "9533-1020", "9533-1021",
                "9533-1022", "9533-1023", "9533-1024", "9533-9998", "9533-9999"
            ],
            "董事会决议": ["9504-0401"],
            "监事会决议": ["9504-0402"],
            "股东大会决议": ["9504-0404"],
            "权益分派": ["9504-0603", "9504-0604"],
            "股权激励类": [
                "9504-1301", "9504-1302", "9504-1303", "9504-1304", "9504-1305",
                "9504-1306", "9504-1307", "9504-1308", "9504-1309", "9504-1310",
                "9504-1311", "9504-1312", "9504-1314", "9504-1315", "9504-1316",
                "9504-3399"
            ],
            "员工持股计划类": ["9504-1401", "9504-1402", "9504-1403", "9504-3499"],
            "募集资金管理类": [
                "9504-4401", "9504-4402", "9504-4403", "9504-4404", "9504-4405",
                "9504-4406", "9504-4407", "9504-4408", "9504-4409", "9504-4410",
                "9504-4411", "9504-4412", "9504-4413", "9504-4414", "9504-4415",
                "9504-4416", "9504-4417", "9504-4418", "9504-4499"
            ],
            "股份回购类": [
                "9504-3501", "9504-3502", "9504-3503", "9504-3504", "9504-3505",
                "9504-3506", "9504-3507", "9504-3508", "9504-3509", "9504-3510",
                "9504-3511", "9504-3512", "9504-3513", "9504-3539", "9504-3599"
            ],
            "公司经营类": [
                "9504-0503", "9504-0502", "9504-0504", "9504-2404", "9504-2405",
                "9504-2406", "9504-2407", "9504-2408", "9504-2409", "9504-0501",
                "9504-2411", "9504-2412", "9504-2413", "9504-2414", "9504-2471",
                "9504-2472", "9504-2473", "9504-2474", "9504-2499"
            ],
        }

        # 生成代码到类别的反向映射
        self.code_to_category = {}
        for category, codes in self.categories.items():
            for code in codes:
                self.code_to_category[code] = category

    def _parse_jsonp(self, jsonp_str: str, callback_name: str) -> Optional[dict]:
        """
        解析 JSONP 响应

        Args:
            jsonp_str: JSONP 格式的字符串
            callback_name: 回调函数名

        Returns:
            解析后的字典，失败返回 None
        """
        if not jsonp_str:
            return None

        try:
            # 移除回调函数名和括号
            # 格式: jQuery1234567890_1234567890000([{...}]);
            match = re.search(rf'{callback_name}\((.+)\)', jsonp_str)
            if match:
                json_str = match.group(1)
                result = json.loads(json_str)

                # 结果是一个数组，取第一个元素
                if isinstance(result, list) and len(result) > 0:
                    return result[0]

                return result
            else:
                return None
        except Exception as e:
            print(f"Error parsing JSONP: {e}")
            return None

    def _fetch_page(
        self,
        start_date: str,
        end_date: str,
        page_no: int = 0,
        disclosure_subtypes: Optional[List[str]] = None
    ) -> Optional[dict]:
        """
        获取指定日期范围的公告列表（单页）

        Args:
            start_date: 开始日期，格式: YYYY-MM-DD
            end_date: 结束日期，格式: YYYY-MM-DD
            page_no: 页码（从 0 开始）
            disclosure_subtypes: 公告子类型列表（可选）

        Returns:
            公告列表数据，失败返回 None
        """
        try:
            # 添加随机延时
            time.sleep(random.uniform(0.3, 0.8))

            # 手动构建表单数据，支持多值参数（数组）
            # 使用列表形式 [(key, value), ...] 来处理数组参数
            form_data = [
                ("startTime", start_date),
                ("endTime", end_date),
                ("isNewThree", "1"),
                ("page", str(page_no)),
                ("companyCd", ""),
                ("keyword", ""),
                ("sortfield", "xxssdq"),
                ("sorttype", "asc"),
            ]

            # 添加数组参数
            form_data.append(("xxfcbj[]", "2"))

            # 添加需要的字段
            need_fields = [
                "companyCd", "companyName", "disclosureTitle",
                "disclosurePostTitle", "destFilePath", "publishDate",
                "xxfcbj", "fileExt", "xxzrlx"
            ]
            for field in need_fields:
                form_data.append(("needFields[]", field))

            # 添加公告子类型
            if disclosure_subtypes:
                for subtype in disclosure_subtypes:
                    form_data.append(("disclosureSubtype[]", subtype))

            # 生成随机的 callback 名称
            callback_name = f"jQuery{random.randint(1000000000, 9999999999)}_{int(time.time() * 1000)}"
            params = {"callback": callback_name}

            response = self.session.post(
                self.base_url,
                params=params,
                data=form_data,  # 使用form_data列表而不是字典
                timeout=15
            )

            if response.status_code != 200:
                print(f"HTTP Error: {response.status_code}")
                return None

            # 解析 JSONP 响应
            result = self._parse_jsonp(response.text, callback_name)
            if not result:
                print("Failed to parse JSONP response")
                return None

            return result

        except requests.exceptions.Timeout:
            print(f"Request timeout for page {page_no}")
            return None
        except Exception as e:
            print(f"Error fetching page {page_no}: {e}")
            return None

    def fetch_notices_by_date(
        self,
        date: datetime,
        disclosure_subtypes: Optional[List[str]] = None
    ) -> List[dict]:
        """
        获取指定日期的所有公告（支持自动翻页）

        Args:
            date: 日期对象
            disclosure_subtypes: 公告子类型列表（可选）

        Returns:
            公告列表
        """
        date_str = date.strftime("%Y-%m-%d")
        all_notices = []
        page_no = 0

        subtype_info = f" (subtypes: {disclosure_subtypes})" if disclosure_subtypes else ""
        print(f"Fetching BSE notices for {date_str}{subtype_info}...")

        while True:
            # 获取当前页数据
            result = self._fetch_page(
                date_str,
                date_str,
                page_no,
                disclosure_subtypes
            )

            if not result:
                # 如果第一页就失败，返回空列表
                if page_no == 0:
                    print(f"No data found for {date_str}")
                    return []
                # 否则认为已经获取完所有页
                break

            # 从响应中提取数据
            if "listInfo" not in result:
                print(f"No listInfo in response")
                break

            list_info = result["listInfo"]
            total_elements = list_info.get("totalElements", 0)

            if page_no == 0 and total_elements > 0:
                print(f"Total records: {total_elements}")

            # 获取公告列表
            records = list_info.get("content", [])

            if not records:
                print(f"No records found on page {page_no}")
                break

            # 处理公告数据
            for record in records:
                try:
                    # 构建附件 URL
                    dest_file_path = record.get("destFilePath", "")
                    if dest_file_path.startswith("/"):
                        full_url = "https://www.bse.cn" + dest_file_path
                    else:
                        full_url = dest_file_path

                    # 解析发布时间
                    publish_date_str = record.get("publishDate", "")
                    try:
                        publish_date = datetime.strptime(publish_date_str, "%Y-%m-%d %H:%M:%S")
                    except:
                        publish_date = date

                    # 使用原始公告类型代码获取文本描述
                    raw_type_code = record.get("xxzrlx", "")
                    bulletin_type = self.code_to_category.get(raw_type_code, raw_type_code)

                    title = record.get("disclosureTitle", "")
                    notice = {
                        "title": title,
                        "url": full_url,
                        "stock_code": record.get("companyCd", ""),
                        "stock_name": record.get("companyName", ""),
                        "announcement_date": publish_date,
                        "bulletin_type": bulletin_type,
                        "source": "北京证券交易所",
                        "ann_id": raw_type_code,
                        "file_ext": record.get("fileExt", ""),
                    }

                    # 只返回有效公告（有标题和 URL）
                    if notice["title"] and notice["url"]:
                        all_notices.append(notice)

                except Exception as e:
                    print(f"Error parsing record: {e}")
                    continue

            print(f"Fetched page {page_no}, got {len(records)} records (total: {len(all_notices)})")

            # 检查是否需要继续翻页
            total_pages = list_info.get("totalPages", 0)
            if page_no >= total_pages - 1:
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
        disclosure_subtypes: Optional[List[str]] = None
    ) -> List[dict]:
        """
        获取日期范围内的所有公告

        Args:
            start_date: 开始日期
            end_date: 结束日期
            disclosure_subtypes: 公告子类型列表（可选）

        Returns:
            公告列表
        """
        all_notices = []
        current_date = start_date

        while current_date <= end_date:
            daily_notices = self.fetch_notices_by_date(current_date, disclosure_subtypes)
            all_notices.extend(daily_notices)
            current_date += timedelta(days=1)

        return all_notices


def fetch_bse_notices_by_date(
    date: datetime,
    disclosure_subtypes: Optional[List[str]] = None
) -> List[dict]:
    """
    便捷函数：获取指定日期的北交所公告

    Args:
        date: 日期对象
        disclosure_subtypes: 公告子类型列表（可选）

    Returns:
        公告列表
    """
    fetcher = BSENoticeFetcher()
    return fetcher.fetch_notices_by_date(date, disclosure_subtypes)

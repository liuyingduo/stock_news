"""
公告内容抓取器 - 从详情页抓取公告正文
支持并发抓取以提高速度
"""
import requests
import re

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional


def extract_art_code(url: str) -> Optional[str]:
    """
    从 URL 中提取文章代码 (art_code)
    Example: https://data.eastmoney.com/notices/detail/002590/AN202601301818593186.html -> AN202601301818593186
    """
    if not url:
        return None
    match = re.search(r'/([A-Z0-9]+)\.html', url)
    if match:
        return match.group(1)
    return None


def fetch_notice_content(url: str) -> str:
    """
    通过 API 获取公告正文内容（支持分页）

    Args:
        url: 公告详情页 URL

    Returns:
        公告正文内容，如果抓取失败返回空字符串
    """
    art_code = extract_art_code(url)
    if not art_code:
        return ""

    api_url = "https://np-cnotice-stock.eastmoney.com/api/content/ann"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": url,
        "Accept": "*/*"
    }

    try:
        # 使用 Session 保持会话
        session = requests.Session()
        session.headers.update(headers)

        # 获取第一页数据
        params = {
            "art_code": art_code,
            "client_source": "web",
            "page_index": 1
        }
        
        response = session.get(api_url, params=params, timeout=10)
        
        if response.status_code != 200:
            return ""

        data = response.json()
        if not data or data.get("success") != 1 or "data" not in data:
            return ""
            
        notice_data = data["data"]
        full_content = notice_data.get("notice_content", "") or ""
        
        # 检查是否需要分页
        # API 不需要 page_size 参数来请求，它在响应中返回 page_size (总页数) ?? 
        # 用户提供的 curl 示例中 page_size: 2，看起来是总页数。
        # 而请求参数 page_index 用于翻页。
        
        total_pages = notice_data.get("page_size", 1) # 这里字段名是 page_size 但含义似乎是总页数，或者每页大小？
        # 根据用户描述： "如果page_Size为2的话，其实就有两页" -> page_size 实际上是 total_pages
        
        if total_pages > 1:
            for page in range(2, total_pages + 1):
                try:
                    params["page_index"] = page
                    page_resp = session.get(api_url, params=params, timeout=10)
                    if page_resp.status_code == 200:
                        page_data = page_resp.json()
                        if page_data.get("success") == 1 and "data" in page_data:
                            content_part = page_data["data"].get("notice_content", "")
                            if content_part:
                                full_content += content_part
                except Exception:
                    continue # 忽略单页获取失败
                    
        return full_content.strip()

    except Exception:
        return ""


def fetch_notices_batch(notices: List[dict], max_workers: int = 20) -> List[dict]:
    """
    批量并发抓取公告内容

    Args:
        notices: 公告列表，每个公告需要有 'original_url' 和 'title' 字段
        max_workers: 最大并发数（默认20）

    Returns:
        更新后的公告列表，content 字段已填充
    """
    if not notices:
        return notices
    
    # 创建 URL 到索引的映射
    url_to_indices: Dict[str, List[int]] = {}
    for i, notice in enumerate(notices):
        url = notice.get("original_url", "")
        if url:
            if url not in url_to_indices:
                url_to_indices[url] = []
            url_to_indices[url].append(i)
    
    # 并发抓取
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {
            executor.submit(fetch_notice_content, url): url 
            for url in url_to_indices.keys()
        }
        
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                content = future.result()
                # 更新所有使用这个 URL 的公告
                for idx in url_to_indices[url]:
                    if content:
                        notices[idx]["content"] = content
                    else:
                        # 如果抓取失败，使用标题
                        notices[idx]["content"] = notices[idx].get("title", "")
            except Exception:
                # 抓取失败，使用标题
                for idx in url_to_indices[url]:
                    notices[idx]["content"] = notices[idx].get("title", "")
    
    return notices


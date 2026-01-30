"""
公告内容抓取器 - 从详情页抓取公告正文
"""
import requests
from lxml import etree


def fetch_notice_content(url: str) -> str:
    """
    抓取公告详情页的正文内容

    Args:
        url: 公告详情页 URL

    Returns:
        公告正文内容，如果抓取失败返回空字符串
    """
    if not url:
        return ""
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return ""
        
        # 解析 HTML
        tree = etree.HTML(response.text)
        
        # 使用 xpath 获取公告内容
        content_elements = tree.xpath('//*[@id="notice_content"]//text()')
        
        if content_elements:
            # 合并文本并清理空白
            content = ' '.join([text.strip() for text in content_elements if text.strip()])
            return content
        
        return ""
        
    except Exception:
        return ""

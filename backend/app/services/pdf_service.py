"""
PDF处理服务
下载、解析和存储PDF文件
"""
import os
import hashlib
import asyncio
import aiohttp
import aiofiles
from typing import Optional, Tuple
from pathlib import Path
import PyPDF2
from io import BytesIO


class PDFService:
    """PDF处理服务"""

    def __init__(self, storage_path: str = "static/pdfs"):
        """
        初始化PDF服务

        Args:
            storage_path: PDF文件存储路径
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def _get_file_hash(self, url: str) -> str:
        """
        根据URL生成文件hash

        Args:
            url: PDF文件URL

        Returns:
            文件hash值
        """
        return hashlib.md5(url.encode('utf-8')).hexdigest()

    def _get_pdf_path(self, url: str) -> Tuple[Path, str]:
        """
        获取PDF文件存储路径

        Args:
            url: PDF文件URL

        Returns:
            (文件路径, 文件名)
        """
        file_hash = self._get_file_hash(url)
        filename = f"{file_hash}.pdf"
        filepath = self.storage_path / filename
        return filepath, filename

    async def download_pdf(self, url: str, timeout: int = 30) -> Optional[Path]:
        """
        下载PDF文件

        Args:
            url: PDF文件URL
            timeout: 超时时间（秒）

        Returns:
            下载的文件路径，失败返回None
        """
        filepath, filename = self._get_pdf_path(url)

        # 如果文件已存在，直接返回
        if filepath.exists():
            print(f"  PDF已存在: {filename}")
            return filepath

        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=timeout), headers=headers) as response:
                    print(f"  下载状态: {response.status}")

                    if response.status != 200:
                        print(f"  HTTP错误: {response.status}")
                        return None

                    # 下载文件内容
                    content = await response.read()
                    print(f"  文件大小: {len(content)} 字节")

                    # 保存到本地
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(content)

                    print(f"  PDF保存成功: {filename}")
                    return filepath

        except asyncio.TimeoutError:
            print(f"  下载超时: {url}")
            return None
        except Exception as e:
            print(f"  下载失败: {type(e).__name__}: {e}")
            return None

    def parse_pdf_text(self, filepath: Path) -> str:
        """
        解析PDF文件内容为文本

        Args:
            filepath: PDF文件路径

        Returns:
            解析出的文本内容
        """
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text_content = []

                # 提取所有页面的文本
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text)

                # 合并所有页面文本
                full_text = '\n\n'.join(text_content)
                return full_text.strip()

        except Exception as e:
            print(f"Error parsing PDF {filepath}: {e}")
            return ""

    async def download_and_parse(self, url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        下载PDF并解析文本

        Args:
            url: PDF文件URL

        Returns:
            (本地PDF URL, 解析的文本内容)
        """
        # 下载PDF
        filepath = await self.download_pdf(url)

        if not filepath:
            return None, None

        # 解析PDF
        try:
            text_content = await asyncio.to_thread(self.parse_pdf_text, filepath)

            # 生成本地访问URL
            _, filename = self._get_pdf_path(url)
            local_url = f"/static/pdfs/{filename}"

            return local_url, text_content

        except Exception as e:
            print(f"Error processing PDF: {e}")
            return None, None

    async def process_pdf_batch(self, urls: list[str], max_concurrent: int = 10) -> dict:
        """
        批量处理PDF文件

        Args:
            urls: PDF URL列表
            max_concurrent: 最大并发数

        Returns:
            {url: (local_url, text_content)} 的字典
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_with_semaphore(url: str):
            async with semaphore:
                return url, await self.download_and_parse(url)

        tasks = [process_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        result_dict = {}
        for result in results:
            if isinstance(result, Exception):
                continue
            url, (local_url, text) = result
            if local_url:  # 只保存成功的结果
                result_dict[url] = (local_url, text)

        return result_dict


# 全局单例
pdf_service = PDFService()

"""
PDF文件清理工具
用于检测、删除损坏的PDF文件
"""
import sys
import os
from pathlib import Path

# 添加 backend 目录到 Python 路径
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

from app.services.pdf_service import pdf_service


def clean_corrupted_pdfs():
    """清理所有损坏的PDF文件"""
    storage_path = Path("static/pdfs")

    if not storage_path.exists():
        print(f"PDF存储目录不存在: {storage_path}")
        return

    pdf_files = list(storage_path.glob("*.pdf"))
    print(f"总共发现 {len(pdf_files)} 个PDF文件")
    print(f"{'='*60}")

    corrupted_count = 0
    valid_count = 0

    for pdf_file in pdf_files:
        is_valid = pdf_service._validate_pdf_file(pdf_file)

        if is_valid:
            valid_count += 1
        else:
            corrupted_count += 1
            # 删除损坏的文件
            pdf_service._delete_corrupted_pdf(pdf_file)

    print(f"{'='*60}")
    print(f"清理完成:")
    print(f"  有效文件: {valid_count}")
    print(f"  损坏文件: {corrupted_count} (已删除)")


def list_pdfs():
    """列出所有PDF文件及其状态"""
    storage_path = Path("static/pdfs")

    if not storage_path.exists():
        print(f"PDF存储目录不存在: {storage_path}")
        return

    pdf_files = list(storage_path.glob("*.pdf"))
    print(f"总共发现 {len(pdf_files)} 个PDF文件")
    print(f"{'='*60}")

    for pdf_file in pdf_files:
        size = pdf_file.stat().st_size
        is_valid = pdf_service._validate_pdf_file(pdf_file)
        status = "✓ 有效" if is_valid else "✗ 损坏"
        print(f"{status:8} | {size:10} bytes | {pdf_file.name}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="PDF文件清理工具")
    parser.add_argument("--clean", action="store_true", help="清理损坏的PDF文件")
    parser.add_argument("--list", action="store_true", help="列出所有PDF文件状态")

    args = parser.parse_args()

    if args.clean:
        clean_corrupted_pdfs()
    elif args.list:
        list_pdfs()
    else:
        parser.print_help()

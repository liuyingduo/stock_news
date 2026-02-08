"""
Sync full stock code/name master data from AkShare into MongoDB.
"""

import asyncio
import os
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple

import akshare as ak

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, backend_dir)

from app.core.database import close_mongo_connection, connect_to_mongo
from app.services.database_service import db_service

CODE_COLUMN_CANDIDATES: Tuple[str, ...] = (
    "code",
    "代码",
    "股票代码",
    "证券代码",
    "symbol",
    "ts_code",
)

NAME_COLUMN_CANDIDATES: Tuple[str, ...] = (
    "name",
    "名称",
    "股票简称",
    "证券简称",
    "display_name",
)


def _find_column(columns: Iterable[Any], candidates: Tuple[str, ...]) -> Optional[str]:
    column_names = [str(col).strip() for col in columns]
    lowered_lookup = {col.lower(): col for col in column_names}

    for candidate in candidates:
        if candidate in column_names:
            return candidate
        lowered = candidate.lower()
        if lowered in lowered_lookup:
            return lowered_lookup[lowered]
    return None


def _normalize_stock_code(raw_code: Any) -> str:
    code = str(raw_code).strip()
    if not code or code.lower() == "nan":
        return ""

    normalized = code.upper()
    if normalized.startswith(("SH", "SZ", "BJ")) and normalized[2:].isdigit():
        normalized = normalized[2:]

    if "." in normalized:
        left, right = normalized.split(".", 1)
        if left.isdigit() and right in {"SH", "SZ", "BJ"}:
            normalized = left

    if normalized.isdigit():
        return normalized.zfill(6)
    return normalized


def _extract_stocks_from_dataframe(df: Any, source_name: str) -> List[Dict[str, str]]:
    if df is None or df.empty:
        raise ValueError(f"{source_name}: empty dataframe")

    code_column = _find_column(df.columns, CODE_COLUMN_CANDIDATES)
    name_column = _find_column(df.columns, NAME_COLUMN_CANDIDATES)

    if not code_column or not name_column:
        raise ValueError(
            f"{source_name}: unsupported columns, got {list(df.columns)}"
        )

    deduped: Dict[str, Dict[str, str]] = {}
    for _, row in df.iterrows():
        code = _normalize_stock_code(row.get(code_column))
        name = str(row.get(name_column, "")).strip()
        if not code or not name or name.lower() == "nan":
            continue
        deduped[code] = {"code": code, "name": name}

    if not deduped:
        raise ValueError(f"{source_name}: no valid stock rows after filtering")

    return list(deduped.values())


def fetch_stock_master_from_akshare() -> List[Dict[str, str]]:
    fetchers = [
        ("ak.stock_info_a_code_name", ak.stock_info_a_code_name),
        ("ak.stock_zh_a_spot_em", ak.stock_zh_a_spot_em),
    ]

    last_error: Optional[Exception] = None
    for fetcher_name, fetcher in fetchers:
        try:
            df = fetcher()
            stocks = _extract_stocks_from_dataframe(df, fetcher_name)
            print(f"{fetcher_name}: fetched {len(stocks)} stock rows")
            return stocks
        except Exception as exc:
            last_error = exc
            print(f"{fetcher_name}: failed - {exc}")

    raise RuntimeError(f"AkShare stock master fetch failed: {last_error}")


async def sync_stock_master() -> Dict[str, int]:
    stocks = fetch_stock_master_from_akshare()
    result = await db_service.replace_all_stocks(stocks)
    print(
        f"Stock master sync completed. "
        f"deleted={result['deleted']} inserted={result['inserted']}"
    )
    return result


async def main() -> None:
    await connect_to_mongo()
    try:
        await sync_stock_master()
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

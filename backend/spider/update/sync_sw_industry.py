"""
Sync SW (Shenwan) level-3 sectors and sector-stock mappings into MongoDB.
"""

import asyncio
import os
import sys
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

import akshare as ak

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, backend_dir)

from app.core.database import close_mongo_connection, connect_to_mongo
from app.services.database_service import db_service

INDUSTRY_CODE_COLUMN_CANDIDATES: Tuple[str, ...] = (
    "行业代码",
    "代码",
    "指数代码",
    "code",
    "symbol",
)

INDUSTRY_NAME_COLUMN_CANDIDATES: Tuple[str, ...] = (
    "行业名称",
    "行业名",
    "名称",
    "name",
)

PARENT_NAME_COLUMN_CANDIDATES: Tuple[str, ...] = (
    "上级行业",
    "父级行业",
    "所属行业",
    "上级名称",
    "parent_name",
)

PARENT_CODE_COLUMN_CANDIDATES: Tuple[str, ...] = (
    "上级行业代码",
    "父级行业代码",
    "所属行业代码",
    "parent_code",
)

STOCK_CODE_COLUMN_CANDIDATES: Tuple[str, ...] = (
    "股票代码",
    "证券代码",
    "代码",
    "code",
    "symbol",
    "ts_code",
)

STOCK_NAME_COLUMN_CANDIDATES: Tuple[str, ...] = (
    "股票名称",
    "股票简称",
    "证券名称",
    "证券简称",
    "名称",
    "name",
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


def _extract_level_rows(df: Any, source_name: str) -> List[Dict[str, str]]:
    if df is None or df.empty:
        raise ValueError(f"{source_name}: empty dataframe")

    code_column = _find_column(df.columns, INDUSTRY_CODE_COLUMN_CANDIDATES)
    name_column = _find_column(df.columns, INDUSTRY_NAME_COLUMN_CANDIDATES)
    parent_name_column = _find_column(df.columns, PARENT_NAME_COLUMN_CANDIDATES)
    parent_code_column = _find_column(df.columns, PARENT_CODE_COLUMN_CANDIDATES)

    if not code_column or not name_column:
        raise ValueError(f"{source_name}: unsupported columns, got {list(df.columns)}")

    rows: List[Dict[str, str]] = []
    for _, row in df.iterrows():
        code = str(row.get(code_column, "")).strip()
        name = str(row.get(name_column, "")).strip()
        if not code or not name or code.lower() == "nan" or name.lower() == "nan":
            continue

        parent_name = ""
        parent_code = ""
        if parent_name_column:
            parent_name = str(row.get(parent_name_column, "")).strip()
        if parent_code_column:
            parent_code = str(row.get(parent_code_column, "")).strip()

        rows.append(
            {
                "code": code,
                "name": name,
                "parent_name": parent_name if parent_name.lower() != "nan" else "",
                "parent_code": parent_code if parent_code.lower() != "nan" else "",
            }
        )

    return rows


def fetch_sw_industry_hierarchy() -> List[Dict[str, str]]:
    sw1_rows = _extract_level_rows(ak.sw_index_first_info(), "ak.sw_index_first_info")
    sw2_rows = _extract_level_rows(ak.sw_index_second_info(), "ak.sw_index_second_info")
    sw3_rows = _extract_level_rows(ak.sw_index_third_info(), "ak.sw_index_third_info")

    level1_by_name = {row["name"]: row for row in sw1_rows}
    level1_by_code = {row["code"]: row for row in sw1_rows}

    level2_to_level1_by_code: Dict[str, Dict[str, str]] = {}
    level2_to_level1_by_name: Dict[str, Dict[str, str]] = {}

    for row2 in sw2_rows:
        parent = None
        parent_code = row2.get("parent_code", "")
        parent_name = row2.get("parent_name", "")

        if parent_code and parent_code in level1_by_code:
            parent = level1_by_code[parent_code]
        elif parent_name and parent_name in level1_by_name:
            parent = level1_by_name[parent_name]

        if not parent:
            continue

        mapping = {
            "industry_level1_code": parent["code"],
            "industry_level1_name": parent["name"],
            "industry_level2_code": row2["code"],
            "industry_level2_name": row2["name"],
        }
        level2_to_level1_by_code[row2["code"]] = mapping
        level2_to_level1_by_name[row2["name"]] = mapping

    hierarchy: List[Dict[str, str]] = []
    for row3 in sw3_rows:
        level2_info = None
        parent_code = row3.get("parent_code", "")
        parent_name = row3.get("parent_name", "")

        if parent_code and parent_code in level2_to_level1_by_code:
            level2_info = level2_to_level1_by_code[parent_code]
        elif parent_name and parent_name in level2_to_level1_by_name:
            level2_info = level2_to_level1_by_name[parent_name]

        hierarchy.append(
            {
                "industry_level1_code": (level2_info or {}).get("industry_level1_code", ""),
                "industry_level1_name": (level2_info or {}).get("industry_level1_name", ""),
                "industry_level2_code": (level2_info or {}).get("industry_level2_code", ""),
                "industry_level2_name": (level2_info or {}).get("industry_level2_name", parent_name),
                "industry_level3_code": row3["code"],
                "industry_level3_name": row3["name"],
            }
        )

    deduped: Dict[str, Dict[str, str]] = {}
    for item in hierarchy:
        level3_code = item.get("industry_level3_code", "")
        if not level3_code:
            continue
        deduped[level3_code] = item

    result = list(deduped.values())
    if not result:
        raise RuntimeError("No SW level-3 industry hierarchy rows were built.")
    return result


def fetch_level3_components(industry_code: str, industry_name: str) -> List[Dict[str, str]]:
    df = ak.sw_index_third_cons(symbol=industry_code)
    if df is None or df.empty:
        return []

    code_column = _find_column(df.columns, STOCK_CODE_COLUMN_CANDIDATES)
    name_column = _find_column(df.columns, STOCK_NAME_COLUMN_CANDIDATES)
    if not code_column:
        return []

    deduped: Dict[str, Dict[str, str]] = {}
    for _, row in df.iterrows():
        instrument = _normalize_stock_code(row.get(code_column))
        if not instrument:
            continue

        name = ""
        if name_column:
            raw_name = str(row.get(name_column, "")).strip()
            name = "" if raw_name.lower() == "nan" else raw_name

        deduped[instrument] = {
            "instrument": instrument,
            "name": name,
            "industry_level3_code": industry_code,
            "industry_level3_name": industry_name,
        }

    return list(deduped.values())


def build_sector_rows(hierarchy_rows: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    sectors: List[Dict[str, Any]] = []
    for row in hierarchy_rows:
        level3_code = row.get("industry_level3_code", "")
        level3_name = row.get("industry_level3_name", "")
        if not level3_code or not level3_name:
            continue

        level1_name = row.get("industry_level1_name", "")
        level2_name = row.get("industry_level2_name", "")
        description = f"申万三级行业 | 一级: {level1_name or '-'} | 二级: {level2_name or '-'}"

        sectors.append(
            {
                "code": level3_code,
                "name": level3_name,
                "risk_level": "neutral",
                "description": description,
                "related_event_ids": [],
                "industry_level": 3,
                "industry_level1_code": row.get("industry_level1_code", ""),
                "industry_level1_name": level1_name,
                "industry_level2_code": row.get("industry_level2_code", ""),
                "industry_level2_name": level2_name,
                "industry_level3_code": level3_code,
                "industry_level3_name": level3_name,
                "source": "sw_akshare",
            }
        )
    return sectors


async def sync_sw_industry_data(request_delay_seconds: float = 0.2) -> Dict[str, Any]:
    hierarchy_rows = fetch_sw_industry_hierarchy()
    sector_rows = build_sector_rows(hierarchy_rows)

    total = len(hierarchy_rows)
    success_count = 0
    fail_count = 0
    all_mappings: List[Dict[str, Any]] = []
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    print(f"SW hierarchy fetched: {total} level-3 industries")
    for idx, row in enumerate(hierarchy_rows, start=1):
        level3_code = row.get("industry_level3_code", "")
        level3_name = row.get("industry_level3_name", "")
        if not level3_code:
            fail_count += 1
            continue

        try:
            components = fetch_level3_components(level3_code, level3_name)
            for item in components:
                item.update(
                    {
                        "industry_level1_code": row.get("industry_level1_code", ""),
                        "industry_level1_name": row.get("industry_level1_name", ""),
                        "industry_level2_code": row.get("industry_level2_code", ""),
                        "industry_level2_name": row.get("industry_level2_name", ""),
                        "industry_level3_code": level3_code,
                        "industry_level3_name": level3_name,
                        "date": date_str,
                    }
                )
            all_mappings.extend(components)
            success_count += 1
            print(f"[{idx}/{total}] {level3_name} ({level3_code}) -> {len(components)} stocks")
        except Exception as exc:
            fail_count += 1
            print(f"[{idx}/{total}] {level3_name} ({level3_code}) failed: {exc}")

        if request_delay_seconds > 0:
            await asyncio.sleep(request_delay_seconds)

    sector_result = await db_service.replace_all_sectors(sector_rows)
    mapping_result = await db_service.replace_all_sector_stock_components(all_mappings)

    print(
        "SW sync completed. "
        f"sectors deleted={sector_result['deleted']} inserted={sector_result['inserted']}; "
        f"mappings deleted={mapping_result['deleted']} inserted={mapping_result['inserted']}; "
        f"level3 success={success_count} fail={fail_count}"
    )

    return {
        "sectors": sector_result,
        "mappings": mapping_result,
        "level3_total": total,
        "level3_success": success_count,
        "level3_fail": fail_count,
    }


async def main() -> None:
    await connect_to_mongo()
    try:
        await sync_sw_industry_data()
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.models import StockCreate, StockUpdate, StockResponse
from app.models.user import UserResponse
from app.services.auth import get_current_user
from app.core.database import get_database
from app.services.database_service import db_service
from app.services.radar_scoring import compute_event_scores, compute_market_index

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


class WatchlistPayload(BaseModel):
    code: str


def _normalize_stock_code(raw: str) -> str:
    cleaned = (raw or "").strip().upper().replace(" ", "")
    if not cleaned:
        return ""
    body = cleaned.split(".")[0]
    digits = "".join(ch for ch in body if ch.isdigit())
    if not digits:
        return ""
    return digits.zfill(6)[-6:]


async def _resolve_watchlist_stocks(codes: List[str]) -> List[dict]:
    if not codes:
        return []

    db = get_database()
    cursor = db.stocks.find({"code": {"$in": codes}})
    stock_by_code = {}
    async for stock in cursor:
        stock_by_code[str(stock.get("code", ""))] = db_service._convert_objectid_to_str(stock)

    return [stock_by_code[code] for code in codes if code in stock_by_code]


def _display_code(code: str) -> str:
    if code.startswith("6"):
        return f"{code}.SH"
    if code.startswith("8") or code.startswith("4"):
        return f"{code}.BJ"
    return f"{code}.SZ"


async def _compute_stock_market_snapshot(
    stock_code: str,
    window_hours: int,
    sample_limit: int,
) -> Dict[str, Any]:
    db = get_database()
    now = datetime.utcnow()
    start_date = now - timedelta(hours=window_hours)

    cursor = (
        db.events.find(
            {
                "announcement_date": {"$gte": start_date},
                "ai_analysis.affected_stocks.code": stock_code,
            }
        )
        .sort("announcement_date", -1)
        .limit(sample_limit)
    )

    cards: List[Dict[str, Any]] = []
    latest_event_at: Optional[datetime] = None
    async for event in cursor:
        cards.append(compute_event_scores(event, now))
        announcement_date = event.get("announcement_date")
        if isinstance(announcement_date, datetime):
            if latest_event_at is None or announcement_date > latest_event_at:
                latest_event_at = announcement_date

    if not cards:
        return {
            "market_index": None,
            "sample_size": 0,
            "latest_event_at": None,
        }

    return {
        "market_index": round(compute_market_index(cards), 2),
        "sample_size": len(cards),
        "latest_event_at": latest_event_at,
    }


@router.get("", response_model=List[dict])
async def get_stocks():
    """获取所有股票"""
    try:
        stocks = await db_service.get_all_stocks()
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stocks: {str(e)}")


@router.get("/watchlist", response_model=List[dict])
async def get_my_watchlist(current_user: UserResponse = Depends(get_current_user)):
    """Get current user's watchlist."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = get_database()
    user = await db.users.find_one({"email": current_user.email}, {"watchlist_codes": 1})
    watchlist_codes = user.get("watchlist_codes", []) if user else []
    return await _resolve_watchlist_stocks(watchlist_codes)


@router.post("/watchlist", response_model=List[dict])
async def add_stock_to_watchlist(
    payload: WatchlistPayload,
    current_user: UserResponse = Depends(get_current_user),
):
    """Add one stock code into current user's watchlist."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    normalized_code = _normalize_stock_code(payload.code)
    if not normalized_code:
        raise HTTPException(status_code=400, detail="Invalid stock code")

    stock = await db_service.get_stock_by_code(normalized_code)
    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found in stocks table")

    db = get_database()
    await db.users.update_one(
        {"email": current_user.email},
        {"$addToSet": {"watchlist_codes": normalized_code}, "$set": {"updated_at": datetime.utcnow()}},
    )

    user = await db.users.find_one({"email": current_user.email}, {"watchlist_codes": 1})
    watchlist_codes = user.get("watchlist_codes", []) if user else []
    return await _resolve_watchlist_stocks(watchlist_codes)


@router.delete("/watchlist/{code}", response_model=List[dict])
async def remove_stock_from_watchlist(code: str, current_user: UserResponse = Depends(get_current_user)):
    """Remove one stock code from current user's watchlist."""
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    normalized_code = _normalize_stock_code(code)
    if not normalized_code:
        raise HTTPException(status_code=400, detail="Invalid stock code")

    db = get_database()
    await db.users.update_one(
        {"email": current_user.email},
        {"$pull": {"watchlist_codes": normalized_code}, "$set": {"updated_at": datetime.utcnow()}},
    )

    user = await db.users.find_one({"email": current_user.email}, {"watchlist_codes": 1})
    watchlist_codes = user.get("watchlist_codes", []) if user else []
    return await _resolve_watchlist_stocks(watchlist_codes)


@router.get("/watchlist/alerts", response_model=dict)
async def get_watchlist_alerts(
    threshold: float = Query(30, ge=-100, le=100, description="Alert threshold for market index"),
    window_hours: int = Query(72, ge=1, le=720, description="Lookback window in hours"),
    sample_limit: int = Query(200, ge=20, le=2000, description="Max events sampled for each stock"),
    current_user: UserResponse = Depends(get_current_user),
):
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    db = get_database()
    user = await db.users.find_one({"email": current_user.email}, {"watchlist_codes": 1})
    watchlist_codes = user.get("watchlist_codes", []) if user else []
    watchlist_stocks = await _resolve_watchlist_stocks(watchlist_codes)

    now = datetime.utcnow()
    items: List[Dict[str, Any]] = []
    for stock in watchlist_stocks:
        code = str(stock.get("code", "")).strip()
        if not code:
            continue

        snapshot = await _compute_stock_market_snapshot(
            stock_code=code,
            window_hours=window_hours,
            sample_limit=sample_limit,
        )
        market_index = snapshot["market_index"]
        if market_index is None or market_index >= threshold:
            continue

        items.append(
            {
                "id": f"{code}:{snapshot['latest_event_at'].isoformat() if snapshot['latest_event_at'] else now.isoformat()}",
                "stock_name": stock.get("name") or code,
                "stock_code": code,
                "display_code": _display_code(code),
                "market_index": market_index,
                "threshold": threshold,
                "sample_size": snapshot["sample_size"],
                "latest_event_at": snapshot["latest_event_at"],
                "triggered_at": now,
                "tag": "市场先生预警",
                "level": "red" if market_index < 0 else "yellow",
            }
        )

    items.sort(key=lambda item: item["market_index"])

    return {
        "threshold": threshold,
        "window_hours": window_hours,
        "watchlist_size": len(watchlist_stocks),
        "triggered_count": len(items),
        "items": items,
        "updated_at": now,
    }


@router.get("/{code}", response_model=dict)
async def get_stock(code: str):
    """根据代码获取单个股票"""
    stock = await db_service.get_stock_by_code(code)

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    return stock


@router.post("", response_model=dict, status_code=201)
async def create_stock(stock_data: StockCreate):
    """创建新股票"""
    try:
        stock_id = await db_service.create_or_update_stock(
            name=stock_data.name,
            code=stock_data.code,
            status=stock_data.status,
            industry=stock_data.industry,
        )
        return await db_service.get_stock_by_code(stock_data.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create stock: {str(e)}")


@router.put("/{code}", response_model=dict)
async def update_stock(code: str, stock_data: StockUpdate):
    """更新股票"""
    stock = await db_service.get_stock_by_code(code)

    if not stock:
        raise HTTPException(status_code=404, detail="Stock not found")

    try:
        update_dict = stock_data.model_dump(exclude_unset=True)
        stock_id = await db_service.create_or_update_stock(
            name=update_dict.get("name", stock["name"]),
            code=code,
            **update_dict,
        )
        return await db_service.get_stock_by_code(code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update stock: {str(e)}")

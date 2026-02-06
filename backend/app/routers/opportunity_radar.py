from datetime import datetime, timedelta
from typing import Any, Dict, Literal

from fastapi import APIRouter, HTTPException, Query

from app.services.database_service import db_service
from app.services.radar_scoring import compute_event_scores, compute_market_index

router = APIRouter(prefix="/api/opportunity-radar", tags=["opportunity-radar"])


def _build_event_card(event: Dict[str, Any], now: datetime) -> Dict[str, Any]:
    ai = event.get("ai_analysis") or {}
    sectors = ai.get("affected_sectors") or []
    stocks = ai.get("affected_stocks") or []
    scores = compute_event_scores(event, now)
    return {
        "id": event.get("id"),
        "title": event.get("title"),
        "content": event.get("content"),
        "event_category": event.get("event_category"),
        "event_types": event.get("event_types") or [],
        "announcement_date": event.get("announcement_date"),
        "source": event.get("source"),
        "original_url": event.get("original_url"),
        "impact_reason": ai.get("impact_reason"),
        "is_hype": bool(ai.get("is_hype", False)),
        "affected_sector_codes": [item.get("code") for item in sectors if item.get("code")],
        "affected_stock_codes": [item.get("code") for item in stocks if item.get("code")],
        **scores,
    }


@router.get("/overview")
async def get_opportunity_radar_overview(
    window_hours: int = Query(72, ge=1, le=720, description="统计窗口（小时）"),
    sample_limit: int = Query(500, ge=20, le=2000, description="读取样本上限"),
):
    try:
        now = datetime.utcnow()
        start_date = now - timedelta(hours=window_hours)
        events, _ = await db_service.get_events(skip=0, limit=sample_limit, start_date=start_date)
        cards = [_build_event_card(item, now) for item in events]

        if not cards:
            return {
                "window_hours": window_hours,
                "sample_size": 0,
                "market_index": 0.0,
                "avg_confidence": 0.0,
                "opportunity_count": 0,
                "risk_count": 0,
                "neutral_count": 0,
                "calculation_logic": {
                    "market_index": "avg(sentiment_score * (0.5 + confidence_score/200))",
                    "direction_rule": "sentiment>=20 => opportunity; sentiment<=-20 => risk; else neutral",
                },
                "updated_at": now,
            }

        market_index = compute_market_index(cards)
        opportunity_count = sum(1 for card in cards if card["direction"] == "opportunity")
        risk_count = sum(1 for card in cards if card["direction"] == "risk")
        neutral_count = len(cards) - opportunity_count - risk_count
        avg_confidence = sum(card["confidence_score"] for card in cards) / len(cards)

        return {
            "window_hours": window_hours,
            "sample_size": len(cards),
            "market_index": round(market_index, 2),
            "avg_confidence": round(avg_confidence, 2),
            "opportunity_count": opportunity_count,
            "risk_count": risk_count,
            "neutral_count": neutral_count,
            "calculation_logic": {
                "market_index": "avg(sentiment_score * (0.5 + confidence_score/200))",
                "direction_rule": "sentiment>=20 => opportunity; sentiment<=-20 => risk; else neutral",
                "relevance_score": "impact*0.45 + abs(sentiment)*0.30 + confidence*0.15 + freshness*0.10",
            },
            "updated_at": now,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch opportunity radar overview: {exc}")


@router.get("/signals")
async def get_opportunity_radar_signals(
    signal_type: Literal["opportunity", "risk"] = Query(
        "opportunity", description="信号类型：opportunity 或 risk"
    ),
    window_hours: int = Query(72, ge=1, le=720, description="统计窗口（小时）"),
    limit: int = Query(10, ge=1, le=100, description="返回数量"),
    sample_limit: int = Query(500, ge=20, le=2000, description="读取样本上限"),
):
    try:
        now = datetime.utcnow()
        start_date = now - timedelta(hours=window_hours)
        events, _ = await db_service.get_events(skip=0, limit=sample_limit, start_date=start_date)
        cards = [_build_event_card(item, now) for item in events]

        filtered = [item for item in cards if item["direction"] == signal_type]
        filtered.sort(
            key=lambda item: (abs(item["sentiment_score"]), item["relevance_score"]),
            reverse=True,
        )

        return {
            "signal_type": signal_type,
            "window_hours": window_hours,
            "total": len(filtered),
            "items": filtered[:limit],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch opportunity radar signals: {exc}")


@router.get("/top-events")
async def get_opportunity_radar_top_events(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    lookback_days: int = Query(30, ge=1, le=365, description="回溯天数"),
    min_relevance: float = Query(0, ge=0, le=100, description="最小相关度"),
    sample_limit: int = Query(1000, ge=20, le=5000, description="读取样本上限"),
):
    try:
        now = datetime.utcnow()
        start_date = now - timedelta(days=lookback_days)
        events, _ = await db_service.get_events(skip=0, limit=sample_limit, start_date=start_date)
        cards = [_build_event_card(item, now) for item in events]

        filtered = [item for item in cards if item["relevance_score"] >= min_relevance]
        filtered.sort(key=lambda item: item["relevance_score"], reverse=True)

        return {
            "lookback_days": lookback_days,
            "min_relevance": min_relevance,
            "total": len(filtered),
            "items": filtered[:limit],
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to fetch opportunity radar top events: {exc}")

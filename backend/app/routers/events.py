from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query

from app.models import EventCreate, EventResponse, EventUpdate, PaginatedResponse
from app.services.ai_service import get_ai_service
from app.services.database_service import db_service

router = APIRouter(prefix="/api/events", tags=["events"])


async def _persist_related_entities(ai_analysis) -> None:
    if ai_analysis.affected_sectors:
        for sector in ai_analysis.affected_sectors:
            await db_service.create_or_update_sector(
                name=sector.name,
                code=sector.code or f"SECTOR_{sector.name}",
            )
    if ai_analysis.affected_stocks:
        for stock in ai_analysis.affected_stocks:
            await db_service.create_or_update_stock(
                name=stock.name,
                code=stock.code or f"STOCK_{stock.name}",
            )


@router.get("", response_model=PaginatedResponse[EventResponse])
async def get_events(
    skip: int = Query(0, ge=0, description="Records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Records to return"),
    category: Optional[str] = Query(None, description="Filter by event category"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    search: Optional[str] = Query(None, description="Search title/content"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    min_impact: Optional[float] = Query(None, description="Min impact score"),
    max_impact: Optional[float] = Query(None, description="Max impact score"),
):
    start_dt = None
    end_dt = None
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid start_date format. Use YYYY-MM-DD")
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid end_date format. Use YYYY-MM-DD")

    events, total = await db_service.get_events(
        skip=skip,
        limit=limit,
        category=category,
        event_type=event_type,
        search=search,
        start_date=start_dt,
        end_date=end_dt,
        min_impact=min_impact,
        max_impact=max_impact,
    )
    return PaginatedResponse(items=events, total=total)


@router.get("/{event_id}", response_model=dict)
async def get_event(event_id: str):
    event = await db_service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("", response_model=dict, status_code=201)
async def create_event(event_data: EventCreate):
    try:
        event_id = await db_service.create_event(event_data)
        return await db_service.get_event_by_id(event_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {exc}")


@router.put("/{event_id}", response_model=dict)
async def update_event(event_id: str, event_data: EventUpdate):
    event = await db_service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    try:
        return await db_service.update_event(event_id, event_data)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {exc}")


@router.delete("/{event_id}")
async def delete_event(event_id: str):
    event = await db_service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    success = await db_service.delete_event(event_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete event")
    return {"message": "Event deleted successfully"}


@router.post("/{event_id}/analyze", response_model=dict)
async def analyze_event(event_id: str):
    event = await db_service.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    ai_service = get_ai_service()
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI service not configured: set ZHIPU_API_KEY")

    try:
        result = await ai_service.analyze_and_classify(
            event_title=event["title"],
            event_content=event["content"],
            needs_classification=True,
        )
        ai_analysis = result["ai_analysis"]
        updated_event = await db_service.update_event(
            event_id,
            EventUpdate(
                ai_analysis=ai_analysis,
                event_category=result.get("event_category"),
                event_types=result.get("event_types"),
            ),
        )
        await _persist_related_entities(ai_analysis)
        return updated_event
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to analyze event: {exc}")


@router.post("/analyze/batch", response_model=dict)
async def analyze_events_batch(
    limit: int = Query(100, ge=1, le=1000, description="Max events to scan"),
    days: Optional[int] = Query(None, ge=1, le=365, description="Only events in latest N days"),
    force: bool = Query(False, description="Reanalyze events that already have ai_analysis"),
):
    ai_service = get_ai_service()
    if not ai_service:
        raise HTTPException(status_code=503, detail="AI service not configured: set ZHIPU_API_KEY")

    start_date = datetime.utcnow() - timedelta(days=days) if days else None
    events, _ = await db_service.get_events(skip=0, limit=limit, start_date=start_date)
    candidates = events if force else [item for item in events if not item.get("ai_analysis")]

    analyzed = 0
    failed = 0
    for event in candidates:
        try:
            result = await ai_service.analyze_and_classify(
                event_title=event["title"],
                event_content=event["content"],
                needs_classification=True,
            )
            ai_analysis = result["ai_analysis"]
            await db_service.update_event(
                event["id"],
                EventUpdate(
                    ai_analysis=ai_analysis,
                    event_category=result.get("event_category"),
                    event_types=result.get("event_types"),
                ),
            )
            await _persist_related_entities(ai_analysis)
            analyzed += 1
        except Exception:
            failed += 1

    return {
        "scanned": len(events),
        "candidates": len(candidates),
        "analyzed": analyzed,
        "failed": failed,
    }


@router.get("/sector/{sector_code}", response_model=List[dict])
async def get_events_by_sector(
    sector_code: str,
    limit: int = Query(50, ge=1, le=100, description="Records to return"),
):
    return await db_service.get_events_by_sector(sector_code, limit=limit)


@router.get("/stock/{stock_code}", response_model=List[dict])
async def get_events_by_stock(
    stock_code: str,
    limit: int = Query(50, ge=1, le=100, description="Records to return"),
):
    return await db_service.get_events_by_stock(stock_code, limit=limit)

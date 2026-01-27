from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from app.models import EventCreate, EventUpdate, EventResponse, EventCategory, EventType
from app.services.database_service import db_service
from app.services.ai_service import get_ai_service

router = APIRouter(prefix="/api/events", tags=["events"])


@router.get("", response_model=List[EventResponse])
async def get_events(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(20, ge=1, le=100, description="返回的记录数"),
    category: Optional[str] = Query(None, description="事件类别筛选"),
    event_type: Optional[str] = Query(None, description="事件类型筛选"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
):
    """
    获取事件列表

    支持分页、筛选和搜索
    """
    # 解析日期
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

    # 获取事件
    events, total = await db_service.get_events(
        skip=skip,
        limit=limit,
        category=category,
        event_type=event_type,
        search=search,
        start_date=start_dt,
        end_date=end_dt,
    )

    return events


@router.get("/{event_id}", response_model=dict)
async def get_event(event_id: str):
    """获取单个事件详情"""
    event = await db_service.get_event_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    return event


@router.post("", response_model=dict, status_code=201)
async def create_event(event_data: EventCreate):
    """创建新事件"""
    try:
        event_id = await db_service.create_event(event_data)
        return await db_service.get_event_by_id(event_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


@router.put("/{event_id}", response_model=dict)
async def update_event(event_id: str, event_data: EventUpdate):
    """更新事件"""
    event = await db_service.get_event_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    try:
        updated_event = await db_service.update_event(event_id, event_data)
        return updated_event
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")


@router.delete("/{event_id}")
async def delete_event(event_id: str):
    """删除事件"""
    event = await db_service.get_event_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    success = await db_service.delete_event(event_id)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete event")

    return {"message": "Event deleted successfully"}


@router.post("/{event_id}/analyze", response_model=dict)
async def analyze_event(event_id: str):
    """
    对事件进行 AI 分析

    包括：
    - 提取影响的板块、股票、原材料
    - 对影响进行打分（0-10分）
    - 给出打分理由
    """
    event = await db_service.get_event_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    ai_service = get_ai_service()
    if not ai_service:
        raise HTTPException(
            status_code=503, detail="AI service is not configured. Please set ZHIPU_API_KEY in .env"
        )

    try:
        # 执行 AI 分析
        ai_analysis = await ai_service.analyze_event(
            event_title=event["title"],
            event_content=event["content"],
        )

        # 更新事件的 AI 分析结果
        event_update = EventUpdate(ai_analysis=ai_analysis)
        updated_event = await db_service.update_event(event_id, event_update)

        # 更新关联的板块和股票
        if ai_analysis.affected_sectors:
            for sector in ai_analysis.affected_sectors:
                await db_service.create_or_update_sector(
                    name=sector.name,
                    code=sector.code if sector.code else f"SECTOR_{sector.name}",
                )

        if ai_analysis.affected_stocks:
            for stock in ai_analysis.affected_stocks:
                await db_service.create_or_update_stock(
                    name=stock.name,
                    code=stock.code if stock.code else f"STOCK_{stock.name}",
                )

        return updated_event

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze event: {str(e)}")


@router.get("/sector/{sector_code}", response_model=List[dict])
async def get_events_by_sector(
    sector_code: str,
    limit: int = Query(50, ge=1, le=100, description="返回的记录数"),
):
    """获取影响指定板块的事件"""
    events = await db_service.get_events_by_sector(sector_code, limit=limit)
    return events


@router.get("/stock/{stock_code}", response_model=List[dict])
async def get_events_by_stock(
    stock_code: str,
    limit: int = Query(50, ge=1, le=100, description="返回的记录数"),
):
    """获取影响指定股票的事件"""
    events = await db_service.get_events_by_stock(stock_code, limit=limit)
    return events

from fastapi import APIRouter, HTTPException
from typing import List
from app.models import SectorCreate, SectorUpdate, SectorResponse
from app.services.database_service import db_service

router = APIRouter(prefix="/api/sectors", tags=["sectors"])


@router.get("", response_model=List[dict])
async def get_sectors():
    """获取所有板块"""
    try:
        sectors = await db_service.get_all_sectors()
        return sectors
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch sectors: {str(e)}")


@router.get("/{code}", response_model=dict)
async def get_sector(code: str):
    """根据代码获取单个板块"""
    sector = await db_service.get_sector_by_code(code)

    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")

    return sector


@router.post("", response_model=dict, status_code=201)
async def create_sector(sector_data: SectorCreate):
    """创建新板块"""
    try:
        sector_id = await db_service.create_or_update_sector(
            name=sector_data.name,
            code=sector_data.code,
            risk_level=sector_data.risk_level,
            description=sector_data.description,
        )
        return await db_service.get_sector_by_code(sector_data.code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sector: {str(e)}")


@router.put("/{code}", response_model=dict)
async def update_sector(code: str, sector_data: SectorUpdate):
    """更新板块"""
    sector = await db_service.get_sector_by_code(code)

    if not sector:
        raise HTTPException(status_code=404, detail="Sector not found")

    try:
        update_dict = sector_data.model_dump(exclude_unset=True)
        sector_id = await db_service.create_or_update_sector(
            name=update_dict.get("name", sector["name"]),
            code=code,
            **update_dict,
        )
        return await db_service.get_sector_by_code(code)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update sector: {str(e)}")

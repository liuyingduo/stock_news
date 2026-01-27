from fastapi import APIRouter, HTTPException
from typing import List
from app.models import StockCreate, StockUpdate, StockResponse
from app.services.database_service import db_service

router = APIRouter(prefix="/api/stocks", tags=["stocks"])


@router.get("", response_model=List[dict])
async def get_stocks():
    """获取所有股票"""
    try:
        stocks = await db_service.get_all_stocks()
        return stocks
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stocks: {str(e)}")


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

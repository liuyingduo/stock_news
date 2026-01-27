from fastapi import APIRouter, HTTPException
from app.services.database_service import db_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
async def get_dashboard_stats():
    """
    获取仪表板统计数据

    包括：
    - 总事件数
    - 总板块数
    - 总股票数
    - 最近 7 天事件数
    - 按类别统计的事件数
    """
    try:
        stats = await db_service.get_dashboard_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard stats: {str(e)}")


@router.get("/summary")
async def get_dashboard_summary():
    """
    获取仪表板摘要信息

    返回更详细的统计数据和趋势
    """
    try:
        stats = await db_service.get_dashboard_stats()

        # 添加更多信息
        summary = {
            **stats,
            "message": "Dashboard data retrieved successfully",
        }

        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch dashboard summary: {str(e)}")

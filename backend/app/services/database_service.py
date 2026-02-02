from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from app.core.database import get_database
from app.models import Event, EventCreate, EventUpdate, EventResponse


class DatabaseService:
    """数据库服务"""

    def __init__(self):
        """初始化数据库服务"""
        pass

    def _get_db(self) -> AsyncIOMotorDatabase:
        """获取数据库实例（延迟加载）"""
        return get_database()

    def _convert_objectid_to_str(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """将 ObjectId 转换为字符串"""
        if "_id" in data:
            data["id"] = str(data.pop("_id"))
        return data

    async def create_indexes(self):
        """创建索引"""
        # 事件集合索引
        await self._get_db().events.create_index("announcement_date")
        await self._get_db().events.create_index("event_category")
        await self._get_db().events.create_index("event_types")
        await self._get_db().events.create_index("ai_analysis.affected_sectors.code")
        await self._get_db().events.create_index("ai_analysis.affected_stocks.code")
        await self._get_db().events.create_index([("announcement_date", -1)])

        # 板块集合索引
        await self._get_db().sectors.create_index("code", unique=True)
        await self._get_db().sectors.create_index("name")

        # 股票集合索引
        await self._get_db().stocks.create_index("code", unique=True)
        await self._get_db().stocks.create_index("name")

        print("Database indexes created successfully")

    # ===== 事件相关操作 =====

    async def create_event(self, event_data: EventCreate) -> str:
        """创建事件"""
        event_dict = event_data.model_dump()
        event_dict["created_at"] = datetime.utcnow()
        event_dict["updated_at"] = datetime.utcnow()

        result = await self._get_db().events.insert_one(event_dict)
        return str(result.inserted_id)

    async def create_events_bulk(self, events_data: List[EventCreate]) -> int:
        """
        批量创建事件

        Args:
            events_data: 事件数据列表

        Returns:
            成功插入的数量
        """
        if not events_data:
            return 0

        now = datetime.utcnow()
        events_dict = []
        for event_data in events_data:
            event_dict = event_data.model_dump()
            event_dict["created_at"] = now
            event_dict["updated_at"] = now
            events_dict.append(event_dict)

        try:
            result = await self._get_db().events.insert_many(events_dict, ordered=False)
            return len(result.inserted_ids)
        except Exception as e:
            # 如果遇到重复键错误，部分数据可能已插入
            # 返回已插入的数量
            if "bulk write error" in str(e).lower():
                return len(events_dict) - 1  # 估算，实际可能需要更精确的处理
            return 0

    async def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """根据 ID 获取事件"""
        try:
            obj_id = ObjectId(event_id)
            event = await self._get_db().events.find_one({"_id": obj_id})
            if event:
                return self._convert_objectid_to_str(event)
            return None
        except Exception:
            return None

    async def get_event_by_title_date(self, title: str, date: datetime, stock_code: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        根据标题和日期获取事件（用于去重）
        支持忽略具体时间（按天查询）和股票代码匹配
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        query = {
            "title": title,
            "announcement_date": {"$gte": start_of_day, "$lte": end_of_day}
        }
        
        if stock_code:
            query["stock_code"] = stock_code
            
        event = await self._get_db().events.find_one(query)
        
        if event:
            return self._convert_objectid_to_str(event)
        return None

    async def get_events(
        self,
        skip: int = 0,
        limit: int = 20,
        category: Optional[str] = None,
        event_type: Optional[str] = None,
        search: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        获取事件列表
        返回 (事件列表, 总数)
        """
        # 构建查询条件
        query = {}

        if category:
            query["event_category"] = category

        if event_type:
            query["event_types"] = event_type

        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["announcement_date"] = date_query

        if search:
            query["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"content": {"$regex": search, "$options": "i"}},
            ]

        # 获取总数
        total = await self._get_db().events.count_documents(query)

        # 获取数据
        cursor = (
            self._get_db().events.find(query)
            .sort("announcement_date", -1)
            .skip(skip)
            .limit(limit)
        )

        events = []
        async for event in cursor:
            events.append(self._convert_objectid_to_str(event))

        return events, total

    async def update_event(
        self, event_id: str, event_data: EventUpdate
    ) -> Optional[Dict[str, Any]]:
        """更新事件"""
        try:
            obj_id = ObjectId(event_id)
            update_dict = {
                k: v for k, v in event_data.model_dump(exclude_unset=True).items() if v is not None
            }
            update_dict["updated_at"] = datetime.utcnow()

            await self._get_db().events.update_one({"_id": obj_id}, {"$set": update_dict})

            return await self.get_event_by_id(event_id)
        except Exception as e:
            print(f"Error updating event: {str(e)}")
            return None

    async def delete_event(self, event_id: str) -> bool:
        """删除事件"""
        try:
            obj_id = ObjectId(event_id)
            result = await self._get_db().events.delete_one({"_id": obj_id})
            return result.deleted_count > 0
        except Exception:
            return False

    async def delete_all_events(self) -> int:
        """删除所有事件"""
        try:
            result = await self._get_db().events.delete_many({})
            return result.deleted_count
        except Exception as e:
            print(f"Error deleting all events: {str(e)}")
            return 0

    async def get_events_by_sector(self, sector_code: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取影响指定板块的事件"""
        query = {"ai_analysis.affected_sectors.code": sector_code}
        cursor = (
            self._get_db().events.find(query)
            .sort("announcement_date", -1)
            .limit(limit)
        )

        events = []
        async for event in cursor:
            events.append(self._convert_objectid_to_str(event))

        return events

    async def get_events_by_stock(self, stock_code: str, limit: int = 50) -> List[Dict[str, Any]]:
        """获取影响指定股票的事件"""
        query = {"ai_analysis.affected_stocks.code": stock_code}
        cursor = (
            self._get_db().events.find(query)
            .sort("announcement_date", -1)
            .limit(limit)
        )

        events = []
        async for event in cursor:
            events.append(self._convert_objectid_to_str(event))

        return events

    # ===== 板块相关操作 =====

    async def create_or_update_sector(self, name: str, code: str, **kwargs) -> str:
        """创建或更新板块"""
        existing = await self._get_db().sectors.find_one({"code": code})

        if existing:
            # 更新
            update_dict = {"name": name, **kwargs, "updated_at": datetime.utcnow()}
            await self._get_db().sectors.update_one({"code": code}, {"$set": update_dict})
            return str(existing["_id"])
        else:
            # 创建
            sector_dict = {
                "name": name,
                "code": code,
                **kwargs,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            result = await self._get_db().sectors.insert_one(sector_dict)
            return str(result.inserted_id)

    async def get_all_sectors(self) -> List[Dict[str, Any]]:
        """获取所有板块"""
        cursor = self._get_db().sectors.find()
        sectors = []
        async for sector in cursor:
            sectors.append(self._convert_objectid_to_str(sector))
        return sectors

    async def get_sector_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """根据代码获取板块"""
        sector = await self._get_db().sectors.find_one({"code": code})
        if sector:
            return self._convert_objectid_to_str(sector)
        return None

    # ===== 股票相关操作 =====

    async def create_or_update_stock(self, name: str, code: str, **kwargs) -> str:
        """创建或更新股票"""
        existing = await self._get_db().stocks.find_one({"code": code})

        if existing:
            # 更新
            update_dict = {"name": name, **kwargs, "updated_at": datetime.utcnow()}
            await self._get_db().stocks.update_one({"code": code}, {"$set": update_dict})
            return str(existing["_id"])
        else:
            # 创建
            stock_dict = {
                "name": name,
                "code": code,
                **kwargs,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            result = await self._get_db().stocks.insert_one(stock_dict)
            return str(result.inserted_id)

    async def get_all_stocks(self) -> List[Dict[str, Any]]:
        """获取所有股票"""
        cursor = self._get_db().stocks.find()
        stocks = []
        async for stock in cursor:
            stocks.append(self._convert_objectid_to_str(stock))
        return stocks

    async def get_stock_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """根据代码获取股票"""
        stock = await self._get_db().stocks.find_one({"code": code})
        if stock:
            return self._convert_objectid_to_str(stock)
        return None

    # ===== 统计相关操作 =====

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """获取仪表板统计数据"""
        total_events = await self._get_db().events.count_documents({})
        total_sectors = await self._get_db().sectors.count_documents({})
        total_stocks = await self._get_db().stocks.count_documents({})

        # 获取最近 7 天的事件数量
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_events = await self._get_db().events.count_documents({
            "announcement_date": {"$gte": seven_days_ago}
        })

        # 按类别统计事件
        pipeline = [
            {"$group": {"_id": "$event_category", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
        ]
        category_stats = []
        async for doc in self._get_db().events.aggregate(pipeline):
            category_stats.append({"category": doc["_id"], "count": doc["count"]})

        return {
            "total_events": total_events,
            "total_sectors": total_sectors,
            "total_stocks": total_stocks,
            "recent_events_7days": recent_events,
            "category_stats": category_stats,
        }


# 全局数据库服务实例
db_service = DatabaseService()

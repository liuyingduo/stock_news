from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class StockStatus(str, Enum):
    """股票状态"""
    NORMAL = "normal"  # 正常
    ST = "st"  # ST
    SUSPENDED = "suspended"  # 停牌


class Stock(BaseModel):
    """股票模型"""
    id: Optional[str] = Field(None, description="MongoDB _id")
    name: str = Field(..., description="股票名称")
    code: str = Field(..., description="股票代码")
    status: StockStatus = Field(default=StockStatus.NORMAL, description="股票状态")
    industry: Optional[str] = Field(None, description="所属行业")
    related_event_ids: List[str] = Field(default_factory=list, description="关联事件ID列表")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


class StockCreate(BaseModel):
    """创建股票的请求模型"""
    name: str
    code: str
    status: StockStatus = StockStatus.NORMAL
    industry: Optional[str] = None


class StockUpdate(BaseModel):
    """更新股票的请求模型"""
    name: Optional[str] = None
    code: Optional[str] = None
    status: Optional[StockStatus] = None
    industry: Optional[str] = None
    related_event_ids: Optional[List[str]] = None


class StockResponse(BaseModel):
    """股票响应模型"""
    id: str
    name: str
    code: str
    status: str
    industry: Optional[str]
    related_event_ids: List[str]
    created_at: datetime
    updated_at: datetime

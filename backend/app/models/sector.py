from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class RiskLevel(str, Enum):
    """风险等级"""
    HIGH_POSITIVE = "high_positive"  # 高度利好
    POSITIVE = "positive"  # 利好
    NEUTRAL = "neutral"  # 中性
    NEGATIVE = "negative"  # 利空
    HIGH_NEGATIVE = "high_negative"  # 高度利空


class Sector(BaseModel):
    """板块模型"""
    id: Optional[str] = Field(None, description="MongoDB _id")
    name: str = Field(..., description="板块名称")
    code: str = Field(..., description="板块代码")
    risk_level: RiskLevel = Field(default=RiskLevel.NEUTRAL, description="风险等级")
    description: Optional[str] = Field(None, description="板块描述")
    related_event_ids: List[str] = Field(default_factory=list, description="关联事件ID列表")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")


class SectorCreate(BaseModel):
    """创建板块的请求模型"""
    name: str
    code: str
    risk_level: RiskLevel = RiskLevel.NEUTRAL
    description: Optional[str] = None


class SectorUpdate(BaseModel):
    """更新板块的请求模型"""
    name: Optional[str] = None
    code: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    description: Optional[str] = None
    related_event_ids: Optional[List[str]] = None


class SectorResponse(BaseModel):
    """板块响应模型"""
    id: str
    name: str
    code: str
    risk_level: str
    description: Optional[str]
    related_event_ids: List[str]
    created_at: datetime
    updated_at: datetime

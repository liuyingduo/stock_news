from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EventCategory(str, Enum):
    """事件大类"""
    GLOBAL_EVENTS = "global_events"       # 全球大事
    POLICY_TRENDS = "policy_trends"       # 政策风向
    INDUSTRY_TRENDS = "industry_trends"   # 行业动向
    COMPANY_UPDATES = "company_updates"   # 公司动态


class EventType(str, Enum):
    """具体事件类型"""
    # 全球大事
    MACRO_GEOPOLITICS = "macro_geopolitics"  # 宏观地缘

    # 政策风向
    REGULATORY_POLICY = "regulatory_policy"  # 监管政策
    MARKET_SENTIMENT = "market_sentiment"    # 市场情绪

    # 行业动向
    INDUSTRIAL_CHAIN = "industrial_chain"    # 产业链驱动
    CORE_SECTOR = "core_sector"              # 核心板块

    # 公司动态
    MAJOR_EVENT = "major_event"                        # 重大事项
    FINANCIAL_REPORT = "financial_report"              # 财务报告
    FINANCING_ANNOUNCEMENT = "financing_announcement"  # 融资公告
    RISK_WARNING = "risk_warning"                      # 风险提示
    ASSET_RESTRUCTURING = "asset_restructuring"        # 资产重组
    INFO_CHANGE = "info_change"                        # 信息变更
    SHAREHOLDING_CHANGE = "shareholding_change"        # 持股变动

    OTHER = "other"  # 其他


class AffectedStock(BaseModel):
    """影响的股票"""
    name: str = Field(..., description="股票名称")
    code: Optional[str] = Field(None, description="股票代码")


class AffectedSector(BaseModel):
    """影响的板块"""
    name: str = Field(..., description="板块名称")
    code: Optional[str] = Field(None, description="板块代码")


class AffectedMaterial(BaseModel):
    """影响的原材料"""
    name: str = Field(..., description="原材料名称")


class AIAnalysis(BaseModel):
    """AI 分析结果"""
    impact_score: Optional[float] = Field(None, ge=0, le=10, description="影响打分 0-10")
    impact_reason: Optional[str] = Field(None, description="打分理由")
    affected_sectors: List[AffectedSector] = Field(default_factory=list, description="影响的板块列表")
    affected_stocks: List[AffectedStock] = Field(default_factory=list, description="影响的股票列表")
    affected_materials: List[AffectedMaterial] = Field(default_factory=list, description="影响的原材料列表")
    analyzed_at: Optional[datetime] = Field(None, description="分析时间")


class Event(BaseModel):
    """事件模型"""
    id: Optional[str] = Field(None, description="MongoDB _id")
    title: str = Field(..., description="事件标题")
    content: str = Field(..., description="事件内容")
    event_category: EventCategory = Field(..., description="事件大类")
    event_type: EventType = Field(..., description="事件类型")
    announcement_date: datetime = Field(..., description="公告日期")
    expected_date: Optional[datetime] = Field(None, description="预期发生日期")
    source: Optional[str] = Field(None, description="数据来源")
    original_url: Optional[str] = Field(None, description="原始链接")

    # AI 分析数据
    ai_analysis: Optional[AIAnalysis] = Field(None, description="AI 分析结果")

    # 元数据
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class EventCreate(BaseModel):
    """创建事件的请求模型"""
    title: str
    content: str
    event_category: EventCategory
    event_type: EventType
    announcement_date: datetime
    expected_date: Optional[datetime] = None
    source: Optional[str] = None
    original_url: Optional[str] = None


class EventUpdate(BaseModel):
    """更新事件的请求模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    event_category: Optional[EventCategory] = None
    event_type: Optional[EventType] = None
    announcement_date: Optional[datetime] = None
    expected_date: Optional[datetime] = None
    source: Optional[str] = None
    original_url: Optional[str] = None
    ai_analysis: Optional[AIAnalysis] = None


class EventResponse(BaseModel):
    """事件响应模型"""
    id: str
    title: str
    content: str
    event_category: str
    event_type: str
    announcement_date: datetime
    expected_date: Optional[datetime] = None
    source: Optional[str] = None
    original_url: Optional[str] = None
    ai_analysis: Optional[AIAnalysis] = None
    created_at: datetime
    updated_at: datetime

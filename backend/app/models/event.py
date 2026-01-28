from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EventCategory(str, Enum):
    """事件大类"""
    CORE_DRIVER = "core_driver"  # 核心驱动板块
    SPECIAL_SITUATION = "special_situation"  # 特殊机遇板块
    INDUSTRIAL_CHAIN = "industrial_chain"  # 产业链与微观驱动
    SENTIMENT_FLOWS = "sentiment_flows"  # 市场情绪与资金流
    MACRO_GEOPOLITICS = "macro_geopolitics"  # 宏观叙事与地缘政治


class EventType(str, Enum):
    """具体事件类型（从接口获取）"""
    REGULATORY_POLICY = "regulatory_policy"  # 监管政策
    INDUSTRY_POLICY = "industry_policy"  # 产业政策
    REGULATORY_PENALTY = "regulatory_penalty"  # 监管处罚
    APPROVAL = "approval"  # 准入与审批
    EARNINGS_PREVIEW = "earnings_preview"  # 业绩预告
    DIVIDEND = "dividend"  # 分红送转
    REFINANCING = "refinancing"  # 再融资
    MA = "ma"  # 并购重组
    RESTRUCTURING = "restructuring"  # 破产重整
    MANAGEMENT_CHANGE = "management_change"  # 管理层异动
    SPINOFF = "spinoff"  # 拆分剥离
    PRICE_CHANGE = "price_change"  # 价格传导
    CAPACITY_CHANGE = "capacity_change"  # 产能变化
    SUPPLY_DEMAND = "supply_demand"  # 供需缺口
    ABNORMAL_MOVEMENT = "abnormal_movement"  # 异常异动
    PUBLIC_SENTIMENT = "public_sentiment"  # 舆情热度
    INDEX_CHANGE = "index_change"  # 指数成分股变动
    MONETARY_POLICY = "monetary_policy"  # 货币政策
    GEOPOLITICAL_RISK = "geopolitical_risk"  # 地缘风险
    MACRO_INDICATORS = "macro_indicators"  # 宏观指标
    LITIGATION = "litigation"  # 诉讼仲裁
    SHAREHOLDER_CHANGE = "shareholder_change"  # 股权转让
    REPURCHASE = "repurchase"  # 回购
    ANNUAL_REPORT = "annual_report"  # 年度报告
    OTHER = "other"  # 其他


class AffectedStock(BaseModel):
    """影响的股票"""
    name: str = Field(..., description="股票名称")
    code: str = Field(..., description="股票代码")


class AffectedSector(BaseModel):
    """影响的板块"""
    name: str = Field(..., description="板块名称")
    code: str = Field(..., description="板块代码")


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

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class EventCategory(str, Enum):
    """事件大类"""
    GLOBAL_MACRO = "global_macro"     # 全球宏观/地缘
    POLICY_REGULATION = "policy"      # 政策监管
    INDUSTRY_SECTOR = "industry"      # 行业/板块
    COMPANY_SPECIFIC = "company"      # 个股动态


class EventType(str, Enum):
    """具体事件类型"""
    # --- 全球与宏观 ---
    MACRO_ECON = "macro_econ"             # 利率/CPI/就业/美联储
    GEOPOLITICS = "geopolitics"           # 战争/制裁/外交/地区局势
    
    # --- 政策与情绪 ---
    REGULATORY_ACTION = "regulatory"      # 证监会新规/指导意见/行政处罚
    MARKET_LIQUIDITY = "liquidity"        # 降准降息/逆回购/资金流向
    MARKET_SENTIMENT = "sentiment"        # 指数异动/破位/情绪面总结
    
    # --- 行业动向 ---
    TECH_INNOVATION = "tech_innov"    # 颠覆性技术/量产进展/实验室突破
    SUPPLY_CHAIN = "supply_chain"     # 产能/供应链变动
    PRICE_VOLATILITY = "price_vol"    # 产品/原材料调价

    # --- 公司动态 (COMPANY_SPECIFIC) ---
    # 1. 业绩与业务 
    FINANCIAL_PERFORMANCE = "fin_perf"     # 业绩预增/扭亏/快报/年报
    ORDER_CONTRACT = "order_contract"      # 重大合同/中标/战略框架协议
    
    # 2. 资本运作
    M_A_RESTRUCTURING = "merger_re"        # 并购重组/吸收合并/分拆上市
    CAPITAL_ACTION = "capital_action"      # 定增/配股/可转债/再融资
    
    # 3. 治理与股东行为
    SHARE_BUYBACK = "buyback"              # 股份回购/注销/业绩补偿回购
    HOLDER_CHANGE = "holder_change"        # 大股东减持/质押/冻结/被动平仓
    INSIDER_TRANSACTION = "insider_trans"  # 高管增持/员工持股计划/股权激励
    
    # 4. 风险与负面
    RISK_CRISIS = "risk_crisis"            # 立案调查/退市风险/财务造假/财务疑点
    LITIGATION_ARBITRATION = "litigation"  # 重大诉讼/仲裁/资产冻结
    
    # 5. 常规与变更
    INFO_CHANGE = "info_change"            # 迁址/更名/更换审计机构/人事变动
    OPERATIONAL_INFO = "ops_info"          # 董事会决议/股东大会/常规会议
    
    OTHER = "other"                        # 其他无法归类的信息


class AffectedStock(BaseModel):
    """影响的股票"""
    name: str = Field(..., description="股票名称")
    code: Optional[str] = Field(None, description="股票代码")
    reason: Optional[str] = Field(None, description="影响逻辑")


class AffectedSector(BaseModel):
    """影响的板块"""
    name: str = Field(..., description="板块名称")
    code: Optional[str] = Field(None, description="板块代码")
    reason: Optional[str] = Field(None, description="带动或压制逻辑")


class AffectedMaterial(BaseModel):
    """影响的原材料"""
    name: str = Field(..., description="原材料名称")
    trend: Optional[str] = Field(None, description="趋势：涨/跌")


class AIAnalysis(BaseModel):
    """AI 分析结果"""
    impact_score: Optional[float] = Field(None, ge=0, le=1, description="影响打分: 0(无影响) 到 1(极大影响)")
    sentiment_score: Optional[float] = Field(None, description="情绪分")
    confidence_score: Optional[float] = Field(None, ge=0, le=1, description="置信度: 0-1")
    is_hype: Optional[bool] = Field(False, description="是否为炒作")
    impact_reason: Optional[str] = Field(None, description="深度理由")
    
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
    
    # 新增支持多类型
    event_types: List[EventType] = Field(default_factory=list, description="所有匹配的事件子类型")
    
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
    event_types: List[EventType] = []
    announcement_date: datetime
    expected_date: Optional[datetime] = None
    source: Optional[str] = None
    original_url: Optional[str] = None
    ai_analysis: Optional[AIAnalysis] = None


class EventUpdate(BaseModel):
    """更新事件的请求模型"""
    title: Optional[str] = None
    content: Optional[str] = None
    event_category: Optional[EventCategory] = None
    event_types: Optional[List[EventType]] = None
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
    event_types: List[str]
    announcement_date: datetime
    expected_date: Optional[datetime] = None
    source: Optional[str] = None
    original_url: Optional[str] = None
    ai_analysis: Optional[AIAnalysis] = None
    created_at: datetime
    updated_at: datetime

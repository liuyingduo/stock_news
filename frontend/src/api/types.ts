// 事件类型
export enum EventCategory {
  CORE_DRIVER = 'core_driver',
  SPECIAL_SITUATION = 'special_situation',
  INDUSTRIAL_CHAIN = 'industrial_chain',
  SENTIMENT_FLOWS = 'sentiment_flows',
  MACRO_GEOPOLITICS = 'macro_geopolitics',
}

export enum EventType {
  REGULATORY_POLICY = 'regulatory_policy',
  INDUSTRY_POLICY = 'industry_policy',
  REGULATORY_PENALTY = 'regulatory_penalty',
  APPROVAL = 'approval',
  EARNINGS_PREVIEW = 'earnings_preview',
  DIVIDEND = 'dividend',
  REFINANCING = 'refinancing',
  MA = 'ma',
  RESTRUCTURING = 'restructuring',
  MANAGEMENT_CHANGE = 'management_change',
  SPINOFF = 'spinoff',
  PRICE_CHANGE = 'price_change',
  CAPACITY_CHANGE = 'capacity_change',
  SUPPLY_DEMAND = 'supply_demand',
  ABNORMAL_MOVEMENT = 'abnormal_movement',
  PUBLIC_SENTIMENT = 'public_sentiment',
  INDEX_CHANGE = 'index_change',
  MONETARY_POLICY = 'monetary_policy',
  GEOPOLITICAL_RISK = 'geopolitical_risk',
  MACRO_INDICATORS = 'macro_indicators',
  LITIGATION = 'litigation',
  SHAREHOLDER_CHANGE = 'shareholder_change',
  REPURCHASE = 'repurchase',
  ANNUAL_REPORT = 'annual_report',
  OTHER = 'other',
}

export interface AffectedStock {
  name: string
  code: string
}

export interface AffectedSector {
  name: string
  code: string
}

export interface AffectedMaterial {
  name: string
}

export interface AIAnalysis {
  impact_score: number | null
  impact_reason: string | null
  affected_sectors: AffectedSector[]
  affected_stocks: AffectedStock[]
  affected_materials: AffectedMaterial[]
  analyzed_at: string | null
}

export interface Event {
  id: string
  title: string
  content: string
  event_category: EventCategory
  event_type: EventType
  announcement_date: string
  expected_date: string | null
  source: string | null
  original_url: string | null
  ai_analysis: AIAnalysis | null
  created_at: string
  updated_at: string
}

export interface DashboardStats {
  total_events: number
  total_sectors: number
  total_stocks: number
  recent_events_7days: number
  category_stats: Array<{ category: string; count: number }>
}

export interface Sector {
  id: string
  name: string
  code: string
  risk_level: string
  description: string | null
  related_event_ids: string[]
  created_at: string
  updated_at: string
}

export interface Stock {
  id: string
  name: string
  code: string
  status: string
  industry: string | null
  related_event_ids: string[]
  created_at: string
  updated_at: string
}

export interface EventsQuery {
  skip?: number
  limit?: number
  category?: string
  event_type?: string
  search?: string
  start_date?: string
  end_date?: string
}

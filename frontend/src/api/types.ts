// 事件类型
export enum EventCategory {
  GLOBAL_MACRO = 'global_macro',
  POLICY = 'policy',
  INDUSTRY = 'industry',
  COMPANY = 'company',
}

export enum EventType {
  // 全球大事
  GEOPOLITICS = 'geopolitics',
  // 政策风向
  REGULATORY = 'regulatory',
  MARKET_SENTIMENT = 'sentiment',
  // 行业动向
  TECH_INNOV = 'tech_innov',
  SUPPLY_CHAIN = 'supply_chain',
  PRICE_VOL = 'price_vol',
  // 公司动态
  INFO_CHANGE = 'info_change',
  OPS_INFO = 'ops_info',
  ORDER_CONTRACT = 'order_contract',
  CAPITAL_ACTION = 'capital_action',
  RISK_CRISIS = 'risk_crisis',
}

export interface AffectedStock {
  name: string
  code: string
  reason?: string  // 新增：影响理由
}

export interface AffectedSector {
  name: string
  code: string
  reason?: string  // 新增：影响理由
}

export interface AffectedMaterial {
  name: string
}

export interface AIAnalysis {
  impact_score: number | null
  sentiment_score?: number       // 新增：-1 to 1
  confidence_score?: number      // 新增：0-1
  is_hype?: boolean              // 新增：是否炒作
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
  event_category: string  // 使用 string 而不是枚举，以匹配数据库实际值
  event_types: EventType[]  // 数据库返回的是数组
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
  min_impact?: number
  max_impact?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
}

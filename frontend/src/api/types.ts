// 事件类型
export enum EventCategory {
  GLOBAL_EVENTS = 'global_events',
  POLICY_TRENDS = 'policy_trends',
  INDUSTRY_TRENDS = 'industry_trends',
  COMPANY_UPDATES = 'company_updates',
}

export enum EventType {
  // 全球大事
  MACRO_GEOPOLITICS = 'macro_geopolitics',
  // 政策风向
  REGULATORY_POLICY = 'regulatory_policy',
  MARKET_SENTIMENT = 'market_sentiment',
  // 行业动向
  INDUSTRIAL_CHAIN = 'industrial_chain',
  CORE_SECTOR = 'core_sector',
  // 公司动态
  MAJOR_EVENT = 'major_event',
  FINANCIAL_REPORT = 'financial_report',
  FINANCING_ANNOUNCEMENT = 'financing_announcement',
  RISK_WARNING = 'risk_warning',
  ASSET_RESTRUCTURING = 'asset_restructuring',
  INFO_CHANGE = 'info_change',
  SHAREHOLDING_CHANGE = 'shareholding_change',
  OTHER = 'other',
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
  event_category: EventCategory
  event_type: EventType | EventType[]  // 支持两种格式：单个字符串或数组
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

export interface PaginatedResponse<T> {
  items: T[]
  total: number
}

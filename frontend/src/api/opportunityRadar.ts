import api from './index'

export interface OpportunityRadarOverview {
  window_hours: number
  sample_size: number
  market_index: number
  avg_confidence: number
  opportunity_count: number
  risk_count: number
  neutral_count: number
  updated_at: string
}

export interface OpportunityRadarEvent {
  id: string
  title: string
  content: string
  event_category: string
  event_types: string[]
  announcement_date: string
  source: string | null
  original_url: string | null
  impact_reason: string | null
  is_hype: boolean
  affected_sector_codes: string[]
  affected_stock_codes: string[]
  impact_score: number
  sentiment_score: number
  confidence_score: number
  freshness_score: number
  relevance_score: number
  direction: 'opportunity' | 'risk' | 'neutral'
  calculation: {
    method: 'llm' | 'heuristic'
    impact_raw: number
    sentiment_raw: number
    confidence_raw: number
    formula: string
  }
}

export interface OpportunityRadarSignalsResponse {
  signal_type: 'opportunity' | 'risk'
  window_hours: number
  total: number
  items: OpportunityRadarEvent[]
}

export interface OpportunityRadarTopEventsResponse {
  lookback_days: number
  min_relevance: number
  total: number
  items: OpportunityRadarEvent[]
}

export const getOpportunityRadarOverview = (windowHours = 72) => {
  return api.get<any, OpportunityRadarOverview>('/opportunity-radar/overview', {
    params: { window_hours: windowHours },
  })
}

export const getOpportunityRadarSignals = (
  signalType: 'opportunity' | 'risk',
  limit = 10,
  windowHours = 72
) => {
  return api.get<any, OpportunityRadarSignalsResponse>('/opportunity-radar/signals', {
    params: {
      signal_type: signalType,
      limit,
      window_hours: windowHours,
    },
  })
}

export const getOpportunityRadarTopEvents = (limit = 20, lookbackDays = 30, minRelevance = 0) => {
  return api.get<any, OpportunityRadarTopEventsResponse>('/opportunity-radar/top-events', {
    params: {
      limit,
      lookback_days: lookbackDays,
      min_relevance: minRelevance,
    },
  })
}

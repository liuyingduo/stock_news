import type { OpportunityRadarOverview } from '@/api/opportunityRadar'
import type { TimeWindowKey } from './types'

export const TOP_EVENTS_INITIAL_VISIBLE = 5

export const windowHoursMap: Record<TimeWindowKey, number> = {
  '1H': 1,
  '4H': 4,
  '1D': 24,
}

export const lookbackDaysMap: Record<TimeWindowKey, number> = {
  '1H': 7,
  '4H': 14,
  '1D': 30,
}

export const defaultOverview: OpportunityRadarOverview = {
  window_hours: 4,
  sample_size: 0,
  market_index: 0,
  avg_confidence: 0,
  opportunity_count: 0,
  risk_count: 0,
  neutral_count: 0,
  updated_at: '',
}

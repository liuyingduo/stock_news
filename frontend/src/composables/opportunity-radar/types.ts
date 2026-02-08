import type { OpportunityRadarEvent } from '@/api/opportunityRadar'

export type TimeWindowKey = '1H' | '4H' | '1D'
export type DirectionFilter = 'all' | 'opportunity' | 'risk'
export type FreshnessFilter = 'all' | 'first' | 'relay'

export interface MarketMetricView {
  label: string
  value: string
  valueClass: string
  delta: number
}

export interface SignalCardView {
  total: number
  title: string
  time: string
  content: string
}

export interface TopEventRowView {
  event: OpportunityRadarEvent
  rank: string
  title: string
  summary: string
  typeLabel: string
  scoreText: string
  scorePositive: boolean
  tags: string[]
}

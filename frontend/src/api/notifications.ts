import api from './index'

export type NotificationLevel = 'red' | 'yellow'

export interface WatchlistAlertItem {
  id: string
  stock_name: string
  stock_code: string
  display_code: string
  market_index: number
  threshold: number
  sample_size: number
  latest_event_at: string | null
  triggered_at: string
  tag: string
  level: NotificationLevel
}

export interface WatchlistAlertsResponse {
  threshold: number
  window_hours: number
  watchlist_size: number
  triggered_count: number
  items: WatchlistAlertItem[]
  updated_at: string
}

export const getWatchlistAlerts = (threshold = 30, windowHours = 72) => {
  return api.get<any, WatchlistAlertsResponse>('/stocks/watchlist/alerts', {
    params: {
      threshold,
      window_hours: windowHours,
    },
  })
}

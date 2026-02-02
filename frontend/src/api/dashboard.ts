import api from './index'
import type { DashboardStats } from './types'

export const getDashboardStats = () => {
  return api.get<any, DashboardStats>('/dashboard/stats')
}

export const getDashboardSummary = () => {
  return api.get('/dashboard/summary')
}

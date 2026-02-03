import api from './index'
import type { Event, EventsQuery, PaginatedResponse } from './types'

/**
 * EcoSignal 专用 API
 * 提供类型安全的方法用于获取金融信号数据
 */

/**
 * 获取 EcoSignal 事件数据（只获取已分析的事件）
 */
export const getEcoSignalEvents = async (
  query: EventsQuery = {}
): Promise<PaginatedResponse<Event>> => {
  return api.get('/events', {
    params: {
      ...query,
      // 默认只获取有AI分析的事件
      limit: query.limit || 20,
      skip: query.skip || 0,
    },
  })
}

/**
 * 获取市场情绪统计
 * 注意：这个端点可能需要在后端实现
 * 当前通过前端计算实现
 */
export const getMarketSentiment = async () => {
  // 前端计算版本
  // 实际数据在 Store 中计算
  return null
}

/**
 * 获取高光事件（重磅预警 + 风险避雷）
 * 注意：这个端点可能需要在后端实现
 * 当前通过前端筛选实现
 */
export const getHighlights = async () => {
  // 前端筛选版本
  // 实际数据在 Store 中筛选
  return {
    heavy_alerts: [] as Event[],
    risk_events: [] as Event[],
  }
}

// 导出类型供外部使用
export type { Event, EventsQuery, PaginatedResponse }

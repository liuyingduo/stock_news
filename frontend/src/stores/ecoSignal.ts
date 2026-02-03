import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getEvents } from '../api/events'
import type { Event, EventsQuery } from '../api/types'

export const useEcoSignalStore = defineStore('ecoSignal', () => {
  // State
  const events = ref<Event[]>([])
  const total = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 分页状态
  const currentPage = ref(1)
  const pageSize = ref(20)
  const hasMore = computed(() => events.value.length < total.value)

  // 筛选状态
  const filters = ref<Partial<EventsQuery>>({
    category: undefined,
    event_type: undefined,
    search: undefined,
    start_date: undefined,
    end_date: undefined,
  })

  // Getters: 计算统计数据
  const eventsWithAI = computed(() => {
    return events.value.filter(e => e.ai_analysis !== null)
  })

  const averageSentiment = computed(() => {
    const validEvents = eventsWithAI.value.filter(
      e => e.ai_analysis?.sentiment_score !== undefined && e.ai_analysis?.sentiment_score !== null
    )
    if (validEvents.length === 0) return 0
    const sum = validEvents.reduce((acc, e) => acc + (e.ai_analysis!.sentiment_score || 0), 0)
    return sum / validEvents.length
  })

  const averageImpact = computed(() => {
    const validEvents = eventsWithAI.value.filter(
      e => e.ai_analysis?.impact_score !== undefined && e.ai_analysis?.impact_score !== null
    )
    if (validEvents.length === 0) return 0
    const sum = validEvents.reduce((acc, e) => acc + (e.ai_analysis!.impact_score || 0), 0)
    return sum / validEvents.length
  })

  // 高亮事件：重磅预警 (impact > 0.7)
  const highImpactEvents = computed(() => {
    return events.value.filter(e => {
      const score = e.ai_analysis?.impact_score
      return score !== null && score !== undefined && score > 0.7
    })
  })

  // 风险避雷 (sentiment < -0.6)
  const riskEvents = computed(() => {
    return events.value.filter(e => {
      const score = e.ai_analysis?.sentiment_score
      return score !== undefined && score !== null && score < -0.6
    })
  })

  // 情绪炒作事件
  const hypeEvents = computed(() => {
    return events.value.filter(e => e.ai_analysis?.is_hype === true)
  })

  // 统计数据
  const stats = computed(() => ({
    total: total.value,
    withAI: eventsWithAI.value.length,
    averageSentiment: averageSentiment.value,
    averageImpact: averageImpact.value,
    highImpactCount: highImpactEvents.value.length,
    riskCount: riskEvents.value.length,
    hypeCount: hypeEvents.value.length,
  }))

  // Actions: 加载事件
  const loadEvents = async (reset = false) => {
    if (loading.value) return

    if (reset) {
      currentPage.value = 1
      events.value = []
    }

    loading.value = true
    error.value = null

    try {
      const queryParams: EventsQuery = {
        skip: (currentPage.value - 1) * pageSize.value,
        limit: pageSize.value,
        ...filters.value,
      }

      const response = await getEvents(queryParams)

      if (reset) {
        events.value = response.items || []
      } else {
        events.value.push(...(response.items || []))
      }

      total.value = response.total || 0
    } catch (err: any) {
      error.value = err.message || '加载事件失败'
      console.error('Failed to load events:', err)
    } finally {
      loading.value = false
    }
  }

  // 加载更多（用于无限滚动）
  const loadMore = async () => {
    if (!hasMore.value || loading.value) return
    currentPage.value++
    await loadEvents(false)
  }

  // 刷新数据
  const refresh = async () => {
    await loadEvents(true)
  }

  // 更新筛选条件
  const updateFilters = (newFilters: Partial<EventsQuery>) => {
    filters.value = { ...filters.value, ...newFilters }
  }

  // 应用筛选（重置并重新加载）
  const applyFilters = async (newFilters?: Partial<EventsQuery>) => {
    if (newFilters) {
      updateFilters(newFilters)
    }
    await loadEvents(true)
  }

  // 清空数据
  const clear = () => {
    events.value = []
    total.value = 0
    currentPage.value = 1
    error.value = null
  }

  return {
    // State
    events,
    total,
    loading,
    error,
    currentPage,
    pageSize,
    filters,

    // Getters
    hasMore,
    eventsWithAI,
    averageSentiment,
    averageImpact,
    highImpactEvents,
    riskEvents,
    hypeEvents,
    stats,

    // Actions
    loadEvents,
    loadMore,
    refresh,
    updateFilters,
    applyFilters,
    clear,
  }
})

import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { getEvents } from '@/api/events'
import { getDashboardStats } from '@/api/dashboard'
import type { Event, EventsQuery } from '@/api/types'
import { categoryGroups } from './dashboard/category-groups'

type SortKey = 'default' | 'impact' | 'sentiment' | 'confidence'
type SortOrder = 'asc' | 'desc'

export function useDashboardEvents() {
  const router = useRouter()

  const loading = ref(false)
  const events = ref<Event[]>([])
  const total = ref(0)
  const pageSize = ref(20)
  const skip = ref(0)

  const searchTerm = ref('')
  const activeCategory = ref('')
  const activeEventType = ref('')
  const dateRange = ref<{ start?: string; end?: string }>({})
  const sortKey = ref<SortKey>('default')
  const sortOrder = ref<SortOrder>('desc')

  const stats = ref({
    total_events: 0,
    total_sectors: 0,
    total_stocks: 0,
    recent_events_7days: 0,
  })

  const hasMore = computed(() => events.value.length < total.value)

  const highConfidenceCount = computed(() =>
    events.value.filter((event) => (event.ai_analysis?.confidence_score ?? 0) >= 0.8).length,
  )

  const bullishRatio = computed(() => {
    const valid = events.value.filter(
      (event) => event.ai_analysis?.sentiment_score !== null && event.ai_analysis?.sentiment_score !== undefined,
    )
    if (valid.length === 0) return '--'
    const bullish = valid.filter((event) => (event.ai_analysis?.sentiment_score ?? 0) > 0).length
    return `${Math.round((bullish / valid.length) * 100)}%`
  })

  const sortedEvents = computed(() => {
    if (sortKey.value === 'default') return events.value

    const list = [...events.value]
    const order = sortOrder.value === 'asc' ? 1 : -1
    const getMetric = (event: Event): number | null => {
      if (sortKey.value === 'impact') return event.ai_analysis?.impact_score ?? null
      if (sortKey.value === 'sentiment') return event.ai_analysis?.sentiment_score ?? null
      if (sortKey.value === 'confidence') return event.ai_analysis?.confidence_score ?? null
      return null
    }

    list.sort((a, b) => {
      const va = getMetric(a)
      const vb = getMetric(b)
      if (va === null && vb === null) return 0
      if (va === null) return 1
      if (vb === null) return -1
      return order * (va - vb)
    })

    return list
  })

  const buildQuery = (): EventsQuery => {
    const query: EventsQuery = {
      skip: skip.value,
      limit: pageSize.value,
      search: searchTerm.value || undefined,
      category: activeCategory.value || undefined,
      event_type: activeEventType.value || undefined,
    }

    if (dateRange.value.start) query.start_date = dateRange.value.start
    if (dateRange.value.end) query.end_date = dateRange.value.end

    return query
  }

  const fetchStats = async () => {
    try {
      const data = await getDashboardStats()
      stats.value = data
    } catch (error) {
      console.error('Failed to load stats:', error)
    }
  }

  const fetchEvents = async (append = false) => {
    loading.value = true
    try {
      const response = await getEvents(buildQuery())
      total.value = response.total || 0
      if (append) {
        const map = new Map(events.value.map((item) => [item.id, item]))
        for (const item of response.items || []) {
          map.set(item.id, item)
        }
        events.value = Array.from(map.values())
      } else {
        events.value = response.items || []
      }
    } catch (error) {
      console.error('Failed to load events:', error)
    } finally {
      loading.value = false
    }
  }

  const applyFilters = () => {
    skip.value = 0
    fetchEvents(false)
  }

  const loadMore = () => {
    if (!hasMore.value || loading.value) return
    skip.value += pageSize.value
    fetchEvents(true)
  }

  const setSort = (key: SortKey) => {
    if (sortKey.value === key) {
      if (key === 'default') return
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
      return
    }
    sortKey.value = key
    sortOrder.value = key === 'default' ? 'desc' : 'desc'
  }

  const selectCategory = (category: string) => {
    activeCategory.value = category
    activeEventType.value = ''
    applyFilters()
  }

  const selectEventType = (category: string, type: string) => {
    activeCategory.value = category
    activeEventType.value = type
    applyFilters()
  }

  const setToday = () => {
    const today = new Date()
    const formatted = today.toISOString().split('T')[0]
    dateRange.value = { start: formatted, end: formatted }
    applyFilters()
  }

  const setLast7Days = () => {
    const end = new Date()
    const start = new Date()
    start.setDate(end.getDate() - 6)
    const startDate = start.toISOString().split('T')[0]
    const endDate = end.toISOString().split('T')[0]
    dateRange.value = { start: startDate, end: endDate }
    applyFilters()
  }

  const getCategoryLabel = (category: string) => {
    const found = categoryGroups.find((group) => group.key === category)
    return found ? found.label : '其他'
  }

  const getTypeLabel = (type: string) => {
    for (const group of categoryGroups) {
      const found = group.types.find((item) => item.key === type)
      if (found) return found.label
    }
    return type
  }

  const formatImpact = (impact?: number | null) => {
    if (impact === null || impact === undefined) return '--'
    return (impact * 10).toFixed(1)
  }

  const formatConfidence = (confidence?: number | null) => {
    if (confidence === null || confidence === undefined) return '--'
    return `${Math.round(confidence * 100)}%`
  }

  const formatSignal = (signal?: number | null) => {
    if (signal === null || signal === undefined) return '--'
    const fixed = signal.toFixed(1)
    return signal > 0 ? `+${fixed}` : fixed
  }

  const getSignalTextClass = (event: Event) => {
    const signal = event.ai_analysis?.sentiment_score
    if (signal === undefined || signal === null) return 'text-signal-neutral'
    return signal >= 0 ? 'text-signal-bullish text-glow-bullish' : 'text-signal-bearish text-glow-bearish'
  }

  const getSignalBarClass = (event: Event) => {
    const signal = event.ai_analysis?.sentiment_score
    if (signal === undefined || signal === null) return 'bg-gray-600'
    return signal >= 0
      ? 'bg-signal-bullish shadow-[0_0_10px_rgba(255,51,51,0.6)]'
      : 'bg-signal-bearish shadow-[0_0_10px_rgba(0,230,118,0.4)]'
  }

  const getCardHighlightClass = (event: Event) => {
    const impact = event.ai_analysis?.impact_score
    if (impact !== undefined && impact !== null && impact >= 0.85) {
      return 'border-primary/40 animate-pulse-border shadow-lg shadow-black/50'
    }
    return ''
  }

  const goToEvent = (id: string) => {
    router.push({ name: 'EventDetail', params: { id } })
  }

  const init = async () => {
    await Promise.all([fetchStats(), fetchEvents(false)])
  }

  return {
    loading,
    events,
    total,
    pageSize,
    searchTerm,
    activeCategory,
    activeEventType,
    sortKey,
    sortOrder,
    stats,
    categoryGroups,
    hasMore,
    highConfidenceCount,
    bullishRatio,
    sortedEvents,
    applyFilters,
    loadMore,
    setSort,
    selectCategory,
    selectEventType,
    setToday,
    setLast7Days,
    getCategoryLabel,
    getTypeLabel,
    formatImpact,
    formatConfidence,
    formatSignal,
    getSignalTextClass,
    getSignalBarClass,
    getCardHighlightClass,
    goToEvent,
    init,
  }
}

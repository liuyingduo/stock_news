import { computed, ref } from 'vue'
import {
  getOpportunityRadarOverview,
  getOpportunityRadarSignals,
  getOpportunityRadarTopEvents,
  type OpportunityRadarEvent,
  type OpportunityRadarOverview,
} from '@/api/opportunityRadar'

export type TimeWindowKey = '1H' | '4H' | '1D'
export type DirectionFilter = 'all' | 'opportunity' | 'risk'
export type FreshnessFilter = 'all' | 'first' | 'relay'

interface MarketMetricView {
  label: string
  value: string
  valueClass: string
  delta: number
}

interface SignalCardView {
  total: number
  title: string
  time: string
  content: string
}

interface TopEventRowView {
  event: OpportunityRadarEvent
  rank: string
  title: string
  summary: string
  typeLabel: string
  scoreText: string
  scorePositive: boolean
  tags: string[]
}

const TOP_EVENTS_INITIAL_VISIBLE = 5

const windowHoursMap: Record<TimeWindowKey, number> = {
  '1H': 1,
  '4H': 4,
  '1D': 24,
}

const lookbackDaysMap: Record<TimeWindowKey, number> = {
  '1H': 7,
  '4H': 14,
  '1D': 30,
}

const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value))

const defaultOverview: OpportunityRadarOverview = {
  window_hours: 4,
  sample_size: 0,
  market_index: 0,
  avg_confidence: 0,
  opportunity_count: 0,
  risk_count: 0,
  neutral_count: 0,
  updated_at: '',
}

function truncateText(text: string | null | undefined, maxLength: number): string {
  const raw = (text || '').replace(/\s+/g, ' ').trim()
  if (!raw) return '--'
  if (raw.length <= maxLength) return raw
  return `${raw.slice(0, maxLength)}...`
}

function toSigned(value: number, digits = 1): string {
  const fixed = Math.abs(value).toFixed(digits)
  return `${value >= 0 ? '+' : '-'}${fixed}`
}

function toChangePercent(current: number, prev: number | null): number {
  if (prev === null) return 0
  if (Math.abs(prev) < 1e-6) return clamp(current * 100, -99.9, 99.9)
  return clamp(((current - prev) / Math.abs(prev)) * 100, -99.9, 99.9)
}

function trendLabel(marketIndex: number): string {
  if (marketIndex >= 40) return '极度乐观'
  if (marketIndex >= 15) return '理性乐观'
  if (marketIndex > -15) return '中性观察'
  if (marketIndex > -40) return '理性谨慎'
  return '风险规避'
}

function formatClock(value: string | null | undefined): string {
  if (!value) return '--:--'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '--:--'
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${hh}:${mm}`
}

export function useOpportunityRadar() {
  const loading = ref(false)
  const selectedTimeWindow = ref<TimeWindowKey>('4H')
  const directionFilter = ref<DirectionFilter>('all')
  const freshnessFilter = ref<FreshnessFilter>('all')
  const topEventsExpanded = ref(false)

  const overview = ref<OpportunityRadarOverview | null>(null)
  const previousOverview = ref<OpportunityRadarOverview | null>(null)
  const opportunityEventsRaw = ref<OpportunityRadarEvent[]>([])
  const riskEventsRaw = ref<OpportunityRadarEvent[]>([])
  const topEventsRaw = ref<OpportunityRadarEvent[]>([])

  const currentOverview = computed<OpportunityRadarOverview>(() => {
    return overview.value || { ...defaultOverview, window_hours: windowHoursMap[selectedTimeWindow.value] }
  })

  const marketIndex = computed(() => Number(currentOverview.value.market_index || 0))
  const avgConfidence = computed(() => Number(currentOverview.value.avg_confidence || 0))
  const sampleSize = computed(() => Number(currentOverview.value.sample_size || 0))
  const longShort = computed(() => {
    if (sampleSize.value <= 0) return 0
    return (currentOverview.value.opportunity_count - currentOverview.value.risk_count) / sampleSize.value
  })
  const impact = computed(() => clamp(Math.abs(marketIndex.value) * 0.7 + avgConfidence.value * 0.3, 0, 100))

  const marketDelta = computed(() => {
    if (!previousOverview.value) return marketIndex.value / 8
    return marketIndex.value - Number(previousOverview.value.market_index || 0)
  })

  const narrativeDelta = computed(() => {
    if (!previousOverview.value) return longShort.value * 100
    return toChangePercent(sampleSize.value, Number(previousOverview.value.sample_size || 0))
  })

  const confidenceDelta = computed(() => {
    if (!previousOverview.value) return avgConfidence.value - 50
    return toChangePercent(avgConfidence.value, Number(previousOverview.value.avg_confidence || 0))
  })

  const longShortDelta = computed(() => {
    if (!previousOverview.value) return longShort.value * 100
    const prevSample = Number(previousOverview.value.sample_size || 0)
    const prevLongShort = prevSample > 0
      ? (previousOverview.value.opportunity_count - previousOverview.value.risk_count) / prevSample
      : null
    return toChangePercent(longShort.value, prevLongShort)
  })

  const impactDelta = computed(() => {
    if (!previousOverview.value) return marketIndex.value / 10
    const prevImpact = clamp(
      Math.abs(Number(previousOverview.value.market_index || 0)) * 0.7 +
      Number(previousOverview.value.avg_confidence || 0) * 0.3,
      0,
      100
    )
    return toChangePercent(impact.value, prevImpact)
  })

  const marketView = computed(() => {
    const positiveTrend = marketIndex.value >= 0
    return {
      value: marketIndex.value.toFixed(1),
      delta: marketDelta.value,
      deltaText: toSigned(marketDelta.value, 1),
      trendText: trendLabel(marketIndex.value),
      positiveTrend,
      deltaClass: positiveTrend
        ? 'text-market-up bg-market-up/10 border-market-up/20'
        : 'text-market-down bg-market-down/10 border-market-down/20',
      trendBadgeClass: positiveTrend
        ? 'border-market-up/30 bg-market-up/5 shadow-glow-red'
        : 'border-market-down/30 bg-market-down/5 shadow-glow-green',
      trendTextClass: positiveTrend ? 'text-market-up text-glow-red' : 'text-market-down',
    }
  })

  const marketMetrics = computed<MarketMetricView[]>(() => {
    return [
      {
        label: '叙事规模',
        value: sampleSize.value.toLocaleString('en-US'),
        valueClass: 'text-white',
        delta: narrativeDelta.value,
      },
      {
        label: '置信度',
        value: `${avgConfidence.value.toFixed(0)}%`,
        valueClass: 'text-white',
        delta: confidenceDelta.value,
      },
      {
        label: '多空信号',
        value: toSigned(longShort.value, 2),
        valueClass: longShort.value >= 0 ? 'text-market-up' : 'text-market-down',
        delta: longShortDelta.value,
      },
      {
        label: '影响力',
        value: impact.value.toFixed(0),
        valueClass: 'text-white',
        delta: impactDelta.value,
      },
    ]
  })

  const isFirstNews = (event: OpportunityRadarEvent): boolean => !event.is_hype
  const isRelayNews = (event: OpportunityRadarEvent): boolean => event.is_hype

  const matchesFreshness = (event: OpportunityRadarEvent): boolean => {
    if (freshnessFilter.value === 'all') return true
    if (freshnessFilter.value === 'first') return isFirstNews(event)
    return isRelayNews(event)
  }

  const matchesDirection = (event: OpportunityRadarEvent): boolean => {
    if (directionFilter.value === 'all') return true
    return event.direction === directionFilter.value
  }

  const filteredOpportunityEvents = computed(() => {
    return opportunityEventsRaw.value.filter(matchesFreshness)
  })

  const filteredRiskEvents = computed(() => {
    return riskEventsRaw.value.filter(matchesFreshness)
  })

  const topEventsFiltered = computed(() => {
    return topEventsRaw.value.filter((event) => {
      return matchesFreshness(event) && matchesDirection(event)
    })
  })

  const displayedTopEvents = computed(() => {
    if (topEventsExpanded.value) return topEventsFiltered.value
    return topEventsFiltered.value.slice(0, TOP_EVENTS_INITIAL_VISIBLE)
  })

  const topEventsButtonText = computed(() => {
    const total = topEventsFiltered.value.length
    if (total <= TOP_EVENTS_INITIAL_VISIBLE) {
      return `已显示全部 ${total} 条事件`
    }
    if (topEventsExpanded.value) {
      return `已显示全部 ${total} 条事件（点击收起）`
    }
    return `查看全部 ${Math.max(total - TOP_EVENTS_INITIAL_VISIBLE, 0)} 条剩余事件`
  })

  const toSignalCard = (events: OpportunityRadarEvent[], enabled: boolean): SignalCardView => {
    if (!enabled) {
      return {
        total: 0,
        title: '暂无事件',
        time: '--:--',
        content: '当前筛选条件下无可展示事件',
      }
    }

    const first = events[0]
    if (!first) {
      return {
        total: 0,
        title: '暂无事件',
        time: '--:--',
        content: '暂无可展示内容',
      }
    }

    return {
      total: events.length,
      title: truncateText(first.title, 14),
      time: formatClock(first.announcement_date),
      content: truncateText(first.content, 42),
    }
  }

  const opportunityCard = computed<SignalCardView>(() => {
    const enabled = directionFilter.value === 'all' || directionFilter.value === 'opportunity'
    return toSignalCard(filteredOpportunityEvents.value, enabled)
  })

  const riskCard = computed<SignalCardView>(() => {
    const enabled = directionFilter.value === 'all' || directionFilter.value === 'risk'
    return toSignalCard(filteredRiskEvents.value, enabled)
  })

  const topEventRows = computed<TopEventRowView[]>(() => {
    return displayedTopEvents.value.map((event, index) => {
      const scorePositive = (event.sentiment_score ?? 0) >= 0
      const tags = (
        event.affected_stock_codes.length > 0
          ? event.affected_stock_codes
          : event.affected_sector_codes
      ).slice(0, 2)

      return {
        event,
        rank: String(index + 1).padStart(2, '0'),
        title: truncateText(event.title, 20),
        summary: truncateText(event.content, 38),
        typeLabel: truncateText(event.event_types[0] || event.event_category || '未分类', 8),
        scoreText: `${scorePositive ? '+' : ''}${Number(event.relevance_score || 0).toFixed(1)}`,
        scorePositive,
        tags: tags.length > 0 ? tags : ['--'],
      }
    })
  })

  const topEventDetail = computed(() => {
    const lead = displayedTopEvents.value[0]
    const lines = displayedTopEvents.value.slice(0, 3).map((event) => ({
      time: formatClock(event.announcement_date),
      text: event.source
        ? `${event.source}: ${truncateText(event.title, 52)}`
        : truncateText(event.title, 52),
    }))

    return {
      newsLines: lines.length > 0 ? lines : [{ time: '--:--', text: '--' }],
      reason: truncateText(lead?.impact_reason || lead?.content || '暂无推演结论', 120),
    }
  })

  function sideFilterButtonClass(active: boolean): string {
    if (active) return 'text-logic-gold bg-white/5'
    return 'text-gray-400 hover:text-white hover:bg-white/5'
  }

  function timeButtonClass(windowKey: TimeWindowKey): string {
    if (selectedTimeWindow.value === windowKey) {
      return 'bg-logic-gold/20 text-logic-gold border border-logic-gold/30 font-bold'
    }
    return 'bg-white/5 hover:bg-white/10 text-gray-400 border border-white/5'
  }

  function setDirectionFilter(nextFilter: DirectionFilter): void {
    if (directionFilter.value === nextFilter) return
    directionFilter.value = nextFilter
    topEventsExpanded.value = false
  }

  function toggleDirectionFilter(target: Exclude<DirectionFilter, 'all'>): void {
    directionFilter.value = directionFilter.value === target ? 'all' : target
    topEventsExpanded.value = false
  }

  function setFreshnessFilter(nextFilter: FreshnessFilter): void {
    if (freshnessFilter.value === nextFilter) return
    freshnessFilter.value = nextFilter
    topEventsExpanded.value = false
  }

  function toggleFreshnessFilter(target: Exclude<FreshnessFilter, 'all'>): void {
    freshnessFilter.value = freshnessFilter.value === target ? 'all' : target
    topEventsExpanded.value = false
  }

  function formatDeltaText(value: number): string {
    return `${toSigned(value, 1)}%`
  }

  async function loadRadarData(windowKey: TimeWindowKey): Promise<void> {
    loading.value = true
    try {
      previousOverview.value = overview.value
      const hours = windowHoursMap[windowKey]
      const lookbackDays = lookbackDaysMap[windowKey]
      const [overviewResp, opportunityResp, riskResp, topResp] = await Promise.all([
        getOpportunityRadarOverview(hours),
        getOpportunityRadarSignals('opportunity', 10, hours),
        getOpportunityRadarSignals('risk', 10, hours),
        getOpportunityRadarTopEvents(20, lookbackDays, 0),
      ])

      overview.value = overviewResp
      opportunityEventsRaw.value = opportunityResp.items || []
      riskEventsRaw.value = riskResp.items || []
      topEventsRaw.value = topResp.items || []
      topEventsExpanded.value = false
    } finally {
      loading.value = false
    }
  }

  async function changeTimeWindow(windowKey: TimeWindowKey): Promise<void> {
    if (selectedTimeWindow.value === windowKey) return
    selectedTimeWindow.value = windowKey
    await loadRadarData(windowKey)
  }

  function toggleTopEventsExpanded(): boolean {
    const canToggle = topEventsFiltered.value.length > TOP_EVENTS_INITIAL_VISIBLE
    if (!canToggle) return false
    const wasExpanded = topEventsExpanded.value
    topEventsExpanded.value = !topEventsExpanded.value
    return wasExpanded
  }

  async function init(): Promise<void> {
    await loadRadarData(selectedTimeWindow.value)
  }

  return {
    loading,
    selectedTimeWindow,
    directionFilter,
    freshnessFilter,
    topEventsExpanded,
    marketView,
    marketMetrics,
    opportunityCard,
    riskCard,
    topEventRows,
    topEventDetail,
    topEventsButtonText,
    timeButtonClass,
    sideFilterButtonClass,
    setDirectionFilter,
    toggleDirectionFilter,
    setFreshnessFilter,
    toggleFreshnessFilter,
    changeTimeWindow,
    toggleTopEventsExpanded,
    formatDeltaText,
    init,
  }
}

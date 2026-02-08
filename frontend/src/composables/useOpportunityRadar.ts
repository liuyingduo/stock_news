import { computed, ref } from 'vue'
import {
  getOpportunityRadarOverview,
  getOpportunityRadarSignals,
  getOpportunityRadarTopEvents,
  type OpportunityRadarEvent,
  type OpportunityRadarOverview,
} from '@/api/opportunityRadar'
import { TOP_EVENTS_INITIAL_VISIBLE, defaultOverview, lookbackDaysMap, windowHoursMap } from './opportunity-radar/constants'
import { clamp, formatClock, toChangePercent, toSigned, truncateText } from './opportunity-radar/helpers'
import type {
  DirectionFilter,
  FreshnessFilter,
  MarketTopItemView,
  MarketMetricView,
  SignalCardView,
  TimeWindowKey,
  TopEventRowView,
} from './opportunity-radar/types'

export type {
  DirectionFilter,
  FreshnessFilter,
  MarketTopItemView,
  MarketMetricView,
  SignalCardView,
  TimeWindowKey,
  TopEventRowView,
} from './opportunity-radar/types'

function trendLabel(marketIndex: number): string {
  if (marketIndex >= 40) return '极度乐观'
  if (marketIndex >= 15) return '理性乐观'
  if (marketIndex > -15) return '中性观望'
  if (marketIndex > -40) return '理性谨慎'
  return '风险规避'
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
      100,
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

  const marketTopFive = computed<MarketTopItemView[]>(() => {
    const sourceEvents = topEventsFiltered.value.length > 0
      ? topEventsFiltered.value
      : topEventsRaw.value

    const aggregate = new Map<string, { total: number; count: number }>()

    for (const event of sourceEvents) {
      const entities = event.affected_stock_codes.length > 0
        ? event.affected_stock_codes
        : event.affected_sector_codes

      if (entities.length === 0) continue

      const uniqueEntities = Array.from(new Set(entities)).slice(0, 3)
      const sentimentRaw = Number(event.sentiment_score ?? 0)
      const directionSign = event.direction === 'risk' ? -1 : 1
      const signedSentiment = Math.abs(sentimentRaw) < 1e-6
        ? directionSign * 0.5
        : clamp(sentimentRaw, -1, 1)
      const confidence = clamp(Number(event.confidence_score ?? 0.7), 0, 1)
      const relevance = clamp(Number(event.relevance_score ?? 0), 0, 100)
      const eventScore = clamp(signedSentiment * (0.7 * relevance + 30 * confidence), -100, 100)

      for (const entity of uniqueEntities) {
        const key = entity || '--'
        const prev = aggregate.get(key)
        if (prev) {
          prev.total += eventScore
          prev.count += 1
        } else {
          aggregate.set(key, { total: eventScore, count: 1 })
        }
      }
    }

    return Array.from(aggregate.entries())
      .map(([label, value]) => {
        const score = value.count > 0 ? value.total / value.count : 0
        return { label, score }
      })
      .sort((a, b) => Math.abs(b.score) - Math.abs(a.score))
      .slice(0, 5)
      .map((item, index) => ({
        rank: index + 1,
        label: item.label,
        score: item.score,
        scoreText: toSigned(item.score, 1),
      }))
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
    marketTopFive,
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

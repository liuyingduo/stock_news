import { computed, ref, watch } from 'vue'
import { getEventsByStock } from '@/api/events'
import {
  addStockToMyWatchlist,
  getMyWatchlist,
  getStockByCode,
  getStocks,
  removeStockFromMyWatchlist,
} from '@/api/stocks'
import type { Event, Stock } from '@/api/types'
import { baseEdges, emptyWatchItem, intervalHours, profileMap, tabs, timeIntervals } from './asset-monitor/constants'
import {
  buildFallbackProfile,
  buildNodes,
  buildSnapshot,
  mapStock,
  normalizeStockCode,
  shortTime,
  unwrapApiResult,
} from './asset-monitor/helpers'
import type {
  GraphNode,
  InsightCard,
  IntervalKey,
  Profile,
  WatchItem,
} from './asset-monitor/types'

export type {
  AssetTabKey,
  GraphEdge,
  GraphNode,
  InsightCard,
  IntervalKey,
  NodeGroup,
  NodeKind,
  NodeSentiment,
  Profile,
  Snapshot,
  WatchItem,
} from './asset-monitor/types'

export function useAssetMonitor() {
  const activeTab = ref<'logic' | 'relation'>('logic')
  const activeInterval = ref<IntervalKey>('1H')
  const activeStockCode = ref('')
  const selectedNodeId = ref('core')
  const graphZoom = ref(1)

  const searchQuery = ref('')
  const notificationsEnabled = ref(true)
  const thresholdIndexMove = ref(20)
  const thresholdNarrativeGrowth = ref(300)

  const allStocks = ref<WatchItem[]>([])
  const watchlist = ref<WatchItem[]>([])
  const stockEvents = ref<Event[]>([])
  const lastUpdated = ref(new Date())

  const matchedStocks = computed(() => {
    const query = searchQuery.value.trim().toLowerCase()
    if (!query) return []

    return allStocks.value
      .filter((item) => item.name.toLowerCase().includes(query) || item.code.includes(query))
      .filter((item) => !watchlist.value.some((w) => w.code === item.code))
      .slice(0, 8)
  })

  const currentStock = computed<WatchItem>(() => {
    return watchlist.value.find((item) => item.code === activeStockCode.value) || watchlist.value[0] || emptyWatchItem
  })

  const currentProfile = computed<Profile>(() => {
    return profileMap[currentStock.value.code] || buildFallbackProfile(currentStock.value.name)
  })

  const snapshot = computed(() => buildSnapshot(currentStock.value.code || '000000', activeInterval.value, currentProfile.value))
  const graphNodes = computed(() => buildNodes(currentProfile.value, currentStock.value))
  const graphEdges = computed(() => baseEdges)

  const nodeMap = computed<Record<string, GraphNode>>(() => {
    return graphNodes.value.reduce<Record<string, GraphNode>>((acc, node) => {
      acc[node.id] = node
      return acc
    }, {})
  })

  const selectedNode = computed(() => nodeMap.value[selectedNodeId.value] || graphNodes.value[0])

  const activeNodeIds = computed(() => {
    const selected = selectedNodeId.value
    const set = new Set<string>([selected])

    graphEdges.value.forEach((edge) => {
      if (selected === 'core' || edge.from === selected || edge.to === selected) {
        set.add(edge.from)
        set.add(edge.to)
      }
    })

    if (selected === 'core') {
      graphNodes.value.forEach((node) => set.add(node.id))
    }

    return set
  })

  const activeEdgeIds = computed(() => {
    const selected = selectedNodeId.value
    const set = new Set<string>()

    graphEdges.value.forEach((edge) => {
      if (selected === 'core') {
        if (edge.from === 'core') set.add(edge.id)
      } else if (edge.from === selected || edge.to === selected) {
        set.add(edge.id)
      }
    })

    return set
  })

  const filteredEvents = computed(() => {
    if (stockEvents.value.length === 0 || !activeStockCode.value) return []

    const cutoff = Date.now() - intervalHours[activeInterval.value] * 60 * 60 * 1000
    const sorted = [...stockEvents.value].sort(
      (a, b) => new Date(b.announcement_date).getTime() - new Date(a.announcement_date).getTime(),
    )
    const recent = sorted.filter((evt) => new Date(evt.announcement_date).getTime() >= cutoff)
    return recent.length > 0 ? recent : sorted
  })

  const insightCards = computed<InsightCard[]>(() => {
    if (filteredEvents.value.length === 0) {
      return []
    }

    return filteredEvents.value.slice(0, 6).map((evt, index) => {
      const sentiment = Number(evt.ai_analysis?.sentiment_score || 0)
      return {
        id: evt.id || `evt-${index}`,
        title: (evt.title || '--').slice(0, 18),
        stance: sentiment >= 0 ? '利好' : '利空',
        confidence: Math.round((evt.ai_analysis?.confidence_score || 0.82) * 100),
        sourceCount: evt.source ? 1 : 0,
        summary: (evt.content || '--').replace(/\s+/g, ' ').slice(0, 120),
        time: shortTime(evt.announcement_date),
        references: [`${evt.source || '系统'} · ${shortTime(evt.announcement_date)}`, (evt.title || '--').slice(0, 38)],
      }
    })
  })

  const topMetrics = computed(() => [
    {
      key: 'narrative',
      label: '叙事规模',
      value: Math.round(snapshot.value.narrative).toString(),
      delta: snapshot.value.deltaNarrative,
    },
    {
      key: 'impact',
      label: '影响力',
      value: snapshot.value.impact.toFixed(1),
      delta: snapshot.value.deltaImpact,
    },
    {
      key: 'longShort',
      label: '多空信号',
      value: snapshot.value.longShort.toFixed(2),
      delta: snapshot.value.deltaLongShort,
    },
    {
      key: 'confidence',
      label: '置信度',
      value: `${Math.round(snapshot.value.confidence)}%`,
      delta: snapshot.value.deltaConfidence,
    },
  ])

  function toY(value: number): number {
    return 130 - ((value + 100) / 200) * 100
  }

  const linePath = computed(() => {
    const points = snapshot.value.trendPoints
    if (points.length === 0) return ''

    const step = 300 / (points.length - 1)
    return points
      .map((v, i) => `${i === 0 ? 'M' : 'L'}${(i * step).toFixed(2)},${toY(v).toFixed(2)}`)
      .join(' ')
  })

  const areaPath = computed(() => `${linePath.value} L300,150 L0,150 Z`)

  const coreTicker = computed(() => {
    const label = (currentStock.value.name || '').toUpperCase().replace(/\s+/g, '')
    return label.slice(0, 4)
  })

  const lastUpdatedText = computed(() => {
    const t = lastUpdated.value
    return `${String(t.getHours()).padStart(2, '0')}:${String(t.getMinutes()).padStart(2, '0')}:${String(t.getSeconds()).padStart(2, '0')}`
  })

  function mapStockList(stocks: Stock[]): WatchItem[] {
    return stocks.map((item) => mapStock(item)).filter((item): item is WatchItem => Boolean(item))
  }

  function emitWatchlistUpdated() {
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('watchlist-updated'))
    }
  }

  function applyWatchlist(nextWatchlist: WatchItem[]) {
    watchlist.value = nextWatchlist
    if (!nextWatchlist.some((item) => item.code === activeStockCode.value)) {
      activeStockCode.value = nextWatchlist[0]?.code || ''
    }
  }

  async function loadStocks() {
    try {
      const stocks = unwrapApiResult<Stock[]>(await getStocks())
      allStocks.value = mapStockList(stocks)
    } catch (error) {
      console.error('加载股票列表失败:', error)
      allStocks.value = []
    }
  }

  async function loadWatchlist() {
    try {
      const stocks = unwrapApiResult<Stock[]>(await getMyWatchlist())
      applyWatchlist(mapStockList(stocks))
    } catch (error) {
      console.error('加载监控列表失败:', error)
      applyWatchlist([])
    }
  }

  async function loadEvents(code: string) {
    if (!code) {
      stockEvents.value = []
      lastUpdated.value = new Date()
      return
    }

    try {
      stockEvents.value = await getEventsByStock(code, 30)
    } catch (error) {
      console.error('加载个股事件失败:', error)
      stockEvents.value = []
    } finally {
      lastUpdated.value = new Date()
    }
  }

  async function addCandidate(candidate: WatchItem) {
    try {
      const stocks = unwrapApiResult<Stock[]>(await addStockToMyWatchlist(candidate.code))
      applyWatchlist(mapStockList(stocks))
    } catch (error) {
      console.error('保存监控股票失败:', error)
      if (!watchlist.value.some((item) => item.code === candidate.code)) {
        watchlist.value.push(candidate)
      }
    }

    activeStockCode.value = candidate.code
    searchQuery.value = ''
    emitWatchlistUpdated()
  }

  async function removeStock(code: string) {
    try {
      const stocks = unwrapApiResult<Stock[]>(await removeStockFromMyWatchlist(code))
      applyWatchlist(mapStockList(stocks))
    } catch (error) {
      console.error('移除监控股票失败:', error)
      watchlist.value = watchlist.value.filter((item) => item.code !== code)
      if (!watchlist.value.some((item) => item.code === activeStockCode.value)) {
        activeStockCode.value = watchlist.value[0]?.code || ''
      }
    }
    emitWatchlistUpdated()
  }

  async function addStockFromSearch() {
    const query = searchQuery.value.trim()
    if (!query) return

    if (matchedStocks.value[0]) {
      await addCandidate(matchedStocks.value[0])
      return
    }

    const normalized = normalizeStockCode(query)
    if (!normalized) return

    try {
      const stock = unwrapApiResult<Stock>(await getStockByCode(normalized))
      const mapped = mapStock(stock)
      if (!mapped) return

      if (!allStocks.value.some((item) => item.code === mapped.code)) {
        allStocks.value.push(mapped)
      }

      await addCandidate(mapped)
    } catch (error) {
      console.error('根据代码添加股票失败:', error)
    }
  }

  function toggleGraphZoom() {
    graphZoom.value = graphZoom.value > 1 ? 1 : 1.12
  }

  function selectNode(id: string) {
    selectedNodeId.value = id
  }

  watch(activeStockCode, async (code) => {
    selectedNodeId.value = 'core'
    graphZoom.value = 1

    if (!code) {
      stockEvents.value = []
      lastUpdated.value = new Date()
      return
    }

    await loadEvents(code)
  })

  watch(activeInterval, () => {
    lastUpdated.value = new Date()
  })

  async function init() {
    await loadStocks()
    await loadWatchlist()
    await loadEvents(activeStockCode.value)
  }

  return {
    tabs,
    timeIntervals,
    activeTab,
    activeInterval,
    activeStockCode,
    selectedNodeId,
    graphZoom,
    searchQuery,
    notificationsEnabled,
    thresholdIndexMove,
    thresholdNarrativeGrowth,
    matchedStocks,
    watchlist,
    currentStock,
    currentProfile,
    graphNodes,
    graphEdges,
    nodeMap,
    selectedNode,
    activeNodeIds,
    activeEdgeIds,
    insightCards,
    topMetrics,
    snapshot,
    linePath,
    areaPath,
    coreTicker,
    lastUpdatedText,
    addStockFromSearch,
    addCandidate,
    removeStock,
    toggleGraphZoom,
    selectNode,
    init,
  }
}

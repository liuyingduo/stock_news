<template>
  <div class="bg-background-light dark:bg-background-dark text-slate-900 dark:text-white antialiased overflow-hidden h-screen flex flex-col font-body text-rendering-optimize">
    <AppHeader />

    <div class="bg-surface-darker border-b border-border-dark shrink-0">
      <div class="flex flex-wrap gap-0 divide-x divide-border-dark">
        <div class="flex items-center gap-4 px-6 py-3">
          <div>
            <p class="text-gray-400 text-xs font-medium uppercase tracking-wider">最近7天事件总量</p>
            <div class="flex items-baseline gap-2">
              <p class="text-white text-xl font-bold font-mono tracking-tight">{{ stats.recent_events_7days.toLocaleString() }}</p>
              <p class="text-signal-bullish text-xs font-bold font-mono text-glow-bullish">总量 {{ stats.total_events.toLocaleString() }}</p>
            </div>
          </div>
          <div class="h-8 w-16 bg-gradient-to-t from-signal-bullish/20 to-transparent flex items-end gap-0.5">
            <div class="w-1 bg-signal-bullish h-[40%] rounded-t-sm shadow-[0_0_5px_rgba(255,51,51,0.5)]"></div>
            <div class="w-1 bg-signal-bullish h-[60%] rounded-t-sm shadow-[0_0_5px_rgba(255,51,51,0.5)]"></div>
            <div class="w-1 bg-signal-bullish h-[30%] rounded-t-sm shadow-[0_0_5px_rgba(255,51,51,0.5)]"></div>
            <div class="w-1 bg-signal-bullish h-[80%] rounded-t-sm shadow-[0_0_5px_rgba(255,51,51,0.5)]"></div>
            <div class="w-1 bg-signal-bullish h-[50%] rounded-t-sm shadow-[0_0_5px_rgba(255,51,51,0.5)]"></div>
            <div class="w-1 bg-signal-bullish h-[90%] rounded-t-sm shadow-[0_0_5px_rgba(255,51,51,0.5)]"></div>
          </div>
        </div>
        <div class="flex items-center gap-4 px-6 py-3">
          <div>
            <p class="text-gray-400 text-xs font-medium uppercase tracking-wider">高置信度事件</p>
            <div class="flex items-baseline gap-2">
              <p class="text-white text-xl font-bold font-mono tracking-tight">{{ highConfidenceCount.toLocaleString() }}</p>
              <p class="text-signal-bullish text-xs font-bold font-mono text-glow-bullish">当前页</p>
            </div>
          </div>
        </div>
        <div class="flex items-center gap-4 px-6 py-3">
          <div>
            <p class="text-gray-400 text-xs font-medium uppercase tracking-wider">看多情绪占比</p>
            <div class="flex items-baseline gap-2">
              <p class="text-white text-xl font-bold font-mono tracking-tight">{{ bullishRatio }}</p>
              <p class="text-signal-bearish text-xs font-bold font-mono text-glow-bearish">当前页</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="flex flex-1 overflow-hidden">
      <aside class="w-80 bg-surface-darker border-r border-border-dark flex flex-col overflow-y-auto shrink-0 custom-scrollbar">
        <div class="p-4 space-y-6">
          <div>
            <label class="flex flex-col w-full">
              <span class="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wide">搜索情报</span>
              <div class="flex w-full items-center rounded-lg h-10 bg-[#181b21] border border-border-dark focus-within:border-primary focus-within:ring-1 focus-within:ring-primary transition-all">
                <div class="text-gray-400 flex items-center justify-center pl-3">
                  <span class="material-symbols-outlined text-[20px]">search</span>
                </div>
                <input
                  v-model="searchTerm"
                  class="w-full bg-transparent border-none text-white text-sm placeholder:text-gray-500 focus:ring-0 px-3 font-display"
                  placeholder="代码、关键词或来源..."
                  @keyup.enter="applyFilters"
                />
              </div>
            </label>
          </div>
          <div class="flex flex-col gap-1">
            <span class="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1">事件类别</span>
            <button
              class="flex items-center justify-between px-3 py-2 rounded-md bg-[#181b21] border border-primary/20 text-primary font-medium text-sm transition-colors text-left w-full mb-1"
              @click="selectCategory('')"
            >
              <span>全部事件</span>
              <span class="material-symbols-outlined text-[16px]">check</span>
            </button>
            <details v-for="group in categoryGroups" :key="group.key" class="group rounded-md" :open="activeCategory === group.key">
              <summary
                class="flex items-center justify-between px-3 py-2 hover:bg-[#181b21] text-gray-400 hover:text-white text-sm transition-colors cursor-pointer select-none"
                @click.prevent="selectCategory(group.key)"
              >
                <span>{{ group.label }}</span>
                <span class="material-symbols-outlined text-[16px] transition-transform group-open:rotate-180">expand_more</span>
              </summary>
              <div class="flex flex-col gap-1 pl-4 pb-2 border-l border-border-dark ml-3.5 my-1">
                <button
                  v-for="type in group.types"
                  :key="type.key"
                  class="text-left text-xs py-1 px-2 rounded transition-colors"
                  :class="type.key === activeEventType ? 'text-primary bg-[#181b21]' : 'text-gray-500 hover:text-primary hover:bg-[#181b21]'"
                  @click="selectEventType(group.key, type.key)"
                >
                  {{ type.label }}
                </button>
              </div>
            </details>
          </div>
          <div class="h-px bg-border-dark w-full"></div>
          <div class="flex flex-col gap-3">
            <span class="text-xs font-semibold text-gray-400 uppercase tracking-wide">筛选器</span>
            <details class="group rounded-lg border border-border-dark bg-[#0f1115] open">
              <summary class="flex cursor-pointer items-center justify-between gap-2 px-3 py-2.5 bg-[#181b21] hover:bg-[#22272e] transition-colors rounded-t-lg select-none">
                <div class="flex items-center gap-2">
                  <span class="material-symbols-outlined text-gray-400 text-[18px]">calendar_today</span>
                  <p class="text-white text-sm font-medium">日期范围</p>
                </div>
                <span class="material-symbols-outlined text-gray-400 group-open:rotate-180 transition-transform text-[20px]">expand_more</span>
              </summary>
              <div class="p-3 border-t border-border-dark">
                <div class="flex flex-col gap-2">
                  <div class="flex gap-2 mt-2">
                    <button class="flex-1 bg-border-dark hover:bg-[#3c4453] text-white text-xs py-1.5 rounded transition-colors" @click="setToday">今天</button>
                    <button class="flex-1 bg-border-dark hover:bg-[#3c4453] text-white text-xs py-1.5 rounded transition-colors" @click="setLast7Days">过去7天</button>
                  </div>
                </div>
              </div>
            </details>
          </div>
        </div>
      </aside>

      <main ref="mainRef" class="flex-1 overflow-y-auto bg-background-dark p-6 custom-scrollbar">
        <div class="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-5">
          <div class="col-span-full flex items-center justify-between mb-4">
            <h1 class="text-white text-xl font-bold font-display tracking-tight">最新实时情报</h1>
            <div class="flex items-center gap-6 bg-[#181b21] px-4 py-2 rounded-lg border border-border-dark">
              <span class="text-xs font-semibold text-gray-500 uppercase tracking-wider">排序</span>
              <button
                class="flex items-center gap-1.5 text-sm font-medium group transition-all"
                :class="sortKey === 'default' ? 'text-primary font-bold' : 'text-gray-400 hover:text-white'"
                @click="setSort('default')"
              >
                <span>默认</span>
              </button>
              <button
                class="flex items-center gap-1.5 text-sm font-medium group transition-all"
                :class="sortKey === 'impact' ? 'text-primary font-bold' : 'text-gray-400 hover:text-white'"
                @click="setSort('impact')"
              >
                <span>影响力</span>
                <div class="flex flex-col -space-y-1.5">
                  <span
                    class="material-symbols-outlined text-[16px] leading-none"
                    :class="sortKey === 'impact' && sortOrder === 'asc' ? 'text-primary' : 'text-gray-600 group-hover:text-gray-500'"
                  >arrow_drop_up</span>
                  <span
                    class="material-symbols-outlined text-[16px] leading-none"
                    :class="sortKey === 'impact' && sortOrder === 'desc' ? 'text-primary' : 'text-gray-600 group-hover:text-gray-500'"
                  >arrow_drop_down</span>
                </div>
              </button>
              <button
                class="flex items-center gap-1.5 text-sm font-medium group transition-all"
                :class="sortKey === 'sentiment' ? 'text-primary font-bold' : 'text-gray-400 hover:text-white'"
                @click="setSort('sentiment')"
              >
                <span>多空信号</span>
                <div class="flex flex-col -space-y-1.5">
                  <span
                    class="material-symbols-outlined text-[16px] leading-none"
                    :class="sortKey === 'sentiment' && sortOrder === 'asc' ? 'text-primary' : 'text-gray-600 group-hover:text-gray-500'"
                  >arrow_drop_up</span>
                  <span
                    class="material-symbols-outlined text-[16px] leading-none"
                    :class="sortKey === 'sentiment' && sortOrder === 'desc' ? 'text-primary' : 'text-gray-600 group-hover:text-gray-500'"
                  >arrow_drop_down</span>
                </div>
              </button>
              <button
                class="flex items-center gap-1.5 text-sm font-medium group transition-all"
                :class="sortKey === 'confidence' ? 'text-primary font-bold' : 'text-gray-400 hover:text-white'"
                @click="setSort('confidence')"
              >
                <span>置信度</span>
                <div class="flex flex-col -space-y-1.5">
                  <span
                    class="material-symbols-outlined text-[16px] leading-none"
                    :class="sortKey === 'confidence' && sortOrder === 'asc' ? 'text-primary' : 'text-gray-600 group-hover:text-gray-500'"
                  >arrow_drop_up</span>
                  <span
                    class="material-symbols-outlined text-[16px] leading-none"
                    :class="sortKey === 'confidence' && sortOrder === 'desc' ? 'text-primary' : 'text-gray-600 group-hover:text-gray-500'"
                  >arrow_drop_down</span>
                </div>
              </button>
            </div>
          </div>

          <div v-if="loading && events.length === 0" class="col-span-full py-10 text-center text-gray-500">加载中...</div>
          <div v-else-if="!loading && events.length === 0" class="col-span-full py-10 text-center text-gray-500">暂无事件数据</div>
          <article
            v-else
            v-for="event in sortedEvents"
            :key="event.id"
            class="flex flex-col bg-[#151a23] rounded-xl border border-border-dark transition-all overflow-hidden relative group hover:bg-[#1c222e] cursor-pointer h-full"
            :class="getCardHighlightClass(event)"
            @click="goToEvent(event.id)"
          >
            <div class="absolute top-0 left-0 w-1 h-full" :class="getSignalBarClass(event)"></div>
            <div class="p-5 flex flex-col gap-3 h-full">
              <div class="flex justify-between items-center w-full">
                <div class="flex flex-wrap items-center gap-2 text-xs">
                  <span class="px-2 py-0.5 rounded bg-surface-dark border border-border-dark text-gray-300 font-medium">
                    {{ getCategoryLabel(event.event_category) }}
                  </span>
                  <span
                    v-for="type in event.event_types"
                    :key="type"
                    class="px-2 py-0.5 rounded bg-primary/10 border border-primary/20 text-primary font-bold"
                  >
                    {{ getTypeLabel(type) }}
                  </span>
                </div>
                <div class="flex items-center gap-2 text-xs text-gray-500 whitespace-nowrap font-mono">
                  <span>{{ event.source || '来源未知' }}</span>
                  <span class="text-border-dark opacity-50">|</span>
                  <span>{{ formatDateTime(event.announcement_date) }}</span>
                </div>
              </div>
              <h3 class="text-white text-lg font-bold leading-snug group-hover:text-primary transition-colors tracking-tight font-display">{{ event.title }}</h3>
              <p class="text-sm text-gray-400 leading-relaxed tracking-wide text-justify font-display line-clamp-2">
                {{ event.content }}
              </p>
              <div class="flex items-center justify-start gap-6 pt-3 border-t border-border-dark/50 mt-auto">
                <div class="flex items-baseline gap-2">
                  <span class="text-[11px] text-gray-500 font-medium uppercase tracking-wider">影响力</span>
                  <span class="text-lg font-bold text-white font-mono text-glow-gold">
                    {{ formatImpact(event.ai_analysis?.impact_score) }}
                  </span>
                </div>
                <div class="flex items-baseline gap-2">
                  <span class="text-[11px] text-gray-500 font-medium uppercase tracking-wider">多空信号</span>
                  <span class="text-lg font-bold font-mono" :class="getSignalTextClass(event)">
                    {{ formatSignal(event.ai_analysis?.sentiment_score) }}
                  </span>
                </div>
                <div class="flex items-baseline gap-2">
                  <span class="text-[11px] text-gray-500 font-medium uppercase tracking-wider">置信度</span>
                  <span class="text-lg font-bold text-white font-mono">
                    {{ formatConfidence(event.ai_analysis?.confidence_score) }}
                  </span>
                </div>
              </div>
            </div>
          </article>
        </div>
        <div class="h-12"></div>
        <div ref="loadMoreTrigger" class="h-4"></div>
        <div v-if="loading && events.length > 0" class="flex justify-center pb-10 text-gray-500 text-sm">
          加载中...
        </div>
        <div v-else-if="!hasMore && events.length > 0" class="flex justify-center pb-10 text-gray-500 text-sm">
          已加载全部数据
        </div>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'
import { useRouter } from 'vue-router'
import AppHeader from '@/components/common/AppHeader.vue'
import { getEvents } from '@/api/events'
import { getDashboardStats } from '@/api/dashboard'
import type { Event, EventsQuery } from '@/api/types'
import { formatDateTime } from '@/utils/date'

const router = useRouter()

const loading = ref(false)
const events = ref<Event[]>([])
const total = ref(0)
const pageSize = ref(20)
const skip = ref(0)
const mainRef = ref<HTMLElement | null>(null)
const loadMoreTrigger = ref<HTMLElement | null>(null)

const searchTerm = ref('')
const activeCategory = ref('')
const activeEventType = ref('')
const dateRange = ref<{ start?: string; end?: string }>({})
const sortKey = ref<'default' | 'impact' | 'sentiment' | 'confidence'>('default')
const sortOrder = ref<'asc' | 'desc'>('desc')

const stats = ref({
  total_events: 0,
  total_sectors: 0,
  total_stocks: 0,
  recent_events_7days: 0,
})

const categoryGroups = [
  {
    key: 'global_macro',
    label: '全球大事',
    types: [
      { key: 'geopolitics', label: '地缘政治' },
      { key: 'macro_econ', label: '宏观经济' },
    ],
  },
  {
    key: 'policy',
    label: '政策风向',
    types: [
      { key: 'regulatory', label: '监管政策' },
      { key: 'liquidity', label: '资金流向' },
      { key: 'sentiment', label: '市场情绪' },
    ],
  },
  {
    key: 'industry',
    label: '行业动向',
    types: [
      { key: 'tech_innov', label: '科技创新' },
      { key: 'supply_chain', label: '供应链' },
      { key: 'price_vol', label: '价格波动' },
    ],
  },
  {
    key: 'company',
    label: '公司动态',
    types: [
      { key: 'fin_perf', label: '业绩披露' },
      { key: 'order_contract', label: '订单合同' },
      { key: 'merger_re', label: '并购重组' },
      { key: 'capital_action', label: '资本运作' },
      { key: 'buyback', label: '股份回购' },
      { key: 'holder_change', label: '股东变动' },
      { key: 'insider_trans', label: '内部交易' },
      { key: 'risk_crisis', label: '风险危机' },
      { key: 'litigation', label: '诉讼仲裁' },
      { key: 'info_change', label: '信息变更' },
      { key: 'ops_info', label: '运营信息' },
      { key: 'other', label: '其他' },
    ],
  },
]

const hasMore = computed(() => events.value.length < total.value)
const highConfidenceCount = computed(() =>
  events.value.filter(event => (event.ai_analysis?.confidence_score ?? 0) >= 0.8).length
)
const bullishRatio = computed(() => {
  const valid = events.value.filter(event => event.ai_analysis?.sentiment_score !== null && event.ai_analysis?.sentiment_score !== undefined)
  if (valid.length === 0) return '--'
  const bullish = valid.filter(event => (event.ai_analysis?.sentiment_score ?? 0) > 0).length
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
      const map = new Map(events.value.map(item => [item.id, item]))
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

const setSort = (key: 'default' | 'impact' | 'sentiment' | 'confidence') => {
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
  const found = categoryGroups.find(group => group.key === category)
  return found ? found.label : '其他'
}

const getTypeLabel = (type: string) => {
  for (const group of categoryGroups) {
    const found = group.types.find(item => item.key === type)
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

onMounted(async () => {
  await Promise.all([fetchStats(), fetchEvents(false)])
})

useIntersectionObserver(
  loadMoreTrigger,
  ([{ isIntersecting }]) => {
    if (isIntersecting) loadMore()
  },
  {
    root: mainRef,
    rootMargin: '200px',
  }
)
</script>

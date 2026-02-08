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
        <div class="max-w-7xl mx-auto grid grid-cols-1 gap-5">
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
import { onMounted, ref } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'
import AppHeader from '@/components/common/AppHeader.vue'
import { formatDateTime } from '@/utils/date'
import { useDashboardEvents } from '@/composables/useDashboardEvents'

const mainRef = ref<HTMLElement | null>(null)
const loadMoreTrigger = ref<HTMLElement | null>(null)

const {
  loading,
  events,
  stats,
  searchTerm,
  activeCategory,
  activeEventType,
  sortKey,
  sortOrder,
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
} = useDashboardEvents()

onMounted(async () => {
  await init()
})

useIntersectionObserver(
  loadMoreTrigger,
  ([{ isIntersecting }]) => {
    if (isIntersecting) loadMore()
  },
  {
    root: mainRef,
    rootMargin: '200px',
  },
)
</script>




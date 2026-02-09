<template>
  <div class="bg-background-dark text-white antialiased text-rendering-optimize min-h-screen">
    <header class="sticky top-0 z-50 flex items-center gap-6 border-b border-border-dark bg-surface-darker/95 px-6 py-4 backdrop-blur">
      <button
        class="group flex items-center gap-2 text-sm font-medium text-gray-400 transition-colors hover:text-white"
        type="button"
        @click="goBack"
      >
        <span class="material-symbols-outlined text-[20px] transition-transform group-hover:-translate-x-1">arrow_back</span>
        返回列表
      </button>
      <div class="h-6 w-px bg-border-dark"></div>
      <div class="flex items-center gap-3">
        <div class="flex size-6 items-center justify-center text-primary shadow-glow-primary">
          <span class="material-symbols-outlined text-xl" style="font-variation-settings: 'FILL' 1, 'wght' 400;">travel_explore</span>
        </div>
        <h1 class="font-display text-base font-bold tracking-tight text-white">
          万古经纬 <span class="mx-2 font-normal text-gray-500">/</span> 情报详情
        </h1>
      </div>
    </header>

    <main class="mx-auto flex w-full max-w-5xl flex-col gap-8 p-6 md:p-10">
      <div v-if="loading" class="py-16 text-center text-sm text-gray-500">加载中...</div>

      <template v-else-if="event">
        <div class="flex flex-col gap-4">
          <div class="flex flex-wrap items-center gap-3">
            <span class="rounded border border-primary/30 bg-primary/10 px-2 py-0.5 text-xs font-bold uppercase tracking-wider text-primary">
              {{ getCategoryLabel(event.event_category) }}
            </span>
            <span
              v-for="type in event.event_types || []"
              :key="type"
              class="rounded border border-gray-600 bg-[#2A2F3A] px-2 py-0.5 text-xs font-bold uppercase tracking-wider text-gray-400"
            >
              {{ getTypeLabel(type) }}
            </span>
          </div>

          <h2 class="font-display text-3xl font-bold leading-tight tracking-tight text-white md:text-4xl">
            {{ event.title }}
          </h2>

          <div class="mt-1 flex flex-wrap items-center gap-6 font-mono text-sm text-gray-500">
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-[16px]">schedule</span>
              <span>{{ formatDate(event.announcement_date) }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="material-symbols-outlined text-[16px]">rss_feed</span>
              <span>来源: {{ event.source || '来源未知' }}</span>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-8">
          <div class="font-display text-[15px] leading-8 text-gray-300 md:text-base">
            <p v-for="(paragraph, index) in contentParagraphs" :key="index" class="mb-5 last:mb-0">
              {{ paragraph }}
            </p>
          </div>

          <div
            v-if="event.original_url"
            class="flex items-center justify-between rounded-lg border border-border-dark bg-surface-dark p-4 transition-colors hover:border-gray-600"
          >
            <div class="flex items-center gap-4">
              <div class="rounded border border-red-500/20 bg-red-500/10 p-2.5 text-red-500">
                <span class="material-symbols-outlined">picture_as_pdf</span>
              </div>
              <div>
                <p class="font-mono text-sm font-bold text-white">{{ originalLinkName }}</p>
                <p class="mt-0.5 font-mono text-xs text-gray-500">{{ originalLinkHost }}</p>
              </div>
            </div>
            <button
              class="flex items-center gap-2 rounded border border-transparent px-3 py-1.5 text-sm text-gray-300 transition-colors hover:border-gray-600 hover:bg-white/5 hover:text-white"
              type="button"
              @click="openOriginalLink"
            >
              <span class="material-symbols-outlined text-[18px]">visibility</span>
              查看详情
            </button>
          </div>
        </div>

        <div v-if="event.ai_analysis" class="space-y-4">
          <div class="rounded-r-lg border-l-4 border-primary bg-gradient-to-r from-primary/10 to-transparent p-4">
            <h3 class="mb-1 text-sm font-bold uppercase tracking-wider text-primary">AI分析理由</h3>
            <p class="text-sm leading-6 text-gray-200">
              {{ event.ai_analysis.impact_reason || '暂无分析理由' }}
            </p>
          </div>

          <div class="grid grid-cols-1 gap-px overflow-hidden rounded-lg border border-border-dark bg-border-dark md:grid-cols-3">
            <div class="flex items-center justify-between bg-surface-dark p-4">
              <div>
                <div class="mb-1 text-xs font-medium uppercase tracking-wider text-gray-500">影响力</div>
                <div class="flex items-baseline gap-2">
                  <span class="font-mono text-2xl font-bold text-white text-glow-gold">{{ formatImpact(event.ai_analysis.impact_score) }}</span>
                  <span class="text-xs text-gray-600">/ 10</span>
                </div>
              </div>
              <div class="h-10 w-1 rounded-full bg-gradient-to-t from-primary/20 to-primary shadow-[0_0_8px_rgba(212,175,55,0.4)]"></div>
            </div>

            <div class="flex items-center justify-between bg-surface-dark p-4">
              <div>
                <div class="mb-1 text-xs font-medium uppercase tracking-wider text-gray-500">多空信号</div>
                <div class="flex items-center gap-2">
                  <span class="font-mono text-2xl font-bold" :class="signalValueClass(event.ai_analysis.sentiment_score)">
                    {{ formatSignal(event.ai_analysis.sentiment_score) }}
                  </span>
                  <span
                    class="rounded border px-1.5 text-[10px] font-bold"
                    :class="signalBadgeClass(event.ai_analysis.sentiment_score)"
                  >
                    {{ signalBadgeLabel(event.ai_analysis.sentiment_score) }}
                  </span>
                </div>
              </div>
              <span class="material-symbols-outlined text-3xl opacity-80" :class="signalValueClass(event.ai_analysis.sentiment_score)">
                {{ signalIcon(event.ai_analysis.sentiment_score) }}
              </span>
            </div>

            <div class="flex items-center justify-between bg-surface-dark p-4">
              <div>
                <div class="mb-1 text-xs font-medium uppercase tracking-wider text-gray-500">置信度</div>
                <div class="flex items-baseline gap-2">
                  <span class="font-mono text-2xl font-bold text-blue-400">{{ formatConfidence(event.ai_analysis.confidence_score) }}</span>
                </div>
              </div>
              <div class="relative size-10">
                <svg class="size-full -rotate-90" viewBox="0 0 36 36">
                  <path
                    class="text-gray-700"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                  />
                  <path
                    class="text-blue-400 drop-shadow-[0_0_3px_rgba(96,165,250,0.5)]"
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="3"
                    :stroke-dasharray="confidenceDasharray(event.ai_analysis.confidence_score)"
                  />
                </svg>
              </div>
            </div>
          </div>
        </div>

        <footer class="mt-4 border-t border-border-dark pt-6">
          <div class="grid grid-cols-[auto_1fr] gap-x-6 gap-y-4 text-sm">
            <div class="whitespace-nowrap pt-1 font-medium text-gray-500">相关股票</div>
            <div class="flex flex-wrap gap-2">
              <template v-if="event.ai_analysis?.affected_stocks?.length">
                <span
                  v-for="stock in event.ai_analysis.affected_stocks"
                  :key="stock.code"
                  class="group flex items-center gap-2 rounded border border-border-dark bg-[#181b21] px-3 py-1 transition-all hover:border-gray-500 hover:bg-[#2A2F3A]"
                >
                  <span class="font-mono text-xs font-bold text-primary transition-colors group-hover:text-white">{{ stock.code }}</span>
                  <span class="text-gray-300 transition-colors group-hover:text-white">{{ stock.name }}</span>
                </span>
              </template>
              <span v-else class="text-xs text-gray-500">暂无相关股票</span>
            </div>

            <div class="whitespace-nowrap pt-1 font-medium text-gray-500">相关板块</div>
            <div class="flex flex-wrap gap-2">
              <template v-if="event.ai_analysis?.affected_sectors?.length">
                <span
                  v-for="sector in event.ai_analysis.affected_sectors"
                  :key="sector.code"
                  class="rounded border border-border-dark bg-[#181b21] px-2 py-1 text-xs text-gray-400"
                >
                  {{ sector.name }}
                </span>
              </template>
              <span v-else class="text-xs text-gray-500">暂无相关板块</span>
            </div>

            <div class="whitespace-nowrap pt-1 font-medium text-gray-500">相关原材料</div>
            <div class="flex flex-wrap gap-2">
              <template v-if="event.ai_analysis?.affected_materials?.length">
                <span
                  v-for="material in event.ai_analysis.affected_materials"
                  :key="material.name"
                  class="rounded border border-transparent bg-gray-800/50 px-2 py-0.5 text-xs text-gray-400"
                >
                  {{ material.name }}
                </span>
              </template>
              <span v-else class="text-xs text-gray-500">暂无相关原材料</span>
            </div>
          </div>
        </footer>
      </template>

      <div v-else class="py-16 text-center text-sm text-gray-500">
        事件不存在或已删除
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getEventById } from '@/api/events'
import type { Event } from '@/api/types'
import { formatDate } from '@/utils/date'
import { categoryGroups } from '@/composables/dashboard/category-groups'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const event = ref<Event | null>(null)

const categoryLabelMap = categoryGroups.reduce<Record<string, string>>((acc, group) => {
  acc[group.key] = group.label
  return acc
}, {})

const typeLabelMap = categoryGroups.flatMap((group) => group.types).reduce<Record<string, string>>((acc, type) => {
  acc[type.key] = type.label
  return acc
}, {})

const contentParagraphs = computed(() => {
  if (!event.value?.content) return ['暂无正文内容']
  const parts = event.value.content.split(/\r?\n+/).map((item) => item.trim()).filter(Boolean)
  return parts.length > 0 ? parts : ['暂无正文内容']
})

const originalLinkName = computed(() => {
  const url = event.value?.original_url
  if (!url) return '原始链接'
  try {
    const pathname = new URL(url).pathname
    const fileName = decodeURIComponent(pathname.split('/').filter(Boolean).pop() || '')
    return fileName || '原始链接'
  } catch {
    return '原始链接'
  }
})

const originalLinkHost = computed(() => {
  const url = event.value?.original_url
  if (!url) return '外部来源'
  try {
    return new URL(url).host
  } catch {
    return '外部来源'
  }
})

const getCategoryLabel = (category: string) => categoryLabelMap[category] || category
const getTypeLabel = (type: string) => typeLabelMap[type] || type

const formatImpact = (score?: number | null) => {
  if (score === undefined || score === null) return '--'
  return (score * 10).toFixed(1)
}

const formatSignal = (score?: number | null) => {
  if (score === undefined || score === null) return '--'
  const fixed = score.toFixed(2)
  return score > 0 ? `+${fixed}` : fixed
}

const formatConfidence = (score?: number | null) => {
  if (score === undefined || score === null) return '--'
  return `${Math.round(score * 100)}%`
}

const signalValueClass = (score?: number | null) => {
  if (score === undefined || score === null) return 'text-signal-neutral'
  return score >= 0 ? 'text-signal-bullish text-glow-bullish' : 'text-signal-bearish text-glow-bearish'
}

const signalBadgeLabel = (score?: number | null) => {
  if (score === undefined || score === null) return '未知'
  if (score >= 0.6) return '强利多'
  if (score >= 0.2) return '利多'
  if (score <= -0.6) return '强利空'
  if (score <= -0.2) return '利空'
  return '中性'
}

const signalBadgeClass = (score?: number | null) => {
  if (score === undefined || score === null) return 'border-signal-neutral/20 bg-signal-neutral/10 text-signal-neutral'
  if (score >= 0) return 'border-signal-bullish/20 bg-signal-bullish/10 text-signal-bullish'
  return 'border-signal-bearish/20 bg-signal-bearish/10 text-signal-bearish'
}

const signalIcon = (score?: number | null) => {
  if (score === undefined || score === null) return 'trending_flat'
  return score >= 0 ? 'trending_up' : 'trending_down'
}

const confidenceDasharray = (score?: number | null) => {
  if (score === undefined || score === null) return '0, 100'
  const percent = Math.max(0, Math.min(100, Math.round(score * 100)))
  return `${percent}, 100`
}

const loadEvent = async () => {
  const eventId = route.params.id as string | undefined
  if (!eventId) {
    event.value = null
    ElMessage.error('无效的事件ID')
    return
  }

  loading.value = true
  try {
    event.value = await getEventById(eventId)
  } catch (error: any) {
    event.value = null
    ElMessage.error(error?.message || '加载情报详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const openOriginalLink = () => {
  if (!event.value?.original_url) return
  window.open(event.value.original_url, '_blank', 'noopener,noreferrer')
}

onMounted(() => {
  void loadEvent()
})

watch(
  () => route.params.id,
  () => {
    void loadEvent()
  },
)
</script>

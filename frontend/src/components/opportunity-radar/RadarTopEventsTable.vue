<template>
  <div class="bg-surface-dark border border-white/5 rounded-2xl overflow-hidden flex flex-col shadow-lg">
    <div class="p-5 border-b border-white/5 bg-surface-lighter/20 flex justify-between items-center">
      <div class="flex items-center gap-3">
        <div class="p-1.5 rounded bg-logic-gold/10 border border-logic-gold/20">
          <span class="material-symbols-outlined text-logic-gold text-sm">view_list</span>
        </div>
        <h2 class="text-base font-bold text-white">博弈拐点 TOP 20</h2>
        <span class="text-xs text-gray-500 bg-white/5 px-2 py-0.5 rounded-full border border-white/10">筛选: 逻辑相关性 &gt; 80%</span>
      </div>
      <div class="flex gap-4 text-xs text-gray-500 font-mono">
        <span class="flex items-center gap-1"><span class="w-2 h-2 bg-market-up rounded-full"></span>多头信号</span>
        <span class="flex items-center gap-1"><span class="w-2 h-2 bg-market-down rounded-full"></span>空头信号</span>
        <span class="flex items-center gap-1"><span class="w-2 h-2 bg-logic-gold rounded-full"></span>关键转折</span>
      </div>
    </div>
    <div class="grid grid-cols-12 px-6 py-3 border-b border-white/5 bg-black/20 text-xs font-medium text-gray-500 uppercase tracking-wider">
      <div class="col-span-1"></div>
      <div class="col-span-4 text-left">事件</div>
      <div class="col-span-2 text-center">事件类型</div>
      <div class="col-span-2 text-right">指数</div>
      <div class="col-span-3 text-right pr-20">影响标的</div>
    </div>
    <div class="divide-y divide-white/5">
      <div v-if="topEventRows.length === 0" class="py-12 text-center text-sm text-gray-500">
        暂无可展示事件
      </div>

      <div v-for="(row, index) in topEventRows" :key="row.event.id || row.rank" :class="index === 0 ? 'bg-white/[0.02]' : ''">
        <div class="grid grid-cols-12 px-6 py-4 items-center hover:bg-white/5 transition-colors cursor-pointer group">
          <div class="col-span-1 font-mono font-bold text-lg" :class="index === 0 ? 'text-logic-gold' : 'text-gray-500'">{{ row.rank }}</div>
          <div class="col-span-4">
            <h3 class="text-sm font-bold transition-colors" :class="index === 0 ? 'text-white group-hover:text-logic-gold' : 'text-gray-300 group-hover:text-white'">{{ row.title }}</h3>
            <p class="text-xs mt-0.5 font-light" :class="index === 0 ? 'text-gray-500' : 'text-gray-600'">{{ row.summary }}</p>
          </div>
          <div class="col-span-2">
            <span class="inline-flex items-center rounded-full bg-blue-400/10 px-2 py-1 text-xs font-medium text-blue-400 ring-1 ring-inset ring-blue-400/20">{{ row.typeLabel }}</span>
          </div>
          <div class="col-span-2 text-right">
            <span class="text-sm font-mono font-bold" :class="row.scorePositive ? 'text-market-up' : 'text-market-down'">{{ row.scoreText }}</span>
          </div>
          <div class="col-span-3 flex justify-end gap-2">
            <span v-for="(tag, tagIndex) in row.tags" :key="`${row.rank}-${tagIndex}`" class="inline-flex items-center rounded bg-surface-lighter px-2 py-1 text-xs font-medium text-gray-300 font-mono border border-white/10">{{ tag }}</span>
            <span class="material-symbols-outlined text-gray-600 text-sm" :class="index === 0 ? 'rotate-180' : ''">{{ index === 0 ? 'expand_less' : 'expand_more' }}</span>
          </div>
        </div>

        <div v-if="index === 0" class="px-6 pb-6 pt-2 border-l-2 border-logic-gold ml-6 mb-2 bg-black/20 rounded-r-lg">
          <div class="grid grid-cols-3 gap-6">
            <div class="col-span-2">
              <h4 class="text-xs font-bold text-gray-400 mb-3 uppercase tracking-wider">新闻聚合 (News Aggregation)</h4>
              <ul class="space-y-2">
                <li v-for="(line, lineIndex) in topEventDetail.newsLines" :key="`line-${lineIndex}`" class="flex gap-3 text-xs text-gray-300">
                  <span class="text-gray-600 font-mono shrink-0">{{ line.time }}</span>
                  <span class="line-clamp-1 hover:text-white cursor-pointer">{{ line.text }}</span>
                </li>
              </ul>
            </div>
            <div class="col-span-1 border-l border-white/5 pl-6">
              <h4 class="text-xs font-bold text-gray-400 mb-3 uppercase tracking-wider">AI 逻辑推演</h4>
              <p class="text-xs text-gray-400 leading-relaxed">
                {{ topEventDetail.reason }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="px-6 py-4 border-t border-white/5 bg-black/10 flex justify-center">
      <button class="text-xs text-gray-500 hover:text-logic-gold transition-colors flex items-center gap-1" :disabled="loading" @click="$emit('toggle')">
        {{ topEventsButtonText }}
        <span class="material-symbols-outlined text-sm">{{ topEventsExpanded ? 'arrow_upward' : 'arrow_downward' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { TopEventRowView } from '@/composables/opportunity-radar/types'

defineProps<{
  loading: boolean
  topEventRows: TopEventRowView[]
  topEventDetail: { newsLines: Array<{ time: string; text: string }>; reason: string }
  topEventsButtonText: string
  topEventsExpanded: boolean
}>()

defineEmits<{
  (e: 'toggle'): void
}>()
</script>

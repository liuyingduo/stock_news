<template>
  <div class="custom-scrollbar h-full min-h-[520px] w-full space-y-3 overflow-y-auto pr-2 pb-6">
    <div
      v-if="cards.length === 0"
      class="flex min-h-[320px] items-center justify-center rounded-lg border border-dashed border-primary/20 bg-bg-card/30"
    >
      <div class="text-center">
        <div class="text-sm font-semibold text-text-sub">暂无逻辑洞察数据</div>
        <div class="mt-1 text-xs text-text-sub/70">当前股票在所选时间范围内没有可用事件</div>
      </div>
    </div>

    <article
      v-for="card in cards"
      :key="card.id"
      class="overflow-hidden rounded-lg border bg-bg-card transition-all"
      :class="card.stance === '利好' ? 'border-market-red/30 hover:border-market-red/50' : 'border-market-green/30 hover:border-market-green/50'"
    >
      <div class="flex items-center justify-between border-b border-primary/10 bg-black/20 px-4 py-3">
        <div class="flex items-center gap-3">
          <h3 class="text-base font-bold text-white">{{ card.title }}</h3>
          <span class="text-sm font-medium" :class="card.stance === '利好' ? 'text-market-red' : 'text-market-green'">{{ card.stance }}</span>
        </div>
        <div class="flex items-center gap-4 text-xs font-mono text-text-sub">
          <span>置信度 {{ card.confidence }}%</span>
          <span>{{ card.sourceCount }} 条来源</span>
          <span>{{ card.time }}</span>
        </div>
      </div>
      <div class="relative px-4 py-3">
        <div
          class="absolute left-0 top-0 h-full w-1"
          :class="card.stance === '利好' ? 'bg-market-red/80' : 'bg-market-green/80'"
        ></div>
        <p class="text-sm leading-relaxed text-text-light">{{ card.summary }}</p>
        <div class="mt-2 space-y-1 border-t border-primary/5 pt-2">
          <div v-for="(line, idx) in card.references" :key="`${card.id}-${idx}`" class="text-xs text-text-sub">
            {{ line }}
          </div>
        </div>
      </div>
    </article>
  </div>
</template>

<script setup lang="ts">
import type { InsightCard } from '@/composables/useAssetMonitor'

defineProps<{
  cards: InsightCard[]
}>()
</script>

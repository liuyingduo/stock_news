<template>
  <section class="shrink-0 border-b border-primary/10 bg-bg-card/50 p-6 pb-2">
    <div class="mb-4 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <h2 class="flex items-center gap-2 text-lg font-bold tracking-wide text-white">
          <span class="material-symbols-outlined text-primary">thermostat</span>
          资产逻辑气压计
        </h2>
        <div class="flex items-center rounded-lg border border-primary/20 bg-bg-main/60 p-0.5">
          <button
            v-for="time in timeIntervals"
            :key="time"
            class="rounded px-3 py-1 text-xs font-mono transition-colors"
            :class="
              activeInterval === time
                ? 'bg-primary/15 font-bold text-primary'
                : 'font-medium text-text-sub hover:text-white'
            "
            @click="$emit('update:activeInterval', time)"
          >
            {{ time }}
          </button>
        </div>
      </div>
      <span class="text-xs font-mono text-text-sub">最后更新: {{ lastUpdatedText }}</span>
    </div>

    <div class="grid grid-cols-1 gap-4 md:grid-cols-5">
      <div
        class="group relative flex min-h-[90px] flex-col justify-between overflow-hidden rounded-lg border border-primary/20 bg-gradient-to-br from-bg-card to-black p-4"
      >
        <div class="absolute right-0 top-0 p-2 opacity-10 transition-opacity group-hover:opacity-20">
          <span class="material-symbols-outlined text-5xl">sentiment_satisfied</span>
        </div>
        <div class="mb-2 flex items-center gap-1 text-xs font-medium text-text-sub">
          市场先生指数
          <span class="material-symbols-outlined text-[10px] text-text-sub/60">info</span>
        </div>
        <div class="mt-auto flex items-end gap-2">
          <span class="text-glow text-2xl font-bold font-mono" :class="marketIndex >= 0 ? 'text-market-red' : 'text-market-green'">
            {{ marketIndex.toFixed(1) }}
          </span>
          <div
            class="mb-1 flex items-center rounded px-1 py-0.5 text-xs font-medium font-mono"
            :class="marketDelta >= 0 ? 'bg-market-red/10 text-market-red' : 'bg-market-green/10 text-market-green'"
          >
            <span class="material-symbols-outlined mr-0.5 text-[10px]">
              {{ marketDelta >= 0 ? 'arrow_upward' : 'arrow_downward' }}
            </span>
            {{ formatDelta(marketDelta) }}
          </div>
        </div>
      </div>

      <div
        v-for="metric in metrics"
        :key="metric.key"
        class="flex min-h-[90px] flex-col justify-between rounded-lg border border-primary/10 bg-bg-card p-4 transition-colors hover:border-primary/30"
      >
        <span class="text-xs font-medium text-text-sub">{{ metric.label }}</span>
        <div class="mt-auto flex items-end gap-2">
          <span class="text-xl font-bold font-mono text-white">{{ metric.value }}</span>
          <div class="mb-1 flex items-center text-xs font-medium font-mono" :class="metric.delta >= 0 ? 'text-market-red' : 'text-market-green'">
            <span class="material-symbols-outlined mr-0.5 text-[10px]">
              {{ metric.delta >= 0 ? 'arrow_upward' : 'arrow_downward' }}
            </span>
            {{ formatDelta(metric.delta) }}
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import type { IntervalKey } from '@/composables/useAssetMonitor'

defineProps<{
  timeIntervals: IntervalKey[]
  activeInterval: IntervalKey
  lastUpdatedText: string
  marketIndex: number
  marketDelta: number
  metrics: Array<{ key: string; label: string; value: string; delta: number }>
}>()

defineEmits<{
  (e: 'update:activeInterval', value: IntervalKey): void
}>()

function formatDelta(value: number): string {
  const prefix = value >= 0 ? '+' : '-'
  return `${prefix}${Math.abs(value).toFixed(1)}%`
}
</script>

<style scoped>
.text-glow {
  text-shadow: 0 0 20px rgba(245, 63, 63, 0.5);
}
</style>

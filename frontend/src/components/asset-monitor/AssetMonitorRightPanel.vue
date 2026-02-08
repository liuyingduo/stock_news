<template>
  <div class="custom-scrollbar flex h-full w-full flex-col gap-4 overflow-y-auto pb-6">
    <div class="flex h-[280px] shrink-0 flex-col rounded-lg border border-primary/20 bg-bg-card p-4">
      <div class="mb-2 flex items-center justify-between">
        <h3 class="flex items-center gap-2 text-sm font-bold text-text-sub">
          <span class="material-symbols-outlined text-base">trending_up</span>
          市场先生指数趋势图
        </h3>
        <div class="rounded border border-primary/10 bg-bg-main px-2 py-0.5 text-[10px] font-mono text-text-sub">
          {{ activeInterval }} 周期
        </div>
      </div>
      <div class="relative flex h-full w-full flex-1 items-center justify-center rounded border border-primary/5 bg-black/20">
        <svg class="h-full w-full p-2" preserveAspectRatio="none" viewBox="0 0 300 150">
          <defs>
            <linearGradient id="gradientDarkRedAsset" x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" style="stop-color:#9B1C1C;stop-opacity:0.28" />
              <stop offset="100%" style="stop-color:#9B1C1C;stop-opacity:0" />
            </linearGradient>
          </defs>
          <line class="chart-grid-line" x1="0" y1="30" x2="300" y2="30" />
          <line class="chart-grid-line" x1="0" y1="75" x2="300" y2="75" />
          <line class="chart-grid-line" x1="0" y1="120" x2="300" y2="120" />
          <path class="chart-area" :d="areaPath" />
          <path class="chart-path" :d="linePath" />
        </svg>
        <div class="absolute right-1/4 top-1/4 rounded border border-market-dark-red/50 bg-bg-card/90 px-2 py-1 shadow-lg backdrop-blur-sm">
          <div class="text-xs font-bold font-mono text-market-dark-red">{{ marketValue.toFixed(1) }}</div>
        </div>
      </div>
    </div>

    <div class="relative flex flex-1 flex-col overflow-hidden rounded-lg border border-primary/20 bg-bg-card p-5">
      <div class="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-bl-full bg-primary/5 blur-2xl"></div>
      <div class="mb-3 flex items-center gap-2 border-b border-primary/10 pb-2">
        <span class="material-symbols-outlined text-xl text-primary">psychology</span>
        <h3 class="text-base font-bold text-white">AI 分析洞察</h3>
      </div>
      <div class="custom-scrollbar flex-1 overflow-y-auto pr-1">
        <p class="text-sm font-light leading-7 text-text-light">
          综合当前事理折叠流分析，该资产正处于多空博弈的关键窗口期。<br /><br />
          <span class="font-medium text-primary">主要矛盾：</span>{{ contradiction }}<br /><br />
          <span class="font-medium text-primary">操作建议：</span>{{ strategy }}<br /><br />
          <span class="font-medium text-primary">当前焦点节点：</span>{{ selectedNodeLabel }}，{{ selectedNodeDescription }}
        </p>
      </div>
      <div class="mt-4 flex items-center justify-end border-t border-primary/10 pt-3 text-xs font-mono text-text-sub/60">
        基于 {{ nodeCount }} 个逻辑节点 + {{ insightCount }} 条洞察
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { IntervalKey } from '@/composables/useAssetMonitor'

defineProps<{
  activeInterval: IntervalKey
  linePath: string
  areaPath: string
  marketValue: number
  contradiction: string
  strategy: string
  selectedNodeLabel: string
  selectedNodeDescription: string
  nodeCount: number
  insightCount: number
}>()
</script>

<style scoped>
.chart-grid-line {
  stroke: #333;
  stroke-dasharray: 2 2;
}

.chart-path {
  fill: none;
  stroke: #9b1c1c;
  stroke-width: 2;
  filter: drop-shadow(0 4px 6px rgba(155, 28, 28, 0.3));
}

.chart-area {
  fill: url(#gradientDarkRedAsset);
}
</style>

<template>
  <aside class="custom-scrollbar flex w-72 shrink-0 flex-col overflow-y-auto border-r border-primary/10 bg-bg-card">
    <div class="border-b border-primary/10 p-4">
      <h2 class="mb-3 flex items-center gap-2 text-sm font-bold text-primary">
        <span class="material-symbols-outlined text-lg">visibility</span>
        我的监控
      </h2>

      <div class="relative">
        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <span class="material-symbols-outlined text-sm text-text-sub">search</span>
        </div>
        <input
          :value="searchQuery"
          class="block w-full rounded border border-primary/20 bg-bg-main py-2 pl-9 pr-9 text-sm text-white placeholder:text-text-sub/60 focus:border-primary/60 focus:outline-none focus:ring-1 focus:ring-primary/60"
          placeholder="搜索/添加代码"
          type="text"
          @input="$emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
          @keydown.enter.prevent="$emit('addFromSearch')"
        />
        <button
          class="absolute inset-y-0 right-0 flex items-center pr-2 text-text-sub transition-colors hover:text-white"
          title="添加股票"
          @click="$emit('addFromSearch')"
        >
          <span class="material-symbols-outlined text-base">add</span>
        </button>
      </div>

      <div
        v-if="searchQuery.trim() && matchedStocks.length > 0"
        class="custom-scrollbar mt-2 max-h-36 overflow-y-auto rounded border border-primary/20 bg-[#10151d]"
      >
        <button
          v-for="item in matchedStocks"
          :key="`candidate-${item.code}`"
          class="flex w-full items-center justify-between border-b border-primary/5 px-3 py-2 text-left last:border-b-0 hover:bg-primary/10"
          @click="$emit('addCandidate', item)"
        >
          <span class="truncate text-xs text-white">{{ item.name }}</span>
          <span class="ml-2 shrink-0 text-[10px] font-mono text-text-sub">{{ item.displayCode }}</span>
        </button>
      </div>
    </div>

    <div class="custom-scrollbar flex-1 space-y-1 overflow-y-auto p-2">
      <div
        v-for="item in watchlist"
        :key="item.code"
        class="group relative flex cursor-pointer items-center justify-between overflow-hidden rounded border p-3 transition-all"
        :class="
          activeStockCode === item.code
            ? 'border-primary/40 bg-primary/10'
            : 'border-primary/5 bg-bg-main hover:border-primary/30 hover:bg-bg-card'
        "
        @click="$emit('update:activeStockCode', item.code)"
      >
        <div
          v-if="activeStockCode === item.code"
          class="pointer-events-none absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent"
        ></div>
        <div class="relative z-10 min-w-0">
          <div class="truncate text-sm font-bold" :class="activeStockCode === item.code ? 'text-primary' : 'text-white'">
            {{ item.name }}
          </div>
          <div class="text-[10px] font-mono" :class="activeStockCode === item.code ? 'text-primary/70' : 'text-text-sub'">
            {{ item.displayCode }}
          </div>
        </div>
        <button
          class="relative z-10 p-1 text-text-sub opacity-0 transition-all hover:text-market-red group-hover:opacity-100"
          title="移除"
          @click.stop="$emit('removeStock', item.code)"
        >
          <span class="material-symbols-outlined text-base">delete</span>
        </button>
      </div>
    </div>

    <div class="border-t border-primary/10 bg-black/20 p-4">
      <div class="mb-3 flex items-center justify-between">
        <div class="flex items-center gap-1.5 text-xs font-semibold text-primary">
          <span class="material-symbols-outlined text-sm">notifications_active</span>
          预警阈值设置
        </div>
        <label class="relative inline-flex cursor-pointer items-center" title="微信推送开关">
          <input
            class="peer sr-only"
            type="checkbox"
            :checked="notificationsEnabled"
            @change="$emit('update:notificationsEnabled', ($event.target as HTMLInputElement).checked)"
          />
          <div
            class="h-4 w-7 rounded-full bg-gray-700 after:absolute after:left-[2px] after:top-[2px] after:h-3 after:w-3 after:rounded-full after:border after:border-gray-300 after:bg-white after:transition-all after:content-[''] peer-checked:bg-market-green peer-checked:after:translate-x-full peer-checked:after:border-white"
          ></div>
        </label>
      </div>

      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-[11px] text-text-sub">指数变动阈值</span>
          <div class="relative flex items-center gap-1">
            <input
              class="w-12 rounded border border-primary/20 bg-bg-main px-1.5 py-1 text-right text-[11px] text-white outline-none focus:border-primary"
              type="number"
              :value="thresholdIndexMove"
              @input="$emit('update:thresholdIndexMove', Number(($event.target as HTMLInputElement).value || 0))"
            />
            <span class="absolute right-[-14px] text-[10px] text-text-sub">%</span>
          </div>
        </div>
        <div class="flex items-center justify-between">
          <span class="text-[11px] text-text-sub">叙事规模增长</span>
          <div class="relative flex items-center gap-1">
            <input
              class="w-12 rounded border border-primary/20 bg-bg-main px-1.5 py-1 text-right text-[11px] text-white outline-none focus:border-primary"
              type="number"
              :value="thresholdNarrativeGrowth"
              @input="$emit('update:thresholdNarrativeGrowth', Number(($event.target as HTMLInputElement).value || 0))"
            />
            <span class="absolute right-[-14px] text-[10px] text-text-sub">%</span>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import type { WatchItem } from '@/composables/useAssetMonitor'

defineProps<{
  searchQuery: string
  matchedStocks: WatchItem[]
  watchlist: WatchItem[]
  activeStockCode: string
  notificationsEnabled: boolean
  thresholdIndexMove: number
  thresholdNarrativeGrowth: number
}>()

defineEmits<{
  (e: 'update:searchQuery', value: string): void
  (e: 'addFromSearch'): void
  (e: 'addCandidate', value: WatchItem): void
  (e: 'update:activeStockCode', value: string): void
  (e: 'removeStock', value: string): void
  (e: 'update:notificationsEnabled', value: boolean): void
  (e: 'update:thresholdIndexMove', value: number): void
  (e: 'update:thresholdNarrativeGrowth', value: number): void
}>()
</script>

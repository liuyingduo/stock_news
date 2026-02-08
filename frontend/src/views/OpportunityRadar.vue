<template>
  <div class="bg-background-dark text-gray-300 font-sans h-screen w-full overflow-hidden flex antialiased selection:bg-logic-gold selection:text-black">
    <aside class="w-16 lg:w-64 border-r border-white/5 bg-[#0b0e12] flex flex-col shrink-0 z-50">
      <div class="h-16 flex items-center justify-center lg:justify-start lg:px-6 border-b border-white/5 shrink-0">
        <div class="flex items-center gap-3">
          <div class="flex h-8 w-8 items-center justify-center rounded-full bg-logic-gold/10 border border-logic-gold/30 shadow-glow-gold shrink-0">
            <span class="material-symbols-outlined text-logic-gold text-xl">language</span>
          </div>
          <span class="hidden lg:block text-base font-bold tracking-tight text-white font-sans">万古经纬</span>
        </div>
      </div>
      <div class="flex-1 overflow-y-auto py-6 px-2 lg:px-4 space-y-8">
        <div>
          <button class="w-full flex items-center gap-3 px-3 py-3 rounded-lg bg-surface-lighter text-logic-gold border border-logic-gold/30 shadow-[0_0_15px_rgba(212,175,55,0.1)] transition-all group relative overflow-hidden hover:bg-surface-lighter/80">
            <div class="absolute left-0 top-0 bottom-0 w-1 bg-logic-gold"></div>
            <span class="material-symbols-outlined shrink-0">restart_alt</span>
            <span class="hidden lg:block text-sm font-bold">默认 (全部事件)</span>
          </button>
        </div>
        <div class="space-y-3">
          <div class="hidden lg:flex px-3 items-center justify-between">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider font-mono">指数倾向</h3>
            <span class="text-[10px] text-gray-600 bg-white/5 px-1.5 py-0.5 rounded">单选互斥</span>
          </div>
          <div class="space-y-1">
            <button
              class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group"
              :class="sideFilterButtonClass(directionFilter === 'all')"
              @click="setDirectionFilter('all')"
            >
              <span class="material-symbols-outlined text-[20px] shrink-0">all_inclusive</span>
              <span class="hidden lg:block text-sm">全部信号</span>
            </button>
            <label class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-white/5 cursor-pointer group transition-colors">
              <input
                class="custom-checkbox rounded border-white/10 bg-white/5 focus:ring-0 focus:ring-offset-0 w-4 h-4 transition-all shrink-0"
                type="checkbox"
                :checked="directionFilter === 'opportunity'"
                @change="toggleDirectionFilter('opportunity')"
              />
              <span class="hidden lg:flex items-center text-sm group-hover:text-logic-gold transition-colors">
                捕捉机会
                <span class="text-xs text-market-up ml-2 font-mono font-bold bg-market-up/10 px-1 rounded">&gt;70</span>
              </span>
            </label>
            <label class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-white/5 cursor-pointer group transition-colors">
              <input
                class="custom-checkbox rounded border-white/10 bg-white/5 focus:ring-0 focus:ring-offset-0 w-4 h-4 transition-all shrink-0"
                type="checkbox"
                :checked="directionFilter === 'risk'"
                @change="toggleDirectionFilter('risk')"
              />
              <span class="hidden lg:flex items-center text-sm group-hover:text-logic-gold transition-colors">
                规避风险
                <span class="text-xs text-market-down ml-2 font-mono font-bold bg-market-down/10 px-1 rounded">&lt;70</span>
              </span>
            </label>
          </div>
        </div>
        <div class="space-y-3 pt-6 border-t border-white/5">
          <div class="hidden lg:flex px-3 items-center justify-between">
            <h3 class="text-xs font-bold text-gray-500 uppercase tracking-wider font-mono">情报鲜度</h3>
          </div>
          <div class="space-y-1">
            <button
              class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors group"
              :class="sideFilterButtonClass(freshnessFilter === 'all')"
              @click="setFreshnessFilter('all')"
            >
              <span class="material-symbols-outlined text-[20px] shrink-0">all_inclusive</span>
              <span class="hidden lg:block text-sm">全部信号</span>
            </button>
            <label class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-white/5 cursor-pointer group transition-colors">
              <input
                class="custom-checkbox rounded border-white/10 bg-white/5 focus:ring-0 focus:ring-offset-0 w-4 h-4 transition-all shrink-0"
                type="checkbox"
                :checked="freshnessFilter === 'first'"
                @change="toggleFreshnessFilter('first')"
              />
              <span class="hidden lg:block text-sm group-hover:text-logic-gold transition-colors">首发新闻</span>
            </label>
            <label class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-gray-300 hover:bg-white/5 cursor-pointer group transition-colors">
              <input
                class="custom-checkbox rounded border-white/10 bg-white/5 focus:ring-0 focus:ring-offset-0 w-4 h-4 transition-all shrink-0"
                type="checkbox"
                :checked="freshnessFilter === 'relay'"
                @change="toggleFreshnessFilter('relay')"
              />
              <span class="hidden lg:block text-sm group-hover:text-logic-gold transition-colors">逻辑接力</span>
            </label>
          </div>
        </div>

        <div class="space-y-3 pt-6 border-t border-white/10 mt-6 lg:mt-8">
          <div class="hidden lg:flex px-3 items-center justify-between">
            <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wider font-mono">市场先生指数 TOP 5</h3>
          </div>
          <div class="space-y-0.5 font-mono text-sm hidden lg:block">
            <div
              v-for="item in marketTopFive"
              :key="item.label"
              class="flex items-center justify-between px-3 py-2 rounded hover:bg-white/5 transition-colors cursor-pointer group"
            >
              <div class="flex items-center gap-3 min-w-0">
                <span class="font-bold w-3 shrink-0" :class="item.rank <= 3 ? 'text-logic-gold' : 'text-gray-500'">{{ item.rank }}</span>
                <span class="text-gray-300 group-hover:text-white transition-colors truncate">{{ item.label }}</span>
              </div>
              <span class="font-bold shrink-0" :class="item.score >= 0 ? 'text-market-up' : 'text-market-down'">{{ item.scoreText }}</span>
            </div>
            <div v-if="marketTopFive.length === 0" class="px-3 py-2 text-xs text-gray-500">
              暂无可用数据
            </div>
          </div>
        </div>
      </div>
    </aside>

    <main class="flex-1 flex flex-col min-w-0 bg-background-dark relative">
      <div class="absolute inset-0 grid-pattern opacity-[0.03] pointer-events-none"></div>
      <AppHeader />

      <div class="flex-1 overflow-y-auto p-4 lg:p-8 space-y-6 scroll-smooth">
        <div class="grid grid-cols-1 xl:grid-cols-12 gap-6">
          <div class="xl:col-span-8 bg-surface-dark border border-white/5 rounded-2xl p-1 relative overflow-hidden group shadow-lg h-full">
            <div class="absolute top-0 right-0 p-4 opacity-50">
              <span class="material-symbols-outlined text-[120px] text-white/[0.02]">speed</span>
            </div>
            <div class="bg-surface-lighter/30 rounded-xl p-6 h-full border border-white/5 backdrop-blur-sm relative z-10 flex flex-col">
              <div class="flex justify-between items-start mb-2">
                <div>
                  <h2 class="text-base font-bold text-white flex items-center gap-2">
                    <span class="material-symbols-outlined text-logic-gold text-sm">network_node</span>
                    市场先生指数
                  </h2>
                  <p class="text-xs text-gray-500 mt-1 font-mono uppercase">Mr. Market Index</p>
                </div>
                <div class="flex gap-2">
                  <button class="px-3 py-1 text-xs rounded transition-colors" :class="timeButtonClass('1H')" :disabled="loading" @click="changeTimeWindow('1H')">1H</button>
                  <button class="px-3 py-1 text-xs rounded transition-colors" :class="timeButtonClass('4H')" :disabled="loading" @click="changeTimeWindow('4H')">4H</button>
                  <button class="px-3 py-1 text-xs rounded transition-colors" :class="timeButtonClass('1D')" :disabled="loading" @click="changeTimeWindow('1D')">1D</button>
                </div>
              </div>
              <div class="flex-1 flex flex-col lg:flex-row items-center justify-center gap-8 py-6">
                <div class="relative w-64 h-32 lg:w-80 lg:h-40 shrink-0 flex justify-center">
                  <div class="absolute top-[90%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-48 h-48 bg-logic-gold/5 rounded-full blur-3xl pointer-events-none animate-[pulse_4s_infinite]"></div>
                  <div class="absolute top-[90%] left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 bg-logic-gold/10 rounded-full blur-2xl pointer-events-none"></div>
                  <svg class="w-full h-full overflow-visible z-10" viewBox="0 0 200 110">
                    <path d="M 10 100 A 90 90 0 0 1 190 100" fill="none" stroke="#1f2937" stroke-linecap="round" stroke-width="8"></path>
                    <path class="drop-shadow-[0_0_10px_rgba(255,77,77,0.5)]" d="M 10 100 A 90 90 0 0 1 190 100" fill="none" stroke="url(#spectrumGradient)" stroke-dasharray="283" stroke-dashoffset="0" stroke-linecap="round" stroke-width="8">
                      <animate attributeName="stroke-dashoffset" dur="1.5s" fill="freeze" from="283" to="31"></animate>
                    </path>
                    <g class="text-gray-500 font-mono text-[8px] font-bold select-none opacity-50">
                      <text text-anchor="middle" x="10" y="115">-100</text>
                      <text text-anchor="middle" x="100" y="5">0</text>
                      <text text-anchor="middle" x="190" y="115">100</text>
                    </g>
                    <defs>
                      <linearGradient id="spectrumGradient" x1="0%" x2="100%" y1="0%" y2="0%">
                        <stop offset="0%" stop-color="#00e676"></stop>
                        <stop offset="30%" stop-color="#115e59"></stop>
                        <stop offset="50%" stop-color="#64748b"></stop>
                        <stop offset="70%" stop-color="#f87171"></stop>
                        <stop offset="100%" stop-color="#ff4d4d"></stop>
                      </linearGradient>
                    </defs>
                  </svg>
                  <div class="absolute bottom-0 left-1/2 -translate-x-1/2 translate-y-6 text-center z-20 pointer-events-none flex flex-col items-center">
                    <div class="relative">
                      <span class="text-5xl font-bold font-mono text-white text-glow leading-none tracking-tighter drop-shadow-lg">{{ marketView.value }}</span>
                      <span class="absolute -top-3 -right-14 text-sm font-bold font-mono px-1.5 py-0.5 rounded border" :class="marketView.deltaClass">{{ marketView.deltaText }}</span>
                    </div>
                    <div class="mt-2 px-3 py-1 rounded-full border backdrop-blur-sm" :class="marketView.trendBadgeClass">
                      <span class="text-xs font-bold uppercase tracking-wider" :class="marketView.trendTextClass">{{ marketView.trendText }}</span>
                    </div>
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-x-12 gap-y-8 w-full lg:w-auto mt-10 lg:mt-0">
                  <div v-for="metric in marketMetrics" :key="metric.label" class="flex flex-col items-center lg:items-start">
                    <p class="text-xs text-gray-500 mb-1">{{ metric.label }}</p>
                    <div class="flex flex-col items-center lg:items-start">
                      <span class="text-2xl font-mono font-bold" :class="metric.valueClass">{{ metric.value }}</span>
                      <span class="text-xs font-mono flex items-center gap-1 mt-1" :class="metric.delta >= 0 ? 'text-market-up' : 'text-market-down'">
                        <span class="material-symbols-outlined text-[14px]">{{ metric.delta >= 0 ? 'arrow_upward' : 'arrow_downward' }}</span>
                        {{ formatDeltaText(metric.delta) }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="xl:col-span-4 flex flex-col gap-6 h-full">
            <div class="bg-surface-dark border border-market-up/30 rounded-xl p-6 relative overflow-hidden shadow-glow-red flex-1 flex flex-col">
              <div class="absolute -right-4 -top-4 w-24 h-24 bg-market-up/5 rounded-full blur-2xl"></div>
              <div class="flex justify-between items-center mb-4 relative z-10">
                <h3 class="text-sm font-bold text-market-up flex items-center gap-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-market-up animate-[pulse_3s_infinite]"></span>
                  机会提示
                </h3>
                <span class="text-xs text-gray-500 font-mono">共 {{ opportunityCard.total }} 条事件</span>
              </div>
              <div class="flex-1 flex flex-col justify-center relative z-10">
                <div class="bg-market-up/5 border border-market-up/10 rounded-lg p-3 group hover:bg-market-up/10 transition-colors cursor-pointer">
                  <div class="flex justify-between items-start mb-1.5">
                    <span class="text-xs font-bold text-market-up group-hover:text-white transition-colors">{{ opportunityCard.title }}</span>
                    <span class="text-[10px] font-mono text-gray-500">{{ opportunityCard.time }}</span>
                  </div>
                  <p class="text-[10px] text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors">{{ opportunityCard.content }}</p>
                </div>
              </div>
            </div>

            <div class="bg-surface-dark border border-market-down/30 rounded-xl p-6 relative overflow-hidden shadow-glow-green flex-1 flex flex-col">
              <div class="flex justify-between items-center mb-4">
                <h3 class="text-sm font-bold text-market-down flex items-center gap-2">
                  <span class="w-1.5 h-1.5 rounded-full bg-market-down animate-pulse"></span>
                  风险预警
                </h3>
                <span class="text-xs text-gray-500 font-mono">共 {{ riskCard.total }} 条事件</span>
              </div>
              <div class="flex-1 flex flex-col justify-center">
                <div class="bg-market-down/5 border border-market-down/10 rounded-lg p-3 hover:bg-market-down/10 transition-colors cursor-pointer group">
                  <div class="flex justify-between items-start mb-1.5">
                    <span class="text-xs font-bold text-market-down group-hover:text-white transition-colors">{{ riskCard.title }}</span>
                    <span class="text-[10px] font-mono text-gray-500">{{ riskCard.time }}</span>
                  </div>
                  <p class="text-[10px] text-gray-400 leading-relaxed group-hover:text-gray-300 transition-colors">{{ riskCard.content }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div ref="topEventsTableRef">
          <RadarTopEventsTable
            :loading="loading"
            :top-event-rows="topEventRows"
            :top-event-detail="topEventDetail"
            :top-events-button-text="topEventsButtonText"
            :top-events-expanded="topEventsExpanded"
            @toggle="onToggleTopEvents"
          />
        </div>
        <footer class="flex justify-between items-center text-[10px] text-gray-600 font-mono pt-4 pb-8 px-6 lg:px-0">
          <div class="flex items-center gap-4">
            <span>万古终端 User_01</span>
            <span class="px-1.5 py-0.5 rounded bg-white/5 border border-white/5 text-[9px] text-logic-gold">PRO</span>
          </div>
          <div class="flex gap-4">
            <span>DATA SOURCE: REUTERS / BLOOMBERG / INTERNAL NLP</span>
            <span>SERVER: HK-01</span>
          </div>
        </footer>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'
import AppHeader from '@/components/common/AppHeader.vue'
import RadarTopEventsTable from '@/components/opportunity-radar/RadarTopEventsTable.vue'
import { useOpportunityRadar } from '@/composables/useOpportunityRadar'

const topEventsTableRef = ref<HTMLElement | null>(null)

const {
  loading,
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
} = useOpportunityRadar()

async function onToggleTopEvents(): Promise<void> {
  const wasExpanded = toggleTopEventsExpanded()
  if (!wasExpanded) return
  await nextTick()
  topEventsTableRef.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

onMounted(async () => {
  try {
    await init()
  } catch (error) {
    console.error('Failed to initialize opportunity radar page:', error)
  }
})
</script>

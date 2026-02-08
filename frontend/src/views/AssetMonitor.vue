<template>
  <div class="flex flex-col h-screen overflow-hidden bg-bg-main text-white selection:bg-primary selection:text-bg-main font-body">
    <!-- Custom Header to match the specific design provided -->
    <AppHeader variant="compact" />

    <div class="flex flex-1 overflow-hidden">
      <!-- Left Sidebar -->
      <aside class="w-72 bg-bg-card border-r border-primary/10 flex flex-col shrink-0 overflow-y-auto z-10 custom-scrollbar">
        <div class="p-4 border-b border-primary/10">
          <h2 class="text-primary font-bold text-sm flex items-center gap-2 mb-3">
            <span class="material-symbols-outlined text-lg">visibility</span>
            我的监控
          </h2>
          <div class="relative group">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span class="material-symbols-outlined text-text-sub text-sm group-focus-within:text-primary transition-colors">search</span>
            </div>
            <input 
              v-model="searchQuery"
              class="block w-full pl-9 pr-8 py-2 border border-primary/20 rounded bg-bg-main text-sm placeholder-text-sub/50 focus:outline-none focus:border-primary/60 focus:ring-1 focus:ring-primary/60 transition-all text-white font-mono" 
              placeholder="搜索/添加代码" 
              type="text"
            />
            <div class="absolute inset-y-0 right-0 pr-2 flex items-center cursor-pointer hover:text-white text-text-sub">
              <span class="material-symbols-outlined text-sm">add</span>
            </div>
          </div>
        </div>
        
        <div class="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
          <!-- Monitor List Items -->
          <div 
            v-for="(item, index) in monitorList" 
            :key="index"
            class="group flex items-center justify-between p-3 rounded border transition-all cursor-pointer relative overflow-hidden"
            :class="[
              activeStock === item.code 
                ? 'bg-primary/10 border-primary/40' 
                : 'bg-bg-main border-primary/5 hover:border-primary/30 hover:bg-bg-card'
            ]"
            @click="activeStock = item.code"
          >
            <div v-if="activeStock === item.code" class="absolute inset-0 bg-gradient-to-r from-primary/5 to-transparent pointer-events-none"></div>
            <div class="relative z-10">
              <div class="text-sm font-bold" :class="activeStock === item.code ? 'text-primary' : 'text-white'">{{ item.name }}</div>
              <div class="text-[10px] font-mono" :class="activeStock === item.code ? 'text-primary/70' : 'text-text-sub'">{{ item.code }}</div>
            </div>
            <button class="relative z-10 text-text-sub hover:text-market-red transition-colors opacity-0 group-hover:opacity-100 p-1">
              <span class="material-symbols-outlined text-base">delete</span>
            </button>
          </div>
        </div>

        <div class="p-4 border-t border-primary/10 bg-black/20">
          <div class="flex items-center justify-between mb-3">
            <div class="text-xs font-semibold text-primary flex items-center gap-1.5">
              <span class="material-symbols-outlined text-sm">notifications_active</span>
              预警阈值设置
            </div>
            <label class="relative inline-flex items-center cursor-pointer" title="微信推送开关">
              <input v-model="notificationsEnabled" class="sr-only peer" type="checkbox" />
              <div class="w-7 h-4 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-3 after:w-3 after:transition-all peer-checked:bg-market-green"></div>
            </label>
          </div>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-[11px] text-text-sub">指数变动阈值</span>
              <div class="flex items-center gap-1 relative">
                <input class="w-12 bg-bg-main border border-primary/20 rounded px-1.5 py-1 text-[11px] text-right text-white focus:border-primary outline-none font-mono" type="text" value="20"/>
                <span class="text-[10px] text-text-sub absolute right-[-14px]">%</span>
              </div>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-[11px] text-text-sub">叙事规模增长</span>
              <div class="flex items-center gap-1 relative">
                <input class="w-12 bg-bg-main border border-primary/20 rounded px-1.5 py-1 text-[11px] text-right text-white focus:border-primary outline-none font-mono" type="text" value="300"/>
                <span class="text-[10px] text-text-sub absolute right-[-14px]">%</span>
              </div>
            </div>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 flex flex-col min-w-0 overflow-hidden relative bg-[#0F1319]">
        <!-- Dashboard Top Section -->
        <section class="p-6 pb-2 border-b border-primary/10 bg-bg-card/50 shrink-0">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-4">
              <h2 class="text-lg font-bold text-white tracking-wide flex items-center gap-2">
                <span class="material-symbols-outlined text-primary">thermostat</span>
                资产逻辑气压计
              </h2>
              <div class="flex items-center bg-bg-main rounded border border-primary/20 p-0.5">
                <button 
                  v-for="time in timeIntervals" 
                  :key="time"
                  @click="activeInterval = time"
                  class="px-3 py-0.5 text-xs rounded-sm transition-colors border"
                  :class="[
                    activeInterval === time 
                      ? 'font-bold bg-primary/20 text-primary border-primary/20 shadow-glow' 
                      : 'font-medium text-text-sub hover:text-primary border-transparent'
                  ]"
                >
                  {{ time }}
                </button>
              </div>
            </div>
            <span class="text-xs text-text-sub font-mono">最后更新: 14:32:05</span>
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
            <!-- Mr. Market Index Card -->
            <div class="relative p-4 rounded-lg bg-gradient-to-br from-bg-card to-black border border-primary/20 flex flex-col justify-between overflow-hidden group min-h-[90px]">
              <div class="absolute top-0 right-0 p-2 opacity-10 group-hover:opacity-20 transition-opacity">
                <span class="material-symbols-outlined text-5xl">sentiment_satisfied</span>
              </div>
              <div class="text-xs text-text-sub font-medium mb-2 flex items-center gap-1">
                市场先生指数
                <span class="material-symbols-outlined text-[10px] text-text-sub/60">info</span>
              </div>
              <div class="flex items-end gap-2 mt-auto">
                <span class="text-2xl font-bold text-market-red text-glow font-mono">78.4</span>
                <div class="text-xs text-market-red font-medium font-mono mb-1 bg-market-red/10 px-1 py-0.5 rounded flex items-center">
                  <span class="material-symbols-outlined text-[10px] mr-0.5">arrow_upward</span>
                  +2.3%
                </div>
              </div>
            </div>

            <!-- Other Metrics -->
            <div class="p-4 rounded-lg bg-bg-card border border-primary/10 flex flex-col justify-between hover:border-primary/30 transition-colors min-h-[90px]">
              <div class="flex items-start justify-between mb-2">
                <span class="text-xs text-text-sub font-medium">叙事规模</span>
              </div>
              <div class="flex items-end gap-2 mt-auto">
                <span class="text-xl font-bold text-white font-mono">128</span>
                <div class="text-xs text-market-red font-medium font-mono mb-1 flex items-center">
                  <span class="material-symbols-outlined text-[10px] mr-0.5">arrow_upward</span>
                  +15.0%
                </div>
              </div>
            </div>

            <div class="p-4 rounded-lg bg-bg-card border border-primary/10 flex flex-col justify-between hover:border-primary/30 transition-colors min-h-[90px]">
              <div class="flex items-start justify-between mb-2">
                <span class="text-xs text-text-sub font-medium">影响力</span>
              </div>
              <div class="flex items-end gap-2 mt-auto">
                <span class="text-xl font-bold text-white font-mono">85.0</span>
                <div class="text-xs text-market-red font-medium font-mono mb-1 flex items-center">
                  <span class="material-symbols-outlined text-[10px] mr-0.5">arrow_upward</span>
                  +5.2%
                </div>
              </div>
            </div>

            <div class="p-4 rounded-lg bg-bg-card border border-primary/10 flex flex-col justify-between hover:border-primary/30 transition-colors min-h-[90px]">
              <div class="flex items-start justify-between mb-2">
                <span class="text-xs text-text-sub font-medium">多空信号</span>
              </div>
              <div class="flex items-end gap-2 mt-auto">
                <span class="text-xl font-bold text-market-red font-mono">0.8</span>
                <div class="text-xs text-market-green font-medium font-mono mb-1 flex items-center">
                  <span class="material-symbols-outlined text-[10px] mr-0.5">arrow_downward</span>
                  -12.5%
                </div>
              </div>
            </div>

            <div class="p-4 rounded-lg bg-bg-card border border-primary/10 flex flex-col justify-between hover:border-primary/30 transition-colors min-h-[90px]">
              <div class="flex items-start justify-between mb-2">
                <span class="text-xs text-text-sub font-medium">置信度</span>
              </div>
              <div class="flex items-end gap-2 mt-auto">
                <span class="text-xl font-bold text-white font-mono">92%</span>
                <div class="text-xs text-market-red font-medium font-mono mb-1 flex items-center">
                  <span class="material-symbols-outlined text-[10px] mr-0.5">arrow_upward</span>
                  +3.0%
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Main Content Area -->
        <section class="flex-1 flex flex-col min-h-0">
          <div class="px-6 pt-4 flex items-center gap-1 shrink-0 border-b border-primary/20">
            <button 
              v-for="tab in mainTabs" 
              :key="tab.key"
              @click="activeMainTab = tab.key"
              :class="[
                activeMainTab === tab.key
                  ? 'px-5 py-2.5 text-sm font-bold text-white bg-bg-card border-t border-l border-r border-primary/20 rounded-t-lg relative'
                  : 'px-5 py-2.5 text-sm font-medium text-text-sub hover:text-white transition-colors relative group'
              ]"
            >
              <span v-if="activeMainTab === tab.key" class="absolute top-0 left-0 w-full h-[2px] bg-primary shadow-glow"></span>
              {{ tab.label }}
              <span v-if="activeMainTab !== tab.key" class="absolute bottom-[-1px] left-1/2 -translate-x-1/2 w-0 h-[2px] bg-primary transition-all group-hover:w-8"></span>
            </button>
          </div>

          <div class="flex flex-1 overflow-hidden p-6 gap-6">
            <!-- Left Column: Insights List -->
            <div class="w-[60%] flex flex-col overflow-y-auto space-y-3 pr-2 pb-10 custom-scrollbar">
              <div class="bg-bg-card border border-primary/20 rounded-lg overflow-hidden group hover:border-primary/50 transition-all shadow-lg shadow-black/30">
                <div class="px-5 py-3 flex items-center justify-between border-b border-primary/10 cursor-pointer bg-bg-card/50">
                  <div class="flex items-center gap-3">
                    <h3 class="text-base font-bold text-white tracking-wide">毛利收缩风险</h3>
                    <span class="text-sm font-medium text-market-green">利空</span>
                  </div>
                  <div class="flex items-center gap-6 text-xs text-text-sub font-mono">
                    <span class="hover:text-primary transition-colors">置信度 88%</span>
                    <span class="hover:text-primary transition-colors">12条信源</span>
                  </div>
                </div>
                <div class="px-5 py-3 relative">
                  <div class="w-1 absolute left-0 top-0 bottom-0 bg-market-green/80"></div>
                  <p class="text-sm text-text-light font-medium leading-relaxed">
                    原材料锂矿供给过剩虽降低成本，但下游整车厂商强势压价，预计Q3毛利率将承压下行3-5个百分点
                  </p>
                </div>
                <!-- Expanded Info -->
                <div class="bg-black/20 px-5 py-3 border-t border-primary/5">
                  <div class="space-y-3">
                    <div class="flex items-start gap-3 group/item py-0.5">
                      <span class="w-1 h-1 rounded-full bg-primary/40 group-hover/item:bg-primary transition-colors mt-1.5 shrink-0"></span>
                      <div class="flex-1 min-w-0 flex items-start justify-between gap-4">
                        <div class="text-xs text-text-sub hover:text-text-light transition-colors cursor-pointer truncate">
                          <span class="text-primary/60 mr-1">[研报]</span>
                          中信证券：动力电池行业中期策略报告——产能出清与价格博弈
                        </div>
                        <div class="text-[10px] text-text-sub/40 font-mono mt-0.5 whitespace-nowrap">14:30:25</div>
                      </div>
                    </div>
                  </div>
                  <div class="mt-3 pt-2 border-t border-primary/5 text-center">
                    <button class="text-xs text-primary hover:text-white transition-colors flex items-center justify-center w-full py-1">
                      查看全部 12 条信息
                      <span class="material-symbols-outlined text-sm ml-1">expand_more</span>
                    </button>
                  </div>
                </div>
              </div>

              <!-- More items... (Simplified for now, reused logic in real app) -->
               <div class="bg-bg-card border border-primary/10 rounded-lg overflow-hidden group hover:border-primary/40 transition-all">
                <div class="px-5 py-3 flex items-center justify-between cursor-pointer">
                  <div class="flex items-center gap-3">
                    <h3 class="text-base font-bold text-white tracking-wide">海外建厂利好</h3>
                    <span class="text-sm font-medium text-market-red">利好</span>
                  </div>
                  <div class="flex items-center gap-6 text-xs text-text-sub font-mono">
                    <span class="hover:text-primary transition-colors">置信度 76%</span>
                    <span class="hover:text-primary transition-colors">8条信源</span>
                  </div>
                </div>
                <div class="px-5 py-3 relative">
                  <div class="w-1 absolute left-0 top-0 bottom-0 bg-market-red/80"></div>
                  <p class="text-sm text-text-light font-medium leading-relaxed">
                    匈牙利工厂项目获得欧盟环保许可，预计年底投产，将有效规避新的关税壁垒
                  </p>
                </div>
              </div>
            </div>

            <!-- Right Column: Charts & AI -->
            <div class="w-[40%] flex flex-col gap-4 overflow-y-auto pb-10 custom-scrollbar">
              <div class="bg-bg-card border border-primary/20 rounded-lg p-4 flex flex-col h-[280px]">
                <div class="flex items-center justify-between mb-2">
                  <h3 class="text-sm font-bold text-text-sub flex items-center gap-2">
                    <span class="material-symbols-outlined text-base">trending_up</span>
                    市场先生指数趋势图
                  </h3>
                  <div class="text-[10px] text-text-sub font-mono bg-bg-main px-2 py-0.5 rounded border border-primary/10">1H Interval</div>
                </div>
                <div class="flex-1 relative w-full h-full flex items-center justify-center bg-black/20 rounded border border-primary/5">
                   <svg class="w-full h-full p-2" preserveAspectRatio="none" viewBox="0 0 300 150">
                    <defs>
                      <linearGradient id="gradientDarkRed" x1="0%" x2="0%" y1="0%" y2="100%">
                        <stop offset="0%" style="stop-color:#9B1C1C;stop-opacity:0.25"></stop>
                        <stop offset="100%" style="stop-color:#9B1C1C;stop-opacity:0"></stop>
                      </linearGradient>
                    </defs>
                    <line class="chart-grid-line" x1="0" x2="300" y1="30" y2="30"></line>
                    <line class="chart-grid-line" x1="0" x2="300" y1="75" y2="75"></line>
                    <line class="chart-grid-line" x1="0" x2="300" y1="120" y2="120"></line>
                    <path class="chart-area" d="M0,120 L0,100 L30,90 L60,110 L90,80 L120,85 L150,60 L180,70 L210,40 L240,50 L270,30 L300,45 L300,150 L0,150 Z"></path>
                    <path class="chart-path" d="M0,100 L30,90 L60,110 L90,80 L120,85 L150,60 L180,70 L210,40 L240,50 L270,30 L300,45" fill="none"></path>
                  </svg>
                  <div class="absolute top-1/4 right-1/4 bg-bg-card border border-[#9B1C1C]/50 px-2 py-1 rounded shadow-lg backdrop-blur-sm bg-opacity-90">
                    <div class="text-xs text-[#9B1C1C] font-mono font-bold">78.4</div>
                  </div>
                </div>
              </div>

              <div class="bg-bg-card border border-primary/20 rounded-lg p-5 flex flex-col flex-1 relative overflow-hidden">
                <div class="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-bl-full -mr-8 -mt-8 blur-2xl pointer-events-none"></div>
                <div class="flex items-center gap-2 mb-3 border-b border-primary/10 pb-2">
                  <span class="material-symbols-outlined text-primary text-xl">psychology</span>
                  <h3 class="text-base font-bold text-white">AI 分析洞察</h3>
                </div>
                <div class="flex-1 overflow-y-auto pr-1 custom-scrollbar">
                  <p class="text-sm text-text-light leading-7 text-justify font-light">
                    综合当前事理折叠流分析，该资产正处于多空博弈的关键窗口期<br/><br/>
                    <span class="text-primary font-medium">主要矛盾：</span>虽然海外建厂进展顺利提供了中长期估值支撑，且短期汇率波动带来额外收益，但核心业务端受上游原材料价格下行引发的产业链降价潮影响显著，毛利率承压是当前市场最大的担忧来源<br/><br/>
                    <span class="text-primary font-medium">操作建议：</span>短期内市场先生指数高位震荡，波动率上升，建议维持中性观察。若股价回调至技术支撑位且叙事规模未出现恶化，可尝试分批低吸布局海外业务占比高的标的，规避纯国内供应链博弈风险
                  </p>
                </div>
                <div class="mt-4 pt-3 border-t border-primary/10 flex justify-end items-center text-xs text-text-sub/50 font-mono">
                  <span>基于28个逻辑节点</span>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AppHeader from '@/components/common/AppHeader.vue'

// State for reactivity
const searchQuery = ref('')
const notificationsEnabled = ref(true)
const activeInterval = ref('1H')
const activeMainTab = ref('logic')
const activeStock = ref('600519.SH')

// Constants
const timeIntervals = ['1H', '4H', '1D']
const mainTabs = [
  { key: 'logic', label: '逻辑洞察' },
  { key: 'relation', label: '关联图谱' }
]

const monitorList = [
  { name: '贵州茅台', code: '600519.SH' },
  { name: '宁德时代', code: '300750.SZ' },
  { name: '比亚迪', code: '002594.SZ' },
  { name: '中信证券', code: '600030.SH' }
]

</script>

<style scoped>
/* Specific styles for this page from the user provided HTML */
.text-glow {
  text-shadow: 0 0 20px rgba(245, 63, 63, 0.5);
}
.chart-grid-line {
  stroke: #333;
  stroke-dasharray: 2,2;
}
.chart-path {
  fill: none;
  stroke: #9B1C1C;
  stroke-width: 2;
  filter: drop-shadow(0 4px 6px rgba(155, 28, 28, 0.3));
}
.chart-area {
  fill: url(#gradientDarkRed);
}

/* Scrollbar overrides for this specific page theme */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: #0B0F15;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #2D333B;
  border-radius: 3px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #D4AF37;
}
</style>

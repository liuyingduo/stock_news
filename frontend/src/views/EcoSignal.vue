<template>
  <div class="ecosignal-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">智金通 EcoSignal AI</h1>
      <el-button @click="handleRefresh" :loading="store.loading" circle>
        <el-icon><Refresh /></el-icon>
      </el-button>
    </div>

    <!-- 三栏布局 -->
    <div class="ecosignal-container">
      <!-- 左侧栏：市场情绪仪表盘 -->
      <div class="left-panel">
        <SentimentGauge
          :average-sentiment="store.stats.averageSentiment"
          :average-impact="store.stats.averageImpact"
          :total-analyzed="store.stats.withAI"
        />

        <!-- 统计卡片 -->
        <div class="stat-cards">
          <div class="stat-card">
            <span class="stat-label">重磅预警</span>
            <span class="stat-value stat-alert">
              {{ store.stats.highImpactCount }}
            </span>
          </div>
          <div class="stat-card">
            <span class="stat-label">风险避雷</span>
            <span class="stat-value stat-risk">
              {{ store.stats.riskCount }}
            </span>
          </div>
          <div class="stat-card">
            <span class="stat-label">情绪炒作</span>
            <span class="stat-value stat-hype">
              {{ store.stats.hypeCount }}
            </span>
          </div>
        </div>

        <!-- 筛选器 -->
        <div class="filter-section">
          <h3 class="filter-title">筛选条件</h3>
          <el-select
            v-model="categoryFilter"
            placeholder="事件类别"
            clearable
            size="small"
            class="filter-select"
            @change="handleFilterChange"
          >
            <el-option label="全球大事" value="global_macro" />
            <el-option label="政策风向" value="policy" />
            <el-option label="行业动向" value="industry" />
            <el-option label="公司动态" value="company" />
          </el-select>

          <el-input
            v-model="searchFilter"
            placeholder="搜索..."
            clearable
            size="small"
            class="filter-input"
            @input="handleSearchInput"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
      </div>

      <!-- 中间栏：核心信号流 -->
      <div class="center-panel">
        <InfiniteScroll
          :items="store.events"
          :loading="store.loading"
          :has-more="store.hasMore"
          @load-more="handleLoadMore"
        >
          <template #default="{ items }">
            <SignalCard
              v-for="event in items"
              :key="event.id"
              :event="event"
              :class="{ 'is-active': selectedEvent?.id === event.id }"
              style="cursor: pointer"
              @click="selectedEvent = event"
            />
          </template>
        </InfiniteScroll>
      </div>

      <!-- 右侧栏：动态战术板 (Tactical Panel) -->
      <div class="right-panel">
        
        <!-- Mode A: 选中事件深度分析 -->
        <div v-if="selectedEvent" class="analysis-view">
          <div class="panel-header">
            <h3 class="panel-title">推演 (Analysis)</h3>
            <el-button link size="small" @click="selectedEvent = null">
              <el-icon><Close /></el-icon>
            </el-button>
          </div>
          
          <div class="reasoning-chain">
            <div class="chain-node source-node">
              <span class="node-label">EVENT</span>
              <div class="node-content">{{ selectedEvent.title }}</div>
            </div>
            <div class="chain-arrow">↓</div>
            <div class="chain-node logic-node">
              <span class="node-label">LOGIC</span>
              <div class="node-content">{{ selectedEvent.ai_analysis?.impact_reason || 'AI 分析中...' }}</div>
            </div>
            <div class="chain-arrow">↓</div>
            <div class="chain-node target-node">
              <span class="node-label">TARGETS</span>
              <div class="targets-grid">
                <el-tag 
                  v-for="stock in selectedEvent.ai_analysis?.affected_stocks || []" 
                  :key="stock.code" 
                  size="small" 
                  class="mb-1 mr-1"
                >
                  {{ stock.name }}
                </el-tag>
                 <el-tag 
                  v-for="sector in selectedEvent.ai_analysis?.affected_sectors || []" 
                  :key="sector.code" 
                  size="small" 
                  type="info"
                  class="mb-1 mr-1"
                >
                  {{ sector.name }}
                </el-tag>
              </div>
            </div>
          </div>

          <!-- Mock Pro/Con -->
          <div class="intro-box">
             <div class="intro-title">多空博弈 (AI Debate)</div>
             <p class="intro-text text-gray-400 text-xs">此处将展示 AI 针对该事件的多空观点辩论（开发中）...</p>
          </div>
        </div>

        <!-- Mode B: 默认预警列表 -->
        <div v-else class="alerts-view">
          <div class="alert-section">
            <h3 class="section-title section-alert">
              <span class="title-icon">🚨</span> 高分预警 Top 5
            </h3>
            <div class="alert-list">
              <div
                v-for="event in store.highImpactEvents.slice(0, 5)"
                :key="event.id"
                class="mini-card"
                @click="selectedEvent = event"
              >
                <div class="flex justify-between items-start">
                   <div class="mini-score text-red-500 font-bold">{{ ((event.ai_analysis?.impact_score || 0) * 10).toFixed(1) }}</div>
                   <div class="mini-time text-xs text-gray-500">{{ formatDate(event.announcement_date) }}</div>
                </div>
                <div class="mini-title text-sm mt-1 line-clamp-2 hover:text-blue-400 cursor-pointer">{{ event.title }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>


    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh, Search, Close } from '@element-plus/icons-vue'
import type { Event } from '../api/types'
import { formatDate } from '../utils/date'
import { useEcoSignalStore } from '../stores/ecoSignal'
import SentimentGauge from '../components/ecoSignal/SentimentGauge.vue'
import SignalCard from '../components/ecoSignal/SignalCard.vue'
import InfiniteScroll from '../components/common/InfiniteScroll.vue'
import { useDebounceFn } from '@vueuse/core'

const store = useEcoSignalStore()
const selectedEvent = ref<Event | null>(null)

// 筛选状态
const categoryFilter = ref<string>()
const searchFilter = ref('')

// 防抖搜索
const debouncedSearch = useDebounceFn(() => {
  store.applyFilters({
    category: categoryFilter.value,
    search: searchFilter.value || undefined,
  })
}, 500)

// 处理刷新
const handleRefresh = () => {
  store.refresh()
}

// 处理加载更多
const handleLoadMore = () => {
  store.loadMore()
}

// 处理筛选变化
const handleFilterChange = () => {
  debouncedSearch()
}

// 处理搜索输入
const handleSearchInput = () => {
  debouncedSearch()
}

// 初始化加载
onMounted(() => {
  store.loadEvents(true)
})
</script>

<style scoped>
.ecosignal-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary, #0f172a);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background: var(--bg-card, rgba(30, 41, 59, 0.5));
  border-bottom: 1px solid var(--border-primary, rgba(148, 163, 184, 0.1));
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary, #f1f5f9);
  margin: 0;
}

.ecosignal-container {
  display: grid;
  grid-template-columns: 300px 1fr 350px;
  gap: 24px;
  padding: 24px;
  flex: 1;
  overflow: hidden;
}

/* 左侧栏 */
.left-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  padding-right: 8px;
}

.stat-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.stat-card {
  background: var(--bg-card, rgba(30, 41, 59, 0.5));
  border: 1px solid var(--border-primary, rgba(148, 163, 184, 0.1));
  border-radius: 8px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 13px;
  color: var(--text-secondary, #94a3b8);
}

.stat-value {
  font-size: 20px;
  font-weight: 600;
}

.stat-alert {
  color: #ef4444;
}

.stat-risk {
  color: #22c55e;
}

.stat-hype {
  color: #f97316;
}

.filter-section {
  background: var(--bg-card, rgba(30, 41, 59, 0.5));
  border: 1px solid var(--border-primary, rgba(148, 163, 184, 0.1));
  border-radius: 8px;
  padding: 16px;
}

.filter-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary, #f1f5f9);
  margin: 0 0 12px 0;
}

.filter-select {
  width: 100%;
  margin-bottom: 12px;
}

.filter-input {
  width: 100%;
}

/* 中间栏 */
.center-panel {
  overflow: hidden;
  background: var(--bg-card, rgba(30, 41, 59, 0.5));
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.2s;
}

:deep(.signal-card.is-active) {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 1px var(--accent-primary);
  background: rgba(59, 130, 246, 0.05); /* Blue tint */
}

/* 右侧栏 */
.right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
  padding-left: 8px;
}

.alert-section,
.risk-section {
  background: var(--bg-card, rgba(30, 41, 59, 0.5));
  border: 1px solid var(--border-primary, rgba(148, 163, 184, 0.1));
  border-radius: 12px;
  padding: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  margin: 0 0 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.title-icon {
  font-size: 18px;
}

.section-alert {
  color: #ef4444;
}

.section-risk {
  color: #22c55e;
}

.alert-list,
.risk-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item,
.risk-item {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 8px;
  padding: 8px;
}

/* 右侧栏样式 */
.right-panel {
  display: flex;
  flex-direction: column;
  background: var(--bg-card);
  border-left: 1px solid var(--border-primary);
  border-radius: 8px;
  overflow-y: auto;
}

.padding-box { padding: 16px; }

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-primary);
}

.panel-title { font-size: 16px; font-weight: 600; margin: 0; }

.reasoning-chain {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chain-node {
  background: rgba(255, 255, 255, 0.03);
  padding: 12px;
  border-radius: 6px;
  border: 1px solid var(--border-primary);
}

.node-label {
  font-size: 10px;
  color: var(--text-muted);
  letter-spacing: 1px;
  display: block;
  margin-bottom: 4px;
}

.node-content { font-size: 14px; line-height: 1.5; }

.chain-arrow { text-align: center; color: var(--text-muted); font-size: 16px; }

/* Mini Cards */
.mini-card {
  padding: 12px;
  border-bottom: 1px solid var(--border-primary);
  transition: background 0.2s;
}
.mini-card:hover { background: rgba(255, 255, 255, 0.03); }

.alert-section { padding: 0; }
.section-title { padding: 16px; margin: 0; border-bottom: 1px solid var(--border-primary); font-size: 14px; }

.intro-box { padding: 20px; text-align: center; border-top: 1px dashed var(--border-primary); margin-top: 20px;}


/* 响应式布局 */
@media (max-width: 1024px) {
  .ecosignal-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr;
    overflow-y: auto;
  }

  .left-panel {
    overflow: visible;
  }

  .center-panel {
    min-height: 500px;
  }

  .stat-cards {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .ecosignal-container {
    padding: 16px;
    gap: 16px;
  }

  .page-title {
    font-size: 18px;
  }

  .stat-cards {
    grid-template-columns: 1fr;
  }
}
</style>

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
            <el-option label="全球大事" value="global_events" />
            <el-option label="政策风向" value="policy_trends" />
            <el-option label="行业动向" value="industry_trends" />
            <el-option label="公司动态" value="company_updates" />
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
            />
          </template>
        </InfiniteScroll>
      </div>

      <!-- 右侧栏：重磅预警 + 风险避雷 -->
      <div class="right-panel">
        <!-- 重磅预警 -->
        <div class="alert-section">
          <h3 class="section-title section-alert">
            <span class="title-icon">🚨</span>
            重磅预警
          </h3>
          <div class="alert-list">
            <div
              v-for="event in store.highImpactEvents.slice(0, 5)"
              :key="event.id"
              class="alert-item"
            >
              <SignalCard :event="event" :compact="true" />
            </div>
            <div v-if="store.highImpactEvents.length === 0" class="empty-hint">
              暂无重磅预警
            </div>
          </div>
        </div>

        <!-- 风险避雷 -->
        <div class="risk-section">
          <h3 class="section-title section-risk">
            <span class="title-icon">⚠️</span>
            风险避雷
          </h3>
          <div class="risk-list">
            <div
              v-for="event in store.riskEvents.slice(0, 5)"
              :key="event.id"
              class="risk-item"
            >
              <SignalCard :event="event" :compact="true" />
            </div>
            <div v-if="store.riskEvents.length === 0" class="empty-hint">
              暂无风险事件
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh, Search } from '@element-plus/icons-vue'
import { useEcoSignalStore } from '../stores/ecoSignal'
import SentimentGauge from '../components/ecoSignal/SentimentGauge.vue'
import SignalCard from '../components/ecoSignal/SignalCard.vue'
import InfiniteScroll from '../components/common/InfiniteScroll.vue'
import { useDebounceFn } from '@vueuse/core'

const store = useEcoSignalStore()

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
  font-weight: 700;
  color: var(--text-primary, #f1f5f9);
  margin: 0;
}

.ecosignal-container {
  display: grid;
  grid-template-columns: 280px 1fr 320px;
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
  font-weight: 700;
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
  font-weight: 600;
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
  background: var(--bg-card, rgba(30, 41, 59, 0.3));
  border-radius: 12px;
  border: 1px solid var(--border-primary, rgba(148, 163, 184, 0.1));
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
  font-weight: 600;
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

.empty-hint {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary, #94a3b8);
  font-size: 13px;
}

/* 响应式布局 */
@media (max-width: 1400px) {
  .ecosignal-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto 1fr auto;
    overflow-y: auto;
  }

  .left-panel {
    order: 2;
    overflow: visible;
  }

  .center-panel {
    order: 1;
    min-height: 500px;
  }

  .right-panel {
    order: 3;
    overflow: visible;
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

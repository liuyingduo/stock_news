<template>
  <!-- Auth pages (login/register) - no layout wrapper -->
  <template v-if="isAuthPage">
    <router-view />
  </template>
  
  <!-- Main app with layout -->
  <div v-else class="app-container">
    <!-- Header -->
    <header class="dashboard-header">
      <div class="header-left">
        <div class="logo">
          <el-icon><TrendCharts /></el-icon>
          <span class="logo-text">金融事件分析</span>
        </div>
      </div>

      <div class="header-center">
        <div class="live-indicator">
          <span class="live-dot"></span>
          <span class="live-text">LIVE</span>
        </div>
        <div class="stats-display">
          <div class="stat-item">
            <span class="stat-value">{{ stats.eventsCount }}</span>
            <span class="stat-label">Events</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.sourcesCount }}</span>
            <span class="stat-label">Sources</span>
          </div>
          <div class="stat-divider"></div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.sectorsCount }}</span>
            <span class="stat-label">Sectors</span>
          </div>
        </div>
      </div>

      <div class="header-right">
        <button class="nav-button nav-button-secondary" @click="navigateToDashboard">
          Dashboard
        </button>
        <button class="nav-button nav-button-secondary" @click="navigateToEcoSignal">
          智金通
        </button>
        <button class="nav-button nav-button-primary" @click="navigateToSectors">
          Sectors View
        </button>
      </div>
    </header>

    <!-- Main Container -->
    <div class="main-container">
      <!-- Sidebar -->
      <aside class="sidebar">
        <nav class="sidebar-menu">
          <el-menu
            :default-active="activeMenu"
            router
            class="menu"
          >
            <el-menu-item index="/">
              <el-icon><DataBoard /></el-icon>
              <span>仪表板</span>
            </el-menu-item>
            <el-menu-item index="/ecosignal">
              <el-icon><TrendCharts /></el-icon>
              <span>智金通</span>
            </el-menu-item>
            <el-menu-item index="/sectors">
              <el-icon><PieChart /></el-icon>
              <span>板块视图</span>
            </el-menu-item>
          </el-menu>
        </nav>

        <!-- Filters Panel -->
        <div class="panel">
          <h3 class="panel-title">Quick Filters</h3>
          <div class="filter-group">
            <button
              v-for="filter in filters"
              :key="filter.key"
              :class="['filter-button', { active: activeFilter === filter.key }]"
              @click="setActiveFilter(filter.key)"
            >
              <span>{{ filter.label }}</span>
            </button>
          </div>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { TrendCharts, DataBoard, PieChart } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 判断是否是认证页面（登录/注册）
const isAuthPage = computed(() => {
  return route.path === '/login' || route.path === '/register'
})

// Stats (从API获取)
const stats = ref({
  eventsCount: '-',
  sourcesCount: '-',
  sectorsCount: '-'
})

// 加载统计数据
const loadStats = async () => {
  try {
    const { getDashboardStats } = await import('./api/dashboard')
    const data = await getDashboardStats()
    stats.value = {
      eventsCount: data.total_events?.toLocaleString() || '-',
      sourcesCount: data.total_sectors?.toLocaleString() || '-', // 暂时使用 sectors
      sectorsCount: data.total_sectors?.toLocaleString() || '-'
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
    // 保持默认值 '-'
  }
}

// Filters
const filters = ref([
  { key: 'all', label: '全部事件', query: {} },
  { key: 'high', label: '高价值', query: { min_impact: '0.7' } },
  { key: 'medium', label: '中价值', query: { min_impact: '0.4', max_impact: '0.7' } },
  { key: 'low', label: '低价值', query: { max_impact: '0.4' } }
])

const activeFilter = computed(() => {
  const q = route.query
  if (q.min_impact === '0.7') return 'high'
  if (q.min_impact === '0.4' && q.max_impact === '0.7') return 'medium'
  if (q.max_impact === '0.4') return 'low'
  return 'all'
})

const activeMenu = computed(() => route.path)

const navigateToDashboard = () => {
  router.push('/')
}

const navigateToEcoSignal = () => {
  router.push('/ecosignal')
}

const navigateToSectors = () => {
  router.push('/sectors')
}

const setActiveFilter = (filterKey: string) => {
  const filter = filters.value.find(f => f.key === filterKey)
  if (filter) {
    router.push({ path: '/', query: filter.query })
  }
}

onMounted(() => {
  // 只在非认证页面加载统计
  if (!isAuthPage.value) {
    loadStats()
  }
})
</script>

<style scoped>
.app-container {
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: var(--bg-primary);
  display: flex;
  flex-direction: column;
}

.menu {
  border: none;
  background: transparent;
  margin-bottom: 20px;
}

.menu .el-menu-item {
  height: 44px;
  line-height: 44px;
  margin-bottom: 4px;
}
</style>

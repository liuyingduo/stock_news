<template>
  <div class="sectors-view">
    <div class="view-header">
      <h1 class="page-title">板块视图</h1>
      <p class="page-subtitle">点击板块查看相关事件</p>
    </div>

    <div v-loading="loading" class="sectors-grid">
      <div v-if="sectors.length === 0 && !loading" class="empty-state">
        <el-empty description="暂无板块数据" />
      </div>
      <div
        v-for="sector in sectors"
        :key="sector.id"
        class="sector-card"
        :class="getRiskClass(sector.risk_level)"
        @click="handleSectorClick(sector)"
      >
        <div class="sector-header">
          <div class="sector-name">{{ sector.name }}</div>
          <el-tag :type="getRiskTagType(sector.risk_level)" size="small">
            {{ getRiskLabel(sector.risk_level) }}
          </el-tag>
        </div>
        <div class="sector-code">{{ sector.code }}</div>
        <div class="sector-events">{{ sector.related_event_ids?.length || 0 }} 个相关事件</div>
      </div>
    </div>

    <!-- 事件详情对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="selectedSector?.name"
      width="800px"
      destroy-on-close
    >
      <div v-loading="eventsLoading">
        <div v-if="sectorEvents.length === 0 && !eventsLoading" class="empty-state">
          <el-empty description="暂无相关事件" />
        </div>
        <div v-else class="events-list">
          <div v-for="event in sectorEvents" :key="event.id" class="event-item">
            <div class="event-title">{{ event.title }}</div>
            <div class="event-date">{{ formatDate(event.announcement_date) }}</div>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSectors } from '../api/sectors'
import { getEventsBySector } from '../api/events'
import { formatDate } from '../utils/date'
import type { Sector, Event } from '../api/types'

const loading = ref(false)
const sectors = ref<Sector[]>([])
const dialogVisible = ref(false)
const selectedSector = ref<Sector | null>(null)
const eventsLoading = ref(false)
const sectorEvents = ref<Event[]>([])

const loadSectors = async () => {
  loading.value = true
  try {
    sectors.value = await getSectors()
  } catch (error: any) {
    ElMessage.error(error.message || '加载板块失败')
  } finally {
    loading.value = false
  }
}

const handleSectorClick = async (sector: Sector) => {
  selectedSector.value = sector
  dialogVisible.value = true
  eventsLoading.value = true

  try {
    sectorEvents.value = await getEventsBySector(sector.code, 50)
  } catch (error: any) {
    ElMessage.error(error.message || '加载事件失败')
  } finally {
    eventsLoading.value = false
  }
}

const getRiskClass = (riskLevel: string) => {
  const classes: Record<string, string> = {
    high_positive: 'risk-high-positive',
    positive: 'risk-positive',
    neutral: 'risk-neutral',
    negative: 'risk-negative',
    high_negative: 'risk-high-negative',
  }
  return classes[riskLevel] || 'risk-neutral'
}

const getRiskLabel = (riskLevel: string) => {
  const labels: Record<string, string> = {
    high_positive: '高度利好',
    positive: '利好',
    neutral: '中性',
    negative: '利空',
    high_negative: '高度利空',
  }
  return labels[riskLevel] || riskLevel
}

const getRiskTagType = (riskLevel: string) => {
  const types: Record<string, any> = {
    high_positive: 'success',
    positive: 'success',
    neutral: 'info',
    negative: 'warning',
    high_negative: 'danger',
  }
  return types[riskLevel] || 'info'
}

onMounted(() => {
  loadSectors()
})
</script>

<style scoped>
.sectors-view {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.view-header {
  text-align: center;
}

.page-title {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #e0e6ed;
}

.page-subtitle {
  margin: 8px 0 0;
  font-size: 14px;
  color: #94a3b8;
}

.sectors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.sector-card {
  padding: 20px;
  border-radius: 8px;
  border: 2px solid;
  cursor: pointer;
  transition: all 0.3s;
  background: #151a23;
}

.sector-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.sector-card.risk-high-positive {
  border-color: #10b981;
}

.sector-card.risk-positive {
  border-color: #34d399;
}

.sector-card.risk-neutral {
  border-color: #64748b;
}

.sector-card.risk-negative {
  border-color: #f59e0b;
}

.sector-card.risk-high-negative {
  border-color: #ef4444;
}

.sector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.sector-name {
  font-size: 18px;
  font-weight: 600;
  color: #e0e6ed;
}

.sector-code {
  font-size: 14px;
  color: #94a3b8;
  margin-bottom: 8px;
}

.sector-events {
  font-size: 13px;
  color: #64748b;
}

.empty-state {
  grid-column: 1 / -1;
  padding: 40px 0;
}

.events-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.event-item {
  padding: 12px;
  background: #151a23;
  border-radius: 6px;
  border: 1px solid #2d3748;
}

.event-title {
  font-size: 14px;
  color: #e0e6ed;
  margin-bottom: 8px;
}

.event-date {
  font-size: 12px;
  color: #94a3b8;
}
</style>

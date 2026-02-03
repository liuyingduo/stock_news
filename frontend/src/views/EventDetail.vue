<template>
  <div class="event-detail" v-loading="loading">
    <div class="detail-header">
      <el-button @click="goBack" :icon="ArrowLeft" type="default">
        返回列表
      </el-button>
    </div>

    <div v-if="event" class="detail-content">
      <!-- Event Header -->
      <div class="event-header">
        <div class="header-tags">
          <span :class="['category-tag', getCategoryClass(event.event_category)]">
            {{ getCategoryLabel(event.event_category) }}
          </span>
          <el-tag
            v-for="type in event.event_types"
            :key="type"
            size="small"
            :type="getTypeTagType(type)"
          >
            {{ getTypeLabel(type) }}
          </el-tag>
        </div>
        <div class="header-meta">
          <span v-if="event.source" class="meta-item">📰 {{ event.source }}</span>
          <span class="meta-item">📅 {{ formatDate(event.announcement_date) }}</span>
        </div>
      </div>

      <!-- Title -->
      <h1 class="event-title">{{ event.title }}</h1>

      <!-- Content -->
      <div class="event-content">
        <p>{{ event.content }}</p>
      </div>

      <!-- AI Analysis Section -->
      <div v-if="event.ai_analysis" class="analysis-section">
        <h2 class="section-title">AI 分析</h2>
        
        <div class="scores-row">
          <div class="score-card">
            <div class="score-label">影响程度</div>
            <div :class="['score-value', getImpactClass(event.ai_analysis.impact_score)]">
              {{ event.ai_analysis.impact_score != null ? ((event.ai_analysis.impact_score * 10).toFixed(1) + '/10') : 'N/A' }}
            </div>
          </div>
          <div class="score-card">
            <div class="score-label">市场情绪</div>
            <div :class="['score-value', getSentimentClass(event.ai_analysis.sentiment_score)]">
              {{ event.ai_analysis.sentiment_score?.toFixed(2) || 'N/A' }}
            </div>
          </div>
          <div class="score-card">
            <div class="score-label">置信度</div>
            <div :class="['score-value', getConfidenceClass(event.ai_analysis.confidence_score)]">
              {{ ((event.ai_analysis.confidence_score || 0) * 100).toFixed(0) }}%
            </div>
          </div>
        </div>

        <div v-if="event.ai_analysis.impact_reason" class="analysis-reason">
          <h3>分析理由</h3>
          <p>{{ event.ai_analysis.impact_reason }}</p>
        </div>

        <!-- Affected Entities -->
        <div class="affected-entities">
          <div v-if="event.ai_analysis.affected_stocks?.length" class="entity-group">
            <h3>相关股票</h3>
            <div class="entity-list">
              <el-tag v-for="stock in event.ai_analysis.affected_stocks" :key="stock.code" type="info">
                {{ stock.name }} ({{ stock.code }})
              </el-tag>
            </div>
          </div>
          
          <div v-if="event.ai_analysis.affected_sectors?.length" class="entity-group">
            <h3>相关板块</h3>
            <div class="entity-list">
              <el-tag v-for="sector in event.ai_analysis.affected_sectors" :key="sector.code" type="warning">
                {{ sector.name }}
              </el-tag>
            </div>
          </div>

          <div v-if="event.ai_analysis.affected_materials?.length" class="entity-group">
            <h3>相关原材料</h3>
            <div class="entity-list">
              <el-tag v-for="material in event.ai_analysis.affected_materials" :key="material.name" type="success">
                {{ material.name }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- Original Link -->
      <div v-if="event.original_url" class="original-link">
        <el-button type="primary" @click="openOriginalLink">
          查看原文 →
        </el-button>
      </div>
    </div>

    <div v-else-if="!loading" class="empty-state">
      <el-empty description="事件不存在或已被删除" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { getEventById } from '../api/events'
import type { Event } from '../api/types'
import { formatDate } from '../utils/date'
import { 
  getCategoryLabel, 
  getCategoryClass, 
  getTypeTagType, 
  getTypeLabel 
} from '../utils/format'
import { 
  getImpactClass, 
  getSentimentClass, 
  getConfidenceClass 
} from '../utils/score'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const event = ref<Event | null>(null)

const loadEvent = async () => {
  const eventId = route.params.id as string
  if (!eventId) {
    ElMessage.error('无效的事件ID')
    return
  }

  loading.value = true
  try {
    event.value = await getEventById(eventId)
  } catch (error: any) {
    ElMessage.error(error.message || '加载事件详情失败')
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.back()
}

const openOriginalLink = () => {
  if (event.value?.original_url) {
    window.open(event.value.original_url, '_blank')
  }
}

// Local functions removed. Using imported utils.

onMounted(() => {
  loadEvent()
})
</script>

<style scoped>
.event-detail {
  max-width: 900px;
  margin: 0 auto;
  padding: 24px;
}

.detail-header {
  margin-bottom: 24px;
}

.detail-content {
  background: var(--bg-card);
  border-radius: var(--radius-md);
  padding: 32px;
  border: 1px solid var(--border-primary);
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.header-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.header-meta {
  display: flex;
  gap: 16px;
  color: var(--text-secondary);
  font-size: 14px;
}

.event-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 24px 0;
  line-height: 1.4;
}

.event-content {
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-secondary);
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-primary);
}

.analysis-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 20px 0;
}

.scores-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.score-card {
  background: var(--bg-panel);
  border-radius: var(--radius-sm);
  padding: 20px;
  text-align: center;
  border: 1px solid var(--border-primary);
}

.score-label {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.score-value {
  font-size: 28px;
  font-weight: 700;
}

.analysis-reason {
  background: var(--bg-panel);
  border-radius: var(--radius-sm);
  padding: 20px;
  margin-bottom: 24px;
  border-left: 4px solid var(--accent-info);
}

.analysis-reason h3 {
  font-size: 16px;
  margin: 0 0 12px 0;
  color: var(--text-primary);
}

.analysis-reason p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.affected-entities {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.entity-group h3 {
  font-size: 16px;
  margin: 0 0 12px 0;
  color: var(--text-primary);
}

.entity-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.original-link {
  padding-top: 24px;
  border-top: 1px solid var(--border-primary);
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
}

/* Score color classes */
.impact-high {
  color: var(--text-primary) !important;
  text-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

.impact-medium {
  color: var(--accent-info) !important;
}

.impact-low {
  color: var(--text-muted) !important;
}

.sentiment-positive {
  color: var(--accent-success) !important;
}

.sentiment-negative {
  color: var(--accent-danger) !important;
}

.sentiment-neutral {
  color: var(--text-secondary) !important;
}

.confidence-high {
  color: var(--accent-success) !important;
}

.confidence-medium {
  color: var(--accent-warning) !important;
}

.confidence-low {
  color: var(--text-muted) !important;
}

@media (max-width: 768px) {
  .scores-row {
    grid-template-columns: 1fr;
  }
  
  .event-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>

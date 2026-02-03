<template>
  <div class="article-card" @click="handleClick">
    <!-- Card Header -->
    <div class="card-header">
      <div class="header-left">
        <span :class="['category-tag', getCategoryClass(event.event_category)]">
          {{ getCategoryLabel(event.event_category) }}
        </span>
        <div v-if="normalizedTypes.length > 0" class="type-tags">
          <el-tag
            v-for="type in normalizedTypes"
            :key="type"
            size="small"
            :type="getTypeTagType(type)"
          >
            {{ getTypeLabel(type) }}
          </el-tag>
        </div>
      </div>
      <div class="card-meta">
        <span v-if="event.source" class="meta-item">
          📰 {{ event.source }}
        </span>
        <span class="meta-item">
          📅 {{ formatRelativeDate(event.announcement_date) }}
        </span>
      </div>
    </div>

    <!-- Card Title & Content with Tooltip -->
    <el-tooltip
      v-if="event.ai_analysis?.impact_reason"
      placement="top"
      :show-after="300"
      popper-class="analysis-tooltip"
    >
      <template #content>
        <div class="tooltip-content">
          <span class="tooltip-icon">💡</span>
          <span class="tooltip-text">{{ event.ai_analysis.impact_reason }}</span>
        </div>
      </template>
      <div class="card-content-wrapper">
        <h3 class="card-title title-tooltip">
          {{ event.title }}
        </h3>
        <p class="card-excerpt">{{ event.content }}</p>
      </div>
    </el-tooltip>
    <div v-else class="card-content-wrapper">
      <h3 class="card-title">{{ event.title }}</h3>
      <p class="card-excerpt">{{ event.content }}</p>
    </div>

    <!-- Card Footer -->
    <div class="card-footer">
      <div v-if="event.ai_analysis?.impact_score !== null && event.ai_analysis?.impact_score !== undefined" class="impact-score">
        <span>影响评分:</span>
        <span :class="getImpactClass(event.ai_analysis?.impact_score ?? null)">
          {{ event.ai_analysis?.impact_score?.toFixed(1) ?? 'N/A' }}/10
        </span>
      </div>
      <el-button
        v-if="event.original_url"
        class="view-button"
        type="primary"
        size="small"
        @click.stop="openOriginalLink"
      >
        查看详情 →
      </el-button>
      <el-button
        v-else-if="!event.ai_analysis"
        class="analyze-button"
        type="primary"
        size="small"
        @click.stop="handleAnalyze"
      >
        AI 分析
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { formatDate } from '../utils/date'
import type { Event, EventType } from '../api/types'

interface Props {
  event: Event
}

interface Emits {
  (e: 'analyze', eventId: string): void
  (e: 'click', event: Event): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 标准化类型为数组
const normalizedTypes = computed(() => {
  const types = props.event.event_types
  if (Array.isArray(types)) {
    return types
  }
  return []
})

const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    global_macro: '全球大事',
    policy: '政策风向',
    industry: '行业动向',
    company: '公司动态',
  }
  return labels[category] || category.toUpperCase()
}

const getCategoryClass = (category: string) => {
  const classes: Record<string, string> = {
    global_macro: 'category-geopolitics',
    policy: 'category-policy',
    industry: 'category-economy',
    company: 'category-company',
  }
  return classes[category] || 'category-others'
}

// 获取类型标签颜色
const getTypeTagType = (type: EventType) => {
  const typeMap: Record<string, any> = {
    risk_crisis: 'danger',
    regulatory: 'danger',
    sentiment: 'warning',
    price_vol: 'warning',
    tech_innov: 'info',
    capital_action: 'success',
    info_change: '',
    ops_info: '',
    order_contract: 'info',
    supply_chain: 'info',
    geopolitics: 'danger',
  }
  return typeMap[type] || ''
}

// 获取类型标签文本
const getTypeLabel = (type: EventType) => {
  const labels: Record<string, string> = {
    geopolitics: '地缘政治',
    regulatory: '监管政策',
    sentiment: '市场情绪',
    tech_innov: '科技创新',
    supply_chain: '供应链',
    capital_action: '资本运作',
    info_change: '信息变更',
    ops_info: '运营信息',
    order_contract: '订单合同',
    price_vol: '价格波动',
    risk_crisis: '风险危机',
  }
  return labels[type] || type
}

const getImpactClass = (score: number | null) => {
  if (score === null) return ''
  if (score >= 8) return 'impact-high'
  if (score >= 6) return 'impact-medium'
  return 'impact-low'
}

const formatRelativeDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffHours / 24)

  if (diffHours < 1) return '刚刚'
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return formatDate(dateStr)
}

const handleClick = () => {
  emit('click', props.event)
}

const handleAnalyze = () => {
  emit('analyze', props.event.id)
}

const openOriginalLink = () => {
  if (props.event.original_url) {
    window.open(props.event.original_url, '_blank')
  }
}
</script>

<style scoped>
.article-card {
  cursor: pointer;
  transition: all var(--transition-base);
  position: relative;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 12px;
}

.card-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.card-title {
  font-size: 16px;
  font-weight: 500;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.title-tooltip {
  cursor: help;
  transition: all var(--transition-base);
}

.card-content-wrapper:hover .title-tooltip {
  opacity: 0.7;
}

.card-excerpt {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 12px 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid var(--border-primary);
}

.impact-score {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
}

.impact-score span:last-child {
  font-weight: 600;
}

.impact-high {
  color: var(--accent-primary);
}

.impact-medium {
  color: var(--accent-secondary);
}

.impact-low {
  color: var(--accent-success);
}

.view-button,
.analyze-button {
  font-size: 12px;
  padding: 6px 16px;
  font-weight: 500;
}
</style>

<style>
/* AI 分析 Tooltip 样式 - 限制宽度和样式 */
.analysis-tooltip {
  max-width: 400px !important;
  word-wrap: break-word !important;
  white-space: normal !important;
  font-size: 14px !important;
  line-height: 1.6 !important;
  padding: 12px 16px !important;
  background: rgba(30, 30, 40, 0.95) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4) !important;
  backdrop-filter: blur(10px) !important;
}

/* Tooltip 箭头颜色 */
.analysis-tooltip .el-tooltip__arrow::before {
  background: rgba(30, 30, 40, 0.95) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* Tooltip 内容样式 */
.tooltip-content {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.tooltip-icon {
  font-size: 16px;
  flex-shrink: 0;
  margin-top: 2px;
  color: #d4a574;
}

.tooltip-text {
  color: rgba(255, 255, 255, 0.85);
  font-weight: 400;
}
</style>

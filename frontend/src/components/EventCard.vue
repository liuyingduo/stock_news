<template>
  <div class="article-card" @click="handleClick">
    <!-- Card Header -->
    <div class="card-header">
      <span :class="['category-tag', getCategoryClass(event.event_category)]">
        {{ getCategoryLabel(event.event_category) }}
      </span>
      <div class="card-meta">
        <span v-if="event.source" class="meta-item">
          📰 {{ event.source }}
        </span>
        <span class="meta-item">
          📅 {{ formatRelativeDate(event.announcement_date) }}
        </span>
      </div>
    </div>

    <!-- Card Title -->
    <h3 class="card-title">{{ event.title }}</h3>

    <!-- Card Excerpt -->
    <p class="card-excerpt">{{ event.content }}</p>

    <!-- AI 分析结果 (可选展示) -->
    <div v-if="event.ai_analysis?.impact_reason" class="analysis-preview">
      💡 {{ event.ai_analysis.impact_reason }}
    </div>

    <!-- Card Footer -->
    <div class="card-footer">
      <div v-if="event.ai_analysis?.impact_score !== null" class="impact-score">
        <span>影响评分:</span>
        <span :class="getImpactClass(event.ai_analysis.impact_score)">
          {{ event.ai_analysis.impact_score?.toFixed(1) }}/10
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
import { formatDate } from '../utils/date'
import type { Event } from '../api/types'

interface Props {
  event: Event
}

interface Emits {
  (e: 'analyze', eventId: string): void
  (e: 'click', event: Event): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const getCategoryLabel = (category: string) => {
  const labels: Record<string, string> = {
    core_driver: '核心驱动',
    special_situation: '特殊机遇',
    industrial_chain: '产业链',
    sentiment_flows: '市场情绪',
    macro_geopolitics: '宏观地缘',
  }
  return labels[category] || category.toUpperCase()
}

const getCategoryClass = (category: string) => {
  const classes: Record<string, string> = {
    core_driver: 'category-markets',
    special_situation: 'category-geopolitics',
    industrial_chain: 'category-economy',
    sentiment_flows: 'category-technology',
    macro_geopolitics: 'category-geopolitics',
  }
  return classes[category] || 'category-others'
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
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 8px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
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

.analysis-preview {
  font-size: 13px;
  color: var(--text-secondary);
  background: rgba(255, 77, 77, 0.05);
  border-left: 3px solid var(--accent-primary);
  padding: 8px 12px;
  margin-bottom: 12px;
  border-radius: 4px;
  line-height: 1.5;
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
  font-weight: 600;
  color: var(--text-secondary);
}

.impact-score span:last-child {
  font-weight: 700;
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
  font-weight: 600;
}
</style>

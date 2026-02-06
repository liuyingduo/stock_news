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
          📰 {{ formatSource(event.source) }}
        </span>
        <span class="meta-item">
          📅 {{ formatDate(event.announcement_date) }}
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
      <div class="scores-container">
        <div v-if="event.ai_analysis?.impact_score != null" class="score-item">
          <span class="score-label">影响:</span>
          <span :class="['score-value', getImpactClass(event.ai_analysis.impact_score)]">
            {{ (event.ai_analysis.impact_score * 10).toFixed(1) }}
          </span>
        </div>
        <div v-if="event.ai_analysis?.sentiment_score != null" class="score-item">
          <span class="score-label">多空:</span>
          <span :class="['score-value', getSentimentClass(event.ai_analysis.sentiment_score)]">
            {{ event.ai_analysis.sentiment_score.toFixed(1) }}
          </span>
        </div>
        <div v-if="event.ai_analysis?.confidence_score != null" class="score-item">
          <span class="score-label">置信:</span>
          <span :class="['score-value', getConfidenceClass(event.ai_analysis.confidence_score)]">
            {{ (event.ai_analysis.confidence_score * 100).toFixed(0) }}%
          </span>
        </div>
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
import type { Event } from '../api/types'
import { 
  getCategoryLabel, 
  getCategoryClass, 
  getTypeTagType, 
  getTypeLabel,
  formatSource
} from '../utils/format'
import { 
  getImpactClass, 
  getSentimentClass, 
  getConfidenceClass 
} from '../utils/score'

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

// Local functions removed. Using imported utils.

// formatRelativeDate removed, using formatDate directly

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

.scores-container {
  display: flex;
  gap: 16px;
  align-items: center;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-secondary);
}

.score-label {
  font-weight: 500;
}

.score-value {
  font-weight: 600;
  font-family: var(--font-mono);
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

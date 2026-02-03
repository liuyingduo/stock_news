<template>
  <div
    class="signal-card"
    :class="{ 'compact': compact, 'expanded': expanded }"
    @click="toggleExpand"
  >
    <!-- Header: 来源 + 类型标签 + 时间 -->
    <div class="card-header">
      <div class="header-left">
        <span v-if="event.source" class="source-tag">
          {{ event.source }}
        </span>
        <div class="type-tags">
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
      <div class="header-right">
        <span class="time-tag">{{ formatRelativeDate(event.announcement_date) }}</span>
      </div>
    </div>

    <!-- Title -->
    <h3 class="card-title">{{ event.title }}</h3>

    <!-- Score Section: 环形进度条 -->
    <div v-if="event.ai_analysis" class="score-section">
      <CircularProgress
        v-if="event.ai_analysis.sentiment_score !== undefined"
        :value="event.ai_analysis.sentiment_score"
        :min="-1"
        :max="1"
        :size="compact ? 60 : 80"
        label="情绪"
      />
      <CircularProgress
        v-if="event.ai_analysis.impact_score !== null"
        :value="event.ai_analysis.impact_score || 0"
        :min="0"
        :max="1"
        :size="compact ? 60 : 80"
        label="影响"
      />
    </div>

    <!-- Hype Tag -->
    <el-tag
      v-if="event.ai_analysis?.is_hype"
      class="hype-tag"
      type="warning"
      effect="dark"
    >
      ⚡ 情绪炒作
    </el-tag>

    <!-- Entity Tags: 股票和板块 -->
    <div v-if="hasEntities" class="entity-tags">
      <div v-if="hasStocks" class="entity-group">
        <span class="entity-icon">📈</span>
        <el-tag
          v-for="stock in displayStocks"
          :key="stock.code"
          size="small"
          class="entity-tag"
        >
          {{ stock.name }}
        </el-tag>
        <span v-if="extraStocks > 0" class="more-tag">
          +{{ extraStocks }}
        </span>
      </div>
      <div v-if="hasSectors" class="entity-group">
        <span class="entity-icon">📊</span>
        <el-tag
          v-for="sector in displaySectors"
          :key="sector.code"
          size="small"
          type="info"
          class="entity-tag"
        >
          {{ sector.name }}
        </el-tag>
        <span v-if="extraSectors > 0" class="more-tag">
          +{{ extraSectors }}
        </span>
      </div>
    </div>

    <!-- Impact Reason (展开显示) -->
    <div v-if="expanded && event.ai_analysis?.impact_reason" class="impact-reason">
      <span class="reason-icon">💡</span>
      <div class="reason-content">
        <div class="reason-label">影响分析</div>
        <p class="reason-text">{{ event.ai_analysis.impact_reason }}</p>
      </div>
    </div>

    <!-- Entity Reasons (展开显示) -->
    <div v-if="expanded && hasEntityReasons" class="entity-reasons">
      <div v-for="stock in stocksWithReason" :key="stock.code" class="entity-reason-item">
        <span class="entity-name">📈 {{ stock.name }}</span>
        <span class="entity-reason-text">{{ stock.reason }}</span>
      </div>
      <div v-for="sector in sectorsWithReason" :key="sector.code" class="entity-reason-item">
        <span class="entity-name">📊 {{ sector.name }}</span>
        <span class="entity-reason-text">{{ sector.reason }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import CircularProgress from './CircularProgress.vue'
import type { Event, EventType } from '../../api/types'

interface Props {
  event: Event
  compact?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  compact: false,
})

const expanded = ref(false)

const toggleExpand = () => {
  expanded.value = !expanded.value
}

// 标准化类型为数组
const normalizedTypes = computed(() => {
  const type = props.event.event_type
  if (Array.isArray(type)) {
    return type
  }
  return [type]
})

// 获取类型标签颜色
const getTypeTagType = (type: EventType) => {
  const typeMap: Record<string, any> = {
    regulatory_policy: 'danger',
    risk_warning: 'danger',
    financial_report: 'info',
    major_event: 'warning',
    info_change: '',
    other: 'info',
  }
  return typeMap[type] || ''
}

// 获取类型标签文本
const getTypeLabel = (type: EventType) => {
  const labels: Record<string, string> = {
    macro_geopolitics: '宏观地缘',
    regulatory_policy: '监管政策',
    market_sentiment: '市场情绪',
    industrial_chain: '产业链',
    core_sector: '核心板块',
    major_event: '重大事项',
    financial_report: '财务报告',
    financing_announcement: '融资公告',
    risk_warning: '风险提示',
    asset_restructuring: '资产重组',
    info_change: '信息变更',
    shareholding_change: '持股变动',
    other: '其他',
  }
  return labels[type] || type
}

// 格式化相对时间
const formatRelativeDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
  const diffDays = Math.floor(diffHours / 24)

  if (diffHours < 1) return '刚刚'
  if (diffHours < 24) return `${diffHours}小时前`
  if (diffDays < 7) return `${diffDays}天前`
  return date.toLocaleDateString('zh-CN')
}

// 判断是否有实体
const hasStocks = computed(() => {
  const stocks = props.event.ai_analysis?.affected_stocks
  return stocks !== undefined && stocks.length > 0
})

const hasSectors = computed(() => {
  const sectors = props.event.ai_analysis?.affected_sectors
  return sectors !== undefined && sectors.length > 0
})

const hasEntities = computed(() => hasStocks.value || hasSectors.value)

// 显示的实体（限制数量）
const displayStocks = computed(() => {
  const stocks = props.event.ai_analysis?.affected_stocks || []
  return props.compact ? stocks.slice(0, 2) : stocks.slice(0, 3)
})

const displaySectors = computed(() => {
  const sectors = props.event.ai_analysis?.affected_sectors || []
  return props.compact ? sectors.slice(0, 1) : sectors.slice(0, 2)
})

const extraStocks = computed(() => {
  const stocks = props.event.ai_analysis?.affected_stocks
  const total = stocks?.length || 0
  const max = props.compact ? 2 : 3
  return Math.max(0, total - max)
})

const extraSectors = computed(() => {
  const sectors = props.event.ai_analysis?.affected_sectors
  const total = sectors?.length || 0
  const max = props.compact ? 1 : 2
  return Math.max(0, total - max)
})

// 判断是否有实体理由
const stocksWithReason = computed(() => {
  return (props.event.ai_analysis?.affected_stocks || []).filter(s => s.reason)
})

const sectorsWithReason = computed(() => {
  return (props.event.ai_analysis?.affected_sectors || []).filter(s => s.reason)
})

const hasEntityReasons = computed(() => {
  return stocksWithReason.value.length > 0 || sectorsWithReason.value.length > 0
})
</script>

<style scoped>
.signal-card {
  background: var(--signal-card-bg, rgba(30, 41, 59, 0.8));
  border: 1px solid var(--signal-card-border, rgba(148, 163, 184, 0.1));
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.signal-card:hover {
  background: var(--signal-card-hover, rgba(51, 65, 85, 0.9));
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.signal-card.compact {
  padding: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  gap: 8px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
  min-width: 0;
}

.source-tag {
  font-size: 12px;
  color: var(--text-secondary, #94a3b8);
  white-space: nowrap;
}

.type-tags {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.header-right {
  flex-shrink: 0;
}

.time-tag {
  font-size: 11px;
  color: var(--text-secondary, #94a3b8);
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary, #f1f5f9);
  margin: 0 0 12px 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.signal-card.compact .card-title {
  font-size: 13px;
  -webkit-line-clamp: 1;
}

.score-section {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin: 12px 0;
}

.signal-card.compact .score-section {
  gap: 12px;
}

.hype-tag {
  margin: 8px 0;
  width: fit-content;
}

.entity-tags {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.entity-group {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.entity-icon {
  font-size: 14px;
}

.entity-tag {
  font-size: 11px;
}

.more-tag {
  font-size: 11px;
  color: var(--text-secondary, #94a3b8);
  margin-left: 4px;
}

.impact-reason {
  display: flex;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-primary, rgba(148, 163, 184, 0.1));
}

.reason-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.reason-content {
  flex: 1;
}

.reason-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary, #94a3b8);
  margin-bottom: 4px;
}

.reason-text {
  font-size: 13px;
  color: var(--text-primary, #f1f5f9);
  line-height: 1.5;
  margin: 0;
}

.entity-reasons {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-primary, rgba(148, 163, 184, 0.1));
}

.entity-reason-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.entity-name {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary, #f1f5f9);
}

.entity-reason-text {
  font-size: 12px;
  color: var(--text-secondary, #94a3b8);
  line-height: 1.4;
}
</style>

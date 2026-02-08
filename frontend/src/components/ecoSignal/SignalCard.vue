<template>
  <div
    class="signal-card"
    :class="{ 'compact': compact, 'expanded': expanded }"
    @click="toggleExpand"
  >
    <!-- Header: 鏉ユ簮 + 绫诲瀷鏍囩 + 鏃堕棿 -->
    <div class="card-header">
      <div class="header-left">
        <span v-if="event.source" class="source-tag">
          {{ formatSource(event.source) }}
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
        <span class="time-tag">{{ formatDate(event.announcement_date) }}</span>
      </div>
    </div>

    <!-- Title -->
    <h3 class="card-title">{{ event.title }}</h3>

    <!-- Score Badges -->
    <div v-if="event.ai_analysis" class="score-badges">
      <!-- Impact Score -->
      <div 
        v-if="event.ai_analysis.impact_score !== null" 
        class="score-badge"
        :class="getImpactClass(event.ai_analysis.impact_score)"
      >
        <span class="score-label">褰卞搷</span>
        <span class="score-num">{{ (event.ai_analysis.impact_score * 10).toFixed(1) }}</span>
      </div>

      <!-- Sentiment Score -->
      <div 
        v-if="event.ai_analysis.sentiment_score !== undefined" 
        class="score-badge"
        :class="getSentimentClass(event.ai_analysis.sentiment_score)"
      >
        <span class="score-label">澶氱┖</span>
        <span class="score-num">{{ event.ai_analysis.sentiment_score.toFixed(1) }}</span>
      </div>
    </div>

    <!-- Hype Tag -->
    <el-tag
      v-if="event.ai_analysis?.is_hype"
      class="hype-tag"
      type="warning"
      effect="dark"
      size="small"
    >
      鈿?鎯呯华鐐掍綔
    </el-tag>

    <!-- Entity Tags: 鑲＄エ鍜屾澘鍧?-->
    <div v-if="hasEntities" class="entity-tags">
      <div v-if="hasStocks" class="entity-group">
        <span class="entity-icon">馃搱</span>
        <el-tag
          v-for="stock in displayStocks"
          :key="stock.code"
          size="small"
          class="entity-tag"
          effect="plain"
        >
          {{ stock.name }}
        </el-tag>
        <span v-if="extraStocks > 0" class="more-tag">
          +{{ extraStocks }}
        </span>
      </div>
      <div v-if="hasSectors" class="entity-group">
        <span class="entity-icon">馃搳</span>
        <el-tag
          v-for="sector in displaySectors"
          :key="sector.code"
          size="small"
          type="info"
          class="entity-tag"
          effect="plain"
        >
          {{ sector.name }}
        </el-tag>
        <span v-if="extraSectors > 0" class="more-tag">
          +{{ extraSectors }}
        </span>
      </div>
    </div>

    <!-- Impact Reason (灞曞紑鏄剧ず) -->
    <div v-if="expanded && event.ai_analysis?.impact_reason" class="impact-reason">
      <span class="reason-icon">馃挕</span>
      <div class="reason-content">
        <div class="reason-label">褰卞搷鍒嗘瀽</div>
        <p class="reason-text">{{ event.ai_analysis.impact_reason }}</p>
      </div>
    </div>

    <!-- Entity Reasons (灞曞紑鏄剧ず) -->
    <div v-if="expanded && hasEntityReasons" class="entity-reasons">
      <div v-for="stock in stocksWithReason" :key="stock.code" class="entity-reason-item">
        <span class="entity-name">馃搱 {{ stock.name }}</span>
        <span class="entity-reason-text">{{ stock.reason }}</span>
      </div>
      <div v-for="sector in sectorsWithReason" :key="sector.code" class="entity-reason-item">
        <span class="entity-name">馃搳 {{ sector.name }}</span>
        <span class="entity-reason-text">{{ sector.reason }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Event, EventType } from '../../api/types'
import { formatDate } from '../../utils/date'
import { formatSource, getTypeLabel, getTypeTagType } from '../../utils/format'
import { getImpactClass, getSentimentClass } from '../../utils/score'

// Props 瀹氫箟
const props = defineProps<{
  event: Event
  compact?: boolean
}>()

// 灞曞紑鐘舵€?
const expanded = ref(false)

// 鍒囨崲灞曞紑
const toggleExpand = () => {
  expanded.value = !expanded.value
}

// 瑙勮寖鍖栦簨浠剁被鍨?
const normalizedTypes = computed<EventType[]>(() => {
  const eventTypes = props.event.event_types
  if (!eventTypes) return []
  if (Array.isArray(eventTypes)) return eventTypes
  return [eventTypes]
})

// 鍒ゆ柇鏄惁鏈夊疄浣?
const hasStocks = computed(() => {
  const stocks = props.event.ai_analysis?.affected_stocks
  return stocks !== undefined && stocks.length > 0
})

const hasSectors = computed(() => {
  const sectors = props.event.ai_analysis?.affected_sectors
  return sectors !== undefined && sectors.length > 0
})

const hasEntities = computed(() => hasStocks.value || hasSectors.value)

// 鏄剧ず鐨勫疄浣擄紙闄愬埗鏁伴噺锛?
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

// 鍒ゆ柇鏄惁鏈夊疄浣撶悊鐢?
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

<style scoped src="./SignalCard.css"></style>


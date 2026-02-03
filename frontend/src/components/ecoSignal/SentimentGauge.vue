<template>
  <div class="sentiment-gauge">
    <v-chart
      :option="chartOption"
      :autoresize="true"
      :style="{ height: '200px' }"
    />
    <div class="gauge-stats">
      <div class="stat-item">
        <span class="stat-label">平均影响</span>
        <span class="stat-value" :style="{ color: getImpactColor(averageImpact) }">
          {{ averageImpact.toFixed(2) }}
        </span>
      </div>
      <div class="stat-item">
        <span class="stat-label">已分析</span>
        <span class="stat-value">{{ totalAnalyzed }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import type { EChartsOption } from 'echarts'

interface Props {
  averageSentiment: number
  averageImpact: number
  totalAnalyzed: number
}

const props = defineProps<Props>()

// 获取影响分颜色
const getImpactColor = (score: number) => {
  if (score > 0.7) return '#ef4444'
  if (score > 0.4) return '#f97316'
  return '#94a3b8'
}

// ECharts 仪表盘配置
const chartOption = computed<EChartsOption>(() => ({
  series: [
    {
      type: 'gauge',
      startAngle: 180,
      endAngle: 0,
      min: -1,
      max: 1,
      splitNumber: 4,
      axisLine: {
        lineStyle: {
          width: 24,
          color: [
            [0.25, '#22c55e'],  // 极度利空（绿）
            [0.45, '#94a3b8'],  // 利空（灰）
            [0.55, '#94a3b8'],  // 中性（灰）
            [0.75, '#ef4444'],  // 利好（红）
            [1, '#ef4444'],     // 极度利好（红）
          ],
        },
      },
      pointer: {
        icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
        length: '12%',
        width: 16,
        offsetCenter: [0, '-60%'],
        itemStyle: {
          color: 'auto',
        },
      },
      axisTick: {
        length: 8,
        lineStyle: {
          color: 'auto',
          width: 2,
        },
      },
      splitLine: {
        length: 16,
        lineStyle: {
          color: 'auto',
          width: 3,
        },
      },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 12,
        distance: -50,
        formatter: (value: number) => {
          if (value === 1) return '极度利好'
          if (value === 0.5) return '利好'
          if (value === 0) return '中性'
          if (value === -0.5) return '利空'
          if (value === -1) return '极度利空'
          return ''
        },
      },
      title: {
        offsetCenter: [0, '-15%'],
        fontSize: 16,
        color: '#94a3b8',
      },
      detail: {
        fontSize: 36,
        offsetCenter: [0, '0%'],
        valueAnimation: true,
        formatter: (value: number) => value.toFixed(2),
        color: 'auto',
      },
      data: [
        {
          value: props.averageSentiment,
          name: '市场情绪',
        },
      ],
    },
  ],
}))
</script>

<style scoped>
.sentiment-gauge {
  background: var(--bg-card, rgba(30, 41, 59, 0.5));
  border-radius: 12px;
  padding: 16px;
  border: 1px solid var(--border-primary, rgba(148, 163, 184, 0.1));
}

.gauge-stats {
  display: flex;
  justify-content: space-around;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-primary, rgba(148, 163, 184, 0.1));
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: var(--text-secondary, #94a3b8);
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #f1f5f9);
}
</style>

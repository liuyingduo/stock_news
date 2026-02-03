<template>
  <div class="circular-progress" :style="{ width: `${size}px`, height: `${size}px` }">
    <v-chart
      :option="chartOption"
      :autoresize="true"
      :style="{ width: '100%', height: '100%' }"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import type { EChartsOption } from 'echarts'

interface Props {
  value: number
  min: number
  max: number
  size?: number
  label?: string
  color?: string | string[]
}

const props = withDefaults(defineProps<Props>(), {
  size: 80,
})

// 计算百分比
const percentage = computed(() => {
  const range = props.max - props.min
  const normalized = (props.value - props.min) / range
  return Math.max(0, Math.min(100, normalized * 100))
})

// 获取颜色
const getColor = computed(() => {
  if (Array.isArray(props.color)) {
    return props.color[0] as string // 数组时取第一个
  }
  if (props.color) {
    return props.color
  }

  // 默认颜色逻辑
  const { value, min } = props

  // sentiment score (-1 to 1)
  if (min < 0) {
    if (value > 0.7) return '#ef4444'      // 极度利好（红）
    if (value > 0.3) return '#f97316'      // 利好（橙）
    if (value > -0.1) return '#94a3b8'     // 中性（灰）
    if (value > -0.7) return '#64748b'     // 利空（深灰）
    return '#22c55e'                       // 极度利空（绿）
  }

  // impact score (0 to 1)
  if (value >= 0.7) return '#ef4444'       // 高影响（红）
  if (value >= 0.4) return '#f59e0b'       // 中影响（橙）
  return '#94a3b8'                        // 低影响（灰）
})

// ECharts 配置
const chartOption = computed<EChartsOption>(() => ({
  series: [
    {
      type: 'pie',
      radius: ['70%', '90%'],
      center: ['50%', '50%'],
      startAngle: 90,
      avoidLabelOverlap: false,
      label: { show: false },
      labelLine: { show: false },
      data: [
        {
          value: percentage.value,
          name: 'value',
          itemStyle: {
            color: getColor.value,
            borderRadius: 0,
          },
        },
        {
          value: 100 - percentage.value,
          name: 'background',
          itemStyle: {
            color: 'rgba(51, 65, 85, 0.5)',
            borderRadius: 0,
          },
        },
      ],
      emphasis: {
        scale: true,
        scaleSize: 5,
      },
    },
  ],
  graphic: [
    {
      type: 'text',
      left: 'center',
      top: '42%',
      style: {
        text: props.value.toFixed(2),
        fontSize: Math.max(14, props.size * 0.22),
        fontWeight: 'bold',
        fill: '#fff',
      },
    },
    {
      type: 'text',
      left: 'center',
      top: '62%',
      style: {
        text: props.label || '',
        fontSize: Math.max(10, props.size * 0.14),
        fill: '#94a3b8',
      },
    },
  ],
}))
</script>

<style scoped>
.circular-progress {
  display: inline-block;
}
</style>

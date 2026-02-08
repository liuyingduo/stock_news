<template>
  <div class="group/graph relative flex h-full min-h-[520px] w-full flex-col overflow-hidden rounded-xl border border-primary/10 bg-bg-card/30">
    <div class="graph-grid absolute inset-0 z-0"></div>

    <svg class="pointer-events-none absolute inset-0 z-10 h-full w-full">
      <defs>
        <linearGradient id="goldGradientAsset" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stop-color="#D4AF37" stop-opacity="0.2" />
          <stop offset="50%" stop-color="#D4AF37" stop-opacity="0.85" />
          <stop offset="100%" stop-color="#D4AF37" stop-opacity="0.2" />
        </linearGradient>
      </defs>

      <line
        v-for="edge in graphEdges"
        :key="edge.id"
        :x1="`${nodeMap[edge.from].x}%`"
        :y1="`${nodeMap[edge.from].y}%`"
        :x2="`${nodeMap[edge.to].x}%`"
        :y2="`${nodeMap[edge.to].y}%`"
        :class="[
          edge.kind === 'main' ? 'connector-line' : 'sub-connector-line',
          activeEdgeIds.has(edge.id) ? 'opacity-100' : 'opacity-30',
        ]"
      />
    </svg>

    <div class="relative z-20 h-full w-full transition-transform duration-500" :style="{ transform: `scale(${graphZoom})` }">
      <div
        v-for="node in graphNodes"
        :key="node.id"
        class="absolute -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-300"
        :style="{ left: `${node.x}%`, top: `${node.y}%` }"
        :class="activeNodeIds.has(node.id) ? 'opacity-100' : 'opacity-40'"
        @click="$emit('selectNode', node.id)"
      >
        <div v-if="node.kind === 'core'" class="flex flex-col items-center">
          <div
            class="node-core relative flex h-24 w-24 flex-col items-center justify-center rounded-full border-4 border-bg-main"
            :class="[coreNodeClass(node), selectedNodeId === node.id ? 'ring-4 ring-primary/40' : '']"
          >
            <span class="text-2xl font-bold text-white drop-shadow-md">{{ coreTicker }}</span>
            <span class="mt-1 text-[10px] font-mono text-white/80">{{ stockDisplayCode ? stockDisplayCode.split('.')[0] : '--' }}</span>
          </div>
          <div class="mt-2 rounded-full border border-primary/30 bg-black/55 px-3 py-1 text-sm font-bold text-primary backdrop-blur-sm">
            {{ stockName }}
          </div>
        </div>

        <div v-else class="flex flex-col items-center">
          <div
            class="flex items-center justify-center rounded-full border-2 bg-bg-card/95 backdrop-blur-sm transition-all"
            :class="[
              node.kind === 'major' ? 'h-14 w-14' : 'h-10 w-10',
              nodeCircleClass(node),
              selectedNodeId === node.id ? 'scale-110 ring-2 ring-primary/50' : 'hover:scale-105',
            ]"
          >
            <span class="material-symbols-outlined" :class="node.kind === 'major' ? 'text-xl' : 'text-sm'">
              {{ node.icon }}
            </span>
          </div>
          <div class="mt-1 text-center">
            <div v-if="node.kind === 'major'" class="mb-0.5 text-[10px] text-text-sub">{{ groupLabel(node.group) }}</div>
            <div class="rounded border border-white/10 bg-black/55 px-2 py-0.5 text-xs font-semibold text-white">
              {{ node.label }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="absolute left-4 top-4 z-30 rounded-lg border border-primary/20 bg-black/60 p-3 backdrop-blur-md">
      <div class="mb-2 text-[10px] font-semibold uppercase tracking-wider text-text-sub">节点状态说明</div>
      <div class="flex items-center gap-3 text-xs">
        <div class="flex items-center gap-1.5">
          <span class="h-2 w-2 rounded-full bg-market-red shadow-[0_0_5px_rgba(245,63,63,0.8)]"></span>
          <span class="text-white/80">利好</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="h-2 w-2 rounded-full bg-market-green shadow-[0_0_5px_rgba(0,180,42,0.8)]"></span>
          <span class="text-white/80">利空</span>
        </div>
        <div class="flex items-center gap-1.5">
          <span class="h-2 w-2 rounded-full bg-gray-500"></span>
          <span class="text-white/80">中性</span>
        </div>
      </div>
    </div>

    <div class="absolute bottom-5 left-4 z-30 max-w-[340px] rounded-lg border border-primary/20 bg-black/60 p-3 backdrop-blur-md">
      <div class="mb-1 text-xs font-semibold text-primary">{{ selectedNode.label }}</div>
      <p class="text-xs leading-relaxed text-text-light">{{ selectedNode.description }}</p>
    </div>

    <div class="absolute bottom-6 right-6 z-30 rounded-full border border-primary/20 bg-black/60 p-2 backdrop-blur-md transition-all hover:scale-105 hover:bg-black/80">
      <button
        class="flex h-10 w-10 items-center justify-center rounded-full text-primary transition-all hover:bg-primary/20 hover:text-white"
        :title="graphZoom > 1 ? '还原图谱' : '放大图谱'"
        @click="$emit('toggleZoom')"
      >
        <span class="material-symbols-outlined text-2xl">{{ graphZoom > 1 ? 'zoom_out_map' : 'search' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { GraphEdge, GraphNode, NodeGroup } from '@/composables/useAssetMonitor'

const props = defineProps<{
  graphNodes: GraphNode[]
  graphEdges: GraphEdge[]
  nodeMap: Record<string, GraphNode>
  activeNodeIds: Set<string>
  activeEdgeIds: Set<string>
  selectedNodeId: string
  selectedNode: GraphNode
  stockName: string
  stockDisplayCode: string
  coreTicker: string
  graphZoom: number
}>()

defineEmits<{
  (e: 'selectNode', value: string): void
  (e: 'toggleZoom'): void
}>()

function groupLabel(group: NodeGroup): string {
  if (group === 'policy') return '宏观政策'
  if (group === 'sector') return '行业板块'
  if (group === 'demand') return '下游需求'
  if (group === 'group') return '关联集团'
  if (group === 'material') return '上游原料'
  return '关联公司'
}

function coreNodeClass(node: GraphNode): string {
  if (node.sentiment === 'bullish') return 'bg-gradient-to-br from-market-red to-[#b32f2f] shadow-node-glow-red'
  if (node.sentiment === 'bearish') return 'bg-gradient-to-br from-market-green to-[#0f7e29] shadow-node-glow-green'
  return 'bg-gradient-to-br from-primary to-[#8a7020] shadow-node-glow-gold'
}

function nodeCircleClass(node: GraphNode): string {
  if (node.sentiment === 'bullish') return 'border-market-red text-market-red shadow-node-glow-red'
  if (node.sentiment === 'bearish') return 'border-market-green text-market-green shadow-node-glow-green'
  return 'border-text-sub text-text-sub'
}

void props
</script>

<style scoped>
.graph-grid {
  background-image: radial-gradient(circle, rgba(148, 163, 184, 0.45) 0.8px, transparent 0.8px);
  background-size: 20px 20px;
  opacity: 0.18;
}

.connector-line {
  stroke: url(#goldGradientAsset);
  stroke-width: 1.6;
  fill: none;
  transition: opacity 0.25s ease;
}

.sub-connector-line {
  stroke: #5a6371;
  stroke-width: 1.1;
  stroke-dasharray: 4 4;
  transition: opacity 0.25s ease;
}

.node-core {
  animation: pulse-slow 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.shadow-node-glow-gold {
  box-shadow: 0 0 15px rgba(212, 175, 55, 0.38);
}

.shadow-node-glow-red {
  box-shadow: 0 0 12px rgba(245, 63, 63, 0.38);
}

.shadow-node-glow-green {
  box-shadow: 0 0 12px rgba(0, 180, 42, 0.38);
}

@keyframes pulse-slow {
  0%,
  100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.03);
  }
}
</style>

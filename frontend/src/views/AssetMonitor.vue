<template>
  <div class="flex min-h-screen flex-col overflow-x-hidden bg-bg-main text-white selection:bg-primary selection:text-bg-main">
    <AppHeader variant="compact" />

    <div class="flex min-h-0 flex-1">
      <AssetMonitorSidebar
        v-model:searchQuery="searchQuery"
        v-model:activeStockCode="activeStockCode"
        v-model:notificationsEnabled="notificationsEnabled"
        v-model:thresholdIndexMove="thresholdIndexMove"
        v-model:thresholdNarrativeGrowth="thresholdNarrativeGrowth"
        :matched-stocks="matchedStocks"
        :watchlist="watchlist"
        @add-from-search="addStockFromSearch"
        @add-candidate="addCandidate"
        @remove-stock="removeStock"
      />

      <main class="relative flex min-w-0 flex-1 flex-col overflow-hidden bg-[#0F1319]">
        <AssetMonitorTopPanel
          v-model:activeInterval="activeInterval"
          :time-intervals="timeIntervals"
          :last-updated-text="lastUpdatedText"
          :market-index="snapshot.marketIndex"
          :market-delta="snapshot.deltaMarket"
          :metrics="topMetrics"
        />

        <section class="flex min-h-0 flex-1 flex-col overflow-hidden">
          <div class="flex shrink-0 items-center gap-1 border-b border-primary/20 px-6 pt-4">
            <button
              v-for="tab in tabs"
              :key="tab.key"
              class="relative px-5 py-2.5 text-sm transition-colors"
              :class="
                activeTab === tab.key
                  ? 'rounded-t-lg border-l border-r border-t border-primary/20 bg-bg-card font-bold text-white'
                  : 'group font-medium text-text-sub hover:text-white'
              "
              @click="activeTab = tab.key"
            >
              <span
                v-if="activeTab === tab.key"
                class="absolute left-0 top-0 h-[2px] w-full bg-primary shadow-glow"
              ></span>
              {{ tab.label }}
              <span
                v-if="activeTab !== tab.key"
                class="absolute bottom-[-1px] left-1/2 h-[2px] w-0 -translate-x-1/2 bg-primary transition-all group-hover:w-8"
              ></span>
            </button>
          </div>

          <div class="custom-scrollbar flex min-h-0 flex-1 flex-col gap-6 overflow-y-auto p-6 lg:flex-row">
            <div class="min-h-0 w-full lg:w-[60%]">
              <AssetMonitorRelationGraph
                v-if="activeTab === 'relation'"
                :graph-nodes="graphNodes"
                :graph-edges="graphEdges"
                :node-map="nodeMap"
                :active-node-ids="activeNodeIds"
                :active-edge-ids="activeEdgeIds"
                :selected-node-id="selectedNodeId"
                :selected-node="selectedNode"
                :stock-name="currentStock.name"
                :stock-display-code="currentStock.displayCode"
                :core-ticker="coreTicker"
                :graph-zoom="graphZoom"
                @select-node="selectNode"
                @toggle-zoom="toggleGraphZoom"
              />
              <AssetMonitorInsightList v-else :cards="insightCards" />
            </div>

            <div class="min-h-0 w-full lg:w-[40%]">
              <AssetMonitorRightPanel
                :active-interval="activeInterval"
                :line-path="linePath"
                :area-path="areaPath"
                :market-value="snapshot.marketIndex"
                :contradiction="currentProfile.contradiction"
                :strategy="currentProfile.strategy"
                :selected-node-label="selectedNode.label"
                :selected-node-description="selectedNode.description"
                :node-count="graphNodes.length"
                :insight-count="insightCards.length"
              />
            </div>
          </div>
        </section>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/common/AppHeader.vue'
import AssetMonitorSidebar from '@/components/asset-monitor/AssetMonitorSidebar.vue'
import AssetMonitorTopPanel from '@/components/asset-monitor/AssetMonitorTopPanel.vue'
import AssetMonitorRelationGraph from '@/components/asset-monitor/AssetMonitorRelationGraph.vue'
import AssetMonitorInsightList from '@/components/asset-monitor/AssetMonitorInsightList.vue'
import AssetMonitorRightPanel from '@/components/asset-monitor/AssetMonitorRightPanel.vue'
import { onMounted } from 'vue'
import { useAssetMonitor } from '@/composables/useAssetMonitor'

const {
  tabs,
  timeIntervals,
  activeTab,
  activeInterval,
  activeStockCode,
  selectedNodeId,
  graphZoom,
  searchQuery,
  notificationsEnabled,
  thresholdIndexMove,
  thresholdNarrativeGrowth,
  matchedStocks,
  watchlist,
  currentStock,
  currentProfile,
  graphNodes,
  graphEdges,
  nodeMap,
  selectedNode,
  activeNodeIds,
  activeEdgeIds,
  insightCards,
  topMetrics,
  snapshot,
  linePath,
  areaPath,
  coreTicker,
  lastUpdatedText,
  addStockFromSearch,
  addCandidate,
  removeStock,
  toggleGraphZoom,
  selectNode,
  init,
} = useAssetMonitor()

onMounted(async () => {
  await init()
})
</script>

<template>
  <div class="infinite-scroll" ref="container">
    <slot :items="items" />

    <!-- 哨兵元素，用于检测滚动到底部 -->
    <div ref="sentinel" class="sentinel"></div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-more">
      <el-icon class="is-loading" :size="20">
        <Loading />
      </el-icon>
      <span>加载中...</span>
    </div>

    <!-- 没有更多数据 -->
    <div v-else-if="!hasMore && items.length > 0" class="no-more">
      已加载全部数据
    </div>

    <!-- 空状态 -->
    <div v-if="items.length === 0 && !loading" class="empty-state">
      <el-empty description="暂无数据" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'
import { Loading } from '@element-plus/icons-vue'

interface Props {
  items: any[]
  loading?: boolean
  hasMore?: boolean
  threshold?: number // 触发加载的距离阈值（px）
}

const props = withDefaults(defineProps<Props>(), {
  loading: false,
  hasMore: true,
  threshold: 100,
})

const emit = defineEmits<{
  loadMore: []
}>()

const container = ref<HTMLElement>()
const sentinel = ref<HTMLElement>()

// 使用 Intersection Observer 监听哨兵元素
useIntersectionObserver(
  sentinel,
  ([{ isIntersecting }]) => {
    if (isIntersecting && !props.loading && props.hasMore) {
      emit('loadMore')
    }
  },
  {
    root: container.value,
    rootMargin: `${props.threshold}px`,
  }
)
</script>

<style scoped>
.infinite-scroll {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 自定义滚动条 */
.infinite-scroll::-webkit-scrollbar {
  width: 6px;
}

.infinite-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.infinite-scroll::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 3px;
}

.infinite-scroll::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.5);
}

.sentinel {
  height: 1px;
  margin-top: -1px;
  pointer-events: none;
}

.loading-more {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 20px;
  color: var(--text-secondary, #94a3b8);
  font-size: 14px;
}

.no-more {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary, #94a3b8);
  font-size: 13px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 300px;
}
</style>

<template>
  <component :is="layoutComponent">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="in-out">
        <component :is="Component" />
      </transition>
    </router-view>
  </component>
</template>

<script setup lang="ts">
import { computed, markRaw } from 'vue'
import { useRoute } from 'vue-router'
import DefaultLayout from '@/layouts/DefaultLayout.vue'
import AuthLayout from '@/layouts/AuthLayout.vue'

const route = useRoute()

// 布局映射表
const layouts = {
  default: markRaw(DefaultLayout),
  auth: markRaw(AuthLayout)
}

// 根据路由 meta.layout 动态选择布局组件
const layoutComponent = computed(() => {
  const layoutName = (route.meta.layout as string) || 'default'
  return layouts[layoutName as keyof typeof layouts] || layouts.default
})
</script>

<style>
/* 页面切换过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.15s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>

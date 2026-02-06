<template>
  <nav :class="variantClasses.container">
    <template v-for="item in navItems" :key="item.key">
      <RouterLink
        v-if="item.to"
        :to="item.to"
        :class="getLinkClass(item)"
      >
        {{ item.label }}
      </RouterLink>
      <span v-else :class="getLinkClass(item)">{{ item.label }}</span>
    </template>
  </nav>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

type Variant = 'dashboard' | 'compact' | 'pricing'

interface NavItem {
  key: string
  label: string
  to?: string
  disabled?: boolean
}

const props = defineProps<{ variant: Variant }>()

const route = useRoute()

const navItems: NavItem[] = [
  { key: 'dashboard', label: '实时信息流', to: '/' },
  { key: 'assets', label: '资产监控', disabled: true },
  { key: 'opportunity', label: '机会雷达', to: '/opportunity-radar' },
  { key: 'pricing', label: '定价与权益', to: '/pricing-benefits' }
]

const variantClasses = computed(() => {
  if (props.variant === 'dashboard') {
    return {
      container: 'hidden md:flex items-center gap-8',
      active: 'text-primary font-bold text-sm leading-normal border-b-2 border-primary pb-0.5 hover:text-primary/80 transition-colors',
      inactive: 'text-gray-400 hover:text-white text-sm font-medium leading-normal transition-colors',
      disabled: 'text-gray-500 text-sm font-medium leading-normal cursor-not-allowed'
    }
  }

  if (props.variant === 'pricing') {
    return {
      container: 'hidden md:flex h-full items-center gap-1',
      active: 'px-4 h-full flex items-center text-sm font-bold text-white transition-colors border-b-2 border-gold-400 bg-white/[0.02]',
      inactive: 'px-4 h-full flex items-center text-sm font-medium text-gray-400 hover:text-white transition-colors border-b-2 border-transparent hover:border-white/10',
      disabled: 'px-4 h-full flex items-center text-sm font-medium text-gray-500 cursor-not-allowed'
    }
  }

  return {
    container: 'hidden xl:flex items-center gap-8 h-full',
    active: 'text-sm font-bold nav-active h-full flex items-center cursor-default',
    inactive: 'text-sm font-medium text-gray-400 hover:text-white transition-colors h-full flex items-center',
    disabled: 'text-sm font-medium text-gray-500 h-full flex items-center cursor-not-allowed'
  }
})

const isActive = (to?: string) => {
  if (!to) return false
  if (to === '/') return route.path === '/'
  return route.path.startsWith(to)
}

const getLinkClass = (item: NavItem) => {
  if (item.disabled) return variantClasses.value.disabled
  return isActive(item.to) ? variantClasses.value.active : variantClasses.value.inactive
}
</script>

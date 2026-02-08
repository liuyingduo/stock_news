<template>
  <header :class="headerClass">
    <div class="flex items-center gap-4 text-white">
      <div :class="brandIconClass">
        <span class="material-symbols-outlined" :class="brandIconSize">language</span>
      </div>
      <h2 class="font-display font-bold tracking-tight text-white" :class="brandTextClass">万古经纬</h2>
    </div>

    <div class="flex flex-1 justify-end gap-8">
      <MainNav :variant="navVariant" />

      <div :class="actionContainerClass">
        <div ref="notificationRoot" class="relative">
          <button
            class="relative flex size-9 cursor-pointer items-center justify-center overflow-hidden rounded-full text-white transition-colors hover:bg-border-dark"
            type="button"
            @click.stop="toggleNotificationPanel"
          >
            <span class="material-symbols-outlined text-[20px]" :class="variant === 'compact' ? 'text-primary' : ''">notifications</span>
            <span
              v-if="newMessageCount > 0"
              class="absolute right-1 top-1 h-2 w-2 rounded-full bg-market-red ring-2 ring-bg-main"
            ></span>
          </button>

          <transition
            enter-active-class="transition duration-150 ease-out"
            enter-from-class="translate-y-1 scale-95 opacity-0"
            enter-to-class="translate-y-0 scale-100 opacity-100"
            leave-active-class="transition duration-100 ease-in"
            leave-from-class="translate-y-0 scale-100 opacity-100"
            leave-to-class="translate-y-1 scale-95 opacity-0"
          >
            <div
              v-if="notificationPanelVisible"
              class="notification-glass absolute right-0 top-full z-50 mt-4 w-96 origin-top-right overflow-hidden rounded-xl"
            >
              <div class="flex items-center justify-between border-b border-primary/10 bg-black/20 px-4 py-3">
                <h3 class="flex items-center gap-2 text-sm font-bold text-white">
                  <span class="material-symbols-outlined text-base text-primary">notifications_active</span>
                  消息通知中心
                </h3>
                <span class="rounded border border-white/5 bg-bg-main px-1.5 py-0.5 text-[10px] text-text-sub">
                  {{ newMessageCount }}条新消息
                </span>
              </div>

              <div class="custom-scrollbar max-h-[400px] divide-y divide-white/5 overflow-y-auto">
                <div
                  v-for="item in notificationItems"
                  :key="item.id"
                  class="cursor-pointer p-4 transition-colors hover:bg-white/5"
                >
                  <div class="flex items-start gap-3">
                    <div :class="dotClass(item.level)"></div>
                    <div class="flex-1 space-y-1">
                      <p class="text-xs leading-relaxed text-text-light" v-html="item.message"></p>
                      <div class="flex items-center justify-between">
                        <span class="text-[10px] text-text-sub">{{ item.tag }}</span>
                        <span class="font-mono text-[10px] text-text-sub">{{ item.time }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="border-t border-primary/10 bg-black/40 p-3 text-center backdrop-blur-sm">
                <a class="group/link flex items-center justify-center gap-1 text-xs text-primary transition-colors hover:text-white" href="#">
                  查看全部历史通知
                  <span class="material-symbols-outlined text-[10px] transition-transform group-hover/link:translate-x-0.5">arrow_forward_ios</span>
                </a>
              </div>
            </div>
          </transition>
        </div>

        <button class="flex size-9 cursor-pointer items-center justify-center overflow-hidden rounded-full text-white transition-colors hover:bg-border-dark" type="button">
          <span class="material-symbols-outlined text-[20px]">settings</span>
        </button>

        <div
          v-if="variant === 'pricing'"
          class="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full border border-white/20 bg-gradient-to-br from-gray-700 to-gray-900 text-xs font-bold text-white transition-colors hover:border-gold-400"
          @click="goToProfile"
        >
          JS
        </div>

        <div
          v-else-if="variant === 'compact'"
          class="relative flex h-8 w-8 cursor-pointer items-center justify-center overflow-hidden rounded-full bg-logic-gold text-xs font-bold text-black"
          @click="goToProfile"
        >
          <img
            alt="User"
            class="h-full w-full object-cover"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuCpjU6SGv9xc_WyNPL1jVdNL4LprOyU7V4DznQJpG150ZZIUlDzHZZYxOs80B0fQ78YCIr91u5KTCyzq9kKCE-sOBCZIznfGRku13ZKtaRnDnf_psyrzWoxHqq3lyPp3Cp6oLaf5mFOGczKvvOD316QTNQDUbLjF-tqkllgDUkjYBXWeyNPxgXni-7IyJn-zg4wmgP1Kyn_U7aWGvDsRDmFLo8tY9SPX-BraLF7IfTbrKHbOV151HEV3fo1_myhnum8auONU3JZYxod"
          />
        </div>

        <div
          v-else
          class="ml-2 size-9 cursor-pointer rounded-full border border-border-dark bg-cover bg-center bg-no-repeat"
          data-alt="User profile avatar"
          style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuBUbia3JhBRZmt9-SBRa-UM2qKAQE5c56W_9u8mftczi3vYM5PBMUOFZ4giFDozw3C9vUxRd89vqD49M-2o9LVB33mdz4gc93ZTlkYFV2znQbkrYmOaDa4xGlxdbPWnSo7zKy4Mx94Rwuj38_vnpRxhlYMgwf8O7U7PgSUCsZKxW9RVztJQF8kbSbvGGjo9JSlqjgOaVMBvoCzBjAL9nB7AdEoKQQPEMLU9v1D598vRxnWiDWa2vfV4fMLfIp_jW1nLibbJAhbcx7o6");'
          @click="goToProfile"
        ></div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import MainNav from '@/components/common/MainNav.vue'
import { useRouter } from 'vue-router'

type Variant = 'dashboard' | 'compact' | 'pricing'
type NotificationLevel = 'red' | 'yellow' | 'gold' | 'gray'

interface NotificationItem {
  id: string
  message: string
  tag: string
  time: string
  level: NotificationLevel
  unread: boolean
}

const props = withDefaults(defineProps<{ variant?: Variant }>(), {
  variant: 'dashboard',
})

const router = useRouter()
const notificationRoot = ref<HTMLElement | null>(null)
const notificationPanelVisible = ref(false)

const notificationItems = ref<NotificationItem[]>([
  {
    id: 'n1',
    message:
      '<span class="font-bold text-white">比亚迪</span> <span class="font-mono text-text-sub">(002594.SZ)</span> 市场先生指数单次变动 <span class="font-bold font-mono text-market-red">+22.5%</span> 触发阈值',
    tag: '异动预警',
    time: '2分钟前',
    level: 'red',
    unread: true,
  },
  {
    id: 'n2',
    message:
      '<span class="font-bold text-white">宁德时代</span> <span class="font-mono text-text-sub">(300750.SZ)</span> 置信度由 <span class="font-mono text-white">92%</span> 降至 <span class="font-bold font-mono text-yellow-500">58%</span> 出现剧烈偏移',
    tag: '逻辑警告',
    time: '15分钟前',
    level: 'yellow',
    unread: true,
  },
  {
    id: 'n3',
    message: '<span class="font-bold text-white">碳酸锂</span> 叙事规模瞬时增长 <span class="font-bold font-mono text-market-red">320%</span>',
    tag: '规模突增',
    time: '42分钟前',
    level: 'red',
    unread: true,
  },
  {
    id: 'n4',
    message: '系统将于今晚 24:00 进行例行维护，预计耗时 15 分钟',
    tag: '系统通知',
    time: '1小时前',
    level: 'gold',
    unread: true,
  },
  {
    id: 'n5',
    message:
      '<span class="font-bold text-white">中信证券</span> <span class="font-mono text-text-sub">(600030.SH)</span> 发布半年度业绩预告',
    tag: '个股动态',
    time: '2小时前',
    level: 'gray',
    unread: true,
  },
])

const variant = computed(() => props.variant)

const newMessageCount = computed(() => notificationItems.value.filter((item) => item.unread).length)

const headerClass = computed(() => {
  if (variant.value === 'pricing') {
    return 'relative z-50 flex h-16 w-full items-center justify-between border-b border-white/10 bg-[#050505]/90 px-6 backdrop-blur-md'
  }
  if (variant.value === 'compact') {
    return 'relative z-20 flex h-16 items-center justify-between border-b border-white/5 bg-[#0b0e12] px-6'
  }
  return 'relative z-20 flex shrink-0 items-center justify-between whitespace-nowrap border-b border-solid border-b-border-dark bg-surface-darker px-6 py-3'
})

const navVariant = computed(() => {
  if (variant.value === 'pricing') return 'pricing'
  if (variant.value === 'compact') return 'compact'
  return 'dashboard'
})

const brandIconClass = computed(() => {
  if (variant.value === 'pricing') {
    return 'text-gold-400 text-3xl drop-shadow-[0_0_8px_rgba(212,175,55,0.5)]'
  }
  return 'size-8 flex items-center justify-center rounded-lg border border-primary/50 bg-transparent text-primary shadow-glow-primary'
})

const brandIconSize = computed(() => (variant.value === 'pricing' ? 'text-3xl' : 'text-xl'))
const brandTextClass = computed(() => (variant.value === 'pricing' ? 'text-lg' : 'text-lg'))

const actionContainerClass = computed(() => {
  if (variant.value === 'pricing') return 'flex items-center gap-5'
  if (variant.value === 'compact') return 'flex items-center gap-4 border-l border-white/10 pl-6'
  return 'flex items-center gap-3 border-l border-border-dark pl-6'
})

function dotClass(level: NotificationLevel): string {
  if (level === 'red') return 'mt-0.5 h-2 w-2 shrink-0 rounded-full bg-market-red shadow-[0_0_5px_rgba(245,63,63,0.8)]'
  if (level === 'yellow') return 'mt-0.5 h-2 w-2 shrink-0 rounded-full bg-yellow-500 shadow-[0_0_5px_rgba(234,179,8,0.8)]'
  if (level === 'gold') return 'mt-0.5 h-2 w-2 shrink-0 rounded-full bg-primary'
  return 'mt-0.5 h-2 w-2 shrink-0 rounded-full bg-text-sub'
}

function toggleNotificationPanel() {
  notificationPanelVisible.value = !notificationPanelVisible.value
}

function closeNotificationPanel() {
  notificationPanelVisible.value = false
}

function handleDocumentClick(event: MouseEvent) {
  const target = event.target as Node | null
  if (!notificationPanelVisible.value || !target) return
  if (notificationRoot.value?.contains(target)) return
  closeNotificationPanel()
}

function handleKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') {
    closeNotificationPanel()
  }
}

onMounted(() => {
  document.addEventListener('mousedown', handleDocumentClick)
  document.addEventListener('keydown', handleKeydown)
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleDocumentClick)
  document.removeEventListener('keydown', handleKeydown)
})

const goToProfile = () => {
  router.push('/profile')
}
</script>

<style scoped>
.notification-glass {
  background: rgba(22, 27, 34, 0.85);
  border: 1px solid rgba(212, 175, 55, 0.2);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
</style>

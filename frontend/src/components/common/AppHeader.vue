<template>
  <header :class="headerClass">
    <div class="flex items-center gap-4 text-white">
      <div :class="brandIconClass">
        <span class="material-symbols-outlined" :class="brandIconSize">language</span>
      </div>
      <h2 class="text-white font-bold tracking-tight font-display" :class="brandTextClass">万古经纬</h2>
    </div>
    <div class="flex flex-1 justify-end gap-8">
      <MainNav :variant="navVariant" />
      <div :class="actionContainerClass">
        <button class="flex size-9 cursor-pointer items-center justify-center overflow-hidden rounded-full hover:bg-border-dark text-white transition-colors">
          <span class="material-symbols-outlined text-[20px]">notifications</span>
          <span v-if="variant === 'pricing'" class="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full border border-black"></span>
        </button>
        <button class="flex size-9 cursor-pointer items-center justify-center overflow-hidden rounded-full hover:bg-border-dark text-white transition-colors">
          <span class="material-symbols-outlined text-[20px]">settings</span>
        </button>
        <div
          v-if="variant === 'pricing'"
          class="h-8 w-8 rounded-full bg-gradient-to-br from-gray-700 to-gray-900 border border-white/20 flex items-center justify-center text-xs text-white font-bold cursor-pointer hover:border-gold-400 transition-colors"
          @click="goToProfile"
        >
          JS
        </div>
        <div
          v-else-if="variant === 'compact'"
          class="w-8 h-8 rounded-full bg-logic-gold text-black flex items-center justify-center font-bold text-xs relative overflow-hidden cursor-pointer"
          @click="goToProfile"
        >
          <img
            alt="User"
            class="w-full h-full object-cover"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuCpjU6SGv9xc_WyNPL1jVdNL4LprOyU7V4DznQJpG150ZZIUlDzHZZYxOs80B0fQ78YCIr91u5KTCyzq9kKCE-sOBCZIznfGRku13ZKtaRnDnf_psyrzWoxHqq3lyPp3Cp6oLaf5mFOGczKvvOD316QTNQDUbLjF-tqkllgDUkjYBXWeyNPxgXni-7IyJn-zg4wmgP1Kyn_U7aWGvDsRDmFLo8tY9SPX-BraLF7IfTbrKHbOV151HEV3fo1_myhnum8auONU3JZYxod"
          />
        </div>
        <div
          v-else
          class="bg-center bg-no-repeat aspect-square bg-cover rounded-full size-9 border border-border-dark ml-2 cursor-pointer"
          data-alt="User profile avatar"
          style='background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuBUbia3JhBRZmt9-SBRa-UM2qKAQE5c56W_9u8mftczi3vYM5PBMUOFZ4giFDozw3C9vUxRd89vqD49M-2o9LVB33mdz4gc93ZTlkYFV2znQbkrYmOaDa4xGlxdbPWnSo7zKy4Mx94Rwuj38_vnpRxhlYMgwf8O7U7PgSUCsZKxW9RVztJQF8kbSbvGGjo9JSlqjgOaVMBvoCzBjAL9nB7AdEoKQQPEMLU9v1D598vRxnWiDWa2vfV4fMLfIp_jW1nLibbJAhbcx7o6");'
          @click="goToProfile"
        ></div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import MainNav from '@/components/common/MainNav.vue'
import { useRouter } from 'vue-router'

type Variant = 'dashboard' | 'compact' | 'pricing'

const props = withDefaults(defineProps<{ variant?: Variant }>(), {
  variant: 'dashboard',
})

const router = useRouter()

const variant = computed(() => props.variant)

const headerClass = computed(() => {
  if (variant.value === 'pricing') {
    return 'w-full h-16 border-b border-white/10 bg-[#050505]/90 backdrop-blur-md sticky top-0 z-50 flex items-center justify-between px-6'
  }
  if (variant.value === 'compact') {
    return 'h-16 border-b border-white/5 flex items-center justify-between px-6 bg-[#0b0e12] z-20'
  }
  return 'flex items-center justify-between whitespace-nowrap border-b border-solid border-b-border-dark bg-surface-darker px-6 py-3 shrink-0 z-20'
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
  return 'size-8 flex items-center justify-center bg-transparent border border-primary/50 rounded-lg text-primary shadow-glow-primary'
})

const brandIconSize = computed(() => (variant.value === 'pricing' ? 'text-3xl' : 'text-xl'))
const brandTextClass = computed(() => (variant.value === 'pricing' ? 'text-lg' : 'text-lg'))

const actionContainerClass = computed(() => {
  if (variant.value === 'pricing') return 'flex items-center gap-5'
  if (variant.value === 'compact') return 'flex items-center gap-4 border-l border-white/10 pl-6'
  return 'flex gap-3 items-center border-l border-border-dark pl-6'
})

const goToProfile = () => {
  router.push('/profile')
}
</script>

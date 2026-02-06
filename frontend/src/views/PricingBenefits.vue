<template>
  <div class="bg-background-dark font-sans text-gray-300 antialiased min-h-screen flex flex-col overflow-x-hidden">
    <AppHeader />

    <main class="flex-grow relative z-10">
      <div class="absolute inset-0 z-0 grid-bg pointer-events-none"></div>
      <div class="max-w-7xl mx-auto px-6 py-20 relative z-10">
        <div class="text-center mb-16">
          <h1 class="text-4xl md:text-5xl font-black text-white mb-10 tracking-tight font-sans">
            定价与权益
          </h1>
          <div class="inline-flex bg-surface-light rounded-lg p-1 border border-white/10 relative">
            <div class="relative flex items-center">
              <button
                class="px-6 py-2 rounded-md text-sm font-medium transition-all relative z-10 border border-transparent"
                :class="billingCycle === 'annual' ? 'bg-white/10 text-white shadow-sm border-white/5' : 'text-gray-500 hover:text-white'"
                @click="billingCycle = 'annual'"
              >
                按年订阅
                <span
                  class="absolute -top-2 -right-2 bg-gold-500 text-black text-[9px] font-bold px-1.5 py-0.5 rounded-full pointer-events-none transition-opacity"
                  :class="billingCycle === 'annual' ? 'opacity-100' : 'opacity-70'"
                >
                  SAVE 20%
                </span>
              </button>
              <button
                class="px-6 py-2 rounded-md text-sm font-medium transition-all relative z-10 border border-transparent"
                :class="billingCycle === 'monthly' ? 'bg-white/10 text-white shadow-sm border-white/5' : 'text-gray-500 hover:text-white'"
                @click="billingCycle = 'monthly'"
              >
                按月订阅
              </button>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 items-start mb-12">
          <div class="bg-surface-dark border border-white/10 rounded-xl p-8 card-hover-effect flex flex-col h-full relative group">
            <div class="mb-6">
              <h3 class="text-xl font-bold text-white">基础版</h3>
              <p class="text-xs text-gray-500 font-mono mt-1">入门级市场洞察</p>
            </div>
            <div class="mb-8">
              <span class="text-4xl font-bold font-mono text-white">¥0</span>
              <span class="text-sm text-gray-500 font-mono">/月</span>
            </div>
            <ul class="space-y-4 mb-8 flex-grow">
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">check</span>
                主要指数情绪概览
              </li>
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">check</span>
                延时15分钟信息流
              </li>
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">check</span>
                每日3次AI简报
              </li>
            </ul>
            <button class="w-full py-3 rounded-lg border border-white/20 hover:border-white/40 text-white text-sm font-medium transition-colors">
              当前版本
            </button>
          </div>

          <div class="bg-[#0A0B0E] border border-gold-500/50 rounded-xl p-8 relative flex flex-col h-full transform md:-translate-y-4 shadow-[0_0_40px_rgba(212,175,55,0.08)]">
            <div class="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-gold-500 text-black text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-lg">
              Recommended
            </div>
            <div class="mb-6">
              <h3 class="text-xl font-bold gold-gradient-text">专业版</h3>
              <p class="text-xs text-gold-400/60 font-mono mt-1">全功能专业交易台</p>
            </div>
            <div class="mb-6">
              <div class="flex items-baseline gap-2">
                <span class="text-4xl font-bold font-mono text-gold-400">¥{{ formatMoney(displayPrice) }}</span>
                <span class="text-sm text-gold-500/50 font-mono">/{{ priceSuffix }}</span>
              </div>
              <div v-if="billingCycle === 'annual'" class="mt-3 space-y-1">
                <div class="text-xs text-gray-500 font-mono">
                  原价 <span class="line-through">¥{{ formatMoney(originalAnnualTotal) }}/年</span>
                </div>
                <div class="text-xs text-gold-400 font-mono">
                  优惠价 ¥{{ formatMoney(discountedAnnualTotal) }}/年（省 ¥{{ formatMoney(savingsTotal) }}）
                </div>
              </div>
              <div v-else class="mt-3 text-xs text-gray-500 font-mono">
                按月付费，随时可取消
              </div>
            </div>
            <ul class="space-y-4 mb-8 flex-grow">
              <li class="flex items-center gap-3 text-sm text-white font-medium">
                <span class="material-symbols-outlined text-gold-400 text-[18px]">check_circle</span>
                全量实时信息流
              </li>
              <li class="flex items-center gap-3 text-sm text-white font-medium">
                <span class="material-symbols-outlined text-gold-400 text-[18px]">check_circle</span>
                万古经纬穿透图谱
              </li>
              <li class="flex items-center gap-3 text-sm text-white font-medium">
                <span class="material-symbols-outlined text-gold-400 text-[18px]">check_circle</span>
                价值雷达预警
              </li>
              <li class="flex items-center gap-3 text-sm text-white font-medium">
                <span class="material-symbols-outlined text-gold-400 text-[18px]">check_circle</span>
                无限次AI深度研报
              </li>
              <li class="flex items-center gap-3 text-sm text-white font-medium">
                <span class="material-symbols-outlined text-gold-400 text-[18px]">check_circle</span>
                7x24h 专属客服支持
              </li>
            </ul>
            <button class="w-full py-3 rounded-lg bg-gold-400 hover:bg-gold-300 text-black text-sm font-bold transition-all shadow-lg shadow-gold-400/20">
              立即升级
            </button>
          </div>

          <div class="bg-surface-dark border border-white/10 rounded-xl p-8 card-hover-effect flex flex-col h-full">
            <div class="mb-6">
              <h3 class="text-xl font-bold text-white">机构版</h3>
              <p class="text-xs text-gray-500 font-mono mt-1">定制化量化解决方案</p>
            </div>
            <div class="mb-8">
              <span class="text-4xl font-bold font-mono text-white">Custom</span>
            </div>
            <ul class="space-y-4 mb-8 flex-grow">
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">verified</span>
                包含专业版所有权益
              </li>
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">verified</span>
                API 原始数据访问权限
              </li>
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">verified</span>
                私有化部署支持
              </li>
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">verified</span>
                专属量化策略顾问
              </li>
            </ul>
            <button class="w-full py-3 rounded-lg border border-white/20 hover:border-white/40 text-white text-sm font-medium transition-colors">
              联系销售
            </button>
          </div>
        </div>
      </div>
    </main>

    <footer class="border-t border-white/10 bg-[#020202] py-8">
      <div class="max-w-7xl mx-auto px-6">
        <p class="text-[10px] text-gray-600 font-mono text-center md:text-left">© 2024 WanGuJingWei Inc. All rights reserved</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/common/AppHeader.vue'
import { computed, ref } from 'vue'

const billingCycle = ref<'annual' | 'monthly'>('annual')

const monthlyPrice = 399
const annualDiscountRate = 0.2

const originalAnnualTotal = computed(() => monthlyPrice * 12)
const discountedAnnualTotal = computed(() => Math.round(originalAnnualTotal.value * (1 - annualDiscountRate)))
const savingsTotal = computed(() => originalAnnualTotal.value - discountedAnnualTotal.value)

const displayPrice = computed(() => {
  if (billingCycle.value === 'annual') {
    return Math.round(monthlyPrice * (1 - annualDiscountRate))
  }
  return monthlyPrice
})

const priceSuffix = computed(() => (billingCycle.value === 'annual' ? '月（年付）' : '月'))

const formatMoney = (amount: number) => new Intl.NumberFormat('zh-CN').format(amount)
</script>

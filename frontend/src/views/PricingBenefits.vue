<template>
  <div class="bg-background-dark font-sans text-gray-300 antialiased min-h-screen flex flex-col overflow-x-hidden">
    <AppHeader />

    <main class="flex-grow relative z-10">
      <div class="absolute inset-0 z-0 grid-bg pointer-events-none"></div>
      <div class="max-w-7xl mx-auto px-6 py-20 relative z-10">
        <div class="text-center mb-16">
          <h1 class="text-4xl md:text-5xl font-black text-white mb-10 tracking-tight font-sans">
            瀹氫环涓庢潈鐩?
          </h1>
          <div class="inline-flex bg-surface-light rounded-lg p-1 border border-white/10 relative">
            <div class="relative flex items-center">
              <button
                class="px-6 py-2 rounded-md text-sm font-medium transition-all relative z-10 border border-transparent"
                :class="billingCycle === 'annual' ? 'bg-white/10 text-white shadow-sm border-white/5' : 'text-gray-500 hover:text-white'"
                @click="billingCycle = 'annual'"
              >
                鎸夊勾璁㈤槄
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
                鎸夋湀璁㈤槄
              </button>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 items-start mb-12">
          <div class="bg-surface-dark border border-white/10 rounded-xl p-8 card-hover-effect flex flex-col h-full relative group">
            <div class="mb-6">
              <h3 class="text-xl font-bold text-white">鍩虹鐗</h3>
              <p class="text-xs text-gray-500 font-mono mt-1">鍏ラ棬绾у競鍦烘礊瀵</p>
            </div>
            <div class="mb-8">
              <span class="text-4xl font-bold font-mono text-white">楼0</span>
              <span class="text-sm text-gray-500 font-mono">/鏈</span>
            </div>
            <ul class="space-y-4 mb-8 flex-grow">
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">check</span>
                涓昏鎸囨暟鎯呯华姒傝
              </li>
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">check</span>
                寤舵椂15鍒嗛挓淇℃伅娴?
              </li>
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">check</span>
                姣忔棩3娆I绠€鎶?
              </li>
            </ul>
            <button class="w-full py-3 rounded-lg border border-white/20 hover:border-white/40 text-white text-sm font-medium transition-colors">
              褰撳墠鐗堟湰
            </button>
          </div>

          <div class="bg-[#0A0B0E] border border-gold-500/50 rounded-xl p-8 relative flex flex-col h-full transform md:-translate-y-4 shadow-[0_0_40px_rgba(212,175,55,0.08)]">
            <div class="absolute -top-3 left-1/2 transform -translate-x-1/2 bg-gold-500 text-black text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-wider shadow-lg">
              Recommended
            </div>
            <div class="mb-6">
              <h3 class="text-xl font-bold gold-gradient-text">涓撲笟鐗</h3>
              <p class="text-xs text-gold-400/60 font-mono mt-1">鍏ㄥ姛鑳戒笓涓氫氦鏄撳彴</p>
            </div>
            <div class="mb-6">
              <div class="flex items-baseline gap-2">
                <span class="text-4xl font-bold font-mono text-gold-400">楼{{ formatMoney(displayPrice) }}</span>
                <span class="text-sm text-gold-500/50 font-mono">/{{ priceSuffix }}</span>
              </div>
              <div v-if="billingCycle === 'annual'" class="mt-3 space-y-1">
                <div class="text-xs text-gray-500 font-mono">
                  鍘熶环 <span class="line-through">楼{{ formatMoney(originalAnnualTotal) }}/骞</span>
                </div>
                <div class="text-xs text-gold-400 font-mono">
                  浼樻儬浠?楼{{ formatMoney(discountedAnnualTotal) }}/骞达紙鐪?楼{{ formatMoney(savingsTotal) }}锛?
                </div>
              </div>
              <div v-else class="mt-3 text-xs text-gray-500 font-mono">
                鎸夋湀浠樿垂锛岄殢鏃跺彲鍙栨秷
              </div>
            </div>
            <ul class="space-y-4 mb-8 flex-grow">
              <li class="flex items-center gap-3 text-sm text-white font-medium">
                <span class="material-symbols-outlined text-gold-400 text-[18px]">check_circle</span>
                鍏ㄩ噺瀹炴椂淇℃伅娴?
              </li>
              <li class="flex items-center gap-3 text-sm text-white font-medium">
                <span class="material-symbols-outlined text-gold-400 text-[18px]">check_circle</span>
                涓囧彜缁忕含绌块€忓浘璋?
              </li>
              <li class="flex items-center gap-3 text-sm text-white font-medium">
                <span class="material-symbols-outlined text-gold-400 text-[18px]">check_circle</span>
                浠峰€奸浄杈鹃璀?
              </li>
              <li class="flex items-center gap-3 text-sm text-white font-medium">
                <span class="material-symbols-outlined text-gold-400 text-[18px]">check_circle</span>
                鏃犻檺娆I娣卞害鐮旀姤
              </li>
              <li class="flex items-center gap-3 text-sm text-white font-medium">
                <span class="material-symbols-outlined text-gold-400 text-[18px]">check_circle</span>
                7x24h 涓撳睘瀹㈡湇鏀寔
              </li>
            </ul>
            <button
              class="w-full py-3 rounded-lg bg-gold-400 hover:bg-gold-300 text-black text-sm font-bold transition-all shadow-lg shadow-gold-400/20"
              @click="openPaymentModal"
            >
              绔嬪嵆鍗囩骇
            </button>
          </div>

          <div class="bg-surface-dark border border-white/10 rounded-xl p-8 card-hover-effect flex flex-col h-full">
            <div class="mb-6">
              <h3 class="text-xl font-bold text-white">鏈烘瀯鐗</h3>
              <p class="text-xs text-gray-500 font-mono mt-1">瀹氬埗鍖栭噺鍖栬В鍐虫柟妗</p>
            </div>
            <div class="mb-8">
              <span class="text-4xl font-bold font-mono text-white">Custom</span>
            </div>
            <ul class="space-y-4 mb-8 flex-grow">
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">verified</span>
                鍖呭惈涓撲笟鐗堟墍鏈夋潈鐩?
              </li>
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">verified</span>
                API 鍘熷鏁版嵁璁块棶鏉冮檺
              </li>
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">verified</span>
                绉佹湁鍖栭儴缃叉敮鎸?
              </li>
              <li class="flex items-center gap-3 text-sm text-gray-300">
                <span class="material-symbols-outlined text-gray-500 text-[18px]">verified</span>
                涓撳睘閲忓寲绛栫暐椤鹃棶
              </li>
            </ul>
            <button class="w-full py-3 rounded-lg border border-white/20 hover:border-white/40 text-white text-sm font-medium transition-colors">
              鑱旂郴閿€鍞?
            </button>
          </div>
        </div>
      </div>
    </main>

    <div
      v-if="showPayment"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm px-4"
    >
      <div class="w-full max-w-xl rounded-2xl border border-white/10 bg-[#0f1115] p-6 shadow-2xl">
        <div class="flex items-center justify-between">
          <div>
            <h3 class="text-lg font-bold text-white">鎵爜鏀粯</h3>
            <p class="text-xs text-gray-500 mt-1">鏀粯鎴愬姛鍚庤嚜鍔ㄥ崌绾ц嚦涓撲笟鐗</p>
          </div>
          <button class="text-gray-400 hover:text-white" @click="closePaymentModal">
            <span class="material-symbols-outlined text-[20px]">close</span>
          </button>
        </div>

        <div class="mt-5 flex items-center gap-3">
          <button
            class="flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition-colors"
            :class="paymentChannel === 'wechat' ? 'border-emerald-500 text-emerald-400 bg-emerald-500/10' : 'border-white/10 text-gray-400 hover:text-white'"
            @click="setChannel('wechat')"
          >
            寰俊鏀粯
          </button>
          <button
            class="flex-1 rounded-lg border px-3 py-2 text-sm font-medium transition-colors"
            :class="paymentChannel === 'alipay' ? 'border-sky-500 text-sky-400 bg-sky-500/10' : 'border-white/10 text-gray-400 hover:text-white'"
            @click="setChannel('alipay')"
          >
            鏀粯瀹?
          </button>
        </div>

        <div class="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6 items-center">
          <div class="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-black/30 p-4 min-h-[220px]">
            <div v-if="qrLoading" class="text-sm text-gray-500">鐢熸垚浜岀淮鐮佷腑...</div>
            <img v-else-if="qrDataUrl" :src="qrDataUrl" alt="payment qrcode" class="w-40 h-40" />
            <div v-else class="text-sm text-gray-500">浜岀淮鐮佽幏鍙栧け璐</div>
          </div>
          <div class="space-y-4">
            <div class="text-sm text-gray-300">
              订阅方式：<span class="text-white">{{ billingCycle === 'annual' ? '按年订阅' : '按月订阅' }}</span>
            </div>
            <div class="text-sm text-gray-300">
              支付金额：
              <span class="text-white font-mono">¥{{ formatMoney(payAmount) }}</span>
              <span class="text-gray-500">/{{ billingCycle === 'annual' ? '年' : '月' }}</span>
            </div>
            <div class="text-xs text-gray-500">璇蜂娇鐢ㄦ墜鏈烘壂鐮佸畬鎴愭敮浠</div>
            <div class="flex items-center gap-3">
              <button
                class="px-4 py-2 rounded-lg bg-white/10 text-white text-sm hover:bg-white/20 transition-colors"
                :disabled="statusLoading"
                @click="refreshOrderStatus"
              >
                鎴戝凡瀹屾垚鏀粯
              </button>
              <span v-if="paymentStatus === 'paid'" class="text-emerald-400 text-sm">鏀粯鎴愬姛锛屽凡鍗囩骇</span>
              <span v-else-if="paymentStatus === 'pending'" class="text-gray-500 text-sm">绛夊緟鏀粯</span>
              <span v-else-if="paymentStatus === 'failed'" class="text-red-400 text-sm">鏀粯澶辫触</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <footer class="border-t border-white/10 bg-[#020202] py-8">
      <div class="max-w-7xl mx-auto px-6">
        <p class="text-[10px] text-gray-600 font-mono text-center md:text-left">漏 2024 WanGuJingWei Inc. All rights reserved</p>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import AppHeader from '@/components/common/AppHeader.vue'
import { usePricingPayment } from '@/composables/usePricingPayment'

const {
  billingCycle,
  showPayment,
  paymentChannel,
  qrDataUrl,
  qrLoading,
  statusLoading,
  paymentStatus,
  originalAnnualTotal,
  discountedAnnualTotal,
  savingsTotal,
  displayPrice,
  priceSuffix,
  payAmount,
  formatMoney,
  openPaymentModal,
  closePaymentModal,
  setChannel,
  refreshOrderStatus,
} = usePricingPayment()
</script>



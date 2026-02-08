import { computed, onBeforeUnmount, ref, watch } from 'vue'
import QRCode from 'qrcode'
import { createPaymentOrder, getPaymentOrder, type PaymentChannel, type PaymentOrderResponse } from '@/api/payments'
import { useAuthStore } from '@/stores/auth'

export function usePricingPayment() {
  const billingCycle = ref<'annual' | 'monthly'>('annual')
  const showPayment = ref(false)
  const paymentChannel = ref<PaymentChannel>('wechat')
  const currentOrder = ref<PaymentOrderResponse | null>(null)
  const qrDataUrl = ref('')
  const qrLoading = ref(false)
  const statusLoading = ref(false)
  const paymentStatus = ref<'pending' | 'paid' | 'failed'>('pending')
  const pollTimer = ref<number | null>(null)
  const authStore = useAuthStore()

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

  const payAmount = computed(() => {
    if (billingCycle.value === 'annual') return discountedAnnualTotal.value
    return monthlyPrice
  })

  const createOrderAndQr = async () => {
    qrLoading.value = true
    paymentStatus.value = 'pending'
    qrDataUrl.value = ''

    try {
      const order = await createPaymentOrder({
        plan_id: 'pro',
        billing_cycle: billingCycle.value,
        channel: paymentChannel.value,
      })
      currentOrder.value = order
      qrDataUrl.value = await QRCode.toDataURL(order.qr_code_url, { width: 200, margin: 1 })
      startPolling()
    } catch (_error) {
      paymentStatus.value = 'failed'
    } finally {
      qrLoading.value = false
    }
  }

  const refreshOrderStatus = async () => {
    if (!currentOrder.value) return
    statusLoading.value = true
    try {
      const status = await getPaymentOrder(currentOrder.value.order_id)
      if (status.status === 'paid') {
        paymentStatus.value = 'paid'
        await authStore.fetchUser()
        stopPolling()
      } else if (status.status === 'failed') {
        paymentStatus.value = 'failed'
      } else {
        paymentStatus.value = 'pending'
      }
    } finally {
      statusLoading.value = false
    }
  }

  const startPolling = () => {
    stopPolling()
    pollTimer.value = window.setInterval(() => {
      refreshOrderStatus()
    }, 3000)
  }

  const stopPolling = () => {
    if (pollTimer.value !== null) {
      window.clearInterval(pollTimer.value)
      pollTimer.value = null
    }
  }

  const openPaymentModal = async () => {
    showPayment.value = true
    await createOrderAndQr()
  }

  const closePaymentModal = () => {
    showPayment.value = false
    stopPolling()
    currentOrder.value = null
    qrDataUrl.value = ''
  }

  const setChannel = (channel: PaymentChannel) => {
    if (paymentChannel.value === channel) return
    paymentChannel.value = channel
  }

  watch(paymentChannel, async () => {
    if (!showPayment.value) return
    await createOrderAndQr()
  })

  watch(billingCycle, async () => {
    if (!showPayment.value) return
    await createOrderAndQr()
  })

  onBeforeUnmount(() => {
    stopPolling()
  })

  return {
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
  }
}

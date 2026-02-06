import api from './index'

export type BillingCycle = 'monthly' | 'annual'
export type PaymentChannel = 'wechat' | 'alipay'

export interface PaymentOrderResponse {
  order_id: string
  out_trade_no: string
  plan_id: string
  billing_cycle: BillingCycle
  channel: PaymentChannel
  amount: number
  currency: string
  qr_code_url: string
  status: string
  created_at: string
}

export interface PaymentOrderStatus {
  order_id: string
  status: string
  paid_at?: string | null
  plan_id?: string
  billing_cycle?: string
  channel?: string
}

export interface PaymentPlan {
  id: string
  name: string
  monthly_price: number
  annual_discount_rate: number
  features: string[]
}

export const getPaymentPlans = (): Promise<PaymentPlan[]> => {
  return api.get('/payments/plans')
}

export const createPaymentOrder = (data: {
  plan_id: string
  billing_cycle: BillingCycle
  channel: PaymentChannel
}): Promise<PaymentOrderResponse> => {
  return api.post('/payments/orders', data)
}

export const getPaymentOrder = (orderId: string): Promise<PaymentOrderStatus> => {
  return api.get(`/payments/orders/${orderId}`)
}

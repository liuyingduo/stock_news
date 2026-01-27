import api from './index'
import type { Stock } from './types'

export const getStocks = () => {
  return api.get<Stock[]>('/stocks')
}

export const getStockByCode = (code: string) => {
  return api.get<Stock>(`/stocks/${code}`)
}

export const createStock = (data: Partial<Stock>) => {
  return api.post<Stock>('/stocks', data)
}

export const updateStock = (code: string, data: Partial<Stock>) => {
  return api.put<Stock>(`/stocks/${code}`, data)
}

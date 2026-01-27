import api from './index'
import type { Sector } from './types'

export const getSectors = () => {
  return api.get<Sector[]>('/sectors')
}

export const getSectorByCode = (code: string) => {
  return api.get<Sector>(`/sectors/${code}`)
}

export const createSector = (data: Partial<Sector>) => {
  return api.post<Sector>('/sectors', data)
}

export const updateSector = (code: string, data: Partial<Sector>) => {
  return api.put<Sector>(`/sectors/${code}`, data)
}

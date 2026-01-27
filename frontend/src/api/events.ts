import api from './index'
import type { Event, EventsQuery, AIAnalysis } from './types'

export const getEvents = (params: EventsQuery) => {
  return api.get<Event[]>('/events', { params })
}

export const getEventById = (id: string) => {
  return api.get<Event>(`/events/${id}`)
}

export const createEvent = (data: Partial<Event>) => {
  return api.post<Event>('/events', data)
}

export const updateEvent = (id: string, data: Partial<Event>) => {
  return api.put<Event>(`/events/${id}`, data)
}

export const deleteEvent = (id: string) => {
  return api.delete(`/events/${id}`)
}

export const analyzeEvent = (id: string) => {
  return api.post<Event>(`/events/${id}/analyze`)
}

export const getEventsBySector = (sectorCode: string, limit = 50) => {
  return api.get<Event[]>(`/events/sector/${sectorCode}`, { params: { limit } })
}

export const getEventsByStock = (stockCode: string, limit = 50) => {
  return api.get<Event[]>(`/events/stock/${stockCode}`, { params: { limit } })
}

export const clamp = (value: number, min: number, max: number) => Math.min(max, Math.max(min, value))

export function truncateText(text: string | null | undefined, maxLength: number): string {
  const raw = (text || '').replace(/\s+/g, ' ').trim()
  if (!raw) return '--'
  if (raw.length <= maxLength) return raw
  return `${raw.slice(0, maxLength)}...`
}

export function toSigned(value: number, digits = 1): string {
  const fixed = Math.abs(value).toFixed(digits)
  return `${value >= 0 ? '+' : '-'}${fixed}`
}

export function toChangePercent(current: number, prev: number | null): number {
  if (prev === null) return 0
  if (Math.abs(prev) < 1e-6) return clamp(current * 100, -99.9, 99.9)
  return clamp(((current - prev) / Math.abs(prev)) * 100, -99.9, 99.9)
}

export function formatClock(value: string | null | undefined): string {
  if (!value) return '--:--'
  const d = new Date(value)
  if (Number.isNaN(d.getTime())) return '--:--'
  const hh = String(d.getHours()).padStart(2, '0')
  const mm = String(d.getMinutes()).padStart(2, '0')
  return `${hh}:${mm}`
}

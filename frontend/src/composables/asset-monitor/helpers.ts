import type { Stock } from '@/api/types'
import type { GraphNode, IntervalKey, Profile, Snapshot, WatchItem } from './types'

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value))
}

function hash(text: string): number {
  let h = 2166136261
  for (let i = 0; i < text.length; i += 1) {
    h ^= text.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return Math.abs(h >>> 0)
}

export function shortTime(value: string | null | undefined): string {
  if (!value) return '--:--'
  const dt = new Date(value)
  if (Number.isNaN(dt.getTime())) return '--:--'
  return `${String(dt.getHours()).padStart(2, '0')}:${String(dt.getMinutes()).padStart(2, '0')}`
}

export function normalizeStockCode(raw: string): string {
  const cleaned = raw.trim().toUpperCase().replace(/\s+/g, '')
  if (!cleaned) return ''

  const body = cleaned.split('.')[0]
  const digits = body.replace(/\D/g, '')
  if (!digits) return ''

  return digits.padStart(6, '0').slice(-6)
}

function inferSuffix(code: string): 'SH' | 'SZ' | 'BJ' {
  if (code.startsWith('6')) return 'SH'
  if (code.startsWith('8') || code.startsWith('4')) return 'BJ'
  return 'SZ'
}

export function mapStock(stock: Pick<Stock, 'code' | 'name'>): WatchItem | null {
  const code = normalizeStockCode(stock.code)
  const name = (stock.name || '').trim()
  if (!code || !name) return null
  return { name, code, displayCode: `${code}.${inferSuffix(code)}` }
}

export function unwrapApiResult<T>(value: unknown): T {
  if (value && typeof value === 'object' && 'data' in (value as Record<string, unknown>)) {
    return (value as { data: T }).data
  }
  return value as T
}

export function buildSnapshot(code: string, interval: IntervalKey, profile: Profile): Snapshot {
  const seed = hash(`${code}-${interval}`)
  const ratioMap: Record<IntervalKey, number> = { '1H': 1, '4H': 0.86, '1D': 0.72 }
  const ratio = ratioMap[interval]

  const noise = ((seed % 19) - 9) / 10
  const marketIndex = clamp(profile.baseIndex * ratio + noise * 2, -99, 99)
  const narrative = clamp(profile.baseNarrative * (0.88 + ratio * 0.22) + (seed % 7), 20, 400)
  const impact = clamp(profile.baseImpact * (0.92 + ratio * 0.1) + (seed % 5) - 2, 0, 100)
  const longShort = clamp(profile.baseLongShort * (0.9 + ratio * 0.15) + ((seed % 9) - 4) * 0.02, -1.2, 1.2)
  const confidence = clamp(profile.baseConfidence * (0.95 + ratio * 0.05) + (seed % 5) - 2, 50, 99)

  const deltaMarket = ((seed % 29) - 14) / 10
  const deltaNarrative = ((seed % 37) - 11) / 2.6
  const deltaImpact = ((seed % 21) - 7) / 2.2
  const deltaLongShort = ((seed % 25) - 12) / 3.8
  const deltaConfidence = ((seed % 17) - 8) / 2.5

  const trendPoints: number[] = []
  for (let i = 0; i < 12; i += 1) {
    const phase = i / 11
    const swing = Math.sin(phase * Math.PI * 1.8 + seed * 0.003) * (6 + ratio * 4)
    const slope = (phase - 0.5) * deltaMarket * 5
    trendPoints.push(clamp(marketIndex + swing + slope, -100, 100))
  }

  return {
    marketIndex,
    narrative,
    impact,
    longShort,
    confidence,
    deltaMarket,
    deltaNarrative,
    deltaImpact,
    deltaLongShort,
    deltaConfidence,
    trendPoints,
  }
}

export function buildNodes(profile: Profile, stock: WatchItem): GraphNode[] {
  const stockName = stock.name || '--'
  return [
    {
      id: 'core',
      x: 50,
      y: 50,
      label: stockName,
      icon: 'domain',
      kind: 'core',
      group: 'group',
      sentiment: 'neutral',
      description: `${stockName} 为当前图谱核心节点。`,
    },
    {
      id: 'policy',
      x: 50,
      y: 15,
      label: profile.policy,
      icon: 'policy',
      kind: 'major',
      group: 'policy',
      sentiment: 'bullish',
      description: '政策节点决定估值预期修正速度。',
    },
    {
      id: 'policy_a',
      x: 35,
      y: 10,
      label: profile.policyExtra[0],
      icon: 'eco',
      kind: 'minor',
      group: 'policy',
      sentiment: 'neutral',
      description: '次级政策叙事。',
    },
    {
      id: 'policy_b',
      x: 65,
      y: 10,
      label: profile.policyExtra[1],
      icon: 'shopping_bag',
      kind: 'minor',
      group: 'policy',
      sentiment: 'bullish',
      description: '消费类政策催化。',
    },
    {
      id: 'sector',
      x: 80,
      y: 35,
      label: profile.sector,
      icon: 'factory',
      kind: 'major',
      group: 'sector',
      sentiment: 'neutral',
      description: '行业板块情绪节点。',
    },
    {
      id: 'demand',
      x: 80,
      y: 65,
      label: profile.demand,
      icon: 'ev_station',
      kind: 'major',
      group: 'demand',
      sentiment: 'bullish',
      description: '下游需求变化节点。',
    },
    {
      id: 'group',
      x: 50,
      y: 85,
      label: profile.group,
      icon: 'domain',
      kind: 'major',
      group: 'group',
      sentiment: 'neutral',
      description: '集团协同节点。',
    },
    {
      id: 'material',
      x: 20,
      y: 65,
      label: profile.materialMain,
      icon: 'diamond',
      kind: 'major',
      group: 'material',
      sentiment: 'bearish',
      description: '上游成本压力节点。',
    },
    {
      id: 'material_a',
      x: 8,
      y: 60,
      label: profile.materialExtra[0],
      icon: 'science',
      kind: 'minor',
      group: 'material',
      sentiment: 'neutral',
      description: '细分材料节点。',
    },
    {
      id: 'material_b',
      x: 8,
      y: 75,
      label: profile.materialExtra[1],
      icon: 'battery_full',
      kind: 'minor',
      group: 'material',
      sentiment: 'bearish',
      description: '次级材料节点。',
    },
    {
      id: 'company',
      x: 20,
      y: 35,
      label: profile.companyMain,
      icon: 'memory',
      kind: 'major',
      group: 'company',
      sentiment: 'neutral',
      description: '关联公司节点。',
    },
    {
      id: 'company_a',
      x: 8,
      y: 25,
      label: profile.companyExtra[0],
      icon: 'battery_charging_full',
      kind: 'minor',
      group: 'company',
      sentiment: 'bullish',
      description: '子业务增长节点。',
    },
    {
      id: 'company_b',
      x: 8,
      y: 45,
      label: profile.companyExtra[1],
      icon: 'directions_car',
      kind: 'minor',
      group: 'company',
      sentiment: 'neutral',
      description: '新业务试错节点。',
    },
  ]
}

export function buildFallbackProfile(stockName: string): Profile {
  return {
    baseIndex: 58,
    baseNarrative: 92,
    baseImpact: 72,
    baseLongShort: 0.22,
    baseConfidence: 85,
    policy: '监管政策边际变化',
    policyExtra: ['流动性调节', '行业扶持导向'],
    sector: '核心业务板块',
    demand: '终端需求恢复',
    group: `${stockName || '--'} 产业链`,
    materialMain: '关键原材料',
    materialExtra: ['上游成本', '库存周期'],
    companyMain: '关联子公司',
    companyExtra: ['渠道业务', '海外业务'],
    contradiction: '业绩修复预期与估值反弹节奏不完全匹配。',
    strategy: '优先观察需求确认信号，在回调区间分批建仓。',
  }
}

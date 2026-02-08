export type AssetTabKey = 'logic' | 'relation'
export type IntervalKey = '1H' | '4H' | '1D'
export type NodeKind = 'core' | 'major' | 'minor'
export type NodeGroup = 'policy' | 'sector' | 'demand' | 'group' | 'material' | 'company'
export type NodeSentiment = 'bullish' | 'bearish' | 'neutral'

export interface WatchItem {
  name: string
  code: string
  displayCode: string
}

export interface GraphNode {
  id: string
  x: number
  y: number
  label: string
  icon: string
  kind: NodeKind
  group: NodeGroup
  sentiment: NodeSentiment
  description: string
}

export interface GraphEdge {
  id: string
  from: string
  to: string
  kind: 'main' | 'sub'
}

export interface InsightCard {
  id: string
  title: string
  stance: '利好' | '利空'
  confidence: number
  sourceCount: number
  summary: string
  time: string
  references: string[]
}

export interface Snapshot {
  marketIndex: number
  narrative: number
  impact: number
  longShort: number
  confidence: number
  deltaMarket: number
  deltaNarrative: number
  deltaImpact: number
  deltaLongShort: number
  deltaConfidence: number
  trendPoints: number[]
}

export interface Profile {
  baseIndex: number
  baseNarrative: number
  baseImpact: number
  baseLongShort: number
  baseConfidence: number
  policy: string
  policyExtra: [string, string]
  sector: string
  demand: string
  group: string
  materialMain: string
  materialExtra: [string, string]
  companyMain: string
  companyExtra: [string, string]
  contradiction: string
  strategy: string
}

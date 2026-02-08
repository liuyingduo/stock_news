import type { AssetTabKey, GraphEdge, IntervalKey, Profile, WatchItem } from './types'

export const timeIntervals: IntervalKey[] = ['1H', '4H', '1D']

export const tabs: Array<{ key: AssetTabKey; label: string }> = [
  { key: 'logic', label: '逻辑洞察' },
  { key: 'relation', label: '关联图谱' },
]

export const intervalHours: Record<IntervalKey, number> = {
  '1H': 1,
  '4H': 4,
  '1D': 24,
}

export const emptyWatchItem: WatchItem = {
  name: '',
  code: '',
  displayCode: '',
}

export const baseEdges: GraphEdge[] = [
  { id: 'e-core-policy', from: 'core', to: 'policy', kind: 'main' },
  { id: 'e-core-sector', from: 'core', to: 'sector', kind: 'main' },
  { id: 'e-core-demand', from: 'core', to: 'demand', kind: 'main' },
  { id: 'e-core-group', from: 'core', to: 'group', kind: 'main' },
  { id: 'e-core-material', from: 'core', to: 'material', kind: 'main' },
  { id: 'e-core-company', from: 'core', to: 'company', kind: 'main' },
  { id: 'e-policy-a', from: 'policy', to: 'policy_a', kind: 'sub' },
  { id: 'e-policy-b', from: 'policy', to: 'policy_b', kind: 'sub' },
  { id: 'e-material-a', from: 'material', to: 'material_a', kind: 'sub' },
  { id: 'e-material-b', from: 'material', to: 'material_b', kind: 'sub' },
  { id: 'e-company-a', from: 'company', to: 'company_a', kind: 'sub' },
  { id: 'e-company-b', from: 'company', to: 'company_b', kind: 'sub' },
]

export const profileMap: Record<string, Profile> = {
  '002594': {
    baseIndex: 78,
    baseNarrative: 128,
    baseImpact: 85,
    baseLongShort: 0.82,
    baseConfidence: 92,
    policy: '购置税优惠',
    policyExtra: ['碳中和目标', '促消费政策'],
    sector: '汽车零部件',
    demand: '终端充电桩',
    group: '比亚迪集团',
    materialMain: '碳酸锂/钴',
    materialExtra: ['氢氧化锂', '磷酸铁锂'],
    companyMain: '比亚迪半导体',
    companyExtra: ['弗迪电池', '仰望汽车'],
    contradiction: '海外建厂与品牌上行提供中长期估值支撑，但国内价格竞争压制单车毛利。',
    strategy: '短线关注政策催化和销量兑现，中线等待原材料企稳后分批布局。',
  },
  '600519': {
    baseIndex: 64,
    baseNarrative: 104,
    baseImpact: 80,
    baseLongShort: 0.55,
    baseConfidence: 89,
    policy: '消费复苏政策',
    policyExtra: ['扩内需措施', '渠道税改预期'],
    sector: '白酒板块',
    demand: '高端宴席需求',
    group: '茅台集团',
    materialMain: '高粱/包材',
    materialExtra: ['玻璃瓶', '物流成本'],
    companyMain: '系列酒业务',
    companyExtra: ['渠道数字化', '国际化业务'],
    contradiction: '需求韧性较强，但渠道库存与价格带竞争加剧。',
    strategy: '关注批价与动销同步改善信号，避免需求验证不足时追高。',
  },
  '300750': {
    baseIndex: 71,
    baseNarrative: 115,
    baseImpact: 83,
    baseLongShort: 0.68,
    baseConfidence: 90,
    policy: '储能补贴延续',
    policyExtra: ['电池回收政策', '海外关税博弈'],
    sector: '动力电池',
    demand: '储能项目招标',
    group: '宁德时代系',
    materialMain: '正极材料',
    materialExtra: ['锂盐价格', '隔膜产能'],
    companyMain: '换电生态',
    companyExtra: ['麒麟电池', '海外基地'],
    contradiction: '技术优势仍在，但行业扩产导致价格压力持续。',
    strategy: '跟踪海外订单与新品放量节奏，结合预期差做波段配置。',
  },
  '600030': {
    baseIndex: 52,
    baseNarrative: 86,
    baseImpact: 74,
    baseLongShort: 0.34,
    baseConfidence: 87,
    policy: '资本市场改革',
    policyExtra: ['并购重组新规', '两融政策优化'],
    sector: '证券板块',
    demand: '交易活跃度',
    group: '中信金融平台',
    materialMain: '自营资产',
    materialExtra: ['固收波动', '权益仓位'],
    companyMain: '投行业务',
    companyExtra: ['财富管理', '机构业务'],
    contradiction: '政策预期改善，但成交与风险偏好恢复斜率不足。',
    strategy: '关注政策落地与成交放大共振窗口，防守仓位优先配置龙头券商。',
  },
}

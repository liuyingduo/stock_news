export interface CategoryType {
  key: string
  label: string
}

export interface CategoryGroup {
  key: string
  label: string
  types: CategoryType[]
}

export const categoryGroups: CategoryGroup[] = [
  {
    key: 'global_macro',
    label: '全球大事',
    types: [
      { key: 'geopolitics', label: '地缘政治' },
      { key: 'macro_econ', label: '宏观经济' },
    ],
  },
  {
    key: 'policy',
    label: '政策风向',
    types: [
      { key: 'regulatory', label: '监管政策' },
      { key: 'liquidity', label: '资金流向' },
      { key: 'sentiment', label: '市场情绪' },
    ],
  },
  {
    key: 'industry',
    label: '行业动向',
    types: [
      { key: 'tech_innov', label: '科技创新' },
      { key: 'supply_chain', label: '供应链' },
      { key: 'price_vol', label: '价格波动' },
    ],
  },
  {
    key: 'company',
    label: '公司动态',
    types: [
      { key: 'fin_perf', label: '业绩披露' },
      { key: 'order_contract', label: '订单合同' },
      { key: 'merger_re', label: '并购重组' },
      { key: 'capital_action', label: '资本运作' },
      { key: 'buyback', label: '股份回购' },
      { key: 'holder_change', label: '股东变动' },
      { key: 'insider_trans', label: '内部交易' },
      { key: 'risk_crisis', label: '风险危机' },
      { key: 'litigation', label: '诉讼仲裁' },
      { key: 'info_change', label: '信息变更' },
      { key: 'ops_info', label: '运营信息' },
      { key: 'other', label: '其他' },
    ],
  },
]

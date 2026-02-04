import type { EventType } from '../api/types'

/**
 * 获取分类对应的 CSS 类名
 * @param category 事件分类
 * @returns CSS 类名
 */
export const getCategoryClass = (category: string): string => {
    const classes: Record<string, string> = {
        global_macro: 'category-geopolitics',
        policy: 'category-policy',
        industry: 'category-economy',
        company: 'category-company',
    }
    return classes[category] || 'category-others'
}

/**
 * 获取分类对应的中文标签
 * @param category 事件分类
 * @returns 中文标签
 */
export const getCategoryLabel = (category: string): string => {
    const labels: Record<string, string> = {
        global_macro: '全球大事',
        policy: '政策风向',
        industry: '行业动向',
        company: '公司动态',
    }
    return labels[category] || category.toUpperCase()
}

/**
 * 获取事件类型对应的 Element Plus Tag 类型
 * @param type 事件类型
 * @returns Tag 类型
 */
export const getTypeTagType = (type: EventType): 'primary' | 'success' | 'info' | 'warning' | 'danger' | undefined => {
    const typeMap: Record<string, 'primary' | 'success' | 'info' | 'warning' | 'danger'> = {
        risk_crisis: 'danger',
        litigation: 'danger',
        regulatory: 'danger',
        geopolitics: 'danger',

        sentiment: 'warning',
        price_vol: 'warning',
        holder_change: 'warning',
        macro_econ: 'warning',

        tech_innov: 'info',
        order_contract: 'info',
        supply_chain: 'info',
        insider_trans: 'info',
        ops_info: 'info',
        info_change: 'info',
        other: 'info',

        capital_action: 'success',
        liquidity: 'success',
        fin_perf: 'success',
        merger_re: 'success',
        buyback: 'success',
    }
    return typeMap[type]
}

/**
 * 获取事件类型对应的中文标签
 * @param type 事件类型
 * @returns 中文标签
 */
export const getTypeLabel = (type: EventType): string => {
    const labels: Record<string, string> = {
        geopolitics: '地缘政治',
        macro_econ: '宏观经济',

        regulatory: '监管政策',
        liquidity: '资金流向',
        sentiment: '市场情绪',

        tech_innov: '科技创新',
        supply_chain: '供应链',
        price_vol: '价格波动',

        fin_perf: '业绩披露',
        order_contract: '订单合同',
        merger_re: '并购重组',
        capital_action: '资本运作',
        buyback: '股份回购',
        holder_change: '股东变动',
        insider_trans: '内部交易',

        risk_crisis: '风险危机',
        litigation: '诉讼仲裁',

        info_change: '信息变更',
        ops_info: '运营信息',

        other: '其他事件',
    }
    return labels[type] || type
}

/**
 * 格式化来源显示
 * @param source 原始来源字符串
 * @returns 格式化后的来源
 */
export const formatSource = (source: string | undefined | null): string => {
    if (!source) return '未知来源'
    if (source.includes('财联社')) {
        return '时讯'
    }
    if (source.includes('交易所')) {
        return '证券交易所'
    }
    return source
}

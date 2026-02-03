/**
 * 分值颜色工具函数
 * 用于根据情绪分和影响分返回对应的颜色
 */

/**
 * 获取情绪分对应的颜色
 * @param score 情绪分，范围 -1 到 1
 * @returns 颜色值（十六进制）
 */
export function getSentimentColor(score: number): string {
  if (score > 0.7) return '#ef4444'      // 极度利好（红）
  if (score > 0.3) return '#f97316'      // 利好（橙）
  if (score > -0.1) return '#94a3b8'     // 中性（灰）
  if (score > -0.7) return '#64748b'     // 利空（深灰）
  return '#22c55e'                       // 极度利空（绿）
}

/**
 * 获取情绪分对应的 CSS 变量名
 * @param score 情绪分，范围 -1 到 1
 * @returns CSS 变量名
 */
export function getSentimentColorVar(score: number): string {
  if (score > 0.7) return 'var(--score-bullish)'
  if (score > 0.3) return 'var(--score-bullish-mid)'
  if (score > -0.1) return 'var(--score-neutral)'
  if (score > -0.7) return 'var(--score-bearish-mid)'
  return 'var(--score-bearish)'
}

/**
 * 获取情绪分对应的描述文本
 * @param score 情绪分，范围 -1 到 1
 * @returns 描述文本
 */
export function getSentimentLabel(score: number): string {
  if (score > 0.7) return '极度利好'
  if (score > 0.3) return '利好'
  if (score > -0.1) return '中性'
  if (score > -0.7) return '利空'
  return '极度利空'
}

/**
 * 获取影响分对应的颜色
 * @param score 影响分，范围 0 到 1
 * @returns 颜色值（十六进制）
 */
export function getImpactColor(score: number): string {
  if (score > 0.7) return '#ef4444'      // 高影响（红）
  if (score > 0.4) return '#f97316'      // 中影响（橙）
  return '#94a3b8'                        // 低影响（灰）
}

/**
 * 获取影响分对应的 CSS 变量名
 * @param score 影响分，范围 0 到 1
 * @returns CSS 变量名
 */
export function getImpactColorVar(score: number): string {
  if (score > 0.7) return 'var(--score-bullish)'
  if (score > 0.4) return 'var(--score-bullish-mid)'
  return 'var(--score-neutral)'
}

/**
 * 获取影响分对应的描述文本
 * @param score 影响分，范围 0 到 1
 * @returns 描述文本
 */
export function getImpactLabel(score: number): string {
  if (score > 0.7) return '重大影响'
  if (score > 0.4) return '中等影响'
  return '轻微影响'
}

/**
 * 判断情绪分是否为利好
 * @param score 情绪分，范围 -1 到 1
 * @returns 是否为利好
 */
export function isBullish(score: number): boolean {
  return score > 0.1
}

/**
 * 判断情绪分是否为利空
 * @param score 情绪分，范围 -1 到 1
 * @returns 是否为利空
 */
export function isBearish(score: number): boolean {
  return score < -0.1
}

/**
 * 判断情绪分是否为中性
 * @param score 情绪分，范围 -1 到 1
 * @returns 是否为中性
 */
export function isNeutral(score: number): boolean {
  return score >= -0.1 && score <= 0.1
}

/**
 * 判断影响分是否为高影响
 * @param score 影响分，范围 0 到 1
 * @returns 是否为高影响
 */
export function isHighImpact(score: number): boolean {
  return score > 0.7
}

/**
 * 判断影响分是否为低影响
 * @param score 影响分，范围 0 到 1
 * @returns 是否为低影响
 */
export function isLowImpact(score: number): boolean {
  return score < 0.4
}

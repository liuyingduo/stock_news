/**
 * 分值样式工具函数
 * 用于根据情绪分、影响分和置信度分返回对应的CSS类名
 */

/**
 * 获取情绪分对应的 CSS 类名
 * Sentiment: Directional - positive is good (green), negative is bad (red)
 * @param score 情绪分
 * @returns CSS 类名
 */
export function getSentimentClass(score: number | undefined | null): string {
  if (score === undefined || score === null) return ''
  const numScore = Number(score)
  if (numScore >= 0.3) return 'sentiment-positive'   // Green
  if (numScore <= -0.3) return 'sentiment-negative'  // Red
  return 'sentiment-neutral'                         // Gray
}

/**
 * 获取影响分对应的 CSS 类名
 * Impact: Magnitude-based - high is prominent (white), medium is emphasized (blue)
 * @param score 影响分
 * @returns CSS 类名
 */
export function getImpactClass(score: number | undefined | null): string {
  if (score === undefined || score === null) return ''
  const numScore = Number(score)
  if (numScore >= 0.7) return 'impact-high'    // High impact
  if (numScore >= 0.4) return 'impact-medium'  // Medium impact
  return 'impact-low'                          // Low impact
}

/**
 * 获取置信度分对应的 CSS 类名
 * Confidence: Reliability - high is trustworthy (green), medium is caution (orange)
 * @param score 置信度分
 * @returns CSS 类名
 */
export function getConfidenceClass(score: number | undefined | null): string {
  if (score === undefined || score === null) return ''
  const numScore = Number(score)
  if (numScore >= 0.8) return 'confidence-high'    // Green
  if (numScore >= 0.5) return 'confidence-medium'  // Orange
  return 'confidence-low'                          // Gray
}


from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List


SOURCE_CONFIDENCE_MAP = {
    "上交所": 0.95,
    "深交所": 0.95,
    "北交所": 0.95,
    "证监会": 0.92,
    "财联社": 0.82,
    "reuters": 0.9,
    "bloomberg": 0.9,
    "default": 0.65,
}

CATEGORY_IMPACT_BASE = {
    "global_macro": 0.82,
    "policy": 0.75,
    "industry": 0.65,
    "company": 0.55,
}

POSITIVE_KEYWORDS = [
    "增长",
    "超预期",
    "突破",
    "中标",
    "回购",
    "降息",
    "放松",
    "improve",
    "beat",
    "upgrade",
]

NEGATIVE_KEYWORDS = [
    "下滑",
    "低于预期",
    "亏损",
    "违约",
    "处罚",
    "诉讼",
    "减持",
    "war",
    "downgrade",
    "risk",
]


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        if v is None:
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def _hours_since_now(dt: Any, now: datetime) -> float:
    if not isinstance(dt, datetime):
        return 9999.0
    return max(0.0, (now - dt).total_seconds() / 3600.0)


def _freshness_score(dt: Any, now: datetime) -> float:
    # 72h 线性衰减，越新分越高
    hours = _hours_since_now(dt, now)
    if hours >= 72:
        return 0.0
    return 100.0 - (hours / 72.0) * 100.0


def _source_confidence(source: Any) -> float:
    if not source:
        return SOURCE_CONFIDENCE_MAP["default"]
    s = str(source).strip().lower()
    for key, score in SOURCE_CONFIDENCE_MAP.items():
        if key == "default":
            continue
        if key.lower() in s:
            return score
    return SOURCE_CONFIDENCE_MAP["default"]


def _keyword_sentiment(text: str) -> float:
    t = text.lower()
    pos = sum(t.count(word.lower()) for word in POSITIVE_KEYWORDS)
    neg = sum(t.count(word.lower()) for word in NEGATIVE_KEYWORDS)
    if pos == 0 and neg == 0:
        return 0.0
    return _clamp((pos - neg) / (pos + neg + 1.0), -1.0, 1.0)


def _heuristic_sentiment(event: Dict[str, Any]) -> float:
    text = f"{event.get('title', '')}\n{event.get('content', '')}"
    base = _keyword_sentiment(text)
    event_type_tokens = " ".join(event.get("event_types") or [])
    type_boost = _keyword_sentiment(event_type_tokens) * 0.2
    return _clamp(base + type_boost, -1.0, 1.0)


def _heuristic_impact(event: Dict[str, Any]) -> float:
    category = event.get("event_category") or "company"
    base = CATEGORY_IMPACT_BASE.get(category, 0.5)
    text_len = len(str(event.get("content") or ""))
    len_boost = min(text_len / 2000.0, 1.0) * 0.15
    type_count = len(event.get("event_types") or [])
    type_boost = min(type_count, 3) * 0.05
    return _clamp(base + len_boost + type_boost, 0.0, 1.0)


def _heuristic_confidence(event: Dict[str, Any]) -> float:
    source_score = _source_confidence(event.get("source"))
    text_len = len(str(event.get("content") or ""))
    length_factor = min(text_len / 1200.0, 1.0) * 0.15
    return _clamp(source_score * 0.85 + length_factor, 0.0, 1.0)


def compute_event_scores(event: Dict[str, Any], now: datetime) -> Dict[str, Any]:
    """
    Core formula:
    - impact_score: LLM impact (0~1) or heuristic estimate
    - sentiment_score: LLM sentiment (-1~1) or keyword-based estimate
    - confidence_score: LLM confidence (0~1) or source+text estimate
    - freshness_score: time decay in 72h (0~100)
    - relevance_score:
      impact*0.45 + abs(sentiment)*0.30 + confidence*0.15 + freshness*0.10
    """
    ai = event.get("ai_analysis") or {}
    has_ai = ai and ai.get("impact_score") is not None and ai.get("sentiment_score") is not None

    if has_ai:
        impact_raw = _clamp(_safe_float(ai.get("impact_score")), 0.0, 1.0)
        sentiment_raw = _clamp(_safe_float(ai.get("sentiment_score")), -1.0, 1.0)
        confidence_raw = _clamp(_safe_float(ai.get("confidence_score"), 0.5), 0.0, 1.0)
        method = "llm"
    else:
        impact_raw = _heuristic_impact(event)
        sentiment_raw = _heuristic_sentiment(event)
        confidence_raw = _heuristic_confidence(event)
        method = "heuristic"

    freshness = _freshness_score(event.get("announcement_date"), now)
    impact = impact_raw * 100.0
    sentiment = sentiment_raw * 100.0
    confidence = confidence_raw * 100.0
    relevance = _clamp(
        impact * 0.45 + abs(sentiment) * 0.30 + confidence * 0.15 + freshness * 0.10,
        0.0,
        100.0,
    )

    if sentiment >= 20:
        direction = "opportunity"
    elif sentiment <= -20:
        direction = "risk"
    else:
        direction = "neutral"

    return {
        "impact_score": round(impact, 2),
        "sentiment_score": round(sentiment, 2),
        "confidence_score": round(confidence, 2),
        "freshness_score": round(freshness, 2),
        "relevance_score": round(relevance, 2),
        "direction": direction,
        "calculation": {
            "method": method,
            "impact_raw": round(impact_raw, 4),
            "sentiment_raw": round(sentiment_raw, 4),
            "confidence_raw": round(confidence_raw, 4),
            "formula": "relevance=impact*0.45+abs(sentiment)*0.30+confidence*0.15+freshness*0.10",
        },
    }


def compute_market_index(cards: List[Dict[str, Any]]) -> float:
    if not cards:
        return 0.0
    # 使用信号强度和置信度加权得到市场指数（-100~100）
    weighted = [
        card["sentiment_score"] * (0.5 + card["confidence_score"] / 200.0) for card in cards
    ]
    return _clamp(sum(weighted) / len(weighted), -100.0, 100.0)

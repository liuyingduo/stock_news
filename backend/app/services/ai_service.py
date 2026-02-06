from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any, Dict, List

from zai import ZhipuAiClient

from app.config import settings
from app.models import AIAnalysis, AffectedMaterial, AffectedSector, AffectedStock


VALID_EVENT_CATEGORIES = {"global_macro", "policy", "industry", "company"}
VALID_EVENT_TYPES = {
    "macro_econ",
    "geopolitics",
    "regulatory",
    "liquidity",
    "sentiment",
    "tech_innov",
    "supply_chain",
    "price_vol",
    "fin_perf",
    "order_contract",
    "merger_re",
    "capital_action",
    "buyback",
    "holder_change",
    "insider_trans",
    "risk_crisis",
    "litigation",
    "info_change",
    "ops_info",
    "other",
}


def _clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


def _as_float(v: Any, default: float) -> float:
    try:
        if v is None:
            return default
        return float(v)
    except (TypeError, ValueError):
        return default


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in model response")
    return json.loads(cleaned[start : end + 1])


class AIService:
    """LLM-based event analyzer with strict schema normalization."""

    def __init__(self):
        if not settings.zhipu_api_key or settings.zhipu_api_key == "your-api-key-here":
            raise ValueError("ZHIPU_API_KEY is not configured")
        self.client = ZhipuAiClient(api_key=settings.zhipu_api_key)
        self.model = getattr(settings, "ai_model", "glm-4.7-flash")

    def _build_prompt(self, event_title: str, event_content: str, needs_classification: bool) -> str:
        classification_hint = (
            "Return both event_category and event_types."
            if needs_classification
            else "Still return event_category and event_types, even if not updating category."
        )
        return f"""
You are a senior financial event analyst.

Task:
1) Extract affected sectors/stocks/materials.
2) Score the event:
   - impact_score: 0 to 1
   - sentiment_score: -1 to 1
   - confidence_score: 0 to 1
3) Explain impact_reason briefly.
4) {classification_hint}

Allowed event_category:
global_macro, policy, industry, company

Allowed event_types:
macro_econ, geopolitics, regulatory, liquidity, sentiment, tech_innov, supply_chain,
price_vol, fin_perf, order_contract, merger_re, capital_action, buyback, holder_change,
insider_trans, risk_crisis, litigation, info_change, ops_info, other

Input title:
{event_title}

Input content:
{event_content}

Strict JSON only:
{{
  "event_category": "company",
  "event_types": ["other"],
  "impact_score": 0.0,
  "sentiment_score": 0.0,
  "confidence_score": 0.5,
  "impact_reason": "string",
  "is_hype": false,
  "entities": {{
    "affected_stocks": [{{"name":"", "code":"", "reason":""}}],
    "affected_sectors": [{{"name":"", "code":"", "reason":""}}],
    "affected_materials": [{{"name":"", "trend":""}}]
  }}
}}
""".strip()

    def _call_model(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500,
            thinking={"type": "disabled"},
        )
        return response.choices[0].message.content.strip()

    def _normalize_result(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        event_category = str(raw.get("event_category") or "company").strip()
        if event_category not in VALID_EVENT_CATEGORIES:
            event_category = "company"

        event_types_raw = raw.get("event_types")
        if not isinstance(event_types_raw, list):
            event_types_raw = []
        event_types = [str(item).strip() for item in event_types_raw if str(item).strip() in VALID_EVENT_TYPES]
        if not event_types:
            event_types = ["other"]

        impact_score = _clamp(_as_float(raw.get("impact_score"), 0.0), 0.0, 1.0)
        sentiment_score = _clamp(_as_float(raw.get("sentiment_score"), 0.0), -1.0, 1.0)
        confidence_score = _clamp(_as_float(raw.get("confidence_score"), 0.5), 0.0, 1.0)
        is_hype = bool(raw.get("is_hype", False))
        impact_reason = str(raw.get("impact_reason") or "AI analysis completed")

        entities = raw.get("entities") if isinstance(raw.get("entities"), dict) else {}
        sectors: List[AffectedSector] = []
        for item in entities.get("affected_sectors", []):
            if not isinstance(item, dict) or not item.get("name"):
                continue
            code = item.get("code") or f"SECTOR_{item['name']}"
            sectors.append(
                AffectedSector(
                    name=str(item["name"]),
                    code=str(code),
                    reason=str(item.get("reason") or ""),
                )
            )

        stocks: List[AffectedStock] = []
        for item in entities.get("affected_stocks", []):
            if not isinstance(item, dict) or not item.get("name"):
                continue
            code = item.get("code") or f"STOCK_{item['name']}"
            stocks.append(
                AffectedStock(
                    name=str(item["name"]),
                    code=str(code),
                    reason=str(item.get("reason") or ""),
                )
            )

        materials: List[AffectedMaterial] = []
        for item in entities.get("affected_materials", []):
            if not isinstance(item, dict) or not item.get("name"):
                continue
            materials.append(
                AffectedMaterial(
                    name=str(item["name"]),
                    trend=str(item.get("trend") or ""),
                )
            )

        return {
            "event_category": event_category,
            "event_types": event_types,
            "impact_score": impact_score,
            "sentiment_score": sentiment_score,
            "confidence_score": confidence_score,
            "is_hype": is_hype,
            "impact_reason": impact_reason,
            "affected_sectors": sectors,
            "affected_stocks": stocks,
            "affected_materials": materials,
        }

    async def analyze_and_classify(
        self,
        event_title: str,
        event_content: str,
        needs_classification: bool = True,
    ) -> Dict[str, Any]:
        prompt = self._build_prompt(event_title, event_content, needs_classification)
        try:
            raw_text = await asyncio.to_thread(self._call_model, prompt)
            raw_json = _extract_json(raw_text)
            normalized = self._normalize_result(raw_json)

            ai_analysis = AIAnalysis(
                impact_score=normalized["impact_score"],
                sentiment_score=normalized["sentiment_score"],
                confidence_score=normalized["confidence_score"],
                is_hype=normalized["is_hype"],
                impact_reason=normalized["impact_reason"],
                affected_sectors=normalized["affected_sectors"],
                affected_stocks=normalized["affected_stocks"],
                affected_materials=normalized["affected_materials"],
                analyzed_at=datetime.utcnow(),
            )
            return {
                "ai_analysis": ai_analysis,
                "event_category": normalized["event_category"],
                "event_types": normalized["event_types"],
            }
        except Exception as exc:
            # Keep pipeline moving on bad/empty model responses.
            return {
                "ai_analysis": AIAnalysis(
                    impact_score=0.0,
                    sentiment_score=0.0,
                    confidence_score=0.0,
                    is_hype=False,
                    impact_reason=f"AI analysis failed: {exc}",
                    affected_sectors=[],
                    affected_stocks=[],
                    affected_materials=[],
                    analyzed_at=datetime.utcnow(),
                ),
                "event_category": "company",
                "event_types": ["other"],
            }

    async def analyze_event(self, event_title: str, event_content: str) -> AIAnalysis:
        """Backward-compatible API used by existing routes."""
        result = await self.analyze_and_classify(
            event_title=event_title,
            event_content=event_content,
            needs_classification=False,
        )
        return result["ai_analysis"]


ai_service = None


def get_ai_service() -> AIService:
    global ai_service
    if ai_service is None:
        try:
            ai_service = AIService()
        except ValueError as exc:
            print(f"Warning: {exc}")
            print("AI service will not be available until API key is configured")
            return None
    return ai_service

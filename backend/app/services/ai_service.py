from __future__ import annotations

import asyncio
import json
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple

try:
    from google import genai
    from google.genai import errors as genai_errors
except Exception:  # pragma: no cover - optional dependency at runtime
    genai = None
    genai_errors = None
from zai import ZhipuAiClient

from app.config import settings
from app.models import AIAnalysis, AffectedMaterial, AffectedSector, AffectedStock
from app.services.database_service import db_service


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

MAX_STOCK_CANDIDATES = 60
MAX_SECTOR_CANDIDATES = 60
ENTITY_CACHE_TTL_SECONDS = 30 * 60
RATE_LIMIT_MAX_RETRIES = 8
RATE_LIMIT_BASE_DELAY_SECONDS = 2.0
RATE_LIMIT_MAX_DELAY_SECONDS = 60.0
AI_ERROR_RESPONSE_PREVIEW_CHARS = 6000

STOCK_CODE_REGEX = re.compile(r"(?<!\d)(?:SH|SZ|BJ)?(\d{6})(?:\.(?:SH|SZ|BJ))?(?!\d)", re.IGNORECASE)
SECTOR_CODE_REGEX = re.compile(r"(?<!\d)(\d{6}\.SI)(?![\dA-Z])", re.IGNORECASE)

# Friendly aliases so .env can use short names while API gets supported model codes.
GEMINI_MODEL_ALIASES: Dict[str, str] = {
    "gemini-3-pro": "gemini-3-pro-preview",
    "gemini-3-flash": "gemini-3-flash-preview",
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


class AIProviderError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class AIService:
    """LLM-based event analyzer with strict schema normalization."""

    def __init__(self):
        self.model = str(getattr(settings, "ai_model", "glm-4.7")).strip()
        self.provider = self._resolve_provider()
        self.zhipu_client: ZhipuAiClient | None = None
        self.gemini_client = None

        if self.provider == "glm":
            if not settings.zhipu_api_key or settings.zhipu_api_key == "your-api-key-here":
                raise ValueError("ZHIPU_API_KEY is not configured")
            self.zhipu_client = ZhipuAiClient(api_key=settings.zhipu_api_key)
        elif self.provider == "gemini":
            if not getattr(settings, "gemini_api_key", ""):
                raise ValueError("GEMINI_API_KEY is not configured")
            if genai is None:
                raise ValueError("google-genai is not installed. Run: uv add google-genai")
            self.gemini_client = genai.Client(api_key=settings.gemini_api_key)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

        self._cache_lock = asyncio.Lock()
        self._entity_cache_ts = 0.0
        self._stock_code_to_name: Dict[str, str] = {}
        self._stock_name_to_code: Dict[str, str] = {}
        self._sector_code_to_name: Dict[str, str] = {}
        self._sector_name_to_code: Dict[str, str] = {}

    def _resolve_provider(self) -> str:
        explicit_provider = str(getattr(settings, "ai_provider", "auto")).strip().lower()
        if explicit_provider in {"glm", "gemini"}:
            return explicit_provider

        # auto mode: infer from model name
        if self.model.lower().startswith("gemini"):
            return "gemini"
        return "glm"

    def _build_prompt(
        self,
        event_title: str,
        event_content: str,
        needs_classification: bool,
        stock_candidates: List[Dict[str, str]],
        sector_candidates: List[Dict[str, str]],
    ) -> str:
        classification_hint = (
            "必须同时返回 event_category 和 event_types。"
            if needs_classification
            else "即使不更新分类，也必须返回 event_category 和 event_types。"
        )
        stock_candidates_json = json.dumps(stock_candidates, ensure_ascii=False)
        sector_candidates_json = json.dumps(sector_candidates, ensure_ascii=False)
        return f"""
你是一名资深金融事件分析师。

任务要求：
1) 提取受影响的板块、股票、原材料。
2) 对事件打分：
   - impact_score：0 到 1
   - sentiment_score：-1 到 1
   - confidence_score：0 到 1
3) 简要说明 impact_reason。
4) {classification_hint}
5) 股票和板块仅输出 code（name 必须为空字符串）。
6) 优先从下方候选列表中选择 code；如果不确定，返回空数组。
7) 语言要求（强制）：所有解释性文本字段必须使用简体中文。
   包括：impact_reason、affected_stocks.reason、affected_sectors.reason、affected_materials.trend。
   这些字段不得输出英文。

允许的 event_category：
global_macro, policy, industry, company

允许的 event_types：
macro_econ, geopolitics, regulatory, liquidity, sentiment, tech_innov, supply_chain,
price_vol, fin_perf, order_contract, merger_re, capital_action, buyback, holder_change,
insider_trans, risk_crisis, litigation, info_change, ops_info, other

输入标题：
{event_title}

输入内容：
{event_content}

候选股票列表：
{stock_candidates_json}

候选板块列表：
{sector_candidates_json}

仅输出严格 JSON：
{{
  "event_category": "company",
  "event_types": ["other"],
  "impact_score": 0.0,
  "sentiment_score": 0.0,
  "confidence_score": 0.5,
  "impact_reason": "请使用中文描述影响逻辑",
  "is_hype": false,
  "entities": {{
    "affected_stocks": [{{"code":"", "name":"", "reason":"请用中文"}}],
    "affected_sectors": [{{"code":"", "name":"", "reason":"请用中文"}}],
    "affected_materials": [{{"name":"", "trend":"请用中文"}}]
  }}
}}
""".strip()

    def _normalize_stock_code(self, raw_code: Any) -> str:
        code = str(raw_code).strip()
        if not code or code.lower() == "nan":
            return ""

        normalized = code.upper()
        if normalized.startswith(("SH", "SZ", "BJ")) and normalized[2:].isdigit():
            normalized = normalized[2:]

        if "." in normalized:
            left, right = normalized.split(".", 1)
            if left.isdigit() and right in {"SH", "SZ", "BJ"}:
                normalized = left

        if normalized.isdigit():
            return normalized.zfill(6)
        return normalized

    def _normalize_sector_code(self, raw_code: Any) -> str:
        code = str(raw_code).strip().upper()
        if not code or code.lower() == "nan":
            return ""
        return code

    async def _refresh_entity_cache(self) -> None:
        stocks = await db_service.get_all_stocks()
        sectors = await db_service.get_all_sectors()

        stock_code_to_name: Dict[str, str] = {}
        stock_name_to_code: Dict[str, str] = {}
        for item in stocks:
            code = self._normalize_stock_code(item.get("code"))
            name = str(item.get("name", "")).strip()
            if not code or not name:
                continue
            stock_code_to_name[code] = name
            stock_name_to_code[name] = code

        sector_code_to_name: Dict[str, str] = {}
        sector_name_to_code: Dict[str, str] = {}
        for item in sectors:
            code = self._normalize_sector_code(item.get("code"))
            name = str(item.get("name", "")).strip()
            if not code or not name:
                continue
            sector_code_to_name[code] = name
            sector_name_to_code[name] = code

        self._stock_code_to_name = stock_code_to_name
        self._stock_name_to_code = stock_name_to_code
        self._sector_code_to_name = sector_code_to_name
        self._sector_name_to_code = sector_name_to_code
        self._entity_cache_ts = time.time()

    async def _ensure_entity_cache(self) -> None:
        now = time.time()
        if now - self._entity_cache_ts < ENTITY_CACHE_TTL_SECONDS and self._stock_code_to_name and self._sector_code_to_name:
            return

        async with self._cache_lock:
            now = time.time()
            if now - self._entity_cache_ts < ENTITY_CACHE_TTL_SECONDS and self._stock_code_to_name and self._sector_code_to_name:
                return
            await self._refresh_entity_cache()

    def _build_candidate_context(self, event_title: str, event_content: str) -> Tuple[List[Dict[str, str]], List[Dict[str, str]]]:
        text = f"{event_title}\n{event_content}"
        seen_stock_codes: set[str] = set()
        seen_sector_codes: set[str] = set()

        stock_candidates: List[Dict[str, str]] = []
        sector_candidates: List[Dict[str, str]] = []

        for match in STOCK_CODE_REGEX.finditer(text):
            code = self._normalize_stock_code(match.group(1))
            if code and code in self._stock_code_to_name and code not in seen_stock_codes:
                seen_stock_codes.add(code)
                stock_candidates.append({"code": code, "name": self._stock_code_to_name[code]})
                if len(stock_candidates) >= MAX_STOCK_CANDIDATES:
                    break

        for name, code in self._stock_name_to_code.items():
            if len(stock_candidates) >= MAX_STOCK_CANDIDATES:
                break
            if len(name) < 2:
                continue
            if name in text and code not in seen_stock_codes:
                seen_stock_codes.add(code)
                stock_candidates.append({"code": code, "name": name})

        for match in SECTOR_CODE_REGEX.finditer(text):
            code = self._normalize_sector_code(match.group(1))
            if code and code in self._sector_code_to_name and code not in seen_sector_codes:
                seen_sector_codes.add(code)
                sector_candidates.append({"code": code, "name": self._sector_code_to_name[code]})
                if len(sector_candidates) >= MAX_SECTOR_CANDIDATES:
                    break

        for name, code in self._sector_name_to_code.items():
            if len(sector_candidates) >= MAX_SECTOR_CANDIDATES:
                break
            if len(name) < 2:
                continue
            if name in text and code not in seen_sector_codes:
                seen_sector_codes.add(code)
                sector_candidates.append({"code": code, "name": name})

        return stock_candidates, sector_candidates

    def _call_glm_model(self, prompt: str) -> str:
        if self.zhipu_client is None:
            raise AIProviderError("GLM client is not initialized")

        response = self.zhipu_client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1500,
            thinking={"type": "disabled"},
        )
        return response.choices[0].message.content.strip()

    def _call_gemini_model(self, prompt: str) -> str:
        if self.gemini_client is None:
            raise AIProviderError("Gemini client is not initialized")

        model_name = GEMINI_MODEL_ALIASES.get(self.model, self.model)
        try:
            response = self.gemini_client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
        except Exception as exc:
            status_code = None
            if genai_errors is not None and isinstance(exc, genai_errors.APIError):
                status_code = getattr(exc, "code", None)
            raise AIProviderError(
                f"Gemini request failed: {exc}",
                status_code=status_code,
            ) from exc

        text = str(getattr(response, "text", "") or "").strip()
        if text:
            return text

        candidates = getattr(response, "candidates", None) or []
        parts_text: List[str] = []
        for candidate in candidates:
            content = getattr(candidate, "content", None)
            parts = getattr(content, "parts", None) or []
            for part in parts:
                part_text = getattr(part, "text", None)
                if part_text:
                    parts_text.append(str(part_text))

        text = "\n".join(parts_text).strip()
        if not text:
            raise AIProviderError("Gemini response has no text content")
        return text

    def _call_model(self, prompt: str) -> str:
        if self.provider == "gemini":
            return self._call_gemini_model(prompt)
        return self._call_glm_model(prompt)

    def _is_rate_limit_error(self, exc: Exception) -> bool:
        status_code = getattr(exc, "status_code", None)
        if status_code == 429:
            return True

        response = getattr(exc, "response", None)
        if response is not None and getattr(response, "status_code", None) == 429:
            return True

        text = str(exc).lower()
        if "429" in text:
            return True
        if "rate limit" in text:
            return True
        if "resource_exhausted" in text:
            return True
        if "quota" in text and ("exceeded" in text or "limit" in text):
            return True
        if "速率限制" in str(exc):
            return True
        if "1302" in text:
            return True
        return False

    async def _call_model_with_retry(self, prompt: str) -> str:
        for attempt in range(1, RATE_LIMIT_MAX_RETRIES + 1):
            try:
                return await asyncio.to_thread(self._call_model, prompt)
            except Exception as exc:
                if not self._is_rate_limit_error(exc) or attempt >= RATE_LIMIT_MAX_RETRIES:
                    raise

                delay = min(
                    RATE_LIMIT_BASE_DELAY_SECONDS * (2 ** (attempt - 1)),
                    RATE_LIMIT_MAX_DELAY_SECONDS,
                )
                print(
                    f"AI rate limit detected (attempt {attempt}/{RATE_LIMIT_MAX_RETRIES}), "
                    f"retrying in {delay:.1f}s..."
                )
                await asyncio.sleep(delay)

        raise RuntimeError("AI call failed after retries")

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
        seen_sector_codes: set[str] = set()
        for item in entities.get("affected_sectors", []):
            if not isinstance(item, dict):
                continue
            raw_code = item.get("code")
            raw_name = str(item.get("name") or "").strip()
            code = self._normalize_sector_code(raw_code)
            if not code and raw_name:
                code = self._sector_name_to_code.get(raw_name, "")
            if not code or code in seen_sector_codes:
                continue
            resolved_name = self._sector_code_to_name.get(code)
            if not resolved_name:
                continue
            seen_sector_codes.add(code)
            sectors.append(
                AffectedSector(
                    name=resolved_name,
                    code=code,
                    reason=str(item.get("reason") or ""),
                )
            )

        stocks: List[AffectedStock] = []
        seen_stock_codes: set[str] = set()
        for item in entities.get("affected_stocks", []):
            if not isinstance(item, dict):
                continue
            raw_code = item.get("code")
            raw_name = str(item.get("name") or "").strip()
            code = self._normalize_stock_code(raw_code)
            if not code and raw_name:
                code = self._stock_name_to_code.get(raw_name, "")
            if not code or code in seen_stock_codes:
                continue
            resolved_name = self._stock_code_to_name.get(code)
            if not resolved_name:
                continue
            seen_stock_codes.add(code)
            stocks.append(
                AffectedStock(
                    name=resolved_name,
                    code=code,
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

    def _print_analysis_error(self, exc: Exception, raw_text: str) -> None:
        print(
            f"AI analysis failed (provider={self.provider}, model={self.model}): {exc}"
        )
        if not raw_text:
            print("AI raw response is empty.")
            return

        if len(raw_text) > AI_ERROR_RESPONSE_PREVIEW_CHARS:
            preview = raw_text[:AI_ERROR_RESPONSE_PREVIEW_CHARS]
            print(
                f"AI raw response is too long ({len(raw_text)} chars), "
                f"printing first {AI_ERROR_RESPONSE_PREVIEW_CHARS} chars:"
            )
            print(preview)
            print("... [truncated]")
            return

        print("AI raw response:")
        print(raw_text)

    async def analyze_and_classify(
        self,
        event_title: str,
        event_content: str,
        needs_classification: bool = True,
    ) -> Dict[str, Any]:
        try:
            await self._ensure_entity_cache()
        except Exception as cache_exc:
            print(f"Warning: failed to refresh entity cache for AI analysis: {cache_exc}")
        stock_candidates, sector_candidates = self._build_candidate_context(event_title, event_content)
        prompt = self._build_prompt(
            event_title,
            event_content,
            needs_classification,
            stock_candidates=stock_candidates,
            sector_candidates=sector_candidates,
        )
        raw_text = ""
        try:
            raw_text = await self._call_model_with_retry(prompt)
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
            self._print_analysis_error(exc, raw_text)
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

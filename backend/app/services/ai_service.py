from zhipuai import ZhipuAI
from app.config import settings
from app.models import AIAnalysis, AffectedStock, AffectedSector, AffectedMaterial
from typing import List
import json
import re


class AIService:
    """AI 分析服务"""

    def __init__(self):
        """初始化 AI 服务"""
        if not settings.zhipu_api_key or settings.zhipu_api_key == "your-api-key-here":
            raise ValueError("ZHIPU_API_KEY is not configured")
        self.client = ZhipuAI(api_key=settings.zhipu_api_key)



    async def analyze_and_classify(
        self, event_title: str, event_content: str, needs_classification: bool = False
    ) -> dict:
        """
        一次性完成实体提取、影响打分和（可选的）事件分类
        返回字典包含 ai_analysis 对象和可能的 event_category, event_type
        """
        classification_instruction = ""
        if needs_classification:
            classification_instruction = """
3. 对事件进行分类，返回 `event_category` 和 `event_type`。
   分类体系：
   【大类】
   - global_events (全球大事)
   - policy_trends (政策风向)
   - industry_trends (行业动向)
   - company_updates (公司动态)

   【子类型】
   - macro_geopolitics (宏观地缘)
   - regulatory_policy (监管政策)
   - market_sentiment (市场情绪)
   - industrial_chain (产业链驱动)
   - core_sector (核心板块)
   - major_event (重大事项)
   - financial_report (财务报告)
   - financing_announcement (融资公告)
   - risk_warning (风险提示)
   - asset_restructuring (资产重组)
   - info_change (信息变更)
   - shareholding_change (持股变动)
   - other (其他)
"""

        prompt = f"""你是一个专业的金融新闻分析专家。请对以下金融新闻进行全面的分析。

新闻标题：{event_title}
新闻内容：{event_content}

请完成以下任务：
1. 提取事件中明确提到的板块、股票、原材料。
   - 仅提取明确提及的，不要联想。
   - 如果没有提及，返回空列表。
2. 对事件影响进行打分（0-10分）并给出简短理由。
   - 10分为最重大利好，0为最重大利空，5为中性。{classification_instruction}

请以JSON格式返回结果，格式如下：
{{
    "impact_score": 评分（0-10）,
    "impact_reason": "打分理由",
    "affected_sectors": [{{"name": "板块名称", "code": "板块代码(可选)"}}],
    "affected_stocks": [{{"name": "股票名称", "code": "股票代码(可选)"}}],
    "affected_materials": [{{"name": "原材料名称"}}],
    "event_category": "分类大类英文标识(可选)",
    "event_type": "子类型英文标识(可选)"
}}

请只返回JSON，不要包含其他说明文字。"""

        result_text = ""
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1500,
            )

            result_text = response.choices[0].message.content.strip()

            # 清理代码块
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                result_text = result_text[start_idx:end_idx + 1]

            result = json.loads(result_text)

            # 构造结果
            affected_sectors = []
            for item in result.get("affected_sectors", []):
                if "code" not in item or not item["code"]:
                    item["code"] = f"SECTOR_{item['name']}"
                affected_sectors.append(AffectedSector(**item))

            affected_stocks = []
            for item in result.get("affected_stocks", []):
                if "code" not in item or not item["code"]:
                    item["code"] = f"STOCK_{item['name']}"
                affected_stocks.append(AffectedStock(**item))

            affected_materials = [
                AffectedMaterial(**item) for item in result.get("affected_materials", [])
            ]

            ai_analysis = AIAnalysis(
                impact_score=result.get("impact_score", 5.0),
                impact_reason=result.get("impact_reason", "AI 分析完成"),
                affected_sectors=affected_sectors,
                affected_stocks=affected_stocks,
                affected_materials=affected_materials,
            )

            response_data = {"ai_analysis": ai_analysis}

            if needs_classification:
                response_data["event_category"] = result.get("event_category")
                response_data["event_type"] = result.get("event_type")

            return response_data

        except Exception as e:
            print(f"Error in analyze_and_classify: {str(e)}")
            # 返回空结果
            return {
                "ai_analysis": AIAnalysis(
                    impact_score=5.0,
                    impact_reason="AI 分析失败",
                    affected_sectors=[],
                    affected_stocks=[],
                    affected_materials=[],
                )
            }




# 全局 AI 服务实例
ai_service = None


def get_ai_service() -> AIService:
    """获取 AI 服务实例"""
    global ai_service
    if ai_service is None:
        try:
            ai_service = AIService()
        except ValueError as e:
            print(f"Warning: {str(e)}")
            print("AI service will not be available until API key is configured")
            return None
    return ai_service

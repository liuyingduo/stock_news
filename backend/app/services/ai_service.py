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

    async def extract_entities(self, event_title: str, event_content: str) -> dict:
        """
        从事件中提取实体（板块、股票、原材料）
        直接提取，不可联想，不可猜测
        """
        prompt = f"""你是一个专业的金融信息提取助手。请从以下金融事件中提取相关信息。

事件标题：{event_title}
事件内容：{event_content}

请严格按照以下要求提取信息：
1. 仅提取事件中明确提到的板块、股票、原材料
2. 不要联想、不要猜测、不要添加事件中未提及的信息
3. 如果某个类别没有提及，返回空列表
4. 股票代码和板块代码如果文本中没有，可以不填

请以JSON格式返回结果，格式如下：
{{
    "affected_sectors": [
        {{"name": "板块名称", "code": "板块代码（如有）"}}
    ],
    "affected_stocks": [
        {{"name": "股票名称", "code": "股票代码（如有）"}}
    ],
    "affected_materials": [
        {{"name": "原材料名称"}}
    ]
}}

请只返回JSON，不要包含其他说明文字。"""

        result_text = ""
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,  # 降低温度以获得更确定的结果
                max_tokens=2000,
            )

            result_text = response.choices[0].message.content.strip()

            # 清理可能的 markdown 代码块标记
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            # 尝试提取JSON（处理可能的额外文本）
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}')

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                result_text = result_text[start_idx:end_idx + 1]

            # 解析 JSON
            result = json.loads(result_text)

            # 构造返回结果
            affected_sectors = []
            for item in result.get("affected_sectors", []):
                # 如果没有代码，使用名称的拼音或默认值
                if "code" not in item or not item["code"]:
                    item["code"] = f"SECTOR_{item['name']}"
                affected_sectors.append(AffectedSector(**item))

            affected_stocks = []
            for item in result.get("affected_stocks", []):
                # 如果没有代码，使用默认值
                if "code" not in item or not item["code"]:
                    item["code"] = f"STOCK_{item['name']}"
                affected_stocks.append(AffectedStock(**item))

            affected_materials = [
                AffectedMaterial(**item) for item in result.get("affected_materials", [])
            ]

            return {
                "affected_sectors": affected_sectors,
                "affected_stocks": affected_stocks,
                "affected_materials": affected_materials,
            }

        except json.JSONDecodeError as e:
            print(f"JSON decode error in extract_entities: {str(e)}")
            print(f"Response text: {result_text[:200]}...")  # 显示前200字符
            # 返回空结果
            return {
                "affected_sectors": [],
                "affected_stocks": [],
                "affected_materials": [],
            }
        except Exception as e:
            print(f"Error extracting entities: {str(e)}")
            if result_text:
                print(f"Response text: {result_text[:200]}...")
            # 返回空结果
            return {
                "affected_sectors": [],
                "affected_stocks": [],
                "affected_materials": [],
            }

    async def score_impact(self, event_title: str, event_content: str) -> dict:
        """
        对事件影响进行打分（0-10分）并给出理由
        10分为最良好，0为最恶劣
        """
        prompt = f"""你是一个专业的金融事件分析专家。请对以下金融事件的影响进行分析和打分。

事件标题：{event_title}
事件内容：{event_content}

请按照以下标准进行评分：
- 9-10分：重大利好，预期将带来显著正面影响
- 7-8分：明显利好，预期带来正面影响
- 5-6分：中性偏正，影响有限或正负影响相当
- 3-4分：中性偏负，有一定负面影响
- 1-2分：明显利空，预期带来负面影响
- 0分：重大利空，预期将带来严重负面影响

请以JSON格式返回结果，格式如下：
{{
    "impact_score": 评分（0-10的浮点数，保留一位小数）,
    "impact_reason": "详细的打分理由，说明为什么给出这个评分，分析事件可能带来的影响"
}}

请只返回JSON，不要包含其他说明文字。"""

        result_text = ""
        try:
            response = self.client.chat.completions.create(
                model="glm-4-flash",
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            result_text = response.choices[0].message.content.strip()

            # 清理可能的 markdown 代码块标记
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()

            # 尝试提取JSON（处理可能的额外文本）
            # 查找第一个 { 和最后一个 }
            start_idx = result_text.find('{')
            end_idx = result_text.rfind('}')

            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                result_text = result_text[start_idx:end_idx + 1]

            # 解析 JSON
            result = json.loads(result_text)

            return {
                "impact_score": result.get("impact_score", 5.0),
                "impact_reason": result.get("impact_reason", "无法生成打分理由"),
            }

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {str(e)}")
            print(f"Response text: {result_text[:200]}...")  # 显示前200字符
            # 返回默认值
            return {
                "impact_score": 5.0,
                "impact_reason": "AI 分析失败，无法生成打分理由",
            }
        except Exception as e:
            print(f"Error scoring impact: {str(e)}")
            if result_text:
                print(f"Response text: {result_text[:200]}...")
            # 返回默认值
            return {
                "impact_score": 5.0,
                "impact_reason": "AI 分析失败，无法生成打分理由",
            }

    async def analyze_event(
        self, event_title: str, event_content: str
    ) -> AIAnalysis:
        """
        对事件进行完整的 AI 分析
        包括实体提取和影响打分
        """
        # 并行执行实体提取和影响打分
        entities_result = await self.extract_entities(event_title, event_content)
        score_result = await self.score_impact(event_title, event_content)

        # 构造 AI 分析结果
        analysis = AIAnalysis(
            impact_score=score_result["impact_score"],
            impact_reason=score_result["impact_reason"],
            affected_sectors=entities_result["affected_sectors"],
            affected_stocks=entities_result["affected_stocks"],
            affected_materials=entities_result["affected_materials"],
        )

        return analysis


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

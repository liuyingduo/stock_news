from zai import ZhipuAiClient
from app.config import settings
from app.models import AIAnalysis, AffectedStock, AffectedSector, AffectedMaterial
from typing import List
import json
import re
from datetime import datetime


class AIService:
    """AI 分析服务"""

    def __init__(self):
        """初始化 AI 服务"""
        if not settings.zhipu_api_key or settings.zhipu_api_key == "your-api-key-here":
            raise ValueError("ZHIPU_API_KEY is not configured")
        self.client = ZhipuAiClient(api_key=settings.zhipu_api_key)



    async def analyze_and_classify(
        self, event_title: str, event_content: str, needs_classification: bool = False
    ) -> dict:
        """
        进行多维度深度分析：实体提取、多重打分（情绪/影响/置信度）、分类
        """
        
        prompt = f"""# Role
你是一名拥有15年经验的资深证券分析师，专注于 A 股及全球金融市场。你擅长穿透财务修辞和媒体炒作，识别公告与新闻背后的真实市场含义及对股价的实质性影响。

# Task
对提供的金融讯息进行多维度深度分析。
1. 识别涉及的实体（股票、板块、原材料）。
2. **判定事件所属的精确分类（严格遵守以下分类体系）**。
3. 根据严密的逻辑给出多空评分。

## Classification System (Strict)
**大类 (event_category)**:
- global_macro (全球宏观/地缘)
- policy (政策监管)
- industry (行业/板块)
- company (个股动态)

**子类型 (event_types) - 请从以下列表中选择最匹配的1-2项**:
[全球与宏观]
- macro_econ (利率/CPI/就业/美联储)
- geopolitics (战争/制裁/外交/地区局势)

[政策与情绪]
- regulatory (证监会新规/指导意见/行政处罚)
- liquidity (降准降息/逆回购/资金流向)
- sentiment (指数异动/破位/情绪面总结)

[行业动向]
- tech_innov (颠覆性技术/量产进展/实验室突破)
- supply_chain (产能/供应链变动)
- price_vol (产品/原材料调价)

[公司动态]
- fin_perf (业绩预增/扭亏/快报/年报)
- order_contract (重大合同/中标/战略框架协议)
- merger_re (并购重组/吸收合并/分拆上市)
- capital_action (定增/配股/可转债/再融资)
- buyback (股份回购/注销/业绩补偿回购)
- holder_change (大股东减持/质押/冻结/被动平仓)
- insider_trans (高管增持/员工持股计划/股权激励)
- risk_crisis (立案调查/退市风险/财务造假/财务疑点)
- litigation (重大诉讼/仲裁/资产冻结)
- info_change (迁址/更名/更换审计机构/人事变动)
- ops_info (董事会决议/股东大会/常规会议)
- other (其他)

# Data Input
- 新闻标题: {event_title}
- 新闻内容: {event_content}

# Analysis Reasoning Logic
1. 含金量分析：对于业绩，区分“经常性”与“非经常性”损益（如政府补贴、变卖房产）。
2. 复合叠加：若同时存在利好与利空（如减持+预增），需计算综合加权分。
3. 情绪穿透：识别电报/新闻中的“夸大词汇”，还原事件本质。
4. 打分逻辑(Multi-Scoring):
    - 情绪分(Sentiment Score): 消息是悲观还是乐观? (范围 -1.0 到 1.0, 如:指数走弱>-0.8, 跌停=-1.0, 涨停=1.0)
    - 影响分(Impact Score): 事情有多大? (范围 0.0 到 1.0, 如:特斯拉量产百万机器人是“高影响”1.0分，而某个小公司的发明专利是“低影响”0.1分)
    - 置信度(Confidence): 消息来源是否权威? (范围 0.0 到 1.0, 如:财联社官宣/交易所公告=1.0, 电报群传闻=0.3)

# DEFINATION
原材料：原材料是指企业在生产过程中，经过加工后构成产品主要实体或辅助实体的各种原始资源或物资。它们处于产业链的最顶端，尚未被加工成最终消费品。

# Output Format (Strict JSON)
{{
    "event_category": "唯一最匹配的大类标识 (e.g. company, policy, industry, global_macro)",
    "event_types": ["子类型标识1", "子类型标识2"],
    "impact_score": 浮点数 (0.0 到 1.0),
    "sentiment_score": 浮点数 (-1.0 到 1.0),
    "confidence_score": 浮点数 (0.0 到 1.0),
    "impact_reason": "结合打分准则和分析逻辑的简短深度理由",
    "entities": {{
        "affected_stocks": [{{"name": "股票名称", "code": "代码(可选)", "reason": "影响逻辑"}}],
        "affected_sectors": [{{"name": "板块名称", "code": "代码(可选)", "reason": "带动或压制逻辑"}}],
        "affected_materials": [{{"name": "原材料名称", "trend": "涨/跌"}}]
    }},
    "is_hype": true/false (判定是否为纯情绪炒作)
}}

如果不涉及特定实体，entities 中的列表可以是空列表。
请只返回严格的 JSON 格式，不要包含 Markdown 代码块标记（如 ```json）。
"""

        result_text = ""
        try:
            response = self.client.chat.completions.create(
                model="glm-4.7-flash",
                messages=[
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=1500,
                thinking={"type": "disabled"}
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

            # 提取实体
            entities = result.get("entities", {})
            
            # 构造结果对象
            affected_sectors = []
            for item in entities.get("affected_sectors", []):
                if "code" not in item or not item["code"]:
                    item["code"] = f"SECTOR_{item['name']}"
                affected_sectors.append(AffectedSector(**item))

            affected_stocks = []
            for item in entities.get("affected_stocks", []):
                if "code" not in item or not item["code"]:
                    item["code"] = f"STOCK_{item['name']}"
                affected_stocks.append(AffectedStock(**item))

            affected_materials = [
                AffectedMaterial(**item) for item in entities.get("affected_materials", [])
            ]

            ai_analysis = AIAnalysis(
                impact_score=result.get("impact_score", 0.0),
                sentiment_score=result.get("sentiment_score", 0.0),
                confidence_score=result.get("confidence_score", 0.5),
                is_hype=result.get("is_hype", False),
                impact_reason=result.get("impact_reason", "AI 分析完成"),
                affected_sectors=affected_sectors,
                affected_stocks=affected_stocks,
                affected_materials=affected_materials,
                analyzed_at=datetime.utcnow() 
            )

            response_data = {"ai_analysis": ai_analysis}
            
            # 总是返回分类信息
            response_data["event_category"] = result.get("event_category")
            response_data["event_types"] = result.get("event_types", [])

            return response_data

        except Exception as e:
            print(f"Error in analyze_and_classify: {str(e)}")
            # 返回空结果
            return {
                "ai_analysis": AIAnalysis(
                    impact_score=0.0,
                    sentiment_score=0.0,
                    confidence_score=0.0,
                    is_hype=False,
                    impact_reason=f"AI 分析失败: {str(e)}",
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

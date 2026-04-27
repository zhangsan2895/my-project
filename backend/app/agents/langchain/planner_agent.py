"""PlannerAgent — 行程规划专家

不挂载工具，直接调用 LLM 整合景点/天气/酒店信息，
输出严格符合 TripPlan Pydantic 模型的 JSON。

关键约束（来自 schemas.py）：
  - Attraction.location: Location  ← 必填，需从景点搜索结果中提取真实坐标
  - Hotel.location: Optional[Location]  ← 可选
  - DayPlan.accommodation: str  ← 住宿类型描述字符串，非 Hotel 对象
  - DayPlan.hotel: Optional[Hotel]  ← 当天推荐酒店对象（可选）
  - WeatherInfo.day_temp / night_temp: int  ← 不要带单位
"""

import logging
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage

from .base import build_chat_openai
from ...models.schemas import TripRequest

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """你是行程规划专家，根据已收集的景点、天气、酒店数据以及 RAG 检索到的目的地攻略知识，生成完整旅行计划。

【数据优先级规则】
1. 高德地图工具结果优先：景点名称、地址、坐标、天气数据、路线等实时事实以高德 MCP 工具结果为准。
2. RAG 攻略知识辅助：推荐理由、避坑建议、预约提醒、适合人群、文化背景、餐饮建议、雨天替代方案等非结构化知识从 RAG 上下文中提取。
3. 若 RAG 与高德工具结果有冲突，以高德实时结果为准。
4. 不要编造 RAG 和工具结果中都没有的事实。

【必须遵守的规则】
1. 只能使用输入数据中已有的景点、酒店、天气信息，不允许编造坐标或地址。
2. Attraction 的 location 字段必须填写真实坐标（从景点数据中提取），不允许填假坐标。
   格式：{"longitude": 116.397026, "latitude": 39.918058}
3. 如果某景点没有坐标，不要安排该景点（跳过）。
4. 温度必须是整数，不要带 °C。
5. 每天安排 2-3 个景点，必须包含早中晚三餐。
6. 从酒店列表中为每天选择一个推荐酒店填入 hotel 字段。
7. 如果天气不佳（雨天、高温、雷暴），优先安排室内景点或低强度路线（参考 RAG 攻略中的替代方案）。
8. overall_suggestions 中必须包含：预约提醒（如有）、交通建议、天气应对建议、适合人群提示等 RAG 增强内容。
9. 输出必须是合法 JSON，不要输出 Markdown 代码块、说明文字或注释。

【必须输出的 JSON 结构】（严格遵守字段名和类型）
{
  "city": "城市名",
  "start_date": "YYYY-MM-DD",
  "end_date": "YYYY-MM-DD",
  "days": [
    {
      "date": "YYYY-MM-DD",
      "day_index": 0,
      "description": "第1天行程概述",
      "transportation": "公共交通",
      "accommodation": "经济型酒店",
      "hotel": {
        "name": "酒店名称",
        "address": "酒店地址",
        "location": {"longitude": 116.397026, "latitude": 39.918058},
        "price_range": "200-400元/晚",
        "rating": "4.5",
        "distance": "距市中心约2公里",
        "type": "经济型酒店",
        "estimated_cost": 300
      },
      "attractions": [
        {
          "name": "景点名称",
          "address": "详细地址",
          "location": {"longitude": 116.397026, "latitude": 39.918058},
          "visit_duration": 120,
          "description": "景点描述",
          "category": "历史文化",
          "ticket_price": 60
        }
      ],
      "meals": [
        {"type": "breakfast", "name": "早餐推荐", "description": "当地特色早餐", "estimated_cost": 30},
        {"type": "lunch", "name": "午餐推荐", "description": "午餐描述", "estimated_cost": 60},
        {"type": "dinner", "name": "晚餐推荐", "description": "晚餐描述", "estimated_cost": 80}
      ]
    }
  ],
  "weather_info": [
    {
      "date": "YYYY-MM-DD",
      "day_weather": "晴",
      "night_weather": "多云",
      "day_temp": 22,
      "night_temp": 12,
      "wind_direction": "南风",
      "wind_power": "1-3级"
    }
  ],
  "overall_suggestions": "总体旅行建议",
  "budget": {
    "total_attractions": 0,
    "total_hotels": 0,
    "total_meals": 0,
    "total_transportation": 0,
    "total": 0
  }
}
"""


def _build_user_message(
    request: TripRequest,
    attractions_json: str,
    weather_json: str,
    hotels_json: str,
    rag_context: str = "",
) -> str:
    rag_section = ""
    if rag_context and rag_context.strip() and rag_context != "（未检索到相关攻略信息）":
        rag_section = f"""
== RAG 检索到的目的地知识（攻略、经验、建议）==
{rag_context}

【说明】上方 RAG 内容仅供参考，用于补充推荐理由、避坑建议、预约提醒、餐饮建议等。
景点坐标、地址、天气等事实信息以下方高德工具数据为准。
"""

    return f"""请根据以下信息生成 {request.city} 的 {request.travel_days} 天旅行计划：

== 基本信息 ==
城市：{request.city}
日期：{request.start_date} 至 {request.end_date}
天数：{request.travel_days} 天
交通方式：{request.transportation}
住宿偏好：{request.accommodation}
偏好标签：{', '.join(request.preferences) if request.preferences else '无'}
额外要求：{request.free_text_input or '无'}
{rag_section}
== 景点数据（来自高德地图工具，事实优先）==
{attractions_json}

== 天气数据（来自高德地图工具，事实优先）==
{weather_json}

== 酒店数据（来自高德地图工具，事实优先）==
{hotels_json}

请严格按照 system prompt 中的 JSON 格式输出旅行计划。只输出 JSON，不要有其他文字。"""


class PlannerAgent:
    """不使用工具，直接调用 LLM 整合信息生成 TripPlan JSON 的规划 Agent。"""

    def __init__(self) -> None:
        self._llm: Any = None

    def _get_llm(self) -> Any:
        if self._llm is None:
            # PlannerAgent 需要最稳定的输出，使用较低 temperature
            self._llm = build_chat_openai(temperature=0.1)
            logger.info("[PlannerAgent] LLM 初始化完成")
        return self._llm

    async def plan(
        self,
        request: TripRequest,
        attractions_json: str,
        weather_json: str,
        hotels_json: str,
        rag_context: str = "",
    ) -> str:
        """整合数据，调用 LLM 生成 TripPlan JSON 字符串。

        Args:
            request: 原始旅行请求。
            attractions_json: AttractionSearchAgent 的原始输出文本。
            weather_json: WeatherQueryAgent 的原始输出文本。
            hotels_json: HotelSearchAgent 的原始输出文本。
            rag_context: RAG 检索到的攻略上下文（可选，为空时跳过）。

        Returns:
            LLM 原始输出文本（应为合法 TripPlan JSON）。
        """
        llm = self._get_llm()
        user_content = _build_user_message(
            request, attractions_json, weather_json, hotels_json, rag_context
        )

        logger.info(
            "[PlannerAgent] 开始规划 city=%s days=%d",
            request.city,
            request.travel_days,
        )

        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=user_content),
        ]
        response = await llm.ainvoke(messages)
        content = response.content if hasattr(response, "content") else str(response)

        logger.info(
            "[PlannerAgent] 输出 (%d chars): %s", len(content), content[:400]
        )
        return content

"""AttractionSearchAgent — 景点搜索专家

只挂载 amap_maps_text_search 工具，输出符合 Attraction schema 的 JSON 数组。

Amap POI 返回的 location 字段格式为 "longitude,latitude" 字符串，
system prompt 中已明确要求拆分并输出为 {"longitude": float, "latitude": float}。
"""

import logging
from typing import List

from langchain_core.tools import BaseTool

from .base import BaseLangChainAgent

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """你是景点搜索专家，负责为旅行规划搜索真实景点信息。

【必须遵守的规则】
1. 必须调用 amap_maps_text_search 工具搜索景点，绝对不允许编造。
2. 从工具返回的 POI 数据中提取信息，不允许虚构任何景点名称、地址或坐标。
3. location 字段通常格式为 "经度,纬度"（如 "116.397026,39.918058"），必须拆分为：
   {"longitude": 116.397026, "latitude": 39.918058}
4. 如果某个景点缺少坐标，可以使用城市中心坐标作为近似值，但必须在 description 中注明。
5. 搜索 8 到 12 个候选景点，涵盖用户偏好。
6. 最终只输出 JSON 数组，不要输出任何 Markdown、说明文字或代码块标记。

【输出格式】
直接输出一个 JSON 数组，每个元素字段如下（只输出数组，不要有其他文字）：
[
  {
    "name": "景点名称",
    "address": "详细地址",
    "location": {"longitude": 116.397026, "latitude": 39.918058},
    "visit_duration": 120,
    "description": "景点描述（50字以内）",
    "category": "景点类别",
    "ticket_price": 60
  }
]

【字段说明】
- visit_duration: 建议游览时长，单位分钟，根据景点规模估算（小景点60，中等120，大景点180）
- ticket_price: 门票价格（元），免费景点填0，不确定填0
- category: 从以下选择：历史文化/自然风光/主题公园/博物馆/公园广场/购物美食/宗教场所/其他
"""


class AttractionSearchAgent(BaseLangChainAgent):
    """使用高德地图文本搜索工具查询景点的 Agent。"""

    def __init__(self, tools: List[BaseTool]) -> None:
        super().__init__(
            agent_name="AttractionSearchAgent",
            system_prompt=_SYSTEM_PROMPT,
            tools=tools,
            temperature=0.1,
        )

    async def search(
        self,
        city: str,
        preferences: List[str],
        days: int,
    ) -> str:
        """搜索景点，返回 JSON 数组字符串。

        Args:
            city: 目标城市。
            preferences: 旅行偏好标签列表（如 ["历史文化", "美食"]）。
            days: 旅行天数，用于估算所需景点数量。

        Returns:
            LLM 输出的原始文本（应为 JSON 数组，可能含 Markdown 包裹）。
        """
        pref_str = "、".join(preferences) if preferences else "综合旅游"
        count = max(8, min(12, days * 3))

        query = (
            f"请搜索{city}的景点，旅行偏好：{pref_str}，旅行天数：{days}天。\n"
            f"需要搜索约 {count} 个候选景点，尽量覆盖偏好类型。\n"
            f"请使用工具搜索，然后输出 JSON 数组（不要 Markdown 代码块）。"
        )

        logger.info(
            "[AttractionSearchAgent] 搜索城市=%s 偏好=%s 天数=%d",
            city,
            pref_str,
            days,
        )
        return await self.ainvoke(query)

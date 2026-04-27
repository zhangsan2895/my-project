"""HotelSearchAgent — 酒店推荐专家

只挂载 amap_maps_text_search 工具，输出符合 Hotel schema 的 JSON 数组。

Hotel 字段：
  name(str), address(str), location(Optional[{longitude, latitude}]),
  price_range(str), rating(str), distance(str), type(str), estimated_cost(int)
"""

import logging
from typing import List, Optional

from langchain_core.tools import BaseTool

from .base import BaseLangChainAgent

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """你是酒店推荐专家，负责搜索目标城市的住宿选项。

【必须遵守的规则】
1. 必须调用 amap_maps_text_search 工具搜索酒店/宾馆/民宿等住宿 POI，不允许编造。
2. 从工具返回的数据中提取真实信息，不允许虚构任何名称、地址或坐标。
3. location 字段通常格式为 "经度,纬度"，必须拆分为：
   {"longitude": float, "latitude": float}
   如果没有坐标信息，location 填 null。
4. 搜索 5 到 8 家候选酒店，覆盖不同价格档次。
5. 最终只输出 JSON 数组，不要输出任何 Markdown、说明文字或代码块标记。

【输出格式】
直接输出一个 JSON 数组，每个元素字段如下（只输出数组，不要有其他文字）：
[
  {
    "name": "酒店名称",
    "address": "酒店地址",
    "location": {"longitude": 116.397026, "latitude": 39.918058},
    "price_range": "200-400元/晚",
    "rating": "4.5",
    "distance": "距市中心约2公里",
    "type": "经济型酒店",
    "estimated_cost": 300
  }
]

【type 参考】豪华酒店/高档酒店/商务酒店/经济型酒店/民宿/青年旅社
【estimated_cost】每晚预估价格（元），从 price_range 取中间值估算
"""


class HotelSearchAgent(BaseLangChainAgent):
    """使用高德地图文本搜索工具查询酒店的 Agent。"""

    def __init__(self, tools: List[BaseTool]) -> None:
        super().__init__(
            agent_name="HotelSearchAgent",
            system_prompt=_SYSTEM_PROMPT,
            tools=tools,
            temperature=0.1,
        )

    async def search_hotels(
        self,
        city: str,
        accommodation: str,
        budget: Optional[str] = None,
    ) -> str:
        """搜索酒店，返回 JSON 数组字符串。

        Args:
            city: 目标城市。
            accommodation: 住宿偏好描述（如 "经济型酒店"）。
            budget: 预算描述（可选）。

        Returns:
            LLM 输出的原始文本（应为 JSON 数组）。
        """
        budget_str = f"，预算参考：{budget}" if budget else ""
        query = (
            f"请搜索{city}的住宿选项，住宿偏好：{accommodation}{budget_str}。\n"
            f"关键词可用：酒店、宾馆、民宿等，覆盖不同档次。\n"
            f"使用工具搜索后，输出 JSON 数组（不要 Markdown 代码块）。"
        )

        logger.info(
            "[HotelSearchAgent] 搜索城市=%s 住宿=%s", city, accommodation
        )
        return await self.ainvoke(query)

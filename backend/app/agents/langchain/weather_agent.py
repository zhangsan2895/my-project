"""WeatherQueryAgent — 天气查询专家

只挂载 amap_maps_weather 工具，输出符合 WeatherInfo schema 的 JSON 数组。

WeatherInfo 字段：
  date, day_weather, night_weather, day_temp(int), night_temp(int),
  wind_direction, wind_power

注意：高德天气 API 通常只返回近 4 天预报；超出范围时禁止编造。
"""

import logging
from typing import List

from langchain_core.tools import BaseTool

from .base import BaseLangChainAgent

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """你是天气查询专家，负责查询目标城市的真实天气预报。

【必须遵守的规则】
1. 必须调用 amap_maps_weather 工具查询天气，绝对不允许编造天气数据。
2. 只输出工具实际返回的天气日期范围内的数据，不允许推测超出工具结果的日期天气。
3. 如果用户请求的日期超出工具返回范围，对超出日期输出：
   {"date": "YYYY-MM-DD", "day_weather": "暂无预报", "night_weather": "暂无预报",
    "day_temp": 0, "night_temp": 0, "wind_direction": "", "wind_power": ""}
4. 温度必须是整数，不要带 °C 等单位。
5. 最终只输出 JSON 数组，不要输出任何 Markdown、说明文字或代码块标记。

【输出格式】
直接输出一个 JSON 数组，每个元素字段如下（只输出数组，不要有其他文字）：
[
  {
    "date": "2026-04-27",
    "day_weather": "晴",
    "night_weather": "多云",
    "day_temp": 22,
    "night_temp": 12,
    "wind_direction": "南风",
    "wind_power": "1-3级"
  }
]
"""


class WeatherQueryAgent(BaseLangChainAgent):
    """使用高德地图天气工具查询天气的 Agent。"""

    def __init__(self, tools: List[BaseTool]) -> None:
        super().__init__(
            agent_name="WeatherQueryAgent",
            system_prompt=_SYSTEM_PROMPT,
            tools=tools,
            temperature=0.0,
        )

    async def query_weather(
        self,
        city: str,
        start_date: str,
        end_date: str,
    ) -> str:
        """查询天气，返回 JSON 数组字符串。

        Args:
            city: 目标城市。
            start_date: 旅行开始日期 YYYY-MM-DD。
            end_date: 旅行结束日期 YYYY-MM-DD。

        Returns:
            LLM 输出的原始文本（应为 JSON 数组）。
        """
        query = (
            f"请查询{city}从 {start_date} 到 {end_date} 的天气预报。\n"
            f"使用工具查询后，按日期输出 JSON 数组（不要 Markdown 代码块）。\n"
            f"注意：工具通常只返回近4天预报，超出范围的日期请标注'暂无预报'。"
        )

        logger.info(
            "[WeatherQueryAgent] 查询城市=%s 日期=%s~%s",
            city,
            start_date,
            end_date,
        )
        return await self.ainvoke(query)

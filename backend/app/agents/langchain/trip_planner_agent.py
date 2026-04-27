"""LangChainTripPlannerAgent — LangChain 版旅行规划编排器（Phase 2）

编排流程（顺序执行）：
  Step 1: AttractionSearchAgent.search()   ← amap_maps_text_search
  Step 2: WeatherQueryAgent.query_weather() ← amap_maps_weather
  Step 3: HotelSearchAgent.search_hotels()  ← amap_maps_text_search
  Step 4: PlannerAgent.plan()               ← 纯 LLM，整合三段数据
  Step 5: json_utils.loads_json()           ← 从 LLM 输出提取 JSON
  Step 6: TripPlan.model_validate()         ← Pydantic v2 校验

工具名称解析策略：
  - 优先按精确名称匹配（amap_maps_text_search / amap_maps_weather）
  - 找不到时按子串模糊匹配（text_search / weather），兼容不同版本命名
"""

import logging
from typing import Optional

from ...models.schemas import TripPlan, TripRequest
from ...tools.langchain_mcp_tools import get_langchain_mcp_tool_manager
from ...utils.json_utils import loads_json
from .attraction_agent import AttractionSearchAgent
from .hotel_agent import HotelSearchAgent
from .planner_agent import PlannerAgent
from .weather_agent import WeatherQueryAgent
from ...rag.retriever import DestinationRAGRetriever, get_destination_rag_retriever

logger = logging.getLogger(__name__)

# 工具名称常量（langchain-mcp-adapters 以 server_name + "_" + tool_name 命名）
_TOOL_TEXT_SEARCH = "amap_maps_text_search"
_TOOL_WEATHER = "amap_maps_weather"


def _find_tool(tool_map: dict, exact_name: str, fallback_substr: str):
    """先精确匹配，找不到时按子串模糊匹配，仍找不到返回 None 并警告。"""
    tool = tool_map.get(exact_name)
    if tool is not None:
        return tool
    # 模糊匹配
    for name, t in tool_map.items():
        if fallback_substr in name:
            logger.warning(
                "工具 '%s' 未找到，使用模糊匹配结果: '%s'", exact_name, name
            )
            return t
    logger.error(
        "工具 '%s' 未找到，可用工具: %s", exact_name, list(tool_map.keys())
    )
    return None


class LangChainTripPlannerAgent:
    """LangChain 版旅行规划 Agent，协调四个子 Agent 顺序完成规划任务。"""

    def __init__(self) -> None:
        self._initialized = False
        self.attraction_agent: Optional[AttractionSearchAgent] = None
        self.weather_agent: Optional[WeatherQueryAgent] = None
        self.hotel_agent: Optional[HotelSearchAgent] = None
        self.planner_agent: Optional[PlannerAgent] = None
        self.rag_retriever: Optional[DestinationRAGRetriever] = None

    async def initialize(self) -> None:
        """从 Phase 1 ToolManager 获取工具，按名称过滤后初始化各子 Agent。"""
        if self._initialized:
            return

        logger.info("[LangChainTripPlannerAgent] 初始化开始...")

        manager = get_langchain_mcp_tool_manager()
        all_tools = await manager.get_tools()
        tool_map = {t.name: t for t in all_tools}

        logger.info(
            "[LangChainTripPlannerAgent] 可用工具: %s", list(tool_map.keys())
        )

        # 解析各 Agent 所需工具
        text_search_tool = _find_tool(tool_map, _TOOL_TEXT_SEARCH, "text_search")
        weather_tool = _find_tool(tool_map, _TOOL_WEATHER, "weather")

        if text_search_tool is None:
            raise RuntimeError(
                f"未找到景点/酒店搜索工具（期望 '{_TOOL_TEXT_SEARCH}' 或含 'text_search' 的工具）。\n"
                f"可用工具: {list(tool_map.keys())}"
            )
        if weather_tool is None:
            raise RuntimeError(
                f"未找到天气工具（期望 '{_TOOL_WEATHER}' 或含 'weather' 的工具）。\n"
                f"可用工具: {list(tool_map.keys())}"
            )

        self.attraction_agent = AttractionSearchAgent(tools=[text_search_tool])
        self.weather_agent = WeatherQueryAgent(tools=[weather_tool])
        self.hotel_agent = HotelSearchAgent(tools=[text_search_tool])
        self.planner_agent = PlannerAgent()

        # RAG 检索器（懒加载，索引不存在时给出警告而非阻断启动）
        try:
            self.rag_retriever = get_destination_rag_retriever()
            if self.rag_retriever.is_loaded:
                logger.info("[LangChainTripPlannerAgent] RAG 索引加载成功")
            else:
                logger.warning(
                    "[LangChainTripPlannerAgent] RAG 索引未就绪，将跳过 RAG 增强。"
                    " 请运行: cd backend && python -m app.rag.build_index"
                )
        except Exception as e:
            logger.warning("[LangChainTripPlannerAgent] RAG 初始化失败（将跳过）: %s", e)
            self.rag_retriever = None

        self._initialized = True
        logger.info("[LangChainTripPlannerAgent] 初始化完成")

    async def plan_trip(self, request: TripRequest) -> TripPlan:
        """顺序执行四阶段规划，返回 TripPlan 对象。

        任何阶段失败时都会记录原始输出片段和错误原因，方便排错。
        """
        if not self._initialized:
            await self.initialize()

        logger.info(
            "\n%s\n🚀 LangChain 旅行规划开始\n  城市: %s  日期: %s~%s  天数: %d\n%s",
            "=" * 60,
            request.city,
            request.start_date,
            request.end_date,
            request.travel_days,
            "=" * 60,
        )

        # ── Step 0: RAG 攻略检索 ─────────────────────────────────────────
        rag_context = ""
        if self.rag_retriever is not None and self.rag_retriever.is_loaded:
            try:
                pref_str = (
                    "、".join(request.preferences) if request.preferences else ""
                )
                rag_query = (
                    f"{request.city} {request.travel_days}天旅游 "
                    f"{pref_str} "
                    f"{request.transportation or ''} {request.accommodation or ''} "
                    "攻略 景点 推荐 避坑 预约 注意事项 路线"
                ).strip()
                rag_docs = self.rag_retriever.retrieve(
                    query=rag_query, city=request.city, top_k=5
                )
                rag_context = self.rag_retriever.format_context(rag_docs)
                sources = [d.metadata.get("source", "?") for d in rag_docs]
                logger.info(
                    "📚 Step 0: RAG 检索完成，retrieved %d docs, sources=%s",
                    len(rag_docs),
                    sources,
                )
            except Exception as e:
                logger.warning("[Step 0] RAG 检索失败（将跳过 RAG 增强）: %s", e)
                rag_context = ""
        else:
            logger.info("📚 Step 0: RAG 索引未就绪，跳过 RAG 增强")

        # ── Step 1: 景点搜索 ─────────────────────────────────────────────
        logger.info("📍 Step 1: 景点搜索...")
        try:
            attraction_raw = await self.attraction_agent.search(
                city=request.city,
                preferences=request.preferences,
                days=request.travel_days,
            )
        except Exception as exc:
            logger.error("[Step 1] AttractionSearchAgent 失败: %s", exc, exc_info=True)
            raise RuntimeError(f"景点搜索失败: {exc}") from exc

        logger.info("📍 Step 1 完成，输出前200字: %s", attraction_raw[:200])

        # ── Step 2: 天气查询 ─────────────────────────────────────────────
        logger.info("🌤  Step 2: 天气查询...")
        try:
            weather_raw = await self.weather_agent.query_weather(
                city=request.city,
                start_date=request.start_date,
                end_date=request.end_date,
            )
        except Exception as exc:
            logger.error("[Step 2] WeatherQueryAgent 失败: %s", exc, exc_info=True)
            raise RuntimeError(f"天气查询失败: {exc}") from exc

        logger.info("🌤  Step 2 完成，输出前200字: %s", weather_raw[:200])

        # ── Step 3: 酒店搜索 ─────────────────────────────────────────────
        logger.info("🏨 Step 3: 酒店搜索...")
        try:
            hotel_raw = await self.hotel_agent.search_hotels(
                city=request.city,
                accommodation=request.accommodation,
            )
        except Exception as exc:
            logger.error("[Step 3] HotelSearchAgent 失败: %s", exc, exc_info=True)
            raise RuntimeError(f"酒店搜索失败: {exc}") from exc

        logger.info("🏨 Step 3 完成，输出前200字: %s", hotel_raw[:200])

        # ── Step 4: 行程规划 ─────────────────────────────────────────────
        logger.info("📋 Step 4: 生成行程计划...")
        try:
            plan_raw = await self.planner_agent.plan(
                request=request,
                attractions_json=attraction_raw,
                weather_json=weather_raw,
                hotels_json=hotel_raw,
                rag_context=rag_context,
            )
        except Exception as exc:
            logger.error("[Step 4] PlannerAgent 失败: %s", exc, exc_info=True)
            raise RuntimeError(f"行程规划失败: {exc}") from exc

        logger.info("📋 Step 4 完成，输出前400字: %s", plan_raw[:400])

        # ── Step 5: JSON 提取 ────────────────────────────────────────────
        logger.info("🔍 Step 5: 解析 JSON...")
        try:
            data = loads_json(plan_raw)
        except ValueError as exc:
            logger.error(
                "[Step 5] JSON 解析失败: %s\nPlannerAgent 原始输出 (前600字):\n%s",
                exc,
                plan_raw[:600],
            )
            raise RuntimeError(
                f"PlannerAgent 输出无法解析为 JSON: {exc}\n"
                f"原始输出片段: {plan_raw[:300]!r}"
            ) from exc

        # ── Step 6: Pydantic 校验 ────────────────────────────────────────
        logger.info("✅ Step 6: Pydantic 校验...")
        try:
            trip_plan = TripPlan.model_validate(data)
        except Exception as exc:
            logger.error(
                "[Step 6] TripPlan 校验失败: %s\nJSON 数据: %s",
                exc,
                str(data)[:600],
            )
            raise RuntimeError(
                f"生成的 JSON 不符合 TripPlan 模型: {exc}\n"
                f"JSON 片段: {str(data)[:300]!r}"
            ) from exc

        logger.info(
            "\n%s\n✅ LangChain 旅行计划生成完成！城市: %s  天数: %d\n%s",
            "=" * 60,
            trip_plan.city,
            len(trip_plan.days),
            "=" * 60,
        )
        return trip_plan


# 全局单例
_lc_planner_instance: Optional[LangChainTripPlannerAgent] = None


def get_langchain_trip_planner_agent() -> LangChainTripPlannerAgent:
    """返回 LangChainTripPlannerAgent 全局单例（首次调用时创建，未初始化）。"""
    global _lc_planner_instance
    if _lc_planner_instance is None:
        _lc_planner_instance = LangChainTripPlannerAgent()
    return _lc_planner_instance

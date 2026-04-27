"""LangChain 旅行规划调试路由（Phase 2）

POST /api/debug/langchain-trip/plan
  - 使用 LangChainTripPlannerAgent（而非原有 HelloAgents 实现）生成旅行计划
  - 请求模型与原接口完全一致（TripRequest）
  - 响应模型与原接口完全一致（TripPlanResponse）
  - 此接口仅用于验证 LangChain 实现，不影响原 /api/trip/plan
"""

import logging

from fastapi import APIRouter, HTTPException

from ...agents.langchain.trip_planner_agent import get_langchain_trip_planner_agent
from ...models.schemas import TripPlanResponse, TripRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug/langchain-trip", tags=["调试-LangChain旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="LangChain 旅行规划（调试）",
    description=(
        "使用 LangChain Agent 生成旅行计划。"
        "调用链：AttractionSearchAgent → WeatherQueryAgent → HotelSearchAgent → PlannerAgent。"
        "所有子 Agent 均通过高德地图 MCP 工具获取真实数据。"
        "不影响原 /api/trip/plan 接口。"
    ),
)
async def langchain_plan_trip(request: TripRequest):
    """使用 LangChain 多 Agent 生成旅行计划。"""
    logger.info(
        "📥 [LangChain] 收到旅行规划请求: city=%s dates=%s~%s days=%d",
        request.city,
        request.start_date,
        request.end_date,
        request.travel_days,
    )

    try:
        agent = get_langchain_trip_planner_agent()
        trip_plan = await agent.plan_trip(request)

        logger.info("✅ [LangChain] 旅行计划生成成功: city=%s", trip_plan.city)

        return TripPlanResponse(
            success=True,
            message="LangChain 旅行计划生成成功",
            data=trip_plan,
        )

    except Exception as exc:
        logger.error("❌ [LangChain] 旅行计划生成失败: %s", exc, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"LangChain 旅行计划生成失败: {exc}",
        )

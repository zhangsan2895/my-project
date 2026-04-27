"""旅行规划API路由

支持通过 AGENT_BACKEND 环境变量在新旧实现之间切换：
  AGENT_BACKEND=legacy    → 原有 HelloAgents MultiAgentTripPlanner（默认）
  AGENT_BACKEND=langchain → Phase 2 LangChainTripPlannerAgent

如果 langchain 后端抛出异常，会自动 fallback 到 legacy 并记录警告日志，
保证演示稳定性。
"""

import asyncio
import logging

from fastapi import APIRouter, HTTPException

from ...agents.trip_planner_agent import get_trip_planner_agent
from ...config import get_settings
from ...models.schemas import TripPlanResponse, TripRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/trip", tags=["旅行规划"])


@router.post(
    "/plan",
    response_model=TripPlanResponse,
    summary="生成旅行计划",
    description="根据用户输入的旅行需求生成详细旅行计划。通过 AGENT_BACKEND 环境变量可切换新旧实现。",
)
async def plan_trip(request: TripRequest):
    """生成旅行计划（支持 legacy / langchain 后端切换）。"""
    settings = get_settings()

    print(f"\n{'='*60}")
    print(f"📥 收到旅行规划请求:")
    print(f"   城市: {request.city}")
    print(f"   日期: {request.start_date} - {request.end_date}")
    print(f"   天数: {request.travel_days}")
    print(f"   后端: {settings.agent_backend}")
    print(f"{'='*60}\n")

    # ── LangChain 后端 ──────────────────────────────────────────────────
    if settings.agent_backend == "langchain":
        try:
            from ...agents.langchain.trip_planner_agent import (
                get_langchain_trip_planner_agent,
            )

            logger.info("🚀 使用 LangChain 后端生成旅行计划...")
            lc_agent = get_langchain_trip_planner_agent()
            trip_plan = await lc_agent.plan_trip(request)

            logger.info("✅ LangChain 旅行计划生成成功")
            return TripPlanResponse(
                success=True,
                message="旅行计划生成成功（LangChain 后端）",
                data=trip_plan,
            )

        except Exception as exc:
            logger.warning(
                "⚠️  LangChain 后端失败，自动 fallback 到 legacy: %s", exc
            )
            print(f"⚠️  LangChain 后端失败，fallback 到 legacy: {exc}")
            # 继续执行 legacy 分支

    # ── Legacy 后端（默认 / fallback）──────────────────────────────────
    try:
        print("🔄 获取多智能体系统实例（legacy）...")
        legacy_agent = get_trip_planner_agent()

        print("🚀 开始生成旅行计划（legacy）...")
        trip_plan = await asyncio.to_thread(legacy_agent.plan_trip, request)

        print("✅ 旅行计划生成成功，准备返回响应\n")
        return TripPlanResponse(
            success=True,
            message="旅行计划生成成功",
            data=trip_plan,
        )

    except Exception as exc:
        print(f"❌ 生成旅行计划失败: {exc}")
        import traceback

        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"生成旅行计划失败: {exc}",
        )


@router.get(
    "/health",
    summary="健康检查",
    description="检查旅行规划服务是否正常",
)
async def health_check():
    """健康检查"""
    try:
        settings = get_settings()
        return {
            "status": "healthy",
            "service": "trip-planner",
            "agent_backend": settings.agent_backend,
        }
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"服务不可用: {exc}")

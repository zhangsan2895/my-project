"""LangChain Agent 调试路由

POST /debug/langchain-agent/invoke  — 让 LangChain ReAct Agent 处理自然语言查询，
                                      Agent 会自动决策并调用高德地图 MCP 工具。
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ...agents.langchain_amap_agent import get_langchain_amap_agent

router = APIRouter(prefix="/debug/langchain-agent", tags=["调试-LangChain Agent"])


class AgentInvokeRequest(BaseModel):
    """Agent 调用请求体。"""
    query: str


@router.post(
    "/invoke",
    summary="调用 LangChain 高德地图 Agent",
    description=(
        "将自然语言查询交给 LangChain ReAct Agent 处理。"
        "Agent 会自动判断需要调用哪些高德地图 MCP 工具，"
        "并基于工具返回的真实数据生成回答。"
    ),
)
async def invoke_agent(request: AgentInvokeRequest):
    """调用 LangChain Agent 处理查询。"""
    try:
        agent = get_langchain_amap_agent()
        result = await agent.ainvoke(request.query)
        return {
            "success": True,
            "query": request.query,
            "result": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LangChain Agent 调用失败: {e}",
        )

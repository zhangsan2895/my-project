"""高德地图 MCP 工具调试路由

提供两个接口用于验证 LangChain MCP 工具层是否正常工作：
  GET  /debug/mcp/tools  — 列出所有已加载工具的名称、描述、参数 schema
  POST /debug/mcp/call   — 直接调用指定工具
"""

from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ...tools.langchain_mcp_tools import get_langchain_mcp_tool_manager

router = APIRouter(prefix="/debug/mcp", tags=["调试-MCP工具"])


@router.get(
    "/tools",
    summary="列出所有 LangChain MCP 工具",
    description="返回已从高德地图 MCP Server 加载的工具列表，包含名称、描述和参数 schema。"
)
async def list_tools():
    """列出所有已加载的 LangChain MCP 工具。"""
    try:
        manager = get_langchain_mcp_tool_manager()
        tools = await manager.get_tools()

        tool_list = []
        for tool in tools:
            schema = None
            if tool.args_schema is not None:
                try:
                    schema = tool.args_schema.model_json_schema()
                except Exception:
                    schema = str(tool.args_schema)

            tool_list.append({
                "name": tool.name,
                "description": tool.description,
                "args_schema": schema,
            })

        return {
            "success": True,
            "total": len(tool_list),
            "tools": tool_list,
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取工具列表失败: {e}",
        )


class ToolCallRequest(BaseModel):
    """工具调用请求体。"""
    name: str
    arguments: Dict[str, Any] = {}


@router.post(
    "/call",
    summary="调用 LangChain MCP 工具",
    description="根据工具名称和参数直接调用高德地图 MCP 工具，使用 tool.ainvoke(arguments)。",
)
async def call_tool(request: ToolCallRequest):
    """直接调用指定的 LangChain MCP 工具。"""
    try:
        manager = get_langchain_mcp_tool_manager()
        tool = await manager.get_tool(request.name)

        if tool is None:
            all_tools = await manager.get_tools()
            available = [t.name for t in all_tools]
            raise HTTPException(
                status_code=404,
                detail=(
                    f"工具 '{request.name}' 不存在。"
                    f"可用工具（{len(available)} 个）: {available}"
                ),
            )

        result = await tool.ainvoke(request.arguments)

        return {
            "success": True,
            "tool": request.name,
            "arguments": request.arguments,
            "result": str(result),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"调用工具 '{request.name}' 失败: {e}",
        )

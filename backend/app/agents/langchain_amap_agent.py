"""LangChain 高德地图 Agent

最小可用的 LangChain ReAct Agent，使用高德地图 MCP 工具回答旅行相关问题。
LLM 配置复用项目现有的 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL_ID 环境变量，
通过 langchain_openai.ChatOpenAI 接入（兼容 OpenAI-compatible 接口，如 DashScope）。

API 版本说明：
  langgraph  >= 1.1: create_react_agent(prompt=str) 直接接受字符串
  langchain  >= 1.2: 模型字符串格式 "openai:gpt-4.1" 也受支持，但这里仍用 ChatOpenAI
                     保证 base_url 可配（DashScope 等第三方端点）
"""

import os
from typing import Optional
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from ..tools.langchain_mcp_tools import get_langchain_mcp_tool_manager

_SYSTEM_PROMPT = """你是一个智能旅行规划助手，可以通过高德地图工具获取真实的地图数据。

必须遵守的规则：
1. 查询景点、POI 时，必须调用高德地图搜索工具（如 amap_maps_text_search）
2. 查询天气时，必须调用天气工具（如 amap_maps_weather）
3. 规划步行/驾车/公交路线时，必须调用对应的路线工具
4. 严禁编造任何景点名称、地址、天气、路线等实时信息
5. 所有回答必须基于工具返回的真实数据

请用中文回答，信息要准确、简洁、有实用价值。"""


class LangChainAmapAgent:
    """基于 langgraph.prebuilt.create_react_agent 的高德地图 Agent。"""

    def __init__(self):
        self._agent = None
        self._initialized: bool = False

    async def initialize(self) -> None:
        """初始化 LLM 和 Agent。幂等，可安全多次调用。"""
        if self._initialized:
            return

        api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        model = os.getenv("LLM_MODEL_ID") or "gpt-4o"

        if not api_key:
            raise RuntimeError(
                "LLM_API_KEY 未配置，无法初始化 LangChain Agent。\n"
                "请在 backend/.env 中设置 LLM_API_KEY=your_key"
            )

        print("🔄 初始化 LangChain 高德地图 Agent...")
        print(f"   模型: {model}")
        print(f"   Base URL: {base_url or 'OpenAI 默认'}")

        llm_kwargs: dict = {"model": model, "api_key": api_key}
        if base_url:
            llm_kwargs["base_url"] = base_url

        llm = ChatOpenAI(**llm_kwargs)

        # 复用已缓存的 MCP 工具（避免重复发现）
        manager = get_langchain_mcp_tool_manager()
        tools = await manager.get_tools()

        if not tools:
            raise RuntimeError("未加载到任何 MCP 工具，LangChain Agent 无法初始化。")

        # langgraph >= 1.1：prompt 参数直接接受字符串
        self._agent = create_react_agent(
            model=llm,
            tools=tools,
            prompt=_SYSTEM_PROMPT,
        )

        self._initialized = True
        print(f"✅ LangChain Agent 初始化成功，共使用 {len(tools)} 个工具")

    async def ainvoke(self, query: str) -> str:
        """以异步方式调用 Agent，返回最终文本回答。"""
        if not self._initialized:
            await self.initialize()

        result = await self._agent.ainvoke({"messages": [("human", query)]})
        messages = result.get("messages", [])
        if messages:
            return messages[-1].content
        return "Agent 未返回任何结果"


# 全局单例
_agent_instance: Optional[LangChainAmapAgent] = None


def get_langchain_amap_agent() -> LangChainAmapAgent:
    """返回 LangChainAmapAgent 全局单例（首次调用时创建，未初始化）。"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = LangChainAmapAgent()
    return _agent_instance

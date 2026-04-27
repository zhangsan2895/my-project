"""BaseLangChainAgent — 所有 LangChain 工具调用 Agent 的基类

使用 langgraph.prebuilt.create_react_agent（langchain.agents.create_agent 的底层实现）
构建 ReAct 模式 Agent，统一处理：
  - LLM 实例构建（复用项目 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL_ID 配置）
  - Agent 延迟构建（首次调用时构建，避免模块加载期副作用）
  - 结构化日志（agent 名称、query、工具调用摘要、响应片段）
  - 多格式 content 提取（str / list of content blocks）
"""

import os
import logging
from typing import Any, Dict, List, Optional

from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)


def build_chat_openai(temperature: float = 0.2) -> ChatOpenAI:
    """从环境变量构建 ChatOpenAI 实例（所有 LangChain Agent 共用）。

    读取顺序：LLM_API_KEY > OPENAI_API_KEY
    """
    api_key = os.getenv("LLM_API_KEY") or os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    model = os.getenv("LLM_MODEL_ID") or "gpt-4o"

    if not api_key:
        raise RuntimeError(
            "LLM_API_KEY 未配置，无法初始化 LangChain Agent。\n"
            "请在 backend/.env 中设置 LLM_API_KEY=your_key"
        )

    kwargs: Dict[str, Any] = {
        "model": model,
        "api_key": api_key,
        "temperature": temperature,
    }
    if base_url:
        kwargs["base_url"] = base_url

    logger.debug("构建 ChatOpenAI: model=%s base_url=%s", model, base_url or "(默认)")
    return ChatOpenAI(**kwargs)


class BaseLangChainAgent:
    """带工具调用日志的 ReAct Agent 基类。

    子类只需传入 agent_name、system_prompt 和工具列表，
    即可通过 await ainvoke(query) 执行推理。
    """

    def __init__(
        self,
        agent_name: str,
        system_prompt: str,
        tools: List[BaseTool],
        temperature: float = 0.2,
    ) -> None:
        self.agent_name = agent_name
        self.system_prompt = system_prompt
        self.tools = tools
        self.temperature = temperature
        self._agent: Optional[Any] = None

    def _build(self) -> None:
        """延迟构建 ReAct Agent（仅执行一次）。"""
        llm = build_chat_openai(self.temperature)
        self._agent = create_react_agent(
            model=llm,
            tools=self.tools,
            prompt=self.system_prompt,
        )
        logger.info(
            "[%s] Agent 构建完成，挂载工具: %s",
            self.agent_name,
            [t.name for t in self.tools],
        )

    # ------------------------------------------------------------------
    # 结果提取辅助方法
    # ------------------------------------------------------------------

    @staticmethod
    def extract_last_text(result: Dict[str, Any]) -> str:
        """从 Agent 返回结果中提取最后一条消息的文本内容。

        兼容两种 content 格式：
          - str：直接返回
          - list[dict]：提取所有 type=="text" 块拼接
        """
        messages = result.get("messages", [])
        if not messages:
            return ""
        content = messages[-1].content
        if isinstance(content, list):
            parts = [
                blk.get("text", "")
                for blk in content
                if isinstance(blk, dict) and blk.get("type") == "text"
            ]
            return "\n".join(parts)
        return str(content)

    def _log_tool_calls(self, result: Dict[str, Any]) -> None:
        """打印工具调用摘要到日志。"""
        for msg in result.get("messages", []):
            # AIMessage 中的 tool_calls 列表
            tool_calls: List[Any] = getattr(msg, "tool_calls", []) or []
            for tc in tool_calls:
                name = tc.get("name", "?") if isinstance(tc, dict) else getattr(tc, "name", "?")
                args = tc.get("args", {}) if isinstance(tc, dict) else getattr(tc, "args", {})
                logger.info("[%s] → tool_call: %s(%s)", self.agent_name, name, args)

            # ToolMessage 的返回内容（截断展示）
            if type(msg).__name__ == "ToolMessage":
                preview = str(msg.content)[:300]
                logger.info("[%s] ← tool_result: %s…", self.agent_name, preview)

    # ------------------------------------------------------------------
    # 主入口
    # ------------------------------------------------------------------

    async def ainvoke(self, query: str) -> str:
        """以异步方式调用 Agent，返回最终文本响应。"""
        if self._agent is None:
            self._build()

        logger.info("[%s] invoke query: %s", self.agent_name, query[:200])

        result = await self._agent.ainvoke({"messages": [("human", query)]})
        self._log_tool_calls(result)

        response = self.extract_last_text(result)
        logger.info(
            "[%s] response (%d chars): %s",
            self.agent_name,
            len(response),
            response[:300],
        )
        return response

"""LangChain MCP工具管理模块

通过 langchain_mcp_adapters 将高德地图 MCP Server 暴露为 LangChain Tools。
使用和原有 HelloAgents MCPTool 相同的 command/args/env 配置：
  command: uvx
  args:    ["amap-mcp-server"]
  env:     {"AMAP_MAPS_API_KEY": <AMAP_API_KEY>}

langchain-mcp-adapters >= 0.2.x API 说明：
  - client.get_tools() 现在是 async（0.1.x 中是 sync）
  - 客户端默认无状态：每次工具调用自动创建/销毁 MCP 会话，
    无需手动管理 __aenter__ / __aexit__ 生命周期
  - 工具对象持有服务器配置，可独立调用
"""

from typing import Dict, List, Optional, Any
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from ..config import get_settings


class LangChainMCPToolManager:
    """管理 LangChain MCP 工具的单例类。

    在 initialize() 时调用 async get_tools() 发现并缓存工具列表。
    后续每次工具调用由工具对象自身管理 MCP 会话（无状态模式），
    无需在管理器层面维护持久连接。
    """

    def __init__(self):
        self._client: Optional[MultiServerMCPClient] = None
        self._tools: List[BaseTool] = []
        self._tool_map: Dict[str, BaseTool] = {}
        self._initialized: bool = False

    async def initialize(self) -> None:
        """发现并缓存 MCP 工具列表。幂等，可安全多次调用。"""
        if self._initialized:
            return

        settings = get_settings()

        if not settings.amap_api_key:
            raise RuntimeError(
                "AMAP_API_KEY 未配置，无法启动高德地图 MCP Server。\n"
                "请在 backend/.env 中设置 AMAP_API_KEY=your_key"
            )

        print("🔄 初始化 LangChain MCP 工具管理器...")
        print("   command: uvx")
        print("   args:    ['amap-mcp-server']")
        print(f"   AMAP_MAPS_API_KEY: {'已设置' if settings.amap_api_key else '未设置'}")

        server_config = {
            "amap": {
                "command": "uvx",
                "args": ["amap-mcp-server"],
                "transport": "stdio",
                "env": {"AMAP_MAPS_API_KEY": settings.amap_api_key},
            }
        }

        try:
            self._client = MultiServerMCPClient(server_config)
            # 0.2.x: get_tools() 是 async，默认无状态（每次调用自建 session）
            self._tools = await self._client.get_tools()
            self._tool_map = {tool.name: tool for tool in self._tools}
            self._initialized = True
            print(f"✅ LangChain MCP 工具初始化成功，共加载 {len(self._tools)} 个工具")
            print(f"   工具列表: {[t.name for t in self._tools]}")
        except Exception as e:
            print(f"❌ LangChain MCP 工具初始化失败: {e}")
            print("   请确认 uvx 已安装（pip install uv）且 amap-mcp-server 可通过 uvx 运行")
            raise

    def reset(self) -> None:
        """重置状态，下次调用时重新初始化（用于错误恢复）。"""
        self._initialized = False
        self._tools = []
        self._tool_map = {}
        self._client = None

    async def get_tools(self) -> List[BaseTool]:
        """返回所有 LangChain 工具（懒初始化）。"""
        if not self._initialized:
            await self.initialize()
        return self._tools

    async def get_tool(self, name: str) -> Optional[BaseTool]:
        """根据名称返回指定工具，不存在时返回 None。"""
        if not self._initialized:
            await self.initialize()
        return self._tool_map.get(name)

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> str:
        """调用指定工具并返回字符串结果。"""
        if not self._initialized:
            await self.initialize()

        tool = self._tool_map.get(name)
        if tool is None:
            available = list(self._tool_map.keys())
            raise ValueError(
                f"工具 '{name}' 不存在。\n"
                f"可用工具（{len(available)} 个）: {available}"
            )

        result = await tool.ainvoke(arguments)
        return str(result)


# 全局单例
_manager_instance: Optional[LangChainMCPToolManager] = None


def get_langchain_mcp_tool_manager() -> LangChainMCPToolManager:
    """获取 LangChainMCPToolManager 全局单例（首次使用时懒初始化）。"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = LangChainMCPToolManager()
    return _manager_instance

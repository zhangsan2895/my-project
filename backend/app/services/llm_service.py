"""LLM服务模块"""

import os
from hello_agents import HelloAgentsLLM
from ..config import get_settings

# 全局LLM实例
_llm_instance = None


def get_llm() -> HelloAgentsLLM:
    """
    获取LLM实例(单例模式)

    Returns:
        HelloAgentsLLM实例
    """
    global _llm_instance

    if _llm_instance is None:
        # 显式读取环境变量，避免依赖 HelloAgentsLLM 的自动检测逻辑
        # 在 config.py 的 load_dotenv 之后读取，确保 .env 已加载
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        model = os.getenv("LLM_MODEL_ID")

        print(f"🔧 LLM配置: api_key={'已设置' if api_key else '未设置'}, "
              f"base_url={base_url!r}, model={model!r}")

        _llm_instance = HelloAgentsLLM(
            api_key=api_key,
            base_url=base_url,
            model=model,
        )

        print(f"✅ LLM服务初始化成功")
        print(f"   提供商: {_llm_instance.provider}")
        print(f"   模型: {_llm_instance.model}")
        print(f"   Base URL: {_llm_instance.base_url}")

    return _llm_instance


def reset_llm():
    """重置LLM实例(用于测试或重新配置)"""
    global _llm_instance
    _llm_instance = None


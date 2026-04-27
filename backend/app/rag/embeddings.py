"""Embedding 模型懒加载（默认 BAAI/bge-large-zh-v1.5，默认 CUDA）

加载策略：
  - 使用 functools.lru_cache 确保全进程只加载一次，避免重复初始化。
  - EMBEDDING_DEVICE=cuda 但 torch.cuda.is_available() 为 False 时，
    自动 fallback 到 cpu 并记录 warning。
  - batch_size=32，适合 2080Ti 22G 显存，可通过环境变量 EMBEDDING_BATCH_SIZE 调整。
"""

import logging
from functools import lru_cache
from typing import Any

from .config import rag_config

logger = logging.getLogger(__name__)


def _resolve_device(requested: str) -> str:
    """解析实际可用的推理设备。

    若请求 cuda 但 CUDA 不可用，fallback 到 cpu 并发出警告。
    """
    if requested == "cpu":
        return "cpu"

    # 延迟 import，避免模块顶层触发 torch 初始化
    try:
        import torch
        if torch.cuda.is_available():
            device_name = torch.cuda.get_device_name(0)
            logger.info("[Embeddings] 检测到 GPU: %s", device_name)
            return requested  # cuda / cuda:0 等
        else:
            logger.warning(
                "[Embeddings] 请求设备 '%s' 但 torch.cuda.is_available()=False，"
                "自动 fallback 到 cpu。请检查 CUDA 驱动和 PyTorch 版本是否匹配。",
                requested,
            )
            return "cpu"
    except ImportError:
        logger.warning(
            "[Embeddings] torch 未安装，无法检测 CUDA，fallback 到 cpu。"
        )
        return "cpu"


@lru_cache(maxsize=1)
def get_embedding_model() -> Any:
    """懒加载 HuggingFaceEmbeddings，全进程只初始化一次（lru_cache 保证）。

    首次调用时会下载/加载模型，可能需要数分钟；后续调用直接返回缓存实例。
    """
    try:
        from langchain_huggingface import HuggingFaceEmbeddings
    except ImportError:
        try:
            from langchain_community.embeddings import HuggingFaceEmbeddings
        except ImportError as e:
            raise ImportError(
                "请运行: pip install langchain-huggingface"
            ) from e

    import os

    model_name = rag_config.embedding_model_name
    device = _resolve_device(rag_config.embedding_device)
    batch_size = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))

    logger.info(
        "[Embeddings] 加载 Embedding 模型: %s  device=%s  batch_size=%d"
        "（首次加载可能需要几分钟）",
        model_name,
        device,
        batch_size,
    )

    try:
        model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": device},
            encode_kwargs={
                "normalize_embeddings": True,
                "batch_size": batch_size,
            },
        )
    except Exception as e:
        logger.error("[Embeddings] 模型加载失败: %s", e)
        raise RuntimeError(
            f"Embedding 模型 '{model_name}' 加载失败: {e}\n"
            "解决方案：\n"
            "  1. 确保网络可访问 HuggingFace\n"
            "  2. 或设置镜像: HF_ENDPOINT=https://hf-mirror.com\n"
            "  3. 或手动下载后设置 SENTENCE_TRANSFORMERS_HOME\n"
            "  4. CUDA 问题：请参照 https://pytorch.org 安装匹配 CUDA 版本的 PyTorch"
        ) from e

    logger.info(
        "[Embeddings] 模型加载完成: %s  实际设备: %s", model_name, device
    )
    return model

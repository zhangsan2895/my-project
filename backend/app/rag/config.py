"""RAG 配置

支持通过环境变量覆盖所有参数：
  EMBEDDING_MODEL_NAME  — Embedding 模型名称，默认 BAAI/bge-large-zh-v1.5
  EMBEDDING_DEVICE      — 推理设备，默认 cuda（有 GPU 时自动使用，否则 fallback 到 cpu）
  RAG_CHUNK_SIZE        — 文本切分块大小，默认 500
  RAG_CHUNK_OVERLAP     — 切分块重叠字符数，默认 80
  RAG_TOP_K             — 检索返回结果数，默认 5
"""

import os
from pathlib import Path


class RAGConfig:
    # Embedding 模型
    embedding_model_name: str = os.getenv(
        "EMBEDDING_MODEL_NAME", "BAAI/bge-large-zh-v1.5"
    )
    # 默认使用 GPU；embeddings.py 会在加载时检测 CUDA 可用性并自动 fallback
    embedding_device: str = os.getenv("EMBEDDING_DEVICE", "cuda")

    # 目录（相对于 backend/ 工作目录）
    knowledge_base_dir: Path = Path("app/rag/knowledge_base")
    faiss_index_dir: Path = Path("storage/faiss_index")

    # 文本切分
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "500"))
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "80"))

    # 检索
    top_k: int = int(os.getenv("RAG_TOP_K", "5"))


rag_config = RAGConfig()

"""FAISS 向量索引的构建、保存、加载"""

import logging
from pathlib import Path
from typing import Any

from langchain_core.documents import Document

from .config import rag_config
from .embeddings import get_embedding_model

logger = logging.getLogger(__name__)


def build_faiss_index(chunks: list[Document]) -> Any:
    """根据 chunk 列表构建 FAISS 向量索引。"""
    try:
        from langchain_community.vectorstores import FAISS
    except ImportError as e:
        raise ImportError("缺少 langchain-community 或 faiss-cpu，请检查 requirements.txt") from e

    if not chunks:
        raise ValueError("chunks 为空，无法构建索引")

    embedding_model = get_embedding_model()
    logger.info("[VectorStore] 开始构建 FAISS 索引，chunk 数: %d", len(chunks))
    vector_store = FAISS.from_documents(chunks, embedding_model)
    logger.info("[VectorStore] FAISS 索引构建完成")
    return vector_store


def save_faiss_index(vector_store: Any, index_dir: Path | None = None) -> Path:
    """将 FAISS 索引保存到磁盘。"""
    save_dir = Path(index_dir or rag_config.faiss_index_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(save_dir))
    logger.info("[VectorStore] FAISS 索引已保存至: %s", save_dir.resolve())
    return save_dir


def load_faiss_index(index_dir: Path | None = None) -> Any:
    """从磁盘加载 FAISS 索引。

    allow_dangerous_deserialization=True 是必要参数，因为 FAISS 使用 pickle 序列化。
    此处只加载本项目自己通过 build_index.py 生成的可信索引文件，不接受外部输入路径。
    """
    try:
        from langchain_community.vectorstores import FAISS
    except ImportError as e:
        raise ImportError("缺少 langchain-community 或 faiss-cpu，请检查 requirements.txt") from e

    load_dir = Path(index_dir or rag_config.faiss_index_dir)

    index_file = load_dir / "index.faiss"
    if not index_file.exists():
        raise FileNotFoundError(
            f"FAISS 索引文件不存在: {index_file.resolve()}\n"
            "请先运行: cd backend && python -m app.rag.build_index"
        )

    embedding_model = get_embedding_model()
    vector_store = FAISS.load_local(
        str(load_dir),
        embedding_model,
        allow_dangerous_deserialization=True,  # 只加载本项目生成的可信索引
    )
    logger.info("[VectorStore] FAISS 索引加载完成: %s", load_dir.resolve())
    return vector_store

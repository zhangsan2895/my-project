"""DestinationRAGRetriever — 目的地知识检索器"""

import logging
from typing import Any, Optional

from langchain_core.documents import Document

from .city_alias import get_city_aliases
from .config import rag_config

logger = logging.getLogger(__name__)


class DestinationRAGRetriever:
    """基于 FAISS 的目的地知识检索器，支持按城市过滤。"""

    def __init__(self) -> None:
        self._vector_store: Any = None
        self._load_error: Optional[str] = None

    def _ensure_loaded(self) -> None:
        if self._vector_store is not None:
            return
        if self._load_error is not None:
            raise RuntimeError(self._load_error)

        from .vector_store import load_faiss_index

        try:
            self._vector_store = load_faiss_index()
            logger.info("[RAGRetriever] FAISS 索引加载成功")
        except FileNotFoundError as e:
            self._load_error = str(e)
            raise RuntimeError(self._load_error) from e
        except Exception as e:
            self._load_error = f"FAISS 索引加载失败: {e}"
            raise RuntimeError(self._load_error) from e

    @property
    def is_loaded(self) -> bool:
        """检查索引是否已成功加载。"""
        try:
            self._ensure_loaded()
            return True
        except RuntimeError:
            return False

    @property
    def load_error(self) -> Optional[str]:
        if self._vector_store is not None:
            return None
        # 触发一次尝试
        try:
            self._ensure_loaded()
            return None
        except RuntimeError:
            return self._load_error

    def retrieve(
        self,
        query: str,
        city: Optional[str] = None,
        top_k: Optional[int] = None,
    ) -> list[Document]:
        """检索与 query 最相关的文档 chunk。

        Args:
            query: 检索查询文本。
            city: 可选，按城市过滤（使用 city_alias 匹配，大小写不敏感）。
            top_k: 返回结果数量，默认使用 rag_config.top_k。

        Returns:
            Document 列表，metadata 中包含 score 字段（越小越相似）。
        """
        self._ensure_loaded()

        k = top_k or rag_config.top_k
        # 多取一些候选，城市过滤后再截取
        fetch_k = k * 4 if city else k

        results = self._vector_store.similarity_search_with_score(query, k=fetch_k)

        docs: list[Document] = []
        for doc, score in results:
            doc.metadata["score"] = round(float(score), 4)
            docs.append(doc)

        if city:
            aliases = [a.lower() for a in get_city_aliases(city)]
            filtered = [
                d for d in docs
                if d.metadata.get("city", "").lower() in aliases
            ]
            # 如果城市过滤后为空（知识库没有该城市数据），降级返回全部
            if filtered:
                docs = filtered[:k]
            else:
                logger.warning(
                    "[RAGRetriever] 城市 '%s' 无匹配文档，返回全局 top_%d 结果", city, k
                )
                docs = docs[:k]
        else:
            docs = docs[:k]

        sources = [d.metadata.get("source", "?") for d in docs]
        logger.info(
            "[RAGRetriever] query='%s' city=%s → %d docs, sources=%s",
            query[:50],
            city,
            len(docs),
            sources,
        )
        return docs

    def format_context(self, docs: list[Document]) -> str:
        """将检索结果格式化为供 LLM 使用的上下文字符串。"""
        if not docs:
            return "（未检索到相关攻略信息）"

        parts: list[str] = []
        for i, doc in enumerate(docs, start=1):
            source = doc.metadata.get("source", "未知来源")
            city = doc.metadata.get("city", "")
            doc_type = doc.metadata.get("doc_type", "")
            score = doc.metadata.get("score", "")
            header = f"[{i}] 来源: {source}"
            if score != "":
                header += f" (相似度得分: {score})"
            parts.append(f"{header}\n{doc.page_content}")

        return "\n\n---\n\n".join(parts)


# 全局单例
_rag_retriever_instance: Optional[DestinationRAGRetriever] = None


def get_destination_rag_retriever() -> DestinationRAGRetriever:
    """返回 DestinationRAGRetriever 全局单例（懒加载，不在模块导入时加载模型）。"""
    global _rag_retriever_instance
    if _rag_retriever_instance is None:
        _rag_retriever_instance = DestinationRAGRetriever()
    return _rag_retriever_instance

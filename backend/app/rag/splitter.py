"""文档切分：RecursiveCharacterTextSplitter 含中文分隔符"""

import logging
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from .config import rag_config

logger = logging.getLogger(__name__)

_SEPARATORS = [
    "\n## ",
    "\n### ",
    "\n\n",
    "。",
    "！",
    "？",
    "\n",
    " ",
    "",
]


def split_documents(
    docs: list[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Document]:
    """将文档列表切分为 chunk，并在 metadata 中添加 chunk_id。"""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or rag_config.chunk_size,
        chunk_overlap=chunk_overlap or rag_config.chunk_overlap,
        separators=_SEPARATORS,
        keep_separator=True,
    )

    chunks: list[Document] = []
    for doc in docs:
        split_result = splitter.split_documents([doc])
        source = doc.metadata.get("source", "unknown")
        for i, chunk in enumerate(split_result):
            chunk.metadata["chunk_id"] = f"{source}::chunk_{i}"
            chunks.append(chunk)

    logger.info("[Splitter] %d 文档 → %d chunk", len(docs), len(chunks))
    return chunks

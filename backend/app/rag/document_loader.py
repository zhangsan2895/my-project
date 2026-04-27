"""加载 knowledge_base 下所有 Markdown 文档"""

import logging
from pathlib import Path

from langchain_core.documents import Document

from .config import rag_config

logger = logging.getLogger(__name__)


def load_markdown_documents(knowledge_base_dir: Path | None = None) -> list[Document]:
    """递归加载 knowledge_base 下所有 .md 文件，返回 Document 列表。

    Metadata 字段：
      - source: 相对于 knowledge_base_dir 的路径字符串
      - city: 从二级目录名推断（如 beijing/attractions.md → beijing）
      - doc_type: 文件名去扩展名（如 attractions）
    """
    base = knowledge_base_dir or rag_config.knowledge_base_dir
    base = Path(base)

    if not base.exists():
        logger.warning("[DocumentLoader] knowledge_base_dir 不存在: %s", base.resolve())
        return []

    docs: list[Document] = []
    md_files = sorted(base.rglob("*.md"))

    if not md_files:
        logger.warning("[DocumentLoader] 未找到任何 .md 文件: %s", base.resolve())
        return []

    for md_path in md_files:
        try:
            text = md_path.read_text(encoding="utf-8")
        except OSError as e:
            logger.error("[DocumentLoader] 读取文件失败 %s: %s", md_path, e)
            continue

        rel = md_path.relative_to(base)
        parts = rel.parts

        # 从目录层级推断 city：knowledge_base/<city>/xxx.md
        city = parts[0] if len(parts) >= 2 else "unknown"
        doc_type = md_path.stem

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": str(rel).replace("\\", "/"),
                    "city": city,
                    "doc_type": doc_type,
                },
            )
        )
        logger.debug("[DocumentLoader] 加载: %s (city=%s, type=%s)", rel, city, doc_type)

    logger.info("[DocumentLoader] 共加载 %d 个文档", len(docs))
    return docs

"""RAG 调试接口（Phase 3）

Prefix: /debug/rag

端点：
  GET  /debug/rag/health        — 检查索引加载状态
  GET  /debug/rag/cities        — 列出知识库中已有城市和文件
  POST /debug/rag/search        — 返回检索到的文档 chunk（前500字 + metadata）
  POST /debug/rag/context       — 返回 format_context 后的上下文和 sources
"""

import logging
from pathlib import Path
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/debug/rag", tags=["debug-rag"])


# ── 请求/响应模型 ─────────────────────────────────────────────────────────────

class RAGSearchRequest(BaseModel):
    query: str
    city: Optional[str] = None
    top_k: Optional[int] = 5


class ChunkResult(BaseModel):
    content_preview: str   # 前500字
    metadata: dict


class RAGSearchResponse(BaseModel):
    query: str
    city: Optional[str]
    top_k: int
    results: list[ChunkResult]
    total: int


class RAGContextResponse(BaseModel):
    query: str
    city: Optional[str]
    top_k: int
    context: str
    sources: list[str]
    total: int


# ── 请求/响应模型（cities） ────────────────────────────────────────────────────

class CityFilesInfo(BaseModel):
    slug: str
    files: list[str]


class CitiesResponse(BaseModel):
    cities: list[CityFilesInfo]


# ── 路由 ──────────────────────────────────────────────────────────────────────

@router.get("/cities", response_model=CitiesResponse)
async def rag_cities():
    """列出知识库目录下已有的城市和 Markdown 文件。"""
    from ...rag.config import RAGConfig

    kb_dir = Path(RAGConfig.knowledge_base_dir)

    # knowledge_base_dir 是相对路径，从 backend/ 工作目录解析；
    # 若 CWD 不是 backend/，则从本文件位置推断绝对路径
    if not kb_dir.is_absolute():
        kb_dir_abs = Path(__file__).resolve().parents[3] / kb_dir
        if kb_dir_abs.exists():
            kb_dir = kb_dir_abs

    cities: list[CityFilesInfo] = []
    if kb_dir.exists():
        for city_dir in sorted(kb_dir.iterdir()):
            if city_dir.is_dir():
                md_files = sorted(f.name for f in city_dir.glob("*.md"))
                cities.append(CityFilesInfo(slug=city_dir.name, files=md_files))

    return CitiesResponse(cities=cities)


@router.get("/health")
async def rag_health():
    """检查 FAISS 索引是否成功加载。"""
    from ...rag.retriever import get_destination_rag_retriever

    retriever = get_destination_rag_retriever()
    if retriever.is_loaded:
        return {
            "status": "ok",
            "index_loaded": True,
            "message": "FAISS 索引已加载，RAG 检索可用",
        }
    else:
        error = retriever.load_error or "未知错误"
        return {
            "status": "error",
            "index_loaded": False,
            "message": (
                f"FAISS 索引未加载: {error}\n"
                "请先运行: cd backend && python -m app.rag.build_index"
            ),
        }


@router.post("/search", response_model=RAGSearchResponse)
async def rag_search(req: RAGSearchRequest):
    """检索相关文档 chunk，返回 content 前500字和 metadata。"""
    from ...rag.retriever import get_destination_rag_retriever

    retriever = get_destination_rag_retriever()
    docs = retriever.retrieve(query=req.query, city=req.city, top_k=req.top_k)

    results = [
        ChunkResult(
            content_preview=doc.page_content[:500],
            metadata=doc.metadata,
        )
        for doc in docs
    ]

    return RAGSearchResponse(
        query=req.query,
        city=req.city,
        top_k=req.top_k or 5,
        results=results,
        total=len(results),
    )


@router.post("/context", response_model=RAGContextResponse)
async def rag_context(req: RAGSearchRequest):
    """检索并格式化上下文，返回 context 文本和 sources 列表。"""
    from ...rag.retriever import get_destination_rag_retriever

    retriever = get_destination_rag_retriever()
    docs = retriever.retrieve(query=req.query, city=req.city, top_k=req.top_k)
    context = retriever.format_context(docs)
    sources = [doc.metadata.get("source", "unknown") for doc in docs]

    return RAGContextResponse(
        query=req.query,
        city=req.city,
        top_k=req.top_k or 5,
        context=context,
        sources=sources,
        total=len(docs),
    )

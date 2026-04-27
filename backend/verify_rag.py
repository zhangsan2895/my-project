"""RAG 系统完整性验证脚本

从 backend/ 目录运行：
    python verify_rag.py

逐步验证：
  Step 1  环境变量 & 配置加载
  Step 2  Embedding 模型加载（GPU/CPU）
  Step 3  文档加载
  Step 4  文档切分
  Step 5  FAISS 索引构建
  Step 6  FAISS 索引保存
  Step 7  FAISS 索引加载（重新从磁盘读取）
  Step 8  RAG 检索（含城市过滤）
  Step 9  format_context 输出
  Step 10 单例工厂 get_destination_rag_retriever()
"""

import sys
import os
from pathlib import Path

# ── 加载 .env ────────────────────────────────────────────────────────────────
_env_path = Path(__file__).parent / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_env_path, override=False)
    print(f"[ENV] 已加载 .env: {_env_path}")
except ImportError:
    print("[ENV] python-dotenv 未安装，依赖系统环境变量")

# ── 彩色输出工具 ─────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

passed = []
failed = []


def ok(msg: str) -> None:
    print(f"  {GREEN}✅ {msg}{RESET}")
    passed.append(msg)


def fail(msg: str, err: Exception | None = None) -> None:
    print(f"  {RED}❌ {msg}{RESET}")
    if err:
        print(f"     {RED}原因: {err}{RESET}")
    failed.append(msg)


def section(title: str) -> None:
    print(f"\n{CYAN}{'─'*60}{RESET}")
    print(f"{CYAN}  {title}{RESET}")
    print(f"{CYAN}{'─'*60}{RESET}")


# ─────────────────────────────────────────────────────────────────────────────

def step1_config():
    section("Step 1  环境变量 & 配置加载")
    try:
        from app.rag.config import rag_config
        print(f"  embedding_model_name : {rag_config.embedding_model_name}")
        print(f"  embedding_device     : {rag_config.embedding_device}")
        print(f"  knowledge_base_dir   : {rag_config.knowledge_base_dir.resolve()}")
        print(f"  faiss_index_dir      : {rag_config.faiss_index_dir.resolve()}")
        print(f"  chunk_size           : {rag_config.chunk_size}")
        print(f"  chunk_overlap        : {rag_config.chunk_overlap}")
        print(f"  top_k                : {rag_config.top_k}")

        model_path = Path(rag_config.embedding_model_name)
        if model_path.exists():
            ok(f"模型路径存在（本地）: {rag_config.embedding_model_name}")
        else:
            ok(f"模型名称配置（将从 Hub 下载）: {rag_config.embedding_model_name}")
        return rag_config
    except Exception as e:
        fail("RAGConfig 加载失败", e)
        return None


def step2_embedding(rag_config):
    section("Step 2  Embedding 模型加载")
    if rag_config is None:
        fail("跳过（依赖 Step 1）")
        return None
    try:
        from app.rag.embeddings import get_embedding_model
        model = get_embedding_model()
        # 简单 embedding 测试
        vec = model.embed_query("北京故宫历史文化")
        ok(f"模型加载成功，向量维度: {len(vec)}")
        return model
    except Exception as e:
        fail("Embedding 模型加载失败", e)
        return None


def step3_document_loader():
    section("Step 3  文档加载")
    try:
        from app.rag.document_loader import load_markdown_documents
        docs = load_markdown_documents()
        if not docs:
            fail("未找到任何 .md 文档，请检查 app/rag/knowledge_base/ 目录")
            return None
        ok(f"加载文档数: {len(docs)}")
        for doc in docs:
            src = doc.metadata.get("source")
            city = doc.metadata.get("city")
            print(f"     - [{city}] {src}  ({len(doc.page_content)} 字符)")
        return docs
    except Exception as e:
        fail("文档加载失败", e)
        return None


def step4_splitter(docs):
    section("Step 4  文档切分")
    if docs is None:
        fail("跳过（依赖 Step 3）")
        return None
    try:
        from app.rag.splitter import split_documents
        chunks = split_documents(docs)
        ok(f"切分 chunk 数: {len(chunks)}")
        print(f"     示例 chunk (前100字): {chunks[0].page_content[:100]!r}")
        print(f"     metadata: {chunks[0].metadata}")
        return chunks
    except Exception as e:
        fail("文档切分失败", e)
        return None


def step5_build_index(chunks, model):
    section("Step 5  FAISS 索引构建")
    if chunks is None or model is None:
        fail("跳过（依赖 Step 2/4）")
        return None
    try:
        from app.rag.vector_store import build_faiss_index
        vs = build_faiss_index(chunks)
        ok(f"FAISS 索引构建完成，chunk 数: {len(chunks)}")
        return vs
    except Exception as e:
        fail("FAISS 索引构建失败", e)
        return None


def step6_save_index(vs):
    section("Step 6  FAISS 索引保存")
    if vs is None:
        fail("跳过（依赖 Step 5）")
        return False
    try:
        from app.rag.vector_store import save_faiss_index
        save_dir = save_faiss_index(vs)
        faiss_file = save_dir / "index.faiss"
        pkl_file   = save_dir / "index.pkl"
        if faiss_file.exists() and pkl_file.exists():
            ok(f"索引文件已写入: {save_dir.resolve()}")
            print(f"     - index.faiss  {faiss_file.stat().st_size / 1024:.1f} KB")
            print(f"     - index.pkl    {pkl_file.stat().st_size / 1024:.1f} KB")
            return True
        else:
            fail("索引文件未生成")
            return False
    except Exception as e:
        fail("保存失败", e)
        return False


def step7_load_index(saved: bool):
    section("Step 7  FAISS 索引加载（从磁盘）")
    if not saved:
        fail("跳过（依赖 Step 6）")
        return None
    try:
        from app.rag.vector_store import load_faiss_index
        vs = load_faiss_index()
        ok("从磁盘加载 FAISS 索引成功")
        return vs
    except Exception as e:
        fail("加载失败", e)
        return None


def step8_retrieve(vs):
    section("Step 8  RAG 检索")
    if vs is None:
        fail("跳过（依赖 Step 7）")
        return None

    cases = [
        ("故宫预约攻略", "北京", 3),
        ("颐和园 低强度 老人", "北京", 3),
        ("北京 雨天 室内 替代方案", "北京", 3),
        ("北京特色美食 烤鸭", None, 3),   # 无城市过滤
    ]

    try:
        from app.rag.retriever import DestinationRAGRetriever
        retriever = DestinationRAGRetriever()
        retriever._vector_store = vs   # 直接注入已加载的索引

        all_ok = True
        for query, city, k in cases:
            docs = retriever.retrieve(query=query, city=city, top_k=k)
            if docs:
                src_list = [d.metadata.get("source") for d in docs]
                print(f"  query='{query}' city={city} → {len(docs)} docs")
                for s in src_list:
                    print(f"       {s}")
            else:
                fail(f"query='{query}' 无结果")
                all_ok = False

        if all_ok:
            ok("所有检索用例通过")
        return retriever
    except Exception as e:
        fail("RAG 检索失败", e)
        return None


def step9_format_context(retriever):
    section("Step 9  format_context 输出")
    if retriever is None:
        fail("跳过（依赖 Step 8）")
        return

    try:
        docs = retriever.retrieve("北京三日游 历史文化 预约 避坑", city="北京", top_k=3)
        ctx = retriever.format_context(docs)
        preview = ctx[:300].replace("\n", "\\n")
        ok(f"format_context 输出正常（总长 {len(ctx)} 字符）")
        print(f"  前300字预览: {preview}...")
    except Exception as e:
        fail("format_context 失败", e)


def step10_singleton():
    section("Step 10  单例工厂 get_destination_rag_retriever()")
    try:
        from app.rag.retriever import get_destination_rag_retriever
        r1 = get_destination_rag_retriever()
        r2 = get_destination_rag_retriever()
        if r1 is r2:
            ok("单例一致（两次调用返回同一对象）")
        else:
            fail("单例不一致，get_destination_rag_retriever() 每次返回不同对象")

        if r1.is_loaded:
            ok("is_loaded = True，索引就绪")
        else:
            err = r1.load_error or "未知"
            fail(f"is_loaded = False: {err}")
    except Exception as e:
        fail("单例工厂失败", e)


# ── 主流程 ────────────────────────────────────────────────────────────────────

def main():
    print(f"\n{'='*60}")
    print("  RAG 系统完整性验证")
    print(f"{'='*60}")

    cfg     = step1_config()
    model   = step2_embedding(cfg)
    docs    = step3_document_loader()
    chunks  = step4_splitter(docs)
    vs_new  = step5_build_index(chunks, model)
    saved   = step6_save_index(vs_new)
    vs_disk = step7_load_index(saved)
    retriever = step8_retrieve(vs_disk)
    step9_format_context(retriever)
    step10_singleton()

    # ── 汇总 ──────────────────────────────────────────────────────────────────
    total = len(passed) + len(failed)
    print(f"\n{'='*60}")
    print(f"  验证结果: {GREEN}{len(passed)} 通过{RESET}  {RED}{len(failed)} 失败{RESET}  / 共 {total} 项")
    if failed:
        print(f"\n{RED}  失败项目:{RESET}")
        for f in failed:
            print(f"  {RED}  • {f}{RESET}")
        print()
        sys.exit(1)
    else:
        print(f"\n{GREEN}  全部通过！RAG 系统可正常运行。{RESET}\n")


if __name__ == "__main__":
    main()

"""构建 FAISS 索引脚本

运行方式（从 backend/ 目录执行）：
    python -m app.rag.build_index
"""

import logging
import sys
from pathlib import Path

# 优先加载 .env，确保 HF_HOME 等环境变量在模型下载前生效
_env_path = Path(__file__).resolve().parents[2] / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_env_path, override=False)
except ImportError:
    pass  # python-dotenv 未安装时跳过，依赖系统环境变量

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def main() -> None:
    from .document_loader import load_markdown_documents
    from .splitter import split_documents
    from .vector_store import build_faiss_index, save_faiss_index

    print("=" * 60)
    print("RAG 知识库索引构建")
    print("=" * 60)

    # Step 1: 加载文档
    print("\n[Step 1] 加载 Markdown 文档...")
    docs = load_markdown_documents()
    if not docs:
        print("❌ 未加载到任何文档，请检查 app/rag/knowledge_base/ 目录")
        sys.exit(1)
    print(f"✅ 加载文档数: {len(docs)}")
    for doc in docs:
        print(f"   - {doc.metadata.get('source')} ({len(doc.page_content)} 字符)")

    # Step 2: 切分 chunk
    print("\n[Step 2] 切分文档为 chunk...")
    chunks = split_documents(docs)
    print(f"✅ 切分后 chunk 数: {len(chunks)}")

    # Step 3: 构建 FAISS 索引
    print("\n[Step 3] 构建 FAISS 向量索引（首次运行会下载 Embedding 模型）...")
    vector_store = build_faiss_index(chunks)
    print("✅ FAISS 索引构建完成")

    # Step 4: 保存索引
    print("\n[Step 4] 保存索引到磁盘...")
    save_dir = save_faiss_index(vector_store)
    print(f"✅ 索引已保存: {save_dir.resolve()}")
    print(f"   - {save_dir / 'index.faiss'}")
    print(f"   - {save_dir / 'index.pkl'}")

    print("\n" + "=" * 60)
    print("索引构建完成！可通过 POST /debug/rag/search 验证检索效果")
    print("=" * 60)


if __name__ == "__main__":
    main()

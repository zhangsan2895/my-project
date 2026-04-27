"""城市知识库爬虫 CLI 入口

用法（从 backend/ 目录运行）：
    python -m app.rag.crawler.crawl_city --city shanghai
    python -m app.rag.crawler.crawl_city --city shanghai --categories attractions food routes tips
    python -m app.rag.crawler.crawl_city --city shanghai --rebuild-index
"""

import argparse
import logging
import sys
from pathlib import Path

# 确保 backend/ 在 sys.path 中，支持直接 python -m 运行
_backend_dir = Path(__file__).resolve().parents[3]
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

# 优先加载 .env
_env_path = _backend_dir / ".env"
try:
    from dotenv import load_dotenv
    load_dotenv(_env_path, override=False)
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)

ALL_CATEGORIES = ["attractions", "food", "routes", "tips"]


def crawl_city(
    city_slug: str,
    categories: list[str],
    rebuild_index: bool = False,
) -> list[str]:
    """
    爬取并生成城市知识库 Markdown 文件。

    Returns:
        成功写入的 category 名称列表（空列表表示全部失败）
    """
    from .city_config import CITY_CONFIGS
    from .cleaner import clean_text
    from .config import DEFAULT_CONFIG
    from .fetcher import fetch_url
    from .markdown_writer import write_city_markdown
    from .parser import extract_main_text
    from .summarizer import summarize_to_markdown

    if city_slug not in CITY_CONFIGS:
        logger.error("未找到城市配置: %s（可用: %s）", city_slug, list(CITY_CONFIGS.keys()))
        sys.exit(1)

    city_cfg = CITY_CONFIGS[city_slug]
    city_name = city_cfg["name"]
    sources_map: dict = city_cfg.get("sources", {})

    logger.info("=" * 60)
    logger.info("开始爬取城市: %s (%s)", city_name, city_slug)
    logger.info("目标分类: %s", categories)
    logger.info("=" * 60)

    written_categories: list[str] = []

    for category in categories:
        sources = sources_map.get(category, [])

        if not sources:
            logger.warning("[%s/%s] 无 seed URL 配置，跳过", city_slug, category)
            continue

        logger.info("[%s/%s] 开始处理，共 %d 个 URL", city_slug, category, len(sources))

        raw_texts: list[dict] = []
        page_count = 0

        for source in sources:
            if page_count >= DEFAULT_CONFIG.max_pages_per_city:
                logger.warning("[%s/%s] 已达最大页面数 %d，停止", city_slug, category, DEFAULT_CONFIG.max_pages_per_city)
                break

            url = source.get("url", "")
            source_name = source.get("name", url)

            if not url:
                logger.warning("[%s/%s] 跳过空 URL 条目: %s", city_slug, category, source_name)
                continue

            try:
                logger.info("[%s/%s] 抓取: %s", city_slug, category, url)
                html = fetch_url(url)
            except PermissionError as e:
                logger.warning("[%s/%s] robots.txt 禁止，跳过: %s — %s", city_slug, category, url, e)
                continue
            except Exception as e:
                logger.error("[%s/%s] 抓取失败，跳过: %s — %s", city_slug, category, url, e)
                continue

            text = extract_main_text(html, url=url)
            text = clean_text(text)

            if not text.strip():
                logger.warning("[%s/%s] 正文为空，跳过: %s", city_slug, category, url)
                continue

            logger.info("[%s/%s] 正文长度 %d 字符: %s", city_slug, category, len(text), url)
            raw_texts.append({"source_name": source_name, "url": url, "text": text})
            page_count += 1

        if not raw_texts:
            logger.error("[%s/%s] 所有 URL 均失败或被跳过，跳过该分类", city_slug, category)
            continue

        try:
            logger.info("[%s/%s] 调用 LLM 整理知识库...", city_slug, category)
            markdown = summarize_to_markdown(city_name, category, raw_texts)
        except Exception as e:
            logger.error("[%s/%s] LLM 摘要失败: %s", city_slug, category, e, exc_info=True)
            continue

        try:
            out_path = write_city_markdown(city_slug, category, markdown)
            logger.info("[%s/%s] 已输出: %s", city_slug, category, out_path)
            written_categories.append(category)
        except Exception as e:
            logger.error("[%s/%s] 文件写入失败: %s", city_slug, category, e)

    if written_categories:
        logger.info("[%s] 本次写入分类: %s", city_slug, written_categories)
    else:
        logger.error("[%s] 所有分类均未成功写入", city_slug)

    if rebuild_index:
        if not written_categories:
            logger.warning("没有成功生成任何文件，跳过重建索引")
        else:
            logger.info("重建 FAISS 索引...")
            try:
                from app.rag.build_index import main as build_index_main
                build_index_main()
            except Exception as e:
                logger.error("重建索引失败: %s", e)

    logger.info("=" * 60)
    logger.info("完成: %s  成功分类: %s", city_slug, written_categories)
    logger.info("=" * 60)

    return written_categories


def main() -> None:
    parser = argparse.ArgumentParser(
        description="城市旅行知识库爬虫与 Markdown 生成器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python -m app.rag.crawler.crawl_city --city shanghai
  python -m app.rag.crawler.crawl_city --city chengdu --categories attractions food
  python -m app.rag.crawler.crawl_city --city shanghai --rebuild-index
        """,
    )
    parser.add_argument("--city", required=True, help="城市 slug，如 shanghai、chengdu")
    parser.add_argument(
        "--categories",
        nargs="+",
        default=ALL_CATEGORIES,
        choices=ALL_CATEGORIES,
        help="要处理的分类（默认全部）",
    )
    parser.add_argument(
        "--rebuild-index",
        action="store_true",
        help="生成完成后自动重建 FAISS 索引",
    )
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="禁用 HTML 缓存，强制重新抓取",
    )

    args = parser.parse_args()

    if args.no_cache:
        from .fetcher import fetch_url as _original_fetch
        import functools

        def _no_cache_fetch(url, use_cache=True, **kwargs):
            return _original_fetch(url, use_cache=False, **kwargs)

        import app.rag.crawler.fetcher as fetcher_mod
        fetcher_mod.fetch_url = _no_cache_fetch  # type: ignore[attr-defined]

    crawl_city(
        city_slug=args.city,
        categories=args.categories,
        rebuild_index=args.rebuild_index,
    )


if __name__ == "__main__":
    main()

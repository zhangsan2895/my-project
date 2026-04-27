"""批量城市知识库构建脚本

用法（从 backend/ 目录运行）：
    python -m app.rag.crawler.crawl_all_cities
    python -m app.rag.crawler.crawl_all_cities --fix-missing        # 只补全缺失文件
    python -m app.rag.crawler.crawl_all_cities --check              # 仅检查缺失，不爬取
    python -m app.rag.crawler.crawl_all_cities --cities chongqing wuhan nanjing
    python -m app.rag.crawler.crawl_all_cities --skip beijing shanghai
"""

import argparse
import logging
import sys
import time
from pathlib import Path

_backend_dir = Path(__file__).resolve().parents[3]
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

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


def get_missing_categories(city_slug: str, kb_base: Path, categories: list[str]) -> list[str]:
    """返回该城市缺失的 category 文件列表。"""
    city_dir = kb_base / city_slug
    return [cat for cat in categories if not (city_dir / f"{cat}.md").exists()]


def print_status_table(kb_base: Path, target_slugs: list[str], categories: list[str]) -> None:
    """打印各城市知识库完整度表格。"""
    from .city_config import CITY_CONFIGS

    logger.info("")
    logger.info("%-12s  %s", "城市", "  ".join(f"{c:12}" for c in categories))
    logger.info("-" * (12 + 16 * len(categories)))
    for slug in target_slugs:
        city_name = CITY_CONFIGS.get(slug, {}).get("name", slug)
        row = []
        for cat in categories:
            path = kb_base / slug / f"{cat}.md"
            row.append("✅" if path.exists() else "❌")
        logger.info("%-12s  %s", f"{city_name}({slug})", "         ".join(row))
    logger.info("")


def main() -> None:
    from .city_config import CITY_CONFIGS
    from .crawl_city import crawl_city

    parser = argparse.ArgumentParser(description="批量构建城市旅行知识库")
    parser.add_argument("--cities", nargs="+", help="只处理指定城市（默认全部）")
    parser.add_argument("--skip", nargs="+", default=[], help="跳过指定城市 slug")
    parser.add_argument(
        "--categories", nargs="+", default=ALL_CATEGORIES, choices=ALL_CATEGORIES,
        help="要处理的分类（默认全部）",
    )
    parser.add_argument(
        "--fix-missing", action="store_true",
        help="只为每个城市补全缺失的 category 文件，已存在的跳过",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="仅打印缺失状态，不执行爬取",
    )
    parser.add_argument(
        "--no-rebuild-index", action="store_true",
        help="完成后不重建 FAISS 索引",
    )
    parser.add_argument(
        "--inter-city-delay", type=float, default=3.0,
        help="城市之间的等待秒数，防止 LLM API 限速（默认 3s）",
    )
    args = parser.parse_args()

    target_slugs = args.cities if args.cities else list(CITY_CONFIGS.keys())
    target_slugs = [s for s in target_slugs if s not in args.skip]

    kb_base = _backend_dir / "app" / "rag" / "knowledge_base"

    logger.info("=" * 70)
    logger.info("批量城市知识库构建")
    logger.info("目标城市 (%d): %s", len(target_slugs), target_slugs)
    logger.info("目标分类: %s", args.categories)
    logger.info("=" * 70)

    # --check 模式：只打印状态，不爬取
    if args.check:
        print_status_table(kb_base, target_slugs, args.categories)
        missing_count = sum(
            len(get_missing_categories(s, kb_base, args.categories))
            for s in target_slugs
        )
        logger.info("共缺失 %d 个文件", missing_count)
        return

    rebuild = not args.no_rebuild_index

    # 结果统计
    full_success: list[str] = []      # 所有 category 都写入成功
    partial_success: list[str] = []   # 部分 category 写入成功
    all_skipped: list[str] = []       # 所有 category 均已存在，全部跳过
    all_failed: list[str] = []        # 没有任何文件写入成功

    total = len(target_slugs)
    any_written = False

    for idx, slug in enumerate(target_slugs, 1):
        city_name = CITY_CONFIGS.get(slug, {}).get("name", slug)

        # 确定本城市需要处理的 category
        if args.fix_missing:
            categories_to_run = get_missing_categories(slug, kb_base, args.categories)
            if not categories_to_run:
                logger.info("[%d/%d] %s (%s) 知识库完整，跳过", idx, total, city_name, slug)
                all_skipped.append(slug)
                continue
            logger.info(
                "[%d/%d] %s (%s) 缺失分类: %s，开始补全",
                idx, total, city_name, slug, categories_to_run,
            )
        else:
            categories_to_run = args.categories

        logger.info("")
        logger.info("─" * 70)
        logger.info("[%d/%d] 处理城市: %s (%s)", idx, total, city_name, slug)
        logger.info("─" * 70)

        t0 = time.time()
        try:
            written = crawl_city(
                city_slug=slug,
                categories=categories_to_run,
                rebuild_index=False,
            )
        except SystemExit:
            logger.error("  ❌ %s 配置错误（SystemExit）", city_name)
            all_failed.append(slug)
            continue
        except Exception as e:
            logger.error("  ❌ %s 出现未预期异常: %s", city_name, e, exc_info=True)
            all_failed.append(slug)
            continue

        elapsed = time.time() - t0
        expected = set(categories_to_run)
        written_set = set(written)

        if not written:
            logger.error("  ❌ %s 无任何文件写入成功（耗时 %.1fs）", city_name, elapsed)
            all_failed.append(slug)
        elif written_set == expected:
            logger.info("  ✅ %s 全部完成（耗时 %.1fs）", city_name, elapsed)
            full_success.append(slug)
            any_written = True
        else:
            missing = sorted(expected - written_set)
            logger.warning(
                "  ⚠️  %s 部分完成（耗时 %.1fs）  成功: %s  失败: %s",
                city_name, elapsed, sorted(written_set), missing,
            )
            partial_success.append(slug)
            any_written = True

        # 城市间等待，避免 LLM API 限速
        if idx < total and args.inter_city_delay > 0:
            logger.info("  等待 %.1fs 后继续下一城市...", args.inter_city_delay)
            time.sleep(args.inter_city_delay)

    # ── 最终汇总 ──────────────────────────────────────────────────────────────
    logger.info("")
    logger.info("=" * 70)
    logger.info("批量构建完成")
    logger.info("  完整成功: %d 个 — %s", len(full_success), full_success)
    logger.info("  部分成功: %d 个 — %s", len(partial_success), partial_success)
    logger.info("  全部跳过: %d 个 — %s", len(all_skipped), all_skipped)
    logger.info("  完全失败: %d 个 — %s", len(all_failed), all_failed)
    logger.info("=" * 70)

    # 打印最终状态表
    print_status_table(kb_base, target_slugs, args.categories)

    if all_failed or partial_success:
        failed_slugs = all_failed + partial_success
        logger.info("重新运行失败/部分成功城市的命令：")
        logger.info(
            "  python -m app.rag.crawler.crawl_all_cities --fix-missing --cities %s",
            " ".join(failed_slugs),
        )

    if rebuild and any_written:
        logger.info("")
        logger.info("重建 FAISS 索引...")
        try:
            from app.rag.build_index import main as build_index_main
            build_index_main()
            logger.info("✅ FAISS 索引重建完成")
        except Exception as e:
            logger.error("❌ 索引重建失败: %s", e, exc_info=True)
    elif not rebuild:
        logger.info("跳过索引重建（--no-rebuild-index）")
    elif not any_written:
        logger.warning("无新文件生成，跳过索引重建")


if __name__ == "__main__":
    main()

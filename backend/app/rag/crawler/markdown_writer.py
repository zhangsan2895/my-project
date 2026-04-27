"""Markdown 知识库文件写入器"""

import logging
from pathlib import Path

from .config import DEFAULT_CONFIG, CrawlerConfig

logger = logging.getLogger(__name__)


def write_city_markdown(
    city_slug: str,
    category: str,
    content: str,
    config: CrawlerConfig = DEFAULT_CONFIG,
) -> Path:
    """
    将 Markdown 内容写入知识库文件。

    Args:
        city_slug: 城市标识，如 "shanghai"
        category: 分类，如 "attractions"
        content: Markdown 文本
        config: 爬虫配置

    Returns:
        写入文件的绝对路径
    """
    output_dir = config.output_base_dir / city_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{category}.md"
    output_path.write_text(content, encoding="utf-8")

    logger.info("知识库已写入: %s", output_path.resolve())
    return output_path

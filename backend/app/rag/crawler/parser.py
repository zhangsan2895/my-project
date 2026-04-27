"""HTML 正文抽取器

优先使用 trafilatura 提取文章正文；失败时回退到 BeautifulSoup。
"""

import logging
from typing import Optional

from .config import DEFAULT_CONFIG, CrawlerConfig

logger = logging.getLogger(__name__)


def extract_main_text(
    html: str,
    url: Optional[str] = None,
    config: CrawlerConfig = DEFAULT_CONFIG,
) -> str:
    """
    从 HTML 中抽取正文文本。

    优先级：trafilatura → BeautifulSoup 回退
    结果截断到 config.max_chars_per_page 字符。
    """
    text = _try_trafilatura(html, url)

    if not text or len(text.strip()) < 100:
        logger.debug("trafilatura 抽取不足，切换 BeautifulSoup: %s", url)
        text = _fallback_beautifulsoup(html)

    text = text.strip()
    if len(text) > config.max_chars_per_page:
        text = text[: config.max_chars_per_page]
        logger.debug("内容截断到 %d 字符: %s", config.max_chars_per_page, url)

    return text


def _try_trafilatura(html: str, url: Optional[str]) -> str:
    try:
        import trafilatura

        result = trafilatura.extract(
            html,
            url=url,
            include_comments=False,
            include_tables=True,
            no_fallback=False,
            favor_precision=True,
        )
        return result or ""
    except Exception as e:
        logger.warning("trafilatura 抽取失败: %s", e)
        return ""


def _fallback_beautifulsoup(html: str) -> str:
    try:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
            tag.decompose()

        # 优先取 <article>、<main>，否则取 <body>
        content_node = (
            soup.find("article")
            or soup.find("main")
            or soup.find("div", id="mw-content-text")  # Wikipedia
            or soup.find("body")
        )

        if content_node is None:
            return soup.get_text(separator="\n")

        return content_node.get_text(separator="\n")
    except Exception as e:
        logger.warning("BeautifulSoup 解析失败: %s", e)
        return ""

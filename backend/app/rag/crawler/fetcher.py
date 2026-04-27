"""网页抓取器

合规约束：
- 强制检查 robots.txt，不允许的 URL 抛出 PermissionError
- 每次请求间隔 request_delay_seconds 秒
- 使用自定义 User-Agent 标识爬虫身份
- HTML 结果缓存到本地，避免重复请求
"""

import hashlib
import logging
import time
import urllib.robotparser
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import httpx

from .config import DEFAULT_CONFIG, CrawlerConfig

logger = logging.getLogger(__name__)

# robots.txt 解析结果缓存（域名 → RobotFileParser）
_robots_cache: dict[str, urllib.robotparser.RobotFileParser] = {}


def _get_robots_parser(base_url: str, config: CrawlerConfig) -> urllib.robotparser.RobotFileParser:
    """获取并缓存指定域名的 robots.txt 解析器。"""
    parsed = urlparse(base_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    if origin in _robots_cache:
        return _robots_cache[origin]

    robots_url = f"{origin}/robots.txt"
    parser = urllib.robotparser.RobotFileParser()
    parser.set_url(robots_url)

    try:
        with httpx.Client(
            headers={"User-Agent": config.user_agent},
            timeout=config.timeout,
            follow_redirects=True,
        ) as client:
            resp = client.get(robots_url)
            if resp.status_code == 200:
                parser.parse(resp.text.splitlines())
                logger.debug("robots.txt 已加载: %s", robots_url)
            else:
                # 无 robots.txt 视为允许
                logger.debug("robots.txt 不存在(%s)，视为允许: %s", resp.status_code, robots_url)
    except Exception as e:
        logger.warning("获取 robots.txt 失败，视为允许: %s — %s", robots_url, e)

    _robots_cache[origin] = parser
    return parser


def can_fetch(url: str, config: CrawlerConfig = DEFAULT_CONFIG) -> bool:
    """检查 robots.txt 是否允许抓取该 URL。"""
    try:
        parser = _get_robots_parser(url, config)
        return parser.can_fetch(config.user_agent, url)
    except Exception as e:
        logger.warning("robots.txt 检查出错，默认允许: %s — %s", url, e)
        return True


def _cache_path(url: str, cache_dir: Path) -> Path:
    """根据 URL 生成缓存文件路径。"""
    url_hash = hashlib.sha256(url.encode()).hexdigest()[:16]
    return cache_dir / f"{url_hash}.html"


def fetch_url(
    url: str,
    use_cache: bool = True,
    config: CrawlerConfig = DEFAULT_CONFIG,
) -> str:
    """
    抓取 URL 的 HTML 内容。

    Args:
        url: 目标 URL
        use_cache: 是否使用本地缓存（默认 True）
        config: 爬虫配置

    Returns:
        HTML 字符串

    Raises:
        PermissionError: robots.txt 不允许抓取
        httpx.HTTPError: 网络请求失败
    """
    if not can_fetch(url, config):
        raise PermissionError(f"robots.txt 禁止抓取: {url}")

    cache_dir = config.cache_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = _cache_path(url, cache_dir)

    if use_cache and cached.exists():
        logger.debug("命中缓存: %s → %s", url, cached)
        return cached.read_text(encoding="utf-8")

    last_exc: Optional[Exception] = None
    for attempt in range(1, config.max_retries + 2):
        try:
            logger.info("抓取(%d/%d): %s", attempt, config.max_retries + 1, url)
            with httpx.Client(
                headers={"User-Agent": config.user_agent},
                timeout=config.timeout,
                follow_redirects=True,
            ) as client:
                resp = client.get(url)
                resp.raise_for_status()
                html = resp.text

            if use_cache:
                cached.write_text(html, encoding="utf-8")
                logger.debug("缓存已写入: %s", cached)

            time.sleep(config.request_delay_seconds)
            return html

        except Exception as e:
            last_exc = e
            logger.warning("请求失败(%d/%d): %s — %s", attempt, config.max_retries + 1, url, e)
            if attempt <= config.max_retries:
                time.sleep(config.request_delay_seconds)

    raise RuntimeError(f"抓取失败，已重试 {config.max_retries} 次: {url}") from last_exc

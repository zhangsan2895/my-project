"""爬虫配置"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CrawlerConfig:
    user_agent: str = "TripPlannerRAGBot/0.1 (+local research project)"
    timeout: int = 15
    max_retries: int = 2
    request_delay_seconds: float = 2.0
    cache_dir: Path = field(default_factory=lambda: Path("storage/rag_crawler_cache"))
    output_base_dir: Path = field(default_factory=lambda: Path("app/rag/knowledge_base"))
    max_pages_per_city: int = 20
    max_chars_per_page: int = 12000


DEFAULT_CONFIG = CrawlerConfig()

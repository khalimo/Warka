from __future__ import annotations

import logging
import time
from typing import Any
from urllib.parse import urlparse

from app.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()
_LAST_REQUEST_BY_DOMAIN: dict[str, float] = {}


def _respect_rate_limit(url: str) -> None:
    domain = urlparse(url).netloc
    if not domain:
        return
    last_request = _LAST_REQUEST_BY_DOMAIN.get(domain)
    if last_request is not None:
        elapsed = time.time() - last_request
        if elapsed < settings.scrape_rate_limit_seconds:
            time.sleep(settings.scrape_rate_limit_seconds - elapsed)
    _LAST_REQUEST_BY_DOMAIN[domain] = time.time()


def scrape_source_entries(source_id: str, base_url: str) -> list[dict[str, Any]]:
    """Scraping is intentionally opt-in and source-specific.

    This pass keeps the framework in place but does not enable any scraper by default,
    because the verified RSS sources are more reliable than brittle HTML extraction.
    """

    if not settings.enable_scrapers:
        return []

    _respect_rate_limit(base_url)
    logger.info("No scraper configured for source_id=%s; returning no entries", source_id)
    return []

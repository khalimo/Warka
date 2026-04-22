from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any

import feedparser
import httpx

from app.config import get_settings
from app.models import Source


logger = logging.getLogger(__name__)
settings = get_settings()
REQUEST_HEADERS = {
    "User-Agent": "WarkaNewsBot/1.0",
    "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
}


class FeedFetchError(Exception):
    pass


def fetch_feed_entries(source: Source) -> Iterable[dict[str, Any]]:
    with httpx.Client(timeout=settings.feed_timeout, follow_redirects=True, headers=REQUEST_HEADERS) as client:
        response = client.get(source.feed_url)
        response.raise_for_status()
    parsed = feedparser.parse(response.content)
    if parsed.bozo and not parsed.entries:
        raise FeedFetchError(f"Failed to parse feed for {source.name}")
    return list(parsed.entries[: settings.feed_limit_per_source])

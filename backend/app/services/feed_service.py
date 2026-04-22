from __future__ import annotations

import logging
from dataclasses import dataclass
from time import perf_counter
from collections.abc import Iterable
from typing import Any, Optional

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
VERIFICATION_HEADERS = {
    "User-Agent": "WarkaBot/1.0 (https://warka.news; verification)",
    "Accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
}


class FeedFetchError(Exception):
    pass


@dataclass
class FeedFetchResult:
    entries: list[dict[str, Any]]
    response_time_ms: int
    status_code: int
    final_url: str


def _parse_feed_payload(source_name: str, payload: bytes) -> list[dict[str, Any]]:
    parsed = feedparser.parse(payload)
    if parsed.bozo and not parsed.entries:
        raise FeedFetchError(f"Failed to parse feed for {source_name}")
    return list(parsed.entries[: settings.feed_limit_per_source])


def fetch_feed(source: Source, *, timeout: Optional[int] = None, verification: bool = False) -> FeedFetchResult:
    headers = VERIFICATION_HEADERS if verification else REQUEST_HEADERS
    start = perf_counter()
    with httpx.Client(timeout=timeout or settings.feed_timeout, follow_redirects=True, headers=headers) as client:
        response = client.get(source.feed_url)
        response.raise_for_status()
    response_time_ms = int((perf_counter() - start) * 1000)
    entries = _parse_feed_payload(source.name, response.content)
    return FeedFetchResult(
        entries=entries,
        response_time_ms=response_time_ms,
        status_code=response.status_code,
        final_url=str(response.url),
    )


def fetch_feed_entries(source: Source) -> Iterable[dict[str, Any]]:
    return fetch_feed(source).entries


def verify_feed(source: Source) -> FeedFetchResult:
    result = fetch_feed(source, timeout=settings.verification_timeout, verification=True)
    if not result.entries:
        raise FeedFetchError(f"No feed entries returned for {source.name}")
    return result

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from app.config import get_settings
from app.services.scrapers.base import (
    ScrapeResult,
    SourceScraper,
    extract_article_html,
    fetch_text,
    meta_content,
    normalize_url,
    robots_sitemaps,
    same_domain,
    sitemap_locations,
)
from app.utils.text import collapse_whitespace, strip_html


logger = logging.getLogger(__name__)
settings = get_settings()

NON_ARTICLE_SEGMENTS = {
    "about",
    "advertise",
    "author",
    "category",
    "contact",
    "page",
    "privacy",
    "tag",
    "terms",
}

ARTICLE_PATH_HINTS = {
    "article",
    "articles",
    "news",
    "war",
    "warar",
    "somalia",
    "somali",
    "caalamka",
    "world",
}


class UniversalNewsScraper(SourceScraper):
    """Conservative public-news scraper using sitemaps, homepage links, and metadata."""

    source_id = "universal"

    def scrape(self, base_url: str, *, limit: int) -> ScrapeResult:
        errors: list[str] = []
        candidate_urls = self._candidate_urls(base_url, limit=max(limit * 3, 12), errors=errors)
        entries: list[dict[str, Any]] = []

        for url in candidate_urls:
            if len(entries) >= limit:
                break
            try:
                entry = self._article_entry(url, base_url=base_url)
            except Exception as exc:
                errors.append(f"{url}: {exc}")
                continue
            if entry:
                entries.append(entry)

        return ScrapeResult(entries=entries, errors=errors[:8])

    def _candidate_urls(self, base_url: str, *, limit: int, errors: list[str]) -> list[str]:
        urls: list[str] = []
        seen: set[str] = set()

        for url in self._sitemap_article_urls(base_url, errors=errors):
            if url in seen:
                continue
            seen.add(url)
            urls.append(url)
            if len(urls) >= limit:
                return urls

        for url in self._homepage_article_urls(base_url, errors=errors):
            if url in seen:
                continue
            seen.add(url)
            urls.append(url)
            if len(urls) >= limit:
                return urls

        return urls

    def _sitemap_article_urls(self, base_url: str, *, errors: list[str]) -> list[str]:
        sitemap_urls = robots_sitemaps(base_url) or [
            urljoin(base_url, "/sitemap.xml"),
            urljoin(base_url, "/sitemap_index.xml"),
        ]
        article_urls: list[str] = []

        for sitemap_url in sitemap_urls[:4]:
            try:
                xml_text = fetch_text(sitemap_url, base_url=base_url)
            except Exception as exc:
                errors.append(f"sitemap {sitemap_url}: {exc}")
                continue

            locations = sitemap_locations(xml_text)
            nested_sitemaps = [url for url in locations if "sitemap" in url.lower()]
            if nested_sitemaps:
                for nested_url in nested_sitemaps[:5]:
                    try:
                        nested_xml = fetch_text(nested_url, base_url=base_url)
                    except Exception as exc:
                        errors.append(f"sitemap {nested_url}: {exc}")
                        continue
                    article_urls.extend(
                        url for url in sitemap_locations(nested_xml) if self._looks_like_article_url(url, base_url)
                    )
                continue

            article_urls.extend(url for url in locations if self._looks_like_article_url(url, base_url))

        return article_urls

    def _homepage_article_urls(self, base_url: str, *, errors: list[str]) -> list[str]:
        try:
            html = fetch_text(base_url, base_url=base_url)
        except Exception as exc:
            errors.append(f"homepage {base_url}: {exc}")
            return []

        soup = BeautifulSoup(html, "html.parser")
        urls: list[str] = []
        for anchor in soup.select("a[href]"):
            url = normalize_url(str(anchor.get("href") or ""), base_url)
            if self._looks_like_article_url(url, base_url):
                urls.append(url)
        return urls

    def _looks_like_article_url(self, url: str, base_url: str) -> bool:
        if not same_domain(url, base_url):
            return False
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        if not path:
            return False
        suffix = path.rsplit(".", 1)[-1].lower()
        if suffix in {"jpg", "jpeg", "png", "gif", "webp", "pdf", "xml", "css", "js"}:
            return False

        segments = [segment.lower() for segment in path.split("/") if segment]
        if any(segment in NON_ARTICLE_SEGMENTS for segment in segments):
            return False
        if len(segments) >= 3:
            return True
        if any(char.isdigit() for char in path):
            return True
        return any(hint in path.lower() for hint in ARTICLE_PATH_HINTS) and len(segments) >= 2

    def _article_entry(self, url: str, *, base_url: str) -> dict[str, Any] | None:
        html = fetch_text(url, base_url=base_url)
        soup = BeautifulSoup(html, "html.parser")

        title = (
            meta_content(soup, ("property", "og:title"), ("name", "twitter:title"))
            or collapse_whitespace(soup.select_one("h1").get_text(" ", strip=True) if soup.select_one("h1") else "")
            or collapse_whitespace(soup.title.get_text(" ", strip=True) if soup.title else "")
        )
        if len(title) < 12:
            return None

        description = meta_content(
            soup,
            ("property", "og:description"),
            ("name", "description"),
            ("name", "twitter:description"),
        )
        content_html = extract_article_html(soup)
        content_text = strip_html(content_html)
        if len(content_text) < 120 and len(description) < 80:
            return None

        image_url = meta_content(soup, ("property", "og:image"), ("name", "twitter:image"))
        published = meta_content(
            soup,
            ("property", "article:published_time"),
            ("name", "article:published_time"),
            ("name", "pubdate"),
            ("name", "publishdate"),
            ("name", "date"),
            ("itemprop", "datePublished"),
        )
        summary = description or content_text[:400]

        entry: dict[str, Any] = {
            "title": title,
            "link": url,
            "summary": summary,
            "description": summary,
            "content": [{"value": content_html}],
        }
        if published:
            entry["published"] = published
            entry["updated"] = published
        if image_url:
            entry["media_content"] = [{"url": normalize_url(image_url, base_url)}]
        return entry

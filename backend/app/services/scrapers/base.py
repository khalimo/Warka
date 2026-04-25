from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from html import escape
from typing import Any, Optional
from urllib.parse import urldefrag, urljoin, urlparse
from urllib.robotparser import RobotFileParser
from xml.etree import ElementTree

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from app.utils.text import collapse_whitespace


logger = logging.getLogger(__name__)
settings = get_settings()

_LAST_REQUEST_BY_DOMAIN: dict[str, float] = {}
_ROBOTS_BY_DOMAIN: dict[str, Optional[RobotFileParser]] = {}

HTML_HEADERS = {
    "User-Agent": settings.scrape_user_agent,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

XML_HEADERS = {
    "User-Agent": settings.scrape_user_agent,
    "Accept": "application/xml,text/xml;q=0.9,*/*;q=0.8",
}

ARTICLE_SELECTORS = [
    "article",
    "main article",
    "[itemprop='articleBody']",
    ".entry-content",
    ".post-content",
    ".article-content",
    ".td-post-content",
    ".single-post-content",
    "main",
]

DATE_META_SELECTORS = [
    ("property", "article:published_time"),
    ("name", "article:published_time"),
    ("name", "pubdate"),
    ("name", "publishdate"),
    ("name", "date"),
    ("itemprop", "datePublished"),
]


@dataclass(frozen=True)
class ScrapeResult:
    entries: list[dict[str, Any]]
    errors: list[str] = field(default_factory=list)


class ScraperError(RuntimeError):
    pass


class SourceScraper:
    source_id: str

    def scrape(self, base_url: str, *, limit: int) -> ScrapeResult:
        raise NotImplementedError


def normalize_url(url: str, base_url: str) -> str:
    absolute_url = urljoin(base_url, url.strip())
    clean_url, _fragment = urldefrag(absolute_url)
    return clean_url


def same_domain(url: str, base_url: str) -> bool:
    url_host = urlparse(url).netloc.lower().removeprefix("www.")
    base_host = urlparse(base_url).netloc.lower().removeprefix("www.")
    return bool(url_host) and url_host == base_host


def respect_rate_limit(url: str) -> None:
    domain = urlparse(url).netloc
    if not domain:
        return
    last_request = _LAST_REQUEST_BY_DOMAIN.get(domain)
    if last_request is not None:
        elapsed = time.time() - last_request
        if elapsed < settings.scrape_rate_limit_seconds:
            time.sleep(settings.scrape_rate_limit_seconds - elapsed)
    _LAST_REQUEST_BY_DOMAIN[domain] = time.time()


def _load_robots(base_url: str) -> Optional[RobotFileParser]:
    domain = urlparse(base_url).netloc
    if not domain:
        return None
    if domain in _ROBOTS_BY_DOMAIN:
        return _ROBOTS_BY_DOMAIN[domain]

    robots_url = f"{urlparse(base_url).scheme}://{domain}/robots.txt"
    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        respect_rate_limit(robots_url)
        with httpx.Client(timeout=min(settings.feed_timeout, 10), follow_redirects=True, headers=XML_HEADERS) as client:
            response = client.get(robots_url)
    except Exception as exc:
        logger.info("Robots check failed for %s: %s", domain, exc)
        _ROBOTS_BY_DOMAIN[domain] = None
        return None

    if response.status_code == 404:
        parser.parse([])
        _ROBOTS_BY_DOMAIN[domain] = parser
        return parser
    if response.status_code >= 500:
        _ROBOTS_BY_DOMAIN[domain] = None
        return None
    if response.status_code >= 400:
        parser.parse([])
        _ROBOTS_BY_DOMAIN[domain] = parser
        return parser

    parser.parse(response.text.splitlines())
    _ROBOTS_BY_DOMAIN[domain] = parser
    return parser


def can_fetch(url: str, base_url: str) -> bool:
    if not settings.scrape_respect_robots:
        return True
    parser = _load_robots(base_url)
    if parser is None:
        return False
    return parser.can_fetch(settings.scrape_user_agent, url)


def fetch_text(url: str, *, base_url: str, headers: Optional[dict[str, str]] = None) -> str:
    if not can_fetch(url, base_url):
        raise ScraperError(f"Blocked by robots.txt: {url}")

    respect_rate_limit(url)
    with httpx.Client(timeout=min(settings.feed_timeout, 12), follow_redirects=True, headers=headers or HTML_HEADERS) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def meta_content(soup: BeautifulSoup, *selectors: tuple[str, str]) -> str:
    for attr, value in selectors:
        tag = soup.find("meta", attrs={attr: value})
        if tag and tag.get("content"):
            return collapse_whitespace(str(tag["content"]))
    return ""


def extract_article_html(soup: BeautifulSoup) -> str:
    for selector in ARTICLE_SELECTORS:
        node = soup.select_one(selector)
        if node is None:
            continue
        paragraphs = _extract_paragraphs(node, max_paragraphs=8)
        if paragraphs:
            return "".join(paragraphs)

    return "".join(_extract_paragraphs(soup, max_paragraphs=6))


def _extract_paragraphs(node: BeautifulSoup, *, max_paragraphs: int) -> list[str]:
    paragraphs: list[str] = []
    for paragraph in node.select("p"):
        text = collapse_whitespace(paragraph.get_text(" ", strip=True))
        if len(text) < 45:
            continue
        paragraphs.append(f"<p>{escape(text)}</p>")
        if len(paragraphs) >= max_paragraphs:
            break
    return paragraphs


def sitemap_locations(xml_text: str) -> list[str]:
    try:
        root = ElementTree.fromstring(xml_text.encode("utf-8"))
    except ElementTree.ParseError:
        return []

    locations: list[str] = []
    for element in root.iter():
        if element.tag.endswith("loc") and element.text:
            locations.append(element.text.strip())
    return locations


def robots_sitemaps(base_url: str) -> list[str]:
    parser = _load_robots(base_url)
    if parser is None:
        return []
    return parser.site_maps() or []

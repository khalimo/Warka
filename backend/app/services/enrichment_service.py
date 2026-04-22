from __future__ import annotations

import logging
from html import escape
from typing import Any, Optional

import httpx
from bs4 import BeautifulSoup

from app.config import get_settings
from app.services.sanitization_service import sanitize_html
from app.utils.text import collapse_whitespace, strip_html


logger = logging.getLogger(__name__)
settings = get_settings()

ARTICLE_HEADERS = {
    "User-Agent": "WarkaNewsBot/1.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

PLACEHOLDER_IMAGES = {
    "politics": "/images/politics-placeholder.svg",
    "security": "/images/security-placeholder.svg",
    "economy": "/images/economy-placeholder.svg",
    "humanitarian": "/images/humanitarian-placeholder.svg",
    "diaspora": "/images/diaspora-placeholder.svg",
    "default": "/images/default-placeholder.svg",
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


def get_category_image(category: Optional[str]) -> str:
    normalized = (category or "").strip().lower()
    return PLACEHOLDER_IMAGES.get(normalized, PLACEHOLDER_IMAGES["default"])


def _extract_meta_content(soup: BeautifulSoup, *selectors: tuple[str, str]) -> Optional[str]:
    for attr, value in selectors:
        tag = soup.find("meta", attrs={attr: value})
        if tag and tag.get("content"):
            return str(tag["content"]).strip()
    return None


def _extract_article_html(soup: BeautifulSoup) -> str:
    for selector in ARTICLE_SELECTORS:
        node = soup.select_one(selector)
        if node is None:
            continue
        paragraphs = []
        for paragraph in node.select("p"):
            text = collapse_whitespace(paragraph.get_text(" ", strip=True))
            if len(text) < 40:
                continue
            paragraphs.append(f"<p>{escape(text)}</p>")
            if len(paragraphs) >= 8:
                break
        if paragraphs:
            return sanitize_html("".join(paragraphs))

    fallback_paragraphs = []
    for paragraph in soup.find_all("p"):
        text = collapse_whitespace(paragraph.get_text(" ", strip=True))
        if len(text) < 40:
            continue
        fallback_paragraphs.append(f"<p>{escape(text)}</p>")
        if len(fallback_paragraphs) >= 6:
            break
    return sanitize_html("".join(fallback_paragraphs))


def _build_summary(title: str, excerpt: str, description: str, article_html: str) -> str:
    for candidate in (description, excerpt, strip_html(article_html)):
        cleaned = collapse_whitespace(candidate)
        if len(cleaned) >= 80:
            return cleaned[:600]
    return collapse_whitespace(f"{title}. {excerpt}")[:600]


def enrich_story_content(
    *,
    url: str,
    title: str,
    excerpt: str,
    current_content_html: str,
    current_summary: str,
    current_image_url: Optional[str],
    category: Optional[str],
) -> dict[str, Any]:
    needs_content = len(strip_html(current_content_html or "")) < 220
    needs_summary = len(collapse_whitespace(current_summary or "")) < 120
    needs_image = not current_image_url

    if not (needs_content or needs_summary or needs_image):
        return {
            "content_html": current_content_html,
            "summary": current_summary,
            "image_url": current_image_url,
        }

    try:
        with httpx.Client(
            timeout=min(settings.feed_timeout, 10),
            follow_redirects=True,
            headers=ARTICLE_HEADERS,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
    except Exception as exc:
        logger.info("Article enrichment skipped for %s: %s", url, exc)
        return {
            "content_html": current_content_html,
            "summary": current_summary or collapse_whitespace(excerpt)[:600],
            "image_url": current_image_url or get_category_image(category),
        }

    soup = BeautifulSoup(response.text, "html.parser")
    description = _extract_meta_content(
        soup,
        ("property", "og:description"),
        ("name", "description"),
        ("name", "twitter:description"),
    ) or ""
    image_url = current_image_url or _extract_meta_content(
        soup,
        ("property", "og:image"),
        ("name", "twitter:image"),
    )
    extracted_html = _extract_article_html(soup)

    final_content = current_content_html
    if len(strip_html(extracted_html)) > len(strip_html(current_content_html or "")):
        final_content = extracted_html

    final_summary = current_summary
    if needs_summary or len(collapse_whitespace(final_summary or "")) < 80:
        final_summary = _build_summary(title, excerpt, description, final_content or extracted_html)

    return {
        "content_html": final_content,
        "summary": final_summary,
        "image_url": image_url or get_category_image(category),
    }

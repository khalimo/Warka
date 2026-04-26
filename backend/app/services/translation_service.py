from __future__ import annotations

import json
import logging
from typing import Any, Optional

from openai import OpenAI

from app.config import get_settings
from app.services.sanitization_service import sanitize_html
from app.utils.text import collapse_whitespace, strip_html


logger = logging.getLogger(__name__)
settings = get_settings()

LANGUAGE_NAMES = {
    "en": "English",
    "so": "Somali",
}

MAX_TITLE_CHARS = 220
MAX_EXCERPT_CHARS = 700
MAX_SUMMARY_CHARS = 900
MAX_CONTENT_CHARS = 5000


def _normalize_language(value: Optional[str]) -> str:
    normalized = (value or "").strip().lower()
    if normalized.startswith("so"):
        return "so"
    if normalized.startswith("en"):
        return "en"
    return "en"


def target_language_for(source_language: Optional[str]) -> Optional[str]:
    source = _normalize_language(source_language)
    if source == "so":
        return "en"
    if source == "en":
        return "so"
    return None


def _clip(value: Optional[str], limit: int) -> str:
    cleaned = collapse_whitespace(value or "")
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "..."


def _build_prompt(
    *,
    target_language: str,
    title: str,
    excerpt: str,
    summary: str,
    content_html: str,
) -> str:
    return "\n".join(
        [
            f"Translate this news story into {LANGUAGE_NAMES[target_language]}.",
            "Return strict JSON with exactly these keys: title, excerpt, summary, content_html.",
            "Keep names, places, source names, numbers, and dates faithful to the original.",
            "Do not add facts, commentary, or context not present in the source text.",
            "For content_html, preserve paragraph HTML tags and translate only human-readable text.",
            "",
            "Story:",
            json.dumps(
                {
                    "title": _clip(title, MAX_TITLE_CHARS),
                    "excerpt": _clip(excerpt, MAX_EXCERPT_CHARS),
                    "summary": _clip(summary, MAX_SUMMARY_CHARS),
                    "content_html": _clip(content_html, MAX_CONTENT_CHARS),
                },
                ensure_ascii=False,
            ),
        ]
    )


def _parse_payload(raw_text: str) -> Optional[dict[str, str]]:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return None
    if not isinstance(parsed, dict):
        return None

    payload = {
        "title": _clip(str(parsed.get("title") or ""), MAX_TITLE_CHARS),
        "excerpt": _clip(str(parsed.get("excerpt") or ""), MAX_EXCERPT_CHARS),
        "summary": _clip(str(parsed.get("summary") or ""), MAX_SUMMARY_CHARS),
        "content_html": sanitize_html(str(parsed.get("content_html") or "")[:MAX_CONTENT_CHARS]),
    }
    if not payload["title"] or not payload["excerpt"]:
        return None
    return payload


def translate_story_fields(
    *,
    source_language: Optional[str],
    title: str,
    excerpt: str,
    summary: str,
    content_html: str,
) -> dict[str, Any]:
    """Return frontend-friendly translations for the opposite supported language."""

    target_language = target_language_for(source_language)
    if target_language is None:
        return {}
    if not settings.enable_translations:
        return {}
    if not settings.openai_api_key:
        return {}
    if not title or not (excerpt or summary or strip_html(content_html)):
        return {}

    client = OpenAI(api_key=settings.openai_api_key)
    prompt = _build_prompt(
        target_language=target_language,
        title=title,
        excerpt=excerpt,
        summary=summary,
        content_html=content_html,
    )

    try:
        completion = client.chat.completions.create(
            model=settings.translation_model,
            temperature=0.1,
            max_tokens=settings.translation_max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You are a careful Somali-English news translator. Respond with strict JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
        )
    except Exception as exc:  # pragma: no cover - provider failures are environment-specific
        logger.warning("Story translation failed: %s", exc)
        return {}

    content = ""
    if completion.choices and completion.choices[0].message:
        content = completion.choices[0].message.content or ""

    payload = _parse_payload(content)
    if payload is None:
        logger.warning("Story translation returned invalid JSON payload")
        return {}

    return {
        "headline": {target_language: payload["title"]},
        "excerpt": {target_language: payload["excerpt"]},
        "summary": {target_language: payload["summary"]},
        "content": {target_language: payload["content_html"]},
    }

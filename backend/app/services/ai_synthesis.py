from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Optional

from openai import OpenAI
from sqlalchemy.orm import Session

from app import models
from app.config import get_settings
from app.repositories.cluster_repository import ClusterRepository
from app.utils.dates import utc_now
from app.utils.text import strip_html


logger = logging.getLogger(__name__)
settings = get_settings()

ALLOWED_CONSENSUS_LEVELS = {"high", "medium", "low"}
MAX_STORIES_PER_CLUSTER = 8
MAX_EXCERPT_CHARS = 320
MAX_TITLE_CHARS = 180
MAX_SOURCE_NAME_CHARS = 80


@dataclass
class AISynthesisResult:
    status: str
    payload: Optional[dict[str, Any]] = None
    reason: str = ""


def _normalize_text(value: Optional[str], limit: int) -> str:
    cleaned = strip_html(value or "").replace("\n", " ").strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 1].rstrip() + "..."


def _cluster_prompt(cluster: models.Cluster) -> str:
    stories = sorted(cluster.stories, key=lambda item: item.published_at, reverse=True)[:MAX_STORIES_PER_CLUSTER]
    lines = [
        "You are synthesizing coverage of the same news event from multiple Somali news sources.",
        "Return strict JSON only with these keys:",
        'neutral_summary, coverage_differences, consensus_level, key_themes',
        "Rules:",
        "- Stay neutral and concise.",
        "- Do not invent facts not supported by the inputs.",
        "- Explain only source-level emphasis differences that are visible in the inputs.",
        "- consensus_level must be one of: high, medium, low.",
        "- key_themes must be an array of 1 to 5 short strings.",
        "",
        "Cluster title: {0}".format(_normalize_text(cluster.title, MAX_TITLE_CHARS)),
        "",
        "Stories:",
    ]

    for index, story in enumerate(stories, start=1):
        lines.extend(
            [
                "{0}. Source: {1}".format(index, _normalize_text(story.source.name, MAX_SOURCE_NAME_CHARS)),
                "   Title: {0}".format(_normalize_text(story.title, MAX_TITLE_CHARS)),
                "   Excerpt: {0}".format(_normalize_text(story.excerpt or story.summary or "", MAX_EXCERPT_CHARS)),
            ]
        )

    return "\n".join(lines)


def _build_client() -> Optional[OpenAI]:
    if not settings.enable_ai_synthesis:
        return None
    if not settings.openai_api_key:
        return None
    return OpenAI(api_key=settings.openai_api_key)


def _parse_ai_payload(raw_text: str) -> Optional[dict[str, Any]]:
    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        return None

    neutral_summary = _normalize_text(parsed.get("neutral_summary"), 900)
    coverage_differences = _normalize_text(parsed.get("coverage_differences"), 900)
    consensus_level = str(parsed.get("consensus_level") or "").strip().lower()
    if consensus_level not in ALLOWED_CONSENSUS_LEVELS:
        return None

    raw_themes = parsed.get("key_themes") or []
    if not isinstance(raw_themes, list):
        return None

    key_themes = []
    for theme in raw_themes:
        cleaned = _normalize_text(str(theme), 40)
        if cleaned and cleaned not in key_themes:
            key_themes.append(cleaned)
        if len(key_themes) >= 5:
            break

    if not neutral_summary:
        return None

    return {
        "ai_neutral_summary": neutral_summary,
        "ai_coverage_differences": coverage_differences,
        "ai_consensus_level": consensus_level,
        "ai_key_themes": json.dumps(key_themes),
        "ai_generated_at": utc_now(),
        "ai_model_used": settings.ai_model,
        "has_ai_synthesis": True,
    }


def synthesize_cluster(
    db: Session,
    cluster_id: str,
    force: bool = False,
    dry_run: bool = False,
) -> AISynthesisResult:
    repository = ClusterRepository(db)
    cluster = repository.get(cluster_id)
    if cluster is None:
        return AISynthesisResult(status="failed", reason="cluster_not_found")

    if len(cluster.stories) < 2:
        return AISynthesisResult(status="skipped", reason="not_enough_stories")

    if cluster.ai_generated_at and not force:
        return AISynthesisResult(status="skipped", reason="already_synthesized")

    if not settings.enable_ai_synthesis:
        return AISynthesisResult(status="skipped", reason="ai_disabled")

    if not settings.openai_api_key:
        return AISynthesisResult(status="skipped", reason="missing_api_key")

    client = _build_client()
    if client is None:
        return AISynthesisResult(status="skipped", reason="client_unavailable")

    prompt = _cluster_prompt(cluster)

    try:
        completion = client.chat.completions.create(
            model=settings.ai_model,
            temperature=settings.ai_temperature,
            max_tokens=settings.ai_max_tokens,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": "You analyze overlapping news coverage and respond with strict JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
        )
    except Exception as exc:  # pragma: no cover - network/provider failures are environment-specific
        logger.warning("AI synthesis failed for cluster %s: %s", cluster_id, exc)
        return AISynthesisResult(status="failed", reason="provider_error")

    content = ""
    if completion.choices and completion.choices[0].message:
        content = completion.choices[0].message.content or ""

    payload = _parse_ai_payload(content)
    if payload is None:
        logger.warning("AI synthesis produced invalid payload for cluster %s", cluster_id)
        return AISynthesisResult(status="failed", reason="invalid_payload")

    if dry_run:
        return AISynthesisResult(status="updated", payload=payload, reason="dry_run")

    try:
        for field, value in payload.items():
            setattr(cluster, field, value)
        repository.save(cluster)
    except Exception as exc:  # pragma: no cover - persistence failures are environment-specific
        db.rollback()
        logger.warning("Persisting AI synthesis failed for cluster %s: %s", cluster_id, exc)
        return AISynthesisResult(status="failed", reason="persistence_error")

    return AISynthesisResult(status="updated", payload=payload)

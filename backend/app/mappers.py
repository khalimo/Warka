from __future__ import annotations

import json

from app import models, schemas


def map_source_to_response(db_source: models.Source) -> schemas.Source:
    return schemas.Source.model_validate(db_source)


def map_story_to_response(db_story: models.Story) -> schemas.Story:
    framing = None
    if db_story.framing_label:
        framing = schemas.Framing(
            id=f"{db_story.id}-framing",
            label=db_story.framing_label,
            description=db_story.framing_description,
            tone=db_story.framing_tone,
        )

    return schemas.Story(
        id=db_story.id,
        slug=db_story.slug,
        title=db_story.title,
        excerpt=db_story.excerpt,
        content_html=db_story.content_html,
        summary=db_story.summary,
        source_id=db_story.source_id,
        original_url=db_story.original_url,
        canonical_url_hash=db_story.canonical_url_hash,
        published_at=db_story.published_at,
        updated_at=db_story.updated_at,
        fetched_at=db_story.fetched_at,
        region=db_story.region,
        category=db_story.category,
        topics=list(db_story.topics or []),
        translations=dict(db_story.translations or {}),
        image_url=db_story.image_url,
        reading_time=db_story.reading_time,
        is_breaking=db_story.is_breaking,
        cluster_id=db_story.cluster_id,
        source=map_source_to_response(db_story.source),
        framing=framing,
        created_at=db_story.created_at,
    )


def _coerce_theme_list(raw_value) -> list[str]:
    if raw_value is None:
        return []
    if isinstance(raw_value, list):
        return [str(item).strip() for item in raw_value if str(item).strip()]
    if isinstance(raw_value, str):
        cleaned = raw_value.strip()
        if not cleaned:
            return []
        try:
            parsed = json.loads(cleaned)
        except json.JSONDecodeError:
            return []
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    return []


def map_cluster_to_response(db_cluster: models.Cluster) -> schemas.Cluster:
    story_items = [map_story_to_response(story) for story in db_cluster.stories]
    unique_sources: dict[str, schemas.Source] = {}
    for story in db_cluster.stories:
        unique_sources[story.source.id] = map_source_to_response(story.source)

    return schemas.Cluster(
        id=db_cluster.id,
        title=db_cluster.title,
        common_facts=db_cluster.common_facts,
        coverage_differences=db_cluster.coverage_differences,
        neutral_summary=db_cluster.neutral_summary,
        key_themes=list(db_cluster.key_themes or []),
        consensus_level=db_cluster.consensus_level,
        ai_neutral_summary=db_cluster.ai_neutral_summary,
        ai_coverage_differences=db_cluster.ai_coverage_differences,
        ai_consensus_level=db_cluster.ai_consensus_level,
        ai_key_themes=_coerce_theme_list(db_cluster.ai_key_themes),
        ai_generated_at=db_cluster.ai_generated_at,
        ai_model_used=db_cluster.ai_model_used,
        has_ai_synthesis=db_cluster.has_ai_synthesis,
        ai_review_status=db_cluster.ai_review_status or "unreviewed",
        ai_review_note=db_cluster.ai_review_note,
        ai_reviewed_at=db_cluster.ai_reviewed_at,
        story_count=db_cluster.story_count,
        created_at=db_cluster.created_at,
        updated_at=db_cluster.updated_at,
        stories=story_items,
        sources=list(unique_sources.values()),
    )

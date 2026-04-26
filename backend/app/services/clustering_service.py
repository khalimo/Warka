from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from statistics import mean
from typing import Any, Optional

from sqlalchemy.orm import Session

from app import models
from app.config import get_settings
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.story_repository import StoryRepository
from app.utils.dates import utc_now
from app.utils.slug import slugify
from app.utils.text import jaccard_similarity, strip_html, tokenize, top_terms


logger = logging.getLogger(__name__)
settings = get_settings()


KNOWN_EVENT_ENTITIES = {
    "al shabaab": "Al-Shabaab",
    "al-shabaab": "Al-Shabaab",
    "aussom": "AUSSOM",
    "atmis": "ATMIS",
    "african union": "African Union",
    "united nations": "United Nations",
    "un": "United Nations",
    "igad": "IGAD",
    "nisa": "NISA",
    "somali national army": "Somali National Army",
    "sna": "Somali National Army",
    "villa somalia": "Villa Somalia",
    "federal government": "Federal Government",
    "somali government": "Somali Government",
    "somaliland": "Somaliland",
    "puntland": "Puntland",
    "jubaland": "Jubaland",
    "hirshabelle": "Hirshabelle",
    "galmudug": "Galmudug",
    "south west": "South West State",
    "muqdisho": "Mogadishu",
    "mogadishu": "Mogadishu",
    "banaadir": "Banadir",
    "banadir": "Banadir",
    "hargeisa": "Hargeisa",
    "kismaayo": "Kismayo",
    "kismayo": "Kismayo",
    "garoowe": "Garowe",
    "garowe": "Garowe",
    "boosaaso": "Bosaso",
    "bosaso": "Bosaso",
    "baydhabo": "Baidoa",
    "baidoa": "Baidoa",
    "beledweyne": "Beledweyne",
    "las anod": "Las Anod",
    "laascaanood": "Las Anod",
    "gedo": "Gedo",
    "hiiraan": "Hiiraan",
    "mudug": "Mudug",
    "nugaal": "Nugaal",
    "sool": "Sool",
    "sanaag": "Sanaag",
    "togdheer": "Togdheer",
    "world bank": "World Bank",
    "imf": "IMF",
}

ENTITY_PATTERN = re.compile(
    r"\b[A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’-]+(?:\s+(?:[A-Z][A-Za-zÀ-ÖØ-öø-ÿ'’-]+|of|and|for|de|al)){0,3}\b"
)


@dataclass(frozen=True)
class EventFeatures:
    tokens: set[str]
    entities: set[str]
    categories: set[str]
    regions: set[str]
    topics: set[str]
    sources: set[str]
    languages: set[str]
    published_at: datetime


@dataclass(frozen=True)
class EventScore:
    total: float
    lexical: float
    entity: float
    topical: float
    temporal: float
    diversity: float


def _story_text(story: models.Story) -> str:
    return " ".join(
        item
        for item in [
            story.title,
            story.excerpt or "",
            strip_html(story.summary or ""),
            " ".join(story.topics or []),
            story.region or "",
            story.category or "",
        ]
        if item
    )


def _canonical_entity(value: str) -> str:
    return " ".join(tokenize(value))


def _extract_entities(text: str) -> set[str]:
    normalized_text = f" {(text or '').lower()} "
    entities = {
        _canonical_entity(display)
        for phrase, display in KNOWN_EVENT_ENTITIES.items()
        if f" {phrase} " in normalized_text
    }

    for match in ENTITY_PATTERN.findall(text or ""):
        cleaned = _canonical_entity(match)
        if cleaned and cleaned not in {"somali", "somalia"}:
            entities.add(cleaned)

    return {entity for entity in entities if entity}


def _published_at(story: models.Story) -> datetime:
    value = story.published_at
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _story_language(story: models.Story) -> str:
    return (story.source.language if story.source else None) or "unknown"


def _features_for_story(story: models.Story) -> EventFeatures:
    text = _story_text(story)
    return EventFeatures(
        tokens=tokenize(text),
        entities=_extract_entities(text),
        categories={story.category.lower()} if story.category else set(),
        regions={story.region.lower()} if story.region else set(),
        topics={str(topic).lower() for topic in (story.topics or []) if str(topic).strip()},
        sources={story.source_id},
        languages={_story_language(story).lower()},
        published_at=_published_at(story),
    )


def _merge_features(features: list[EventFeatures]) -> EventFeatures:
    if not features:
        now = utc_now()
        return EventFeatures(set(), set(), set(), set(), set(), set(), set(), now)

    return EventFeatures(
        tokens=set().union(*(item.tokens for item in features)),
        entities=set().union(*(item.entities for item in features)),
        categories=set().union(*(item.categories for item in features)),
        regions=set().union(*(item.regions for item in features)),
        topics=set().union(*(item.topics for item in features)),
        sources=set().union(*(item.sources for item in features)),
        languages=set().union(*(item.languages for item in features)),
        published_at=max(item.published_at for item in features),
    )


def _temporal_score(story: models.Story, cluster_stories: list[models.Story]) -> float:
    if not cluster_stories:
        return 0.0
    story_time = _published_at(story)
    nearest_hours = min(
        abs((story_time - _published_at(item)).total_seconds()) / 3600 for item in cluster_stories
    )
    return max(0.0, min(1.0, math.pow(2, -nearest_hours / 36)))


def _topical_score(story_features: EventFeatures, cluster_features: EventFeatures) -> float:
    category_score = jaccard_similarity(story_features.categories, cluster_features.categories)
    region_score = jaccard_similarity(story_features.regions, cluster_features.regions)
    topic_score = jaccard_similarity(story_features.topics, cluster_features.topics)
    return max(category_score, region_score, topic_score)


def _diversity_score(story_features: EventFeatures, cluster_features: EventFeatures) -> float:
    source_bonus = 1.0 if not story_features.sources <= cluster_features.sources else 0.35
    language_bonus = 1.0 if not story_features.languages <= cluster_features.languages else 0.45
    return (source_bonus * 0.65) + (language_bonus * 0.35)


def _score_story_against_cluster(
    story: models.Story,
    story_features: EventFeatures,
    cluster_stories: list[models.Story],
    cluster_features: EventFeatures,
) -> EventScore:
    lexical = jaccard_similarity(story_features.tokens, cluster_features.tokens)
    entity = jaccard_similarity(story_features.entities, cluster_features.entities)
    topical = _topical_score(story_features, cluster_features)
    temporal = _temporal_score(story, cluster_stories)
    diversity = _diversity_score(story_features, cluster_features)
    total = (
        lexical * 0.46
        + entity * 0.27
        + topical * 0.11
        + temporal * 0.12
        + diversity * 0.04
    )
    return EventScore(total, lexical, entity, topical, temporal, diversity)


def _is_event_match(score: EventScore) -> bool:
    threshold = min(max(settings.cluster_similarity_threshold, 0.35), 0.52)
    has_shared_event_signal = score.lexical >= 0.18 or score.entity >= 0.25
    strong_entity_match = score.entity >= 0.42 and score.temporal >= 0.45
    timely_text_match = score.lexical >= 0.25 and score.temporal >= 0.35
    return (score.total >= threshold and has_shared_event_signal) or strong_entity_match or timely_text_match


def _cluster_tokens(stories: list[models.Story]) -> set[str]:
    text = " ".join(_story_text(story) for story in stories)
    return tokenize(text)


def _cluster_features(stories: list[models.Story]) -> EventFeatures:
    return _merge_features([_features_for_story(story) for story in stories])


def _story_time_span_hours(stories: list[models.Story]) -> float:
    if len(stories) < 2:
        return 0.0
    dates = [_published_at(story) for story in stories]
    return round((max(dates) - min(dates)).total_seconds() / 3600, 1)


def _score_cluster_cohesion(stories: list[models.Story]) -> EventScore:
    if len(stories) < 2:
        return EventScore(0.35, 0.0, 0.0, 0.0, 1.0, 0.0)

    pair_scores: list[EventScore] = []
    for index, story in enumerate(stories):
        other_stories = stories[:index] + stories[index + 1 :]
        pair_scores.append(
            _score_story_against_cluster(
                story,
                _features_for_story(story),
                other_stories,
                _cluster_features(other_stories),
            )
        )

    return EventScore(
        total=mean(score.total for score in pair_scores),
        lexical=mean(score.lexical for score in pair_scores),
        entity=mean(score.entity for score in pair_scores),
        topical=mean(score.topical for score in pair_scores),
        temporal=mean(score.temporal for score in pair_scores),
        diversity=mean(score.diversity for score in pair_scores),
    )


def _confidence_score(stories: list[models.Story], cohesion: EventScore) -> int:
    if not stories:
        return 0
    source_count = len({story.source_id for story in stories})
    language_count = len({_story_language(story).lower() for story in stories})
    diversity = min(1.0, source_count / 4)
    language_mix = min(1.0, language_count / 2)
    volume = min(1.0, len(stories) / 5)
    confidence = cohesion.total * 0.58 + diversity * 0.18 + language_mix * 0.12 + volume * 0.12
    return max(0, min(100, round(confidence * 100)))


def _consensus_from_confidence(confidence: int) -> str:
    if confidence >= 72:
        return "high"
    if confidence >= 50:
        return "medium"
    return "low"


def _event_signature(
    stories: list[models.Story],
    cluster_features: EventFeatures,
    cohesion: EventScore,
    confidence: int,
    event_terms: list[str],
) -> dict[str, Any]:
    return {
        "method": "hybrid_event_v2",
        "confidence": confidence,
        "components": {
            "cohesion": round(cohesion.total, 3),
            "lexical": round(cohesion.lexical, 3),
            "entity": round(cohesion.entity, 3),
            "topical": round(cohesion.topical, 3),
            "temporal": round(cohesion.temporal, 3),
            "diversity": round(cohesion.diversity, 3),
        },
        "entities": sorted(cluster_features.entities)[:12],
        "event_terms": event_terms[:8],
        "source_count": len({story.source_id for story in stories}),
        "languages": sorted({_story_language(story).lower() for story in stories}),
        "temporal_span_hours": _story_time_span_hours(stories),
        "story_ids": [str(story.id) for story in stories[:12]],
        "updated_at": utc_now().isoformat(),
    }


def _coverage_differences(stories: list[models.Story], event_terms: list[str]) -> str:
    if len(stories) <= 1:
        return "Only one report is currently available for this event. More contrast will appear as other sources publish."

    source_count = len({story.source_id for story in stories})
    language_count = len({_story_language(story).lower() for story in stories})
    span_hours = _story_time_span_hours(stories)
    terms = ", ".join(event_terms[:4]) if event_terms else "the same developing event"
    return (
        f"Coverage spans {source_count} source{'s' if source_count != 1 else ''} "
        f"across {language_count} language group{'s' if language_count != 1 else ''} "
        f"over about {span_hours:g} hours. Compare headlines and framing around {terms} "
        "to see where outlets differ in emphasis."
    )


def _summarize_cluster(cluster: models.Cluster, story_candidates: Optional[list[models.Story]] = None) -> None:
    stories = sorted(
        story_candidates if story_candidates is not None else cluster.stories,
        key=lambda item: item.published_at,
        reverse=True,
    )
    if not stories:
        cluster.story_count = 0
        cluster.confidence_score = 0
        cluster.event_signature = {}
        return

    lead_story = stories[0]
    features = _cluster_features(stories)
    cohesion = _score_cluster_cohesion(stories)
    confidence = _confidence_score(stories, cohesion)
    categories = [story.category or "general" for story in stories]
    event_terms = top_terms(
        categories
        + [story.title for story in stories]
        + [story.region or "" for story in stories]
        + list(features.entities),
        limit=8,
    )
    lead_summary = lead_story.excerpt or strip_html(lead_story.summary or "") or lead_story.title

    cluster.story_count = len(stories)
    cluster.title = lead_story.title
    cluster.common_facts = lead_summary
    cluster.neutral_summary = lead_summary
    cluster.coverage_differences = _coverage_differences(stories, event_terms)
    cluster.key_themes = event_terms[:5] or ["general"]
    cluster.confidence_score = confidence
    cluster.consensus_level = _consensus_from_confidence(confidence)
    cluster.event_signature = _event_signature(stories, features, cohesion, confidence, event_terms)


def run_clustering(db: Session) -> dict[str, int]:
    logger.info("Starting clustering run")
    cutoff = utc_now() - timedelta(hours=settings.ingest_lookback_hours)
    story_repo = StoryRepository(db)
    cluster_repo = ClusterRepository(db)

    unclustered = story_repo.recent_unclustered(cutoff)
    recent_clusters = cluster_repo.recent_clusters(cutoff)
    cluster_story_map: dict[str, list[models.Story]] = {cluster.id: list(cluster.stories) for cluster in recent_clusters}

    created_clusters = 0
    assigned_stories = 0
    updated_clusters = 0

    for story in unclustered:
        story_features = _features_for_story(story)
        best_cluster: Optional[models.Cluster] = None
        best_score: Optional[EventScore] = None

        for cluster in recent_clusters:
            cluster_stories = cluster_story_map.get(cluster.id, [])
            if not cluster_stories:
                continue
            cluster_features = _cluster_features(cluster_stories)
            score = _score_story_against_cluster(story, story_features, cluster_stories, cluster_features)
            if _is_event_match(score) and (best_score is None or score.total > best_score.total):
                best_cluster = cluster
                best_score = score

        if best_cluster is None:
            cluster_id = f"cluster-{slugify(story.title)[:24]}-{str(story.id).split('-')[0]}"
            best_cluster = models.Cluster(
                id=cluster_id,
                title=story.title,
                common_facts=story.excerpt or story.title,
                coverage_differences="",
                neutral_summary=story.excerpt or story.title,
                key_themes=[story.category] if story.category else ["general"],
                consensus_level="low",
                story_count=0,
                confidence_score=0,
                event_signature={},
            )
            cluster_repo.add(best_cluster)
            recent_clusters.append(best_cluster)
            cluster_story_map[best_cluster.id] = []
            created_clusters += 1

        story.cluster_id = best_cluster.id
        cluster_story_map[best_cluster.id].append(story)
        assigned_stories += 1

    for cluster in recent_clusters:
        if cluster.id in cluster_story_map:
            _summarize_cluster(cluster, cluster_story_map[cluster.id])
            updated_clusters += 1

    db.commit()
    logger.info(
        "Clustering run complete: created_clusters=%s assigned_stories=%s updated_clusters=%s",
        created_clusters,
        assigned_stories,
        updated_clusters,
    )
    return {
        "created_clusters": created_clusters,
        "assigned_stories": assigned_stories,
        "updated_clusters": updated_clusters,
    }

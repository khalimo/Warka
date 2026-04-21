from __future__ import annotations

import logging
from collections import defaultdict
from datetime import timedelta

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


def _cluster_tokens(stories: list[models.Story]) -> set[str]:
    text = " ".join(f"{story.title} {story.excerpt or ''}" for story in stories)
    return tokenize(text)


def _summarize_cluster(cluster: models.Cluster) -> None:
    stories = sorted(cluster.stories, key=lambda item: item.published_at, reverse=True)
    if not stories:
        cluster.story_count = 0
        return

    lead_story = stories[0]
    cluster.story_count = len(stories)
    cluster.title = lead_story.title
    cluster.common_facts = lead_story.excerpt or strip_html(lead_story.summary or "") or lead_story.title
    cluster.neutral_summary = lead_story.excerpt or strip_html(lead_story.summary or "") or lead_story.title
    cluster.coverage_differences = (
        "Coverage is still converging across outlets."
        if len(stories) > 1
        else ""
    )
    categories = [story.category or "general" for story in stories]
    cluster.key_themes = top_terms(categories + [story.title for story in stories], limit=3)


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

    for story in unclustered:
        story_tokens = tokenize(f"{story.title} {story.excerpt or ''}")
        best_cluster: models.Cluster | None = None
        best_score = 0.0

        for cluster in recent_clusters:
            cluster_tokens = _cluster_tokens(cluster_story_map.get(cluster.id, []))
            score = jaccard_similarity(story_tokens, cluster_tokens)
            if score >= settings.cluster_similarity_threshold and score > best_score:
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
            )
            cluster_repo.add(best_cluster)
            recent_clusters.append(best_cluster)
            cluster_story_map[best_cluster.id] = []
            created_clusters += 1

        story.cluster_id = best_cluster.id
        cluster_story_map[best_cluster.id].append(story)
        assigned_stories += 1

        scores = [
            jaccard_similarity(story_tokens, tokenize(f"{other.title} {other.excerpt or ''}"))
            for other in cluster_story_map[best_cluster.id]
            if other.id != story.id
        ]
        if not scores:
            best_cluster.consensus_level = "low"
        elif min(scores) > 0.7:
            best_cluster.consensus_level = "high"
        elif min(scores) > 0.5:
            best_cluster.consensus_level = "medium"
        else:
            best_cluster.consensus_level = "low"

    for cluster in recent_clusters:
        if cluster.id in cluster_story_map:
            _summarize_cluster(cluster)

    db.commit()
    logger.info("Clustering run complete: created_clusters=%s assigned_stories=%s", created_clusters, assigned_stories)
    return {"created_clusters": created_clusters, "assigned_stories": assigned_stories}

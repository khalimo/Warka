from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.auth import require_internal_api_key
from app.database import get_db
from app.mappers import map_cluster_to_response
from app.rate_limit import require_internal_rate_limit
from app.repositories.cluster_repository import ClusterRepository
from app.schemas import AIReviewUpdateRequest, AIReviewUpdateResponse, Cluster, PaginatedResponse
from app.utils.dates import utc_now


router = APIRouter(prefix="/api", tags=["clusters"])

ALLOWED_AI_REVIEW_STATUSES = {"unreviewed", "good", "weak", "misleading", "hallucinated"}
ALLOWED_COMPARE_FILTERS = {"somalia", "world", "politics", "security", "humanitarian", "economy"}
ALLOWED_CONFIDENCE_FILTERS = {"low", "medium", "high"}
ALLOWED_LANGUAGE_FILTERS = {"so", "en"}


def _normalize_filter(value: Optional[str]) -> Optional[str]:
    normalized = (value or "").strip().lower() or None
    if normalized in ALLOWED_COMPARE_FILTERS:
        return normalized
    return None


def _normalize_allowed(value: Optional[str], allowed: set[str]) -> Optional[str]:
    normalized = (value or "").strip().lower() or None
    if normalized in allowed:
        return normalized
    return None


def _normalize_public_string(value: Optional[str]) -> Optional[str]:
    normalized = (value or "").strip().lower()
    if not normalized or len(normalized) > 80:
        return None
    return normalized


@router.get("/clusters", response_model=PaginatedResponse[Cluster])
def get_clusters(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    has_ai_synthesis: Optional[bool] = Query(default=None),
    ai_review_status: Optional[str] = Query(default=None),
    renderable_only: bool = Query(default=True),
    category: Optional[str] = Query(default=None),
    region: Optional[str] = Query(default=None),
    source_id: Optional[str] = Query(default=None),
    language: Optional[str] = Query(default=None),
    source_category: Optional[str] = Query(default=None),
    confidence: Optional[str] = Query(default=None),
    recent_hours: Optional[int] = Query(default=None, ge=1, le=720),
    min_sources: Optional[int] = Query(default=None, ge=1, le=50),
    max_sources: Optional[int] = Query(default=None, ge=1, le=50),
    db: Session = Depends(get_db),
) -> PaginatedResponse[Cluster]:
    repository = ClusterRepository(db)
    normalized_review_status = (ai_review_status or "").strip().lower() or None
    if normalized_review_status not in ALLOWED_AI_REVIEW_STATUSES:
        normalized_review_status = None
    normalized_category = _normalize_filter(category)
    normalized_region = _normalize_filter(region)
    normalized_source_id = (source_id or "").strip() or None
    normalized_language = _normalize_allowed(language, ALLOWED_LANGUAGE_FILTERS)
    normalized_source_category = _normalize_public_string(source_category)
    normalized_confidence = _normalize_allowed(confidence, ALLOWED_CONFIDENCE_FILTERS)

    clusters = repository.list_paginated(
        limit=limit,
        offset=offset,
        has_ai_synthesis=has_ai_synthesis,
        ai_review_status=normalized_review_status,
        renderable_only=renderable_only,
        category=normalized_category,
        region=normalized_region,
        source_id=normalized_source_id,
        language=normalized_language,
        source_category=normalized_source_category,
        confidence=normalized_confidence,
        recent_hours=recent_hours,
        min_sources=min_sources,
        max_sources=max_sources,
    )
    return PaginatedResponse[Cluster](
        items=[map_cluster_to_response(cluster) for cluster in clusters],
        total=repository.count_all(
            has_ai_synthesis=has_ai_synthesis,
            ai_review_status=normalized_review_status,
            renderable_only=renderable_only,
            category=normalized_category,
            region=normalized_region,
            source_id=normalized_source_id,
            language=normalized_language,
            source_category=normalized_source_category,
            confidence=normalized_confidence,
            recent_hours=recent_hours,
            min_sources=min_sources,
            max_sources=max_sources,
        ),
        limit=limit,
        offset=offset,
    )


@router.get("/clusters/{cluster_id}", response_model=Cluster)
def get_cluster(
    cluster_id: str = Path(...),
    renderable_only: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> Cluster:
    repository = ClusterRepository(db)
    cluster = repository.get(cluster_id)
    if cluster is None or (renderable_only and not repository.is_renderable(cluster_id)):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found")
    return map_cluster_to_response(cluster)


@router.patch(
    "/internal/clusters/{cluster_id}/ai-review",
    response_model=AIReviewUpdateResponse,
    dependencies=[Depends(require_internal_api_key), Depends(require_internal_rate_limit)],
)
def update_cluster_ai_review(
    payload: AIReviewUpdateRequest,
    cluster_id: str = Path(...),
    db: Session = Depends(get_db),
) -> AIReviewUpdateResponse:
    repository = ClusterRepository(db)
    cluster = repository.get(cluster_id)
    if cluster is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found")

    cluster.ai_review_status = payload.review_status
    cluster.ai_review_note = payload.review_note
    cluster.ai_reviewed_at = None if payload.review_status == "unreviewed" else utc_now()
    repository.save(cluster)

    return AIReviewUpdateResponse(
        cluster_id=cluster.id,
        ai_review_status=cluster.ai_review_status or "unreviewed",
        ai_review_note=cluster.ai_review_note,
        ai_reviewed_at=cluster.ai_reviewed_at,
    )

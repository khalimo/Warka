from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.auth import require_internal_api_key
from app.database import get_db
from app.mappers import map_cluster_to_response
from app.repositories.cluster_repository import ClusterRepository
from app.schemas import AIReviewUpdateRequest, AIReviewUpdateResponse, Cluster, PaginatedResponse
from app.utils.dates import utc_now


router = APIRouter(prefix="/api", tags=["clusters"])

ALLOWED_AI_REVIEW_STATUSES = {"unreviewed", "good", "weak", "misleading", "hallucinated"}


@router.get("/clusters", response_model=PaginatedResponse[Cluster])
def get_clusters(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    has_ai_synthesis: Optional[bool] = Query(default=None),
    ai_review_status: Optional[str] = Query(default=None),
    renderable_only: bool = Query(default=True),
    db: Session = Depends(get_db),
) -> PaginatedResponse[Cluster]:
    repository = ClusterRepository(db)
    normalized_review_status = (ai_review_status or "").strip().lower() or None
    if normalized_review_status not in ALLOWED_AI_REVIEW_STATUSES:
        normalized_review_status = None

    clusters = repository.list_paginated(
        limit=limit,
        offset=offset,
        has_ai_synthesis=has_ai_synthesis,
        ai_review_status=normalized_review_status,
        renderable_only=renderable_only,
    )
    return PaginatedResponse[Cluster](
        items=[map_cluster_to_response(cluster) for cluster in clusters],
        total=repository.count_all(
            has_ai_synthesis=has_ai_synthesis,
            ai_review_status=normalized_review_status,
            renderable_only=renderable_only,
        ),
        limit=limit,
        offset=offset,
    )


@router.patch(
    "/internal/clusters/{cluster_id}/ai-review",
    response_model=AIReviewUpdateResponse,
    dependencies=[Depends(require_internal_api_key)],
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

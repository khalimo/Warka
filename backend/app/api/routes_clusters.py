from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.mappers import map_cluster_to_response
from app.repositories.cluster_repository import ClusterRepository
from app.schemas import Cluster, PaginatedResponse


router = APIRouter(prefix="/api", tags=["clusters"])


@router.get("/clusters", response_model=PaginatedResponse[Cluster])
def get_clusters(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedResponse[Cluster]:
    repository = ClusterRepository(db)
    clusters = repository.list_paginated(limit=limit, offset=offset)
    return PaginatedResponse[Cluster](
        items=[map_cluster_to_response(cluster) for cluster in clusters],
        total=repository.count_all(),
        limit=limit,
        offset=offset,
    )


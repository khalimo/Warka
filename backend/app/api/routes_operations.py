from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models
from app.auth import require_internal_api_key
from app.database import get_db
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.ingest_run_repository import IngestRunRepository
from app.repositories.source_repository import SourceRepository
from app.schemas import IngestRun, OperationsSummary
from app.services.health_monitor import build_source_health_report
from app.utils.dates import utc_now


router = APIRouter(
    prefix="/api/internal",
    tags=["operations"],
    dependencies=[Depends(require_internal_api_key)],
)


@router.get("/operations", response_model=OperationsSummary)
def get_operations_summary(db: Session = Depends(get_db)) -> OperationsSummary:
    source_repo = SourceRepository(db)
    latest_run = IngestRunRepository(db).latest()
    source_health = build_source_health_report(db)
    story_count = int(db.scalar(select(func.count(models.Story.id))) or 0)
    translated_sample_count = sum(
        1
        for translations in db.scalars(
            select(models.Story.translations).order_by(models.Story.published_at.desc()).limit(500)
        )
        if translations
    )

    return OperationsSummary(
        status="ok",
        generated_at=utc_now(),
        story_count=story_count,
        cluster_count=ClusterRepository(db).count_all(),
        source_count=len(source_health),
        active_source_count=source_repo.count_active(),
        translated_story_sample_count=translated_sample_count,
        latest_ingest_run=IngestRun.model_validate(latest_run) if latest_run else None,
        source_health=source_health,
    )

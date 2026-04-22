from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models
from app.config import get_settings
from app.utils.dates import utc_now


logger = logging.getLogger(__name__)
settings = get_settings()


def _blend_response_time(existing: Optional[int], new_value: Optional[int]) -> Optional[int]:
    if new_value is None:
        return existing
    if existing is None:
        return int(new_value)
    return int(round((existing * 4 + new_value) / 5))


def record_validation_result(
    db: Session,
    source: models.Source,
    *,
    is_valid: bool,
    error: Optional[str],
    response_time_ms: Optional[int],
    enable_on_success: bool,
) -> None:
    source.last_validated_at = utc_now()
    source.avg_response_time_ms = _blend_response_time(source.avg_response_time_ms, response_time_ms)
    if is_valid:
        source.validation_status = "verified"
        source.last_error_message = None
        if enable_on_success:
            source.is_active = True
        if source.consecutive_failures < 3:
            source.consecutive_failures = 0
    else:
        prior_status = source.validation_status
        source.is_active = False
        source.validation_status = "disabled" if prior_status == "disabled" else "failed"
        source.last_error_message = error
        source.last_error_at = utc_now()
    db.add(source)
    db.commit()


def record_source_success(
    db: Session,
    source: models.Source,
    *,
    response_time_ms: Optional[int],
) -> None:
    source.last_success_at = utc_now()
    source.last_error_at = None
    source.last_error_message = None
    source.validation_status = "verified"
    source.consecutive_failures = 0
    source.avg_response_time_ms = _blend_response_time(source.avg_response_time_ms, response_time_ms)
    db.add(source)
    db.commit()


def record_source_failure(
    db: Session,
    source: models.Source,
    *,
    error: str,
    response_time_ms: Optional[int] = None,
) -> None:
    source.last_error_at = utc_now()
    source.last_error_message = error
    source.validation_status = "failed"
    source.consecutive_failures = int(source.consecutive_failures or 0) + 1
    source.avg_response_time_ms = _blend_response_time(source.avg_response_time_ms, response_time_ms)
    if source.consecutive_failures >= 3:
        source.is_active = False
        source.validation_status = "disabled"
        logger.warning("Source %s disabled after %s consecutive failures", source.name, source.consecutive_failures)
    db.add(source)
    db.commit()


def build_source_health_report(db: Session) -> list[dict[str, Any]]:
    cutoff = utc_now() - timedelta(hours=24)
    story_counts = {
        source_id: int(count)
        for source_id, count in db.execute(
            select(models.Story.source_id, func.count(models.Story.id))
            .where(models.Story.created_at >= cutoff)
            .group_by(models.Story.source_id)
        )
    }

    sources = list(
        db.scalars(select(models.Source).order_by(models.Source.priority.asc(), models.Source.name.asc()))
    )
    return [
        {
            "id": source.id,
            "name": source.name,
            "is_enabled": source.is_active,
            "validation_status": source.validation_status,
            "last_validated_at": source.last_validated_at.isoformat() if source.last_validated_at else None,
            "last_success_at": source.last_success_at.isoformat() if source.last_success_at else None,
            "last_failure_at": source.last_error_at.isoformat() if source.last_error_at else None,
            "last_error": source.last_error_message,
            "consecutive_failures": source.consecutive_failures,
            "stories_ingested_24h": story_counts.get(source.id, 0),
            "avg_response_time_ms": source.avg_response_time_ms,
        }
        for source in sources
    ]

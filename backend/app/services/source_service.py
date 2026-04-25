from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from sqlalchemy.orm import Session

from app.config import get_settings
from app.repositories.source_repository import SourceRepository
from app.services.feed_service import verify_feed
from app.services.health_monitor import record_validation_result
from app.services.scraper_service import scrape_source_entries
from app.services.source_registry import SOURCE_CANDIDATES, registry_seed_payloads
from app.utils.dates import utc_now


logger = logging.getLogger(__name__)
settings = get_settings()


def seed_initial_sources(db: Session) -> None:
    repository = SourceRepository(db)
    repository.seed_sources(registry_seed_payloads())
    logger.info("Source seeding checked for %d registered feeds", len(SOURCE_CANDIDATES))


def _needs_validation(source) -> bool:
    if source.last_validated_at is None:
        return True
    return source.last_validated_at <= utc_now() - timedelta(hours=settings.health_check_interval_hours)


def verify_registered_sources(
    db: Session,
    *,
    manual_reenable: bool,
    force: bool,
) -> list[dict[str, Any]]:
    repository = SourceRepository(db)
    results: list[dict[str, Any]] = []

    for source in repository.list_all():
        if not force and not _needs_validation(source):
            results.append(
                {
                    "id": source.id,
                    "name": source.name,
                    "status": source.validation_status,
                    "is_enabled": bool(source.is_active),
                    "item_count": 0,
                    "response_time_ms": source.avg_response_time_ms,
                    "error": "",
                }
            )
            continue
        try:
            fetch_result = verify_feed(source)
            allow_enable = manual_reenable or source.last_validated_at is None
            if source.validation_status == "disabled" and not manual_reenable:
                allow_enable = False
            record_validation_result(
                db,
                source,
                is_valid=True,
                error=None,
                response_time_ms=fetch_result.response_time_ms,
                enable_on_success=allow_enable,
            )
            results.append(
                {
                    "id": source.id,
                    "name": source.name,
                    "status": "verified",
                    "is_enabled": bool(source.is_active if not allow_enable else True),
                    "item_count": len(fetch_result.entries),
                    "response_time_ms": fetch_result.response_time_ms,
                    "error": "",
                }
            )
        except Exception as exc:
            scraper_entries = []
            if settings.enable_scrapers and source.base_url:
                scraper_entries = scrape_source_entries(source.id, source.base_url)

            if scraper_entries:
                allow_enable = manual_reenable or source.last_validated_at is None
                if source.validation_status == "disabled" and not manual_reenable:
                    allow_enable = False
                record_validation_result(
                    db,
                    source,
                    is_valid=True,
                    error=None,
                    response_time_ms=None,
                    enable_on_success=allow_enable,
                )
                results.append(
                    {
                        "id": source.id,
                        "name": source.name,
                        "status": "verified",
                        "is_enabled": bool(source.is_active if not allow_enable else True),
                        "item_count": len(scraper_entries),
                        "response_time_ms": None,
                        "error": "",
                    }
                )
                continue

            record_validation_result(
                db,
                source,
                is_valid=False,
                error=str(exc),
                response_time_ms=None,
                enable_on_success=False,
            )
            results.append(
                {
                    "id": source.id,
                    "name": source.name,
                    "status": source.validation_status or "failed",
                    "is_enabled": bool(source.is_active),
                    "item_count": 0,
                    "response_time_ms": None,
                    "error": str(exc),
                }
            )
    return results

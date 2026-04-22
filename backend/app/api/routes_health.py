from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.source_repository import SourceRepository
from app.services.health_monitor import build_source_health_report
from app.schemas import HealthCheck


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthCheck)
def health_check(db: Session = Depends(get_db)) -> HealthCheck:
    database_ok = False
    active_sources = 0
    verified_sources = 0
    disabled_sources = 0
    stories_ingested_24h = 0
    try:
        db.execute(text("SELECT 1"))
        database_ok = True
        active_sources = SourceRepository(db).count_active()
        health_rows = build_source_health_report(db)
        verified_sources = sum(1 for row in health_rows if row["validation_status"] == "verified")
        disabled_sources = sum(1 for row in health_rows if not row["is_enabled"])
        stories_ingested_24h = sum(int(row["stories_ingested_24h"]) for row in health_rows)
    except Exception:
        database_ok = False

    checks = {
        "database": {"ok": database_ok},
        "feeds": {
            "ok": active_sources > 0,
            "active_sources": active_sources,
            "verified_sources": verified_sources,
            "disabled_sources": disabled_sources,
            "stories_ingested_24h": stories_ingested_24h,
        },
    }
    status = "ok" if database_ok else "degraded"
    return HealthCheck(status=status, timestamp=datetime.now(timezone.utc), checks=checks)

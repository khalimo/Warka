from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.source_repository import SourceRepository
from app.schemas import HealthCheck


router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthCheck)
def health_check(db: Session = Depends(get_db)) -> HealthCheck:
    database_ok = False
    active_sources = 0
    try:
        db.execute(text("SELECT 1"))
        database_ok = True
        active_sources = SourceRepository(db).count_active()
    except Exception:
        database_ok = False

    checks = {
        "database": {"ok": database_ok},
        "feeds": {"ok": active_sources > 0, "active_sources": active_sources},
    }
    status = "ok" if database_ok else "degraded"
    return HealthCheck(status=status, timestamp=datetime.now(timezone.utc), checks=checks)

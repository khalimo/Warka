from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session
from sqlalchemy import select

from app import models


class IngestRunRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_running(self) -> models.IngestRun:
        run = models.IngestRun(status="running", details_json={"sources": {}})
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def complete(self, run: models.IngestRun, *, completed_at: datetime, stats: dict[str, Any]) -> models.IngestRun:
        run.status = "completed"
        run.completed_at = completed_at
        run.processed_count = int(stats.get("processed_count", 0))
        run.inserted_count = int(stats.get("inserted_count", 0))
        run.updated_count = int(stats.get("updated_count", 0))
        run.skipped_count = int(stats.get("skipped_count", 0))
        run.error_count = int(stats.get("error_count", 0))
        run.details_json = stats.get("details_json", {})
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def fail(self, run: models.IngestRun, *, completed_at: datetime, stats: dict[str, Any]) -> models.IngestRun:
        self.db.rollback()
        run.status = "failed"
        run.completed_at = completed_at
        run.processed_count = int(stats.get("processed_count", 0))
        run.inserted_count = int(stats.get("inserted_count", 0))
        run.updated_count = int(stats.get("updated_count", 0))
        run.skipped_count = int(stats.get("skipped_count", 0))
        run.error_count = int(stats.get("error_count", 0))
        run.details_json = stats.get("details_json", {})
        self.db.add(run)
        self.db.commit()
        self.db.refresh(run)
        return run

    def latest(self) -> models.IngestRun | None:
        stmt = select(models.IngestRun).order_by(models.IngestRun.started_at.desc()).limit(1)
        return self.db.scalars(stmt).first()

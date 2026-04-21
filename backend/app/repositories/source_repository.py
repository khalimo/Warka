from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app import models


class SourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_active(self) -> list[models.Source]:
        stmt = select(models.Source).where(models.Source.is_active.is_(True)).order_by(models.Source.name.asc())
        return list(self.db.scalars(stmt))

    def count_active(self) -> int:
        stmt = select(func.count(models.Source.id)).where(models.Source.is_active.is_(True))
        return int(self.db.scalar(stmt) or 0)

    def get_by_id(self, source_id: str) -> models.Source | None:
        return self.db.get(models.Source, source_id)

    def seed_sources(self, seed_items: list[dict[str, str]]) -> None:
        existing_ids = set(self.db.scalars(select(models.Source.id)))
        for item in seed_items:
            if item["id"] in existing_ids:
                continue
            self.db.add(models.Source(**item))
        self.db.commit()

    def mark_success(self, source: models.Source, timestamp: datetime) -> None:
        source.last_success_at = timestamp
        source.last_error_at = None
        source.last_error_message = None
        self.db.add(source)
        self.db.commit()

    def mark_error(self, source: models.Source, timestamp: datetime, message: str) -> None:
        source.last_error_at = timestamp
        source.last_error_message = message
        self.db.add(source)
        self.db.commit()


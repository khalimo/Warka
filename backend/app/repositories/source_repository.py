from __future__ import annotations

from datetime import datetime
from typing import Optional, Sequence

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

    def get_by_id(self, source_id: str) -> Optional[models.Source]:
        return self.db.get(models.Source, source_id)

    def seed_sources(
        self,
        seed_items: list[dict[str, str]],
        deactivate_ids: Optional[Sequence[str]] = None,
    ) -> None:
        existing_sources = {
            source.id: source
            for source in self.db.scalars(select(models.Source))
        }
        for item in seed_items:
            existing = existing_sources.get(item["id"])
            if existing is None:
                self.db.add(models.Source(**item))
                continue

            for field, value in item.items():
                setattr(existing, field, value)
            self.db.add(existing)

        for source_id in deactivate_ids or []:
            existing = existing_sources.get(source_id)
            if existing is None:
                continue
            existing.is_active = False
            self.db.add(existing)
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

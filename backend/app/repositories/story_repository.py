from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app import models


class StoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_select(self):
        return select(models.Story).options(
            joinedload(models.Story.source),
            selectinload(models.Story.cluster),
        )

    def count_all(self) -> int:
        return int(self.db.scalar(select(func.count(models.Story.id))) or 0)

    def count_by_region(self, region: str) -> int:
        return int(
            self.db.scalar(select(func.count(models.Story.id)).where(models.Story.region == region)) or 0
        )

    def list_latest(self, limit: int, offset: int) -> list[models.Story]:
        stmt = self._base_select().order_by(models.Story.published_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).unique())

    def list_by_region(self, region: str, limit: int, offset: int) -> list[models.Story]:
        stmt = (
            self._base_select()
            .where(models.Story.region == region)
            .order_by(models.Story.published_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique())

    def get_by_slug(self, slug: str) -> Optional[models.Story]:
        stmt = self._base_select().where(models.Story.slug == slug)
        return self.db.scalars(stmt).unique().first()

    def hero_story(self) -> Optional[models.Story]:
        stmt = (
            self._base_select()
            .where(models.Story.category.in_(["politics", "security", "diplomacy"]))
            .order_by(models.Story.published_at.desc())
            .limit(1)
        )
        return self.db.scalars(stmt).unique().first()

    def secondary_stories(self, exclude_story_id, limit: int = 3) -> list[models.Story]:
        stmt = (
            self._base_select()
            .where(models.Story.id != exclude_story_id)
            .order_by(models.Story.published_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique())

    def latest_for_home(self, limit: int = 10) -> list[models.Story]:
        stmt = self._base_select().order_by(models.Story.published_at.desc()).limit(limit)
        return list(self.db.scalars(stmt).unique())

    def find_existing_by_url_hash(self, url_hash: str) -> Optional[models.Story]:
        stmt = select(models.Story).where(models.Story.canonical_url_hash == url_hash)
        return self.db.scalars(stmt).first()

    def add(self, story: models.Story) -> models.Story:
        self.db.add(story)
        self.db.commit()
        self.db.refresh(story)
        return story

    def recent_unclustered(self, cutoff: datetime) -> list[models.Story]:
        stmt = (
            select(models.Story)
            .options(joinedload(models.Story.source))
            .where(models.Story.published_at >= cutoff, or_(models.Story.cluster_id.is_(None), models.Story.cluster_id == ""))
            .order_by(models.Story.published_at.asc())
        )
        return list(self.db.scalars(stmt).unique())

    def recent_clustered(self, cutoff: datetime) -> list[models.Story]:
        stmt = (
            select(models.Story)
            .options(joinedload(models.Story.source), joinedload(models.Story.cluster))
            .where(models.Story.published_at >= cutoff, models.Story.cluster_id.is_not(None))
        )
        return list(self.db.scalars(stmt).unique())

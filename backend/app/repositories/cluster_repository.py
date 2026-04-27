from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session, selectinload

from app import models


class ClusterRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_select(self):
        return select(models.Cluster).options(
            selectinload(models.Cluster.stories).selectinload(models.Story.source)
        )

    def count_all(
        self,
        has_ai_synthesis: Optional[bool] = None,
        ai_review_status: Optional[str] = None,
        renderable_only: bool = False,
        category: Optional[str] = None,
        region: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> int:
        if renderable_only or category or region or source_id:
            stmt = select(models.Cluster.id)
            if renderable_only:
                stmt = stmt.where(models.Cluster.id.in_(self._renderable_ids_select()))
            if category or region or source_id:
                stmt = stmt.where(models.Cluster.id.in_(self._story_filtered_ids_select(category, region, source_id)))
            stmt = self._apply_cluster_filters(stmt, has_ai_synthesis, ai_review_status)
            return int(self.db.scalar(select(func.count()).select_from(stmt.subquery())) or 0)

        stmt = select(func.count(models.Cluster.id))
        stmt = self._apply_cluster_filters(stmt, has_ai_synthesis, ai_review_status)
        return int(self.db.scalar(stmt) or 0)

    def _apply_cluster_filters(
        self,
        stmt,
        has_ai_synthesis: Optional[bool] = None,
        ai_review_status: Optional[str] = None,
    ):
        if has_ai_synthesis is not None:
            stmt = stmt.where(models.Cluster.has_ai_synthesis.is_(has_ai_synthesis))
        if ai_review_status:
            if ai_review_status == "unreviewed":
                stmt = stmt.where(
                    (models.Cluster.ai_review_status.is_(None)) | (models.Cluster.ai_review_status == "unreviewed")
                )
            else:
                stmt = stmt.where(models.Cluster.ai_review_status == ai_review_status)
        return stmt

    def _story_filtered_ids_select(
        self,
        category: Optional[str] = None,
        region: Optional[str] = None,
        source_id: Optional[str] = None,
    ):
        stmt = select(models.Story.cluster_id).where(models.Story.cluster_id.is_not(None)).group_by(models.Story.cluster_id)
        if category:
            stmt = stmt.where(func.lower(models.Story.category) == category.lower())
        if region:
            stmt = stmt.where(func.lower(models.Story.region) == region.lower())
        if source_id:
            stmt = stmt.where(models.Story.source_id == source_id)
        return stmt

    def _renderable_ids_select(self):
        return (
            select(models.Cluster.id)
            .join(models.Cluster.stories)
            .where(func.length(func.trim(models.Cluster.title)) > 0)
            .group_by(models.Cluster.id)
            .having(
                (func.count(models.Story.id) >= 2)
                | (func.count(distinct(models.Story.source_id)) >= 2)
            )
        )

    def is_renderable(self, cluster_id: str) -> bool:
        stmt = select(models.Cluster.id).where(
            models.Cluster.id == cluster_id,
            models.Cluster.id.in_(self._renderable_ids_select()),
        )
        return self.db.scalar(stmt) is not None

    def list_paginated(
        self,
        limit: int,
        offset: int,
        has_ai_synthesis: Optional[bool] = None,
        ai_review_status: Optional[str] = None,
        renderable_only: bool = False,
        category: Optional[str] = None,
        region: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> list[models.Cluster]:
        stmt = self._base_select().order_by(models.Cluster.created_at.desc())
        stmt = self._apply_cluster_filters(stmt, has_ai_synthesis, ai_review_status)
        if renderable_only:
            stmt = stmt.where(models.Cluster.id.in_(self._renderable_ids_select()))
        if category or region or source_id:
            stmt = stmt.where(models.Cluster.id.in_(self._story_filtered_ids_select(category, region, source_id)))
        stmt = stmt.offset(offset).limit(limit)
        return list(self.db.scalars(stmt).unique())

    def latest_cluster(self) -> Optional[models.Cluster]:
        stmt = self._base_select().order_by(models.Cluster.created_at.desc()).limit(1)
        return self.db.scalars(stmt).unique().first()

    def list_recent_renderable(self, limit: int = 6) -> list[models.Cluster]:
        stmt = (
            self._base_select()
            .where(models.Cluster.id.in_(self._renderable_ids_select()))
            .order_by(models.Cluster.created_at.desc())
            .limit(limit)
        )
        return list(self.db.scalars(stmt).unique())

    def recent_clusters(self, cutoff: datetime) -> list[models.Cluster]:
        stmt = (
            self._base_select()
            .join(models.Cluster.stories)
            .where(models.Story.published_at >= cutoff)
            .order_by(models.Cluster.created_at.desc())
        )
        return list(self.db.scalars(stmt).unique())

    def get(self, cluster_id: str) -> Optional[models.Cluster]:
        stmt = self._base_select().where(models.Cluster.id == cluster_id)
        return self.db.scalars(stmt).unique().first()

    def list_recent_for_synthesis(
        self,
        cutoff: datetime,
        limit: int,
        include_completed: bool = False,
    ) -> list[models.Cluster]:
        stmt = (
            self._base_select()
            .join(models.Cluster.stories)
            .where(models.Story.published_at >= cutoff)
            .distinct()
            .order_by(models.Cluster.created_at.desc())
            .limit(limit)
        )
        if not include_completed:
            stmt = stmt.where(models.Cluster.ai_generated_at.is_(None))
        return list(self.db.scalars(stmt).unique())

    def save(self, cluster: models.Cluster) -> models.Cluster:
        self.db.add(cluster)
        self.db.commit()
        self.db.refresh(cluster)
        return cluster

    def add(self, cluster: models.Cluster) -> models.Cluster:
        self.db.add(cluster)
        self.db.flush()
        self.db.refresh(cluster)
        return cluster

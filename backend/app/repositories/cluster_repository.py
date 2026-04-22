from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app import models


class ClusterRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def _base_select(self):
        return select(models.Cluster).options(
            selectinload(models.Cluster.stories).selectinload(models.Story.source)
        )

    def count_all(self) -> int:
        return int(self.db.scalar(select(func.count(models.Cluster.id))) or 0)

    def list_paginated(self, limit: int, offset: int) -> list[models.Cluster]:
        stmt = self._base_select().order_by(models.Cluster.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).unique())

    def latest_cluster(self) -> Optional[models.Cluster]:
        stmt = self._base_select().order_by(models.Cluster.created_at.desc()).limit(1)
        return self.db.scalars(stmt).unique().first()

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

    def add(self, cluster: models.Cluster) -> models.Cluster:
        self.db.add(cluster)
        self.db.flush()
        self.db.refresh(cluster)
        return cluster

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, Uuid, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.database import Base


JsonType = JSON().with_variant(JSONB, "postgresql")


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    source_type: Mapped[str] = mapped_column(String, default="rss", server_default="rss")
    base_url: Mapped[Optional[str]] = mapped_column(String)
    feed_url: Mapped[Optional[str]] = mapped_column(String)
    category: Mapped[Optional[str]] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(Text)
    language: Mapped[str] = mapped_column(String, default="so", server_default="so")
    country: Mapped[str] = mapped_column(String, default="SO", server_default="SO")
    priority: Mapped[int] = mapped_column(Integer, default=100, server_default="100")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")
    validation_status: Mapped[str] = mapped_column(String, default="pending", server_default="pending")
    last_validated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_error_message: Mapped[Optional[str]] = mapped_column(Text)
    consecutive_failures: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    avg_response_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    stories: Mapped[list["Story"]] = relationship(back_populates="source")


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    common_facts: Mapped[Optional[str]] = mapped_column(Text)
    coverage_differences: Mapped[Optional[str]] = mapped_column(Text)
    neutral_summary: Mapped[Optional[str]] = mapped_column(Text)
    key_themes: Mapped[list[str]] = mapped_column(JsonType, default=list)
    consensus_level: Mapped[Optional[str]] = mapped_column(String)
    ai_neutral_summary: Mapped[Optional[str]] = mapped_column(Text)
    ai_coverage_differences: Mapped[Optional[str]] = mapped_column(Text)
    ai_consensus_level: Mapped[Optional[str]] = mapped_column(String)
    ai_key_themes: Mapped[Optional[str]] = mapped_column(Text)
    ai_generated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    ai_model_used: Mapped[Optional[str]] = mapped_column(String)
    has_ai_synthesis: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    ai_review_status: Mapped[Optional[str]] = mapped_column(String)
    ai_review_note: Mapped[Optional[str]] = mapped_column(Text)
    ai_reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    story_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    stories: Mapped[list["Story"]] = relationship(back_populates="cluster")


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    excerpt: Mapped[Optional[str]] = mapped_column(Text)
    content_html: Mapped[Optional[str]] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text)
    source_id: Mapped[str] = mapped_column(String, ForeignKey("sources.id"), nullable=False, index=True)
    original_url: Mapped[str] = mapped_column(String, nullable=False)
    canonical_url_hash: Mapped[str] = mapped_column(String, nullable=False, unique=True, index=True)
    published_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    region: Mapped[Optional[str]] = mapped_column(String, index=True)
    category: Mapped[Optional[str]] = mapped_column(String, index=True)
    topics: Mapped[list[str]] = mapped_column(JsonType, default=list)
    image_url: Mapped[Optional[str]] = mapped_column(String)
    reading_time: Mapped[Optional[int]] = mapped_column(Integer)
    is_breaking: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    cluster_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("clusters.id"), index=True)
    framing_label: Mapped[Optional[str]] = mapped_column(String)
    framing_description: Mapped[Optional[str]] = mapped_column(Text)
    framing_tone: Mapped[Optional[str]] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    source: Mapped[Source] = relationship(back_populates="stories")
    cluster: Mapped[Optional[Cluster]] = relationship(back_populates="stories")


class IngestRun(Base):
    __tablename__ = "ingest_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String, nullable=False, index=True)
    processed_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    inserted_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    updated_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    skipped_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    error_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    details_json: Mapped[dict[str, Any]] = mapped_column(JsonType, default=dict)

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class Source(BaseModel):
    id: str
    name: str
    base_url: str | None = None
    feed_url: str | None = None
    category: str | None = None
    description: str | None = None
    language: str = "so"
    country: str = "SO"
    is_active: bool = True
    last_success_at: datetime | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class Framing(BaseModel):
    id: str
    label: str
    description: str | None = None
    tone: str | None = None

    model_config = ConfigDict(from_attributes=True)


class Story(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    excerpt: str | None = None
    content_html: str | None = None
    summary: str | None = None
    source_id: str
    original_url: str
    canonical_url_hash: str
    published_at: datetime
    updated_at: datetime | None = None
    fetched_at: datetime
    region: str | None = None
    category: str | None = None
    topics: list[str] = Field(default_factory=list)
    image_url: str | None = None
    reading_time: int | None = None
    is_breaking: bool = False
    cluster_id: str | None = None
    source: Source
    framing: Framing | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Cluster(BaseModel):
    id: str
    title: str
    common_facts: str | None = None
    coverage_differences: str | None = None
    neutral_summary: str | None = None
    key_themes: list[str] = Field(default_factory=list)
    consensus_level: str | None = None
    story_count: int = 0
    created_at: datetime
    updated_at: datetime | None = None
    stories: list[Story] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class HomePageData(BaseModel):
    hero_story: Story
    secondary_stories: list[Story]
    compare_preview: Cluster
    latest_stories: list[Story]
    somalia_stories: list[Story]
    world_stories: list[Story]


T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    checks: dict[str, Any]


class IngestRun(BaseModel):
    id: uuid.UUID
    started_at: datetime
    completed_at: datetime | None = None
    status: str
    processed_count: int = 0
    inserted_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    details_json: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

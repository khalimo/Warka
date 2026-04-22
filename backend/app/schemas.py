from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class Source(BaseModel):
    id: str
    name: str
    base_url: Optional[str] = None
    feed_url: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    language: str = "so"
    country: str = "SO"
    is_active: bool = True
    last_success_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class Framing(BaseModel):
    id: str
    label: str
    description: Optional[str] = None
    tone: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class Story(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    excerpt: Optional[str] = None
    content_html: Optional[str] = None
    summary: Optional[str] = None
    source_id: str
    original_url: str
    canonical_url_hash: str
    published_at: datetime
    updated_at: Optional[datetime] = None
    fetched_at: datetime
    region: Optional[str] = None
    category: Optional[str] = None
    topics: list[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    reading_time: Optional[int] = None
    is_breaking: bool = False
    cluster_id: Optional[str] = None
    source: Source
    framing: Optional[Framing] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Cluster(BaseModel):
    id: str
    title: str
    common_facts: Optional[str] = None
    coverage_differences: Optional[str] = None
    neutral_summary: Optional[str] = None
    key_themes: list[str] = Field(default_factory=list)
    consensus_level: Optional[str] = None
    ai_neutral_summary: Optional[str] = None
    ai_coverage_differences: Optional[str] = None
    ai_consensus_level: Optional[str] = None
    ai_key_themes: list[str] = Field(default_factory=list)
    ai_generated_at: Optional[datetime] = None
    ai_model_used: Optional[str] = None
    has_ai_synthesis: bool = False
    story_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
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
    completed_at: Optional[datetime] = None
    status: str
    processed_count: int = 0
    inserted_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    details_json: dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

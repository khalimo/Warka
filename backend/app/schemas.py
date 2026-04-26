from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field
from pydantic import field_validator


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
    translations: dict[str, Any] = Field(default_factory=dict)
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
    ai_review_status: Optional[str] = None
    ai_review_note: Optional[str] = None
    ai_reviewed_at: Optional[datetime] = None
    story_count: int = 0
    created_at: datetime
    updated_at: Optional[datetime] = None
    stories: list[Story] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class HomePageData(BaseModel):
    hero_story: Story
    secondary_stories: list[Story]
    compare_preview: Optional[Cluster] = None
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


class AIReviewUpdateRequest(BaseModel):
    review_status: str
    review_note: Optional[str] = None

    @field_validator("review_status")
    @classmethod
    def validate_review_status(cls, value: str) -> str:
        normalized = (value or "").strip().lower()
        allowed = {"unreviewed", "good", "weak", "misleading", "hallucinated"}
        if normalized not in allowed:
            raise ValueError("Invalid review status")
        return normalized

    @field_validator("review_note", mode="before")
    @classmethod
    def normalize_review_note(cls, value: Any) -> Optional[str]:
        if value is None:
            return None
        cleaned = " ".join(str(value).split()).strip()
        if not cleaned:
            return None
        return cleaned[:500]


class AIReviewUpdateResponse(BaseModel):
    cluster_id: str
    ai_review_status: str
    ai_review_note: Optional[str] = None
    ai_reviewed_at: Optional[datetime] = None

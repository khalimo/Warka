from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str
    internal_api_key: str = ""
    openai_api_key: str = ""
    enable_openai: bool = False
    enable_ai_synthesis: bool = False
    enable_translations: bool = False
    ai_model: str = "gpt-4o-mini"
    translation_model: str = "gpt-4o-mini"
    ai_temperature: float = 0.3
    ai_max_tokens: int = 500
    translation_max_tokens: int = 1600
    source_validation_on_startup: bool = True
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    feed_timeout: int = 30
    verification_timeout: int = 15
    feed_limit_per_source: int = 20
    ingest_lookback_hours: int = 48
    enable_scrapers: bool = False
    scrape_respect_robots: bool = True
    scrape_rate_limit_seconds: int = 2
    scrape_max_articles_per_source: int = 8
    scrape_user_agent: str = "WarkaNewsBot/1.0 (+https://www.warkasta.com)"
    health_check_interval_hours: int = 24
    log_level: str = "INFO"
    cluster_similarity_threshold: float = 0.6

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if value is None or value == "":
            return ["http://localhost:3000"]
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return ["http://localhost:3000"]
            if raw.startswith("["):
                loaded = json.loads(raw)
                return [str(item).strip() for item in loaded if str(item).strip()]
            return [part.strip() for part in raw.split(",") if part.strip()]
        raise ValueError("Invalid CORS origins format")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

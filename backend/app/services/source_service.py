from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.repositories.source_repository import SourceRepository


logger = logging.getLogger(__name__)


SEED_SOURCES = [
    {
        "id": "bbc-somali",
        "name": "BBC Somali",
        "base_url": "https://www.bbc.com/somali",
        "feed_url": "https://feeds.bbci.co.uk/somali/rss.xml",
        "category": "international",
        "description": "Somali-language coverage from BBC Somali.",
        "language": "so",
        "country": "GB",
        "is_active": True,
    },
    {
        "id": "garowe-online",
        "name": "Garowe Online",
        "base_url": "https://garoweonline.com",
        "feed_url": "https://garoweonline.com/en/rss-feed",
        "category": "somali_regional",
        "description": "Regional Somali reporting from Garowe Online.",
        "language": "en",
        "country": "SO",
        "is_active": True,
    },
    {
        "id": "hiiraan-online",
        "name": "Hiiraan Online",
        "base_url": "https://www.hiiraan.com",
        "feed_url": "https://www.hiiraan.com/rss/news.xml",
        "category": "somali_national",
        "description": "Somali national news from Hiiraan Online.",
        "language": "en",
        "country": "SO",
        "is_active": True,
    },
    {
        "id": "horseed-media",
        "name": "Horseed Media",
        "base_url": "https://horseedmedia.net",
        "feed_url": "https://horseedmedia.net/feed",
        "category": "somali_national",
        "description": "Somali news and analysis from Horseed Media.",
        "language": "so",
        "country": "SO",
        "is_active": True,
    },
    {
        "id": "sonna",
        "name": "SONNA",
        "base_url": "https://sonna.so/en",
        "feed_url": "https://sonna.so/en/feed",
        "category": "official",
        "description": "Official Somali National News Agency feed.",
        "language": "en",
        "country": "SO",
        "is_active": True,
    },
]


def seed_initial_sources(db: Session) -> None:
    repository = SourceRepository(db)
    repository.seed_sources(SEED_SOURCES)
    logger.info("Source seeding checked for %d canonical feeds", len(SEED_SOURCES))


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
        "id": "hiiraan-online",
        "name": "Hiiraan Online",
        "base_url": "https://www.hiiraan.com",
        "feed_url": "https://www.hiiraan.com/news.xml",
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
        "id": "caasimada",
        "name": "Caasimada",
        "base_url": "https://www.caasimada.net",
        "feed_url": "https://www.caasimada.net/feed/",
        "category": "somali_national",
        "description": "Somali political and general news from Caasimada.",
        "language": "so",
        "country": "SO",
        "is_active": True,
    },
    {
        "id": "goobjoog",
        "name": "Goobjoog",
        "base_url": "https://goobjoog.com",
        "feed_url": "https://goobjoog.com/feed/",
        "category": "somali_national",
        "description": "Somali current affairs and national reporting from Goobjoog.",
        "language": "en",
        "country": "SO",
        "is_active": True,
    },
    {
        "id": "radio-muqdisho",
        "name": "Radio Muqdisho",
        "base_url": "https://radiomuqdisho.so",
        "feed_url": "https://radiomuqdisho.so/feed/",
        "category": "official",
        "description": "Public service Somali news coverage from Radio Muqdisho.",
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

DEACTIVATED_SOURCE_IDS = [
    "garowe-online",
]


def seed_initial_sources(db: Session) -> None:
    repository = SourceRepository(db)
    repository.seed_sources(SEED_SOURCES, deactivate_ids=DEACTIVATED_SOURCE_IDS)
    logger.info("Source seeding checked for %d canonical feeds", len(SEED_SOURCES))

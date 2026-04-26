from __future__ import annotations

import logging
from typing import Any

from app.config import get_settings
from app.services.scrapers.base import SourceScraper
from app.services.scrapers.universal import UniversalNewsScraper


logger = logging.getLogger(__name__)
settings = get_settings()

_UNIVERSAL = UniversalNewsScraper()

SCRAPER_ADAPTERS: dict[str, SourceScraper] = {
    "allafrica-somalia": _UNIVERSAL,
    "bbc-somali": _UNIVERSAL,
    "berbera-news": _UNIVERSAL,
    "caasimada": _UNIVERSAL,
    "garowe-online": _UNIVERSAL,
    "goobjoog": _UNIVERSAL,
    "goobjoog-en": _UNIVERSAL,
    "guardian-somalia": _UNIVERSAL,
    "hiiraan-online": _UNIVERSAL,
    "hiiraanweyn": _UNIVERSAL,
    "horseed-media": _UNIVERSAL,
    "icrc-somalia": _UNIVERSAL,
    "jowhar": _UNIVERSAL,
    "nyt-somalia": _UNIVERSAL,
    "oodweyne-media": _UNIVERSAL,
    "puntland-post": _UNIVERSAL,
    "puntland-mirror": _UNIVERSAL,
    "radio-ergo": _UNIVERSAL,
    "radio-dalsan": _UNIVERSAL,
    "radio-muqdisho": _UNIVERSAL,
    "raxanreeb": _UNIVERSAL,
    "reliefweb-somalia": _UNIVERSAL,
    "saxafi-media": _UNIVERSAL,
    "shabelle-media": _UNIVERSAL,
    "sntv": _UNIVERSAL,
    "somali-digest": _UNIVERSAL,
    "somali-dispatch": _UNIVERSAL,
    "somali-guardian": _UNIVERSAL,
    "somalia-investor": _UNIVERSAL,
    "sonna": _UNIVERSAL,
    "unfpa-somalia": _UNIVERSAL,
    "voa-somali": _UNIVERSAL,
    "wardheer-news": _UNIVERSAL,
    "wargeyska-dawan": _UNIVERSAL,
}


def scrape_source_entries(source_id: str, base_url: str) -> list[dict[str, Any]]:
    """Return public article entries from an approved source scraper.

    Scraping stays disabled unless ENABLE_SCRAPERS=true. RSS/API ingestion remains
    the first choice; these adapters only supplement or recover public articles
    where a source is explicitly approved.
    """

    if not settings.enable_scrapers:
        return []

    scraper = SCRAPER_ADAPTERS.get(source_id)
    if scraper is None:
        logger.info("No scraper configured for source_id=%s; returning no entries", source_id)
        return []

    try:
        result = scraper.scrape(base_url, limit=settings.scrape_max_articles_per_source)
    except Exception as exc:
        logger.warning("Scraper failed for source_id=%s: %s", source_id, exc)
        return []
    if result.errors:
        logger.info("Scraper completed for source_id=%s with %d warning(s)", source_id, len(result.errors))
    return result.entries

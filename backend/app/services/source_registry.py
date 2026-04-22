from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Optional


@dataclass(frozen=True)
class SourceCandidate:
    id: str
    name: str
    source_type: str
    base_url: str
    feed_url: str
    language: str
    category: str
    priority: int
    is_enabled: bool = False
    validation_status: str = "pending"
    last_validated_at: Optional[str] = None
    last_error: Optional[str] = None
    consecutive_failures: int = 0
    notes: str = ""
    country: str = "SO"
    description: str = ""

    def to_seed_payload(self) -> dict[str, object]:
        payload = asdict(self)
        payload["is_active"] = payload.pop("is_enabled")
        payload["last_error_message"] = payload.pop("last_error")
        payload.pop("last_validated_at")
        payload.pop("consecutive_failures")
        return payload


SOURCE_CANDIDATES = [
    SourceCandidate(
        id="bbc-somali",
        name="BBC Somali",
        source_type="rss",
        base_url="https://www.bbc.com/somali",
        feed_url="https://feeds.bbci.co.uk/somali/rss.xml",
        language="so",
        category="international",
        priority=10,
        description="Somali-language coverage from BBC Somali.",
        country="GB",
        notes="Reliable international Somali-language source.",
    ),
    SourceCandidate(
        id="horseed-media",
        name="Horseed Media",
        source_type="rss",
        base_url="https://horseedmedia.net",
        feed_url="https://horseedmedia.net/feed",
        language="so",
        category="somali_national",
        priority=20,
        description="Somali news and analysis from Horseed Media.",
        notes="Currently a stable feed.",
    ),
    SourceCandidate(
        id="sonna",
        name="SONNA",
        source_type="rss",
        base_url="https://sonna.so/en",
        feed_url="https://sonna.so/en/feed",
        language="en",
        category="official",
        priority=30,
        description="Official Somali National News Agency feed.",
        notes="Official government-aligned source.",
    ),
    SourceCandidate(
        id="caasimada",
        name="Caasimada Online",
        source_type="rss",
        base_url="https://www.caasimada.net",
        feed_url="https://www.caasimada.net/feed/",
        language="so",
        category="somali_national",
        priority=40,
        description="Somali political and general news from Caasimada.",
        notes="Good national politics coverage.",
    ),
    SourceCandidate(
        id="goobjoog",
        name="Goobjoog News",
        source_type="rss",
        base_url="https://goobjoog.com",
        feed_url="https://goobjoog.com/feed/",
        language="en",
        category="somali_national",
        priority=50,
        description="Somali current affairs and national reporting from Goobjoog.",
        notes="General national reporting.",
    ),
    SourceCandidate(
        id="radio-muqdisho",
        name="Radio Muqdisho",
        source_type="rss",
        base_url="https://radiomuqdisho.so",
        feed_url="https://radiomuqdisho.so/feed/",
        language="so",
        category="official",
        priority=60,
        description="Public service Somali news coverage from Radio Muqdisho.",
        notes="Strong official reporting, often includes images.",
    ),
    SourceCandidate(
        id="hiiraan-online",
        name="Hiiraan Online",
        source_type="rss",
        base_url="https://www.hiiraan.com",
        feed_url="https://www.hiiraan.com/news.xml",
        language="en",
        category="somali_national",
        priority=70,
        description="Somali national news from Hiiraan Online.",
        notes="Legacy feed path was broken; news.xml currently works.",
    ),
    SourceCandidate(
        id="garowe-online",
        name="Garowe Online",
        source_type="rss",
        base_url="https://garoweonline.com",
        feed_url="https://garoweonline.com/en/rss-feed",
        language="en",
        category="somali_regional",
        priority=80,
        description="Regional Somali reporting from Garowe Online.",
        notes="Candidate only until feed is consistently verified.",
    ),
    SourceCandidate(
        id="puntland-post",
        name="Puntland Post",
        source_type="rss",
        base_url="https://puntlandpost.net",
        feed_url="https://puntlandpost.net/feed",
        language="en",
        category="somali_regional",
        priority=90,
        description="Regional reporting focused on Puntland and Somali politics.",
        notes="Candidate feed for verification.",
    ),
    SourceCandidate(
        id="somali-guardian",
        name="Somali Guardian",
        source_type="rss",
        base_url="https://somaliguardian.com",
        feed_url="https://somaliguardian.com/feed/",
        language="en",
        category="somali_national",
        priority=100,
        description="Somali Guardian politics and breaking developments.",
        notes="Candidate feed for verification.",
    ),
    SourceCandidate(
        id="radio-dalsan",
        name="Radio Dalsan",
        source_type="rss",
        base_url="https://radiodalsan.com",
        feed_url="https://radiodalsan.com/feed/",
        language="so",
        category="somali_national",
        priority=110,
        description="Somali radio and web reporting from Radio Dalsan.",
        notes="Candidate feed; reject if the server continues returning 406.",
    ),
    SourceCandidate(
        id="shabelle-media",
        name="Shabelle Media",
        source_type="rss",
        base_url="https://shabellemedia.com",
        feed_url="https://shabellemedia.com/feed/",
        language="en",
        category="somali_national",
        priority=120,
        description="Somali news and regional reporting from Shabelle Media.",
        notes="Candidate feed for verification.",
    ),
]


def registry_seed_payloads() -> list[dict[str, object]]:
    return [candidate.to_seed_payload() for candidate in SOURCE_CANDIDATES]


def registry_source_ids() -> set[str]:
    return {candidate.id for candidate in SOURCE_CANDIDATES}

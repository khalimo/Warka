from __future__ import annotations

from app.utils.slug import build_story_slug
from app.utils.text import top_terms


REGION_KEYWORDS = {
    "somalia",
    "mogadishu",
    "puntland",
    "somaliland",
    "jubaland",
    "galmudug",
    "hirshabelle",
    "kismayo",
    "baidoa",
}

CATEGORY_RULES: list[tuple[str, tuple[str, ...]]] = [
    ("politics", ("president", "parliament", "election", "minister", "government", "political")),
    ("security", ("security", "military", "attack", "al-shabaab", "fighting", "army", "police")),
    ("diplomacy", ("diplomat", "ambassador", "united nations", "au", "igad", "summit")),
    ("economy", ("economy", "business", "trade", "investment", "bank", "dollar")),
    ("humanitarian", ("aid", "drought", "flood", "refugee", "humanitarian", "relief")),
    ("health", ("health", "hospital", "disease", "covid", "clinic", "medical")),
    ("education", ("school", "university", "education", "student", "teacher")),
]


def normalize_region(*, source_category: str | None, title: str, summary: str) -> str:
    haystack = f"{title} {summary}".lower()
    if any(keyword in haystack for keyword in REGION_KEYWORDS):
        return "somalia"
    if source_category in {"somali_national", "somali_regional"}:
        return "somalia"
    if source_category == "official":
        return "somalia"
    return "world"


def normalize_category(*, title: str, summary: str) -> str:
    haystack = f"{title} {summary}".lower()
    for category, keywords in CATEGORY_RULES:
        if any(keyword in haystack for keyword in keywords):
            return category
    return "general"


def derive_topics(*, title: str, summary: str, category: str) -> list[str]:
    seeds = top_terms([title, summary], limit=3)
    if category != "general" and category not in seeds:
        seeds.insert(0, category)
    return seeds[:3]


def make_story_slug(*, title: str, published_at):
    return build_story_slug(title, published_at)


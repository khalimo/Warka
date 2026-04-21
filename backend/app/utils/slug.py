from __future__ import annotations

import hashlib
import re
from datetime import datetime


def slugify(value: str) -> str:
    lowered = re.sub(r"[^a-z0-9\s-]", "", value.lower())
    compact = re.sub(r"[\s_-]+", "-", lowered).strip("-")
    return compact[:50].strip("-") or "story"


def build_story_slug(title: str, published_at: datetime | None) -> str:
    base = slugify(title)
    date_value = published_at.isoformat() if published_at else "undated"
    suffix = hashlib.sha1(date_value.encode("utf-8")).hexdigest()[:8]
    return f"{base}-{suffix}"


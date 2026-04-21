from __future__ import annotations

import bleach


ALLOWED_TAGS = ["p", "a", "strong", "em", "br", "ul", "ol", "li"]
ALLOWED_ATTRIBUTES = {"a": ["href", "title", "rel", "target"]}


def sanitize_html(value: str) -> str:
    return bleach.clean(
        value or "",
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=["http", "https"],
        strip=True,
    )


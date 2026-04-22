from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from dateutil import parser as date_parser


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def parse_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    if isinstance(value, datetime):
        return ensure_utc(value)
    try:
        parsed = date_parser.parse(str(value))
    except (ValueError, TypeError, OverflowError):
        return None
    return ensure_utc(parsed)

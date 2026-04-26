from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Deque

from fastapi import HTTPException, Request, status

from app.config import get_settings


_REQUEST_WINDOWS: dict[str, Deque[float]] = defaultdict(deque)


def require_internal_rate_limit(request: Request) -> None:
    limit = max(1, get_settings().internal_rate_limit_per_minute)
    now = time.monotonic()
    window_start = now - 60
    client = request.client.host if request.client else "unknown"
    key = f"{client}:{request.url.path}"
    timestamps = _REQUEST_WINDOWS[key]

    while timestamps and timestamps[0] < window_start:
        timestamps.popleft()

    if len(timestamps) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many internal requests; try again soon",
        )

    timestamps.append(now)


def clear_rate_limit_state() -> None:
    _REQUEST_WINDOWS.clear()

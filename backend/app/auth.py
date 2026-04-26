from __future__ import annotations

import hmac
from typing import Optional

from fastapi import Header, HTTPException, status

from app.config import get_settings


def require_internal_api_key(
    x_internal_api_key: Optional[str] = Header(default=None),
) -> None:
    settings = get_settings()
    expected = settings.internal_api_key

    if not expected:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Internal API key is not configured",
        )

    if not x_internal_api_key or not hmac.compare_digest(x_internal_api_key, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid internal API key",
        )

from __future__ import annotations

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import require_internal_api_key
from app.config import get_settings


def _client() -> TestClient:
    app = FastAPI()

    @app.get("/protected", dependencies=[Depends(require_internal_api_key)])
    def protected() -> dict[str, str]:
        return {"status": "ok"}

    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_settings_cache() -> None:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_protected_route_without_key_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("INTERNAL_API_KEY", "correct-secret")

    response = _client().get("/protected")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid internal API key"


def test_protected_route_with_wrong_key_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("INTERNAL_API_KEY", "correct-secret")

    response = _client().get("/protected", headers={"X-Internal-API-Key": "wrong"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid internal API key"


def test_protected_route_with_correct_key_reaches_endpoint(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("INTERNAL_API_KEY", "correct-secret")

    response = _client().get("/protected", headers={"X-Internal-API-Key": "correct-secret"})

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_protected_route_without_configured_key_returns_503(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.delenv("INTERNAL_API_KEY", raising=False)

    response = _client().get("/protected", headers={"X-Internal-API-Key": "anything"})

    assert response.status_code == 503
    assert response.json()["detail"] == "Internal API key is not configured"


def test_ingest_route_without_key_returns_401(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite:///test.db")
    monkeypatch.setenv("INTERNAL_API_KEY", "correct-secret")

    from app.api.routes_ingest import router

    app = FastAPI()
    app.include_router(router)

    response = TestClient(app).post("/api/ingest")

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid internal API key"

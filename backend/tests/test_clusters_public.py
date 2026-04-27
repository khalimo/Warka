from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import models
from app.api import routes_clusters, routes_home
from app.database import Base, get_db


@pytest.fixture()
def db_session() -> Iterator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        _seed_cluster_data(session)
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session: Session) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(routes_home.router)
    app.include_router(routes_clusters.router)

    def override_get_db() -> Iterator[Session]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


def _source(source_id: str, name: str) -> models.Source:
    return models.Source(
        id=source_id,
        name=name,
        base_url=f"https://{source_id}.example.com",
        feed_url=f"https://{source_id}.example.com/rss",
        category="news",
        description=f"{name} feed",
        language="so",
        country="SO",
        is_active=True,
    )


def _story(
    slug: str,
    source: models.Source,
    published_at: datetime,
    cluster: models.Cluster | None = None,
    category: str = "politics",
) -> models.Story:
    return models.Story(
        slug=slug,
        title=f"Story {slug}",
        excerpt=f"Excerpt {slug}",
        summary=f"Summary {slug}",
        source=source,
        original_url=f"https://{source.id}.example.com/{slug}",
        canonical_url_hash=f"hash-{slug}",
        published_at=published_at,
        fetched_at=published_at,
        region="somalia",
        category=category,
        topics=["somalia"],
        translations={},
        is_breaking=False,
        cluster=cluster,
        created_at=published_at,
    )


def _cluster(cluster_id: str, title: str, created_at: datetime) -> models.Cluster:
    return models.Cluster(
        id=cluster_id,
        title=title,
        common_facts="Shared fact",
        coverage_differences="Different emphasis",
        neutral_summary="Neutral summary",
        key_themes=["politics"],
        consensus_level="medium",
        story_count=0,
        confidence_score=80,
        event_signature={},
        created_at=created_at,
    )


def _seed_cluster_data(session: Session) -> None:
    now = datetime.now(timezone.utc)
    source_a = _source("source-a", "Source A")
    source_b = _source("source-b", "Source B")
    source_c = _source("source-c", "Source C")

    renderable = _cluster("renderable", "Renderable cluster", now - timedelta(hours=2))
    older_renderable = _cluster("older-renderable", "Older renderable cluster", now - timedelta(hours=3))
    newest_not_renderable = _cluster("newest-not-renderable", "Newest single story", now - timedelta(hours=1))
    empty_not_renderable = _cluster("empty-not-renderable", "Empty cluster", now)

    stories = [
        _story("hero", source_a, now - timedelta(minutes=20), renderable),
        _story("related", source_b, now - timedelta(minutes=30), renderable),
        _story("older-a", source_a, now - timedelta(hours=4), older_renderable),
        _story("older-b", source_c, now - timedelta(hours=5), older_renderable, category="economy"),
        _story("single", source_a, now - timedelta(minutes=10), newest_not_renderable),
    ]

    renderable.story_count = 2
    older_renderable.story_count = 2
    newest_not_renderable.story_count = 1

    session.add_all(
        [
            source_a,
            source_b,
            source_c,
            renderable,
            older_renderable,
            newest_not_renderable,
            empty_not_renderable,
            *stories,
        ]
    )
    session.commit()


def test_home_returns_renderable_compare_clusters(client: TestClient) -> None:
    response = client.get("/api/home")

    assert response.status_code == 200
    body = response.json()
    assert body["compare_preview"]["id"] == "renderable"
    assert body["diagnostics"]["story_count"] == 5
    assert body["diagnostics"]["active_source_count"] == 3
    assert body["diagnostics"]["total_cluster_count"] == 4
    assert body["diagnostics"]["renderable_cluster_count"] == 2
    assert [cluster["id"] for cluster in body["compare_clusters"]] == [
        "renderable",
        "older-renderable",
    ]


def test_clusters_renderable_only_filters_empty_and_single_story_clusters(client: TestClient) -> None:
    response = client.get("/api/clusters?limit=10&offset=0&renderable_only=true")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [cluster["id"] for cluster in body["items"]] == [
        "renderable",
        "older-renderable",
    ]


def test_clusters_can_return_all_clusters_for_internal_tooling(client: TestClient) -> None:
    response = client.get("/api/clusters?limit=10&offset=0&renderable_only=false")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 4
    assert {cluster["id"] for cluster in body["items"]} == {
        "empty-not-renderable",
        "newest-not-renderable",
        "renderable",
        "older-renderable",
    }


def test_clusters_can_filter_by_category(client: TestClient) -> None:
    response = client.get("/api/clusters?limit=10&offset=0&renderable_only=true&category=politics")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert [cluster["id"] for cluster in body["items"]] == [
        "renderable",
        "older-renderable",
    ]


def test_clusters_unknown_filter_is_ignored(client: TestClient) -> None:
    response = client.get("/api/clusters?limit=10&offset=0&renderable_only=true&category=unknown")

    assert response.status_code == 200
    assert response.json()["total"] == 2


def test_clusters_filter_uses_any_matching_story_after_renderability(client: TestClient) -> None:
    response = client.get("/api/clusters?limit=10&offset=0&renderable_only=true&category=economy")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["id"] == "older-renderable"


def test_get_cluster_returns_renderable_cluster(client: TestClient) -> None:
    response = client.get("/api/clusters/renderable")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "renderable"
    assert len(body["stories"]) == 2
    assert len(body["sources"]) == 2


def test_get_cluster_hides_non_renderable_cluster_by_default(client: TestClient) -> None:
    response = client.get("/api/clusters/newest-not-renderable")

    assert response.status_code == 404


def test_get_cluster_can_return_non_renderable_for_future_internal_tooling(client: TestClient) -> None:
    response = client.get("/api/clusters/newest-not-renderable?renderable_only=false")

    assert response.status_code == 200
    assert response.json()["id"] == "newest-not-renderable"

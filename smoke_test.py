import os
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite:///smoke_test.db")
os.environ.setdefault("OPENAI_ENABLED", "false")

import app
from sources import NEWS_SOURCES


def main() -> None:
    ready, label = app.database_ready()
    assert ready, label

    article = {
        "article_hash": app.hash_article("Smoke story", "https://example.com/smoke", "Smoke Source"),
        "title": "Smoke story",
        "summary": "Security reform and rights discussion.",
        "content": "",
        "source": "Smoke Source",
        "source_url": "https://example.com/smoke",
        "region": "test",
        "section": "Somalia",
        "source_category": "Smoke",
        "language": "en",
        "published_at": None,
        "fetched_at": app.utc_now(),
        "bias": "center",
        "bias_confidence": 0.5,
    }

    first = app.insert_articles([article])
    second = app.insert_articles([article])
    assert first in (0, 1)
    assert second == 0

    df = app.load_recent_stories(1)
    assert not df.empty

    clustered = app.assign_clusters(df)
    assert "cluster_label" in clustered.columns
    assert "section" in df.columns
    assert app.story_section(df.iloc[0])
    assert app.story_excerpt(df.iloc[0])

    rollup = app.load_source_rollup(1)
    assert "story_count" in rollup.columns

    bias, confidence, mode = app.classify_bias_with_ai("A neutral smoke-test story.")
    assert bias in {"left", "center-left", "center", "center-right", "right"}
    assert 0 <= confidence <= 1
    assert mode == "fallback"

    username = f"smoke_{uuid4().hex[:10]}"
    ok, msg = app.register_user(username, "pass1234", f"{username}@example.com")
    assert ok, msg
    ok, _ = app.login_user(username, "pass1234")
    assert ok

    assert len(NEWS_SOURCES) >= 12
    assert any(source["section"] == "Somalia" for source in NEWS_SOURCES)

    print("Smoke test passed")


if __name__ == "__main__":
    main()

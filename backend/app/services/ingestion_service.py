from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas
from app.repositories.ingest_run_repository import IngestRunRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.story_repository import StoryRepository
from app.services.clustering_service import run_clustering
from app.services.enrichment_service import enrich_story_content, get_category_image
from app.services.feed_service import FeedFetchError, fetch_feed
from app.services.health_monitor import build_source_health_report, record_source_failure, record_source_success
from app.services.normalization_service import derive_topics, make_story_slug, normalize_category, normalize_region
from app.services.scraper_service import scrape_source_entries
from app.services.sanitization_service import sanitize_html
from app.utils.dates import parse_datetime, utc_now
from app.utils.text import canonical_url_hash, estimate_reading_time, strip_html


logger = logging.getLogger(__name__)


def _entry_value(entry: dict[str, Any], key: str) -> str:
    value = entry.get(key)
    if isinstance(value, str):
        return value
    return str(value or "")


def _entry_content(entry: dict[str, Any]) -> str:
    content = entry.get("content") or []
    if isinstance(content, list) and content:
        first = content[0]
        if isinstance(first, dict):
            return str(first.get("value") or "")
    return _entry_value(entry, "summary") or _entry_value(entry, "description")


def _entry_image(entry: dict[str, Any]) -> Optional[str]:
    media_thumbnail = entry.get("media_thumbnail") or []
    if isinstance(media_thumbnail, list):
        for item in media_thumbnail:
            if isinstance(item, dict) and item.get("url"):
                return str(item["url"])
    media_content = entry.get("media_content") or []
    if isinstance(media_content, list):
        for item in media_content:
            if isinstance(item, dict) and item.get("url"):
                return str(item["url"])
    return None


def run_ingestion(db: Session) -> models.IngestRun:
    logger.info("Starting ingestion run")
    source_repo = SourceRepository(db)
    story_repo = StoryRepository(db)
    run_repo = IngestRunRepository(db)

    run = run_repo.create_running()
    details: dict[str, Any] = {"sources": {}}
    stats = {
        "processed_count": 0,
        "inserted_count": 0,
        "updated_count": 0,
        "skipped_count": 0,
        "error_count": 0,
        "details_json": details,
    }

    try:
        for source in source_repo.list_active():
            source_log = {
                "feed_url": source.feed_url,
                "processed": 0,
                "inserted": 0,
                "updated": 0,
                "skipped": 0,
                "errors": [],
            }
            details["sources"][source.id] = source_log
            try:
                fetch_result = fetch_feed(source)
                entries = fetch_result.entries
                source_log["response_time_ms"] = fetch_result.response_time_ms
                record_source_success(db, source, response_time_ms=fetch_result.response_time_ms)
            except Exception as exc:
                logger.warning("Feed failed for %s: %s", source.name, exc)
                entries = []
                if source.base_url:
                    entries = scrape_source_entries(source.id, source.base_url)
                if not entries:
                    stats["error_count"] += 1
                    source_log["errors"].append(str(exc))
                    record_source_failure(db, source, error=str(exc))
                    source_log["status"] = "failed"
                    continue
                source_log["status"] = "scraped"

            for entry in entries:
                source_log["processed"] += 1
                stats["processed_count"] += 1

                link = _entry_value(entry, "link").strip()
                title = _entry_value(entry, "title").strip()
                if not link or not title:
                    stats["skipped_count"] += 1
                    source_log["skipped"] += 1
                    continue

                url_hash = canonical_url_hash(link)
                if story_repo.find_existing_by_url_hash(url_hash):
                    stats["skipped_count"] += 1
                    source_log["skipped"] += 1
                    continue

                published_at = (
                    parse_datetime(entry.get("published"))
                    or parse_datetime(entry.get("updated"))
                    or utc_now()
                )
                raw_summary = _entry_value(entry, "summary") or _entry_value(entry, "description")
                raw_content = _entry_content(entry)
                sanitized_content = sanitize_html(raw_content)
                excerpt = strip_html(raw_summary or raw_content)[:400] or title
                category = normalize_category(title=title, summary=excerpt)
                region = normalize_region(source_category=source.category, title=title, summary=excerpt)
                topics = derive_topics(title=title, summary=excerpt, category=category)

                initial_summary = strip_html(raw_summary)[:600] if raw_summary else excerpt
                enrichment = enrich_story_content(
                    url=link,
                    title=title,
                    excerpt=excerpt,
                    current_content_html=sanitized_content,
                    current_summary=initial_summary,
                    current_image_url=_entry_image(entry),
                    category=category,
                )

                db_story = models.Story(
                    slug=make_story_slug(title=title, published_at=published_at),
                    title=title,
                    excerpt=excerpt,
                    content_html=enrichment["content_html"],
                    summary=enrichment["summary"],
                    source_id=source.id,
                    original_url=link,
                    canonical_url_hash=url_hash,
                    published_at=published_at,
                    updated_at=parse_datetime(entry.get("updated")),
                    region=region,
                    category=category,
                    topics=topics,
                    image_url=enrichment["image_url"] or get_category_image(category),
                    reading_time=estimate_reading_time(enrichment["content_html"] or excerpt),
                    is_breaking=category in {"security", "politics"} and "breaking" in title.lower(),
                )
                try:
                    story_repo.add(db_story)
                    stats["inserted_count"] += 1
                    source_log["inserted"] += 1
                except IntegrityError:
                    db.rollback()
                    stats["skipped_count"] += 1
                    source_log["skipped"] += 1
                except Exception as exc:
                    db.rollback()
                    logger.warning("Failed to store story for %s: %s", source.name, exc)
                    stats["error_count"] += 1
                    source_log["errors"].append(str(exc))

        cluster_stats = run_clustering(db)
        details["clustering"] = cluster_stats
        details["source_health"] = build_source_health_report(db)
        logger.info("Ingestion run complete")
        return run_repo.complete(run, completed_at=utc_now(), stats=stats)
    except Exception as exc:
        logger.exception("Ingestion run failed")
        stats["error_count"] += 1
        details.setdefault("fatal_error", str(exc))
        db.rollback()
        return run_repo.fail(run, completed_at=utc_now(), stats=stats)

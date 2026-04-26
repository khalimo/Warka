from __future__ import annotations

import argparse

from sqlalchemy import select

from app import models
from app.database import SessionLocal
from app.logging_config import configure_logging
from app.config import get_settings
from app.services.translation_service import target_language_for, translate_story_fields


def _has_translation(story: models.Story, target_language: str) -> bool:
    translations = story.translations or {}
    return bool(
        translations.get("headline", {}).get(target_language)
        and translations.get("excerpt", {}).get(target_language)
        and translations.get("content", {}).get(target_language)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill story translations in batches.")
    parser.add_argument("--limit", type=int, default=25)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    configure_logging(settings.log_level)

    db = SessionLocal()
    updated = 0
    skipped = 0
    try:
        stmt = (
            select(models.Story)
            .join(models.Story.source)
            .order_by(models.Story.published_at.desc())
            .limit(max(1, args.limit))
        )
        for story in db.scalars(stmt):
            target_language = target_language_for(story.source.language)
            if target_language is None:
                skipped += 1
                continue
            if not args.force and _has_translation(story, target_language):
                skipped += 1
                continue

            translations = translate_story_fields(
                source_language=story.source.language,
                title=story.title,
                excerpt=story.excerpt or "",
                summary=story.summary or "",
                content_html=story.content_html or "",
            )
            if not translations:
                skipped += 1
                continue

            story.translations = {**(story.translations or {}), **translations}
            db.add(story)
            db.commit()
            updated += 1
    finally:
        db.close()

    print({"updated": updated, "skipped": skipped, "limit": args.limit})


if __name__ == "__main__":
    main()

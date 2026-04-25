from __future__ import annotations

from app.database import SessionLocal
from app.services.health_monitor import build_source_health_report


def main() -> None:
    db = SessionLocal()
    try:
        rows = build_source_health_report(db)
    finally:
        db.close()

    headers = [
        "source",
        "enabled",
        "status",
        "score",
        "category",
        "stories_24h",
        "avg_ms",
        "failures",
        "last_error",
    ]
    values = [
        [
            row["name"],
            "yes" if row["is_enabled"] else "no",
            str(row["validation_status"] or ""),
            str(row["health_score"]),
            str(row["category"] or ""),
            str(row["stories_ingested_24h"]),
            str(row["avg_response_time_ms"] or "-"),
            str(row["consecutive_failures"]),
            str(row["last_error"] or ""),
        ]
        for row in rows
    ]

    widths = [
        max(len(header), *(len(row[index]) for row in values)) if values else len(header)
        for index, header in enumerate(headers)
    ]

    def render(parts: list[str]) -> str:
        return " | ".join(part.ljust(width) for part, width in zip(parts, widths))

    print(render(headers))
    print("-+-".join("-" * width for width in widths))
    for row in values:
        print(render(row))


if __name__ == "__main__":
    main()

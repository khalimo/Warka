from __future__ import annotations

from app.database import SessionLocal
from app.services.source_service import seed_initial_sources, verify_registered_sources


def _format_row(values: list[str], widths: list[int]) -> str:
    return " | ".join(value.ljust(width) for value, width in zip(values, widths))


def main() -> None:
    db = SessionLocal()
    try:
        seed_initial_sources(db)
        results = verify_registered_sources(db, manual_reenable=True, force=True)
    finally:
        db.close()

    headers = ["source", "status", "enabled", "items", "response_ms", "error"]
    rows = [
        [
            result["name"],
            result["status"],
            "yes" if result["is_enabled"] else "no",
            str(result["item_count"]),
            str(result["response_time_ms"] or "-"),
            result["error"] or "",
        ]
        for result in results
    ]
    widths = [
        max(len(header), *(len(row[index]) for row in rows)) if rows else len(header)
        for index, header in enumerate(headers)
    ]

    print(_format_row(headers, widths))
    print("-+-".join("-" * width for width in widths))
    for row in rows:
        print(_format_row(row, widths))


if __name__ == "__main__":
    main()

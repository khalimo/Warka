from __future__ import annotations

from app.database import SessionLocal
from app.logging_config import configure_logging
from app.services.ingestion_service import run_ingestion
from app.config import get_settings


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    db = SessionLocal()
    try:
        run = run_ingestion(db)
        print(f"Ingestion completed with status={run.status} id={run.id}")
    finally:
        db.close()


if __name__ == "__main__":
    main()


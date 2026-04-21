from __future__ import annotations

from app.config import get_settings
from app.database import SessionLocal
from app.logging_config import configure_logging
from app.services.clustering_service import run_clustering


def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    db = SessionLocal()
    try:
        stats = run_clustering(db)
        print(stats)
    finally:
        db.close()


if __name__ == "__main__":
    main()

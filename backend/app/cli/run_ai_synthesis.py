from __future__ import annotations

import argparse
from datetime import timedelta

from app.config import get_settings
from app.database import SessionLocal
from app.repositories.cluster_repository import ClusterRepository
from app.services.ai_synthesis import synthesize_cluster
from app.utils.dates import utc_now


def build_parser() -> argparse.ArgumentParser:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Run optional AI synthesis for Warka clusters")
    parser.add_argument("--hours", type=int, default=settings.ingest_lookback_hours, help="Lookback window in hours")
    parser.add_argument("--cluster-id", dest="cluster_id", help="Run synthesis for a specific cluster")
    parser.add_argument("--dry-run", action="store_true", help="Build prompts and validate responses without saving")
    parser.add_argument("--force", action="store_true", help="Regenerate synthesis even if AI output already exists")
    parser.add_argument("--limit", type=int, default=25, help="Maximum recent clusters to inspect")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    db = SessionLocal()
    summary = {"processed": 0, "updated": 0, "skipped": 0, "failed": 0}

    try:
        cluster_repo = ClusterRepository(db)
        if args.cluster_id:
            cluster = cluster_repo.get(args.cluster_id)
            clusters = [cluster] if cluster else []
        else:
            cutoff = utc_now() - timedelta(hours=max(args.hours, 1))
            clusters = cluster_repo.list_recent_for_synthesis(
                cutoff=cutoff,
                limit=max(args.limit, 1),
                include_completed=args.force,
            )

        if not clusters:
            print("No eligible clusters found.")

        for cluster in clusters:
            if cluster is None:
                continue
            summary["processed"] += 1
            result = synthesize_cluster(db, cluster.id, force=args.force, dry_run=args.dry_run)
            print("{0}: {1} ({2})".format(cluster.id, result.status, result.reason or "ok"))
            if result.status in summary:
                summary[result.status] += 1
            else:
                summary["failed"] += 1
    finally:
        db.close()

    print(
        "processed={processed} updated={updated} skipped={skipped} failed={failed}".format(
            **summary
        )
    )


if __name__ == "__main__":
    main()

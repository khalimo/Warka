from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import require_internal_api_key
from app.database import get_db
from app.rate_limit import require_internal_rate_limit
from app.schemas import IngestRun
from app.services.ingestion_service import run_ingestion


router = APIRouter(prefix="/api", tags=["ingestion"])


@router.post(
    "/ingest",
    response_model=IngestRun,
    dependencies=[Depends(require_internal_api_key), Depends(require_internal_rate_limit)],
)
def trigger_ingestion(db: Session = Depends(get_db)) -> IngestRun:
    return IngestRun.model_validate(run_ingestion(db))

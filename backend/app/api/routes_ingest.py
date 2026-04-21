from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import IngestRun
from app.services.ingestion_service import run_ingestion


router = APIRouter(prefix="/api", tags=["ingestion"])


@router.post("/ingest", response_model=IngestRun)
def trigger_ingestion(db: Session = Depends(get_db)) -> IngestRun:
    return IngestRun.model_validate(run_ingestion(db))


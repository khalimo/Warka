from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.mappers import map_source_to_response
from app.repositories.source_repository import SourceRepository
from app.schemas import Source


router = APIRouter(prefix="/api", tags=["sources"])


@router.get("/sources", response_model=list[Source])
def get_sources(db: Session = Depends(get_db)) -> list[Source]:
    repository = SourceRepository(db)
    return [map_source_to_response(source) for source in repository.list_active()]


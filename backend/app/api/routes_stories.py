from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.mappers import map_story_to_response
from app.repositories.story_repository import StoryRepository
from app.schemas import PaginatedResponse, Story


router = APIRouter(prefix="/api/stories", tags=["stories"])


@router.get("/latest", response_model=PaginatedResponse[Story])
def get_latest_stories(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedResponse[Story]:
    repository = StoryRepository(db)
    items = repository.list_latest(limit=limit, offset=offset)
    return PaginatedResponse[Story](
        items=[map_story_to_response(item) for item in items],
        total=repository.count_all(),
        limit=limit,
        offset=offset,
    )


@router.get("/section/somalia", response_model=PaginatedResponse[Story])
def get_somalia_stories(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedResponse[Story]:
    repository = StoryRepository(db)
    items = repository.list_by_region(region="somalia", limit=limit, offset=offset)
    return PaginatedResponse[Story](
        items=[map_story_to_response(item) for item in items],
        total=repository.count_by_region("somalia"),
        limit=limit,
        offset=offset,
    )


@router.get("/section/world", response_model=PaginatedResponse[Story])
def get_world_stories(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> PaginatedResponse[Story]:
    repository = StoryRepository(db)
    items = repository.list_by_region(region="world", limit=limit, offset=offset)
    return PaginatedResponse[Story](
        items=[map_story_to_response(item) for item in items],
        total=repository.count_by_region("world"),
        limit=limit,
        offset=offset,
    )


@router.get("/{slug}", response_model=Story)
def get_story(slug: str, db: Session = Depends(get_db)) -> Story:
    story = StoryRepository(db).get_by_slug(slug)
    if story is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Story not found")
    return map_story_to_response(story)


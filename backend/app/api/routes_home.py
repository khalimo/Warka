from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.mappers import map_cluster_to_response, map_story_to_response
from app.repositories.cluster_repository import ClusterRepository
from app.repositories.story_repository import StoryRepository
from app.schemas import HomePageData


router = APIRouter(prefix="/api", tags=["home"])


@router.get("/home", response_model=HomePageData)
def get_home_page(db: Session = Depends(get_db)) -> HomePageData:
    story_repo = StoryRepository(db)
    cluster_repo = ClusterRepository(db)

    hero_story = story_repo.hero_story()
    if hero_story is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stories available")

    compare_clusters = cluster_repo.list_recent_renderable(limit=6)
    compare_preview = compare_clusters[0] if compare_clusters else None

    return HomePageData(
        hero_story=map_story_to_response(hero_story),
        secondary_stories=[map_story_to_response(item) for item in story_repo.secondary_stories(hero_story.id, limit=3)],
        compare_preview=map_cluster_to_response(compare_preview) if compare_preview is not None else None,
        compare_clusters=[map_cluster_to_response(cluster) for cluster in compare_clusters],
        latest_stories=[map_story_to_response(item) for item in story_repo.latest_for_home(limit=10)],
        somalia_stories=[map_story_to_response(item) for item in story_repo.list_by_region("somalia", limit=6, offset=0)],
        world_stories=[map_story_to_response(item) for item in story_repo.list_by_region("world", limit=4, offset=0)],
    )

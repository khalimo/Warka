from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import (
    routes_clusters,
    routes_health,
    routes_home,
    routes_ingest,
    routes_operations,
    routes_sources,
    routes_stories,
)
from app.config import get_settings
from app.database import SessionLocal
from app.logging_config import configure_logging
from app.services.source_service import seed_initial_sources, verify_registered_sources


settings = get_settings()
configure_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = SessionLocal()
    try:
        seed_initial_sources(db)
        if settings.source_validation_on_startup:
            verify_registered_sources(db, manual_reenable=False, force=False)
    except Exception:
        logger.exception("Startup source seeding failed")
    finally:
        db.close()
    yield


app = FastAPI(title="Warka Backend", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled application error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(routes_health.router)
app.include_router(routes_home.router)
app.include_router(routes_stories.router)
app.include_router(routes_clusters.router)
app.include_router(routes_sources.router)
app.include_router(routes_ingest.router)
app.include_router(routes_operations.router)

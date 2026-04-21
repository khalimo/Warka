# Warka Backend

Production FastAPI backend for Warka, a Somali news aggregation and comparison platform.

## What It Includes

- FastAPI JSON API for the Next.js frontend
- SQLAlchemy 2.0 models and repositories
- Alembic migrations for schema management
- PostgreSQL-ready persistence
- RSS ingestion with `httpx` + `feedparser`
- HTML sanitization with `bleach`
- Deterministic V1 clustering with Jaccard similarity
- Startup-safe seeding for the 5 canonical sources

## Backend Structure

```text
backend/
  app/
  migrations/
  requirements.txt
  alembic.ini
  .env.example
  README.md
```

## Local Development

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Create the database, then run migrations:

```bash
createdb warka
alembic upgrade head
```

Start the API server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:

```text
http://localhost:8000/docs
```

## Render Deployment

Create a Render Web Service pointing at `backend/` with:

```text
Build Command:
pip install -r requirements.txt

Start Command:
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Required environment variables:

```text
DATABASE_URL
OPENAI_API_KEY
ENABLE_OPENAI=false
CORS_ORIGINS=["https://your-frontend-domain.com","http://localhost:3000"]
FEED_TIMEOUT=30
FEED_LIMIT_PER_SOURCE=20
INGEST_LOOKBACK_HOURS=48
LOG_LEVEL=INFO
CLUSTER_SIMILARITY_THRESHOLD=0.6
```

## API Endpoints

```text
GET  /api/health
GET  /api/home
GET  /api/stories/latest
GET  /api/stories/section/somalia
GET  /api/stories/section/world
GET  /api/stories/{slug}
GET  /api/clusters
GET  /api/sources
POST /api/ingest
```

## First Run Workflow

1. Run migrations
2. Start the API
3. Source seeding happens on startup
4. Trigger ingestion:

```bash
curl -X POST http://localhost:8000/api/ingest
```

5. Verify:

```bash
curl http://localhost:8000/api/home
```

## Scheduled Ingestion

Render cron example, every 30 minutes:

```bash
cd /opt/render/project/src/backend && alembic upgrade head && python -m app.jobs.run_ingestion
```

Clustering can also be run separately:

```bash
cd /opt/render/project/src/backend && alembic upgrade head && python -m app.jobs.run_clustering
```

## Exact Commands

Set up database:

```bash
createdb warka
```

Run migrations:

```bash
cd backend
alembic upgrade head
```

Start the server:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Trigger first ingestion:

```bash
curl -X POST http://localhost:8000/api/ingest
```

Set up a cron job locally:

```bash
*/30 * * * * cd /absolute/path/to/backend && . .venv/bin/activate && alembic upgrade head && python -m app.jobs.run_ingestion >> /tmp/warka_ingest.log 2>&1
```

## Notes

- OpenAI enrichment is optional and currently not required for clustering.
- Search, auth, newsletter APIs, and advanced clustering are intentionally excluded for this backend version.
- The backend assumes migrations have been applied before normal startup.

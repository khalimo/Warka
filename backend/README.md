# Warka Backend

Production FastAPI backend for Warka, a Somali news aggregation and comparison platform.

## What It Includes

- FastAPI JSON API for the Next.js frontend
- SQLAlchemy 2.0 models and repositories
- Alembic migrations for schema management
- PostgreSQL-ready persistence
- RSS ingestion with `httpx` + `feedparser`
- Lightweight article enrichment with `beautifulsoup4`
- HTML sanitization with `bleach`
- Deterministic V1 clustering with Jaccard similarity
- Source registry with verification-first enablement
- Source health monitoring and CLI health report
- Optional AI synthesis for cluster-level consensus summaries

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
ENABLE_OPENAI=false
ENABLE_AI_SYNTHESIS=false
AI_MODEL=gpt-4o-mini
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=500
CORS_ORIGINS=["https://your-frontend-domain.com","http://localhost:3000"]
SOURCE_VALIDATION_ON_STARTUP=true
VERIFICATION_TIMEOUT=15
FEED_TIMEOUT=30
FEED_LIMIT_PER_SOURCE=20
INGEST_LOOKBACK_HOURS=48
ENABLE_SCRAPERS=false
SCRAPE_RATE_LIMIT_SECONDS=2
HEALTH_CHECK_INTERVAL_HOURS=24
LOG_LEVEL=INFO
CLUSTER_SIMILARITY_THRESHOLD=0.6
```

Optional:

```text
OPENAI_API_KEY
```

AI synthesis stays fully optional. If `ENABLE_AI_SYNTHESIS=false`, no model calls are made and the rest of the backend behaves exactly as before.

For a split Render/Vercel deployment, set `CORS_ORIGINS` to include both your production frontend URL and local development URL. Example:

```text
CORS_ORIGINS=["https://warka-news.vercel.app","http://localhost:3000"]
```

## Source Verification

Candidate sources are seeded into the registry, but only verified feeds should remain enabled.

Run verification manually:

```bash
cd backend
python -m app.cli.verify_sources
```

Review source health:

```bash
cd backend
python -m app.cli.source_health_report
```

Run manual AI synthesis for recent clusters:

```bash
cd backend
python -m app.cli.run_ai_synthesis --hours 48 --limit 20
```

Useful flags:

```bash
python -m app.cli.run_ai_synthesis --cluster-id <cluster-id>
python -m app.cli.run_ai_synthesis --hours 48 --limit 20 --dry-run
python -m app.cli.run_ai_synthesis --hours 48 --limit 20 --force
```

Verified working feeds in the current pass:

- BBC Somali — `https://feeds.bbci.co.uk/somali/rss.xml`
- Horseed Media — `https://horseedmedia.net/feed`
- SONNA — `https://sonna.so/en/feed`
- Caasimada Online — `https://www.caasimada.net/feed/`
- Goobjoog News — `https://goobjoog.com/feed/`
- Radio Muqdisho — `https://radiomuqdisho.so/feed/`
- Hiiraan Online — `https://www.hiiraan.com/news.xml`
- Puntland Post — `https://puntlandpost.net/feed`
- Somali Guardian — `https://somaliguardian.com/feed/`
- Radio Dalsan — `https://radiodalsan.com/feed/`
- Shabelle Media — `https://shabellemedia.com/feed/`

Currently disabled:

- Garowe Online — `https://garoweonline.com/en/rss-feed` (HTTP 500 during verification)

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

6. Optionally inspect source health:

```bash
python -m app.cli.source_health_report
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
- The source registry tracks validation status, last validation time, response time, and consecutive failures. Sources auto-disable after three ingestion failures.
- If feed content is too thin or an image is missing, the ingestion pipeline now attempts a lightweight article-page enrichment pass before falling back to category placeholder artwork.
- Scraper support exists as a disabled scaffold but no scraper is enabled by default in this pass.
- AI synthesis is stored in separate `ai_*` fields on clusters and is only generated through the manual CLI in this pass.
- Search, auth, newsletter APIs, and advanced clustering are intentionally excluded for this backend version.
- The backend assumes migrations have been applied before normal startup.

# Warka Deployment Runbook

Warka's active production stack is split into a public Next.js frontend and a FastAPI backend.

```text
Frontend:  frontend/  -> Vercel       -> https://www.warkasta.com
Backend:   backend/   -> Render        -> https://api.warkasta.com
Database:  Render Postgres
DNS:       Cloudflare
Legacy:    app.py Streamlit app remains in the repo, but is not the active public frontend.
```

## Production Domains

Use these hostnames:

```text
www.warkasta.com       Vercel frontend
warkasta.com           Vercel apex redirect or primary alias
api.warkasta.com       Render FastAPI backend
```

## Cloudflare DNS

Keep records as DNS only during setup and verification.

```text
CNAME  api  warka-api.onrender.com                 DNS only
CNAME  www  <Vercel-provided target>               DNS only
A      @    76.76.21.21                            DNS only
TXT    _vercel <Vercel-provided verification text>  DNS only
```

Do not point `www` at Cloudflare Pages or `somanews.pages.dev`.
Do not put `api.warkasta.com` in the CNAME target field. The `api` target should be the Render hostname.

## Render Backend

Create a Render Web Service with:

```text
Root Directory: backend
Build Command: pip install -r requirements.txt
Start Command: alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
Health Check Path: /api/health
```

Required environment variables:

```text
DATABASE_URL=<Render internal database URL>
ENABLE_OPENAI=false
ENABLE_AI_SYNTHESIS=false
AI_MODEL=gpt-4o-mini
AI_TEMPERATURE=0.3
AI_MAX_TOKENS=500
CORS_ORIGINS=["https://www.warkasta.com","https://warkasta.com","http://localhost:3000"]
SOURCE_VALIDATION_ON_STARTUP=true
VERIFICATION_TIMEOUT=15
FEED_TIMEOUT=30
FEED_LIMIT_PER_SOURCE=20
INGEST_LOOKBACK_HOURS=48
ENABLE_SCRAPERS=false
SCRAPE_RESPECT_ROBOTS=true
SCRAPE_RATE_LIMIT_SECONDS=2
SCRAPE_MAX_ARTICLES_PER_SOURCE=8
SCRAPE_USER_AGENT=WarkaNewsBot/1.0 (+https://www.warkasta.com)
HEALTH_CHECK_INTERVAL_HOURS=24
LOG_LEVEL=INFO
CLUSTER_SIMILARITY_THRESHOLD=0.6
```

Optional AI synthesis:

```text
OPENAI_API_KEY=<server-side API key>
ENABLE_AI_SYNTHESIS=true
```

## Vercel Frontend

Create a Vercel project from the GitHub repo with:

```text
Root Directory: frontend
Framework Preset: Next.js
```

Required environment variables:

```text
NEXT_PUBLIC_API_BASE_URL=https://api.warkasta.com
NEXT_PUBLIC_SITE_URL=https://www.warkasta.com
ENABLE_INTERNAL_AI_REVIEW=false
```

Redeploy after changing environment variables.

## First Data Run

The homepage needs both stories and at least one cluster. After the backend is live, trigger ingestion:

```bash
curl -X POST https://api.warkasta.com/api/ingest
```

Then verify:

```bash
curl https://api.warkasta.com/api/health
curl https://api.warkasta.com/api/home
curl https://www.warkasta.com
```

If `api.warkasta.com` is not resolving yet, test Render directly:

```bash
curl https://warka-api.onrender.com/api/health
curl -X POST https://warka-api.onrender.com/api/ingest
```

## Production Smoke Check

Run:

```bash
scripts/production-smoke.sh
```

You can override domains:

```bash
FRONTEND_URL=https://www.warkasta.com API_BASE_URL=https://api.warkasta.com scripts/production-smoke.sh
```

The smoke check verifies the frontend responds, backend health responds, story endpoints respond, and the homepage API has enough data to render.

## Legacy Streamlit App

The root `app.py` Streamlit app is retained as legacy reference code. Do not use the root `render.yaml` for the active public Warka deployment. Once the Next.js and FastAPI stack is stable, move the legacy Streamlit files into a `legacy-streamlit/` folder or remove them in a dedicated cleanup pass.

# Somali News Lens

Somali News Lens is a Streamlit dashboard for ingesting RSS news, comparing multi-source coverage, classifying editorial framing, clustering related stories, and reviewing source/region analytics.

The app is designed as a production-ready MVP for Render free-tier testing. It uses Postgres on Render, SQLite for local development, and falls back gracefully when OpenAI is not configured or quota-limited.

## What It Does

- Ingests configured RSS feeds
- Deduplicates stories by normalized title, URL, and source
- Classifies framing with OpenAI when available
- Uses local fallback classification when OpenAI is missing or unavailable
- Clusters related stories with TF-IDF and DBSCAN
- Shows multi-source comparison cards
- Provides analytics for source activity, framing mix, and coverage volume
- Supports login and registration with bcrypt password hashing
- Keeps secrets out of the repo

## Local Setup

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
export DATABASE_URL=sqlite:///news.db
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Open:

```text
http://localhost:8501
```

OpenAI is optional. If `OPENAI_API_KEY` is not set, the app still works with fallback classification.

## Render Deployment

The repo includes `render.yaml`, so Render can create:

- a Python web service
- a free Postgres database
- a `DATABASE_URL` environment variable wired from that database

### Render Settings

Use these settings if entering them manually:

```text
Service type: Web Service
Branch: main
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
Health Check Path: /_stcore/health
```

Do not create a Static Site. Streamlit must run as a Web Service.

### Environment Variables

Required on Render:

```text
DATABASE_URL
```

If using the included blueprint, Render sets `DATABASE_URL` from the Postgres database automatically.

Optional:

```text
OPENAI_API_KEY
OPENAI_MODEL=gpt-4o-mini
OPENAI_ENABLED=true
MAX_ARTICLES_PER_FEED=12
MAX_AI_CLASSIFICATIONS_PER_RUN=8
SESSION_TIMEOUT_MINUTES=45
```

If your OpenAI key has no quota, the app will detect the failure and continue with fallback classification.

## Validation

Run a quick local smoke test:

```bash
python smoke_test.py
```

The smoke test checks:

- database initialization
- duplicate insert protection
- fallback classification
- clustering path
- registration
- login

## Operational Notes

- Render free services may sleep after inactivity.
- The first request after sleep can be slow.
- Free Postgres is suitable for testing, not production retention guarantees.
- RSS feeds can temporarily fail or return malformed entries; the app reports feed warnings without crashing.
- OpenAI failures are isolated so ingestion can continue.

## Files

```text
app.py                Main Streamlit application
render.yaml           Render web service and Postgres blueprint
runtime.txt           Python runtime pin for Render
requirements.txt      Python dependencies
.env.example          Local environment template
smoke_test.py         Lightweight validation script
AGENTS.md             Codex repo instructions
IMPLEMENT.md          Implementation runbook
```

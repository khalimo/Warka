# Somali News Lens

Somali News Lens is a dual-mode Streamlit product for Somali and international news coverage: a public news front page with built-in source comparison, plus a private newsroom intelligence workspace.

- Reader Mode is a public-facing news website for visitors.
- Editor / Insights Mode is an internal newsroom workspace for feed monitoring, ingestion, comparison, analytics, and operations.

The app is built for Render free-tier testing with a simple Python web service and Postgres database. It also supports local SQLite development.

## Product Modes

### Reader Mode

Reader Mode is the public news experience:

- publication-style homepage
- lead story and top-story hierarchy
- deeper latest news stream with search
- Somalia section
- World and regional context
- reader-friendly Compare Coverage cards
- source, section, time, and framing labels
- feed image support when publishers provide media
- graceful sparse-data states

### Editor / Insights Mode

Editor / Insights Mode is the internal workflow:

- newsroom dashboard
- feed ingestion
- coverage intelligence
- analytics
- source health monitoring
- operations and maintenance
- account/login flow

Operational controls are separated from the public reader experience.
Insights Mode requires sign-in before dashboard, ingestion, source health, analytics, or operations pages are shown.

## Source Coverage

The source catalog lives in `sources.py`. It includes Somali national, regional Somali, Somaliland, diaspora, humanitarian, Africa-region, Somali-language international, and global feeds. The default Render config ingests the full configured catalog while keeping concurrency low enough for free-tier testing.

Current configured sources include:

- Hiiraan Online
- SONNA English
- Radio Muqdisho
- Somali National TV
- BBC Somali
- VOA Somali
- Shabelle Media
- Goobjoog English
- Caasimada Online
- Raxanreeb Online
- Jowhar
- Puntland Post
- Horseed Media
- Hiiraanweyn
- Puntland Mirror
- Somali Guardian
- Somali Dispatch
- The Somali Digest
- Idil News
- Mudug24
- Goobjooge
- AllSanaag
- Wardheer News
- Radio Ergo
- Somaliland Chronicle
- Berbera News
- Wargeyska Dawan
- Oodweyne Media
- Saxafi Media
- AllAfrica Somalia
- ReliefWeb Somalia
- The Guardian Somalia
- New York Times Somalia
- New York Times Africa
- BBC World
- BBC Africa
- Al Jazeera

Feed failures are isolated per source. A broken source should report as failed in Insights Mode without crashing the app.

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

OpenAI is optional. If `OPENAI_API_KEY` is missing or quota-limited, ingestion continues with local fallback classification.

## Render Deployment

Use a Render Web Service, not a Static Site.

The included `render.yaml` can create:

- a Python web service
- a free Postgres database
- a `DATABASE_URL` environment variable wired from that database

Manual Render settings:

```text
Service type: Web Service
Branch: main
Build Command: pip install -r requirements.txt
Start Command: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
Health Check Path: /_stcore/health
```

## Environment Variables

Required on Render:

```text
DATABASE_URL
```

Optional:

```text
OPENAI_API_KEY
OPENAI_MODEL=gpt-4o-mini
OPENAI_ENABLED=true
MAX_FEEDS_PER_RUN=37
MAX_ARTICLES_PER_FEED=16
FEED_CONCURRENCY=6
MAX_AI_CLASSIFICATIONS_PER_RUN=8
READER_LOOKBACK_DAYS=60
READER_LATEST_LIMIT=90
READER_SECTION_LIMIT=72
SESSION_TIMEOUT_MINUTES=45
EDITOR_INVITE_CODE=
```

Set `EDITOR_INVITE_CODE` if you want new editor accounts to require a private invite code.

## Validation

Run the local smoke test:

```bash
python smoke_test.py
```

The smoke test checks:

- database initialization and lightweight migrations
- duplicate insert protection
- new story section/source fields
- source rollups
- fallback classification
- clustering path
- registration and login
- expanded source catalog presence

## Operational Notes

- Render free web services may sleep after inactivity.
- First load after sleep can be slow.
- Free Postgres is suitable for MVP testing, not production-grade retention.
- RSS feeds can fail, throttle, or change format; source failures are isolated and visible in Insights Mode.
- Reader Mode does not call OpenAI during page rendering.
- Ingestion caps feeds and article volume to stay free-tier friendly, but Reader Mode can show a much deeper latest and section archive than the homepage.

## Key Files

```text
app.py                Main Streamlit application
sources.py            Source catalog and metadata
render.yaml           Render web service and Postgres blueprint
runtime.txt           Python runtime pin for Render
requirements.txt      Python dependencies
.env.example          Local environment template
smoke_test.py         Lightweight validation script
AGENTS.md             Codex repo instructions
IMPLEMENT.md          Implementation runbook
```

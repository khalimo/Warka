# AGENTS.md

## Project
Somali News Lens is a dual-mode Streamlit news product:
- Reader Mode is a public-facing Somali news website
- Editor / Insights Mode is an internal newsroom intelligence dashboard
- The app ingests RSS feeds, classifies framing, clusters related stories, compares coverage, supports login/registration, and shows analytics/source health

## Run
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

## Environment variables
OPENAI_API_KEY
DATABASE_URL

## Rules
- Fix runtime issues before major refactors.
- Do not hardcode secrets.
- Keep deployment compatible with Render.
- Prefer production-safe fixes over hacks.
- Use PostgreSQL in deployment through DATABASE_URL.
- Keep public Reader Mode separate from internal operations.

## Validate
- Reader Mode home/latest/section/compare pages load.
- Insights Mode dashboard, ingest, sources, analytics, operations, and account pages load.
- Ingest fetches and stores stories.
- Duplicate insert protection works.
- Bias classification returns labels.
- Clustering works.
- Login and registration work.
- Source health is visible after ingest.

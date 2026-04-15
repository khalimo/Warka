# AGENTS.md

## Project
Somali News Lens is a Streamlit app that:
- ingests RSS feeds
- classifies framing/bias with OpenAI
- clusters related stories
- supports login/registration
- shows analytics

## Run
pip install -r requirements.txt
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

## Environment variables
OPENAI_API_KEY
DATABASE_URL

## Rules
- Fix runtime issues before major refactors
- Do not hardcode secrets
- Keep deployment compatible with Render
- Prefer production-safe fixes over hacks

## Validate
- Home loads
- Ingest News fetches and stores stories
- Duplicate insert protection works
- Bias classification returns labels
- Clustering works
- Login and registration work
- Analytics renders

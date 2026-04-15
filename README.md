# Somali News Lens

A Streamlit app for ingesting and analyzing news coverage across multiple sources.

## Features
- RSS news ingestion
- AI-assisted framing/bias classification
- Story clustering with TF-IDF and DBSCAN
- Login and registration
- Analytics dashboard
- Duplicate article protection
- Render-ready deployment

## Local run

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=your_key_here
export DATABASE_URL=sqlite:///news.db
streamlit run app.py
```

If `OPENAI_API_KEY` is not set, the app uses a local fallback classifier so the core UI can still be tested.

## Render

Set these environment variables in Render:

- `OPENAI_API_KEY`
- `DATABASE_URL`

The included `render.yaml` starts Streamlit with:

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Codex validation prompt

```text
Review, improve, deploy, and test this Streamlit app.

Tasks:
1. Install dependencies and run the app.
2. Fix all runtime errors.
3. Verify OpenAI integration works with the current SDK.
4. Verify Render deployment config is correct.
5. Deploy to Render.
6. Test:
   - Home page
   - Ingest News
   - DB insert path
   - bias classification
   - clustering
   - registration/login
   - analytics
7. Fix any failures and redeploy.
8. Return the live URL, change summary, and remaining risks.

Read AGENTS.md first and use it as the repo instruction file.
```

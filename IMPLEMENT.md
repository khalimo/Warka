# IMPLEMENT.md

## Goal
Review, improve, deploy, and test Somali News Lens end to end as a dual-mode product.

## Milestones
1. Install dependencies and run locally in sandbox.
2. Fix runtime/import/OpenAI API issues.
3. Replace SQLite-only behavior with PostgreSQL-compatible database access using DATABASE_URL.
4. Add duplicate prevention for stories.
5. Maintain a public Reader Mode and private Editor / Insights Mode.
6. Add or verify Render deployment config.
7. Deploy to Render.
8. Test live app end to end.
9. Summarize changes and remaining risks.

## Constraints
- Use environment variables only.
- No hardcoded secrets.
- Streamlit must bind to 0.0.0.0 and $PORT on Render.
- Keep diffs scoped and reviewable.
- Public reader pages must not expose operations, secrets, or debug traces.

## Validation after each milestone
- Run the app or relevant tests.
- Fix failures immediately before moving on.

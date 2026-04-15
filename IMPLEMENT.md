# IMPLEMENT.md

## Goal
Review, improve, deploy, and test Somali News Lens end to end.

## Milestones
1. Install dependencies and run locally in sandbox
2. Fix runtime/import/OpenAI API issues
3. Replace SQLite with PostgreSQL using DATABASE_URL
4. Add duplicate prevention for stories
5. Add Render deployment config
6. Deploy to Render
7. Test live app end to end
8. Summarize changes and remaining risks

## Constraints
- Use environment variables only
- No hardcoded secrets
- Streamlit must bind to 0.0.0.0 and $PORT on Render
- Keep diffs scoped and reviewable

## Validation after each milestone
- Run the app or relevant tests
- Fix failures immediately before moving on

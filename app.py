import asyncio
import hashlib
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Optional

import aiohttp
import bcrypt
import feedparser
import pandas as pd
import plotly.express as px
import streamlit as st
from openai import OpenAI
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from tenacity import retry, stop_after_attempt, wait_exponential


class Config:
    APP_NAME = "Somali News Lens"
    VERSION = "3.0.0"

    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///news.db")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    SESSION_TIMEOUT_MINUTES = 30
    PASSWORD_MIN_LENGTH = 8
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_MINUTES = 15

    CACHE_TTL_SECONDS = 300
    MAX_ARTICLES_PER_FEED = 15

    CLUSTER_EPS = 0.45
    CLUSTER_MIN_SAMPLES = 2

    FEEDS = [
        {
            "name": "BBC World",
            "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
            "region": "international",
        },
        {
            "name": "Al Jazeera",
            "url": "https://www.aljazeera.com/xml/rss/all.xml",
            "region": "international",
        },
        {
            "name": "Garowe Online",
            "url": "https://www.garoweonline.com/en/rss",
            "region": "somalia",
        },
        {
            "name": "Hiiraan Online",
            "url": "https://www.hiiraan.com/rss.xml",
            "region": "somalia",
        },
    ]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("somali-news-lens")


st.set_page_config(
    page_title=Config.APP_NAME,
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_engine() -> Engine:
    connect_args = {}
    if Config.DATABASE_URL.startswith("sqlite"):
        connect_args = {"check_same_thread": False}
    return create_engine(
        Config.DATABASE_URL,
        future=True,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


def is_postgres(engine: Engine) -> bool:
    return engine.dialect.name in {"postgresql", "postgres"}


def id_column(engine: Engine) -> str:
    if is_postgres(engine):
        return "id SERIAL PRIMARY KEY"
    return "id INTEGER PRIMARY KEY AUTOINCREMENT"


def init_db(engine: Engine) -> None:
    pk = id_column(engine)
    with engine.begin() as conn:
        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS users (
                {pk},
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE,
                role TEXT DEFAULT 'user',
                login_attempts INTEGER DEFAULT 0,
                locked_until TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP NULL
            )
        """))

        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS stories (
                {pk},
                article_hash TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                summary TEXT,
                content TEXT,
                source TEXT NOT NULL,
                source_url TEXT,
                region TEXT,
                language TEXT DEFAULT 'en',
                published_at TIMESTAMP NULL,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                bias TEXT,
                bias_confidence REAL,
                ai_summary TEXT,
                cluster_label INTEGER NULL
            )
        """))

        conn.execute(text(f"""
            CREATE TABLE IF NOT EXISTS user_activity (
                {pk},
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                story_id INTEGER NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))

        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_source ON stories(source)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_region ON stories(region)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_published_at ON stories(published_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_bias ON stories(bias)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_cluster_label ON stories(cluster_label)"))


engine = get_engine()
init_db(engine)


def hash_article(title: str, source_url: str) -> str:
    key = f"{title.strip().lower()}|{source_url.strip().lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def parse_feed_datetime(entry) -> Optional[datetime]:
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        if hasattr(entry, "updated_parsed") and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6])
    except Exception:
        return None
    return None


def init_session_state() -> None:
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("login_time", None)


def logout() -> None:
    st.session_state["user"] = None
    st.session_state["login_time"] = None


def session_active() -> bool:
    user = st.session_state.get("user")
    login_time = st.session_state.get("login_time")
    if not user or not login_time:
        return False
    if datetime.utcnow() - login_time > timedelta(minutes=Config.SESSION_TIMEOUT_MINUTES):
        logout()
        return False
    return True


def log_activity(username: str, action: str, story_id: Optional[int] = None) -> None:
    if not username:
        return
    with engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO user_activity (username, action, story_id)
                VALUES (:username, :action, :story_id)
            """),
            {"username": username, "action": action, "story_id": story_id},
        )


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def register_user(username: str, password: str, email: Optional[str]) -> tuple[bool, str]:
    username = username.strip()
    email = email.strip() if email else None
    if len(password) < Config.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {Config.PASSWORD_MIN_LENGTH} characters."
    if not username:
        return False, "Username is required."

    try:
        with engine.begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO users (username, password_hash, email)
                    VALUES (:username, :password_hash, :email)
                """),
                {
                    "username": username,
                    "password_hash": hash_password(password),
                    "email": email,
                },
            )
        return True, "Account created."
    except Exception as exc:
        logger.warning("register_user failed: %s", exc)
        return False, "Could not create account. Username or email may already exist."


def login_user(username: str, password: str) -> tuple[bool, str]:
    username = username.strip()
    with engine.begin() as conn:
        row = conn.execute(
            text("""
                SELECT username, password_hash, login_attempts, locked_until
                FROM users
                WHERE username = :username
            """),
            {"username": username},
        ).mappings().first()

        if not row:
            return False, "Invalid username or password."

        locked_until = row["locked_until"]
        if locked_until:
            try:
                locked_dt = pd.to_datetime(locked_until).to_pydatetime()
                if locked_dt > datetime.utcnow():
                    return False, "Account is temporarily locked. Try again later."
            except Exception:
                logger.info("Could not parse lockout timestamp for %s", username)

        if verify_password(password, row["password_hash"]):
            conn.execute(
                text("""
                    UPDATE users
                    SET login_attempts = 0,
                        locked_until = NULL,
                        last_login = CURRENT_TIMESTAMP
                    WHERE username = :username
                """),
                {"username": username},
            )
            st.session_state["user"] = username
            st.session_state["login_time"] = datetime.utcnow()
            log_activity(username, "login")
            return True, "Login successful."

        next_attempts = int(row["login_attempts"] or 0) + 1
        lockout_until = None
        if next_attempts >= Config.MAX_LOGIN_ATTEMPTS:
            lockout_until = datetime.utcnow() + timedelta(minutes=Config.LOCKOUT_MINUTES)

        conn.execute(
            text("""
                UPDATE users
                SET login_attempts = :login_attempts,
                    locked_until = :locked_until
                WHERE username = :username
            """),
            {
                "username": username,
                "login_attempts": next_attempts,
                "locked_until": lockout_until,
            },
        )
        return False, "Invalid username or password."


@st.cache_resource
def get_openai_client() -> Optional[OpenAI]:
    if not Config.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=Config.OPENAI_API_KEY)


def fallback_bias(text_input: str) -> str:
    text_lower = text_input.lower()
    left_words = {"justice", "equity", "climate", "rights", "reform", "workers"}
    right_words = {"security", "military", "border", "conservative", "tradition", "terror"}
    left_count = sum(1 for word in left_words if word in text_lower)
    right_count = sum(1 for word in right_words if word in text_lower)
    if left_count > right_count + 1:
        return "left"
    if right_count > left_count + 1:
        return "right"
    return "center"


def parse_ai_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        start = raw.find("{")
        end = raw.rfind("}")
        if start >= 0 and end > start:
            return json.loads(raw[start : end + 1])
        raise


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=8))
def classify_bias_with_ai(text_input: str) -> tuple[str, float]:
    client = get_openai_client()
    if client is None:
        return fallback_bias(text_input), 0.45

    prompt = (
        "Classify the political or editorial framing of this news text. "
        "Return strict JSON with keys bias and confidence. "
        "Allowed bias values: left, center-left, center, center-right, right. "
        f"Text: {text_input[:1200]}"
    )

    try:
        response = client.responses.create(
            model=Config.OPENAI_MODEL,
            input=prompt,
            max_output_tokens=120,
        )
        raw = getattr(response, "output_text", "") or ""
        parsed = parse_ai_json(raw)
        bias = parsed.get("bias", "center")
        confidence = float(parsed.get("confidence", 0.5))
        return bias, max(0.0, min(confidence, 1.0))
    except Exception as exc:
        logger.warning("AI bias classification failed: %s", exc)
        return fallback_bias(text_input), 0.45


@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=4))
def summarize_cluster_with_ai(items: list[dict]) -> str:
    client = get_openai_client()
    if client is None:
        return items[0]["title"] if items else "No summary available."

    joined = "\n\n".join(
        f"Source: {item['source']}\nTitle: {item['title']}\nSummary: {item.get('summary') or ''}"
        for item in items[:4]
    )
    prompt = (
        "Summarize the shared core story across these news reports in 2-3 neutral sentences. "
        "Focus on common facts and avoid sensational language.\n\n"
        f"{joined[:3000]}"
    )

    try:
        response = client.responses.create(
            model=Config.OPENAI_MODEL,
            input=prompt,
            max_output_tokens=180,
        )
        return (getattr(response, "output_text", "") or "").strip() or "No summary available."
    except Exception as exc:
        logger.warning("Cluster summary failed: %s", exc)
        return items[0]["title"] if items else "No summary available."


async def fetch_single_feed(session: aiohttp.ClientSession, feed_def: dict) -> list[dict]:
    try:
        async with session.get(feed_def["url"], timeout=aiohttp.ClientTimeout(total=15)) as resp:
            body = await resp.text()
            parsed = feedparser.parse(body)

        articles = []
        for entry in parsed.entries[: Config.MAX_ARTICLES_PER_FEED]:
            title = entry.get("title", "").strip() or "Untitled"
            summary = entry.get("summary", "") or ""
            content = ""
            if entry.get("content"):
                try:
                    content = entry["content"][0].get("value", "")
                except Exception:
                    content = ""
            source_url = entry.get("link", "") or ""

            articles.append(
                {
                    "title": title,
                    "summary": summary,
                    "content": content,
                    "source": feed_def["name"],
                    "source_url": source_url,
                    "region": feed_def["region"],
                    "language": "en",
                    "published_at": parse_feed_datetime(entry),
                    "fetched_at": datetime.utcnow(),
                    "article_hash": hash_article(title, source_url),
                }
            )
        return articles
    except Exception as exc:
        logger.warning("Feed fetch failed for %s: %s", feed_def["name"], exc)
        return []


async def fetch_all_feeds_async() -> list[dict]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_single_feed(session, feed_def) for feed_def in Config.FEEDS]
        results = await asyncio.gather(*tasks)
    return [item for group in results for item in group]


def fetch_all_feeds() -> list[dict]:
    try:
        return asyncio.run(fetch_all_feeds_async())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(fetch_all_feeds_async())
        finally:
            loop.close()


def enrich_articles(articles: list[dict]) -> list[dict]:
    enriched = []
    for article in articles:
        text_input = f"{article['title']}\n{article.get('summary', '')}"
        bias, confidence = classify_bias_with_ai(text_input)
        article["bias"] = bias
        article["bias_confidence"] = confidence
        enriched.append(article)
    return enriched


def insert_articles(articles: list[dict]) -> int:
    if is_postgres(engine):
        statement = text("""
            INSERT INTO stories (
                article_hash, title, summary, content,
                source, source_url, region, language,
                published_at, fetched_at, bias, bias_confidence, ai_summary, cluster_label
            )
            VALUES (
                :article_hash, :title, :summary, :content,
                :source, :source_url, :region, :language,
                :published_at, :fetched_at, :bias, :bias_confidence, :ai_summary, :cluster_label
            )
            ON CONFLICT (article_hash) DO NOTHING
        """)
    else:
        statement = text("""
            INSERT OR IGNORE INTO stories (
                article_hash, title, summary, content,
                source, source_url, region, language,
                published_at, fetched_at, bias, bias_confidence, ai_summary, cluster_label
            )
            VALUES (
                :article_hash, :title, :summary, :content,
                :source, :source_url, :region, :language,
                :published_at, :fetched_at, :bias, :bias_confidence, :ai_summary, :cluster_label
            )
        """)

    inserted = 0
    with engine.begin() as conn:
        for article in articles:
            result = conn.execute(
                statement,
                {
                    "article_hash": article["article_hash"],
                    "title": article["title"],
                    "summary": article.get("summary"),
                    "content": article.get("content"),
                    "source": article["source"],
                    "source_url": article.get("source_url"),
                    "region": article.get("region"),
                    "language": article.get("language", "en"),
                    "published_at": article.get("published_at"),
                    "fetched_at": article.get("fetched_at", datetime.utcnow()),
                    "bias": article.get("bias"),
                    "bias_confidence": article.get("bias_confidence"),
                    "ai_summary": None,
                    "cluster_label": None,
                },
            )
            if result.rowcount and result.rowcount > 0:
                inserted += 1
    return inserted


@st.cache_data(ttl=Config.CACHE_TTL_SECONDS)
def load_recent_stories(days: int = 7) -> pd.DataFrame:
    query = text("""
        SELECT *
        FROM stories
        WHERE fetched_at >= :cutoff
        ORDER BY COALESCE(published_at, fetched_at) DESC
    """)
    cutoff = datetime.utcnow() - timedelta(days=days)
    with engine.begin() as conn:
        return pd.read_sql(query, conn, params={"cutoff": cutoff})


def assign_clusters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    texts = (df["title"].fillna("") + " " + df["summary"].fillna("")).tolist()
    if len(texts) < 2:
        out = df.copy()
        out["cluster_label"] = [0]
        return out

    vectorizer = TfidfVectorizer(
        max_features=1500,
        stop_words="english",
        ngram_range=(1, 2),
    )
    matrix = vectorizer.fit_transform(texts)
    labels = DBSCAN(
        eps=Config.CLUSTER_EPS,
        min_samples=Config.CLUSTER_MIN_SAMPLES,
        metric="cosine",
    ).fit_predict(matrix)

    out = df.copy()
    out["cluster_label"] = labels
    return out


def persist_cluster_labels(df: pd.DataFrame) -> None:
    if df.empty or "id" not in df.columns or "cluster_label" not in df.columns:
        return
    with engine.begin() as conn:
        for _, row in df[["id", "cluster_label"]].iterrows():
            conn.execute(
                text("""
                    UPDATE stories
                    SET cluster_label = :cluster_label
                    WHERE id = :id
                """),
                {"id": int(row["id"]), "cluster_label": int(row["cluster_label"])},
            )


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(f"## {Config.APP_NAME}")
        page = st.radio(
            "Navigation",
            ["Home", "Ingest News", "Analytics", "Settings"],
            label_visibility="collapsed",
        )

        st.markdown("---")
        st.markdown("### Account")

        if session_active():
            st.success(f"Signed in as {st.session_state['user']}")
            if st.button("Logout"):
                logout()
                st.rerun()
        else:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                if submit:
                    ok, msg = login_user(username, password)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

            with st.expander("Create account"):
                with st.form("register_form"):
                    new_user = st.text_input("New username")
                    new_email = st.text_input("Email")
                    new_password = st.text_input("New password", type="password")
                    confirm = st.text_input("Confirm password", type="password")
                    create = st.form_submit_button("Register")
                    if create:
                        if new_password != confirm:
                            st.error("Passwords do not match.")
                        else:
                            ok, msg = register_user(new_user, new_password, new_email)
                            if ok:
                                st.success(msg)
                            else:
                                st.error(msg)

        st.markdown("---")
        st.caption(f"Version {Config.VERSION}")
        return page


def render_cluster(cluster_df: pd.DataFrame) -> None:
    if cluster_df.empty:
        return

    first = cluster_df.iloc[0].to_dict()
    items = cluster_df.to_dict(orient="records")

    st.markdown("---")
    col_a, col_b = st.columns([3, 1])

    with col_a:
        st.subheader(first["title"])
        st.info(summarize_cluster_with_ai(items))

    with col_b:
        bias_counts = cluster_df["bias"].fillna("unknown").value_counts()
        st.write("**Bias mix**")
        st.bar_chart(bias_counts)

    with st.expander("Compare coverage"):
        cols = st.columns(min(3, len(items)))
        for idx, item in enumerate(items):
            with cols[idx % len(cols)]:
                st.markdown(f"### {item['source']}")
                confidence = float(item.get("bias_confidence") or 0)
                st.caption(f"Bias: {item.get('bias', 'unknown')} | Confidence: {confidence:.0%}")
                st.write(item.get("summary") or "No summary available.")
                if item.get("source_url"):
                    st.markdown(f"[Read full article]({item['source_url']})")


def home_page() -> None:
    st.header("Top stories")

    days = st.slider("Look back window (days)", 1, 14, 7)
    region = st.selectbox("Region", ["All", "somalia", "international"])
    df = load_recent_stories(days)

    if df.empty:
        st.info("No stories available yet. Go to Ingest News to fetch the latest feeds.")
        return

    if region != "All":
        df = df[df["region"] == region]

    if df.empty:
        st.info("No stories match that filter.")
        return

    df = assign_clusters(df)
    persist_cluster_labels(df)

    clustered = df[df["cluster_label"] != -1]
    singles = df[df["cluster_label"] == -1]

    shown_any = False
    for _, cluster_df in clustered.groupby("cluster_label"):
        if len(cluster_df) >= 2:
            shown_any = True
            render_cluster(cluster_df.sort_values(by="published_at", ascending=False))

    if not shown_any:
        st.info("No multi-source clusters found yet.")

    if not singles.empty:
        st.markdown("---")
        st.subheader("Other stories")
        for _, row in singles.head(10).iterrows():
            with st.expander(f"{row['title']} - {row['source']}"):
                st.write(row.get("summary") or "No summary available.")
                st.caption(f"Bias: {row.get('bias', 'unknown')}")


def ingest_page() -> None:
    st.header("Fetch latest news")
    st.write(
        "This pulls the configured RSS feeds, classifies article framing, "
        "and stores new stories without re-inserting duplicates."
    )

    if st.button("Fetch feeds", type="primary"):
        with st.spinner("Fetching feeds..."):
            raw_articles = fetch_all_feeds()
        if not raw_articles:
            st.error("No articles were fetched.")
            return

        with st.spinner("Classifying articles..."):
            enriched = enrich_articles(raw_articles)

        inserted = insert_articles(enriched)
        load_recent_stories.clear()

        st.success(f"Fetched {len(enriched)} articles. Inserted {inserted} new stories.")

        preview_cols = ["title", "source", "region", "bias", "bias_confidence"]
        preview = pd.DataFrame(enriched)[preview_cols].head(20)
        st.dataframe(preview, use_container_width=True)

        if st.session_state.get("user"):
            log_activity(st.session_state["user"], "ingest_news")


def analytics_page() -> None:
    st.header("Analytics")

    df = load_recent_stories(30)
    if df.empty:
        st.info("No analytics available yet.")
        return

    col1, col2 = st.columns(2)

    with col1:
        bias_df = df["bias"].fillna("unknown").value_counts().reset_index()
        bias_df.columns = ["bias", "count"]
        fig = px.pie(bias_df, values="count", names="bias", title="Bias distribution")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        source_df = (
            df.groupby("source", as_index=False)
            .agg(count=("id", "count"), avg_confidence=("bias_confidence", "mean"))
            .sort_values("count", ascending=False)
            .head(10)
        )
        fig = px.bar(
            source_df,
            x="source",
            y="count",
            color="avg_confidence",
            title="Most active sources",
        )
        st.plotly_chart(fig, use_container_width=True)

    series = df.copy()
    series["date"] = pd.to_datetime(series["fetched_at"]).dt.date
    times = (
        series.groupby(["date", "bias"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    fig = px.line(times, x="date", y="count", color="bias", title="Volume by bias over time")
    st.plotly_chart(fig, use_container_width=True)

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Stories", int(df["id"].count()))
    with m2:
        st.metric("Sources", int(df["source"].nunique()))
    with m3:
        st.metric("Avg confidence", f"{float(df['bias_confidence'].fillna(0).mean()):.0%}")
    with m4:
        clustered = assign_clusters(df)
        st.metric("Clustered stories", int((clustered["cluster_label"] != -1).sum()))


def settings_page() -> None:
    st.header("Settings")

    st.subheader("Environment")
    st.code(
        f"OPENAI configured: {'yes' if bool(Config.OPENAI_API_KEY) else 'no'}\n"
        f"DATABASE_URL set: {'yes' if bool(os.getenv('DATABASE_URL')) else 'no'}\n"
        f"Database dialect: {engine.dialect.name}",
        language="text",
    )

    st.subheader("Configured feeds")
    st.json(Config.FEEDS)

    st.subheader("Maintenance")
    if st.button("Delete stories older than 30 days"):
        cutoff = datetime.utcnow() - timedelta(days=30)
        with engine.begin() as conn:
            result = conn.execute(
                text("DELETE FROM stories WHERE fetched_at < :cutoff"),
                {"cutoff": cutoff},
            )
        load_recent_stories.clear()
        st.success(f"Deleted {result.rowcount or 0} rows.")


def main() -> None:
    init_session_state()

    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.5rem; padding-bottom: 2rem;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Somali News Lens")
    st.caption("AI-assisted multi-source Somali and international news analysis")

    page = render_sidebar()

    if page == "Home":
        home_page()
    elif page == "Ingest News":
        ingest_page()
    elif page == "Analytics":
        analytics_page()
    else:
        settings_page()

    st.markdown("---")
    st.caption(f"{Config.APP_NAME} v{Config.VERSION}")


if __name__ == "__main__":
    main()

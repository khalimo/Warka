import asyncio
import hashlib
import html
import json
import logging
import os
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import aiohttp
import bcrypt
import feedparser
import pandas as pd
import plotly.express as px
import streamlit as st
from dotenv import load_dotenv
from openai import APIStatusError, OpenAI, RateLimitError
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


load_dotenv()


def env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


def env_int(name: str, default: int, minimum: Optional[int] = None) -> int:
    try:
        value = int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default
    if minimum is not None:
        return max(minimum, value)
    return value


def env_float(name: str, default: float, minimum: Optional[float] = None) -> float:
    try:
        value = float(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default
    if minimum is not None:
        return max(minimum, value)
    return value


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql://" + url.removeprefix("postgres://")
    return url


class Config:
    APP_NAME = "Somali News Lens"
    VERSION = "3.1.0"

    DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///news.db"))
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_ENABLED = env_bool("OPENAI_ENABLED", True)

    SESSION_TIMEOUT_MINUTES = env_int("SESSION_TIMEOUT_MINUTES", 45, 5)
    PASSWORD_MIN_LENGTH = env_int("PASSWORD_MIN_LENGTH", 8, 8)
    MAX_LOGIN_ATTEMPTS = env_int("MAX_LOGIN_ATTEMPTS", 5, 1)
    LOCKOUT_MINUTES = env_int("LOCKOUT_MINUTES", 15, 1)

    CACHE_TTL_SECONDS = env_int("CACHE_TTL_SECONDS", 300, 30)
    MAX_ARTICLES_PER_FEED = env_int("MAX_ARTICLES_PER_FEED", 12, 1)
    FEED_TIMEOUT_SECONDS = env_int("FEED_TIMEOUT_SECONDS", 12, 3)
    MAX_AI_CLASSIFICATIONS_PER_RUN = env_int("MAX_AI_CLASSIFICATIONS_PER_RUN", 8, 0)

    CLUSTER_EPS = env_float("CLUSTER_EPS", 0.46, 0.05)
    CLUSTER_MIN_SAMPLES = env_int("CLUSTER_MIN_SAMPLES", 2, 1)

    FEEDS = [
        {"name": "BBC World", "url": "http://feeds.bbci.co.uk/news/world/rss.xml", "region": "international"},
        {"name": "Al Jazeera", "url": "https://www.aljazeera.com/xml/rss/all.xml", "region": "international"},
        {"name": "Garowe Online", "url": "https://www.garoweonline.com/en/rss", "region": "somalia"},
        {"name": "Hiiraan Online", "url": "https://www.hiiraan.com/rss.xml", "region": "somalia"},
    ]


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger("somali-news-lens")

OPENAI_QUOTA_DISABLED = False
OPENAI_CALLS_THIS_RUN = 0

st.set_page_config(
    page_title=Config.APP_NAME,
    layout="wide",
    initial_sidebar_state="expanded",
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def clean_text(value: object, max_len: int = 5000) -> str:
    text_value = re.sub(r"<[^>]+>", " ", str(value or ""))
    text_value = html.unescape(text_value)
    text_value = re.sub(r"\s+", " ", text_value).strip()
    return text_value[:max_len]


def safe_date(value: object) -> str:
    if value is None or value == "":
        return "Date unavailable"
    try:
        return pd.to_datetime(value).strftime("%d %b %Y")
    except Exception:
        return "Date unavailable"


def bias_color(bias: object) -> str:
    palette = {
        "left": "#0f766e",
        "center-left": "#2f855a",
        "center": "#475569",
        "center-right": "#b7791f",
        "right": "#b45309",
        "unknown": "#64748b",
    }
    return palette.get(str(bias or "unknown").lower(), "#64748b")


def badge(text_value: object, tone: str = "neutral") -> str:
    colors = {
        "neutral": ("#f4f6f8", "#26313d", "#d9e0e7"),
        "source": ("#eef7f4", "#17594a", "#cfe7df"),
        "region": ("#f5f2ea", "#5f4b1f", "#e5dcc6"),
        "bias": ("#f4f6f8", "#26313d", "#d9e0e7"),
        "warn": ("#fff6e8", "#7a4a00", "#f3d3a3"),
        "ok": ("#eef7f4", "#17594a", "#cfe7df"),
    }
    bg, fg, border = colors.get(tone, colors["neutral"])
    return (
        f"<span class='snl-badge' style='background:{bg};color:{fg};border-color:{border};'>"
        f"{html.escape(str(text_value or 'unknown'))}</span>"
    )


def inject_css() -> None:
    st.markdown(
        """
        <style>
        :root {
            --snl-ink: #1f2933;
            --snl-muted: #667085;
            --snl-line: #d8dee6;
            --snl-soft: #f6f8fa;
            --snl-panel: #ffffff;
            --snl-accent: #0f766e;
            --snl-accent-2: #b7791f;
        }
        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2.2rem;
            max-width: 1280px;
        }
        h1, h2, h3 {
            color: var(--snl-ink);
            letter-spacing: 0;
        }
        p, li, label, .stMarkdown {
            color: var(--snl-ink);
        }
        section[data-testid="stSidebar"] {
            background: #fbfcfd;
            border-right: 1px solid var(--snl-line);
        }
        .snl-shell {
            border: 1px solid var(--snl-line);
            background: var(--snl-panel);
            border-radius: 8px;
            padding: 18px;
            margin-bottom: 14px;
        }
        .snl-hero {
            border: 1px solid var(--snl-line);
            border-radius: 8px;
            padding: 22px;
            background: linear-gradient(180deg, #ffffff 0%, #f7faf9 100%);
            margin-bottom: 16px;
        }
        .snl-eyebrow {
            color: var(--snl-accent);
            font-weight: 700;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0;
            margin-bottom: 0.4rem;
        }
        .snl-title {
            font-size: 2.15rem;
            line-height: 1.15;
            font-weight: 780;
            color: var(--snl-ink);
            margin-bottom: 0.35rem;
        }
        .snl-subtitle {
            color: var(--snl-muted);
            font-size: 1rem;
            max-width: 860px;
            line-height: 1.55;
        }
        .snl-card {
            border: 1px solid var(--snl-line);
            background: var(--snl-panel);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .snl-card-title {
            font-weight: 760;
            font-size: 1.08rem;
            line-height: 1.35;
            color: var(--snl-ink);
            margin: 8px 0;
        }
        .snl-muted {
            color: var(--snl-muted);
            line-height: 1.5;
        }
        .snl-badge {
            display: inline-block;
            border: 1px solid;
            border-radius: 8px;
            padding: 3px 8px;
            margin: 0 4px 5px 0;
            font-size: 0.76rem;
            font-weight: 650;
            vertical-align: middle;
        }
        .snl-score {
            font-size: 1.7rem;
            font-weight: 780;
            color: var(--snl-ink);
        }
        .snl-score-label {
            color: var(--snl-muted);
            font-size: 0.82rem;
            margin-top: 2px;
        }
        .snl-source-row {
            border-top: 1px solid #edf0f3;
            padding-top: 10px;
            margin-top: 10px;
        }
        .snl-small {
            font-size: 0.84rem;
        }
        .stButton > button, .stFormSubmitButton > button {
            border-radius: 8px;
            border: 1px solid var(--snl-accent);
            background: var(--snl-accent);
            color: white;
            font-weight: 700;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            border-color: #0b5f58;
            background: #0b5f58;
            color: white;
        }
        div[data-testid="stMetric"] {
            border: 1px solid var(--snl-line);
            border-radius: 8px;
            padding: 12px;
            background: #fff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner=False)
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
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_hash ON stories(article_hash)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_source ON stories(source)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_region ON stories(region)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_fetched_at ON stories(fetched_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_bias ON stories(bias)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_cluster_label ON stories(cluster_label)"))


def database_ready() -> tuple[bool, str]:
    try:
        engine = get_engine()
        init_db(engine)
        return True, engine.dialect.name
    except Exception as exc:
        logger.exception("Database initialization failed")
        return False, f"Database is not ready: {exc.__class__.__name__}"


def hash_article(title: str, source_url: str, source: str = "") -> str:
    key = f"{clean_text(title, 500).lower()}|{clean_text(source_url, 1000).lower()}|{clean_text(source, 100).lower()}"
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def parse_feed_datetime(entry) -> Optional[datetime]:
    try:
        if getattr(entry, "published_parsed", None):
            return datetime(*entry.published_parsed[:6])
        if getattr(entry, "updated_parsed", None):
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
    if utc_now() - login_time > timedelta(minutes=Config.SESSION_TIMEOUT_MINUTES):
        logout()
        return False
    return True


def log_activity(username: str, action: str, story_id: Optional[int] = None) -> None:
    if not username:
        return
    try:
        with get_engine().begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO user_activity (username, action, story_id)
                    VALUES (:username, :action, :story_id)
                """),
                {"username": username, "action": action, "story_id": story_id},
            )
    except Exception as exc:
        logger.warning("Could not log activity: %s", exc)


def valid_username(username: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", username or ""))


def valid_password(password: str) -> tuple[bool, str]:
    if len(password or "") < Config.PASSWORD_MIN_LENGTH:
        return False, f"Password must be at least {Config.PASSWORD_MIN_LENGTH} characters."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return False, "Use at least one letter and one number."
    return True, "Password looks good."


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except Exception:
        return False


def register_user(username: str, password: str, email: Optional[str]) -> tuple[bool, str]:
    username = clean_text(username, 60).strip()
    email = clean_text(email, 254).lower() if email else None
    if not valid_username(username):
        return False, "Username must be 3-32 characters using letters, numbers, dots, dashes, or underscores."
    ok, message = valid_password(password)
    if not ok:
        return False, message
    if email and "@" not in email:
        return False, "Enter a valid email address or leave it blank."

    try:
        with get_engine().begin() as conn:
            conn.execute(
                text("""
                    INSERT INTO users (username, password_hash, email)
                    VALUES (:username, :password_hash, :email)
                """),
                {"username": username, "password_hash": hash_password(password), "email": email},
            )
        return True, "Account created. You can sign in now."
    except Exception as exc:
        logger.warning("register_user failed: %s", exc)
        return False, "Could not create account. The username or email may already exist."


def login_user(username: str, password: str) -> tuple[bool, str]:
    username = clean_text(username, 60).strip()
    if not username or not password:
        return False, "Enter your username and password."

    logged_in = False
    try:
        with get_engine().begin() as conn:
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
                    locked_dt = pd.to_datetime(locked_until).to_pydatetime().replace(tzinfo=None)
                    if locked_dt > utc_now():
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
                st.session_state["login_time"] = utc_now()
                logged_in = True
            else:
                next_attempts = int(row["login_attempts"] or 0) + 1
                lockout_until = None
                if next_attempts >= Config.MAX_LOGIN_ATTEMPTS:
                    lockout_until = utc_now() + timedelta(minutes=Config.LOCKOUT_MINUTES)

                conn.execute(
                    text("""
                        UPDATE users
                        SET login_attempts = :login_attempts,
                            locked_until = :locked_until
                        WHERE username = :username
                    """),
                    {"username": username, "login_attempts": next_attempts, "locked_until": lockout_until},
                )
                return False, "Invalid username or password."
    except Exception as exc:
        logger.warning("login_user failed: %s", exc)
        return False, "Sign-in is unavailable right now. Please try again shortly."

    if logged_in:
        log_activity(username, "login")
        return True, "Signed in."
    return False, "Invalid username or password."


@st.cache_resource(show_spinner=False)
def get_openai_client() -> Optional[OpenAI]:
    if not Config.OPENAI_ENABLED or not Config.OPENAI_API_KEY:
        return None
    return OpenAI(api_key=Config.OPENAI_API_KEY, max_retries=0)


def fallback_bias(text_input: str) -> str:
    text_lower = text_input.lower()
    left_words = {"justice", "equity", "climate", "rights", "reform", "workers", "humanitarian"}
    right_words = {"security", "military", "border", "conservative", "tradition", "terror", "sovereignty"}
    left_count = sum(1 for word in left_words if word in text_lower)
    right_count = sum(1 for word in right_words if word in text_lower)
    if left_count > right_count + 1:
        return "center-left"
    if right_count > left_count + 1:
        return "center-right"
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


def classify_bias_with_ai(text_input: str) -> tuple[str, float, str]:
    global OPENAI_QUOTA_DISABLED, OPENAI_CALLS_THIS_RUN
    if OPENAI_QUOTA_DISABLED or OPENAI_CALLS_THIS_RUN >= Config.MAX_AI_CLASSIFICATIONS_PER_RUN:
        return fallback_bias(text_input), 0.45, "fallback"

    client = get_openai_client()
    if client is None:
        return fallback_bias(text_input), 0.45, "fallback"

    prompt = (
        "Classify the political or editorial framing of this news text. "
        "Return strict JSON only with keys bias and confidence. "
        "Allowed bias values: left, center-left, center, center-right, right. "
        f"Text: {text_input[:1200]}"
    )

    try:
        OPENAI_CALLS_THIS_RUN += 1
        response = client.responses.create(model=Config.OPENAI_MODEL, input=prompt, max_output_tokens=120)
        parsed = parse_ai_json(getattr(response, "output_text", "") or "")
        bias = str(parsed.get("bias", "center")).lower()
        if bias not in {"left", "center-left", "center", "center-right", "right"}:
            bias = "center"
        confidence = max(0.0, min(float(parsed.get("confidence", 0.5)), 1.0))
        return bias, confidence, "openai"
    except (RateLimitError, APIStatusError) as exc:
        OPENAI_QUOTA_DISABLED = True
        logger.warning("OpenAI unavailable; using fallback classifier: %s", exc)
        return fallback_bias(text_input), 0.45, "fallback"
    except Exception as exc:
        logger.warning("AI bias classification failed: %s", exc)
        return fallback_bias(text_input), 0.45, "fallback"


def summarize_cluster_with_ai(items: list[dict]) -> str:
    global OPENAI_QUOTA_DISABLED
    if OPENAI_QUOTA_DISABLED:
        return "Coverage appears to describe the same developing story. Compare source summaries below for framing differences."

    client = get_openai_client()
    if client is None:
        return "Coverage appears to describe the same developing story. Compare source summaries below for framing differences."

    joined = "\n\n".join(
        f"Source: {item['source']}\nTitle: {item['title']}\nSummary: {item.get('summary') or ''}"
        for item in items[:4]
    )
    prompt = (
        "Summarize the shared core story across these reports in 2 neutral sentences. "
        "Focus on facts common across sources.\n\n"
        f"{joined[:3000]}"
    )

    try:
        response = client.responses.create(model=Config.OPENAI_MODEL, input=prompt, max_output_tokens=160)
        return (getattr(response, "output_text", "") or "").strip() or "No summary available."
    except (RateLimitError, APIStatusError) as exc:
        OPENAI_QUOTA_DISABLED = True
        logger.warning("OpenAI unavailable; using fallback cluster summary: %s", exc)
    except Exception as exc:
        logger.warning("Cluster summary failed: %s", exc)
    return "Coverage appears to describe the same developing story. Compare source summaries below for framing differences."


async def fetch_single_feed(session: aiohttp.ClientSession, feed_def: dict) -> tuple[str, list[dict], Optional[str]]:
    try:
        async with session.get(feed_def["url"], timeout=aiohttp.ClientTimeout(total=Config.FEED_TIMEOUT_SECONDS)) as resp:
            if resp.status >= 400:
                return feed_def["name"], [], f"HTTP {resp.status}"
            body = await resp.text()
            parsed = feedparser.parse(body)

        articles = []
        for entry in parsed.entries[: Config.MAX_ARTICLES_PER_FEED]:
            title = clean_text(entry.get("title", ""), 300) or "Untitled"
            source_url = clean_text(entry.get("link", ""), 1000)
            if not title and not source_url:
                continue
            summary = clean_text(entry.get("summary", ""), 1200)
            content = ""
            if entry.get("content"):
                try:
                    content = clean_text(entry["content"][0].get("value", ""), 2500)
                except Exception:
                    content = ""

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
                    "fetched_at": utc_now(),
                    "article_hash": hash_article(title, source_url, feed_def["name"]),
                }
            )
        return feed_def["name"], articles, None
    except Exception as exc:
        logger.warning("Feed fetch failed for %s: %s", feed_def["name"], exc)
        return feed_def["name"], [], str(exc.__class__.__name__)


async def fetch_all_feeds_async() -> tuple[list[dict], list[str]]:
    async with aiohttp.ClientSession(headers={"User-Agent": f"{Config.APP_NAME}/{Config.VERSION}"}) as session:
        results = await asyncio.gather(*(fetch_single_feed(session, feed_def) for feed_def in Config.FEEDS))
    articles = []
    warnings = []
    for source, rows, error in results:
        articles.extend(rows)
        if error:
            warnings.append(f"{source}: {error}")
    return articles, warnings


def fetch_all_feeds() -> tuple[list[dict], list[str]]:
    try:
        return asyncio.run(fetch_all_feeds_async())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(fetch_all_feeds_async())
        finally:
            loop.close()
    except Exception as exc:
        logger.warning("Feed fetch orchestration failed: %s", exc)
        return [], [str(exc.__class__.__name__)]


def enrich_articles(articles: list[dict]) -> tuple[list[dict], dict]:
    stats = {"openai": 0, "fallback": 0}
    enriched = []
    for article in articles:
        text_input = f"{article['title']}\n{article.get('summary', '')}"
        bias, confidence, mode = classify_bias_with_ai(text_input)
        article["bias"] = bias
        article["bias_confidence"] = confidence
        stats[mode] = stats.get(mode, 0) + 1
        enriched.append(article)
    return enriched, stats


def insert_articles(articles: list[dict]) -> int:
    if not articles:
        return 0
    engine = get_engine()
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
                    "fetched_at": article.get("fetched_at", utc_now()),
                    "bias": article.get("bias"),
                    "bias_confidence": article.get("bias_confidence"),
                    "ai_summary": None,
                    "cluster_label": None,
                },
            )
            if result.rowcount and result.rowcount > 0:
                inserted += 1
    return inserted


@st.cache_data(ttl=Config.CACHE_TTL_SECONDS, show_spinner=False)
def load_recent_stories(days: int = 7) -> pd.DataFrame:
    query = text("""
        SELECT *
        FROM stories
        WHERE fetched_at >= :cutoff
        ORDER BY COALESCE(published_at, fetched_at) DESC
    """)
    cutoff = utc_now() - timedelta(days=days)
    with get_engine().begin() as conn:
        return pd.read_sql(query, conn, params={"cutoff": cutoff})


def assign_clusters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    required = {"title", "summary"}
    if not required.issubset(df.columns):
        out = df.copy()
        out["cluster_label"] = -1
        return out

    texts = (df["title"].fillna("") + " " + df["summary"].fillna("")).tolist()
    if len(texts) < 2:
        out = df.copy()
        out["cluster_label"] = [0]
        return out

    try:
        matrix = TfidfVectorizer(max_features=1500, stop_words="english", ngram_range=(1, 2)).fit_transform(texts)
        labels = DBSCAN(
            eps=Config.CLUSTER_EPS,
            min_samples=Config.CLUSTER_MIN_SAMPLES,
            metric="cosine",
        ).fit_predict(matrix)
    except Exception as exc:
        logger.warning("Clustering failed: %s", exc)
        labels = [-1] * len(texts)

    out = df.copy()
    out["cluster_label"] = labels
    return out


def persist_cluster_labels(df: pd.DataFrame) -> None:
    if df.empty or "id" not in df.columns or "cluster_label" not in df.columns:
        return
    try:
        with get_engine().begin() as conn:
            for _, row in df[["id", "cluster_label"]].iterrows():
                conn.execute(
                    text("UPDATE stories SET cluster_label = :cluster_label WHERE id = :id"),
                    {"id": int(row["id"]), "cluster_label": int(row["cluster_label"])},
                )
    except Exception as exc:
        logger.warning("Could not persist cluster labels: %s", exc)


def render_header() -> None:
    ai_mode = "AI enabled" if Config.OPENAI_ENABLED and Config.OPENAI_API_KEY and not OPENAI_QUOTA_DISABLED else "Fallback mode"
    st.markdown(
        f"""
        <div class="snl-hero">
          <div class="snl-eyebrow">Multi-source news intelligence</div>
          <div class="snl-title">{Config.APP_NAME}</div>
          <div class="snl-subtitle">
            Compare Somali and international coverage across sources, regions, framing signals, and story clusters.
            Built for fast editorial review on Render's free tier.
          </div>
          <div style="margin-top:14px;">
            {badge(ai_mode, "ok" if ai_mode == "AI enabled" else "warn")}
            {badge("Postgres-ready", "ok")}
            {badge(f"{len(Config.FEEDS)} monitored feeds", "source")}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> str:
    with st.sidebar:
        st.markdown("### Somali News Lens")
        page = st.radio(
            "Workspace",
            ["Dashboard", "Ingest", "Analytics", "Account", "Operations"],
            label_visibility="collapsed",
        )
        st.caption("Editorial comparison dashboard")
        st.divider()

        if session_active():
            st.success(f"Signed in as {st.session_state['user']}")
            if st.button("Sign out", use_container_width=True):
                logout()
                st.rerun()
        else:
            st.info("Sign in from Account to track activity.")

        st.divider()
        st.caption(f"Version {Config.VERSION}")
        return page


def metric_card(label: str, value: object, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="snl-card">
          <div class="snl-score">{html.escape(str(value))}</div>
          <div class="snl-score-label">{html.escape(label)}</div>
          <div class="snl-muted snl-small">{html.escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_story_card(row: pd.Series) -> None:
    confidence = float(row.get("bias_confidence") or 0)
    bias = row.get("bias") or "unknown"
    title = html.escape(str(row.get("title") or "Untitled"))
    summary = html.escape(clean_text(row.get("summary") or "No summary available.", 380))
    source_url = row.get("source_url") or ""
    link = f"<a href='{html.escape(source_url)}' target='_blank'>Read source</a>" if source_url else ""
    st.markdown(
        f"""
        <div class="snl-card">
          <div>
            {badge(row.get("source"), "source")}
            {badge(row.get("region"), "region")}
            <span class="snl-badge" style="background:#fff;color:{bias_color(bias)};border-color:{bias_color(bias)};">
              {html.escape(str(bias))} · {confidence:.0%}
            </span>
          </div>
          <div class="snl-card-title">{title}</div>
          <div class="snl-muted">{summary}</div>
          <div class="snl-muted snl-small" style="margin-top:10px;">{safe_date(row.get("published_at") or row.get("fetched_at"))} {link}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cluster(cluster_df: pd.DataFrame) -> None:
    items = cluster_df.to_dict(orient="records")
    first = cluster_df.iloc[0]
    bias_counts = cluster_df["bias"].fillna("unknown").value_counts()
    source_count = cluster_df["source"].nunique()
    confidence = float(cluster_df["bias_confidence"].fillna(0).mean())
    title = html.escape(str(first.get("title") or "Untitled story"))

    with st.container():
        st.markdown(
            f"""
            <div class="snl-shell">
              <div>{badge(f"{source_count} sources", "source")}{badge(first.get("region"), "region")}{badge(f"avg confidence {confidence:.0%}", "neutral")}</div>
              <div class="snl-card-title" style="font-size:1.25rem;">{title}</div>
              <div class="snl-muted">{html.escape(summarize_cluster_with_ai(items))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        col_a, col_b = st.columns([2.2, 1])
        with col_a:
            for _, row in cluster_df.head(4).iterrows():
                render_story_card(row)
        with col_b:
            st.markdown("**Framing mix**")
            st.bar_chart(bias_counts, use_container_width=True)
            st.markdown("**Source list**")
            for source in cluster_df["source"].dropna().unique():
                st.markdown(badge(source, "source"), unsafe_allow_html=True)


def dashboard_page() -> None:
    st.markdown("## Top Stories")
    col_filter, col_region = st.columns([1, 1])
    with col_filter:
        days = st.slider("Coverage window", 1, 30, 7, help="How many days of stored stories to review.")
    with col_region:
        region = st.selectbox("Region", ["All", "somalia", "international"])

    try:
        df = load_recent_stories(days)
    except Exception as exc:
        logger.warning("Could not load stories: %s", exc)
        st.error("The story database is unavailable right now. Check DATABASE_URL and redeploy.")
        return

    if region != "All" and not df.empty:
        df = df[df["region"] == region]

    if df.empty:
        st.markdown(
            """
            <div class="snl-shell">
              <div class="snl-card-title">No coverage yet</div>
              <div class="snl-muted">Start with Ingest to fetch stories. The dashboard will group related coverage once enough articles are stored.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    clustered_df = assign_clusters(df)
    persist_cluster_labels(clustered_df)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Stories", len(clustered_df), "Stored in current window")
    with c2:
        metric_card("Sources", clustered_df["source"].nunique(), "Distinct publishers")
    with c3:
        metric_card("Regions", clustered_df["region"].nunique(), "Coverage areas")
    with c4:
        metric_card("Clustered", int((clustered_df["cluster_label"] != -1).sum()), "Stories in story groups")

    clusters = clustered_df[clustered_df["cluster_label"] != -1]
    singles = clustered_df[clustered_df["cluster_label"] == -1]

    st.markdown("### Multi-source comparisons")
    rendered = False
    for _, cluster in clusters.groupby("cluster_label"):
        if len(cluster) >= 2:
            rendered = True
            render_cluster(cluster.sort_values(by="published_at", ascending=False, na_position="last"))

    if not rendered:
        st.info("No multi-source clusters yet. Ingest more feeds or widen the coverage window.")

    if not singles.empty:
        st.markdown("### Additional single-source stories")
        cols = st.columns(2)
        for idx, (_, row) in enumerate(singles.head(8).iterrows()):
            with cols[idx % 2]:
                render_story_card(row)


def ingest_page() -> None:
    st.markdown("## Ingest News")
    st.markdown(
        """
        <div class="snl-shell">
          <div class="snl-card-title">Fetch, classify, deduplicate</div>
          <div class="snl-muted">Pulls configured RSS feeds, applies OpenAI classification when available, and falls back automatically when the key is missing or quota-limited.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        metric_card("Configured feeds", len(Config.FEEDS), "RSS sources")
    with col_b:
        ai_state = "OpenAI" if Config.OPENAI_ENABLED and Config.OPENAI_API_KEY else "Fallback"
        metric_card("Classification", ai_state, "Current mode")
    with col_c:
        metric_card("Max per feed", Config.MAX_ARTICLES_PER_FEED, "Free-tier friendly")

    if st.button("Fetch latest coverage", type="primary", use_container_width=True):
        with st.spinner("Fetching feeds..."):
            raw_articles, warnings = fetch_all_feeds()

        for warning in warnings:
            st.warning(f"Feed warning: {warning}")

        if not raw_articles:
            st.error("No articles were fetched. Try again later or check feed availability.")
            return

        with st.spinner("Classifying and preparing stories..."):
            enriched, stats = enrich_articles(raw_articles)

        try:
            inserted = insert_articles(enriched)
            load_recent_stories.clear()
        except Exception as exc:
            logger.exception("Insert failed")
            st.error("Stories were fetched but could not be saved. Check DATABASE_URL and database permissions.")
            st.caption(exc.__class__.__name__)
            return

        st.success(f"Fetched {len(enriched)} articles and inserted {inserted} new stories.")
        if stats.get("fallback", 0):
            st.info(f"{stats.get('fallback', 0)} stories used fallback classification.")
        if stats.get("openai", 0):
            st.info(f"{stats.get('openai', 0)} stories used OpenAI classification.")

        preview_cols = ["title", "source", "region", "bias", "bias_confidence"]
        st.dataframe(pd.DataFrame(enriched)[preview_cols].head(30), use_container_width=True)

        if st.session_state.get("user"):
            log_activity(st.session_state["user"], "ingest_news")


def analytics_page() -> None:
    st.markdown("## Analytics")
    try:
        df = load_recent_stories(30)
    except Exception as exc:
        logger.warning("Analytics load failed: %s", exc)
        st.error("Analytics are unavailable until the database is reachable.")
        return

    if df.empty:
        st.info("No analytics yet. Ingest news to populate charts.")
        return

    clustered = assign_clusters(df)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Stories", int(df["id"].count()))
    with c2:
        st.metric("Sources", int(df["source"].nunique()))
    with c3:
        st.metric("Avg confidence", f"{float(df['bias_confidence'].fillna(0).mean()):.0%}")
    with c4:
        st.metric("Clustered stories", int((clustered["cluster_label"] != -1).sum()))

    col1, col2 = st.columns(2)
    with col1:
        bias_df = df["bias"].fillna("unknown").value_counts().reset_index()
        bias_df.columns = ["bias", "count"]
        fig = px.bar(bias_df, x="bias", y="count", title="Framing distribution", color="bias")
        fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        source_df = (
            df.groupby("source", as_index=False)
            .agg(count=("id", "count"), avg_confidence=("bias_confidence", "mean"))
            .sort_values("count", ascending=False)
            .head(10)
        )
        fig = px.bar(source_df, x="source", y="count", color="avg_confidence", title="Most active sources")
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    series = df.copy()
    series["date"] = pd.to_datetime(series["fetched_at"], errors="coerce").dt.date
    times = series.dropna(subset=["date"]).groupby(["date", "bias"], as_index=False).size().rename(columns={"size": "count"})
    if not times.empty:
        fig = px.line(times, x="date", y="count", color="bias", title="Coverage volume by framing")
        fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)


def account_page() -> None:
    st.markdown("## Account")
    left, right = st.columns(2)

    with left:
        st.markdown("### Sign in")
        if session_active():
            st.success(f"You are signed in as {st.session_state['user']}.")
            if st.button("Sign out", use_container_width=True):
                logout()
                st.rerun()
        else:
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Sign in", use_container_width=True)
                if submit:
                    ok, msg = login_user(username, password)
                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    with right:
        st.markdown("### Create account")
        with st.form("register_form"):
            new_user = st.text_input("Username", help="3-32 characters. Letters, numbers, dots, dashes, and underscores.")
            new_email = st.text_input("Email optional")
            new_password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            create = st.form_submit_button("Create account", use_container_width=True)
            if create:
                if new_password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(new_user, new_password, new_email)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)


def operations_page(db_label: str) -> None:
    st.markdown("## Operations")
    st.markdown(
        """
        <div class="snl-shell">
          <div class="snl-card-title">Deployment readiness</div>
          <div class="snl-muted">No secrets are displayed here. Use Render environment variables for credentials and database URLs.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Database", db_label, "Current SQL dialect")
    with c2:
        metric_card("OpenAI key", "set" if bool(Config.OPENAI_API_KEY) else "missing", "Fallback works without it")
    with c3:
        metric_card("Runtime", "Python 3.11", "Pinned for Render")

    with st.expander("Configured feeds"):
        st.dataframe(pd.DataFrame(Config.FEEDS), use_container_width=True)

    st.markdown("### Maintenance")
    if st.button("Delete stories older than 30 days"):
        try:
            cutoff = utc_now() - timedelta(days=30)
            with get_engine().begin() as conn:
                result = conn.execute(text("DELETE FROM stories WHERE fetched_at < :cutoff"), {"cutoff": cutoff})
            load_recent_stories.clear()
            st.success(f"Deleted {result.rowcount or 0} old rows.")
        except Exception as exc:
            logger.warning("Maintenance cleanup failed: %s", exc)
            st.error("Cleanup failed. Check database connectivity.")


def main() -> None:
    inject_css()
    init_session_state()
    ready, db_label = database_ready()
    render_header()

    if not ready:
        st.error(db_label)
        st.info("Check DATABASE_URL in Render. The app did not expose secrets or stack traces.")
        return

    page = render_sidebar()
    if page == "Dashboard":
        dashboard_page()
    elif page == "Ingest":
        ingest_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Account":
        account_page()
    else:
        operations_page(db_label)

    st.caption(f"{Config.APP_NAME} v{Config.VERSION}")


if __name__ == "__main__":
    main()

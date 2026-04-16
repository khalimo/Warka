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
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from sources import NEWS_SOURCES, SOURCE_BY_NAME


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
    VERSION = "4.1.0"

    DATABASE_URL = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///news.db"))
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_ENABLED = env_bool("OPENAI_ENABLED", True)

    SESSION_TIMEOUT_MINUTES = env_int("SESSION_TIMEOUT_MINUTES", 45, 5)
    PASSWORD_MIN_LENGTH = env_int("PASSWORD_MIN_LENGTH", 8, 8)
    MAX_LOGIN_ATTEMPTS = env_int("MAX_LOGIN_ATTEMPTS", 5, 1)
    LOCKOUT_MINUTES = env_int("LOCKOUT_MINUTES", 15, 1)

    CACHE_TTL_SECONDS = env_int("CACHE_TTL_SECONDS", 300, 30)
    MAX_ARTICLES_PER_FEED = env_int("MAX_ARTICLES_PER_FEED", 16, 1)
    MAX_FEEDS_PER_RUN = min(env_int("MAX_FEEDS_PER_RUN", len(NEWS_SOURCES), 1), len(NEWS_SOURCES))
    FEED_CONCURRENCY = env_int("FEED_CONCURRENCY", 6, 1)
    FEED_TIMEOUT_SECONDS = env_int("FEED_TIMEOUT_SECONDS", 12, 3)
    MAX_AI_CLASSIFICATIONS_PER_RUN = env_int("MAX_AI_CLASSIFICATIONS_PER_RUN", 8, 0)
    READER_LOOKBACK_DAYS = env_int("READER_LOOKBACK_DAYS", 60, 7)
    READER_LATEST_LIMIT = env_int("READER_LATEST_LIMIT", 90, 12)
    READER_SECTION_LIMIT = env_int("READER_SECTION_LIMIT", 72, 12)
    EDITOR_INVITE_CODE = os.getenv("EDITOR_INVITE_CODE", "").strip()

    CLUSTER_EPS = env_float("CLUSTER_EPS", 0.46, 0.05)
    CLUSTER_MIN_SAMPLES = env_int("CLUSTER_MIN_SAMPLES", 2, 1)

    FEEDS = NEWS_SOURCES[:MAX_FEEDS_PER_RUN]


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


def inject_css(mode: str = "Reader Mode") -> None:
    sidebar_rule = (
        "section[data-testid=\"stSidebar\"] {display:none;}"
        if mode == "Reader Mode"
        else "section[data-testid=\"stSidebar\"] {background:#fbfcfd;border-right:1px solid var(--snl-line);}"
    )
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
        """
        + sidebar_rule
        + """
        h1, h2, h3 {
            color: var(--snl-ink);
            letter-spacing: 0;
        }
        p, li, label, .stMarkdown {
            color: var(--snl-ink);
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
        .public-masthead {
            display: flex;
            justify-content: space-between;
            gap: 18px;
            align-items: flex-end;
            border-bottom: 2px solid #1f2933;
            padding: 10px 0 14px 0;
            margin-bottom: 12px;
        }
        .public-brand {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 2.45rem;
            font-weight: 700;
            color: var(--snl-ink);
            line-height: 1;
        }
        .brand-kicker, .section-kicker {
            color: var(--snl-accent);
            font-size: 0.78rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0;
        }
        .masthead-note {
            max-width: 360px;
            color: var(--snl-muted);
            font-size: 0.9rem;
            text-align: right;
        }
        .section-heading {
            border-top: 1px solid var(--snl-line);
            padding-top: 18px;
            margin: 24px 0 12px 0;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.65rem;
            font-weight: 700;
            color: var(--snl-ink);
        }
        .reader-intro {
            color: var(--snl-muted);
            font-size: 1rem;
            max-width: 760px;
        }
        .article-card {
            border-top: 1px solid var(--snl-line);
            padding: 14px 0 16px 0;
            min-height: 150px;
        }
        .article-card-hero {
            border: 1px solid var(--snl-line);
            border-radius: 8px;
            padding: 22px;
            background: #ffffff;
            min-height: 360px;
        }
        .article-card h2 {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.35rem;
            line-height: 1.2;
            margin: 8px 0;
        }
        .article-card-hero h2 {
            font-size: 2.35rem;
        }
        .article-card p,
        .compare-card p,
        .source-perspective p,
        .about-panel p {
            color: var(--snl-muted);
            line-height: 1.55;
            margin-bottom: 8px;
        }
        .article-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 4px;
            align-items: center;
        }
        .article-footer {
            margin-top: 12px;
        }
        .story-link {
            color: var(--snl-accent);
            font-weight: 700;
            text-decoration: none;
        }
        .compact-story {
            border-top: 1px solid var(--snl-line);
            padding: 12px 0;
        }
        .compact-title {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.05rem;
            font-weight: 700;
            line-height: 1.25;
            color: var(--snl-ink);
            margin-bottom: 6px;
        }
        .rail-title {
            font-weight: 800;
            color: var(--snl-ink);
            margin-bottom: 4px;
        }
        .compare-card {
            border: 1px solid var(--snl-line);
            border-radius: 8px;
            padding: 18px;
            margin: 14px 0 10px 0;
            background: #fbfcfd;
        }
        .compare-card h3 {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.45rem;
            margin: 6px 0;
        }
        .source-perspective {
            border: 1px solid var(--snl-line);
            border-radius: 8px;
            padding: 14px;
            background: #ffffff;
            min-height: 210px;
            margin-bottom: 12px;
        }
        .perspective-title {
            font-weight: 750;
            line-height: 1.3;
            margin: 8px 0;
            color: var(--snl-ink);
        }
        .reader-empty, .about-panel, .insights-header {
            border: 1px solid var(--snl-line);
            border-radius: 8px;
            padding: 20px;
            background: #ffffff;
            margin: 12px 0;
        }
        .empty-title {
            font-family: Georgia, "Times New Roman", serif;
            font-weight: 700;
            font-size: 1.35rem;
            color: var(--snl-ink);
            margin-bottom: 6px;
        }
        .public-footer {
            border-top: 1px solid var(--snl-line);
            margin-top: 28px;
            padding-top: 14px;
            color: var(--snl-muted);
            display: flex;
            justify-content: space-between;
            gap: 16px;
            font-size: 0.88rem;
        }
        .insights-header h1 {
            font-size: 1.8rem;
            margin: 6px 0;
        }
        @media (max-width: 760px) {
            .public-masthead, .public-footer {
                display: block;
            }
            .masthead-note {
                text-align: left;
                margin-top: 8px;
            }
            .public-brand {
                font-size: 1.9rem;
            }
            .article-card-hero h2 {
                font-size: 1.75rem;
            }
        }
        .block-container {
            max-width: 1360px;
            padding-top: 0.9rem;
            background: #fcfdfc;
        }
        .public-masthead {
            align-items: center;
            border-bottom: 1px solid #111827;
            border-top: 4px solid #111827;
            padding: 18px 0 16px 0;
            margin-bottom: 10px;
        }
        .public-brand {
            font-size: 3.05rem;
            letter-spacing: 0;
        }
        .brand-kicker, .section-kicker {
            color: #0d6b63;
        }
        .reader-edition-strip {
            display: flex;
            justify-content: space-between;
            gap: 16px;
            align-items: center;
            border-bottom: 1px solid var(--snl-line);
            padding: 8px 0 14px 0;
            margin-bottom: 10px;
            color: var(--snl-muted);
            font-size: 0.9rem;
        }
        .reader-nav-note {
            color: var(--snl-muted);
            font-size: 0.9rem;
            margin: 8px 0 18px 0;
        }
        div[role="radiogroup"] {
            gap: 0.35rem;
        }
        div[role="radiogroup"] label {
            border: 1px solid var(--snl-line);
            border-radius: 8px;
            padding: 0.36rem 0.62rem;
            background: #ffffff;
        }
        .reader-trust-bar {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin: 14px 0 22px 0;
        }
        .trust-item {
            border-top: 2px solid #111827;
            background: #ffffff;
            padding: 12px 0 4px 0;
        }
        .trust-number {
            font-family: Georgia, "Times New Roman", serif;
            color: #111827;
            font-size: 1.7rem;
            font-weight: 760;
        }
        .trust-label {
            color: var(--snl-muted);
            font-size: 0.9rem;
            line-height: 1.35;
        }
        .front-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.65fr) minmax(320px, 0.9fr);
            gap: 20px;
            align-items: stretch;
            margin-top: 8px;
        }
        .article-card {
            border: 0;
            border-top: 1px solid var(--snl-line);
            background: transparent;
            border-radius: 0;
            padding: 16px 0 18px 0;
            margin-bottom: 0;
            min-height: 0;
        }
        .article-card-hero {
            display: grid;
            grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);
            gap: 22px;
            align-items: stretch;
            border: 1px solid #111827;
            border-radius: 8px;
            padding: 18px;
            background: #ffffff;
            min-height: 440px;
        }
        .article-card-feature {
            border: 1px solid var(--snl-line);
            border-radius: 8px;
            background: #ffffff;
            padding: 12px;
            min-height: 360px;
        }
        .article-card-list {
            display: grid;
            grid-template-columns: 132px minmax(0, 1fr);
            gap: 14px;
            align-items: start;
        }
        .story-visual {
            position: relative;
            overflow: hidden;
            border-radius: 8px;
            background: #eaf3f1;
            min-height: 155px;
            border: 1px solid #d7e4e1;
        }
        .story-visual img {
            width: 100%;
            height: 100%;
            min-height: 155px;
            object-fit: cover;
            display: block;
        }
        .story-visual-hero {
            min-height: 398px;
        }
        .story-visual-hero img {
            min-height: 398px;
        }
        .story-visual-list {
            min-height: 96px;
        }
        .story-visual-list img {
            min-height: 96px;
        }
        .story-visual-list .story-visual-placeholder {
            font-size: 0.95rem;
        }
        .story-visual-placeholder {
            height: 100%;
            min-height: inherit;
            display: flex;
            align-items: end;
            padding: 14px;
            background:
                linear-gradient(135deg, rgba(15, 118, 110, 0.16), rgba(183, 121, 31, 0.12)),
                repeating-linear-gradient(45deg, rgba(17, 24, 39, 0.06) 0, rgba(17, 24, 39, 0.06) 1px, transparent 1px, transparent 10px);
            color: #111827;
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.45rem;
            font-weight: 760;
        }
        .article-card h2 {
            font-family: Georgia, "Times New Roman", serif;
            font-size: 1.42rem;
            line-height: 1.15;
            margin: 10px 0 7px 0;
        }
        .article-card-hero h2 {
            font-size: 2.85rem;
            line-height: 1.04;
            margin-top: 12px;
        }
        .article-card-feature h2 {
            font-size: 1.42rem;
        }
        .article-card-list h2 {
            font-size: 1.16rem;
        }
        .article-card p {
            font-size: 0.98rem;
            color: #4b5563;
        }
        .article-card-hero p {
            font-size: 1.08rem;
        }
        .snl-badge {
            border-radius: 6px;
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0;
            padding: 3px 7px;
        }
        .section-heading {
            border-top: 2px solid #111827;
            padding-top: 14px;
            margin-top: 30px;
            display: flex;
            justify-content: space-between;
            align-items: baseline;
        }
        .section-deck {
            color: var(--snl-muted);
            max-width: 760px;
            margin: -5px 0 12px 0;
            line-height: 1.5;
        }
        .latest-stream {
            border-top: 1px solid var(--snl-line);
        }
        .compare-card {
            border: 1px solid #111827;
            background: #ffffff;
            padding: 20px;
        }
        .compare-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin: 14px 0;
        }
        .compare-lens {
            background: #f7faf9;
            border: 1px solid #d7e4e1;
            border-radius: 8px;
            padding: 12px;
            min-height: 112px;
        }
        .compare-lens-title {
            color: #0d6b63;
            font-weight: 800;
            margin-bottom: 5px;
            text-transform: uppercase;
            font-size: 0.76rem;
        }
        .source-perspective {
            border-color: #d8dee6;
            box-shadow: 0 8px 20px rgba(17, 24, 39, 0.04);
        }
        .insights-header {
            border-top: 4px solid #111827;
        }
        .source-summary-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 10px;
            margin-bottom: 12px;
        }
        .public-footer {
            border-top: 2px solid #111827;
            padding-top: 18px;
            margin-top: 34px;
        }
        @media (max-width: 900px) {
            .front-grid,
            .article-card-hero,
            .compare-grid,
            .reader-trust-bar,
            .source-summary-grid {
                display: block;
            }
            .article-card-list {
                grid-template-columns: 104px minmax(0, 1fr);
            }
            .story-visual-hero,
            .story-visual-hero img {
                min-height: 240px;
            }
            .article-card-hero h2 {
                font-size: 2rem;
            }
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
                image_url TEXT,
                source TEXT NOT NULL,
                source_url TEXT,
                region TEXT,
                section TEXT DEFAULT 'Somalia',
                source_category TEXT,
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
        existing_columns = {column["name"] for column in inspect(conn).get_columns("stories")}
        for column_name, column_sql in {
            "section": "section TEXT DEFAULT 'Somalia'",
            "source_category": "source_category TEXT",
            "image_url": "image_url TEXT",
        }.items():
            if column_name not in existing_columns:
                conn.execute(text(f"ALTER TABLE stories ADD COLUMN {column_sql}"))

        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_hash ON stories(article_hash)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_source ON stories(source)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_region ON stories(region)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_stories_section ON stories(section)"))
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


def extract_entry_image(entry) -> str:
    candidates = []
    for key in ("media_thumbnail", "media_content"):
        values = entry.get(key) or []
        if isinstance(values, list):
            candidates.extend(item.get("url") for item in values if isinstance(item, dict))

    for link in entry.get("links", []) or []:
        href = link.get("href") if isinstance(link, dict) else ""
        content_type = str(link.get("type", "")) if isinstance(link, dict) else ""
        if href and content_type.startswith("image/"):
            candidates.append(href)

    for field in ("summary", "description"):
        match = re.search(r"<img[^>]+src=[\"']([^\"']+)", str(entry.get(field, "")), flags=re.IGNORECASE)
        if match:
            candidates.append(match.group(1))

    if entry.get("content"):
        for content_item in entry.get("content", []) or []:
            value = content_item.get("value", "") if isinstance(content_item, dict) else ""
            match = re.search(r"<img[^>]+src=[\"']([^\"']+)", value, flags=re.IGNORECASE)
            if match:
                candidates.append(match.group(1))

    for candidate in candidates:
        image_url = clean_text(candidate, 1000)
        if image_url.startswith(("http://", "https://")):
            return image_url
    return ""


def init_session_state() -> None:
    st.session_state.setdefault("user", None)
    st.session_state.setdefault("login_time", None)
    st.session_state.setdefault("source_status", {})


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


def register_user(username: str, password: str, email: Optional[str], invite_code: str = "") -> tuple[bool, str]:
    username = clean_text(username, 60).strip()
    email = clean_text(email, 254).lower() if email else None
    if Config.EDITOR_INVITE_CODE and invite_code.strip() != Config.EDITOR_INVITE_CODE:
        return False, "Enter the editor invite code to create an account."
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


async def fetch_single_feed(session: aiohttp.ClientSession, feed_def: dict) -> tuple[list[dict], dict]:
    status = {
        "name": feed_def["name"],
        "url": feed_def["url"],
        "region": feed_def.get("region", "unknown"),
        "section": feed_def.get("section", "Somalia"),
        "category": feed_def.get("category", "News"),
        "status": "failed",
        "item_count": 0,
        "error": "",
        "checked_at": utc_now(),
    }
    try:
        async with session.get(feed_def["url"], timeout=aiohttp.ClientTimeout(total=Config.FEED_TIMEOUT_SECONDS)) as resp:
            if resp.status >= 400:
                status["error"] = f"HTTP {resp.status}"
                return [], status
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
                    "image_url": extract_entry_image(entry),
                    "source": feed_def["name"],
                    "source_url": source_url,
                    "region": feed_def.get("region", "unknown"),
                    "section": feed_def.get("section", "Somalia"),
                    "source_category": feed_def.get("category", "News"),
                    "language": feed_def.get("language", "en"),
                    "published_at": parse_feed_datetime(entry),
                    "fetched_at": utc_now(),
                    "article_hash": hash_article(title, source_url, feed_def["name"]),
                }
            )
        status["status"] = "healthy" if articles else "warning"
        status["item_count"] = len(articles)
        if not articles:
            status["error"] = "No parseable entries"
        return articles, status
    except Exception as exc:
        logger.warning("Feed fetch failed for %s: %s", feed_def["name"], exc)
        status["error"] = str(exc.__class__.__name__)
        return [], status


async def fetch_all_feeds_async() -> tuple[list[dict], list[dict]]:
    semaphore = asyncio.Semaphore(Config.FEED_CONCURRENCY)

    async def guarded_fetch(feed_def: dict) -> tuple[list[dict], dict]:
        async with semaphore:
            return await fetch_single_feed(session, feed_def)

    async with aiohttp.ClientSession(headers={"User-Agent": f"{Config.APP_NAME}/{Config.VERSION}"}) as session:
        results = await asyncio.gather(*(guarded_fetch(feed_def) for feed_def in Config.FEEDS))
    articles = []
    statuses = []
    for rows, status in results:
        articles.extend(rows)
        statuses.append(status)
    return articles, statuses


def fetch_all_feeds() -> tuple[list[dict], list[dict]]:
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
        return [], [
            {
                "name": "Feed runner",
                "url": "",
                "region": "system",
                "section": "Operations",
                "category": "System",
                "status": "failed",
                "item_count": 0,
                "error": str(exc.__class__.__name__),
                "checked_at": utc_now(),
            }
        ]


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
                image_url, source, source_url, region, section, source_category, language,
                published_at, fetched_at, bias, bias_confidence, ai_summary, cluster_label
            )
            VALUES (
                :article_hash, :title, :summary, :content,
                :image_url, :source, :source_url, :region, :section, :source_category, :language,
                :published_at, :fetched_at, :bias, :bias_confidence, :ai_summary, :cluster_label
            )
            ON CONFLICT (article_hash) DO NOTHING
        """)
    else:
        statement = text("""
            INSERT OR IGNORE INTO stories (
                article_hash, title, summary, content,
                image_url, source, source_url, region, section, source_category, language,
                published_at, fetched_at, bias, bias_confidence, ai_summary, cluster_label
            )
            VALUES (
                :article_hash, :title, :summary, :content,
                :image_url, :source, :source_url, :region, :section, :source_category, :language,
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
                    "image_url": article.get("image_url"),
                    "source": article["source"],
                    "source_url": article.get("source_url"),
                    "region": article.get("region"),
                    "section": article.get("section", "Somalia"),
                    "source_category": article.get("source_category"),
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


def metric_card(label: str, value: object, note: str = "") -> None:
    st.markdown(
        f"""
        <div class="snl-card metric-card">
          <div class="snl-score">{html.escape(str(value))}</div>
          <div class="snl-score-label">{html.escape(label)}</div>
          <div class="snl-muted snl-small">{html.escape(note)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def story_section(row: pd.Series) -> str:
    section = row.get("section")
    if section and str(section).strip():
        return str(section)
    region = str(row.get("region") or "").lower()
    if region in {"somalia", "diaspora", "humanitarian"}:
        return "Somalia"
    return "World"


def story_excerpt(row: pd.Series, limit: int = 220) -> str:
    summary = clean_text(row.get("summary") or row.get("content") or "", limit)
    if summary:
        return summary
    return "A developing story from the monitored source network."


def story_time(row: pd.Series) -> str:
    value = row.get("published_at") or row.get("fetched_at")
    if not value:
        return "Time unavailable"
    try:
        dt = pd.to_datetime(value).to_pydatetime().replace(tzinfo=None)
        delta = utc_now() - dt
        if delta.days > 0:
            return f"{delta.days}d ago"
        hours = int(delta.total_seconds() // 3600)
        if hours > 0:
            return f"{hours}h ago"
        minutes = max(1, int(delta.total_seconds() // 60))
        return f"{minutes}m ago"
    except Exception:
        return safe_date(value)


def story_meta_html(row: pd.Series, show_framing: bool = True) -> str:
    bias = row.get("bias") or "center"
    confidence = float(row.get("bias_confidence") or 0)
    parts = [
        badge(row.get("source"), "source"),
        badge(story_section(row), "region"),
        badge(story_time(row), "neutral"),
    ]
    if show_framing:
        parts.append(
            f"<span class='snl-badge' style='background:#fff;color:{bias_color(bias)};border-color:{bias_color(bias)};'>"
            f"{html.escape(str(bias))} | {confidence:.0%}</span>"
        )
    return "".join(parts)


def story_link(row: pd.Series, label: str = "Read original") -> str:
    url = row.get("source_url") or ""
    if not url:
        return ""
    return f"<a class='story-link' href='{html.escape(str(url))}' target='_blank'>{html.escape(label)}</a>"


def story_image_html(row: pd.Series, variant: str = "standard") -> str:
    visual_class = "story-visual"
    if variant == "hero":
        visual_class += " story-visual-hero"
    elif variant == "list":
        visual_class += " story-visual-list"

    image_url = clean_text(row.get("image_url") or "", 1000)
    title = html.escape(str(row.get("title") or "News image"))
    if image_url.startswith(("http://", "https://")):
        return f"<div class='{visual_class}'><img src='{html.escape(image_url)}' alt='{title}' loading='lazy'></div>"

    label = story_section(row)
    return f"<div class='{visual_class}'><div class='story-visual-placeholder'>{html.escape(label)}</div></div>"


def render_article_card(row: pd.Series, variant: str = "standard") -> None:
    title = html.escape(str(row.get("title") or "Untitled story"))
    excerpt_limit = 360 if variant == "hero" else 190
    excerpt = html.escape(story_excerpt(row, excerpt_limit))
    class_name = f"article-card article-card-{variant}" if variant != "standard" else "article-card"
    visual = story_image_html(row, variant)
    if variant == "list":
        body = f"""
          {visual}
          <div>
            <div class="article-meta">{story_meta_html(row)}</div>
            <h2>{title}</h2>
            <p>{excerpt}</p>
            <div class="article-footer">{story_link(row)}</div>
          </div>
        """
    else:
        body = f"""
          {visual}
          <div>
            <div class="article-meta">{story_meta_html(row)}</div>
            <h2>{title}</h2>
            <p>{excerpt}</p>
            <div class="article-footer">{story_link(row)}</div>
          </div>
        """
    st.markdown(
        f"""
        <article class="{class_name}">
          {body}
        </article>
        """,
        unsafe_allow_html=True,
    )


def render_compact_story(row: pd.Series) -> None:
    title = html.escape(str(row.get("title") or "Untitled story"))
    st.markdown(
        f"""
        <div class="compact-story">
          <div class="compact-title">{title}</div>
          <div class="compact-meta">{story_meta_html(row, show_framing=False)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_reader_state(title: str, message: str) -> None:
    st.markdown(
        f"""
        <div class="reader-empty">
          <div class="empty-title">{html.escape(title)}</div>
          <div class="snl-muted">{html.escape(message)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str, deck: str = "") -> None:
    st.markdown(f"<div class='section-heading'>{html.escape(title)}</div>", unsafe_allow_html=True)
    if deck:
        st.markdown(f"<div class='section-deck'>{html.escape(deck)}</div>", unsafe_allow_html=True)


def reader_trust_bar(df: pd.DataFrame) -> None:
    source_count = int(df["source"].nunique()) if not df.empty and "source" in df.columns else len(Config.FEEDS)
    somalia_count = 0
    if not df.empty and "section" in df.columns:
        somalia_count = int(df["section"].fillna("").str.lower().isin(["somalia", "humanitarian"]).sum())
    st.markdown(
        f"""
        <div class="reader-trust-bar">
          <div class="trust-item">
            <div class="trust-number">{source_count} sources</div>
            <div class="trust-label">recent coverage is drawn from a mixed Somali, regional, humanitarian, and international network</div>
          </div>
          <div class="trust-item">
            <div class="trust-number">Somalia first</div>
            <div class="trust-label">{somalia_count} Somalia-focused stories are available in the current reader window</div>
          </div>
          <div class="trust-item">
            <div class="trust-number">Transparent</div>
            <div class="trust-label">source links and cautious framing signals stay visible without turning the page into an analytics panel</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_stories_for_reader(days: int = 14) -> pd.DataFrame:
    try:
        return load_recent_stories(days)
    except Exception as exc:
        logger.warning("Reader load failed: %s", exc)
        return pd.DataFrame()


@st.cache_data(ttl=Config.CACHE_TTL_SECONDS, show_spinner=False)
def load_source_rollup(days: int = 30) -> pd.DataFrame:
    query = text("""
        SELECT source, COUNT(*) AS story_count, MAX(fetched_at) AS last_fetched
        FROM stories
        WHERE fetched_at >= :cutoff
        GROUP BY source
    """)
    cutoff = utc_now() - timedelta(days=days)
    with get_engine().begin() as conn:
        return pd.read_sql(query, conn, params={"cutoff": cutoff})


def clustered_stories(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = assign_clusters(df)
    persist_cluster_labels(out)
    return out


def cluster_summary(items: list[dict]) -> str:
    if not items:
        return "Coverage is still developing."
    sources = ", ".join(sorted({str(item.get("source")) for item in items if item.get("source")})[:4])
    first_summary = clean_text(items[0].get("summary") or items[0].get("title") or "", 240)
    if first_summary:
        return f"Common facts: {first_summary}"
    return f"Common facts are being tracked across {sources}."


def coverage_emphasis(text_value: str) -> str:
    text_lower = text_value.lower()
    signals = [
        ("Security", {"security", "military", "attack", "al-shabaab", "police", "army"}),
        ("Politics", {"president", "minister", "parliament", "election", "government"}),
        ("Humanitarian", {"humanitarian", "aid", "displacement", "drought", "food", "un"}),
        ("Economy", {"business", "economy", "trade", "port", "market", "investment"}),
        ("Diplomacy", {"ethiopia", "kenya", "united nations", "turkey", "agreement", "talks"}),
    ]
    for label, keywords in signals:
        if any(keyword in text_lower for keyword in keywords):
            return label
    return "General update"


def render_comparison_card(cluster_df: pd.DataFrame, public: bool = True) -> None:
    items = cluster_df.to_dict(orient="records")
    first = cluster_df.iloc[0]
    title = html.escape(str(first.get("title") or "Developing story"))
    source_count = cluster_df["source"].nunique()
    confidence = float(cluster_df["bias_confidence"].fillna(0).mean())
    heading = "See how outlets covered this story" if public else "Coverage intelligence"
    emphases = sorted({coverage_emphasis(f"{item.get('title', '')} {item.get('summary', '')}") for item in items})
    emphasis_text = ", ".join(emphases[:4]) if emphases else "General update"
    bias_mix = ", ".join(cluster_df["bias"].fillna("center").value_counts().head(3).index.astype(str).tolist())
    source_names = ", ".join(sorted(cluster_df["source"].dropna().astype(str).unique())[:5])
    st.markdown(
        f"""
        <div class="compare-card">
          <div class="section-kicker">{html.escape(heading)}</div>
          <h3>{title}</h3>
          <div class="article-meta">
            {badge(f"{source_count} sources", "source")}
            {badge(story_section(first), "region")}
            {badge(f"avg confidence {confidence:.0%}", "neutral")}
          </div>
          <div class="compare-grid">
            <div class="compare-lens">
              <div class="compare-lens-title">What they agree on</div>
              <p>{html.escape(cluster_summary(items).replace("Common facts: ", ""))}</p>
            </div>
            <div class="compare-lens">
              <div class="compare-lens-title">Emphasis differs around</div>
              <p>{html.escape(emphasis_text)}. These labels describe visible story emphasis, not a judgment about accuracy.</p>
            </div>
            <div class="compare-lens">
              <div class="compare-lens-title">Source map</div>
              <p>{html.escape(source_names)}{html.escape("..." if source_count > 5 else "")}</p>
              <p>Framing mix: {html.escape(bias_mix or "center")}</p>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    cols = st.columns(min(3, max(1, len(items))))
    for idx, item in enumerate(items[:6]):
        row = pd.Series(item)
        emphasis = coverage_emphasis(f"{item.get('title', '')} {item.get('summary', '')}")
        with cols[idx % len(cols)]:
            st.markdown(
                f"""
                <div class="source-perspective">
                  <div>{badge(item.get("source"), "source")}{badge(emphasis, "neutral")}</div>
                  <div class="perspective-title">{html.escape(str(item.get("title") or "Untitled"))}</div>
                  <p>{html.escape(story_excerpt(row, 150))}</p>
                  {story_link(row, "Original story")}
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_public_header() -> str:
    st.markdown(
        f"""
        <div class="public-masthead">
          <div>
            <div class="brand-kicker">Independent source intelligence for Somali readers</div>
            <div class="public-brand">Somali News Lens</div>
          </div>
          <div class="masthead-note">A modern Somali front page with built-in coverage comparison across {len(Config.FEEDS)} monitored sources.</div>
        </div>
        <div class="reader-edition-strip">
          <div>Reader edition: story-first, source-transparent, Somalia-focused.</div>
          <div>Editor workspace: ingestion, health, analytics, and operations.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    mode = st.radio(
        "Product mode",
        ["Reader Mode", "Editor / Insights Mode"],
        horizontal=True,
        label_visibility="collapsed",
        key="product_mode",
    )
    return mode


def render_reader_nav() -> str:
    page = st.radio(
        "Reader navigation",
        ["Home", "Latest", "Somalia", "World", "Compare Coverage", "About"],
        horizontal=True,
        label_visibility="collapsed",
        key="reader_page",
    )
    st.markdown(
        "<div class='reader-nav-note'>Browse the public edition, then open Compare Coverage when you want to see how different outlets frame the same developing story.</div>",
        unsafe_allow_html=True,
    )
    return page


def reader_home_page(df: pd.DataFrame) -> None:
    st.markdown("<div class='section-kicker'>Front page</div>", unsafe_allow_html=True)
    if df.empty:
        empty_reader_state(
            "The newsroom is ready.",
            "No stories are stored yet. Open Editor / Insights Mode and ingest feeds to publish the first reader view.",
        )
        return

    ordered = df.sort_values(by=["published_at", "fetched_at"], ascending=False, na_position="last")
    reader_trust_bar(ordered)
    lead = ordered.iloc[0]
    left, right = st.columns([1.65, 0.95])
    with left:
        render_article_card(lead, "hero")
    with right:
        st.markdown("<div class='rail-title'>Worth your attention</div>", unsafe_allow_html=True)
        st.markdown("<div class='snl-muted snl-small'>Fast scan of the next stories moving through the source network.</div>", unsafe_allow_html=True)
        for _, row in ordered.iloc[1:7].iterrows():
            render_compact_story(row)
    section_header("Latest News", "A broader wire view so readers can keep moving beyond the first screen.")
    cols = st.columns(3)
    for idx, (_, row) in enumerate(ordered.iloc[7:25].iterrows()):
        with cols[idx % 3]:
            render_article_card(row, "feature")

    somalia = ordered[ordered["section"].fillna("Somalia").str.lower().isin(["somalia", "humanitarian"])]
    section_header("Somalia", "National, regional, diaspora, humanitarian, and Somali-language international reporting in one place.")
    if somalia.empty:
        empty_reader_state("Somalia coverage will appear here.", "Ingest feeds to populate national and regional stories.")
    else:
        cols = st.columns(2)
        for idx, (_, row) in enumerate(somalia.head(12).iterrows()):
            with cols[idx % 2]:
                render_article_card(row, "list")

    world = ordered[ordered["section"].fillna("").str.lower().isin(["world", "africa"])]
    section_header("World and Region", "International and Horn of Africa context that helps explain the wider story environment.")
    if world.empty:
        empty_reader_state("International context is still loading.", "World and Horn of Africa stories will appear after ingestion.")
    else:
        cols = st.columns(2)
        for idx, (_, row) in enumerate(world.head(8).iterrows()):
            with cols[idx % 2]:
                render_article_card(row, "list")

    section_header("Compare Coverage", "The signature feature: see what sources agree on, where emphasis differs, and how the story is still developing.")
    render_reader_compare(df, limit=3)


def reader_latest_page(df: pd.DataFrame) -> None:
    section_header("Latest", "A deeper reverse-chronological stream from the monitored source network.")
    if df.empty:
        empty_reader_state("No latest stories yet.", "The latest feed fills after the editor ingests source updates.")
        return
    ordered = df.sort_values(by=["published_at", "fetched_at"], ascending=False, na_position="last")
    query = st.text_input("Search latest stories", placeholder="Search by headline, source, region, or topic")
    if query.strip():
        q = query.strip().lower()
        ordered = ordered[
            ordered["title"].fillna("").str.lower().str.contains(q, regex=False)
            | ordered["summary"].fillna("").str.lower().str.contains(q, regex=False)
            | ordered["source"].fillna("").str.lower().str.contains(q, regex=False)
            | ordered["region"].fillna("").str.lower().str.contains(q, regex=False)
        ]
    if ordered.empty:
        empty_reader_state("No stories match that search.", "Try a source name, region, or broader topic.")
        return
    st.caption(f"Showing up to {Config.READER_LATEST_LIMIT} stories from the last {Config.READER_LOOKBACK_DAYS} days.")
    for _, row in ordered.head(Config.READER_LATEST_LIMIT).iterrows():
        render_article_card(row, "list")


def reader_section_page(df: pd.DataFrame, section_name: str) -> None:
    deck = (
        "Somalia-first coverage from national, regional, diaspora, humanitarian, and Somali-language sources."
        if section_name.lower() == "somalia"
        else "Global and regional context from international and Africa-focused feeds."
    )
    section_header(section_name, deck)
    if df.empty:
        empty_reader_state(f"No {section_name.lower()} stories yet.", "Check back after the next feed update.")
        return
    target = section_name.lower()
    if target == "world":
        subset = df[df["section"].fillna("").str.lower().isin(["world", "africa"])]
    else:
        subset = df[df["section"].fillna("somalia").str.lower().isin(["somalia", "humanitarian"])]
    if subset.empty:
        empty_reader_state(f"No {section_name.lower()} stories yet.", "This section will populate as matching sources publish updates.")
        return
    cols = st.columns(3)
    st.caption(f"Showing up to {Config.READER_SECTION_LIMIT} stories.")
    for idx, (_, row) in enumerate(subset.sort_values(by=["published_at", "fetched_at"], ascending=False, na_position="last").head(Config.READER_SECTION_LIMIT).iterrows()):
        with cols[idx % 3]:
            render_article_card(row, "feature")


def render_reader_compare(df: pd.DataFrame, limit: int = 6) -> None:
    if df.empty:
        empty_reader_state("Comparison cards need more coverage.", "Once multiple sources cover the same story, comparisons will appear here.")
        return
    clustered = clustered_stories(df)
    if clustered.empty or "cluster_label" not in clustered.columns:
        empty_reader_state("No comparable story groups yet.", "Ingest more sources to build overlap across coverage.")
        return
    clusters = [
        cluster.sort_values(by=["published_at", "fetched_at"], ascending=False, na_position="last")
        for _, cluster in clustered[clustered["cluster_label"] != -1].groupby("cluster_label")
        if len(cluster) >= 2
    ]
    if not clusters:
        empty_reader_state("No comparable story groups yet.", "The system needs at least two related stories before it can compare coverage.")
        return
    for cluster in clusters[:limit]:
        render_comparison_card(cluster, public=True)


def reader_about_page() -> None:
    st.markdown(
        """
        <div class="about-panel">
          <div class="section-kicker">About and methodology</div>
          <h2>A Somali front page built around transparency, not outrage.</h2>
          <p>
            Somali News Lens gathers public RSS feeds from Somali national outlets, regional publishers,
            diaspora voices, humanitarian sources, and international newsrooms. Reader Mode keeps the experience
            story-first, while Compare Coverage adds context about who else reported the same development.
          </p>
          <p>
            Framing labels are assistive signals, not verdicts. They are meant to help readers notice emphasis,
            source mix, and confidence, while the original reporting remains one click away.
          </p>
          <p>
            Editor / Insights Mode is private by design. It handles feed refreshes, source health, analytics,
            and maintenance without exposing operational controls to public visitors.
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_reader_mode(db_ready: bool) -> None:
    reader_page = render_reader_nav()
    if not db_ready:
        empty_reader_state("Coverage is temporarily unavailable.", "The database is not reachable. No secrets or internal diagnostics are shown here.")
        return
    df = load_stories_for_reader(Config.READER_LOOKBACK_DAYS)
    if reader_page == "Home":
        reader_home_page(df)
    elif reader_page == "Latest":
        reader_latest_page(df)
    elif reader_page == "Somalia":
        reader_section_page(df, "Somalia")
    elif reader_page == "World":
        reader_section_page(df, "World")
    elif reader_page == "Compare Coverage":
        section_header("Compare Coverage", "See how multiple sources covered the same developing story, without turning the reader experience into a technical dashboard.")
        render_reader_compare(df, limit=10)
    else:
        reader_about_page()

    st.markdown(
        """
        <footer class="public-footer">
          <div>Somali News Lens</div>
          <div>Source-transparent coverage. Reader view for the public, Insights view for newsroom operations.</div>
        </footer>
        """,
        unsafe_allow_html=True,
    )


def insights_sidebar() -> str:
    with st.sidebar:
        st.markdown("### Insights Mode")
        page = st.radio(
            "Workspace",
            ["Dashboard", "Ingest", "Coverage Intelligence", "Analytics", "Sources", "Operations", "Account"],
            label_visibility="collapsed",
        )
        st.caption("Internal newsroom intelligence")
        st.divider()
        if session_active():
            st.success(f"Signed in as {st.session_state['user']}")
            if st.button("Sign out", use_container_width=True):
                logout()
                st.rerun()
        else:
            st.warning("Sign in to use ingestion and operations controls.")
        st.divider()
        st.caption(f"Version {Config.VERSION}")
        return page


def require_editor() -> bool:
    if session_active():
        return True
    st.warning("Sign in from Account to use this editor control.")
    return False


def insights_dashboard_page(df: pd.DataFrame) -> None:
    st.markdown("## Newsroom Dashboard")
    if df.empty:
        empty_reader_state("No stored coverage yet.", "Run Ingest to fetch stories from the expanded source network.")
        return
    clustered = clustered_stories(df)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("Stories", int(df["id"].count()), "Stored in the last 30 days")
    with c2:
        metric_card("Sources", int(df["source"].nunique()), "Publishing sources represented")
    with c3:
        metric_card("Somalia share", f"{(df['section'].fillna('').str.lower().isin(['somalia', 'humanitarian']).mean() * 100):.0f}%", "Reader-facing priority")
    with c4:
        metric_card("Clustered", int((clustered["cluster_label"] != -1).sum()), "Stories with comparison potential")

    st.markdown("### Recently stored stories")
    for _, row in df.sort_values(by=["published_at", "fetched_at"], ascending=False, na_position="last").head(8).iterrows():
        render_article_card(row)


def insights_ingest_page() -> None:
    st.markdown("## Ingest")
    st.markdown(
        """
        <div class="snl-shell">
          <div class="snl-card-title">Refresh monitored feeds</div>
          <div class="snl-muted">Fetches the expanded Somali, regional, humanitarian, and international source list. Each feed is isolated so failures are reported without stopping the run.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        metric_card("Sources in run", len(Config.FEEDS), "Capped for Render free tier")
    with col_b:
        metric_card("Per-feed cap", Config.MAX_ARTICLES_PER_FEED, "Articles per source")
    with col_c:
        metric_card("Concurrency", Config.FEED_CONCURRENCY, "Parallel fetch limit")

    if not require_editor():
        return

    if st.button("Fetch latest coverage", type="primary", use_container_width=True):
        with st.spinner("Checking feeds and collecting stories..."):
            raw_articles, statuses = fetch_all_feeds()
        st.session_state["source_status"] = {status["name"]: status for status in statuses}

        healthy = sum(1 for status in statuses if status["status"] == "healthy")
        failed = sum(1 for status in statuses if status["status"] == "failed")
        st.info(f"{healthy} feeds returned stories. {failed} feeds need attention.")

        if not raw_articles:
            st.error("No articles were fetched. Review the Sources page for feed status.")
            return

        with st.spinner("Classifying framing and preparing deduplicated records..."):
            enriched, stats = enrich_articles(raw_articles)

        try:
            inserted = insert_articles(enriched)
            load_recent_stories.clear()
            load_source_rollup.clear()
        except Exception as exc:
            logger.exception("Insert failed")
            st.error("Stories were fetched but could not be saved. Check DATABASE_URL and database permissions.")
            st.caption(exc.__class__.__name__)
            return

        st.success(f"Fetched {len(enriched)} articles and inserted {inserted} new stories.")
        st.caption(f"Classification: {stats.get('openai', 0)} OpenAI, {stats.get('fallback', 0)} fallback.")
        preview_cols = ["title", "source", "section", "region", "bias", "bias_confidence"]
        st.dataframe(pd.DataFrame(enriched)[preview_cols].head(50), use_container_width=True)
        log_activity(st.session_state.get("user"), "ingest_news")


def coverage_intelligence_page(df: pd.DataFrame) -> None:
    st.markdown("## Coverage Intelligence")
    st.markdown("<p class='reader-intro'>Review overlapping stories, common facts, source perspectives, and framing signals.</p>", unsafe_allow_html=True)
    render_reader_compare(df, limit=12)


def analytics_page(df: pd.DataFrame) -> None:
    st.markdown("## Analytics")
    if df.empty:
        empty_reader_state("No analytics yet.", "Ingest news to populate source, section, and framing charts.")
        return

    clustered = clustered_stories(df)
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
        bias_df.columns = ["framing", "count"]
        fig = px.bar(bias_df, x="framing", y="count", title="Framing distribution", color="framing")
        fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        section_df = df["section"].fillna("Unsectioned").value_counts().reset_index()
        section_df.columns = ["section", "count"]
        fig = px.bar(section_df, x="section", y="count", title="Section mix", color="section")
        fig.update_layout(showlegend=False, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig, use_container_width=True)

    source_df = (
        df.groupby("source", as_index=False)
        .agg(count=("id", "count"), avg_confidence=("bias_confidence", "mean"))
        .sort_values("count", ascending=False)
        .head(15)
    )
    fig = px.bar(source_df, x="source", y="count", color="avg_confidence", title="Source activity")
    fig.update_layout(margin=dict(l=20, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)


def sources_page() -> None:
    st.markdown("## Sources")
    st.markdown("<p class='reader-intro'>Monitor feed coverage, recent ingest results, and source diversity.</p>", unsafe_allow_html=True)
    try:
        rollup = load_source_rollup(30)
    except Exception as exc:
        logger.warning("Source rollup failed: %s", exc)
        rollup = pd.DataFrame(columns=["source", "story_count", "last_fetched"])

    rollup_map = {}
    if not rollup.empty:
        rollup_map = rollup.set_index("source").to_dict(orient="index")
    status_map = st.session_state.get("source_status", {})
    rows = []
    for source in Config.FEEDS:
        stored = rollup_map.get(source["name"], {})
        status = status_map.get(source["name"], {})
        rows.append(
            {
                "source": source["name"],
                "section": source.get("section"),
                "category": source.get("category"),
                "language": source.get("language"),
                "status": status.get("status", "not checked"),
                "items_last_run": status.get("item_count", 0),
                "stored_30d": int(stored.get("story_count", 0) or 0),
                "last_fetched": stored.get("last_fetched", ""),
                "error": status.get("error", ""),
                "feed_url": source.get("url"),
            }
        )
    source_df = pd.DataFrame(rows)
    healthy = int((source_df["status"] == "healthy").sum()) if "status" in source_df else 0
    checked = int((source_df["status"] != "not checked").sum()) if "status" in source_df else 0
    categories = int(source_df["category"].nunique()) if "category" in source_df else 0
    regions = int(source_df["section"].nunique()) if "section" in source_df else 0
    st.markdown(
        f"""
        <div class="source-summary-grid">
          <div class="trust-item"><div class="trust-number">{len(source_df)}</div><div class="trust-label">configured sources</div></div>
          <div class="trust-item"><div class="trust-number">{healthy}/{checked or len(source_df)}</div><div class="trust-label">healthy in latest checked run</div></div>
          <div class="trust-item"><div class="trust-number">{categories}</div><div class="trust-label">source categories</div></div>
          <div class="trust-item"><div class="trust-number">{regions}</div><div class="trust-label">editorial sections represented</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    source_filter = st.selectbox("Filter source directory", ["All", "Healthy", "Warnings / failed", "Somalia", "World / Africa", "Humanitarian"])
    if source_filter == "Healthy":
        source_df = source_df[source_df["status"] == "healthy"]
    elif source_filter == "Warnings / failed":
        source_df = source_df[source_df["status"].isin(["warning", "failed"])]
    elif source_filter == "Somalia":
        source_df = source_df[source_df["section"].isin(["Somalia"])]
    elif source_filter == "World / Africa":
        source_df = source_df[source_df["section"].isin(["World", "Africa"])]
    elif source_filter == "Humanitarian":
        source_df = source_df[source_df["section"].isin(["Humanitarian"])]
    st.dataframe(source_df, use_container_width=True, hide_index=True)


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
        st.markdown("### Create editor account")
        with st.form("register_form"):
            new_user = st.text_input("Username", help="3-32 characters. Letters, numbers, dots, dashes, and underscores.")
            new_email = st.text_input("Email optional")
            new_password = st.text_input("Password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            invite_code = ""
            if Config.EDITOR_INVITE_CODE:
                invite_code = st.text_input("Editor invite code", type="password")
            create = st.form_submit_button("Create account", use_container_width=True)
            if create:
                if new_password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(new_user, new_password, new_email, invite_code)
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)


def operations_page(db_label: str) -> None:
    st.markdown("## Operations")
    st.markdown(
        """
        <div class="snl-shell">
          <div class="snl-card-title">Deployment and maintenance</div>
          <div class="snl-muted">Operational controls are separated from Reader Mode. Secrets and raw connection strings are never displayed.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    with c1:
        metric_card("Database", db_label, "Current SQL dialect")
    with c2:
        metric_card("OpenAI", "enabled" if Config.OPENAI_ENABLED and Config.OPENAI_API_KEY else "fallback", "Reader pages do not call OpenAI")
    with c3:
        metric_card("Runtime", "Python 3.11", "Pinned for Render")

    if not require_editor():
        return

    st.markdown("### Maintenance")
    if st.button("Delete stories older than 30 days"):
        try:
            cutoff = utc_now() - timedelta(days=30)
            with get_engine().begin() as conn:
                result = conn.execute(text("DELETE FROM stories WHERE fetched_at < :cutoff"), {"cutoff": cutoff})
            load_recent_stories.clear()
            load_source_rollup.clear()
            st.success(f"Deleted {result.rowcount or 0} old rows.")
        except Exception as exc:
            logger.warning("Maintenance cleanup failed: %s", exc)
            st.error("Cleanup failed. Check database connectivity.")


def render_insights_mode(db_ready: bool, db_label: str) -> None:
    st.markdown(
        """
        <div class="insights-header">
          <div class="section-kicker">Editor / Insights Mode</div>
          <h1>Newsroom intelligence workspace</h1>
          <p>Monitor source health, refresh coverage, compare framing, and review analytics without exposing operations to public readers.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not db_ready:
        st.error(db_label)
        st.info("Check DATABASE_URL in Render. The app did not expose secrets or stack traces.")
        return
    page = insights_sidebar()
    if page != "Account" and not session_active():
        st.warning("Insights Mode is for editor workflows. Sign in or create an editor account to continue.")
        account_page()
        return
    try:
        df = load_recent_stories(30)
    except Exception as exc:
        logger.warning("Insights load failed: %s", exc)
        df = pd.DataFrame()

    if page == "Dashboard":
        insights_dashboard_page(df)
    elif page == "Ingest":
        insights_ingest_page()
    elif page == "Coverage Intelligence":
        coverage_intelligence_page(df)
    elif page == "Analytics":
        analytics_page(df)
    elif page == "Sources":
        sources_page()
    elif page == "Operations":
        operations_page(db_label)
    else:
        account_page()


def main() -> None:
    init_session_state()
    selected_mode = render_public_header()
    inject_css(selected_mode)
    ready, db_label = database_ready()

    if selected_mode == "Reader Mode":
        render_reader_mode(ready)
    else:
        render_insights_mode(ready, db_label)

    st.caption(f"{Config.APP_NAME} v{Config.VERSION}")


if __name__ == "__main__":
    main()

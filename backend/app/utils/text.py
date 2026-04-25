from __future__ import annotations

import hashlib
import re
from collections import Counter


STOP_WORDS = {
    "a",
    "about",
    "after",
    "again",
    "against",
    "all",
    "also",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "their",
    "this",
    "to",
    "was",
    "with",
}


def collapse_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def strip_html(value: str) -> str:
    return collapse_whitespace(re.sub(r"<[^>]+>", " ", value or ""))


def estimate_reading_time(text: str) -> int:
    words = max(1, len(strip_html(text).split()))
    return max(1, round(words / 200))


def tokenize(value: str) -> set[str]:
    tokens = re.findall(r"[a-z0-9_]+", (value or "").lower())
    return {token for token in tokens if len(token) > 2 and token not in STOP_WORDS}


def jaccard_similarity(left: set[str], right: set[str]) -> float:
    if not left or not right:
        return 0.0
    union = left | right
    if not union:
        return 0.0
    return len(left & right) / len(union)


def top_terms(values: list[str], limit: int = 3) -> list[str]:
    counter: Counter[str] = Counter()
    for value in values:
        counter.update(tokenize(value))
    return [item for item, _ in counter.most_common(limit)]


def normalized_title_key(value: str) -> str:
    tokens = re.findall(r"[a-z0-9_]+", (value or "").lower())
    meaningful_tokens = [token for token in tokens if len(token) > 2 and token not in STOP_WORDS]
    return " ".join(meaningful_tokens)


def canonical_url_hash(url: str) -> str:
    normalized = collapse_whitespace(url).lower().rstrip("/")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

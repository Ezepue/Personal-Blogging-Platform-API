"""Text utilities: slug generation and reading-time estimation."""
import math
import re
import secrets

from sqlalchemy.orm import Session

_TAG_RE = re.compile(r"<[^>]+>")
_NON_WORD_RE = re.compile(r"[^a-z0-9]+")
WORDS_PER_MINUTE = 200


def slugify(title: str, max_length: int = 80) -> str:
    """Turn a title into a URL-safe slug ("Hello, World!" -> "hello-world")."""
    slug = _NON_WORD_RE.sub("-", title.lower()).strip("-")
    return slug[:max_length].rstrip("-") or "post"


def unique_slug(db: Session, title: str) -> str:
    """Generate a slug unique across articles, suffixing a short token on collision."""
    from models.article import ArticleDB  # local import to avoid a cycle

    base = slugify(title)
    slug = base
    while db.query(ArticleDB.id).filter(ArticleDB.slug == slug).first() is not None:
        slug = f"{base}-{secrets.token_hex(3)}"
    return slug


def strip_html(html: str) -> str:
    """Remove tags to approximate the visible text of an HTML fragment."""
    return _TAG_RE.sub(" ", html or "")


def reading_time_minutes(html_content: str) -> int:
    """Estimate reading time in whole minutes (minimum 1) at ~200 wpm."""
    words = len(strip_html(html_content).split())
    return max(1, math.ceil(words / WORDS_PER_MINUTE))

"""Authentication primitives: password hashing and token lifecycle.

This module owns *how* credentials and tokens work. It knows nothing about
HTTP or FastAPI — request-scoped dependencies live in ``app.api.deps``.
"""
import logging
import secrets
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import SecretStr
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.refresh_token import RefreshTokenDB
from app.models.user import UserDB

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

WS_TICKET_EXPIRE_SECONDS = 60
PREVIEW_TOKEN_EXPIRE_HOURS = 72


def hash_password(password) -> str:
    """Hash a plaintext password (str or SecretStr) for storage."""
    value = password.get_secret_value() if isinstance(password, SecretStr) else password
    return pwd_context.hash(value)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check a plaintext password against its stored hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Error verifying password: {e}")
        return False


def verify_user_credentials(db: Session, username: str, password: str) -> Optional[UserDB]:
    """Return the user when username/password match an active account.

    Uses exact (case-insensitive) matching on the lowercased username; ILIKE would
    let %/_ wildcards in the submitted name match unrelated accounts.
    """
    user = db.query(UserDB).filter(func.lower(UserDB.username) == username.strip().lower()).first()
    if user and user.is_active and verify_password(password, user.hashed_password):
        return user
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Mint a short-lived JWT access token carrying ``sub`` and role claims."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def verify_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT, raising 401 on any failure."""
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")


def create_ws_ticket(user_id: int) -> str:
    """Mint a seconds-lived, single-purpose token for WebSocket handshakes.

    Issued instead of exposing the real access token to client JavaScript;
    accepted only by the WebSocket endpoint.
    """
    expire = datetime.utcnow() + timedelta(seconds=WS_TICKET_EXPIRE_SECONDS)
    return jwt.encode(
        {"sub": str(user_id), "token_type": "ws", "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_preview_token(article_id: int, author_id: int) -> str:
    """Mint a days-lived token that grants read access to one unpublished draft."""
    expire = datetime.utcnow() + timedelta(hours=PREVIEW_TOKEN_EXPIRE_HOURS)
    return jwt.encode(
        {"sub": str(author_id), "article_id": article_id, "token_type": "preview", "exp": expire},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def verify_preview_token(token: str) -> Optional[int]:
    """Return the article id a preview token grants access to, or None."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
    if payload.get("token_type") != "preview":
        return None
    return payload.get("article_id")


def create_refresh_token(user_id: int, db: Session) -> str:
    """Create and persist an opaque refresh token for the user."""
    refresh_token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    db_token = RefreshTokenDB(user_id=user_id, token=refresh_token, expires_at=expires_at)
    db.add(db_token)
    db.commit()
    return refresh_token


def verify_refresh_token(refresh_token: str, db: Session) -> Optional[int]:
    """Return the owning user id when the refresh token is live, else None.

    A token is live only if it exists, has not been revoked or deactivated
    (logout), and has not expired.
    """
    db_token = db.query(RefreshTokenDB).filter(RefreshTokenDB.token == refresh_token).first()
    if not db_token or db_token.revoked or not db_token.is_active:
        return None
    if db_token.expires_at < datetime.utcnow():
        return None
    return db_token.user_id

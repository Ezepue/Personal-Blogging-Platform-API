"""
Pytest configuration and shared fixtures.

Env vars MUST be set before any app module is imported so that config.py
and database.py pick them up (load_dotenv() won't override pre-set vars).
"""
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_blog.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-pytest-minimum-32-chars"
os.environ["UPLOAD_FOLDER"] = "/tmp/test_uploads"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["FRONTEND_URL"] = "http://localhost:3000"
# Allow TestClient's default host ("testserver") through TrustedHostMiddleware
os.environ["ALLOWED_HOSTS"] = "testserver,localhost,127.0.0.1"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address

# App imports come AFTER env vars are set
from database import Base, get_db
from main import app
from models.user import UserDB
from models.enums import UserRole
from utils.auth_helpers import create_access_token
import routes.users as _users_routes   # needed to reset its per-route rate limiter

# ── Disable the app-level (middleware) limiter ────────────────────────────────
_unlimited_limiter = Limiter(key_func=get_remote_address, enabled=False)
app.state.limiter = _unlimited_limiter

# ── Test database (file-based SQLite so both database.py engine and test
#    engine share the same file, avoiding in-memory isolation issues) ──────────
_TEST_DB_URL = "sqlite:///./test_blog.db"
_engine = create_engine(_TEST_DB_URL, connect_args={"check_same_thread": False})
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _override_get_db():
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_db():
    """Drop and recreate all tables before each test for full isolation."""
    Base.metadata.create_all(bind=_engine)
    yield
    Base.metadata.drop_all(bind=_engine)


@pytest.fixture(autouse=True)
def reset_rate_limits():
    """Reset per-route rate limit counters between tests.

    The per-route @limiter.limit() decorators in routes/users.py use a
    separate Limiter instance whose in-memory storage persists across tests.
    Calling .reset() clears all counters so login/register tests don't bleed
    into each other.
    """
    _users_routes.limiter.reset()
    yield
    _users_routes.limiter.reset()


@pytest.fixture
def db():
    session = _TestSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


# ── Helpers (importable by test files) ────────────────────────────────────────

def make_user(
    db,
    username: str,
    role: UserRole = UserRole.READER,
    password: str = "password123",
) -> UserDB:
    """Create a user directly in the test database."""
    user = UserDB(
        username=username,
        email=f"{username}@test.com",
        hashed_password=_pwd.hash(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_header(user: UserDB) -> dict:
    """Return Bearer auth header for the given user."""
    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"Authorization": f"Bearer {token}"}


def make_article(client, user: UserDB, title: str = "Test Article Title", content: str = "This is the article body content.") -> dict:
    """Create an article via the API and return the JSON response."""
    res = client.post(
        "/articles/",
        json={"title": title, "content": content, "tags": [], "category": "tech"},
        headers=auth_header(user),
    )
    assert res.status_code == 200, f"Article creation failed: {res.text}"
    return res.json()

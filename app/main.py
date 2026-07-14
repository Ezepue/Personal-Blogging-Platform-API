"""Application factory.

Middleware and routers are registered from declarative tables, so extending
the app (new router, new middleware) means appending an entry — existing
wiring stays closed to modification.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.routes import (
    admin,
    articles,
    bookmarks,
    comments,
    dashboard,
    feeds,
    likes,
    media,
    notifications,
    reports,
    users,
)

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

ROUTERS = (
    (users.router, "/users", "Users"),
    (articles.router, "/articles", "Articles"),
    (likes.router, "/like", "Likes"),
    (comments.router, "/comments", "Comments"),
    (notifications.router, "/notification", "Notifications"),
    (media.router, "/media", "Media"),
    (admin.router, "/admin", "Admin"),
    (bookmarks.router, "/bookmarks", "Bookmarks"),
    (dashboard.router, "/dashboard", "Dashboard"),
    (reports.router, "/reports", "Reports"),
    (feeds.router, "", "Feeds"),
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach browser hardening headers to every response."""

    async def dispatch(self, request: StarletteRequest, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response


def init_db() -> None:
    """Ensure database tables exist before serving requests."""
    Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup/shutdown hooks."""
    init_db()
    yield
    logger.info("Shutting down server...")


def create_app() -> FastAPI:
    """Build and wire the FastAPI application."""
    app = FastAPI(title="Quill — Personal Blogging Platform API", lifespan=lifespan)

    limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
    app.state.limiter = limiter

    # Starlette applies middleware LIFO: last registered runs first.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

    for router, prefix, tag in ROUTERS:
        app.include_router(router, prefix=prefix, tags=[tag])

    app.add_exception_handler(429, _rate_limit_exceeded_handler)

    @app.exception_handler(404)
    async def custom_404_handler(request: Request, exc):
        return JSONResponse(status_code=404, content={"detail": "Resource not found"})

    @app.get("/")
    async def root():
        return {"message": "Welcome to the Quill API!"}

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    return app


app = create_app()

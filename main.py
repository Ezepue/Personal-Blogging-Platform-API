import logging
from fastapi import FastAPI, Request
from database import Base, engine
from models import *  # Ensure all models are imported before creating tables
from routes import likes, users, articles, comments, admin, media, notifications
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

# --- Logging Configuration ---
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Initialize FastAPI ---
app = FastAPI(title="Personal Blogging Platform API")

# --- Rate Limiting Setup ---
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])
app.state.limiter = limiter

# --- Middleware Setup ---
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["yourdomain.com", "127.0.0.1"])
app.add_middleware(SlowAPIMiddleware)

# Optional: Enable CORS if frontend needs access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5500/", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database Initialization ---
def init_db():
    """Ensures database tables exist before starting."""
    logger.info("Initializing database...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully.")

@app.on_event("startup")
def startup_event():
    """Runs on server startup."""
    init_db()

@app.on_event("shutdown")
def shutdown_event():
    """Handles any cleanup or closing operations during shutdown."""
    logger.info("Shutting down server...")

# --- Register Routers ---
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(articles.router, prefix="/articles", tags=["Articles"])
app.include_router(likes.router, prefix="/like", tags=["Likes"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(notifications.router, prefix="/notification", tags=["Notifications"])
app.include_router(media.router, prefix="/media", tags=["Media"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])

# --- Custom 404 Error Handler ---
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    """Handles 404 errors with logging."""
    logger.warning(f"404 Not Found: {request.method} {request.url}")
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})

# --- Attach SlowAPI rate limit exceeded handler ---
app.add_exception_handler(429, _rate_limit_exceeded_handler)

# --- Root Endpoint ---
@app.get("/")
async def root():
    """Welcome message."""
    return {"message": "Welcome to the Personal Blogging Platform API!"}

from fastapi import FastAPI, Request
from database import Base, engine
from routes import users, articles, comments, admin, media
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse

# Initialize Limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI()

# Assign limiter to app state
app.state.limiter = limiter

# Add Middlewares
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Create database tables (Ensure tables are created before the app starts)
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(articles.router, prefix="/articles", tags=["Articles"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(media.router, prefix="/media", tags=["Media"])

# Custom Rate Limit Exceeded Handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests, slow down!"},
    )

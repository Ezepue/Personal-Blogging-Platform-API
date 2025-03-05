from fastapi import FastAPI, Request
from database import Base, engine
from routes import users, articles, comments, admin, media
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

# Initialize FastAPI
app = FastAPI()

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Middlewares
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(SlowAPIMiddleware)

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)

# Register Routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(articles.router, prefix="/articles", tags=["Articles"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
app.include_router(media.router, prefix="/media", tags=["Media"])

# Custom 404 Error Handler
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    return JSONResponse(status_code=404, content={"detail": "Resource not found"})

# Attach SlowAPI rate limit exceeded handler
app.add_exception_handler(429, _rate_limit_exceeded_handler)

from fastapi import FastAPI
from database import Base, engine
from routes import users, articles, comments

# Initialize FastAPI app
app = FastAPI()

# Create database tables (Ensure tables are created before the app starts)
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(articles.router, prefix="/articles", tags=["Articles"])
app.include_router(comments.router, prefix="/comments", tags=["Comments"])

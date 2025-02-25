from fastapi import FastAPI
from database import Base, engine
from routes import users, articles
# from users import router as user_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(articles.router, prefix="/articles", tags=["Articles"])

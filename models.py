from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class ArticleDB(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    tags = Column(String, nullable=True)  # Store as comma-separated string
    published_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=True)

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime
from database import Base

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relationship: A user can have multiple articles
    articles = relationship("ArticleDB", back_populates="owner")

class ArticleDB(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(String)
    tags = Column(JSON, nullable=True)  # Store tags as JSON
    published_date = Column(DateTime, default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("UserDB", back_populates="articles")

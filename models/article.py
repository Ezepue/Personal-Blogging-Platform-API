from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, func
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import select
from database import Base
from models.enums import ArticleStatus
from models.like import LikeDB

class ArticleDB(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    tags = Column(JSONB, nullable=False, default=lambda: [])  
    category = Column(String, nullable=True)

    status = Column(Enum(ArticleStatus, native_enum=True), default=ArticleStatus.DRAFT, nullable=False)
    published_date = Column(DateTime, nullable=True, index=True)
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author = relationship("UserDB", back_populates="articles", passive_deletes=True)

    likes = relationship("LikeDB", back_populates="article", cascade="all, delete-orphan", passive_deletes=True)
    comments = relationship("CommentDB", back_populates="article", cascade="all, delete-orphan", passive_deletes=True)
    
    likes_count = Column(Integer, default=0, nullable=False)

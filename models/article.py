from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from database import Base
from .enums import ArticleStatus

class ArticleDB(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    content = Column(String, nullable=False)
    tags = Column(JSON, default=[])
    category = Column(String, nullable=True)
    status = Column(Enum(ArticleStatus, native_enum=False), default=ArticleStatus.DRAFT, nullable=False)
    published_date = Column(DateTime, nullable=True)
    updated_date = Column(DateTime, nullable=True)

    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author = relationship("UserDB", back_populates="articles")
    
    likes_count = Column(Integer, default=0)
    likes = relationship("LikeDB", back_populates="article", cascade="all, delete-orphan")
    comments = relationship("CommentDB", back_populates="article", cascade="all, delete-orphan")
    

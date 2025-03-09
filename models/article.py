from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.sql import func

from database import Base
from .enums import ArticleStatus  # Ensure this is correctly imported

class ArticleDB(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)  # Optimized for long content
    tags = Column(JSON, nullable=False, default=list)  # Handle default in Python instead of `server_default`
    category = Column(String, nullable=True)

    status = Column(Enum(ArticleStatus, native_enum=False), default=ArticleStatus.DRAFT, nullable=False)
    published_date = Column(DateTime, nullable=True, index=True)
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author = relationship("UserDB", back_populates="articles", passive_deletes=True)

    likes = relationship("LikeDB", back_populates="article", cascade="all, delete-orphan")
    comments = relationship("CommentDB", back_populates="article", cascade="all, delete-orphan")

    @property
    def likes_count(self):
        """Dynamically calculate likes count."""
        return len(self.likes)

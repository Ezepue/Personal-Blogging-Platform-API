from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text, func, Boolean
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import select
from app.db.base_class import Base
from app.models.enums import ArticleStatus
from app.models.like import LikeDB
from app.models.comment import CommentDB

class ArticleDB(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    subtitle = Column(String(300), nullable=True)
    slug = Column(String(250), unique=True, nullable=True, index=True)
    content = Column(Text, nullable=False)
    tags = Column(JSONB, nullable=False, default=lambda: [])
    category = Column(String, nullable=True)
    cover_image_url = Column(String(500), nullable=True)

    status = Column(Enum(ArticleStatus, native_enum=True), default=ArticleStatus.DRAFT, nullable=False)
    published_date = Column(DateTime, nullable=True, index=True)
    updated_date = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    author = relationship(
        "UserDB", back_populates="articles", passive_deletes=True, foreign_keys=[author_id]
    )

    likes = relationship("LikeDB", back_populates="article", cascade="all, delete-orphan", passive_deletes=True)
    comments = relationship("CommentDB", back_populates="article", cascade="all, delete-orphan", passive_deletes=True)

    likes_count = Column(Integer, default=0, nullable=False)
    views_count = Column(Integer, default=0, nullable=False, server_default="0")
    reading_time_minutes = Column(Integer, default=1, nullable=False, server_default="1")
    word_count = Column(Integer, default=0, nullable=False, server_default="0")

    # Visibility & curation: unlisted stories are link-only; featured stories
    # appear in the editors' picks rail.
    is_unlisted = Column(Boolean, default=False, nullable=False, server_default="false")
    is_featured = Column(Boolean, default=False, nullable=False, server_default="false")

    comments_count = column_property(
        select(func.count(CommentDB.id))
        .where(CommentDB.article_id == id, CommentDB.is_deleted == False)
        .correlate_except(CommentDB)
        .scalar_subquery()
    )

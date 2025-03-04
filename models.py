from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.sqlite import JSON
from datetime import datetime
from database import Base
import enum

# User roles
class UserRole(enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    author = "author"
    reader = "reader"

# Article status
class ArticleStatus(enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False), default=UserRole.reader.value, nullable=False)

    articles = relationship("ArticleDB", back_populates="owner", cascade="all, delete-orphan")
    likes = relationship("LikeDB", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("CommentDB", back_populates="user", cascade="all, delete-orphan")

class ArticleDB(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)  # Ensured required field
    content = Column(String, nullable=False)  # Ensured required field
    tags = Column(JSON, default=[])  # Default to empty list to prevent None issues
    category = Column(String, nullable=True)
    status = Column(Enum(ArticleStatus, native_enum=False), default=ArticleStatus.DRAFT.value, nullable=False)  
    published_date = Column(DateTime, nullable=True)
    updated_date = Column(DateTime, nullable=True)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)  # Ensured required field
    owner = relationship("UserDB", back_populates="articles")
    likes = relationship("LikeDB", back_populates="article", cascade="all, delete-orphan")
    comments = relationship("CommentDB", back_populates="article", cascade="all, delete-orphan")

class LikeDB(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "article_id", name="unique_like"),)

    article = relationship("ArticleDB", back_populates="likes")
    user = relationship("UserDB", back_populates="likes")

class CommentDB(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    created_date = Column(DateTime, default=lambda: datetime.utcnow(), nullable=False)  # Fixed default issue

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)

    user = relationship("UserDB", back_populates="comments")
    article = relationship("ArticleDB", back_populates="comments")

import re
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, Index, Text, Boolean, DateTime
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from database import Base
from .enums import UserRole

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False), default=UserRole.READER, nullable=False, index=True)
    bio = Column(Text, nullable=True)
    avatar_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False, server_default="true")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, server_default=func.now())

    # Public profile extras
    website = Column(String(300), nullable=True)
    location = Column(String(120), nullable=True)
    twitter = Column(String(80), nullable=True)
    github = Column(String(80), nullable=True)

    # Notification preferences — which events generate a notification for this user.
    notify_likes = Column(Boolean, default=True, nullable=False, server_default="true")
    notify_comments = Column(Boolean, default=True, nullable=False, server_default="true")
    notify_follows = Column(Boolean, default=True, nullable=False, server_default="true")

    # Composite index for faster lookups
    __table_args__ = (
        Index("idx_email_username", "email", "username"),
    )

    # Relationships with cascading delete. Loaded lazily (default "select") so a plain
    # user lookup — which happens on every authenticated request — does not emit a
    # multi-collection cartesian JOIN across all of the user's rows.
    articles = relationship("ArticleDB", back_populates="author", cascade="all, delete-orphan", passive_deletes=True)
    likes = relationship("LikeDB", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    comments = relationship("CommentDB", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    refresh_tokens = relationship("RefreshTokenDB", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    notifications = relationship("NotificationDB", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)


    @validates("username")
    def validate_username(self, key, value):
        """Validate and normalize username"""
        if value and isinstance(value, str):
            value = value.strip().lower()  # Store in lowercase
            if len(value) < 3:
                raise ValueError("Username must be at least 3 characters long")
            if not re.match(r"^[a-zA-Z0-9_]+$", value):
                raise ValueError("Username can only contain letters, numbers, and underscores")
            return value
        raise ValueError("Invalid username")

    @validates("email")
    def validate_email(self, key, value):
        """Validate and normalize email"""
        if value and isinstance(value, str):
            value = value.strip().lower()  # Store in lowercase
            email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_regex, value):
                raise ValueError("Invalid email format")
            return value
        raise ValueError("Invalid email")

    def __repr__(self):
        return f"<UserDB id={self.id}, username={self.username}, email={self.email}, role={self.role}>"

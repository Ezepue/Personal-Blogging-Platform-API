import re
from sqlalchemy import Column, Integer, String, Enum, Index
from sqlalchemy.orm import relationship, validates
from database import Base
from .enums import UserRole

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False), default=UserRole.READER, nullable=False, index=True)

    # Composite index for faster lookups
    __table_args__ = (
        Index("idx_email_username", "email", "username"),
    )

    # Relationships with cascading delete
    articles = relationship("ArticleDB", back_populates="author", cascade="all, delete-orphan", passive_deletes=True, lazy="joined")
    likes = relationship("LikeDB", back_populates="user", cascade="all, delete-orphan", passive_deletes=True, lazy="joined")
    comments = relationship("CommentDB", back_populates="user", cascade="all, delete-orphan", passive_deletes=True, lazy="joined")
    refresh_tokens = relationship("RefreshTokenDB", back_populates="user", cascade="all, delete-orphan", passive_deletes=True, lazy="joined")
    notifications = relationship("NotificationDB", back_populates="user", cascade="all, delete-orphan", passive_deletes=True, lazy="joined")


    @validates("username")
    def validate_username(self, key, value):
        """Validate and normalize username"""
        if value and isinstance(value, str):
            value = value.strip().lower()  # Store in lowercase
            if len(value) < 3:
                raise ValueError("Username must be at least 3 characters long")
            if not re.match(r"^[a-zA-Z0-9._]+$", value):
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

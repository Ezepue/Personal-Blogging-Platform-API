from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship, validates
from database import Base
from .enums import UserRole

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False), default=UserRole.READER, nullable=False)  # Fixed default value

    articles = relationship("ArticleDB", back_populates="author", cascade="all, delete-orphan", passive_deletes=True)
    likes = relationship("LikeDB", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    comments = relationship("CommentDB", back_populates="user", cascade="all, delete-orphan", passive_deletes=True)
    refresh_tokens = relationship("RefreshTokenDB", back_populates="user", cascade="all, delete-orphan")  # Fixed model name

    @validates("username")
    def convert_username_to_lowercase(self, key, value):
        if value and isinstance(value, str):
            value = value.strip()
            if len(value) < 3:
                raise ValueError("Username must be at least 3 characters long")
            return value.lower()
        raise ValueError("Invalid username")

    @validates("email")
    def convert_email_to_lowercase(self, key, value):
        if value and isinstance(value, str):
            value = value.strip()
            if "@" not in value or len(value) < 5:
                raise ValueError("Invalid email format")
            return value.lower()
        raise ValueError("Invalid email")

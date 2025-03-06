from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from database import Base
from .enums import UserRole

class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole, native_enum=False), default=UserRole.reader, nullable=False)

    articles = relationship("ArticleDB", back_populates="author", cascade="all, delete-orphan")
    likes = relationship("LikeDB", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("CommentDB", back_populates="user", cascade="all, delete-orphan")

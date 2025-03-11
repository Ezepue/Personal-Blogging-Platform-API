from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base


class CommentDB(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False) 
    created_date = Column(DateTime, default=func.now(), nullable=False)
    updated_date = Column(DateTime, onupdate=func.now(), nullable=True)  # Fixed update behavior

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)

    user = relationship("UserDB", back_populates="comments", passive_deletes=True)
    article = relationship("ArticleDB", back_populates="comments", passive_deletes=True)

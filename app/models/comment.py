from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship, backref
from app.db.base_class import Base


class CommentDB(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_date = Column(DateTime, default=func.now(), nullable=False)
    updated_date = Column(DateTime, onupdate=func.now(), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    # Threading: a reply points at its parent comment. Top-level comments have NULL.
    parent_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)
    likes_count = Column(Integer, default=0, nullable=False, server_default="0")

    user = relationship("UserDB", back_populates="comments", passive_deletes=True)
    article = relationship("ArticleDB", back_populates="comments", passive_deletes=True)
    # Deleting a parent comment cascades to its replies (matching the FK's
    # ON DELETE CASCADE) rather than orphaning them as top-level comments.
    replies = relationship(
        "CommentDB",
        backref=backref("parent", remote_side=[id]),
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

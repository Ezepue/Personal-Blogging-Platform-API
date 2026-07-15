from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class BookmarkDB(Base):
    __tablename__ = "bookmarks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # A user can bookmark an article at most once
    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="unique_bookmark"),
    )

    user = relationship("UserDB", passive_deletes=True)
    article = relationship("ArticleDB", passive_deletes=True)

    def __repr__(self):
        return f"<BookmarkDB user_id={self.user_id} article_id={self.article_id}>"

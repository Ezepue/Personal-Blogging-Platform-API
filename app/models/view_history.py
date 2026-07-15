from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class ViewHistoryDB(Base):
    """A signed-in reader's most recent visit to an article (one row per pair)."""

    __tablename__ = "view_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)
    viewed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="unique_view_history"),
    )

    article = relationship("ArticleDB", passive_deletes=True)

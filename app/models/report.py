from datetime import datetime

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime

from app.db.base_class import Base


class ReportDB(Base):
    """A user's report against an article or a comment, for admin review."""

    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=True, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=True, index=True)
    reason = Column(String(500), nullable=False)
    status = Column(String(20), default="open", nullable=False, server_default="open", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

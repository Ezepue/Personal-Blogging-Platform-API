from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class CommentLikeDB(Base):
    __tablename__ = "comment_likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    comment_id = Column(Integer, ForeignKey("comments.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # A user can like a comment at most once
    __table_args__ = (
        UniqueConstraint("user_id", "comment_id", name="unique_comment_like"),
    )

    user = relationship("UserDB", passive_deletes=True)
    comment = relationship("CommentDB", passive_deletes=True)

    def __repr__(self):
        return f"<CommentLikeDB user_id={self.user_id} comment_id={self.comment_id}>"

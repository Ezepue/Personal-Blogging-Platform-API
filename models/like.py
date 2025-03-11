from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class LikeDB(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False, index=True)

    # Ensure a user can only like an article once
    __table_args__ = (
        UniqueConstraint("user_id", "article_id", name="unique_like"),
    )

    article = relationship("ArticleDB", back_populates="likes", passive_deletes=True, lazy="joined")
    user = relationship("UserDB", back_populates="likes", passive_deletes=True, lazy="joined")

    def __repr__(self):
        return f"<LikeDB user_id={self.user_id or 'N/A'} article_id={self.article_id or 'N/A'}>"

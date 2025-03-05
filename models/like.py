from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base

class LikeDB(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    article_id = Column(Integer, ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)

    __table_args__ = (UniqueConstraint("user_id", "article_id", name="unique_like"),)

    article = relationship("ArticleDB", back_populates="likes")
    user = relationship("UserDB", back_populates="likes")

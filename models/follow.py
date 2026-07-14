from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class FollowDB(Base):
    __tablename__ = "follows"

    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    followed_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # A user can follow another user at most once
    __table_args__ = (
        UniqueConstraint("follower_id", "followed_id", name="unique_follow"),
    )

    follower = relationship("UserDB", foreign_keys=[follower_id], passive_deletes=True)
    followed = relationship("UserDB", foreign_keys=[followed_id], passive_deletes=True)

    def __repr__(self):
        return f"<FollowDB follower_id={self.follower_id} followed_id={self.followed_id}>"

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from database import Base

class RefreshTokenDB(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    revoked = Column(Boolean, default=False, nullable=False, index=True)

    # Composite index for faster querying of active tokens
    __table_args__ = (
        Index("idx_user_expires", "user_id", "expires_at"),
    )

    user = relationship("UserDB", back_populates="refresh_tokens", passive_deletes=True, lazy="joined")

    def is_valid(self) -> bool:
        """Check if the token is still valid and not revoked."""
        return not self.revoked and datetime.utcnow() < self.expires_at

    @staticmethod
    def generate_expiration(days: int = 30) -> datetime:
        """Generate an expiration date for the token."""
        return datetime.utcnow() + timedelta(days=days)

    def __repr__(self):
        return f"<RefreshTokenDB user_id={self.user_id}, revoked={self.revoked}, expires_at={self.expires_at}>"

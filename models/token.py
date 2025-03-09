from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from database import Base

class RefreshTokenDB(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)  # Indexed for faster lookups
    revoked = Column(Boolean, default=False)

    user = relationship("UserDB", back_populates="refresh_tokens")

    def is_valid(self) -> bool:
        """Check if the token is still valid and not revoked."""
        return not self.revoked and self.expires_at > datetime.utcnow()

    @staticmethod
    def generate_expiration(days: int = 30) -> datetime:
        """Generate an expiration date for the token."""
        return datetime.utcnow() + timedelta(days=days)

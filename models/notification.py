from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from .enums import NotificationType
from datetime import datetime
from database import Base

class NotificationDB(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    message = Column(String, nullable=False)
    extra_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    user = relationship("UserDB", back_populates="notifications", passive_deletes=True, lazy="joined")

    def __repr__(self):
        return f"<NotificationDB user_id={self.user_id or 'N/A'}, message={self.message[:30]}..., is_read={self.is_read}>"

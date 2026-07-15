from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class ActiveSessionResponse(BaseModel):
    session_id: UUID
    user_id: int
    created_at: datetime
    device_info: str
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True

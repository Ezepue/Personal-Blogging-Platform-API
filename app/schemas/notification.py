from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, Dict
from datetime import datetime


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    message: str
    type: str = "system"
    is_read: bool = False
    extra_data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

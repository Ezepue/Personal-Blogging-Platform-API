from pydantic import BaseModel
from datetime import datetime

class ActiveSessionResponse(BaseModel):
    session_id: int
    user_id: int
    created_at: datetime
    device_info: str

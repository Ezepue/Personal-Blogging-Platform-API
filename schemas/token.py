from pydantic import BaseModel
from datetime import datetime

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenResponse(BaseModel):
    id: int
    user_id: int
    device_info: str | None
    created_at: datetime
    expires_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
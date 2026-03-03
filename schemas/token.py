from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "example.access.token",
                "refresh_token": "example.refresh.token",
                "token_type": "bearer",
            }
        }
    )


class RefreshTokenResponse(BaseModel):
    id: int
    user_id: int
    device_info: Optional[str] = None
    created_at: datetime
    expires_at: datetime
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 101,
                "device_info": "Device XYZ",
                "created_at": "2025-03-10T12:00:00Z",
                "expires_at": "2025-04-10T12:00:00Z",
                "is_active": True,
            }
        },
    )
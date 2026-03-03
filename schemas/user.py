from typing import Optional
from pydantic import BaseModel, SecretStr, EmailStr, Field, ConfigDict, field_validator
from models.enums import UserRole

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, description="Password must be at least 8 characters long and strong.")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "password": "strong_password_123",
            }
        }
    )


class PromoteUserRequest(BaseModel):
    new_role: UserRole = Field(..., description="Valid roles: reader, admin, super_admin")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "user_id": 101,
                "new_role": "admin",
            }
        }
    )


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 101,
                "username": "john_doe",
                "email": "john.doe@example.com",
                "role": "reader",
            }
        },
    )

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if v is not None and len(v) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v

class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class UserPublicProfile(BaseModel):
    id: int
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    model_config = ConfigDict(from_attributes=True)

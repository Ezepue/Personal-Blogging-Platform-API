from typing import Optional
from datetime import datetime
from pydantic import BaseModel, SecretStr, EmailStr, Field, ConfigDict, field_validator
from models.enums import UserRole

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, description="Password must be at least 8 characters long and strong.")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "password": "strong_password_123"
            }
        }

class PromoteUserRequest(BaseModel):
    new_role: UserRole = Field(..., description="Valid roles: reader, admin, super_admin")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 101,
                "new_role": "admin"
            }
        }

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 101,
                "username": "john_doe",
                "email": "john.doe@example.com",
                "role": "reader"
            }
        }

class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    bio: Optional[str] = None
    website: Optional[str] = Field(None, max_length=300)
    location: Optional[str] = Field(None, max_length=120)
    twitter: Optional[str] = Field(None, max_length=80)
    github: Optional[str] = Field(None, max_length=80)

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
    role: UserRole
    website: Optional[str] = None
    location: Optional[str] = None
    twitter: Optional[str] = None
    github: Optional[str] = None
    created_at: Optional[datetime] = None
    followers_count: int = 0
    following_count: int = 0
    articles_count: int = 0
    is_followed_by_me: bool = False

    model_config = ConfigDict(from_attributes=True)


class NotificationPrefs(BaseModel):
    notify_likes: bool = True
    notify_comments: bool = True
    notify_follows: bool = True

    model_config = ConfigDict(from_attributes=True)


class FollowUserEntry(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

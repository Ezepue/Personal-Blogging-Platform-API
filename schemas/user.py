from pydantic import BaseModel, SecretStr, EmailStr, Field, ConfigDict
from models.enums import UserRole

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=30, pattern="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: SecretStr = Field(..., min_length=8, description="Password must be at least 8 characters long and strong.")

    class Config:
        schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john.doe@example.com",
                "password": "strong_password_123"
            }
        }

class PromoteUserRequest(BaseModel):
    user_id: int = Field(..., gt=0)  # User ID must be positive
    new_role: UserRole = Field(..., description="Valid roles: reader, admin, super_admin")

    class Config:
        schema_extra = {
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
        schema_extra = {
            "example": {
                "id": 101,
                "username": "john_doe",
                "email": "john.doe@example.com",
                "role": "reader"
            }
        }

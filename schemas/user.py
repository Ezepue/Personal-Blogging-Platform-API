from pydantic import BaseModel, SecretStr, EmailStr, Field, ConfigDict
from models.enums import UserRole

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=30, regex="^[a-zA-Z0-9_]+$")
    email: EmailStr
    password: SecretStr  # Ensure password is hashed before storing

class PromoteUserRequest(BaseModel):
    user_id: int = Field(gt=0)  # User ID must be positive
    new_role: UserRole = Field(description="Valid roles: reader, admin, super_admin")

class UserResponse(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)  # Corrected ConfigDict usage

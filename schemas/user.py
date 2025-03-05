from pydantic import BaseModel, SecretStr
from models.enums import UserRole

class UserCreate(BaseModel):
    username: str
    email: str
    password: SecretStr

class PromoteUserRequest(BaseModel):
    user_id: int
    new_role: UserRole

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

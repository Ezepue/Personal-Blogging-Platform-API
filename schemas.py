from pydantic import BaseModel, SecretStr
from typing import List, Optional
from datetime import datetime
from models import ArticleStatus, UserRole 

# User Schema
class UserCreate(BaseModel):
    username: str
    email: str
    password: SecretStr  # Ensures password is not exposed in logs or responses

class PromoteUserRequest(BaseModel):
    user_id: int
    new_role: UserRole
class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # Ensures compatibility with ORM models

# Article Schema
class ArticleCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []  # Default to empty list instead of None
    category: Optional[str] = None
    status: ArticleStatus = ArticleStatus.DRAFT  # Uses Enum for status

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]
    category: Optional[str] = None
    status: ArticleStatus  
    published_date: Optional[datetime] = None  # Explicitly set default to None
    updated_date: Optional[datetime] = None  
    user_id: int

    class Config:
        from_attributes = True

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = []  # Default to empty list to prevent None issues
    category: Optional[str] = None
    status: Optional[ArticleStatus] = None  

    class Config:
        from_attributes = True

# Comment Schema
class CommentCreate(BaseModel):
    content: str

class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    article_id: int
    created_date: datetime  # Ensures consistency with database field names

    class Config:
        from_attributes = True  

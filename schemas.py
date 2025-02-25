from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# User Schema
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # Ensures ORM compatibility

# Article Schema
class ArticleBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    published_date: datetime = datetime.utcnow()
    updated_date: Optional[datetime] = None

class ArticleCreate(ArticleBase):
    pass  # Inherits everything from ArticleBase

class ArticleResponse(ArticleBase):
    id: int  # Add article ID for responses

    class Config:
        from_attributes = True  # Ensures ORM compatibility

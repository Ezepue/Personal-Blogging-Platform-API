from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models import ArticleStatus

# User Schema
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  

# Article Schema
class ArticleCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    category: Optional[str] = None
    status: ArticleStatus = ArticleStatus.DRAFT  # Fix: Use enum for status

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]
    category: Optional[str]
    status: ArticleStatus  
    published_date: Optional[datetime]  
    updated_date: Optional[datetime]
    user_id: int

    class Config:
        from_attributes = True

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None
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
    created_date: datetime  # Fix: renamed from created_at

    class Config:
        from_attributes = True  

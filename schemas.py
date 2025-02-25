from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import json

# User Schema
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True  # Enables ORM compatibility

# Article Schema
class ArticleCreate(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []
    published_date: datetime = datetime.utcnow()

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]
    published_date: datetime
    updated_date: Optional[datetime]
    user_id: int
    
    @classmethod
    def from_orm(cls, obj):
        """Ensure tags is always returned as a list"""
        tags = json.loads(obj.tags) if isinstance(obj.tags, str) else obj.tags
        return cls(id=obj.id, title=obj.title, content=obj.content, tags=tags)
    
class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    tags: Optional[List[str]] = None

    class Config:
        from_attributes = True

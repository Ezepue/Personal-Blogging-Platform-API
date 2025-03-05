from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from models.enums import ArticleStatus

class ArticleCreate(BaseModel):
    title: str
    content: str
    tags: List[str] = []
    category: Optional[str] = None
    status: ArticleStatus = ArticleStatus.DRAFT

class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str]
    category: Optional[str] = None
    status: ArticleStatus
    published_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    user_id: int

    class Config:
        from_attributes = True

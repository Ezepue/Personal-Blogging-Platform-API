from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from models.enums import ArticleStatus

class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = Field(None, max_length=100)
    status: ArticleStatus = ArticleStatus.DRAFT

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = Field(None)
    status: Optional[ArticleStatus] = None

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: List[str] = Field(default_factory=list) 
    category: Optional[str] = None
    status: ArticleStatus
    published_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    author_id: int
    likes_count: int = Field(default=0, ge=0, description="Total likes on the article")

    model_config = ConfigDict(from_attributes=True)

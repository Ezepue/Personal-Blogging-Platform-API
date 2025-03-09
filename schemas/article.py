from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from models.enums import ArticleStatus

class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=10)
    tags: Optional[List[str]] = None  # Changed Set to List for JSON compatibility
    category: Optional[str] = None
    status: ArticleStatus = ArticleStatus.DRAFT

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = None
    tags: Optional[List[str]] = None  # Changed Set to List
    status: Optional[ArticleStatus] = None  # Allow updates to status

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    tags: Optional[List[str]] = None  # Changed Set to List
    category: Optional[str] = None
    status: ArticleStatus
    published_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    author_id: int

    model_config = ConfigDict(from_attributes=True)  # Corrected ConfigDict usage

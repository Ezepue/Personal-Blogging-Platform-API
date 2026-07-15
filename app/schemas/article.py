from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from app.models.enums import ArticleStatus


class AuthorInfo(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)


class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=300)
    content: str = Field(..., min_length=10)
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = Field(None, max_length=100)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    status: ArticleStatus = ArticleStatus.DRAFT
    is_unlisted: bool = False


class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    subtitle: Optional[str] = Field(None, max_length=300)
    content: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, max_length=100)
    cover_image_url: Optional[str] = Field(None, max_length=500)
    tags: Optional[List[str]] = Field(None)
    status: Optional[ArticleStatus] = None
    is_unlisted: Optional[bool] = None


class ArticleResponse(BaseModel):
    id: int
    title: str
    subtitle: Optional[str] = None
    slug: Optional[str] = None
    content: str
    tags: List[str] = Field(default_factory=list)
    category: Optional[str] = None
    cover_image_url: Optional[str] = None
    status: ArticleStatus
    published_date: Optional[datetime] = None
    updated_date: Optional[datetime] = None
    author_id: int
    author: Optional[AuthorInfo] = None
    likes_count: int = Field(default=0, ge=0, description="Total likes on the article")
    views_count: int = Field(default=0, ge=0, description="Total views of the article")
    comments_count: int = Field(default=0, ge=0, description="Visible comments on the article")
    reading_time_minutes: int = Field(default=1, ge=1, description="Estimated reading time")
    word_count: int = Field(default=0, ge=0, description="Word count of the story body")
    is_unlisted: bool = False
    is_featured: bool = False

    model_config = ConfigDict(from_attributes=True)


class TagCount(BaseModel):
    tag: str
    count: int


class SearchResults(BaseModel):
    articles: List[ArticleResponse]
    authors: List["SearchAuthor"]


class SearchAuthor(BaseModel):
    id: int
    username: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


SearchResults.model_rebuild()

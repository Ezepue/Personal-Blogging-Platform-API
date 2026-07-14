from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class ArticleStats(BaseModel):
    id: int
    title: str
    slug: Optional[str] = None
    status: str
    published_date: Optional[datetime] = None
    views_count: int = 0
    likes_count: int = 0
    comments_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    total_articles: int
    total_published: int
    total_drafts: int
    total_views: int
    total_likes: int
    total_comments: int
    followers_count: int
    following_count: int
    articles: List[ArticleStats]

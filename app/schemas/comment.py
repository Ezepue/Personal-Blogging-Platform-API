from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class CommentCreate(BaseModel):
    article_id: int = Field(..., gt=0, description="ID of the article being commented on")
    content: str = Field(..., min_length=1, max_length=2000, description="Comment text")
    parent_id: Optional[int] = Field(None, gt=0, description="Parent comment ID when replying")

    model_config = ConfigDict(str_strip_whitespace=True)


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=2000, description="Updated comment text")

    model_config = ConfigDict(str_strip_whitespace=True)


class CommentAuthor(BaseModel):
    id: int
    username: str
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CommentResponse(BaseModel):
    id: int = Field(..., gt=0, description="Unique identifier of the comment")
    content: str = Field(..., description="Comment text")
    user_id: int = Field(..., gt=0, description="ID of the user who posted the comment")
    article_id: int = Field(..., gt=0, description="ID of the associated article")
    parent_id: Optional[int] = Field(None, description="Parent comment ID for replies")
    likes_count: int = Field(0, ge=0, description="Number of likes on the comment")
    liked_by_me: bool = Field(False, description="Whether the requesting user liked this comment")
    created_date: datetime = Field(..., description="Timestamp when the comment was created")
    updated_date: Optional[datetime] = Field(None, description="Timestamp when the comment was last edited")
    user: Optional[CommentAuthor] = Field(None, description="Author of the comment")

    model_config = ConfigDict(from_attributes=True)

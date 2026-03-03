from pydantic import BaseModel, Field, ConfigDict
from pydantic import field_validator
from datetime import datetime
from typing import Optional


class CommentUser(BaseModel):
    username: str
    avatar_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CommentCreate(BaseModel):
    article_id: int = Field(..., gt=0, description="ID of the article being commented on")
    content: str = Field(..., min_length=3, max_length=500, description="Comment text (3-500 characters)")

    @field_validator("content", mode="before")
    @classmethod
    def strip_content(cls, v: str) -> str:
        return v.strip() if isinstance(v, str) else v


class CommentResponse(BaseModel):
    id: int = Field(..., gt=0, description="Unique identifier of the comment")
    content: str = Field(..., min_length=3, max_length=500, description="Comment text (3-500 characters)")
    user_id: int = Field(..., gt=0, description="ID of the user who posted the comment")
    user: Optional[CommentUser] = None
    article_id: int = Field(..., gt=0, description="ID of the associated article")
    is_deleted: bool = False
    created_date: datetime = Field(..., description="Timestamp when the comment was created")
    updated_date: Optional[datetime] = Field(None, description="Timestamp when the comment was last updated")

    model_config = ConfigDict(from_attributes=True)

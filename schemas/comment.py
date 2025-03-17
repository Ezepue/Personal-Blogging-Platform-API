from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

class CommentCreate(BaseModel):
    article_id: int = Field(..., gt=0, description="ID of the article being commented on")
    content: str = Field(..., min_length=3, max_length=500, strip_whitespace=True, description="Comment text (3-500 characters)")

class CommentResponse(BaseModel):
    id: int = Field(..., gt=0, description="Unique identifier of the comment")
    content: str = Field(..., min_length=3, max_length=500, strip_whitespace=True, description="Comment text (3-500 characters)")
    user_id: int = Field(..., gt=0, description="ID of the user who posted the comment")
    article_id: int = Field(..., gt=0, description="ID of the associated article")
    created_date: datetime = Field(..., description="Timestamp when the comment was created")
    updated_date: Optional[datetime] = Field(None, description="Timestamp when the comment was last updated")

    model_config = ConfigDict(from_attributes=True)

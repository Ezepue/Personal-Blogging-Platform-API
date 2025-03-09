from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class CommentCreate(BaseModel):
    article_id: int = Field(..., gt=0)  # Ensures valid positive IDs
    content: str = Field(..., min_length=3, max_length=500)  # Enforces content length

class CommentResponse(BaseModel):
    id: int
    content: str = Field(min_length=3, max_length=500)  # Same validation as creation
    user_id: int = Field(gt=0)
    article_id: int = Field(gt=0)
    created_date: datetime

    model_config = ConfigDict(from_attributes=True)  # Corrected ConfigDict usage

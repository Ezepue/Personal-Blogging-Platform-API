from pydantic import BaseModel
from datetime import datetime

class CommentCreate(BaseModel):
    article_id: int
    content: str

class CommentResponse(BaseModel):
    id: int
    content: str
    user_id: int
    article_id: int
    created_date: datetime

    class Config:
        from_attributes = True

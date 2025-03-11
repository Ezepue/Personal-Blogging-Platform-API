from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class LikeResponse(BaseModel):
    message: str
    user_id: int = Field(..., gt=0, description="User who liked the article")  
    article_id: int = Field(..., gt=0, description="Liked article ID")
    user_id: Optional[int] = None  # Make it optional
    likes_count: int

    model_config = ConfigDict(from_attributes=True) 

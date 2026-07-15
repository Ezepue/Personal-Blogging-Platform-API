from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class LikeResponse(BaseModel):
    message: str
    article_id: int = Field(..., gt=0, description="Liked article ID")
    user_id: Optional[int] = Field(None, description="User who liked the article, if applicable")
    likes_count: int = Field(..., ge=0)

    model_config = ConfigDict(from_attributes=True)

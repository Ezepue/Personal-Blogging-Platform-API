from pydantic import BaseModel

class LikeResponse(BaseModel):
    user_id: int
    article_id: int
    likes_count: int

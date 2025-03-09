from pydantic import BaseModel, Field, ConfigDict

class LikeResponse(BaseModel):
    user_id: int = Field(gt=0)  # User ID must be positive
    article_id: int = Field(gt=0)  # Article ID must be positive
    likes_count: int = Field(ge=0)  # Likes cannot be negative

    model_config = ConfigDict(from_attributes=True)  # Corrected ConfigDict usage

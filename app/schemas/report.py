from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ReportCreate(BaseModel):
    """A report against exactly one target: an article or a comment."""

    article_id: Optional[int] = Field(None, gt=0)
    comment_id: Optional[int] = Field(None, gt=0)
    reason: str = Field(..., min_length=3, max_length=500)

    @model_validator(mode="after")
    def exactly_one_target(self):
        if bool(self.article_id) == bool(self.comment_id):
            raise ValueError("Provide exactly one of article_id or comment_id")
        return self


class ReportResponse(BaseModel):
    id: int
    reporter_id: int
    article_id: Optional[int] = None
    comment_id: Optional[int] = None
    reason: str
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

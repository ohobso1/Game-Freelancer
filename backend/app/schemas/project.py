from datetime import datetime

from pydantic import BaseModel, Field


class ProjectIdeaCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=140)
    raw_prompt: str = Field(min_length=10, max_length=5000)
    notes: str | None = Field(default=None, max_length=2000)


class ProjectIdeaResponse(BaseModel):
    id: str = Field(alias="_id")
    title: str
    raw_prompt: str
    notes: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

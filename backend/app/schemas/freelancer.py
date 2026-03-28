from datetime import datetime

from pydantic import BaseModel, Field


class FreelancerProfile(BaseModel):
    id: str = Field(alias="_id")
    display_name: str
    headline: str
    skills: list[str]
    role_tags: list[str] = []
    seniority: str = "unspecified"
    hourly_rate_usd: float = 0
    availability_hours_per_week: int = 0
    timezone: str = ""
    portfolio_links: list[str] = []
    created_at: datetime
    updated_at: datetime


class FreelancerListResponse(BaseModel):
    items: list[FreelancerProfile]
    count: int

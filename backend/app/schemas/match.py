from datetime import datetime

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    required_skill_coverage: float
    optional_skill_bonus: float
    rate_fit_bonus: float = 0.0


class MatchItem(BaseModel):
    freelancer_id: str
    rank: int
    score: float
    score_breakdown: ScoreBreakdown
    matched_required_skills: list[str]
    matched_optional_skills: list[str]


class GenerateMatchesResponse(BaseModel):
    project_id: str
    match_set_id: str
    generated_at: datetime
    total_candidates_scanned: int
    matches: list[MatchItem]


class SavedMatchesResponse(BaseModel):
    project_id: str
    match_set_id: str
    matches: list[MatchItem]

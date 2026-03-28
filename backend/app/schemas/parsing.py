import re

from pydantic import BaseModel, Field, field_validator


class ParsedRole(BaseModel):
    role_name: str = Field(min_length=2, max_length=80)
    count: int = Field(ge=1, le=20)
    seniority: str = Field(pattern="^(junior|mid|senior|lead|unspecified)$")
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)

    @field_validator("seniority", mode="before")
    @classmethod
    def normalize_seniority(cls, value: str) -> str:
        if not isinstance(value, str):
            return "unspecified"

        cleaned = re.sub(r"[^a-z]+", " ", value.strip().lower()).strip()

        if not cleaned:
            return "unspecified"
        if cleaned in {"junior", "jr", "entry", "entry level", "entrylevel"}:
            return "junior"
        if cleaned in {"mid", "middle", "intermediate", "mid level", "midlevel", "mid senior", "midsenior", "senior mid"}:
            return "mid"
        if cleaned in {"senior", "sr", "expert", "principal"}:
            return "senior"
        if cleaned in {"lead", "team lead", "technical lead", "tech lead", "staff"}:
            return "lead"

        # Fallback keeps parsing resilient when the model returns unfamiliar labels.
        return "unspecified"


class ParsedConstraints(BaseModel):
    budget_min_usd: float | None = Field(default=None, ge=0)
    budget_max_usd: float | None = Field(default=None, ge=0)
    timeline_weeks: int | None = Field(default=None, ge=1, le=260)
    timezone_overlap_required: bool | None = None


class ParsedRequirements(BaseModel):
    project_summary: str = Field(min_length=10, max_length=2000)
    roles: list[ParsedRole] = Field(min_length=1, max_length=10)
    required_skills: list[str] = Field(min_length=1, max_length=100)
    optional_skills: list[str] = Field(default_factory=list, max_length=100)
    constraints: ParsedConstraints | None = None
    confidence: float | None = Field(default=None, ge=0, le=1)

    @field_validator("required_skills", "optional_skills")
    @classmethod
    def normalize_skills(cls, value: list[str]) -> list[str]:
        normalized = [item.strip() for item in value if item.strip()]
        return list(dict.fromkeys(normalized))


class ParseProjectRequest(BaseModel):
    project_id: str


class ParseProjectResponse(BaseModel):
    project_id: str
    requirements_id: str
    parsed_requirements: ParsedRequirements

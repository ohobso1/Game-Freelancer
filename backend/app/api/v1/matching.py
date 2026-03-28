from fastapi import APIRouter, Query

from app.schemas.match import GenerateMatchesResponse, SavedMatchesResponse
from app.services.matching_service import generate_matches, get_saved_matches


router = APIRouter()


@router.post("/matching/{project_id}", response_model=GenerateMatchesResponse)
async def create_matches(project_id: str, top_n: int = Query(default=20, ge=1, le=50)):
    """Generate, persist, and return ranked freelancer matches for a project."""
    response = await generate_matches(project_id, top_n=top_n)
    return GenerateMatchesResponse.model_validate(response)


@router.get("/matching/{project_id}", response_model=SavedMatchesResponse)
async def fetch_matches(project_id: str):
    """Return the latest saved match set for a project id."""
    response = await get_saved_matches(project_id)
    return SavedMatchesResponse.model_validate(response)

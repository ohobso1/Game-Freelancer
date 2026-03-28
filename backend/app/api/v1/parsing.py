from fastapi import APIRouter

from app.schemas.parsing import ParseProjectRequest, ParseProjectResponse
from app.services.parsing_service import parse_and_store_requirements


router = APIRouter()


@router.post("/parsing", response_model=ParseProjectResponse)
async def parse_project(payload: ParseProjectRequest):
    """Parse a project's raw prompt with Gemini and store normalized requirements."""
    response = await parse_and_store_requirements(payload.project_id)
    return ParseProjectResponse.model_validate(response)

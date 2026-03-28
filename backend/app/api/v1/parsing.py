from fastapi import APIRouter

from app.schemas.parsing import ParseProjectRequest, ParseProjectResponse
from app.services.parsing_service import parse_and_store_requirements


router = APIRouter()


@router.post("/parsing", response_model=ParseProjectResponse)
async def parse_project(payload: ParseProjectRequest):
    response = await parse_and_store_requirements(payload.project_id)
    return ParseProjectResponse.model_validate(response)

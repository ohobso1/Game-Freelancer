from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.db.client import get_database
from app.db.collections import PROJECT_IDEAS
from app.schemas.common import parse_object_id
from app.schemas.project import ProjectIdeaCreateRequest, ProjectIdeaResponse


router = APIRouter()


@router.post("/projects", response_model=ProjectIdeaResponse)
async def create_project(payload: ProjectIdeaCreateRequest):
    """Create and persist a new project idea from raw prompt input."""
    db = get_database()
    now = datetime.now(tz=timezone.utc)

    document = {
        "title": payload.title,
        "raw_prompt": payload.raw_prompt,
        "notes": payload.notes,
        "status": "draft",
        "created_at": now,
        "updated_at": now,
    }

    result = await db[PROJECT_IDEAS].insert_one(document)
    document["_id"] = str(result.inserted_id)
    return ProjectIdeaResponse.model_validate(document)


@router.get("/projects/{project_id}", response_model=ProjectIdeaResponse)
async def get_project(project_id: str):
    """Fetch a previously saved project idea by id."""
    db = get_database()
    document = await db[PROJECT_IDEAS].find_one({"_id": parse_object_id(project_id)})
    if document is None:
        raise HTTPException(status_code=404, detail="Project not found")

    document["_id"] = str(document["_id"])
    return ProjectIdeaResponse.model_validate(document)

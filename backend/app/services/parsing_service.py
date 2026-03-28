from datetime import datetime, timezone

from fastapi import HTTPException

from app.db.client import get_database
from app.db.collections import PROJECT_IDEAS, PROJECT_REQUIREMENTS
from app.integrations.gemini_client import GeminiClient
from app.schemas.common import parse_object_id
from app.schemas.parsing import ParsedRequirements
from app.services.normalization_service import normalize_roles, normalize_skills


gemini_client = GeminiClient()


async def parse_and_store_requirements(project_id: str) -> dict:
    db = get_database()

    project_object_id = parse_object_id(project_id)
    project = await db[PROJECT_IDEAS].find_one({"_id": project_object_id})
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        parsed_raw = await gemini_client.parse_project_prompt(project["raw_prompt"])
        parsed = ParsedRequirements.model_validate(parsed_raw)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to parse prompt with Gemini: {exc}") from exc

    parsed_required_skills = await normalize_skills(db, parsed.required_skills)
    parsed_optional_skills = await normalize_skills(db, parsed.optional_skills)

    role_names = [role.role_name for role in parsed.roles]
    normalized_role_names = await normalize_roles(db, role_names)

    normalized_roles: list[dict] = []
    for index, role in enumerate(parsed.roles):
        normalized_must = await normalize_skills(db, role.must_have_skills)
        normalized_nice = await normalize_skills(db, role.nice_to_have_skills)

        normalized_roles.append(
            {
                **role.model_dump(),
                "role_name": normalized_role_names[index] if index < len(normalized_role_names) else role.role_name,
                "must_have_skills": normalized_must,
                "nice_to_have_skills": normalized_nice,
            }
        )

    parsed_data = {
        **parsed.model_dump(),
        "roles": normalized_roles,
        "required_skills": parsed_required_skills,
        "optional_skills": parsed_optional_skills,
    }
    parsed = ParsedRequirements.model_validate(parsed_data)

    now = datetime.now(tz=timezone.utc)
    document = {
        "project_id": project_object_id,
        **parsed_data,
        "raw_llm_output": parsed_raw,
        "parser": {
            "provider": "gemini",
            "model": "gemini-2.0-flash",
            "schema_version": "v1",
        },
        "created_at": now,
    }

    await db[PROJECT_REQUIREMENTS].delete_many({"project_id": project_object_id})
    result = await db[PROJECT_REQUIREMENTS].insert_one(document)

    await db[PROJECT_IDEAS].update_one(
        {"_id": project_object_id},
        {"$set": {"status": "parsed", "updated_at": now}},
    )

    return {
        "project_id": project_id,
        "requirements_id": str(result.inserted_id),
        "parsed_requirements": parsed.model_dump(),
    }

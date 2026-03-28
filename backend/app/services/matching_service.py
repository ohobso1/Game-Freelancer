from datetime import datetime, timezone

from fastapi import HTTPException

from app.db.client import get_database
from app.db.collections import (
    FREELANCER_PROFILES,
    PROJECT_IDEAS,
    PROJECT_MATCH_SET,
    PROJECT_MATCHES,
    PROJECT_REQUIREMENTS,
)
from app.schemas.common import parse_object_id


def _score_candidate(required_skills: set[str], optional_skills: set[str], freelancer_skills: set[str]) -> tuple[float, dict, list[str], list[str]]:
    matched_required = sorted(required_skills.intersection(freelancer_skills))
    matched_optional = sorted(optional_skills.intersection(freelancer_skills))

    required_coverage = len(matched_required) / len(required_skills) if required_skills else 0.0
    optional_bonus = (len(matched_optional) / len(optional_skills) * 0.2) if optional_skills else 0.0
    score = round(min(required_coverage + optional_bonus, 1.0), 4)

    breakdown = {
        "required_skill_coverage": round(required_coverage, 4),
        "optional_skill_bonus": round(optional_bonus, 4),
        "rate_fit_bonus": 0.0,
    }
    return score, breakdown, matched_required, matched_optional


async def generate_matches(project_id: str, top_n: int = 20) -> dict:
    db = get_database()
    project_object_id = parse_object_id(project_id)

    project = await db[PROJECT_IDEAS].find_one({"_id": project_object_id})
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    requirements = await db[PROJECT_REQUIREMENTS].find_one({"project_id": project_object_id})
    if requirements is None:
        raise HTTPException(status_code=400, detail="Project requirements not found. Parse prompt first.")

    required_skills = {skill.lower().strip() for skill in requirements.get("required_skills", [])}
    optional_skills = {skill.lower().strip() for skill in requirements.get("optional_skills", [])}

    freelancers = await db[FREELANCER_PROFILES].find({}).to_list(length=1000)
    now = datetime.now(tz=timezone.utc)

    scored = []
    for freelancer in freelancers:
        skills = {item.lower().strip() for item in freelancer.get("skills", [])}
        score, breakdown, matched_required, matched_optional = _score_candidate(required_skills, optional_skills, skills)

        if score <= 0:
            continue

        scored.append(
            {
                "freelancer_id": str(freelancer["_id"]),
                "score": score,
                "score_breakdown": breakdown,
                "matched_required_skills": matched_required,
                "matched_optional_skills": matched_optional,
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)
    top_scored = scored[:top_n]

    await db[PROJECT_MATCHES].delete_many({"project_id": project_object_id})

    match_set = {
        "project_id": project_object_id,
        "requirements_id": requirements["_id"],
        "algorithm_version": "skill_overlap_v1",
        "total_candidates_scanned": len(freelancers),
        "top_n": top_n,
        "created_at": now,
    }
    match_set_result = await db[PROJECT_MATCH_SET].insert_one(match_set)

    documents = []
    response_matches = []
    for rank, match in enumerate(top_scored, start=1):
        response_item = {
            "freelancer_id": match["freelancer_id"],
            "rank": rank,
            "score": match["score"],
            "score_breakdown": match["score_breakdown"],
            "matched_required_skills": match["matched_required_skills"],
            "matched_optional_skills": match["matched_optional_skills"],
        }
        response_matches.append(response_item)

        documents.append(
            {
                "project_id": project_object_id,
                "match_set_id": match_set_result.inserted_id,
                "freelancer_id": parse_object_id(match["freelancer_id"]),
                **response_item,
                "created_at": now,
            }
        )

    if documents:
        await db[PROJECT_MATCHES].insert_many(documents)

    await db[PROJECT_IDEAS].update_one(
        {"_id": project_object_id},
        {"$set": {"status": "matched", "updated_at": now}},
    )

    return {
        "project_id": project_id,
        "match_set_id": str(match_set_result.inserted_id),
        "generated_at": now,
        "total_candidates_scanned": len(freelancers),
        "matches": response_matches,
    }


async def get_saved_matches(project_id: str) -> dict:
    db = get_database()
    project_object_id = parse_object_id(project_id)

    match_set = await db[PROJECT_MATCH_SET].find_one(
        {"project_id": project_object_id},
        sort=[("created_at", -1)],
    )
    if match_set is None:
        raise HTTPException(status_code=404, detail="No saved matches found for project")

    documents = (
        await db[PROJECT_MATCHES]
        .find({"match_set_id": match_set["_id"]})
        .sort("rank", 1)
        .to_list(length=1000)
    )

    matches = []
    for document in documents:
        matches.append(
            {
                "freelancer_id": str(document["freelancer_id"]),
                "rank": document["rank"],
                "score": document["score"],
                "score_breakdown": document["score_breakdown"],
                "matched_required_skills": document["matched_required_skills"],
                "matched_optional_skills": document["matched_optional_skills"],
            }
        )

    return {
        "project_id": project_id,
        "match_set_id": str(match_set["_id"]),
        "matches": matches,
    }

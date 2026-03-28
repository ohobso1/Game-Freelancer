from fastapi import APIRouter, Query

from app.db.client import get_database
from app.db.collections import FREELANCER_PROFILES
from app.schemas.freelancer import FreelancerListResponse, FreelancerProfile
from app.schemas.common import parse_object_id


router = APIRouter()


@router.get("/freelancers", response_model=FreelancerListResponse)
async def list_freelancers(
    skill: str | None = Query(default=None),
    min_rate: float | None = Query(default=None, ge=0),
    max_rate: float | None = Query(default=None, ge=0),
    min_availability: int | None = Query(default=None, ge=0),
):
    db = get_database()

    query: dict = {}
    if skill:
        query["skills"] = {"$in": [skill]}
    if min_rate is not None or max_rate is not None:
        query["hourly_rate_usd"] = {}
        if min_rate is not None:
            query["hourly_rate_usd"]["$gte"] = min_rate
        if max_rate is not None:
            query["hourly_rate_usd"]["$lte"] = max_rate
    if min_availability is not None:
        query["availability_hours_per_week"] = {"$gte": min_availability}

    docs = await db[FREELANCER_PROFILES].find(query).sort("updated_at", -1).to_list(length=200)
    items = []
    for doc in docs:
        doc["_id"] = str(doc["_id"])
        items.append(FreelancerProfile.model_validate(doc))

    return FreelancerListResponse(items=items, count=len(items))


@router.get("/freelancers/{freelancer_id}", response_model=FreelancerProfile)
async def get_freelancer(freelancer_id: str):
    db = get_database()
    doc = await db[FREELANCER_PROFILES].find_one({"_id": parse_object_id(freelancer_id)})
    if doc is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="Freelancer not found")

    doc["_id"] = str(doc["_id"])
    return FreelancerProfile.model_validate(doc)

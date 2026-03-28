import asyncio

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.db.collections import (
    FREELANCER_PROFILES,
    PROJECT_IDEAS,
    PROJECT_MATCH_SET,
    PROJECT_MATCHES,
    PROJECT_REQUIREMENTS,
)


async def main() -> None:
    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is not configured")

    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]

    await db[FREELANCER_PROFILES].create_index([("skills", 1)])
    await db[FREELANCER_PROFILES].create_index([("hourly_rate_usd", 1)])
    await db[FREELANCER_PROFILES].create_index([("availability_hours_per_week", 1)])

    await db[PROJECT_IDEAS].create_index([("created_at", -1)])
    await db[PROJECT_REQUIREMENTS].create_index([("project_id", 1)], unique=True)

    await db[PROJECT_MATCH_SET].create_index([("project_id", 1), ("created_at", -1)])
    await db[PROJECT_MATCHES].create_index([("project_id", 1), ("rank", 1)])
    await db[PROJECT_MATCHES].create_index([("match_set_id", 1), ("rank", 1)])

    client.close()


if __name__ == "__main__":
    asyncio.run(main())

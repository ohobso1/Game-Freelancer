import asyncio
from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.db.collections import FREELANCER_PROFILES


SEED_DATA = [
    {
        "display_name": "Alex Rivera",
        "headline": "Unity Gameplay Programmer",
        "skills": ["Unity", "C#", "Netcode", "AI"],
        "role_tags": ["Gameplay Developer", "Multiplayer Engineer"],
        "seniority": "mid",
        "hourly_rate_usd": 45,
        "availability_hours_per_week": 20,
        "timezone": "UTC-5",
        "portfolio_links": ["https://portfolio.example/alex"],
    },
    {
        "display_name": "Mina Patel",
        "headline": "Pixel Artist",
        "skills": ["Pixel Art", "Aseprite", "UI Art"],
        "role_tags": ["2D Artist"],
        "seniority": "senior",
        "hourly_rate_usd": 35,
        "availability_hours_per_week": 25,
        "timezone": "UTC+1",
        "portfolio_links": ["https://portfolio.example/mina"],
    },
    {
        "display_name": "Jordan Kim",
        "headline": "Technical Sound Designer",
        "skills": ["FMOD", "Wwise", "Unity"],
        "role_tags": ["Audio Engineer"],
        "seniority": "mid",
        "hourly_rate_usd": 40,
        "availability_hours_per_week": 15,
        "timezone": "UTC-8",
        "portfolio_links": ["https://portfolio.example/jordan"],
    },
]


async def main() -> None:
    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is not configured")

    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]

    now = datetime.now(tz=timezone.utc)
    docs = []
    for record in SEED_DATA:
        docs.append({**record, "created_at": now, "updated_at": now})

    await db[FREELANCER_PROFILES].delete_many({})
    if docs:
        await db[FREELANCER_PROFILES].insert_many(docs)

    client.close()


if __name__ == "__main__":
    asyncio.run(main())

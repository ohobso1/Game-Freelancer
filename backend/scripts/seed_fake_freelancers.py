import asyncio
import random
from argparse import ArgumentParser
from datetime import datetime, timezone
from pathlib import Path
import sys

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from motor.motor_asyncio import AsyncIOMotorClient

from app.config import settings
from app.db.collections import FREELANCER_PROFILES, ROLE_CATALOG, SKILL_CATALOG
from app.services.normalization_service import dedupe_keep_order, slugify


DEFAULT_COUNT = 60

FIRST_NAMES = [
    "Alex", "Mina", "Jordan", "Sam", "Taylor", "Riley", "Casey", "Harper", "Morgan", "Avery",
    "Kai", "Noah", "Liam", "Ethan", "Maya", "Nora", "Zoe", "Iris", "Leo", "Jules",
]
LAST_NAMES = [
    "Rivera", "Patel", "Kim", "Johnson", "Chen", "Garcia", "Singh", "Lopez", "Brown", "Turner",
    "Khan", "Nguyen", "Reed", "Diaz", "Sato", "Miller", "Hughes", "Bennett", "Park", "Shaw",
]

TIMEZONES = ["UTC-8", "UTC-5", "UTC-3", "UTC+0", "UTC+1", "UTC+2", "UTC+5:30", "UTC+8", "UTC+10"]

ROLE_LIBRARY = [
    {
        "role": "Unity Gameplay Developer",
        "aliases": ["Gameplay Developer", "Unity Programmer", "Unity Dev"],
        "headline": "Unity Gameplay Programmer",
        "skills": ["Unity", "C#", "Gameplay Systems", "Physics", "State Machines"],
    },
    {
        "role": "Unreal Developer",
        "aliases": ["UE Developer", "Unreal Programmer"],
        "headline": "Unreal Gameplay Engineer",
        "skills": ["Unreal Engine", "C++", "Blueprints", "AI", "Networking"],
    },
    {
        "role": "Pixel Artist",
        "aliases": ["2D Artist", "Sprite Artist"],
        "headline": "Pixel Art Specialist",
        "skills": ["Pixel Art", "Aseprite", "Animation", "UI Art", "Color Theory"],
    },
    {
        "role": "3D Artist",
        "aliases": ["Environment Artist", "Character Artist"],
        "headline": "Game 3D Artist",
        "skills": ["Blender", "Maya", "Substance Painter", "Rigging", "PBR"],
    },
    {
        "role": "Technical Sound Designer",
        "aliases": ["Audio Engineer", "Game Audio Designer"],
        "headline": "Technical Sound Designer",
        "skills": ["FMOD", "Wwise", "Audio Mixing", "Unity", "Unreal Engine"],
    },
    {
        "role": "UI UX Designer",
        "aliases": ["UI Designer", "UX Designer"],
        "headline": "Game UI UX Designer",
        "skills": ["Figma", "UI Design", "UX Research", "Wireframing", "Prototyping"],
    },
    {
        "role": "Backend Game Developer",
        "aliases": ["Backend Engineer", "API Developer"],
        "headline": "Backend Game Services Engineer",
        "skills": ["Python", "FastAPI", "MongoDB", "Redis", "Docker"],
    },
    {
        "role": "Multiplayer Engineer",
        "aliases": ["Network Programmer", "Online Systems Engineer"],
        "headline": "Multiplayer Network Engineer",
        "skills": ["Netcode", "Matchmaking", "WebSockets", "Unity", "Unreal Engine"],
    },
    {
        "role": "QA Tester",
        "aliases": ["Game Tester", "QA Analyst"],
        "headline": "Game QA Tester",
        "skills": ["Bug Tracking", "Test Plans", "Regression Testing", "Jira", "Automation"],
    },
    {
        "role": "Technical Artist",
        "aliases": ["TA", "Pipeline Artist"],
        "headline": "Game Technical Artist",
        "skills": ["Shaders", "VFX", "Unity", "Unreal Engine", "Python"],
    },
]

SKILL_ALIAS_MAP = {
    "csharp": "C#",
    "unity-engine": "Unity",
    "ue5": "Unreal Engine",
    "ue4": "Unreal Engine",
    "networking": "Netcode",
    "mongo": "MongoDB",
    "figma-ui": "Figma",
    "quality-assurance": "QA",
}


def _seniority_and_rate(rng: random.Random) -> tuple[str, int, int]:
    roll = rng.random()
    if roll < 0.3:
        return "junior", rng.randint(20, 38), rng.randint(10, 20)
    if roll < 0.75:
        return "mid", rng.randint(35, 65), rng.randint(15, 30)
    return "senior", rng.randint(60, 110), rng.randint(10, 25)


def _build_display_name(index: int) -> str:
    first = FIRST_NAMES[index % len(FIRST_NAMES)]
    last = LAST_NAMES[(index * 3) % len(LAST_NAMES)]
    serial = (index // len(FIRST_NAMES)) + 1
    return f"{first} {last} {serial}"


def _canonicalize_skill(value: str) -> str:
    key = slugify(value)
    return SKILL_ALIAS_MAP.get(key, value.strip())


def build_freelancers(count: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    now = datetime.now(tz=timezone.utc)

    freelancers: list[dict] = []
    for idx in range(count):
        role_info = ROLE_LIBRARY[idx % len(ROLE_LIBRARY)]
        seniority, rate, availability = _seniority_and_rate(rng)

        base_skills = role_info["skills"]
        sampled = rng.sample(base_skills, k=min(4, len(base_skills)))

        if rng.random() < 0.35:
            cross_role = ROLE_LIBRARY[rng.randint(0, len(ROLE_LIBRARY) - 1)]
            sampled.extend(rng.sample(cross_role["skills"], k=1))

        skills = dedupe_keep_order(sampled)
        skills_normalized = dedupe_keep_order([_canonicalize_skill(skill) for skill in skills])

        role_tags = [role_info["role"]]
        if role_info["aliases"]:
            role_tags.append(role_info["aliases"][0])
        role_tags = dedupe_keep_order(role_tags)

        freelancer = {
            "display_name": _build_display_name(idx),
            "headline": role_info["headline"],
            "skills": skills,
            "skills_normalized": skills_normalized,
            "role_tags": role_tags,
            "role_tags_normalized": [role_info["role"]],
            "seniority": seniority,
            "hourly_rate_usd": rate,
            "availability_hours_per_week": availability,
            "timezone": TIMEZONES[idx % len(TIMEZONES)],
            "portfolio_links": [f"https://portfolio.example/{slugify(_build_display_name(idx))}"],
            "created_at": now,
            "updated_at": now,
        }
        freelancers.append(freelancer)

    return freelancers


def build_skill_catalog() -> list[dict]:
    canonical_to_aliases: dict[str, set[str]] = {}

    for role_info in ROLE_LIBRARY:
        for skill in role_info["skills"]:
            canonical = _canonicalize_skill(skill)
            canonical_to_aliases.setdefault(canonical, set())

    for alias_slug, canonical in SKILL_ALIAS_MAP.items():
        canonical_to_aliases.setdefault(canonical, set()).add(alias_slug.replace("-", " "))

    docs: list[dict] = []
    for canonical_name in sorted(canonical_to_aliases.keys()):
        aliases = sorted(canonical_to_aliases[canonical_name])
        docs.append(
            {
                "canonical_name": canonical_name,
                "slug": slugify(canonical_name),
                "aliases": aliases,
            }
        )
    return docs


def build_role_catalog() -> list[dict]:
    docs: list[dict] = []
    for role_info in ROLE_LIBRARY:
        docs.append(
            {
                "canonical_name": role_info["role"],
                "slug": slugify(role_info["role"]),
                "aliases": dedupe_keep_order(role_info["aliases"]),
                "common_skills": dedupe_keep_order(role_info["skills"]),
            }
        )
    return docs


def parse_args() -> ArgumentParser:
    parser = ArgumentParser(description="Seed fake freelancers and attribute catalogs.")
    parser.add_argument("--count", type=int, default=DEFAULT_COUNT, help="Number of freelancers to seed. Default: 60")
    parser.add_argument("--seed", type=int, default=20260328, help="Random seed for deterministic data generation.")
    parser.add_argument("--append", action="store_true", help="Append freelancers instead of wiping collections first.")
    return parser


async def main() -> None:
    parser = parse_args()
    args = parser.parse_args()

    if not settings.mongodb_uri:
        raise RuntimeError("MONGODB_URI is not configured")

    if args.count < 1:
        raise RuntimeError("--count must be at least 1")

    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_database]

    freelancers = build_freelancers(args.count, args.seed)
    skill_catalog = build_skill_catalog()
    role_catalog = build_role_catalog()

    if not args.append:
        await db[FREELANCER_PROFILES].delete_many({})
        await db[SKILL_CATALOG].delete_many({})
        await db[ROLE_CATALOG].delete_many({})

    for record in skill_catalog:
        await db[SKILL_CATALOG].replace_one(
            {"canonical_name": record["canonical_name"]},
            record,
            upsert=True,
        )

    for record in role_catalog:
        await db[ROLE_CATALOG].replace_one(
            {"canonical_name": record["canonical_name"]},
            record,
            upsert=True,
        )
    if freelancers:
        await db[FREELANCER_PROFILES].insert_many(freelancers)

    print(f"Seeded {len(freelancers)} freelancers")
    print(f"Seeded {len(skill_catalog)} skill catalog records")
    print(f"Seeded {len(role_catalog)} role catalog records")

    client.close()


if __name__ == "__main__":
    asyncio.run(main())

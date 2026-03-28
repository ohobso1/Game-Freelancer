from __future__ import annotations

import re
from collections.abc import Iterable

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.db.collections import ROLE_CATALOG, SKILL_CATALOG

_WHITESPACE_RE = re.compile(r"\s+")
_SKILL_FALLBACK_ALIASES = {
    "2d-game-development": "Unity",
    "2d-game-dev": "Unity",
    "game-development": "Unity",
    "systems-design": "Gameplay Systems",
    "system-design": "Gameplay Systems",
    "game-systems": "Gameplay Systems",
    "multiplayer": "Netcode",
}


def slugify(value: str) -> str:
    normalized = _WHITESPACE_RE.sub(" ", value.strip().lower())
    return normalized.replace(" ", "-")


def dedupe_keep_order(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        cleaned = item.strip()
        if not cleaned:
            continue
        marker = cleaned.lower()
        if marker in seen:
            continue
        seen.add(marker)
        result.append(cleaned)
    return result


async def _build_alias_map(db: AsyncIOMotorDatabase, collection: str) -> dict[str, str]:
    documents = await db[collection].find({}).to_list(length=2000)

    alias_map: dict[str, str] = {}
    for doc in documents:
        canonical = str(doc.get("canonical_name", "")).strip()
        if not canonical:
            continue

        alias_values = [canonical]
        alias_values.extend(doc.get("aliases", []))

        for alias in alias_values:
            alias_key = slugify(str(alias))
            if alias_key:
                alias_map[alias_key] = canonical

    return alias_map


async def normalize_skills(db: AsyncIOMotorDatabase, values: Iterable[str]) -> list[str]:
    alias_map = await _build_alias_map(db, SKILL_CATALOG)
    for alias, canonical in _SKILL_FALLBACK_ALIASES.items():
        alias_map.setdefault(alias, canonical)

    output: list[str] = []
    for value in values:
        key = slugify(value)
        if not key:
            continue
        output.append(alias_map.get(key, value.strip()))

    return dedupe_keep_order(output)


async def normalize_roles(db: AsyncIOMotorDatabase, values: Iterable[str]) -> list[str]:
    alias_map = await _build_alias_map(db, ROLE_CATALOG)

    output: list[str] = []
    for value in values:
        key = slugify(value)
        if not key:
            continue
        output.append(alias_map.get(key, value.strip()))

    return dedupe_keep_order(output)

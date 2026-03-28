import json

import httpx

from app.config import settings


class GeminiClient:
    def __init__(self) -> None:
        self._endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{settings.gemini_model}:generateContent"
        )

    async def parse_project_prompt(self, raw_prompt: str) -> dict:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        instruction = (
            "You are a parser for game project staffing requirements. "
            "Return JSON only with keys: project_summary, roles, required_skills, "
            "optional_skills, constraints, confidence. "
            "roles must contain role_name, count, seniority, must_have_skills, "
            "nice_to_have_skills. constraints may contain budget_min_usd, "
            "budget_max_usd, timeline_weeks, timezone_overlap_required. "
            "Do not include markdown or extra text."
        )

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{instruction}\n\nProject prompt:\n{raw_prompt}"
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "responseMimeType": "application/json",
            },
        }

        async with httpx.AsyncClient(timeout=settings.gemini_timeout_seconds) as client:
            response = await client.post(
                self._endpoint,
                params={"key": settings.gemini_api_key},
                json=payload,
            )
            response.raise_for_status()

        body = response.json()
        text = body["candidates"][0]["content"]["parts"][0]["text"]
        return json.loads(text)

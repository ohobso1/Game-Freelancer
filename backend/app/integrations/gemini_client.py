import json

import httpx

from app.config import settings


class GeminiClient:
    def __init__(self) -> None:
        self._base_endpoint = "https://generativelanguage.googleapis.com/v1beta/models"

    def _candidate_models(self) -> list[str]:
        # Some API keys do not have access to every Gemini model id.
        defaults = [
            settings.gemini_model,
            "gemini-flash-latest",
            "gemini-2.5-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-pro",
        ]

        deduped: list[str] = []
        seen: set[str] = set()
        for model in defaults:
            candidate = str(model).strip()
            if not candidate or candidate in seen:
                continue
            seen.add(candidate)
            deduped.append(candidate)

        return deduped

    def _build_instruction(
        self,
        raw_prompt: str,
        allowed_skills: list[str] | None,
        allowed_roles: list[str] | None,
    ) -> str:
        instruction = (
            "You are a parser for game project staffing requirements. "
            "Return JSON only with keys: project_summary, roles, required_skills, "
            "optional_skills, constraints, confidence. "
            "roles must contain role_name, count, seniority, must_have_skills, "
            "nice_to_have_skills. constraints may contain budget_min_usd, "
            "budget_max_usd, timeline_weeks, timezone_overlap_required. "
            "Do not include markdown or extra text."
        )

        if allowed_roles:
            instruction += (
                " Use role_name values from this canonical role list whenever possible: "
                f"{', '.join(allowed_roles[:120])}."
            )

        if allowed_skills:
            instruction += (
                " Use required_skills and optional_skills values from this canonical skill list whenever possible: "
                f"{', '.join(allowed_skills[:300])}."
            )

        instruction += f"\n\nProject prompt:\n{raw_prompt}"
        return instruction

    async def parse_project_prompt(
        self,
        raw_prompt: str,
        allowed_skills: list[str] | None = None,
        allowed_roles: list[str] | None = None,
    ) -> tuple[dict, str]:
        if not settings.gemini_api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        instruction = self._build_instruction(raw_prompt, allowed_skills, allowed_roles)

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": instruction
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
            last_error: str | None = None

            for model in self._candidate_models():
                endpoint = f"{self._base_endpoint}/{model}:generateContent"
                try:
                    response = await client.post(
                        endpoint,
                        params={"key": settings.gemini_api_key},
                        json=payload,
                    )

                    if response.status_code == 404:
                        last_error = f"Model '{model}' is not available for this API key or has been retired."
                        continue

                    response.raise_for_status()
                    body = response.json()
                    text = body["candidates"][0]["content"]["parts"][0]["text"]
                    return json.loads(text), model
                except httpx.HTTPStatusError as exc:
                    status = exc.response.status_code
                    if status == 404:
                        last_error = f"Model '{model}' is not available for this API key or has been retired."
                        continue
                    raise RuntimeError(f"Gemini API request failed with HTTP {status}.") from exc
                except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
                    raise RuntimeError("Gemini response was not valid JSON content.") from exc

        raise RuntimeError(last_error or "No compatible Gemini model is available for this API key. Try GEMINI_MODEL=gemini-flash-latest.")

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

try:
    import openai
except Exception:  # noqa: BLE001
    openai = None  # type: ignore

logger = logging.getLogger(__name__)


def build_prompt(
    question: str,
    *,
    company: dict[str, Any] | None = None,
    technology: dict[str, Any] | None = None,
    evidence_standards: str | None = None,
    credibility_scoring: str | None = None,
    deliverable_guidelines: str | None = None,
    audience: str | None = None,
    preferences: str | None = None,
) -> str:
    """Return a prompt for the OpenAI model."""

    evidence_text = evidence_standards or ""
    scoring_text = credibility_scoring or ""
    guidelines_text = deliverable_guidelines or ""
    audience_text = audience or ""
    prefs_text = preferences or ""
    company_text = json.dumps(company) if company else ""
    tech_text = json.dumps(technology) if technology else ""

    prompt = (
        "You are the Unitron insight orchestrator.\n"
        f"Adhere to the following evidence standards:\n{evidence_text}\n"
        f"Apply the credibility scoring formula:\n{scoring_text}\n"
        f"Follow these deliverable guidelines:\n{guidelines_text}\n"
        f"Audience: {audience_text}\n"
        f"Preferences: {prefs_text}\n"
        f"Company: {company_text}\n"
        f"Technology: {tech_text}\n"
        f"Question: {question}\n"
        "Respond only with a JSON payload."
    )
    return prompt


async def generate_report(
    prompt: str, *, timeout: int = 30, retries: int = 2
) -> dict[str, Any]:
    """Call OpenAI with ``prompt`` and return parsed JSON.

    Timeouts and transient errors trigger retries. On failure the return
    value includes ``{"error": "[Data Gap]"}``.
    """

    if openai is None:
        logger.error("OpenAI library not available")
        return {"error": "[Data Gap]"}

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("OPENAI_API_KEY missing")
        return {"error": "[Data Gap]"}

    client = openai.AsyncOpenAI(api_key=api_key)
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = await asyncio.wait_for(
                client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Return JSON only."},
                        {"role": "user", "content": prompt},
                    ],
                ),
                timeout=timeout,
            )
            content = resp.choices[0].message.content.strip()
            return json.loads(content)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            await asyncio.sleep(2 ** attempt)
    logger.error("OpenAI request failed", exc_info=last_exc)
    return {"error": "[Data Gap]"}

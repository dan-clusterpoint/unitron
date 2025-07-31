from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any
from json import JSONDecodeError

try:
    import openai
except Exception:  # noqa: BLE001
    openai = None  # type: ignore

logger = logging.getLogger(__name__)

# Default token limit for OpenAI responses
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "800"))

# Canonical schema used when prompting the LLM. The example combines a
# TypeScript interface and JSON snippet so tests can verify the keys
# are present in the service response.
NEXT_BEST_ACTION_EXAMPLE = """
```ts
interface NextBestAction {
  title: string;
  description: string;
  action: string;
  source: { url: string };
  credibilityScore: number;
}
```

```json
{
  "title": "Improve caching",
  "description": "Use caching to reduce load",
  "action": "Add HTTP cache middleware",
  "source": { "url": "https://example.com" },
  "credibilityScore": 0.9
}
```
"""


async def call_openai_with_retry(
    messages: list[dict[str, str]],
    *,
    max_tokens: int | None = None,
    model: str | None = None,
) -> tuple[str, bool]:
    """Call OpenAI with retry and return ``(content, degraded)``."""

    if openai is None:
        raise RuntimeError("OpenAI library not available")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    selected_model = model or os.getenv("OPENAI_MODEL", "gpt-4")

    client = openai.AsyncOpenAI(api_key=api_key)
    delays = [1, 2, 4]
    for attempt in range(3):
        try:
            resp = await client.chat.completions.create(
                model=selected_model,
                messages=messages,
                **({"max_tokens": max_tokens} if max_tokens is not None else {}),
            )
            content = resp.choices[0].message.content.strip()
            return content, False
        except Exception as exc:  # noqa: BLE001
            status = getattr(exc, "status_code", getattr(exc, "status", None))
            if status not in (429, 500):
                raise
            if attempt < 2:
                await asyncio.sleep(delays[attempt])
    logger.warning("OpenAI request failed after retries")
    return "", True


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
    prompt += "\n" + NEXT_BEST_ACTION_EXAMPLE
    prompt += ("\nReply only with JSON matching the above structure inside a"
               " ```json code block. Keep empty arrays/objects.")
    return prompt


def _extract_json_block(text: str) -> str:
    """Return ``text`` minus surrounding ```json fences, if present."""

    stripped = text.strip()
    if stripped.startswith("```"):
        lines = stripped.splitlines()
        if len(lines) >= 3 and lines[0].startswith("```") and lines[-1].startswith("```"):
            inner = "\n".join(lines[1:-1]).strip()
            if inner.lower().startswith("json\n"):
                inner = inner.split("\n", 1)[1].strip()
            return inner
    return stripped


async def generate_report(
    prompt: str, *, timeout: int = 30, retries: int = 2
) -> dict[str, Any]:
    """Call OpenAI with ``prompt`` and return parsed JSON.

    Timeouts and transient errors trigger retries. If the response cannot be
    parsed as JSON, the raw ``content`` is returned as
    ``{"insight": content, "degraded": True}``. On other failures the return
    value includes ``{"error": "[Data Gap]"}``.
    """

    messages = [
        {"role": "system", "content": "Return JSON only."},
        {"role": "user", "content": prompt},
    ]
    try:
        content, degraded = await asyncio.wait_for(
            call_openai_with_retry(messages, max_tokens=OPENAI_MAX_TOKENS),
            timeout=timeout,
        )
    except Exception:  # noqa: BLE001
        logger.error("OpenAI request failed", exc_info=True)
        return {"error": "[Data Gap]"}

    if degraded:
        return {"error": "[Data Gap]"}
    try:
        return json.loads(_extract_json_block(content))
    except JSONDecodeError:
        return {"insight": content, "degraded": True}

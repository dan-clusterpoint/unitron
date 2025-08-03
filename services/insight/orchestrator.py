from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from typing import Any

try:  # Optional dependency
    import openai
except Exception:  # noqa: BLE001
    openai = None  # type: ignore

logger = logging.getLogger(__name__)

# Token and temperature defaults
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1100"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.3"))

# Markdown outline for the orchestrator
MARKDOWN_OUTLINE = """
## Executive Summary
*One sentence.*

## Next-Best Actions
### {Action 1}
- **Reasoning:** …
- **Benefit:** …

## Personas
| ID | Name | Role | Goal | Challenge |
|----|------|------|------|-----------|
| …  | …    | …    | …    | …         |

If no actions, write: _No recommended actions could be generated for this analysis._
"""


async def call_openai_with_retry(
    messages: list[dict[str, str]],
    *,
    max_tokens: int | None = None,
    model: str | None = None,
    stream: bool = False,
) -> tuple[str, str, bool]:
    """Call OpenAI with retry and return ``(content, finish_reason, degraded)``."""

    if openai is None:
        raise RuntimeError("OpenAI library not available")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY missing")

    selected_model = model or os.getenv("OPENAI_MODEL", "gpt-4")

    client = openai.AsyncOpenAI(api_key=api_key)
    delays = [1, 2, 4]
    params: dict[str, Any] = {
        "model": selected_model,
        "messages": messages,
        "temperature": OPENAI_TEMPERATURE,
    }
    if max_tokens is not None:
        params["max_tokens"] = max_tokens

    for attempt in range(3):
        try:
            if stream:
                content = ""
                finish_reason = "stop"
                events = await client.chat.completions.create(stream=True, **params)
                async for event in events:
                    delta = (
                        event.choices[0].delta.get("content")
                        if hasattr(event.choices[0], "delta")
                        else None
                    )
                    if delta:
                        content += delta
                    fr = getattr(event.choices[0], "finish_reason", None)
                    if fr:
                        finish_reason = fr
                logger.info("openai streaming usage unavailable")
                return content.strip(), finish_reason, False
            resp = await client.chat.completions.create(**params)
            content = resp.choices[0].message.content or ""
            finish_reason = getattr(resp.choices[0], "finish_reason", "stop")
            usage = getattr(resp, "usage", None)
            if usage:
                prompt_tokens = getattr(usage, "prompt_tokens", 0) or 0
                completion_tokens = getattr(usage, "completion_tokens", 0) or 0
                total_tokens = getattr(usage, "total_tokens", 0) or 0
                cost = prompt_tokens * 0.000005 + completion_tokens * 0.000015
                logger.info(
                    "openai usage prompt=%s completion=%s total=%s cost=%s",
                    prompt_tokens,
                    completion_tokens,
                    total_tokens,
                    cost,
                )
            else:
                logger.info("openai usage unavailable")
            return content.strip(), finish_reason, False
        except Exception as exc:  # noqa: BLE001
            status = getattr(exc, "status_code", getattr(exc, "status", None))
            if status not in (429, 500):
                raise
            if attempt < 2:
                await asyncio.sleep(delays[attempt])
    logger.warning("OpenAI request failed after retries")
    return "", "error", True


FENCE_RE = re.compile(r"```(?:markdown|md)?\n(.*?)```", re.DOTALL | re.IGNORECASE)


def _extract_markdown(text: str) -> tuple[str, bool]:
    """Return extracted markdown and whether degradation occurred."""

    degraded = False
    stripped = text.strip()
    match = FENCE_RE.search(stripped)
    if match:
        markdown = match.group(1).strip()
    else:
        if "```" in stripped:
            degraded = True
        markdown = stripped

    if not markdown or len(markdown) < 10 or not re.search(r"(^|\n)[#*-]", markdown):
        degraded = True
    return markdown, degraded


async def generate_report(prompt: str, *, timeout: int = 30) -> dict[str, Any]:
    """Return ``{"markdown": str, "degraded": bool}`` from the model response."""

    messages = [
        {"role": "system", "content": "Return GitHub-flavoured Markdown."},
        {"role": "user", "content": prompt},
    ]
    try:
        content, finish_reason, degraded_call = await asyncio.wait_for(
            call_openai_with_retry(
                messages,
                max_tokens=OPENAI_MAX_TOKENS,
            ),
            timeout=timeout,
        )
    except Exception:  # noqa: BLE001
        logger.error("OpenAI request failed", exc_info=True)
        return {"markdown": "", "degraded": True}

    logger.info(
        "finish_reason=%s preview=%s",
        finish_reason,
        content[:300],
    )

    try:
        markdown, degraded_extract = _extract_markdown(content)
    except Exception:  # noqa: BLE001
        logger.exception("Markdown extraction failed")
        return {"markdown": content, "degraded": True}

    degraded = degraded_call or degraded_extract or finish_reason == "length"
    return {"markdown": markdown, "degraded": degraded}


def build_prompt(
    question: str,
    *,
    company: dict[str, Any] | None = None,
    technology: dict[str, Any] | None = None,
    industry: str | None = None,
    pain_point: str | None = None,
    stack: list[dict[str, str]] | None = None,
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
    industry_text = industry or ""
    pain_text = pain_point or ""
    stack_lines = [
        f"  - {item.get('category', '')}: {item.get('vendor', '')}"
        for item in (stack or [])
    ]
    context_text = "\n".join(
        [
            "Context",
            f"- Industry: {industry_text}",
            f"- Pain point: {pain_text}",
            "- Declared stack:",
            *stack_lines,
        ]
    )

    prompt = (
        "You are the Unitron insight orchestrator.\n"
        f"Adhere to the following evidence standards:\n{evidence_text}\n"
        f"Apply the credibility scoring formula:\n{scoring_text}\n"
        f"Follow these deliverable guidelines:\n{guidelines_text}\n"
        f"Audience: {audience_text}\n"
        f"Preferences: {prefs_text}\n"
        f"{context_text}\n"
        f"Company: {company_text}\n"
        f"Technology: {tech_text}\n"
        f"Question: {question}\n"
        "Return ONLY GitHub-flavoured Markdown using the following outline:\n"
    )
    prompt += MARKDOWN_OUTLINE
    return prompt

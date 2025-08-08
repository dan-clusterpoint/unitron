from __future__ import annotations

import os
import json
import logging
import re
import time
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from services.shared import SecurityHeadersMiddleware
from utils.logging import redact
from contextlib import asynccontextmanager
import httpx
from pydantic import BaseModel, ValidationError, Field

try:
    import jsonschema
except Exception:  # noqa: BLE001
    jsonschema = None  # type: ignore
from starlette.responses import JSONResponse
import base64
import csv
import io
from typing import Any
from services.insight import orchestrator

try:  # Optional dependency
    import openai
except Exception:  # noqa: BLE001
    openai = None  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient()
    try:
        yield
    finally:
        await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)

ui_origin = os.getenv("UI_ORIGIN")
allow = [ui_origin] if ui_origin else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization"],
)
app.add_middleware(SecurityHeadersMiddleware)

logger = logging.getLogger(__name__)

# Simple in-memory metrics
metrics: dict[str, Any] = {
    "generate-insights": {
        "requests": 0,
        "scope": 0,
        "sources": 0,
        "duration": 0.0,
    },
    "research": {"requests": 0, "scope": 0, "sources": 0, "duration": 0.0},
    "postprocess-report": {
        "requests": 0,
        "scope": 0,
        "sources": 0,
        "duration": 0.0,
    },
    "insight-and-personas": {
        "requests": 0,
        "scope": 0,
        "sources": 0,
        "duration": 0.0,
    },
    "insight": {"requests": 0, "scope": 0, "sources": 0, "duration": 0.0},
    "aeris": {"requests": 0, "scope": 0, "sources": 0, "duration": 0.0},
    "data_gaps": 0,
}


def _record_metrics(
    endpoint: str, scope: int, sources: int, duration: float, gap_count: int
) -> None:
    """Update in-memory metrics and log them."""
    data = metrics.setdefault(
        endpoint, {"requests": 0, "scope": 0, "sources": 0, "duration": 0.0}
    )
    data["requests"] += 1
    data["scope"] += scope
    data["sources"] += sources
    data["duration"] += duration
    metrics["data_gaps"] += gap_count
    logger.info(
        "%s scope=%d sources=%d duration=%.3f gap_count=%d",
        endpoint,
        scope,
        sources,
        duration,
        gap_count,
    )


def _append_size_warning(data: dict[str, Any]) -> None:
    """Add size warning to ``meta.warnings`` if serialized ``data`` is large."""
    try:
        size = len(json.dumps(data).encode())
    except Exception:
        return
    if size > 250 * 1024:  # 250 KB
        meta = data.setdefault("meta", {})
        warnings = meta.setdefault("warnings", [])
        warnings.append("response exceeds 250KB")


class InsightRequest(BaseModel):
    text: str


class ReadyResponse(BaseModel):
    ready: bool


class ResearchRequest(BaseModel):
    topic: str


class AerisRequest(BaseModel):
    url: str
    notes: str | None = None


class MarkdownResponse(BaseModel):
    markdown: str
    degraded: bool


class InsightPersonaRequest(BaseModel):
    url: str
    industry: str | None = None
    pain_point: str | None = Field(default=None, max_length=280)
    stack: list[dict[str, str]] = Field(default_factory=list)
    evidence_standards: str | None = Field(
        default=None,
        example="Use peer-reviewed data when available",
    )
    credibility_scoring: str | None = Field(
        default=None,
        example="Score evidence 1-5 based on reliability",
    )
    deliverable_guidelines: str | None = Field(
        default=None,
        example="Write deliverables in plain language",
    )
    audience: str | None = Field(
        default=None,
        example="CTO and senior engineers",
    )
    preferences: str | None = Field(
        default=None,
        example="Focus on open-source solutions",
    )


def _validate_with_schema(data: dict, model: type[BaseModel]) -> BaseModel:
    """Validate ``data`` using JSON Schema or Pydantic models."""
    if jsonschema is not None:
        jsonschema.validate(data, model.model_json_schema())
    return model.model_validate(data)


def _sanitize(text: str) -> str:
    """Return a compact single-line version of ``text``."""
    return " ".join(text.strip().split())


def _to_persona_list(gen: dict) -> list[dict]:
    """Return list of persona dicts from ``gen`` mapping."""
    out = []
    if isinstance(gen, dict):
        for k, v in gen.items():
            if isinstance(v, dict):
                out.append({"id": k, **v})
    return out


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/metrics")
async def metrics_endpoint() -> JSONResponse:
    """Return accumulated metrics."""
    return JSONResponse(metrics)


@app.get("/ready", response_model=ReadyResponse, tags=["Service"])
async def ready() -> ReadyResponse:
    return ReadyResponse(ready=True)


@app.post("/generate-insights")
async def generate_insights(req: InsightRequest) -> JSONResponse:
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    sanitized = _sanitize(req.text)
    logger.debug("generate-insights request: %s", redact(sanitized))
    start = time.perf_counter()
    try:
        result = await orchestrator.generate_report(
            f"Generate concise insights.\n{sanitized}"
        )
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to generate insights")

    _append_size_warning(result)
    duration = time.perf_counter() - start
    scope = len(sanitized)
    sources = len(re.findall(r"https?://", json.dumps(result)))
    gap_count = json.dumps(result).count("[Data Gap]")
    _record_metrics("generate-insights", scope, sources, duration, gap_count)
    logger.debug("generate-insights response: %s", redact(json.dumps(result)))
    return JSONResponse(result)


@app.post("/research")
async def research(data: dict) -> JSONResponse:
    """Return research summary for a topic."""
    try:
        req = _validate_with_schema(data, ResearchRequest)
    except (ValidationError, Exception):
        raise HTTPException(status_code=400, detail="Invalid request")
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Empty topic")
    sanitized = _sanitize(req.topic)
    logger.debug("research request: %s", redact(sanitized))
    start = time.perf_counter()
    try:
        result = await orchestrator.generate_report(
            f"Provide a short research summary.\n{sanitized}"
        )
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to generate research")

    _append_size_warning(result)
    duration = time.perf_counter() - start
    scope = len(sanitized)
    sources = len(re.findall(r"https?://", json.dumps(result)))
    gap_count = json.dumps(result).count("[Data Gap]")
    _record_metrics("research", scope, sources, duration, gap_count)
    logger.debug("research response: %s", redact(json.dumps(result)))
    try:
        _validate_with_schema(result, MarkdownResponse)
    except (ValidationError, Exception):
        raise HTTPException(status_code=400, detail="Invalid response")
    return JSONResponse(result)


@app.post("/insight", response_model=MarkdownResponse)
async def insight(data: dict[str, Any]) -> JSONResponse:
    """Return markdown insights for text or URL-based payloads."""

    if "text" in data:
        try:
            req = _validate_with_schema(data, InsightRequest)
        except (ValidationError, Exception):
            raise HTTPException(status_code=400, detail="Invalid request")
        if not req.text.strip():
            raise HTTPException(status_code=400, detail="Empty text")
        sanitized = _sanitize(req.text)
        logger.debug("insight text request: %s", redact(sanitized))
        start = time.perf_counter()
        try:
            result = await orchestrator.generate_report(
                f"Generate concise insights.\n{sanitized}"
            )
        except Exception:  # noqa: BLE001
            raise HTTPException(status_code=500, detail="Failed to generate insights")
        _append_size_warning(result)
        duration = time.perf_counter() - start
        scope = len(sanitized)
        sources = len(re.findall(r"https?://", json.dumps(result)))
        gap_count = json.dumps(result).count("[Data Gap]")
        _record_metrics("generate-insights", scope, sources, duration, gap_count)
        logger.debug("insight text response: %s", redact(json.dumps(result)))
        return JSONResponse(result)

    try:
        req = _validate_with_schema(data, InsightPersonaRequest)
    except (ValidationError, Exception):
        raise HTTPException(status_code=400, detail="Invalid request")

    logger.debug("insight request: %s", redact(json.dumps(req.model_dump())))
    start = time.perf_counter()
    company = {"url": req.url}
    tech: dict[str, Any] = {"declared": req.stack}

    prompt = orchestrator.build_prompt(
        "Generate next-best-action insights.",
        company=company,
        technology=tech,
        industry=req.industry,
        pain_point=req.pain_point,
        stack=req.stack,
        evidence_standards=req.evidence_standards,
        credibility_scoring=req.credibility_scoring,
        deliverable_guidelines=req.deliverable_guidelines,
        audience=req.audience,
        preferences=req.preferences,
    )

    try:
        result = await orchestrator.generate_report(prompt)
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=500, detail="Failed to generate insight")

    _append_size_warning(result)
    duration = time.perf_counter() - start
    scope = len(json.dumps(req.model_dump()))
    sources = len(re.findall(r"https?://", json.dumps(result)))
    gap_count = json.dumps(result).count("[Data Gap]")
    _record_metrics("insight", scope, sources, duration, gap_count)
    logger.debug("insight response: %s", redact(json.dumps(result)))
    return JSONResponse(result)


app.add_api_route("/insight/", insight, methods=["POST"], include_in_schema=False)


async def _generate_alt_text(description: str) -> str:
    """Return alt text for ``description`` limited to 15 words."""
    text = _sanitize(description)[:200]
    if not text:
        return ""
    if not os.getenv("OPENAI_API_KEY") or openai is None:
        return ""
    try:
        alt, _, _ = await orchestrator.call_openai_with_retry(
            [
                {
                    "role": "user",
                    "content": f"Describe the image in under 15 words: {text}",
                }
            ],
            max_tokens=30,
        )
    except Exception:  # noqa: BLE001
        return ""
    words = alt.split()
    if len(words) > 15:
        alt = " ".join(words[:15])
    return alt


async def create_markdown(report: dict[str, Any]) -> str:
    """Return Markdown representation of ``report`` with generated alt text."""
    lines: list[str] = []
    title = report.get("title")
    if title:
        lines.append(f"# {title}")

    summary = report.get("summary")
    if summary:
        lines.append(str(summary))

    for key, value in report.items():
        if key in {"title", "summary", "visuals", "scenarios"}:
            continue
        lines.append(f"## {key}")
        lines.append(str(value))

    visuals = report.get("visuals", [])
    if visuals:
        lines.append("## Visuals")
        for vis in visuals:
            desc = vis.get("description") or ""
            alt = await _generate_alt_text(desc)
            url = vis.get("url", "")
            lines.append(f"![{alt}]({url})")

    return "\n\n".join(lines)


def create_scenario_csv(report: dict[str, Any]) -> str:
    """Return CSV text for the ``scenarios`` in ``report``."""
    scenarios = report.get("scenarios", [])
    if not scenarios:
        return ""
    fieldnames = sorted({k for sc in scenarios for k in sc})
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(scenarios)
    return output.getvalue()


class PostProcessRequest(BaseModel):
    report: dict[str, Any]


@app.post("/postprocess-report")
async def postprocess_report(req: PostProcessRequest) -> JSONResponse:
    """Return downloads with markdown and scenario CSV representations."""
    report = req.report
    logger.debug("postprocess-report request: %s", redact(json.dumps(report)))
    start = time.perf_counter()
    markdown = await create_markdown(report)
    csv_text = create_scenario_csv(report)
    downloads: dict[str, str] = {}
    if markdown:
        downloads["markdown"] = base64.b64encode(markdown.encode()).decode()
    if csv_text:
        downloads["scenarios"] = base64.b64encode(csv_text.encode()).decode()
    result = {"report": report, "downloads": downloads}
    _append_size_warning(result)
    duration = time.perf_counter() - start
    scope = len(json.dumps(report))
    sources = len(re.findall(r"https?://", json.dumps(result)))
    gap_count = json.dumps(result).count("[Data Gap]")
    _record_metrics("postprocess-report", scope, sources, duration, gap_count)
    logger.debug("postprocess-report response: %s", redact(json.dumps(result)))
    return JSONResponse(result)


@app.post("/insight-and-personas")
async def insight_and_personas(req: InsightPersonaRequest) -> JSONResponse:
    """Return insight and persona reports using the orchestrator."""
    logger.debug(
        "insight-and-personas request: %s",
        redact(json.dumps(req.model_dump())),
    )
    start = time.perf_counter()
    company = {"url": req.url}
    tech: dict[str, Any] = {"declared": req.stack}

    insight_prompt = orchestrator.build_prompt(
        "Generate next-best-action insights.",
        company=company,
        technology=tech,
        industry=req.industry,
        pain_point=req.pain_point,
        stack=req.stack,
        evidence_standards=req.evidence_standards,
        credibility_scoring=req.credibility_scoring,
        deliverable_guidelines=req.deliverable_guidelines,
        audience=req.audience,
        preferences=req.preferences,
    )

    persona_prompt = orchestrator.build_prompt(
        "Generate buyer personas.",
        company=company,
        technology=tech,
        industry=req.industry,
        pain_point=req.pain_point,
        stack=req.stack,
        evidence_standards=req.evidence_standards,
        credibility_scoring=req.credibility_scoring,
        deliverable_guidelines=req.deliverable_guidelines,
        audience=req.audience,
        preferences=req.preferences,
    )

    try:
        insight_raw, personas_raw = await asyncio.gather(
            orchestrator.generate_report(insight_prompt),
            orchestrator.generate_report(persona_prompt),
        )

        insight_text: Any
        if isinstance(insight_raw, dict):
            for key in ("insight", "report", "summary"):
                if key in insight_raw:
                    insight_text = insight_raw[key]
                    break
            else:
                insight_text = insight_raw
        else:
            insight_text = insight_raw

        personas_source: Any
        if (
            isinstance(personas_raw, dict)
            and "generated_buyer_personas" in personas_raw
        ):
            personas_source = personas_raw["generated_buyer_personas"]
        else:
            personas_source = personas_raw
        personas_list = _to_persona_list(personas_source)
        if not personas_list:
            from urllib.parse import urlparse

            domain = urlparse(req.url).netloc or req.url
            tech_names = [item.get("vendor", "") for item in req.stack]
            tech_text = (
                ", ".join(sorted({name for name in tech_names if name})) or "unknown"
            )
            personas_list = [
                {
                    "id": "company",
                    "name": domain,
                    "role": "unknown",
                    "goal": "unknown",
                    "challenge": "unknown",
                    "demographics": "unknown",
                    "needs": "unknown",
                    "goals": "unknown",
                },
                {
                    "id": "tech",
                    "name": tech_text,
                    "role": "unknown",
                    "goal": "unknown",
                    "challenge": "unknown",
                    "demographics": "unknown",
                    "needs": "unknown",
                    "goals": "unknown",
                },
            ]

        actions: list[Any] = []
        if isinstance(insight_raw, dict):
            for key in (
                "actions",
                "action_items",
                "next_best_actions",
                "NextBestAction",
            ):
                if key in insight_raw:
                    val = insight_raw[key]
                    if key == "NextBestAction" and val is not None:
                        actions = [val]
                    elif isinstance(val, list):
                        actions = val
                    elif val is not None:
                        actions = [val]
                    break

        if not actions and isinstance(insight_text, dict):
            if "NextBestAction" in insight_text:
                val = insight_text.pop("NextBestAction")
                if val is not None:
                    actions = [val]
            elif {"title", "action"}.issubset(insight_text.keys()):
                actions = [insight_text]
                insight_text = ""

        evidence_text = ""
        evidence_obj: Any
        if isinstance(insight_text, dict):
            evidence_text = insight_text.pop("evidence", "") or ""
            persona_obj = insight_text.pop("Persona", None)
            if isinstance(persona_obj, dict):
                persona_defaults = {
                    "id": "unknown",
                    "name": "unknown",
                    "role": "unknown",
                    "goal": "unknown",
                    "challenge": "unknown",
                    "demographics": "unknown",
                    "needs": "unknown",
                    "goals": "unknown",
                }
                persona_defaults.update(persona_obj)
                personas_list.append(persona_defaults)
            if actions or evidence_text:
                evidence_obj = {"insights": actions, "evidence": evidence_text}
            else:
                evidence_obj = insight_text
        else:
            if isinstance(insight_raw, dict):
                evidence_text = insight_raw.get("evidence", "") or ""
            elif isinstance(insight_text, str):
                evidence_text = insight_text
            evidence_obj = {"insights": actions, "evidence": evidence_text}

        insight_obj = {"actions": actions, "evidence": evidence_obj}

        degraded = False
        if (
            isinstance(insight_raw, dict) and insight_raw.get("error") == "[Data Gap]"
        ) or (
            isinstance(personas_raw, dict) and personas_raw.get("error") == "[Data Gap]"
        ):
            degraded = True
        if any(
            field in (None, "")
            for field in (
                req.evidence_standards,
                req.credibility_scoring,
                req.deliverable_guidelines,
                req.audience,
                req.preferences,
            )
        ):
            degraded = True

        result = {
            "insight": insight_obj,
            "personas": personas_list,
            "degraded": degraded,
        }
        _append_size_warning(result)
        duration = time.perf_counter() - start
        scope = len(json.dumps(req.model_dump()))
        sources = len(re.findall(r"https?://", json.dumps(result)))
        gap_count = json.dumps(result).count("[Data Gap]")
        _record_metrics("insight-and-personas", scope, sources, duration, gap_count)
        logger.debug(
            "insight-and-personas response: %s",
            redact(json.dumps(result)),
        )
        return JSONResponse(result)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, detail=str(exc))


@app.post("/aeris")
async def aeris(data: dict[str, Any]) -> JSONResponse:
    """Return AERIS analysis for a URL and optional notes."""
    try:
        req = _validate_with_schema(data, AerisRequest)
    except (ValidationError, Exception):
        raise HTTPException(status_code=400, detail="Invalid request")

    prompt = f"Analyze {req.url} using the AERIS framework."
    if req.notes:
        prompt += f"\nNotes: {req.notes}"
    prompt += (
        "\nReturn JSON with keys: core_score, signal_breakdown, peers, "
        "variants, opportunities, narratives."
    )

    start = time.perf_counter()
    try:
        content, _finish, degraded_call = await orchestrator.call_openai_with_retry(
            [
                {"role": "system", "content": "Return JSON."},
                {"role": "user", "content": prompt},
            ],
            model=os.getenv("OPENAI_AERIS_MODEL"),
        )
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc))

    try:
        parsed = json.loads(content) if content else {}
    except Exception:  # noqa: BLE001
        parsed = {}
        degraded_call = True

    result = {
        "core_score": parsed.get("core_score", 0),
        "signal_breakdown": parsed.get("signal_breakdown", []),
        "peers": parsed.get("peers", []),
        "variants": parsed.get("variants", []),
        "opportunities": parsed.get("opportunities", []),
        "narratives": parsed.get("narratives", []),
        "degraded": degraded_call,
    }

    _append_size_warning(result)
    duration = time.perf_counter() - start
    scope = len(json.dumps(req.model_dump()))
    sources = len(re.findall(r"https?://", json.dumps(result)))
    gap_count = json.dumps(result).count("[Data Gap]")
    _record_metrics("aeris", scope, sources, duration, gap_count)
    logger.debug("aeris response: %s", redact(json.dumps(result)))
    return JSONResponse(result)

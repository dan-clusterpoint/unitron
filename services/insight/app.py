from __future__ import annotations

import os
import json
import logging
import re
import time
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ValidationError

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

app = FastAPI()

origins = [os.getenv("UI_ORIGIN", "*")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger = logging.getLogger(__name__)

# Simple in-memory metrics
metrics: dict[str, Any] = {
    "generate-insights": {"requests": 0, "scope": 0, "sources": 0, "duration": 0.0},
    "research": {"requests": 0, "scope": 0, "sources": 0, "duration": 0.0},
    "postprocess-report": {"requests": 0, "scope": 0, "sources": 0, "duration": 0.0},
    "insight-and-personas": {"requests": 0, "scope": 0, "sources": 0, "duration": 0.0},
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


class ResearchResponse(BaseModel):
    summary: str


class InsightPersonaRequest(BaseModel):
    url: str
    martech: dict[str, list[str]] | None = None
    cms: list[str] | None = None
    cms_manual: str | None = None


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
    start = time.perf_counter()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or openai is None:
        raise HTTPException(status_code=503, detail="OpenAI not configured")
    client = openai.AsyncOpenAI(api_key=api_key)
    try:
        resp = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Generate concise insights."},
                {"role": "user", "content": sanitized},
            ],
            max_tokens=100,
        )
        content = resp.choices[0].message.content.strip()
    except Exception:  # noqa: BLE001

        raise HTTPException(
            status_code=500,
            detail="Failed to generate insights",
        )
    result = {"insight": content}
    _append_size_warning(result)
    duration = time.perf_counter() - start
    scope = len(sanitized)
    sources = len(re.findall(r"https?://", json.dumps(result)))
    gap_count = json.dumps(result).count("[Data Gap]")
    _record_metrics("generate-insights", scope, sources, duration, gap_count)
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
    start = time.perf_counter()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or openai is None:
        raise HTTPException(status_code=503, detail="OpenAI not configured")
    client = openai.AsyncOpenAI(api_key=api_key)
    try:
        resp = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "Provide a short research summary.",
                },
                {"role": "user", "content": sanitized},
            ],
            max_tokens=150,
        )
        content = resp.choices[0].message.content.strip()
    except Exception:  # noqa: BLE001
        raise HTTPException(
            status_code=500,
            detail="Failed to generate research",
        )

    result = {"summary": content}
    _append_size_warning(result)
    duration = time.perf_counter() - start
    scope = len(sanitized)
    sources = len(re.findall(r"https?://", json.dumps(result)))
    gap_count = json.dumps(result).count("[Data Gap]")
    _record_metrics("research", scope, sources, duration, gap_count)
    try:
        _validate_with_schema(result, ResearchResponse)
    except (ValidationError, Exception):
        raise HTTPException(status_code=400, detail="Invalid response")
    return JSONResponse(result)


async def _generate_alt_text(description: str) -> str:
    """Return alt text for ``description`` limited to 15 words."""
    text = _sanitize(description)[:200]
    if not text:
        return ""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or openai is None:
        return ""
    client = openai.AsyncOpenAI(api_key=api_key)
    try:
        resp = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "user",
                    "content": f"Describe the image in under 15 words: {text}",
                }
            ],
            max_tokens=30,
        )
        alt = resp.choices[0].message.content.strip()
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
    return JSONResponse(result)


@app.post("/insight-and-personas")
async def insight_and_personas(req: InsightPersonaRequest) -> JSONResponse:
    """Return insight and persona reports using the orchestrator."""
    start = time.perf_counter()
    company = {"url": req.url}
    tech: dict[str, Any] = {"martech": req.martech or {}, "cms": req.cms or []}
    if req.cms_manual:
        tech["cms_manual"] = req.cms_manual

    insight_prompt = orchestrator.build_prompt(
        "Generate next-best-action insights.",
        company=company,
        technology=tech,
    )

    persona_prompt = orchestrator.build_prompt(
        "Generate buyer personas.",
        company=company,
        technology=tech,
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
        if isinstance(personas_raw, dict) and "generated_buyer_personas" in personas_raw:
            personas_source = personas_raw["generated_buyer_personas"]
        else:
            personas_source = personas_raw
        personas_list = _to_persona_list(personas_source)

        actions: list[Any] = []
        if isinstance(insight_raw, dict):
            for key in ("actions", "action_items", "next_best_actions"):
                if key in insight_raw:
                    val = insight_raw[key]
                    if isinstance(val, list):
                        actions = val
                    elif val is not None:
                        actions = [val]
                    break

        insight_obj = {"actions": actions, "evidence": insight_text}

        degraded = False
        if (
            isinstance(insight_raw, dict) and insight_raw.get("error") == "[Data Gap]"
        ) or (
            isinstance(personas_raw, dict) and personas_raw.get("error") == "[Data Gap]"
        ):
            degraded = True

        result = {
            "insight": insight_obj,
            "personas": personas_list,
            "degraded": degraded,
        }
        if req.cms_manual:
            result["cms_manual"] = req.cms_manual
        _append_size_warning(result)
        duration = time.perf_counter() - start
        scope = len(json.dumps(req.model_dump()))
        sources = len(re.findall(r"https?://", json.dumps(result)))
        gap_count = json.dumps(result).count("[Data Gap]")
        _record_metrics("insight-and-personas", scope, sources, duration, gap_count)
        return JSONResponse(result)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, detail=str(exc))

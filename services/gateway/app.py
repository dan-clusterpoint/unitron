import os
import asyncio
import time
import logging
import json
from urllib.parse import urlparse
from typing import Any

from services.shared.utils import normalize_url
from prometheus_client import Histogram, generate_latest, CONTENT_TYPE_LATEST
from utils.logging import redact

import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from services.shared import SecurityHeadersMiddleware
from pydantic import BaseModel, model_validator
from starlette.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient()
    try:
        yield
    finally:
        await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)

# Allow calls from the UI hosted on a different origin during development.
# UI_ORIGIN should contain the frontend domain (e.g. http://localhost:5173)
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

# Default service URLs used in local docker-compose
MARTECH_URL = os.getenv("MARTECH_URL", "http://martech:8000")
PROPERTY_URL = os.getenv("PROPERTY_URL", "http://property:8000")
INSIGHT_URL = os.getenv("INSIGHT_URL", "http://insight:8000")
INSIGHT_TIMEOUT = int(os.getenv("INSIGHT_TIMEOUT", "30"))

# Prometheus histogram for insight requests
insight_call_duration = Histogram(
    "insight_call_duration",
    "Duration of calls to the insight service",
)

# In-memory metrics for service calls
metrics: dict[str, dict[str, Any]] = {
    "martech": {"success": 0, "failure": 0, "duration": 0.0, "codes": {}},
    "property": {"success": 0, "failure": 0, "duration": 0.0, "codes": {}},
    "insight": {"success": 0, "failure": 0, "duration": 0.0, "codes": {}},
}


def record_success(service: str, duration: float, status_code: int) -> None:
    data = metrics.setdefault(
        service,
        {"success": 0, "failure": 0, "duration": 0.0, "codes": {}},
    )
    data["success"] += 1
    data["duration"] += duration
    codes = data.setdefault("codes", {})
    codes[str(status_code)] = codes.get(str(status_code), 0) + 1


def record_failure(service: str, status_code: int | None = None) -> None:
    data = metrics.setdefault(
        service,
        {"success": 0, "failure": 0, "duration": 0.0, "codes": {}},
    )
    data["failure"] += 1
    if status_code is not None:
        codes = data.setdefault("codes", {})
        codes[str(status_code)] = codes.get(str(status_code), 0) + 1


class AnalyzeRequest(BaseModel):
    url: str
    debug: bool | None = False
    headless: bool | None = False
    force: bool | None = False

    @model_validator(mode="before")
    def _allow_domain(cls, values: dict) -> dict:  # noqa: D401
        """Allow legacy ``domain`` field as alias for ``url``."""
        if "url" not in values and "domain" in values:
            values["url"] = values.pop("domain")
        return values


class MartechItem(BaseModel):
    category: str
    vendor: str


class GenerateRequest(BaseModel):
    url: str
    martech: dict[str, list[str]] | None = None
    cms: list[str] | None = None
    cms_manual: str | None = None
    martech_manual: list[MartechItem | str] | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "url": "https://example.com",
                "martech": {"core": ["Google Analytics"]},
                "martech_manual": [{"category": "analytics", "vendor": "Segment"}],
                "cms": ["WordPress"],
            }
        }
    }


def merge_martech(
    detected: dict[str, list[str]] | None,
    manual: list[MartechItem | str] | None,
) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    if manual:
        for item in manual:
            if isinstance(item, MartechItem):
                vendor = item.vendor
            elif isinstance(item, dict):
                vendor = str(item.get("vendor", ""))
            else:
                vendor = str(item)
            if vendor and vendor not in seen:
                result.append(vendor)
                seen.add(vendor)
    if detected:
        for items in detected.values():
            for item in items:
                if item not in seen:
                    result.append(item)
                    seen.add(item)
    return result


def build_snapshot(
    property_data: dict[str, Any] | None,
    martech_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Assemble a minimal snapshot from analysis artifacts."""
    martech_count = 0
    martech_list: list[str] = []
    if martech_data:
        for items in martech_data.values():
            if isinstance(items, list):
                martech_count += len(items)
                martech_list.extend(str(i) for i in items)
            elif isinstance(items, dict):
                martech_count += len(items)
                martech_list.extend(str(k) for k in items)

    domain = ""
    confidence = 0.0
    notes: list[str] = []
    industry = ""
    location = ""
    logo_url = ""
    if property_data:
        domain_list = property_data.get("domains") or []
        if domain_list:
            domain = domain_list[0]
        confidence = float(property_data.get("confidence", 0.0) or 0.0)
        notes = property_data.get("notes", []) or []
        industry = property_data.get("industry", "") or property_data.get("category", "")
        location = property_data.get("location", "") or property_data.get("country", "")
        logo_url = (
            property_data.get("logoUrl")
            or property_data.get("logo_url")
            or property_data.get("logo")
            or ""
        )

    profile: dict[str, str] = {}
    if domain:
        profile["name"] = domain
        profile["website"] = f"https://{domain}"
    if industry:
        profile["industry"] = industry
    if location:
        profile["location"] = location
    if logo_url:
        profile["logoUrl"] = logo_url

    digital_score = int(confidence * 100) + martech_count

    # Derive risk coordinates from domain confidence and martech coverage.
    if confidence >= 0.8:
        x = 0
        dns_risk = "low"
    elif confidence >= 0.5:
        x = 1
        dns_risk = "medium"
    else:
        x = 2
        dns_risk = "high"

    if martech_count == 0:
        y = 2
    elif martech_count < 3:
        y = 1
    else:
        y = 0

    risk = {"x": x, "y": y}
    risk_matrix = risk  # backwards compat

    stack_delta = [{"label": vendor, "status": "added"} for vendor in martech_list]

    next_actions: list[dict[str, str]] = []
    if dns_risk != "low" and domain:
        next_actions.append(
            {"label": f"Investigate DNS records for {domain}", "targetId": "property"}
        )
    if martech_list:
        next_actions.append(
            {
                "label": f"Review {martech_list[0]} usage",
                "targetId": "martech",
            }
        )
    else:
        next_actions.append(
            {
                "label": "Consider adding analytics tooling",
                "targetId": "martech",
            }
        )

    return {
        "profile": profile,
        "digitalScore": digital_score,
        "risk": risk,
        "riskMatrix": risk_matrix,
        "stackDelta": stack_delta,
        "growthTriggers": notes,
        "nextActions": next_actions,
    }


async def _get_with_retry(url: str, service: str) -> bool:
    """GET ``url`` with one retry, recording metrics."""
    last_code: int | None = None
    for _ in range(2):
        start = time.perf_counter()
        try:
            resp = await app.state.client.get(url, timeout=2)
            resp.raise_for_status()
            duration = time.perf_counter() - start
            record_success(service, duration, resp.status_code)
            return True
        except httpx.HTTPStatusError as exc:
            last_code = exc.response.status_code
        except Exception:  # noqa: BLE001
            pass
    record_failure(service, last_code)
    return False


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})


@app.get("/metrics")
async def metrics_endpoint() -> PlainTextResponse:
    """Return Prometheus metrics."""
    return PlainTextResponse(
        generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )


@app.get("/ready")
async def ready() -> JSONResponse:
    """Check readiness of downstream services."""
    martech_task = _get_with_retry(f"{MARTECH_URL}/ready", "martech")
    property_task = _get_with_retry(f"{PROPERTY_URL}/ready", "property")
    ok_martech, ok_property = await asyncio.gather(martech_task, property_task)
    return JSONResponse(
        {
            "ready": ok_martech and ok_property,
            "martech": "ok" if ok_martech else "degraded",
            "property": "ok" if ok_property else "degraded",
        }
    )


async def _post_with_retry(
    url: str,
    data: dict[str, Any],
    service: str,
    *,
    pass_status: bool = False,
) -> tuple[dict[str, Any] | None, bool]:
    """POST ``data`` to ``url`` with one retry on failure.

    Returns a tuple of ``(response_json, degraded)``. ``degraded`` is ``True``
    when the service reports a 503 status code, indicating it is not ready.
    """
    last_exc: Exception | None = None
    last_code: int | None = None
    last_detail: str | None = None
    for attempt in range(2):
        start = time.perf_counter()
        logger.debug("POST %s body=%s", url, redact(json.dumps(data)))
        try:
            timeout_seconds = INSIGHT_TIMEOUT if service == "insight" else 5
            resp = await app.state.client.post(url, json=data, timeout=timeout_seconds)
            duration = time.perf_counter() - start
            if service == "insight":
                insight_call_duration.observe(duration)
            if resp.status_code != 200:
                last_code = resp.status_code
                last_detail = resp.text
                if resp.status_code == 503:
                    break
                status = resp.status_code if pass_status else 502
                raise HTTPException(status_code=status, detail=resp.text)
            record_success(service, duration, resp.status_code)
            logger.debug("RESPONSE %s body=%s", url, redact(resp.text))
            return resp.json(), False
        except httpx.HTTPStatusError as exc:  # noqa: BLE001
            duration = time.perf_counter() - start
            if service == "insight":
                insight_call_duration.observe(duration)
            last_exc = exc
            last_code = exc.response.status_code
            last_detail = exc.response.text
            logger.debug("RESPONSE %s body=%s", url, redact(last_detail))
            if exc.response.status_code == 503:
                break
        except Exception as exc:  # noqa: BLE001
            duration = time.perf_counter() - start
            if service == "insight":
                insight_call_duration.observe(duration)
            last_exc = exc
    record_failure(service, last_code)
    if last_code == 503:
        return None, True
    status = last_code if pass_status and last_code else 502
    detail = f"{service} service unavailable"
    if isinstance(last_exc, HTTPException):
        status = last_exc.status_code
        detail = str(last_exc.detail) or last_detail or detail
    elif last_detail:
        detail = last_detail
    if last_detail:
        logger.debug("RESPONSE %s body=%s", url, redact(last_detail))
    raise HTTPException(status_code=status, detail=detail)


@app.post("/analyze")
async def analyze(req: AnalyzeRequest) -> JSONResponse:
    clean_url = normalize_url(req.url)
    domain = urlparse(clean_url).hostname
    if not domain:
        raise HTTPException(status_code=400, detail="Invalid URL")

    martech_task = _post_with_retry(
        f"{MARTECH_URL}/analyze",
        {
            "url": clean_url,
            "debug": req.debug,
            "headless": req.headless,
            "force": req.force,
        },
        "martech",
    )
    property_task = _post_with_retry(
        f"{PROPERTY_URL}/analyze",
        {"domain": domain},
        "property",
    )

    martech_res, property_res = await asyncio.gather(
        martech_task,
        property_task,
    )
    martech_data, martech_degraded = martech_res
    property_data, property_degraded = property_res

    cms_list = martech_data.pop("cms", []) if martech_data else []
    snapshot = build_snapshot(property_data, martech_data)
    result = {
        "property": property_data,
        "martech": martech_data or {},
        "cms": cms_list,
        "degraded": martech_degraded or property_degraded,
        "snapshot": snapshot,
    }
    return JSONResponse(result)


@app.post("/generate")
async def generate(req: GenerateRequest) -> JSONResponse:
    clean_url = normalize_url(req.url)
    merged = merge_martech(req.martech or {}, req.martech_manual or [])
    payload = {
        "url": clean_url,
        "martech": merged,
        "cms": req.cms or [],
    }
    if req.cms_manual:
        payload["cms_manual"] = req.cms_manual
    martech_data, degraded = await _post_with_retry(
        f"{MARTECH_URL}/generate", payload, "martech"
    )
    return JSONResponse({"result": martech_data or {}, "degraded": degraded})


@app.post("/insight")
async def insight(data: dict[str, Any]) -> JSONResponse:
    """Proxy insight generation to the insight service."""
    try:
        insight_data, degraded = await _post_with_retry(
            f"{INSIGHT_URL}/insight", data, "insight", pass_status=True
        )
    except HTTPException as exc:
        try:
            detail_json = json.loads(str(exc.detail))
        except Exception:  # noqa: BLE001
            detail_json = {"detail": str(exc.detail)}
        return JSONResponse(detail_json, status_code=exc.status_code)

    if insight_data is None:
        return JSONResponse({"markdown": "", "degraded": True}, status_code=503)
    return JSONResponse(insight_data)


@app.post("/research")
async def research(data: dict[str, Any]) -> JSONResponse:
    """Proxy research requests to the insight service."""
    research_data, degraded = await _post_with_retry(
        f"{INSIGHT_URL}/research", data, "insight"
    )
    if research_data is None:
        return JSONResponse({"markdown": "", "degraded": True}, status_code=503)
    return JSONResponse(research_data)

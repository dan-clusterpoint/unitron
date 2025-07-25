import os
import asyncio
import time
from urllib.parse import urlparse
from typing import Any, Dict

from services.shared.utils import normalize_url

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, root_validator
from starlette.responses import JSONResponse

app = FastAPI()

# Allow calls from the UI hosted on a different origin during development
# UI_ORIGIN should contain the frontend domain
# (e.g. http://localhost:5173)
origins = [os.getenv("UI_ORIGIN", "*")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Default service URLs used in local docker-compose
MARTECH_URL = os.getenv("MARTECH_URL", "http://martech:8000")
PROPERTY_URL = os.getenv("PROPERTY_URL", "http://property:8000")

# In-memory metrics for service calls
metrics: Dict[str, Dict[str, Any]] = {
    "martech": {"success": 0, "failure": 0, "duration": 0.0, "codes": {}},
    "property": {"success": 0, "failure": 0, "duration": 0.0, "codes": {}},
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

    @root_validator(pre=True)
    def _allow_domain(cls, values: dict) -> dict:  # noqa: D401
        """Allow legacy ``domain`` field as alias for ``url``."""
        if "url" not in values and "domain" in values:
            values["url"] = values.pop("domain")
        return values


async def _get_with_retry(url: str, service: str) -> bool:
    """GET ``url`` with one retry, recording metrics."""
    last_code: int | None = None
    for _ in range(2):
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                resp = await client.get(url)
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


@app.get('/health')
async def health():
    return JSONResponse({'status': 'ok'})


@app.get('/metrics')
async def metrics_endpoint() -> JSONResponse:
    return JSONResponse(metrics)


@app.get('/ready')
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
    url: str, data: dict, service: str
) -> tuple[dict | None, bool]:
    """POST ``data`` to ``url`` with one retry on failure.

    Returns a tuple of ``(response_json, degraded)``. ``degraded`` is ``True``
    when the service reports a 503 status code, indicating it is not ready.
    """
    last_exc: Exception | None = None
    last_code: int | None = None
    for attempt in range(2):
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.post(url, json=data)
            resp.raise_for_status()
            duration = time.perf_counter() - start
            record_success(service, duration, resp.status_code)
            return resp.json(), False
        except httpx.HTTPStatusError as exc:  # noqa: BLE001
            last_exc = exc
            last_code = exc.response.status_code
            if exc.response.status_code == 503:
                break
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    record_failure(service, last_code)
    if isinstance(last_exc, httpx.HTTPStatusError) and last_code == 503:
        return None, True
    status = 502
    if isinstance(last_exc, HTTPException):
        status = last_exc.status_code
    raise HTTPException(
        status_code=status,
        detail=f"{service} service unavailable",
    )


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

    result = {
        "property": property_data,
        "martech": martech_data,
        "degraded": martech_degraded or property_degraded,
    }
    return JSONResponse(result)

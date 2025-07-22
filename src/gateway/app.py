import os
import asyncio
import time
from urllib.parse import urlparse

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse

app = FastAPI()

# Default service URLs used in local docker-compose
MARTECH_URL = os.getenv("MARTECH_URL", "http://martech:8000")
PROPERTY_URL = os.getenv("PROPERTY_URL", "http://property:8000")

# In-memory metrics for service calls
metrics = {
    "martech": {"success": 0, "failure": 0, "duration": 0.0},
    "property": {"success": 0, "failure": 0, "duration": 0.0},
}


def record_success(service: str, duration: float) -> None:
    data = metrics.setdefault(service, {"success": 0, "failure": 0, "duration": 0.0})
    data["success"] += 1
    data["duration"] += duration


def record_failure(service: str) -> None:
    data = metrics.setdefault(service, {"success": 0, "failure": 0, "duration": 0.0})
    data["failure"] += 1


class AnalyzeRequest(BaseModel):
    url: str
    debug: bool | None = False


async def _get_with_retry(url: str, service: str) -> bool:
    """GET ``url`` with one retry, recording metrics."""
    last_exc: Exception | None = None
    for _ in range(2):
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                resp = await client.get(url)
            resp.raise_for_status()
            record_success(service, time.perf_counter() - start)
            return True
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    record_failure(service)
    return False


@app.get('/health')
async def health():
    return JSONResponse({'status': 'ok'})


@app.get('/metrics')
async def metrics_endpoint() -> JSONResponse:
    return JSONResponse(metrics)


@app.get('/ready')
async def ready() -> JSONResponse:
    martech_task = _get_with_retry(f"{MARTECH_URL}/health", "martech")
    property_task = _get_with_retry(f"{PROPERTY_URL}/health", "property")
    ok_martech, ok_property = await asyncio.gather(martech_task, property_task)
    return JSONResponse({'ready': ok_martech and ok_property})


async def _post_with_retry(url: str, data: dict, service: str) -> dict:
    """POST ``data`` to ``url`` with one retry on failure."""
    last_exc: Exception | None = None
    for attempt in range(2):
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.post(url, json=data)
            resp.raise_for_status()
            record_success(service, time.perf_counter() - start)
            return resp.json()
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    record_failure(service)
    if isinstance(last_exc, HTTPException):
        raise last_exc
    raise HTTPException(status_code=502, detail=f"{service} service unavailable")


@app.post("/analyze")
async def analyze(req: AnalyzeRequest) -> JSONResponse:
    domain = urlparse(req.url).hostname
    if not domain:
        raise HTTPException(status_code=400, detail="Invalid URL")

    martech_task = _post_with_retry(
        f"{MARTECH_URL}/analyze",
        {"url": req.url, "debug": req.debug},
        "martech",
    )
    property_task = _post_with_retry(
        f"{PROPERTY_URL}/analyze",
        {"domain": domain},
        "property",
    )

    martech_data, property_data = await asyncio.gather(martech_task, property_task)
    result = {**martech_data, **property_data}
    return JSONResponse(result)

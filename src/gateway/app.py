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


async def _get_with_retry(url: str, service: str) -> bool:
    """GET ``url`` with one retry, recording metrics."""
    last_code: int | None = None
    for _ in range(2):
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=2) as client:
                resp = await client.get(url)
            resp.raise_for_status()
            record_success(service, time.perf_counter() - start, resp.status_code)
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
    return JSONResponse({'ready': ok_martech and ok_property})


async def _post_with_retry(url: str, data: dict, service: str) -> dict:
    """POST ``data`` to ``url`` with one retry on failure."""
    last_exc: Exception | None = None
    last_code: int | None = None
    for attempt in range(2):
        start = time.perf_counter()
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.post(url, json=data)
            resp.raise_for_status()
            record_success(service, time.perf_counter() - start, resp.status_code)
            return resp.json()
        except httpx.HTTPStatusError as exc:  # noqa: BLE001
            last_exc = exc
            last_code = exc.response.status_code
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
    record_failure(service, last_code)
    status = 502
    if isinstance(last_exc, HTTPException):
        status = last_exc.status_code
    raise HTTPException(
        status_code=status,
        detail=f"{service} service unavailable",
    )


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

    martech_data, property_data = await asyncio.gather(
        martech_task, property_task
    )
    result = {
        "property": property_data,
        "martech": martech_data,
    }
    return JSONResponse(result)

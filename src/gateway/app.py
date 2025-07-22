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
    "martech": {"failures": 0, "duration": 0.0},
    "property": {"failures": 0, "duration": 0.0},
}


class AnalyzeRequest(BaseModel):
    url: str
    debug: bool | None = False


async def check_health(url: str) -> bool:
    """Return ``True`` if ``GET url`` succeeds quickly."""
    try:
        async with httpx.AsyncClient(timeout=2) as client:
            r = await client.get(url)
            return r.status_code == 200
    except Exception:
        return False


@app.get('/health')
async def health():
    return JSONResponse({'status': 'ok'})


@app.get('/ready')
async def ready() -> JSONResponse:
    martech_task = check_health(f"{MARTECH_URL}/health")
    property_task = check_health(f"{PROPERTY_URL}/health")
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
            metrics[service]["duration"] = time.perf_counter() - start
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:  # noqa: BLE001
            metrics[service]["duration"] = time.perf_counter() - start
            last_exc = exc
    metrics[service]["failures"] += 1
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

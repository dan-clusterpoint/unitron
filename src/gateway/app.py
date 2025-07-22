import os
import asyncio

import httpx
from fastapi import FastAPI
from starlette.responses import JSONResponse

app = FastAPI()

# Default service URLs used in local docker-compose
MARTECH_URL = os.getenv("MARTECH_URL", "http://martech:8000")
PROPERTY_URL = os.getenv("PROPERTY_URL", "http://property:8000")


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

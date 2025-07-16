import os
import logging
from fastapi import FastAPI, HTTPException
import httpx

from models import (
    PropertyIn, MartechIn,
    PropertyOut, MartechOut,
    GatewayAnalyzeIn, GatewayAnalyzeOut,
)

log = logging.getLogger("gateway")

app = FastAPI(title="Unitron Gateway", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok"}


def _martech_base() -> str:
    # Accept MARTECH_URL from env; must be full base URL (no trailing /)
    url = os.getenv("MARTECH_URL", "http://martech.railway.internal")
    return url.rstrip("/")

async def _call_martech(m: MartechIn) -> MartechOut:
    base = _martech_base()
    url = f"{base}/analyze"
    payload = {"url": str(m.url)}
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(url, json=payload)
        r.raise_for_status()
        data = r.json()
        return MartechOut(**data)
    except Exception as exc:  # broad: downstream may not exist yet
        log.exception("Martech call failed: %s", exc)
        # graceful degrade
        return MartechOut()

@app.post("/analyze", response_model=GatewayAnalyzeOut)
async def analyze_endpoint(req: GatewayAnalyzeIn) -> GatewayAnalyzeOut:
    # downstream martech
    martech_res = await _call_martech(req.martech)
    # stub property; when property service is wired, replace with real call
    prop_res = PropertyOut(
        domain=req.property.domain,
        confidence=0.5,
        notes=["stub: property service not yet wired"],
    )
    return GatewayAnalyzeOut(property=prop_res, martech=martech_res)

import os
import logging
import json

import httpx
from fastapi import FastAPI, HTTPException
from .models import (
    GatewayAnalyzeIn,
    GatewayAnalyzeOut,
    GatewayPropertyOut,
    GatewayMartechOut,
    MartechIn,
)
from .property_analyzer import analyze_domain

log = logging.getLogger("uvicorn.error")


def jlog(event: str, **kw: object) -> None:
    log.info("%s %s", event, json.dumps(kw))


app = FastAPI(title="Unitron Gateway", version="0.1.0")


@app.get("/")
async def root():
    return {"service": "gateway", "docs": "/docs"}


@app.get("/health")
async def health():
    jlog("health")
    return {"status": "ok"}


async def _martech_call(m: MartechIn) -> GatewayMartechOut:
    base = os.getenv("MARTECH_URL", "http://localhost:8000").rstrip("/")
    url = f"{base}/analyze"
    payload = {"url": str(m.url)}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return GatewayMartechOut(**data)
    except Exception as exc:
        jlog("martech_error", error=str(exc))
        return GatewayMartechOut()


@app.post("/analyze", response_model=GatewayAnalyzeOut)
async def analyze(req: GatewayAnalyzeIn) -> GatewayAnalyzeOut:
    jlog("analyze", property=bool(req.property), martech=bool(req.martech))
    martech_out = await _martech_call(req.martech) if req.martech else None
    property_out = None
    if req.property:
        conf, notes = await analyze_domain(req.property.domain)
        property_out = GatewayPropertyOut(
            domain=req.property.domain,
            confidence=conf,
            notes=notes,
        )
    return GatewayAnalyzeOut(property=property_out, martech=martech_out)

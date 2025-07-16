import os
import logging
import json
from typing import List, Optional

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl, Field, model_validator

log = logging.getLogger("uvicorn.error")


def jlog(event: str, **kw: object) -> None:
    log.info("%s %s", event, json.dumps(kw))


app = FastAPI(title="Unitron Gateway")


class PropertyIn(BaseModel):
    domain: str


class MartechIn(BaseModel):
    url: HttpUrl


class MartechOut(BaseModel):
    core: List[str] = []
    adjacent: List[str] = []
    broader: List[str] = []
    competitors: List[str] = []


class PropertyOut(BaseModel):
    domain: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    notes: List[str] = []


class GatewayAnalyzeIn(BaseModel):
    property: Optional[PropertyIn] = None
    martech: Optional[MartechIn] = None

    @model_validator(mode="after")
    def check_one(cls, values):
        if not (values.property or values.martech):
            raise ValueError("property or martech required")
        return values


class GatewayAnalyzeOut(BaseModel):
    property: Optional[PropertyOut] = None
    martech: Optional[MartechOut] = None


@app.get("/")
async def root():
    return {"service": "gateway", "docs": "/docs"}


@app.get("/health")
async def health():
    jlog("health")
    return {"status": "ok"}


async def _martech_call(m: MartechIn) -> MartechOut:
    base = os.getenv("MARTECH_URL", "http://martech:8000").rstrip("/")
    url = f"{base}/analyze"
    payload = {"url": str(m.url)}
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return MartechOut(**data)
    except Exception as exc:
        jlog("martech_error", error=str(exc))
        return MartechOut()


async def _property_stub(p: PropertyIn) -> PropertyOut:
    return PropertyOut(domain=p.domain, confidence=0.1, notes=["stubbed property analysis"])


@app.post("/analyze", response_model=GatewayAnalyzeOut)
async def analyze(req: GatewayAnalyzeIn) -> GatewayAnalyzeOut:
    jlog("analyze", property=bool(req.property), martech=bool(req.martech))
    prop = await _property_stub(req.property) if req.property else None
    mt = await _martech_call(req.martech) if req.martech else None
    return GatewayAnalyzeOut(property=prop, martech=mt)

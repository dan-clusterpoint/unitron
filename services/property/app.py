import logging
import json
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

log = logging.getLogger("uvicorn.error")


def jlog(event: str, **kw: object) -> None:
    log.info("%s %s", event, json.dumps(kw))


app = FastAPI(title="Property Service")


class PropertyRequest(BaseModel):
    domain: str


class PropertyResponse(BaseModel):
    domain: str
    confidence: float = 0.0
    notes: List[str] = []


@app.get("/")
async def root():
    return {"service": "property", "docs": "/docs"}


@app.get("/health")
async def health():
    jlog("health")
    return {"status": "ok"}


@app.post("/analyze", response_model=PropertyResponse)
async def analyze(req: PropertyRequest) -> PropertyResponse:
    jlog("analyze", domain=req.domain)
    return PropertyResponse(domain=req.domain, confidence=0.0, notes=["stub"])

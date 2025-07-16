import logging
import json
from typing import List
import asyncio

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



@app.on_event("startup")
async def _startup() -> None:
    await asyncio.sleep(1)

    @app.get("/health", include_in_schema=False)
    async def health() -> dict[str, str]:
        jlog("health")
        return {"status": "ok"}


@app.post("/analyze", response_model=PropertyResponse)
async def analyze(req: PropertyRequest) -> PropertyResponse:
    jlog("analyze", domain=req.domain)
    return PropertyResponse(domain=req.domain, confidence=0.0, notes=["stub"])

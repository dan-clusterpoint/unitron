import logging
import json
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl

from .detect import detect

log = logging.getLogger("uvicorn.error")


def jlog(event: str, **kw: object) -> None:
    log.info("%s %s", event, json.dumps(kw))


app = FastAPI(title="Martech Analyzer Service")


class AnalyzeRequest(BaseModel):
    url: HttpUrl


class AnalyzeResponse(BaseModel):
    core: List[str] = []
    adjacent: List[str] = []
    broader: List[str] = []
    competitors: List[str] = []


@app.get("/")
async def root():
    return {"service": "martech", "docs": "/docs"}


@app.get("/health")
async def health():
    jlog("health")
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    jlog("analyze", url=str(req.url))
    try:
        data = detect(str(req.url))
    except Exception as e:  # pragma: no cover - network heavy
        raise HTTPException(status_code=502, detail=f"martech detection error: {e}")
    return AnalyzeResponse(
        core=data.get("core", []),
        adjacent=data.get("adjacent", []),
        broader=data.get("broader", []),
        competitors=data.get("competitors", []),
    )

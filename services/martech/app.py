import os
import logging
from fastapi import FastAPI, Body

log = logging.getLogger("uvicorn.error")

app = FastAPI(title="Martech Service", version="0.1.0")

@app.get("/health", tags=["Health"])
async def health():
    """Railway healthcheck endpoint."""
    log.info("martech /health OK")
    return {"status": "ok"}

@app.get("/", include_in_schema=False)
async def root():
    return {"service": "martech", "docs": "/docs"}

@app.post("/analyze", summary="Analyze a URL")
async def analyze(payload: dict = Body(..., example={"url": "https://example.com"})):
    """
    Stub analysis: accept JSON with {"url": "..."} and return empty buckets.
    (We'll wire in real martech detection later.)
    """
    url = payload.get("url")
    log.info("martech /analyze url=%s", url)
    return {
        "core": [],
        "adjacent": [],
        "broader": [],
        "competitors": []
    }

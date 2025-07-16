import os
import logging
from fastapi import FastAPI, Body, HTTPException
from detector import detect, DetectionError

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
    """Fetch and fingerprint martech stack for the given URL."""
    url = payload.get("url")
    log.info("martech /analyze url=%s", url)
    try:
        data = await detect(url)
        return data
    except DetectionError as de:
        raise HTTPException(status_code=502, detail=str(de))
    except Exception as e:
        log.exception("Unexpected error in /analyze: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")

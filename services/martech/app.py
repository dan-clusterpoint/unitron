import os, logging
from fastapi import FastAPI, Body, Query, HTTPException
from detector import detect, DetectionError
from models import MartechAnalyzeIn, MartechAnalyzeOut

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

@app.post("/analyze", summary="Analyze a URL", response_model=MartechAnalyzeOut)
async def analyze(payload: MartechAnalyzeIn = Body(..., example={"url": "https://example.com"}), debug: bool = Query(False)):
    """
    Fetch and fingerprint martech stack for the given URL.
    If ?debug=true, include debug info (scripts fetched, errors) in output.
    """
    url = str(payload.url)
    log.info("martech /analyze url=%s", url)
    try:
        if debug:
            data, dbg = await detect(url, return_debug=True)
            out = MartechAnalyzeOut(**data, debug=dbg)
            return out
        data = await detect(url)
        return MartechAnalyzeOut(**data)
    except DetectionError as de:
        raise HTTPException(status_code=502, detail=str(de))
    except Exception as e:
        log.exception("Unexpected error in /analyze: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")

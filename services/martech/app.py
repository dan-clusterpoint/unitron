import os, logging
from fastapi import FastAPI, Query, HTTPException

from detector import detect, DetectionError
from models import MartechAnalyzeIn, MartechAnalyzeOut
from Wappalyzer import Wappalyzer, WebPage

log = logging.getLogger("uvicorn.error")

app = FastAPI(title="Martech Service", version="0.1.0")
wappalyzer = Wappalyzer.latest()

@app.get("/", include_in_schema=False)
async def root():
    return {"service": "martech", "docs": "/docs"}

@app.post("/analyze", summary="Analyze a URL", response_model=MartechAnalyzeOut)
async def analyze(payload: MartechAnalyzeIn, debug: bool = Query(False)):
    """
    Fetch and fingerprint martech stack for the given URL.
    If ?debug=true, include debug info (scripts fetched, errors) in output.
    """
    url = str(payload.url)
    log.info("martech /analyze url=%s", url)
    try:
        if debug:
            data, dbg = await detect(url, return_debug=True)
        else:
            data = await detect(url)
            dbg = None

        techs = []
        try:
            page = WebPage.new_from_url(url)
            apps = wappalyzer.analyze(page)
            techs = [{"name": a.name, "version": (a.version or None)} for a in apps]
            if dbg is not None:
                dbg["wappalyzer_apps"] = techs
        except Exception as e:
            log.exception("Wappalyzer failed: %s", e)
            if dbg is not None:
                dbg.setdefault("errors", []).append(f"wappalyzer:{e}")

        out = MartechAnalyzeOut(**data, technologies=techs, debug=dbg)
        return out
    except DetectionError as de:
        raise HTTPException(status_code=502, detail=str(de))
    except Exception as e:
        log.exception("Unexpected error in /analyze: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok"}

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Set
import asyncio
import logging

import httpx
import yaml  # type: ignore
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse

# Default path for fingerprint definitions
FINGERPRINT_PATH = Path(__file__).resolve().parents[2] / "fingerprints.yaml"
CACHE_TTL = 15 * 60  # 15 minutes

app = FastAPI()

# Allow calls from the UI hosted on a different origin during development
origins = [os.getenv("VITE_API_BASE_URL", "*")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state populated on startup
fingerprints: Dict[str, List[Dict[str, str]]] | None = None
cache: Dict[str, Dict[str, Any]] = {}


class AnalyzeRequest(BaseModel):
    url: str
    debug: bool | None = False


class ReadyResponse(BaseModel):
    ready: bool


def _load_fingerprints(path: Path) -> Dict[str, List[Dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path) as f:
        if path.suffix in {".yaml", ".yml"}:
            return yaml.safe_load(f)
        return json.load(f)


async def _fetch(client: httpx.AsyncClient, url: str) -> str:
    r = await client.get(url)
    r.raise_for_status()
    return r.text


async def _extract_scripts(client: httpx.AsyncClient, html: str) -> Set[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls: Set[str] = set()
    for tag in soup.find_all("script"):
        src = tag.get("src")
        if src:
            urls.add(src)
            if "googletagmanager.com/gtm.js" in src:
                try:
                    gtm = await _fetch(client, src)
                    found = {
                        u
                        for u in re.findall(r"https?://[^'\"]+", gtm)
                        if u.endswith(".js")
                    }
                    urls.update(found)
                except Exception:
                    pass
    return urls


async def analyze_url(url: str, debug: bool = False) -> Dict[str, object]:
    proxy = (
        os.getenv("OUTBOUND_HTTP_PROXY")
        or os.getenv("HTTP_PROXY")
        or os.getenv("HTTPS_PROXY")
        or None
    )
    client_opts: Dict[str, Any] = {"timeout": 10}
    if proxy:
        client_opts["proxies"] = {
            "http://": proxy,
            "https://": proxy,
        }
    async with httpx.AsyncClient(**client_opts) as client:
        html = await _fetch(client, url)
        scripts = await _extract_scripts(client, html)
    result: Dict[str, List[str]] = {k: [] for k in fingerprints or {}}
    for bucket, vendors in (fingerprints or {}).items():
        for vendor in vendors:
            pat = vendor["pattern"]
            if any(pat in s for s in scripts):
                result[bucket].append(vendor["name"])
    response: Dict[str, Any] = result
    if debug:
        response["debug"] = {"scripts": list(scripts), "html_size": len(html)}
    return response


@app.on_event("startup")
async def _startup() -> None:
    global fingerprints
    try:
        fingerprints = _load_fingerprints(FINGERPRINT_PATH)
    except Exception:
        fingerprints = None


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/ready", response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    global fingerprints
    if fingerprints is None:
        try:
            fingerprints = _load_fingerprints(FINGERPRINT_PATH)
        except Exception:
            fingerprints = None
    return ReadyResponse(ready=fingerprints is not None)


@app.post("/analyze")
async def analyze(req: AnalyzeRequest) -> JSONResponse:
    if fingerprints is None:
        raise HTTPException(status_code=503, detail="Service not ready")
    url = req.url
    now = time.time()
    entry = cache.get(url)
    fresh = (
        entry
        and isinstance(entry.get("time"), float)
        and now - entry["time"] < CACHE_TTL
    )
    if fresh and entry is not None:
        result = entry["data"]
    else:
        try:
            result = await analyze_url(url, debug=bool(req.debug))
        except (httpx.RequestError, asyncio.TimeoutError):
            logging.exception("failed analyzing URL")
            return JSONResponse(
                {"detail": "martech service unavailable"}, status_code=503
            )
        cache[url] = {"time": now, "data": result}
    return JSONResponse(result)


@app.get("/diagnose")
async def diagnose() -> JSONResponse:
    """Check outbound connectivity by fetching https://example.com."""
    proxy = (
        os.getenv("OUTBOUND_HTTP_PROXY")
        or os.getenv("HTTP_PROXY")
        or os.getenv("HTTPS_PROXY")
        or None
    )
    client_opts: Dict[str, Any] = {"timeout": 5}
    if proxy:
        client_opts["proxies"] = {
            "http://": proxy,
            "https://": proxy,
        }
    try:
        async with httpx.AsyncClient(**client_opts) as client:
            await client.get("https://example.com")
    except Exception as exc:  # noqa: BLE001
        return JSONResponse({"error": str(exc)})
    return JSONResponse({"success": True})

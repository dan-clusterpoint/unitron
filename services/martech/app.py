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
from services.shared.utils import detect_vendors

# Default path for fingerprint definitions
FINGERPRINT_PATH = Path(__file__).resolve().parents[2] / "fingerprints.yaml"
CACHE_TTL = 15 * 60  # 15 minutes

app = FastAPI()

# Allow calls from the UI hosted on a different origin during development
# UI_ORIGIN should contain the frontend domain
# (e.g. http://localhost:5173)
origins = [os.getenv("UI_ORIGIN", "*")]
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


class DiagnoseResponse(BaseModel):
    success: bool
    error: str | None = None


class ReadyResponse(BaseModel):
    ready: bool


def _load_fingerprints(path: Path) -> Dict[str, List[Dict[str, str]]]:
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path) as f:
        if path.suffix in {".yaml", ".yml"}:
            return yaml.safe_load(f)
        return json.load(f)


async def _fetch(client: httpx.AsyncClient, url: str) -> tuple[str, dict[str, str]]:
    r = await client.get(url, follow_redirects=True)
    r.raise_for_status()
    cookies = {k: v for k, v in r.cookies.items()}
    return r.text, cookies


async def _extract_scripts(client: httpx.AsyncClient, html: str) -> tuple[Set[str], List[str]]:
    soup = BeautifulSoup(html, "html.parser")
    urls: Set[str] = set()
    inline: List[str] = []
    for tag in soup.find_all("script"):
        src = tag.get("src")
        if src:
            urls.add(src)
            if "googletagmanager.com/gtm.js" in src:
                try:
                    gtm_html, _ = await _fetch(client, src)
                    found_urls, found_inline = await _extract_scripts(client, gtm_html)
                    urls.update(found_urls)
                    inline.extend(found_inline)
                except Exception:
                    pass
        else:
            text = tag.string
            if text:
                inline.append(text)
    return urls, inline


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
        html, resp_cookies = await _fetch(client, url)
        script_urls, inline = await _extract_scripts(client, html)
    vendors = detect_vendors(html, resp_cookies)
    response: Dict[str, Any] = vendors
    if debug:
        response["debug"] = {
            "scripts": list(script_urls),
            "inline_count": len(inline),
            "html_size": len(html),
            "cookies": resp_cookies,
        }
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


@app.get("/fingerprints")
async def fingerprints_endpoint(url: str, debug: bool | None = False) -> JSONResponse:
    if fingerprints is None:
        raise HTTPException(status_code=503, detail="Service not ready")
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
        html, resp_cookies = await _fetch(client, url)
    vendors = detect_vendors(html, resp_cookies)
    if not debug:
        vendors = {bucket: list(info.keys()) for bucket, info in vendors.items()}
    return JSONResponse(vendors)


@app.get("/diagnose", response_model=DiagnoseResponse, tags=["Service"])
async def diagnose() -> DiagnoseResponse:
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
        return DiagnoseResponse(success=False, error=str(exc))
    return DiagnoseResponse(success=True)

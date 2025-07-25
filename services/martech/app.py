from __future__ import annotations

import json
import os
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
    headless: bool | None = False
    force: bool | None = False


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


async def _fetch(
    client: httpx.AsyncClient, url: str
) -> tuple[str, dict[str, str]]:
    r = await client.get(url, follow_redirects=True)
    r.raise_for_status()
    cookies = {k: v for k, v in r.cookies.items()}
    return r.text, cookies


async def _extract_scripts(
    client: httpx.AsyncClient | None,
    html: str,
    base_url: str | None = None,
) -> tuple[Set[str], List[str], List[str]]:
    soup = BeautifulSoup(html, "html.parser")
    urls: Set[str] = set()
    inline: List[str] = []
    external: List[str] = []
    from urllib.parse import urljoin

    for tag in soup.find_all("script"):
        src = tag.get("src")
        if src:
            urls.add(src)
            if client is not None:
                try:
                    full_src = src if (src.startswith("http")) else urljoin(base_url or "", src)
                    script_text, _ = await _fetch(client, full_src)
                    external.append(script_text)
                    if "googletagmanager.com/gtm.js" in src:
                        import re
                        matches = re.findall(r"https?://[^\"']+\.js", script_text)
                        urls.update(matches)
                except Exception:
                    external.append("")
        else:
            text = tag.string
            if text:
                inline.append(text)
    return urls, inline, external


async def _headless_request(url: str) -> str:
    """Fetch ``url`` using Playwright with JavaScript disabled."""
    try:
        from playwright.async_api import async_playwright
    except Exception:
        return ""

    try:
        async with async_playwright() as pw:
            browser = await pw.firefox.launch(headless=True)
            context = await browser.new_context(java_script_enabled=False)
            page = await context.new_page()
            await page.goto(url, wait_until="load", timeout=5000)
            content = await page.content()
            await browser.close()
            return content
    except Exception:
        return ""


def _collect_resource_hints(html: str) -> Set[str]:
    """Return URLs from resource hint/link and img tags."""
    soup = BeautifulSoup(html, "html.parser")
    urls: Set[str] = set()
    for tag in soup.find_all("link"):
        rel = tag.get("rel", [])
        if isinstance(rel, str):
            rel = [rel]
        if any(r in {"preconnect", "dns-prefetch"} for r in rel):
            href = tag.get("href")
            if href:
                urls.add(href)
    for tag in soup.find_all("img"):
        src = tag.get("src")
        if src:
            urls.add(src)
    for tag in soup.find_all("source"):
        srcset = tag.get("srcset") or tag.get("src")
        if srcset:
            for part in srcset.split(","):
                val = part.strip().split(" ")[0]
                if val:
                    urls.add(val)
    return urls


async def analyze_url(
    url: str, debug: bool = False, headless: bool = False
) -> Dict[str, object]:
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
        script_urls, inline, external = await _extract_scripts(
            client, html, base_url=url
        )

    resource_urls: Set[str] = set()
    if headless:
        headless_html = await _headless_request(url)
        if headless_html:
            resource_urls.update(_collect_resource_hints(headless_html))

    all_urls = list(script_urls | resource_urls)
    vendors = detect_vendors(
        html, resp_cookies, all_urls, fingerprints, script_bodies=external
    )
    response: Dict[str, Any] = vendors
    if debug:
        response["debug"] = {
            "scripts": all_urls,
            "inline_count": len(inline) + len(external),
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
    if fresh and entry is not None and not req.force:
        result = entry["data"]
    else:
        try:
            result = await analyze_url(
                url, debug=bool(req.debug), headless=bool(req.headless)
            )
        except (httpx.RequestError, asyncio.TimeoutError):
            logging.exception("failed analyzing URL")
            return JSONResponse(
                {"detail": "martech service unavailable"}, status_code=503
            )
        cache[url] = {"time": now, "data": result}

    final_result: Dict[str, Any]
    if req.debug:
        final_result = result
    else:
        final_result = {
            bucket: list(info.keys()) for bucket, info in result.items()
        }

    return JSONResponse(final_result)


@app.get("/fingerprints")
async def fingerprints_endpoint(debug: bool | None = False) -> JSONResponse:
    """Return fingerprint definitions or sample detection results."""
    if fingerprints is None:
        raise HTTPException(status_code=503, detail="Service not ready")

    if debug:
        sample_html = (
            "<script src='https://www.google-analytics.com/analytics.js'>"
            "</script>"
            "<script src='https://cdn.segment.com/analytics.js'></script>"
            "<script>analytics.load('XYZ');"
            "ga('create','UA-XYZ','auto');</script>"
        )
        detected = detect_vendors(sample_html, {}, [], fingerprints)
        result: Dict[str, Dict[str, list[str]]] = {}
        for bucket, vendors in detected.items():
            bucket_out: Dict[str, list[str]] = {}
            for name, info in vendors.items():
                evid = info.get("evidence", {})
                bucket_out[name] = [k for k, v in evid.items() if v]
            if bucket_out:
                result[bucket] = bucket_out
        return JSONResponse(result)

    return JSONResponse(fingerprints)


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

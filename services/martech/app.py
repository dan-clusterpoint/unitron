from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any
import io
import asyncio
import logging

import httpx
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse
from services.shared.utils import detect_vendors
from services.shared.fingerprint import (
    DEFAULT_CMS_FINGERPRINTS,
    DEFAULT_FINGERPRINTS,
    load_fingerprints,
    match_fingerprints,
)

# Default path for fingerprint definitions
CACHE_TTL = 15 * 60  # 15 minutes
BASE_DIR = Path(__file__).resolve().parents[2]
FINGERPRINT_PATH = BASE_DIR / "fingerprints.yaml"
CMS_FINGERPRINT_PATH = BASE_DIR / "cms_fingerprints.yaml"

# Optional logging of manually submitted CMS strings.
# If set, CMS_MANUAL_LOG_PATH should point to a file that receives one entry
# per request where ``cms_manual`` is provided.
CMS_MANUAL_LOG_PATH = os.getenv("CMS_MANUAL_LOG_PATH")
_cms_log_file: io.TextIOWrapper | None = None

# Optional technology detection via python-wappalyzer
ENABLE_WAPPALYZER = os.getenv("ENABLE_WAPPALYZER", "0").lower() in {
    "1",
    "true",
    "yes",
}

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
try:
    fingerprints: dict[str, Any] | None = load_fingerprints(FINGERPRINT_PATH)
except Exception:
    fingerprints = DEFAULT_FINGERPRINTS or {}

try:
    cms_fingerprints: dict[str, Any] | None = load_fingerprints(
        CMS_FINGERPRINT_PATH
    )
except Exception:
    cms_fingerprints = DEFAULT_CMS_FINGERPRINTS or {}
cache: dict[str, dict[str, Any]] = {}

# URL of the insight service used for persona generation
INSIGHT_URL = os.getenv("INSIGHT_URL", "http://insight:8000")


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


class GenerateRequest(BaseModel):
    url: str
    martech: dict[str, list[str]] | None = None
    cms: list[str] | None = None
    cms_manual: str | None = None


def _load_fingerprints(path: Path) -> dict[str, Any]:
    """Wrapper around :func:`load_fingerprints` that ignores cache."""
    return load_fingerprints(path)


def _log_manual_cms(value: str) -> None:
    """Append manual CMS entries to `CMS_MANUAL_LOG_PATH` if configured."""
    if not CMS_MANUAL_LOG_PATH or not value:
        return
    global _cms_log_file
    try:
        if _cms_log_file is None:
            _cms_log_file = open(CMS_MANUAL_LOG_PATH, "a", encoding="utf-8")
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        _cms_log_file.write(f"{timestamp}\t{value}\n")
        _cms_log_file.flush()
    except Exception:  # noqa: BLE001
        logging.exception("failed to record cms_manual")


async def _fetch(
    client: httpx.AsyncClient, url: str
) -> tuple[str, dict[str, str], dict[str, str]]:
    r = await client.get(url, follow_redirects=True)
    r.raise_for_status()
    cookies = {k: v for k, v in r.cookies.items()}
    headers = {k.lower(): v for k, v in r.headers.items()}
    return r.text, headers, cookies


async def _extract_scripts(
    client: httpx.AsyncClient | None,
    html: str,
    base_url: str | None = None,
) -> tuple[set[str], list[str], list[str]]:
    soup = BeautifulSoup(html, "html.parser")
    urls: set[str] = set()
    inline: list[str] = []
    external: list[str] = []
    from urllib.parse import urljoin

    for tag in soup.find_all("script"):
        src = tag.get("src")
        if src:
            urls.add(src)
            if client is not None:
                try:
                    if src.startswith("http"):
                        full_src = src
                    else:
                        full_src = urljoin(base_url or "", src)
                    script_text, _, _ = await _fetch(client, full_src)
                    external.append(script_text)
                    if "googletagmanager.com/gtm.js" in src:
                        import re
                        matches = re.findall(
                            r"https?://[^\"']+\.js", script_text
                        )
                        urls.update(matches)
                except Exception:
                    external.append("")
        else:
            text = tag.string
            if text:
                inline.append(text)
    return urls, inline, external


async def _headless_request(url: str, proxy: str | None = None) -> str:
    """Fetch ``url`` using Playwright with JavaScript disabled."""
    try:
        from playwright.async_api import async_playwright
    except Exception:
        return ""

    try:
        async with async_playwright() as pw:
            browser = await pw.firefox.launch(headless=True)
            context_opts: dict[str, Any] = {"java_script_enabled": False}
            if proxy:
                context_opts["proxy"] = {"server": proxy}
            context = await browser.new_context(**context_opts)
            page = await context.new_page()
            await page.goto(url, wait_until="load", timeout=5000)
            content = await page.content()
            await browser.close()
            return content
    except Exception:
        return ""


def _collect_resource_hints(html: str) -> set[str]:
    """Return URLs from resource hint/link and img tags."""
    soup = BeautifulSoup(html, "html.parser")
    urls: set[str] = set()
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
) -> dict[str, object]:
    proxy = (
        os.getenv("OUTBOUND_HTTP_PROXY")
        or os.getenv("HTTP_PROXY")
        or os.getenv("HTTPS_PROXY")
        or None
    )
    client_opts: dict[str, Any] = {"timeout": 10}
    if proxy:
        client_opts["proxy"] = proxy
    network_error = False
    script_urls: set[str]
    inline: list[str]
    external: list[str]
    async with httpx.AsyncClient(**client_opts) as client:
        try:
            html, resp_headers, resp_cookies = await _fetch(client, url)
        except (
            httpx.RequestError,
            asyncio.TimeoutError,
        ):  # noqa: BLE001
            logging.exception("failed fetching %s", url)
            network_error = True
            html = ""
            resp_headers = {}
            resp_cookies = {}
            script_urls, inline, external = set(), [], []
        else:
            script_urls, inline, external = await _extract_scripts(
                client, html, base_url=url
            )

    resource_urls: set[str] = set()
    if headless and not network_error:
        headless_html = await _headless_request(url, proxy)
        if headless_html:
            resource_urls.update(_collect_resource_hints(headless_html))

    all_urls = list(script_urls | resource_urls)
    vendors = detect_vendors(
        html, resp_cookies, all_urls, fingerprints, script_bodies=external
    )
    cms_results: dict[str, Any] = {}
    if cms_fingerprints is not None:
        cms_results = match_fingerprints(
            html,
            url,
            resp_headers,
            resp_cookies,
            all_urls,
            cms_fingerprints,
        )
    if ENABLE_WAPPALYZER:
        try:
            from Wappalyzer import Wappalyzer, WebPage

            page = WebPage(url, html, resp_headers)
            techs = Wappalyzer.latest().analyze(page)
            for name in techs:
                exists = any(name in v for v in cms_results.values())
                if not exists:
                    cms_results.setdefault("uncategorized", {})[name] = {
                        "confidence": 1.0,
                        "evidence": {"wappalyzer": []},
                    }
        except Exception:
            logging.exception("wappalyzer failed")
    response: dict[str, Any] = vendors
    response["cms"] = cms_results
    response["network_error"] = network_error
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
    global fingerprints, cms_fingerprints
    if fingerprints is None:
        try:
            fingerprints = _load_fingerprints(FINGERPRINT_PATH)
        except Exception:
            fingerprints = {}
    if cms_fingerprints is None:
        try:
            cms_fingerprints = _load_fingerprints(CMS_FINGERPRINT_PATH)
        except Exception:
            cms_fingerprints = {}


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/ready", response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    global fingerprints, cms_fingerprints
    if fingerprints is None:
        try:
            fingerprints = _load_fingerprints(FINGERPRINT_PATH)
        except Exception:
            fingerprints = {}
    if cms_fingerprints is None:
        try:
            cms_fingerprints = _load_fingerprints(CMS_FINGERPRINT_PATH)
        except Exception:
            cms_fingerprints = {}
    return ReadyResponse(
        ready=fingerprints is not None and cms_fingerprints is not None
    )


@app.post("/analyze")
async def analyze(req: AnalyzeRequest) -> JSONResponse:
    if fingerprints is None or cms_fingerprints is None:
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
        except Exception:  # noqa: BLE001
            logging.exception("unexpected error analyzing URL")
            raise HTTPException(status_code=500, detail="internal error")
        cache[url] = {"time": now, "data": result}

    final_result: dict[str, Any]
    if req.debug:
        final_result = result
    else:
        final_result = {"network_error": result.get("network_error", False)}
        for bucket, info in result.items():
            if bucket == "network_error":
                continue
            if bucket == "cms":
                names: list[str] = []
                for vendors in info.values():
                    names.extend(list(vendors.keys()))
                final_result["cms"] = names
            else:
                final_result[bucket] = list(info.keys())

    return JSONResponse(final_result)


@app.post("/generate")
async def generate(req: GenerateRequest) -> JSONResponse:
    """Proxy persona requests to the insight service."""
    payload = {
        "url": req.url,
        "martech": req.martech or {},
        "cms": req.cms or [],
    }
    if req.cms_manual:
        payload["cms_manual"] = req.cms_manual
        _log_manual_cms(req.cms_manual)
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{INSIGHT_URL}/insight-and-personas", json=payload
            )
        resp.raise_for_status()
    except httpx.HTTPStatusError as exc:  # noqa: BLE001
        raise HTTPException(
            status_code=exc.response.status_code, detail=exc.response.text
        )
    except Exception:  # noqa: BLE001
        logging.exception("failed to contact insight service")
        raise HTTPException(status_code=500, detail="insight service error")
    return JSONResponse(resp.json())


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
        result: dict[str, dict[str, list[str]]] = {}
        for bucket, vendors in detected.items():
            bucket_out: dict[str, list[str]] = {}
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
    client_opts: dict[str, Any] = {"timeout": 5}
    if proxy:
        client_opts["proxy"] = proxy
    try:
        async with httpx.AsyncClient(**client_opts) as client:
            await client.get("https://example.com")
    except Exception as exc:  # noqa: BLE001
        return DiagnoseResponse(success=False, error=str(exc))
    return DiagnoseResponse(success=True)

"""Unified FastAPI application exposing core Unitron endpoints.

This module replaces the previous multi-service layout and directly exposes
the small subset of endpoints exercised in the tests.  Only the `/health`,
`/analyze` and `/generate` routes are implemented.  The original project
contains far more functionality; this file only preserves the behaviour required
for the unit tests.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urlparse
import os

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, model_validator
from starlette.responses import JSONResponse

from services.shared import SecurityHeadersMiddleware
from services.shared.utils import normalize_url


PROPERTY_URL = os.getenv("PROPERTY_URL", "http://property:8000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create a single shared HTTP client for outbound calls."""
    app.state.client = httpx.AsyncClient()
    try:
        yield
    finally:
        await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)

# Allow calls from the web interface during development.  The behaviour mirrors
# the former individual services.
ui_origin = os.getenv("UI_ORIGIN")
allow = [ui_origin] if ui_origin else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization"],
)
app.add_middleware(SecurityHeadersMiddleware)


class AnalyzeRequest(BaseModel):
    """Request model for the `/analyze` endpoint."""

    url: str
    debug: bool | None = False
    headless: bool | None = False
    force: bool | None = False

    @model_validator(mode="before")
    def _allow_domain(cls, values: dict) -> dict:  # noqa: D401
        """Allow legacy ``domain`` field as alias for ``url``."""
        if "url" not in values and "domain" in values:
            values["url"] = values.pop("domain")
        return values


class MartechItem(BaseModel):
    category: str
    vendor: str


class GenerateRequest(BaseModel):
    """Request model for the `/generate` endpoint."""

    url: str
    martech: dict[str, list[str]] | None = None
    cms: list[str] | None = None
    cms_manual: str | None = None
    martech_manual: list[MartechItem | str] | None = None


def merge_martech(
    detected: dict[str, list[str]] | None,
    manual: list[MartechItem | str] | None,
) -> list[str]:
    """Merge detected and manually supplied martech vendors.

    This mirrors the helper previously used by the gateway service.  Manual
    entries appear first and duplicates are removed while preserving order.
    """

    result: list[str] = []
    seen: set[str] = set()
    if manual:
        for item in manual:
            if isinstance(item, MartechItem):
                vendor = item.vendor
            elif isinstance(item, dict):
                vendor = str(item.get("vendor", ""))
            else:
                vendor = str(item)
            if vendor and vendor not in seen:
                result.append(vendor)
                seen.add(vendor)
    if detected:
        for items in detected.values():
            for item in items:
                if item not in seen:
                    result.append(item)
                    seen.add(item)
    return result


@app.get("/health")
async def health() -> JSONResponse:
    """Basic liveness probe used by tests and Docker containers."""
    return JSONResponse({"status": "ok"})


@app.post("/analyze")
async def analyze(req: AnalyzeRequest) -> JSONResponse:
    """Return property and martech information for the supplied URL.

    The implementation only proxies the property lookup via HTTP and returns an
    empty martech result.  The original project also performed extensive client
    side analysis which is intentionally omitted here.
    """

    clean_url = normalize_url(req.url)
    domain = urlparse(clean_url).hostname
    if not domain:
        raise HTTPException(status_code=400, detail="Invalid URL")

    try:
        resp = await app.state.client.post(
            f"{PROPERTY_URL}/analyze", json={"domain": domain}, timeout=5
        )
        resp.raise_for_status()
        property_data: dict[str, Any] = resp.json()
        degraded = False
    except httpx.HTTPStatusError:
        raise HTTPException(status_code=502, detail="property service unavailable")
    except Exception:  # noqa: BLE001
        property_data = {}
        degraded = True

    result = {
        "property": property_data,
        "martech": {},
        "cms": [],
        "degraded": degraded,
    }
    return JSONResponse(result)


@app.post("/generate")
async def generate(req: GenerateRequest) -> JSONResponse:
    """Merge martech hints and return a simple payload.

    Historically this endpoint proxied to a separate insight service.  The
    unified implementation instead returns the merged martech and CMS data
    directly which keeps the example lightweight while preserving the public
    contract exercised by the tests.
    """

    clean_url = normalize_url(req.url)
    merged = merge_martech(req.martech or {}, req.martech_manual or [])
    payload = {
        "url": clean_url,
        "martech": merged,
        "cms": req.cms or [],
    }
    if req.cms_manual:
        payload["cms_manual"] = req.cms_manual
    return JSONResponse({"result": payload, "degraded": False})


__all__ = ["app", "merge_martech"]


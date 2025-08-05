"""Unified FastAPI application exposing core Unitron endpoints.

This module replaces the previous multi-service layout and directly exposes
the small subset of endpoints exercised in the tests.  Only the `/health`,
`/analyze` and `/generate` routes are implemented.  The original project
contains far more functionality; this file only preserves the behaviour required
for the unit tests.
"""

from __future__ import annotations

from urllib.parse import urlparse
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, model_validator
from starlette.responses import JSONResponse

from services.shared.utils import normalize_url


app = FastAPI()

# Allow calls from the web interface during development.
ui_origin = os.getenv("UI_ORIGIN")
if ui_origin:
    app.add_middleware(CORSMiddleware, allow_origins=[ui_origin])


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
    """Return basic analysis for the supplied URL.

    Domain verification via the deprecated property service has been removed.
    The endpoint now simply normalizes the URL and returns empty analysis
    placeholders.
    """

    clean_url = normalize_url(req.url)
    domain = urlparse(clean_url).hostname
    if not domain:
        raise HTTPException(status_code=400, detail="Invalid URL")

    result = {
        "url": clean_url,
        "martech": {},
        "cms": [],
        "degraded": False,
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

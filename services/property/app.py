from __future__ import annotations

from urllib.parse import urlparse
import socket
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
import httpx
from fastapi.middleware.cors import CORSMiddleware
from services.shared import SecurityHeadersMiddleware
from pydantic import BaseModel
from services.shared.utils import normalize_url
from starlette.responses import JSONResponse
from bs4 import BeautifulSoup


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient()
    try:
        yield
    finally:
        await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)

# Allow web interface to call this API from another origin during development.
# UI_ORIGIN should contain the frontend domain (e.g. http://localhost:5173)
ui_origin = os.getenv("UI_ORIGIN")
allow = [ui_origin] if ui_origin else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow,
    allow_methods=["*"],
    allow_headers=["Content-Type", "Authorization"],
)
app.add_middleware(SecurityHeadersMiddleware)


class RawAnalyzeRequest(BaseModel):
    domain: str


class ReadyResponse(BaseModel):
    ready: bool


def _lookup(host: str) -> list:
    try:
        return socket.getaddrinfo(host, None, flags=socket.AI_CANONNAME)
    except socket.gaierror:
        return []


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/ready", response_model=ReadyResponse, tags=["Service"])
async def ready() -> ReadyResponse:
    return ReadyResponse(ready=True)


@app.post("/analyze")
async def analyze(req: RawAnalyzeRequest) -> JSONResponse:
    try:
        clean_url = normalize_url(req.domain)
    except Exception:  # noqa: BLE001
        raise HTTPException(status_code=400, detail="Invalid domain")
    domain = urlparse(clean_url).hostname
    if not domain:
        raise HTTPException(status_code=400, detail="Invalid domain")

    domain = domain.lower()
    bare = domain
    if domain.startswith("www."):
        bare = domain[4:]
    www = f"www.{bare}"
    results = {bare: _lookup(bare), www: _lookup(www)}

    resolved = [d for d, info in results.items() if info]
    if not resolved:
        raise HTTPException(status_code=400, detail="Domain unresolved")

    notes = []
    for host, info in results.items():
        if info:
            notes.append(f"{host} resolved to {len(info)} records")
        else:
            notes.append(f"{host} did not resolve")

    actionable = [n for n in notes if "resolve" not in n.lower()]
    actionable = actionable[:3]

    confidence = len(resolved) / len(results)

    industry = ""
    location = ""
    logo_url = ""
    tagline = ""
    enrich_url = os.getenv("ENRICH_URL")
    if enrich_url:
        try:
            resp = await app.state.client.get(
                f"{enrich_url}?domain={bare}", timeout=5
            )
            resp.raise_for_status()
            data = resp.json()
            industry = data.get("industry", "") or data.get("category", "")
            location = data.get("location", "") or data.get("country", "")
            logo_url = (
                data.get("logoUrl")
                or data.get("logo_url")
                or data.get("logo")
                or ""
            )
        except Exception:  # noqa: BLE001
            pass

    # Attempt to fetch a short tagline from the site itself.
    fetch_domain = resolved[0]
    try:
        resp = await app.state.client.get(f"https://{fetch_domain}", timeout=5)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.find("title")
        if title and title.get_text(strip=True):
            tagline = title.get_text(strip=True)
        else:
            meta = soup.find("meta", attrs={"name": "description"})
            if meta and meta.get("content"):
                tagline = meta["content"].strip()
    except Exception:  # noqa: BLE001
        pass

    payload = {
        "domains": resolved,
        "confidence": round(confidence, 2),
        "industry": industry,
        "location": location,
        "logoUrl": logo_url,
        "tagline": tagline,
    }
    if actionable:
        payload["notes"] = actionable

    return JSONResponse(payload)

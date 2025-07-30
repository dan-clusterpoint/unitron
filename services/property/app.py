from __future__ import annotations

import os
from urllib.parse import urlparse
import socket
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
import httpx
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.shared.utils import normalize_url
from starlette.responses import JSONResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient()
    try:
        yield
    finally:
        await app.state.client.aclose()


app = FastAPI(lifespan=lifespan)

# Allow web interface to call this API from another origin during development
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

    confidence = len(resolved) / len(results)

    return JSONResponse(
        {
            "domains": resolved,
            "confidence": round(confidence, 2),
            "notes": notes,
        }
    )

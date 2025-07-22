from __future__ import annotations

import os
import re
import socket
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse

DOMAIN_RE = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")

app = FastAPI()

# Allow web interface to call this API from another origin during development
origins = [os.getenv("VITE_API_BASE_URL", "*")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
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


@app.get("/ready", response_model=ReadyResponse)
async def ready() -> ReadyResponse:
    return ReadyResponse(ready=True)


@app.post("/analyze")
async def analyze(req: AnalyzeRequest) -> JSONResponse:
    domain = req.domain.strip().lower()
    if not DOMAIN_RE.fullmatch(domain):
        raise HTTPException(status_code=400, detail="Invalid domain")

    bare = domain
    www = f"www.{domain}"
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

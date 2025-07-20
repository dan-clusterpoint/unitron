from __future__ import annotations

import re
import socket
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse

DOMAIN_RE = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")

app = FastAPI()


class AnalyzeRequest(BaseModel):
    domain: str


def _lookup(host: str) -> list:
    try:
        return socket.getaddrinfo(host, None, flags=socket.AI_CANONNAME)
    except socket.gaierror:
        return []


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


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
        {"domains": resolved, "confidence": round(confidence, 2), "notes": notes}
    )

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
import httpx
import os
from uuid import uuid4
from shared.db import upsert_job, get_job
from shared.models import JobStatus

MARTECH_URL = os.getenv("MARTECH_URL")
N8N_URL = os.getenv("N8N_URL")
N8N_WORKFLOW_ID = os.getenv("N8N_WORKFLOW_ID", "1")

app = FastAPI(title="Unitron Gateway Service")

martech_app = FastAPI()

class TechRequest(BaseModel):
    url: str

class TechResponse(BaseModel):
    core: list[str]
    adjacent: list[str]
    broader: list[str]
    competitors: list[str]


@app.get("/health")
def health():
    """Lightweight liveness probe."""
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    """Check downstream service health."""
    services = {
        "martech": MARTECH_URL,
    }
    results = {}
    async with httpx.AsyncClient() as client:
        async def check(name: str, url: str) -> tuple[str, bool]:
            try:
                resp = await client.get(f"{url}/health", timeout=2)
                return name, resp.status_code == 200
            except Exception:
                return name, False

        tasks = [check(name, url) for name, url in services.items() if url]
        for name, ok in await asyncio.gather(*tasks):
            results[name] = ok
    status = "ok" if all(results.values()) else "degraded"
    return {"status": status, "services": results}


@martech_app.post("/analyze", response_model=TechResponse)
async def martech_analyze(req: TechRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{MARTECH_URL}/analyze", json=req.model_dump())
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Martech service error")
    return resp.json()

app.mount("/martech", martech_app)


@app.post("/jobs/start", response_model=JobStatus)
async def jobs_start():
    if not N8N_URL:
        raise HTTPException(status_code=500, detail="N8N_URL not configured")
    job_id = str(uuid4())
    upsert_job(job_id, "start", "pending")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{N8N_URL}/api/v1/workflows/{N8N_WORKFLOW_ID}/execute",
                json={"job_id": job_id},
            )
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"n8n error: {e}")
    return JobStatus(job_id=job_id, stage="start", status="pending")


@app.get("/jobs/{job_id}", response_model=JobStatus)
async def jobs_get(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**job)

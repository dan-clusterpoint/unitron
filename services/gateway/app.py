from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from uuid import uuid4
from shared.db import upsert_job, get_job
from shared.models import JobStatus

PROPERTY_URL = os.getenv("PROPERTY_URL")
MARTECH_URL  = os.getenv("MARTECH_URL")
N8N_URL = os.getenv("N8N_URL")
N8N_WORKFLOW_ID = os.getenv("N8N_WORKFLOW_ID", "1")

app = FastAPI(title="Unitron Gateway Service")

property_app = FastAPI()
martech_app = FastAPI()

class PropertyRequest(BaseModel):
    domain: str

class PropertyResponse(BaseModel):
    domain: str
    confidence: float
    notes: list[str]

class TechRequest(BaseModel):
    url: str

class TechResponse(BaseModel):
    core: list[str]
    adjacent: list[str]
    broader: list[str]
    competitors: list[str]

class CombinedRequest(BaseModel):
    property: PropertyRequest
    martech: TechRequest

class CombinedResponse(BaseModel):
    property: PropertyResponse
    martech: TechResponse

@app.get("/health")
async def health():
    return {"status": "ok"}

@property_app.post("/analyze", response_model=PropertyResponse)
async def property_analyze(req: PropertyRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{PROPERTY_URL}/analyze", json=req.model_dump())
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Property service error")
    return resp.json()

@martech_app.post("/analyze", response_model=TechResponse)
async def martech_analyze(req: TechRequest):
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{MARTECH_URL}/analyze", json=req.model_dump())
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, "Martech service error")
    return resp.json()

app.mount("/property", property_app)
app.mount("/martech", martech_app)

@app.post("/analyze", response_model=CombinedResponse)
async def analyze(req: CombinedRequest):
    async with httpx.AsyncClient() as client:
        prop_r = await client.post(
            f"{PROPERTY_URL}/analyze", json=req.property
        )
        if prop_r.status_code != 200:
            raise HTTPException(prop_r.status_code, "Property service error")
        tech_r = await client.post(
            f"{MARTECH_URL}/analyze", json=req.martech
        )
        if tech_r.status_code != 200:
            raise HTTPException(tech_r.status_code, "Martech service error")
    return CombinedResponse(property=prop_r.json(), martech=tech_r.json())


@app.post("/jobs/start", response_model=JobStatus)
async def jobs_start():
    if not N8N_URL:
        raise HTTPException(status_code=500, detail="N8N_URL not configured")
    job_id = str(uuid4())
    await upsert_job(job_id, "start", "pending")
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
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobStatus(**job)

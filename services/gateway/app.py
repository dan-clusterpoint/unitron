from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import os
from services.gateway.models import AnalyzeResponse

PROPERTY_URL = os.getenv("PROPERTY_URL")
MARTECH_URL = os.getenv("MARTECH_URL")

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


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_endpoint(request: PropertyRequest) -> AnalyzeResponse:
    async with httpx.AsyncClient() as client:
        martech_res = await client.post(
            f"{MARTECH_URL}/analyze",
            json={"url": request.domain},
        )
    if martech_res.status_code != 200:
        raise HTTPException(martech_res.status_code, "Martech service error")
    return AnalyzeResponse(
        property=request,
        martech=martech_res.json(),
    )

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import builtwith

app = FastAPI(title="Martech Analyzer Service")

class AnalyzeRequest(BaseModel):
    url: str

class AnalyzeResponse(BaseModel):
    core: list[str]
    adjacent: list[str]
    broader: list[str]
    competitors: list[str]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    try:
        tech_data = builtwith.parse(req.url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    core, adjacent, broader, competitors = [], [], [], []
    COMPETITORS = {"Sitecore", "Optimizely", "Salesforce", "Contentful"}

    for tech, categories in tech_data.items():
        cats = [c.lower() for c in categories]
        if any(k in cats for k in ["cms", "analytics", "marketing", "tag manager"]):
            core.append(tech)
        elif any(k in cats for k in ["cdn", "cloud", "security"]):
            broader.append(tech)
        else:
            adjacent.append(tech)
        if tech in COMPETITORS:
            competitors.append(tech)

    return AnalyzeResponse(
        core=core,
        adjacent=adjacent,
        broader=broader,
        competitors=competitors
    )

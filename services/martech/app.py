from fastapi import FastAPI
from pydantic import BaseModel
import builtwith

app = FastAPI(title="Martech Analyzer Service")

COMPETITORS = {"Sitecore", "Optimizely", "Salesforce", "Contentful"}

class TechRequest(BaseModel):
    url: str

class TechResponse(BaseModel):
    core: list[str]
    adjacent: list[str]
    broader: list[str]
    competitors: list[str]

@app.post("/analyze", response_model=TechResponse)
async def analyze(req: TechRequest):
    data = builtwith.parse(req.url)
    core, adjacent, broader, competitors = [], [], [], []
    for tech, cats in data.items():
        cats_lower = [c.lower() for c in cats]
        if any(k in cats_lower for k in ["cms", "tag manager", "analytics", "marketing"]):
            core.append(tech)
        elif any(k in cats_lower for k in ["cdn", "cloud", "security"]):
            broader.append(tech)
        else:
            adjacent.append(tech)
        if tech in COMPETITORS:
            competitors.append(tech)
    return TechResponse(core=core, adjacent=adjacent, broader=broader, competitors=competitors)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from detect import detect

app = FastAPI(title="Martech Analyzer Service (OSS)")

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
        data = detect(req.url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"martech detection error: {e}")

    return AnalyzeResponse(
        core=data["core"],
        adjacent=data["adjacent"],
        broader=data["broader"],
        competitors=data["competitors"],
        evidence=data.get("evidence"),
    )

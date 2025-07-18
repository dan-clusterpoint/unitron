from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI(title="Insight Agent Service")

class CompanyInfo(BaseModel):
    name: str
    website: str | None = None
    description: str | None = None

class NotesResponse(BaseModel):
    notes: str

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/generate", response_model=NotesResponse)
async def generate(info: CompanyInfo):
    if not openai.api_key:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY not configured")

    prompt = f"Generate research notes for the company {info.name}."
    if info.website:
        prompt += f" Website: {info.website}."
    if info.description:
        prompt += f" Description: {info.description}."
    try:
        resp = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
        )
        notes = resp.choices[0].message.content.strip()
        return NotesResponse(notes=notes)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

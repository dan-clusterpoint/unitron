from __future__ import annotations

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import JSONResponse

try:  # Optional dependency
    import openai
except Exception:  # noqa: BLE001
    openai = None  # type: ignore

app = FastAPI()

origins = [os.getenv("UI_ORIGIN", "*")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class InsightRequest(BaseModel):
    text: str


class ReadyResponse(BaseModel):
    ready: bool


def _sanitize(text: str) -> str:
    """Return a compact single-line version of ``text``."""
    return " ".join(text.strip().split())


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/ready", response_model=ReadyResponse, tags=["Service"])
async def ready() -> ReadyResponse:
    return ReadyResponse(ready=True)


@app.post("/generate-insights")
async def generate_insights(req: InsightRequest) -> JSONResponse:
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Empty text")
    sanitized = _sanitize(req.text)
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or openai is None:
        raise HTTPException(status_code=503, detail="OpenAI not configured")
    client = openai.AsyncOpenAI(api_key=api_key)
    try:
        resp = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Generate concise insights."},
                {"role": "user", "content": sanitized},
            ],
            max_tokens=100,
        )
        content = resp.choices[0].message.content.strip()
    except Exception:  # noqa: BLE001

        raise HTTPException(
            status_code=500,
            detail="Failed to generate insights",
        )
    return JSONResponse({"insight": content})

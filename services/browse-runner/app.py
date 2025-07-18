from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from pathlib import Path
import pathlib
import os
import boto3
from playwright.async_api import async_playwright

SCREENSHOT_DIR = os.getenv("SCREENSHOT_DIR", "/tmp/screenshots")
S3_BUCKET = os.getenv("S3_BUCKET")

app = FastAPI(title="Browse Runner Service")

class RunRequest(BaseModel):
    script: str

class RunResponse(BaseModel):
    screenshots: List[str]

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/run", response_model=RunResponse)
async def run(req: RunRequest):
    screenshot_dir = Path(SCREENSHOT_DIR)
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        page = await browser.new_page()
        local_env = {"page": page, "screenshot_dir": str(screenshot_dir), "pathlib": pathlib}
        exec(req.script, local_env)
        if callable(local_env.get("main")):
            await local_env["main"](page=page, screenshot_dir=str(screenshot_dir))
        await browser.close()

    shots = []
    if S3_BUCKET:
        s3 = boto3.client("s3")
        for img in screenshot_dir.glob("*.png"):
            s3.upload_file(str(img), S3_BUCKET, img.name)
            shots.append(f"https://{S3_BUCKET}.s3.amazonaws.com/{img.name}")
    else:
        shots = [str(p.name) for p in screenshot_dir.glob("*.png")]

    return RunResponse(screenshots=shots)

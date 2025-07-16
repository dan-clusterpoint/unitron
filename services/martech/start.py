from fastapi import FastAPI
import os
import logging
import uvicorn
from app import app as martech_app

app = FastAPI()

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok"}

# Mount the existing application under root
app.mount("/", martech_app)

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    logging.getLogger("uvicorn.error").info("\ud83d\ude80 Starting Martech on 0.0.0.0:%s", port)
    uvicorn.run("start:app", host="0.0.0.0", port=port)

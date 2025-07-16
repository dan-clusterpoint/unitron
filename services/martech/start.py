import os
import logging
import uvicorn
from app import app  # relative import; PYTHONPATH handled in Dockerfile

log = logging.getLogger("uvicorn.error")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    log.info("\ud83d\ude80 Starting Martech on 0.0.0.0:%s", port)
    uvicorn.run(app, host="0.0.0.0", port=port)

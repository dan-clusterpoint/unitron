import os
import logging
import uvicorn

from app import app

log = logging.getLogger("uvicorn.error")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    log.info("\u2728 Starting service on 0.0.0.0:%s", port)
    uvicorn.run(app, host="0.0.0.0", port=port)

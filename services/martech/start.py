import os
import logging
import uvicorn

from app import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("martech.start")


def main() -> None:
    raw_port = os.getenv("PORT", "8000").strip()
    try:
        port = int(raw_port)
    except ValueError:
        logger.warning("Invalid PORT value %r; falling back to 8000", raw_port)
        port = 8000

    host = "0.0.0.0"
    logger.info("\U0001F680 Martech starting on %s:%s", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()

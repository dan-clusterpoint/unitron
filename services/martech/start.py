import os
import logging
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("martech.start")


def get_port(default: int = 8000) -> int:
    val = os.getenv("PORT") or os.getenv("RAILWAY_STATIC_PORT")
    try:
        p = int(val)
        if not (0 < p < 65536):
            raise ValueError
        return p
    except Exception:
        return default


def main() -> None:
    from app import app

    port = get_port()
    host = "0.0.0.0"
    logger.info("\U0001F680 Martech starting on %s:%s", host, port)
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()

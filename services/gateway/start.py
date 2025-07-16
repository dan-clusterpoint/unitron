import os
import sys
import uvicorn


def get_port(default: int = 8000) -> int:
    """Return PORT env var as int, falling back safely."""
    val = os.getenv("PORT") or os.getenv("RAILWAY_STATIC_PORT")
    try:
        p = int(val)
        if not (0 < p < 65536):
            raise ValueError
        return p
    except Exception:
        return default


def main() -> None:
    from gateway.app import app

    port = get_port()
    print(f"[gateway] \U0001F680 starting on 0.0.0.0:{port}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

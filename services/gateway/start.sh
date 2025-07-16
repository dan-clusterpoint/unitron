#!/usr/bin/env bash
set -euo pipefail
PORT="${PORT:-80}"
echo "[gateway] PORT='${PORT}' → starting uvicorn"
exec uvicorn app:app --host 0.0.0.0 --port "${PORT}"

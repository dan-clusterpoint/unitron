#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PORT="${PORT:-8000}"
echo "[martech] Starting on port ${PORT}..."
exec uvicorn app:app --host 0.0.0.0 --port "${PORT}"

#!/usr/bin/env sh
set -e

# Expand defaults safely
SERVICE="${SERVICE:-gateway}"
PORT="${PORT:-8000}"

# Validate import *before* running uvicorn
python /app/ops/validate_import.py

# Start uvicorn with fully-qualified path
exec uvicorn "services.${SERVICE}.app:app" --host 0.0.0.0 --port "${PORT}"

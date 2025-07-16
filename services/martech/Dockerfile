FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=60

# Install build prerequisites for lxml and others
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libxml2-dev libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements early for caching
COPY requirements.txt /tmp/requirements.txt
COPY ../../constraints /tmp/constraints

# Upgrade packaging tools separately
RUN python -m pip install --upgrade "pip<25" "setuptools>=70" "wheel>=0.44"

# Install dependencies with retries and verbose logging
RUN set -ex; \
    pip install --retries 5 --timeout 60 --no-cache-dir \
      -r /tmp/requirements.txt \
      > /tmp/pip-install.log 2>&1 || \
    (echo '--- pip install failed; dumping log ---' && cat /tmp/pip-install.log && exit 1) \
    && python - <<'PY'
import fastapi, pydantic, httpx
import bs4, lxml
print("FastAPI:", fastapi.__version__)
print("Pydantic:", pydantic.__version__)
PY

WORKDIR /app
COPY . /app

ENV PORT=8000
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "start:app", "--host", "0.0.0.0", "--port", "8000"]

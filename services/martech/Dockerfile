FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential libxml2-dev libxslt1-dev curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

COPY . .

# Build-time import check
RUN python - <<'PY'
import fastapi, httpx, bs4, lxml
print("✅ imports ok")
PY

ENV PORT=8000
EXPOSE 8000
CMD ["python", "start.py"]

FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install build tooling (only what's needed; expand later if libmagic, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy service code
COPY . .

# default fallback; Railway passes PORT env var at runtime
ENV PORT=8000
EXPOSE 8000

CMD ["python", "start.py"]

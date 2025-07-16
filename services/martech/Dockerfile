FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1) Upgrade pip first so it’s cached separately
RUN pip install --upgrade pip

# Install build tooling (only what's needed; expand later if libmagic, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2) Copy & install requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# 3) Copy service code
COPY . .

# default fallback; Railway passes PORT env var at runtime
ENV PORT=8000
EXPOSE 8000

CMD ["python", "start.py"]

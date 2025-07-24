FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
ENV PORT=8000

WORKDIR /app

# This Dockerfile expects the repository root as the build context.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source after installing dependencies
COPY . /app
ENV PYTHONPATH=/app/src:/app/services:/app

EXPOSE 8000
HEALTHCHECK --interval=2s --timeout=2s --start-period=5s \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

CMD ["sh", "-c", "uvicorn property.app:app --host 0.0.0.0 --port ${PORT:-8000}"]

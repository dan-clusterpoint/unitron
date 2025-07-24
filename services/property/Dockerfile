FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
ENV PORT=8000

WORKDIR /app

# Install dependencies from root project
COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry==1.7.1 \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-root

# Copy the property service and shared modules
COPY src/shared /app/shared
COPY services/property /app/property
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["sh", "-c", "uvicorn property.app:app --host 0.0.0.0 --port ${PORT:-8000}"]

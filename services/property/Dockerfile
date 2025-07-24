FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
ENV PORT=8000

WORKDIR /app

# Copy the entire repository so paths resolve correctly even when the build
# context is ``services/property``.
COPY ../.. /app
ENV PYTHONPATH=/app

# Install dependencies from the project files that were copied in the previous
# step.
RUN pip install --no-cache-dir poetry==1.7.1 \
    && poetry config virtualenvs.create false \
    && poetry install --only main --no-root

# Optionally list files for troubleshooting
RUN ls -R /app

EXPOSE 8000

CMD ["sh", "-c", "uvicorn property.app:app --host 0.0.0.0 --port ${PORT:-8000}"]

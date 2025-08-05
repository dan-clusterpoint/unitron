FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry \
    && poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction
COPY . /app
ENV PYTHONPATH=/app/services:/app
EXPOSE 8000
HEALTHCHECK CMD curl -fsS http://127.0.0.1:8000/health || exit 1
# Each service exposes its own FastAPI app under `services/<name>/app.py`.
# The `SERVICE` environment variable selects which module Uvicorn runs.
CMD ["sh", "-c", "uvicorn services.${SERVICE}.app:app --host 0.0.0.0 --port ${PORT:-8000}"]

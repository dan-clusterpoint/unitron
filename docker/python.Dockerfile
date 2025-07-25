FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    PORT=8000

WORKDIR /app

# 1. Install deps deterministically via Poetry OR fallback requirements.txt
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction && \
    playwright install --with-deps

# 2. Copy entire repo
COPY . /app

# 3. (Optional) Fallback if no poetry - leave in place but not used if poetry works
# RUN test -f requirements.txt && pip install -r requirements.txt || true

# 4. Import check at build time (fail fast)
ARG SERVICE=gateway
RUN python /app/ops/validate_import.py

# Healthcheck should be light: only /health
HEALTHCHECK --interval=5s --timeout=2s --start-period=10s --retries=12 \
  CMD curl -fsS http://127.0.0.1:${PORT}/health || exit 1

EXPOSE 8000

CMD ["/app/ops/entrypoint.sh"]

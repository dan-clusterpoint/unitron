FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
ENV PYTHONPATH=/app
ENV PORT=8000

ARG SERVICE

WORKDIR /app

# Copy dependencies file if available and install
COPY requirements.txt /tmp/requirements.txt
RUN if [ -f /tmp/requirements.txt ]; then \
        pip install --no-cache-dir -r /tmp/requirements.txt; \
    else \
        echo "fastapi\nuvicorn[standard]" > /tmp/requirements.txt && \
        pip install --no-cache-dir -r /tmp/requirements.txt; \
    fi

# Copy application code
COPY src/ /app/src
COPY services/ /app/services
COPY fingerprints.yaml /app/

EXPOSE ${PORT}

HEALTHCHECK --interval=2s --timeout=2s --start-period=5s \
  CMD curl -fsS http://127.0.0.1:${PORT}/health || exit 1

CMD ["uvicorn", "services.${SERVICE}.app:app", "--host", "0.0.0.0", "--port", "${PORT}"]

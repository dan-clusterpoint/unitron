FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
ENV PORT=8000

WORKDIR /app
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src
COPY services/ /app/services
COPY fingerprints.yaml /app/
ENV PYTHONPATH=/app/services:/app

# Expose port
EXPOSE 8000

# Liveness probe
HEALTHCHECK --interval=2s --timeout=2s --start-period=5s \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# Default to gateway; override SERVICE=martech for that service
# Use a shell to expand $PORT so Railway can inject the port number
CMD ["sh", "-c", "uvicorn services.${SERVICE:-gateway}.app:app --host 0.0.0.0 --port ${PORT:-8000}"]

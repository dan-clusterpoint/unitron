FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install build prerequisites for lxml and others
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential libxml2-dev libxslt1-dev && \
    rm -rf /var/lib/apt/lists/*

# Install pinned runtime dependencies
COPY constraints /tmp/constraints
RUN pip install --no-cache-dir -r /tmp/constraints/python311-common.txt

# Install service requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["python", "-m", "uvicorn", "start:app", "--host", "0.0.0.0", "--port", "8000"]

# Located at services/python.Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8000 \
    # This ensures Python can find your modules.
    PYTHONPATH=/app

# Set the working directory
WORKDIR /app

# Copy and install dependencies from the root.
# The build will correctly fail if this file is missing.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy all your code into the container.
# This makes `services/`, `src/`, etc. available at /app/services, /app/src...
COPY . /app/

# Expose the port
EXPOSE 8000

# Set up a generic health check.
HEALTHCHECK --interval=5s --timeout=3s --start-period=10s \
  CMD curl -fsS http://127.0.0.1:8000/health || exit 1

# No CMD is needed here because railway.toml will provide the startCommand.
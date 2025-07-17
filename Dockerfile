# Use official Python image
FROM python:3.11-slim AS base
WORKDIR /app

# Copy and install dependencies
COPY services/property/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and startup script
COPY shared ./shared
COPY services/property/ .
RUN chmod +x start.sh

# Railway sets `RAILWAY_ENVIRONMENT` automatically but the value is not
# consumed during build or runtime, so no build arguments are required.

# Expose and run
EXPOSE 80
CMD ["./start.sh"]

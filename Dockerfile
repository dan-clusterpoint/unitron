# Use official Python image
FROM python:3.11-slim AS base
WORKDIR /app

# Copy and install dependencies
COPY services/property/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY services/property/ .

# Set args for Railway variables during build
ARG RAILWAY_ENVIRONMENT

# Expose and run
EXPOSE 80
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

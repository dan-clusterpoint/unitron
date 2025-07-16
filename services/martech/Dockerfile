# 1) Base image
FROM python:3.11-slim

# 2) Speed up installs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3) Work directory
WORKDIR /app

# 4) Copy & upgrade pip + install requirements
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 5) Copy application code
COPY . .

# 6) Expose proper port & default
EXPOSE 8000
ENV PORT=8000

# 7) Launch Uvicorn bound to 0.0.0.0:8000
CMD ["uvicorn", "start:app", "--host", "0.0.0.0", "--port", "8000"]

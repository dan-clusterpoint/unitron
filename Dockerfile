# ---- Base image ----
FROM python:3.11-slim AS base
WORKDIR /app

# ---- Install deps ----
COPY services/property/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy source ----
COPY services/property/ .

# ---- Run ----
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

FROM python:3.11-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    build-essential \
    libxml2-dev \
    libxslt-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
COPY ../../constraints/python311.txt /constraints/python311.txt

RUN pip install --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt \
    --constraint=/constraints/python311.txt

COPY . .

ENV PORT=8000
EXPOSE 8000

CMD ["python", "start.py"]

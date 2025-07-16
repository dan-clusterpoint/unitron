FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY services/martech/requirements.txt /tmp/requirements.txt
COPY constraints/python311.txt /tmp/constraints.txt
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /tmp/requirements.txt \
        --constraint=/tmp/constraints.txt

COPY services/martech /app

WORKDIR /app
EXPOSE 8000

ENTRYPOINT ["sh", "-c"]
CMD ["exec uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]

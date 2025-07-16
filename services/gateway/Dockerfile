FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt /tmp/requirements.txt
COPY constraints.txt /tmp/constraints.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir --constraint /tmp/constraints.txt -r /tmp/requirements.txt

COPY . .

ENV PORT=8000
EXPOSE $PORT

CMD ["uvicorn", "gateway.app:app", "--host", "0.0.0.0", "--port", "$PORT"]

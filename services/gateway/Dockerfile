FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./requirements.txt
COPY ../../constraints/python311.txt /constraints/python311.txt
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt \
    --constraint=/constraints/python311.txt

COPY . /app

EXPOSE 8000

CMD ["python", "start.py"]

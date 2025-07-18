FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
WORKDIR /app
# Copy the entire services package so martech can import shared code
COPY services/ ./services/
COPY services/martech/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY services/martech ./services/martech
EXPOSE 8000
HEALTHCHECK CMD curl -fsS http://127.0.0.1:8000/health || exit 1
CMD ["uvicorn", "services.martech.app:app", "--host", "0.0.0.0", "--port", "8000"]

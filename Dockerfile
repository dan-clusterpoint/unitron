FROM python:3.11.13-slim
WORKDIR /app
COPY services/gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY services/gateway/ .
COPY shared/ ./shared
RUN chmod +x start.sh
EXPOSE 80
CMD ["./start.sh"]

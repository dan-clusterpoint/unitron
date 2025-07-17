FROM python:3.11-slim
WORKDIR /app
COPY services/gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared ./shared
COPY services/gateway/ .
RUN chmod +x start.sh
EXPOSE 80
CMD ["./start.sh"]


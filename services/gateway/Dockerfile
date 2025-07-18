FROM python:3.11.13-slim
WORKDIR /app
# Copy requirements from the gateway service directory
COPY services/gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Include shared modules located at the repo root
COPY shared ./shared
# Copy the gateway source code
COPY services/gateway/ .
RUN chmod +x start.sh
EXPOSE 80
CMD ["./start.sh"]


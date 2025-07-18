FROM python:3.11.13-slim
WORKDIR /app
# Copy requirements from the gateway service directory
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Include shared modules located one directory up
COPY ../shared ./shared
# Copy the gateway source code
COPY . .
RUN chmod +x start.sh
EXPOSE 80
CMD ["./start.sh"]


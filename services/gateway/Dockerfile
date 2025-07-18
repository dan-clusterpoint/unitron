FROM python:3.11.13-slim
WORKDIR /app

# Install dependencies for the gateway service
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pull in shared utilities
COPY ../shared ./shared

# Copy the gateway application code
COPY . .
RUN chmod +x start.sh

EXPOSE 80
CMD ["./start.sh"]


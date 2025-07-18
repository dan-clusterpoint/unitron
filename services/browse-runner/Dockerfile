FROM mcr.microsoft.com/playwright/python:v1.42.0-jammy
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN chmod +x start.sh

EXPOSE 80
CMD ["./start.sh"]

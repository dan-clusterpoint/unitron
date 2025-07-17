FROM python:3.11.13-slim
WORKDIR /app
COPY services/martech/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY shared ./shared
COPY services/martech/ .
RUN chmod +x start.sh
EXPOSE 80
CMD ["./start.sh"]

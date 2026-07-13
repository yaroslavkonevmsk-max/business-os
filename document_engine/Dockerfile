# Dockerfile for Document Engine (Celery + docxtpl + LibreOffice)
FROM python:3.11-slim

WORKDIR /app

# Install build deps + LibreOffice headless + fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev libpq5 \
    libreoffice-writer libreoffice-calc \
    fonts-liberation fonts-dejavu \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

CMD ["celery", "-A", "app.main", "worker", "-l", "info", "-Q", "documents"]


FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copy application code
COPY . .

# Create directories and a non-root user
RUN adduser --disabled-password --gecos "" appuser \
    && mkdir -p /app/staticfiles \
                /app/media \
                /app/smart_inventory/staticfiles \
                /app/smart_inventory/media \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

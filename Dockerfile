# Multi-stage production container for Railway.com
FROM python:3.11-slim

# Set environment — do NOT set PORT here; Railway injects it at runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose default port for local dev (Railway overrides with $PORT)
EXPOSE 5050

# Shell form (no JSON array) — Docker runs this via /bin/sh -c, so $PORT expands correctly at runtime
CMD gunicorn dashboard.app:app --bind 0.0.0.0:${PORT:-5050} --workers 2 --threads 4 --timeout 120

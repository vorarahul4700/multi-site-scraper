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

# Make entrypoint executable
RUN chmod +x start.sh

# Expose default port for local dev (Railway overrides with $PORT)
EXPOSE 5050

# Use shell script so $PORT is evaluated at runtime, not build time
CMD ["sh", "start.sh"]

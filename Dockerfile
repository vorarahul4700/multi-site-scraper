# Multi-stage production container for Railway.com
FROM python:3.11-slim

# Set environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5050

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

# Expose port (overridden dynamically by Railway $PORT)
EXPOSE 5050

# Launch with Gunicorn
CMD ["sh", "-c", "gunicorn dashboard.app:app --bind 0.0.0.0:${PORT:-5050} --workers 2 --threads 4 --timeout 120"]

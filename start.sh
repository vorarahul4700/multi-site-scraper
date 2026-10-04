#!/bin/sh
# Railway injects $PORT at runtime — read it here safely
exec gunicorn dashboard.app:app \
  --bind "0.0.0.0:${PORT:-5050}" \
  --workers 2 \
  --threads 4 \
  --timeout 120

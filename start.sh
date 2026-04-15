#!/usr/bin/env sh
set -eu

PORT="${PORT:-8000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
WEB_TIMEOUT="${WEB_TIMEOUT:-120}"
APP_MODULE="${APP_MODULE:-app.main:app}"

echo "Applying database migrations..."
alembic upgrade head

echo "Starting MealMate..."
exec gunicorn \
  -k uvicorn.workers.UvicornWorker \
  "${APP_MODULE}" \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout "${WEB_TIMEOUT}" \
  --access-logfile "-" \
  --error-logfile "-" \
  --forwarded-allow-ips "*"

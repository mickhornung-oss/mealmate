# Deployment Guide

This document describes the supported deployment baseline for MealMate.

## Runtime Requirements
- Python 3.12 (containerized runtime recommended)
- PostgreSQL for production
- Environment variables configured explicitly

## Required Environment Variables
- `APP_ENV=prod`
- `APP_URL=https://<your-domain>`
- `SECRET_KEY=<long-random-secret>`
- `DATABASE_URL=postgresql+psycopg://...`
- `ALLOWED_HOSTS=<your-domain>[,additional-domain]`
- `COOKIE_SECURE=1`
- `TOKEN_EXPIRE_MINUTES=60`
- `MAX_UPLOAD_MB=4`
- `AUTO_SEED_KOCHWIKI=0`
- `PORT=<platform-port>`
- `WEB_CONCURRENCY=<worker-count>`
- `WEB_TIMEOUT=<seconds>`

## Local Container Validation
```bash
docker compose up --build
```

Validation endpoints:
- `http://localhost:8000/health`
- `http://localhost:8000/healthz`

## Render Baseline
The repository includes `render.yaml` and `Dockerfile`.

Deployment sequence:
1. Connect repository in Render.
2. Use Docker deployment.
3. Set required environment variables.
4. Provide a managed PostgreSQL `DATABASE_URL`.
5. Verify `/healthz` after rollout.

## Migration Behavior
- Container startup runs `alembic upgrade head` (`start.sh`).
- App then starts with Gunicorn + Uvicorn worker.

## Operability and Diagnostics
- Every response includes `X-Request-ID`.
- Correlate request/incident traces through application logs using `request_id`.
- For mutation/conflict triage, use `docs/development/OPERABILITY.md`.

Recommended log filters:
- `mealmate.request`
- `mealmate.translation.batch`
- `mealmate.translations`
- `mealmate.submissions`
- `mealmate.admin`

## Release Verification (Minimum)
Run after each deployment:
1. `GET /healthz` returns `200 {"status":"ok"}`.
2. Login flow works (`/login`).
3. Admin route protection works (`/admin` for admin only).
4. Translation batch start conflict contract returns `409` when a batch is already active.

## Production Notes
- Do not use SQLite in production.
- Never keep the default `SECRET_KEY`.
- Keep `AUTO_SEED_KOCHWIKI=0` in production environments.

# MealMate Deployment Guide

Dieses Dokument zeigt zwei einfache Wege, um MealMate als oeffentliche Website zu deployen.

## Voraussetzungen

- Ein GitHub-Repository mit diesem Projekt.
- Eine erzeugte `SECRET_KEY` mit hoher Entropie.
- `AUTO_SEED_KOCHWIKI=0` in Produktion als sicherer Standard.

## Wichtige ENV Variablen

- `APP_ENV=prod`
- `APP_URL=https://deine-domain`
- `SECRET_KEY=<lange-zufaellige-zeichenkette>`
- `DATABASE_URL=<postgres-connection-string>`
- `ALLOWED_HOSTS=deine-domain[,weitere-domain]`
- `COOKIE_SECURE=1`
- `TOKEN_EXPIRE_MINUTES=60`
- `MAX_UPLOAD_MB=4`
- `AUTO_SEED_KOCHWIKI=0`

## Weg A (Empfohlen): Neon + Render

1. Erstelle bei Neon ein neues Projekt und kopiere den Postgres Connection String.
2. Passe den Connection String fuer SQLAlchemy an (`postgresql+psycopg://...`) falls noetig.
3. Pushe dieses Projekt zu GitHub.
4. Erstelle auf Render einen neuen Web Service aus dem GitHub-Repository.
5. Nutze den Docker-Deploy (Render erkennt die `Dockerfile` automatisch).
6. Setze in Render die ENV Variablen aus der Liste oben.
7. Setze `DATABASE_URL` auf den Neon String.
8. Setze `ALLOWED_HOSTS` auf deine Render Domain (z. B. `mealmate.onrender.com`).
9. Deploye den Service.
10. Pruefe `https://deine-domain/healthz` auf `{ "status": "ok" }`.
11. Oeffne danach die Website im Browser und teste Login, Rezeptseite und PDF-Download.

Hinweis:
- Free-Tarife haben oft Cold Starts und schlafen bei Inaktivitaet.

## Weg B (Alternative): Supabase + Render

1. Erstelle ein Supabase Projekt und hole den Postgres Connection String.
2. Konvertiere den String bei Bedarf nach `postgresql+psycopg://...`.
3. Erstelle den Render Web Service aus dem GitHub-Repository.
4. Hinterlege die gleichen ENV Variablen wie bei Weg A.
5. Setze `DATABASE_URL` auf den Supabase String.
6. Deploye und pruefe `.../healthz`.

Hinweis:
- Supabase Free kann bei Quota-Limits gedrosselt werden oder in read-only Situationen laufen.

## Render Blueprint (Optional)

- Dieses Projekt enthaelt bereits eine `render.yaml`.
- Du kannst in Render statt manueller Konfiguration auch den Blueprint verwenden.
- Trage danach noch geheime Werte wie `DATABASE_URL` ein.

## Lokaler prod-naher Test mit Docker Compose

```bash
docker compose up --build
```

Danach:
- App: `http://localhost:8000`
- Healthcheck: `http://localhost:8000/healthz`
- DB: Postgres auf `localhost:5432`

## Migrations und Startverhalten

- Der Container startet ueber `start.sh`.
- `start.sh` fuehrt zuerst `alembic upgrade head` aus.
- Danach startet Gunicorn mit Uvicorn-Worker.
- Seed laeuft nur, wenn `AUTO_SEED_KOCHWIKI=1` gesetzt wurde.

## Sicherheitshinweise fuer Produktion

- Nutze niemals den Default `SECRET_KEY`.
- Setze `COOKIE_SECURE=1`.
- Nutze keine SQLite-Datei in Produktion.
- Begrenze `ALLOWED_HOSTS` auf echte Domains.

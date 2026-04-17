# MealMate Runbook

Dieses Runbook zeigt Setup, Start und einen durchgehenden Demo-Flow inklusive Security-Smoketests.

Operability-/Konflikt-Diagnose fuer gehaertete Mutationspfade:
- `docs/development/OPERABILITY.md`

## 1) Lokales Setup (venv)

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
py -m alembic -c alembic.ini upgrade head
py scripts/seed_admin.py
py -m uvicorn app.main:app --reload
```

Danach:
- App: `http://localhost:8000`
- Healthcheck: `http://localhost:8000/healthz`
- Admin: `admin@mealmate.local` / `AdminPass123!`

## 2) Lokales Setup mit Docker

```bash
docker compose up --build
```

Danach:
- App: `http://localhost:8000`
- Postgres: `localhost:5432`
- Healthcheck: `http://localhost:8000/healthz`

## 3) ENV Beispiele

### Dev (SQLite)

```dotenv
APP_ENV=dev
APP_URL=http://localhost:8000
SECRET_KEY=change-me-dev
DATABASE_URL=sqlite:///./mealmate.db
ALLOWED_HOSTS=*
COOKIE_SECURE=0
FORCE_HTTPS=0
ENABLE_KOCHWIKI_SEED=0
AUTO_SEED_KOCHWIKI=0
```

### Prod (Postgres)

```dotenv
APP_ENV=prod
APP_URL=https://mealmate.example.com
SECRET_KEY=<lange-zufaellige-zeichenkette>
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname
ALLOWED_HOSTS=mealmate.example.com
COOKIE_SECURE=1
FORCE_HTTPS=1
ENABLE_KOCHWIKI_SEED=0
AUTO_SEED_KOCHWIKI=0
```

## 4) Demo Flow (End-to-End)

1. Starte die App lokal oder via Docker.
2. Oeffne `http://localhost:8000/login` und melde dich als Admin an.
3. Oeffne `http://localhost:8000/admin`.
4. Seed nur bewusst und nur bei leerer DB:
   - Setze `ENABLE_KOCHWIKI_SEED=1` und `AUTO_SEED_KOCHWIKI=1` nur gezielt und starte neu.
   - Der Seed laeuft einmalig nur ohne Rezepte und mit Meta-Flag.
5. Manueller CSV Import:
   - Im Admin Panel CSV hochladen.
   - Standard ist `insert_only`; optional `update_existing`.
6. Oeffne ein Rezept im Detail.
7. Lade ein Bild hoch, setze optional Hauptbild, pruefe Anzeige.
8. Klicke `PDF herunterladen` und pruefe Download.
9. Registriere einen normalen User.
10. Als User Favorite setzen und eine Review schreiben.
11. Pruefe Discover mit Filtern, Sortierung und Pagination.

## 5) Security Checks

### CSRF Fail

```bash
curl -i -X POST http://localhost:8000/logout
```

Erwartung: `403` wegen fehlendem CSRF Token.

### CSRF Pass (mit Browser-Session)

- Seite per Browser laden, damit `csrf_token` Cookie gesetzt wird.
- Normale Form-POSTs oder HTMX-Requests senden danach Token automatisch.

### Rate Limit (Login)

- Sende 6 fehlerhafte Login-Versuche innerhalb 1 Minute.
- Erwartung: spaetestens der 6. Request liefert `429`.

### Security Headers

```bash
curl -I http://localhost:8000/
```

Erwartung: `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Request-ID`.

### Healthcheck

```bash
curl http://localhost:8000/healthz
```

Erwartung: `{"status":"ok"}`.

## 6) Smoke Test Script

Das Script testet:
- `/healthz`
- Register/Login inkl. `access_token` Cookie
- CSRF Token holen und Rezept per POST erstellen
- PDF Endpoint mit `application/pdf`

Start:

```bash
py scripts/smoke_test.py
```

Optional gegen laufende URL:

```bash
set SMOKE_BASE_URL=http://localhost:8000
py scripts/smoke_test.py
```

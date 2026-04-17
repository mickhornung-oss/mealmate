# MealMate

**Current release:** `v1.0.0`  
**Status:** Production-ready baseline (self-hosted), release-governed, and reproducible.

MealMate is a FastAPI web application for recipe management with a server-rendered UI (Jinja2 + HTMX), moderation workflows, translation support, and hardened operational contracts.

## Core Capabilities
- JWT cookie authentication with CSRF protection
- Recipe CRUD, favorites, ratings, PDF export
- Moderation workflow for recipe submissions and image-change requests
- CSV-based recipe import
- Translation workflow for `de`, `en`, `fr`

## Tech Stack
- Python 3.12, FastAPI, SQLAlchemy 2, Alembic
- Jinja2, HTMX
- SQLite for local development, PostgreSQL for deployment
- Pytest (plus optional Playwright browser E2E)
- Docker / Docker Compose

## Quickstart (Local)
Windows:
```bash
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
python -m alembic -c alembic.ini upgrade head
python scripts/seed_admin.py
python -m uvicorn app.main:app --reload
```

macOS/Linux:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
python -m alembic -c alembic.ini upgrade head
python scripts/seed_admin.py
python -m uvicorn app.main:app --reload
```

Access:
- App: `http://localhost:8000`
- Health: `http://localhost:8000/healthz`
- Admin seed user: `admin@mealmate.local` / `AdminPass123!`

## Configuration
Copy `.env.example` to `.env` and review at least:
- `APP_ENV`
- `DATABASE_URL`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `KOCHWIKI_CSV_PATH` (default: `data/seed/rezepte_kochwiki_clean_3713.csv`)
- `COOKIE_SECURE` and `FORCE_HTTPS` for production
- `PORT`, `WEB_CONCURRENCY`, `WEB_TIMEOUT` for container/runtime behavior

## Quality Gates
```bash
pytest -q
pytest -q -W error
python -m compileall app tests
```

Playwright note:
- Browser E2E tests are skipped automatically if browser binaries are missing.
- Enable locally with: `python -m playwright install chromium`

## Deployment
- Local container run: `docker compose up --build`
- Deployment baseline: `docs/deployment/DEPLOYMENT.md`
- Security verification: `docs/deployment/SECURITY.md`
- Operability diagnostics: `docs/development/OPERABILITY.md`

## Release Governance
- Changelog: `CHANGELOG.md`
- Release process: `docs/development/RELEASE.md`
- Release gate checklist: `docs/development/RELEASE_CHECKLIST.md`

## Repository Structure
```text
app/            application code (routers, services, templates, static)
alembic/        database migrations
tests/          test suite (unit/integration/e2e)
scripts/        developer/operator scripts
tools/          diagnostics and maintenance tooling
docs/           public and internal project documentation
data/seed/      local seed/import data
```

## Known Limitations
- SQLite is for local development only; production requires PostgreSQL.
- Playwright browser tests require local browser installation and are otherwise skipped.

## Documentation
- Main docs index: `docs/README.md`
- Setup baseline: `docs/development/SETUP.md`
- Testing baseline: `docs/development/TESTING.md`
- Internal documentation boundary: `docs/internal/README.md`
- Contribution guide: `CONTRIBUTING.md`

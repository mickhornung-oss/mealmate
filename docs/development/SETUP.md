# Local Setup (Reproducible Baseline)

This setup is the canonical local developer path.

## 1) Python Version
Use Python `3.12`.

Windows check:
```powershell
py -0p
```

## 2) Create a Fresh Virtual Environment
Do not rely on old local virtual environments.

Windows:
```powershell
py -3.12 -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

macOS/Linux:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Configure Environment Variables
Windows:
```powershell
copy .env.example .env
```

macOS/Linux:
```bash
cp .env.example .env
```

Review at least:
- `DATABASE_URL`
- `SECRET_KEY`
- `APP_ENV`
- `ALLOWED_HOSTS`
- `PORT`, `WEB_CONCURRENCY`, `WEB_TIMEOUT` (container/runtime behavior)
- `COOKIE_SECURE`, `FORCE_HTTPS` (prod-like local verification)

## 4) Initialize Database
```powershell
python -m alembic -c alembic.ini upgrade head
python scripts/seed_admin.py
```

## 5) Start the Application
```powershell
python -m uvicorn app.main:app --reload
```

Health check:
- `http://127.0.0.1:8000/healthz`

## 6) Run Baseline Tests
```powershell
pytest -q
```

Strict warning mode:
```powershell
pytest -q -W error
```

Notes:
- E2E browser tests are expected to skip when Playwright browsers are not installed.
- To enable browser E2E: `python -m playwright install chromium`.
- Operability diagnostics are documented in `docs/development/OPERABILITY.md`.

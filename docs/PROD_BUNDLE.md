# Production Bundle Guide

## Goal
Define which parts of the repository belong to runtime deployment and which parts stay for development/QA.

## Recommended Branch Plan (`prod-clean`)
1. Create branch:
   - `git checkout -b prod-clean`
2. Run backup first:
   - `py -m tools.backup_project`
   - `py -m tools.backup_project --yes`
3. Run cleanup checks:
   - `py -m tools.diagnostics.find_unused_files --output docs/CLEANUP_AUDIT.md`
4. Apply safe packaging changes (ignore rules, docs, optional archive moves).
5. Open PR from `prod-clean` into main.

## Deploy: Include
- `app/` (runtime code, templates, static)
- `alembic/` + `alembic.ini`
- `start.sh`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml` (optional for ops)
- `.env.example`
- `render.yaml` (if Render deployment)

## Deploy: Exclude
- `tests/`
- `docs/` (optional, not runtime required)
- `diagnostics/`
- `scripts/` (dev helpers)
- `tools/` except explicit runtime tools (default: exclude all)
- `outbox/`
- local DB files (`*.db`, `*.sqlite`, `*.sqlite3`)
- cache folders (`__pycache__/`, `.pytest_cache/`, etc.)

## Runtime/Dev Separation
- Runtime code remains in `app/`.
- Dev-only automation remains in `tools/` and `scripts/`.
- Cleanup candidates are documented in `docs/CLEANUP_AUDIT.md` before any archive/delete action.

## DB Reset + CSV Reimport Test Flow
1. Backup first (mandatory).
2. Reset DB safely:
   - `py -m tools.db_reset --drop-all --migrate --seed-admin --yes`
3. Start app and test admin CSV import via UI.

# Repo Reframe Execution - 2026-04-16

## Scope dieses Blocks
Umgesetzt wurden strukturelle Repo-Massnahmen gemaess Audit-Entscheidung Variante B:
- Root entschlacken
- Dokumentationsarchitektur konsolidieren
- Produktidentitaet konsistent auf `MealMate` setzen
- Public-Repo-Hygiene verbessern

Kein tiefes Business-Logic-Refactoring.

## Root-Entscheidungen
### KEEP IN ROOT
- `README.md`
- `CHANGELOG.md`
- `requirements.txt`
- `Dockerfile`
- `docker-compose.yml`
- `render.yaml`
- `alembic.ini`
- `start.sh`
- `pytest.ini`
- `pytest_strict.ini`
- `.env.example`
- `.gitignore`
- `.dockerignore`
- Kernordner: `app/`, `alembic/`, `tests/`, `scripts/`, `tools/`, `docs/`, `data/`

### MOVE TO DOCS / INTERNAL / DATA
- Root-Readme-Satelliten:
  - `README_DEPLOY.md` -> `docs/deployment/DEPLOYMENT.md`
  - `README_SECURITY.md` -> `docs/deployment/SECURITY.md`
  - `README_RUNBOOK.md` -> `docs/development/RUNBOOK.md`
  - `README_I18N.md` -> `docs/development/I18N.md`
  - `README_CSV_IMPORT.md` -> `docs/development/CSV_IMPORT.md`
  - `README_MODERATION.md` -> `docs/development/MODERATION.md`
  - `README_AUTH_RECOVERY.md` -> `docs/development/AUTH_RECOVERY.md`
  - `README_EMAIL_CHANGE.md` -> `docs/development/EMAIL_CHANGE.md`
- Deliverables:
  - `DELIVERABLE_*.md` -> `docs/internal/legacy/deliverables/`
- Legacy-Artefakt:
  - `projekt_3_meal_mate.pdf` -> `docs/internal/legacy/artifacts/`
- Seed-Daten:
  - `rezepte_kochwiki_clean_3713.csv` -> `data/seed/rezepte_kochwiki_clean_3713.csv`
- Dokumente in `docs/` neu geordnet:
  - `docs/architecture/`, `docs/development/`, `docs/deployment/`, `docs/internal/`
- Diagnostik-Reports:
  - `diagnostics/*` -> `docs/internal/reports/diagnostics/`

### REMOVE FROM TRACKING / EXCLUDE
- `diagnostics/` als lokaler Laufordner in `.gitignore` aufgenommen.
- Leere Strukturreste entfernt: `app/services/` (leer).

### REVIEW NEEDED
- Versionierte historische Diagnose-Reports unter `docs/internal/reports/diagnostics/`:
  - fachlich internisiert, aber weiterhin gross/operativ.
  - Entscheidung fuer spaeteren Block: behalten als Historie vs. in Git-History ausduennen.

## Produktidentitaet (konsolidiert)
Hauptname ist jetzt zentral `MealMate`.

Umgesetzt:
1. Default-Brand in Settings:
   - `app/config.py`: `app_name` auf `MealMate`.
2. Entferntes Zwangs-Rewrite auf Altnamen:
   - `parse_app_name` normalisiert nur noch leere Werte auf `MealMate`.
3. UI-Branding:
   - `app/templates/base.html`
   - `app/templates/impressum.html`
4. Translation-Diagnose-Text:
   - `app/routers/translations.py`
5. Branding-Tests angepasst:
   - `tests/test_branding_app_name.py`
   - `tests/test_translations_admin_diagnose.py`

## Pfadkonsolidierung fuer Seed-Daten
Umgestellt auf `data/seed`:
- `app/config.py`: `kochwiki_csv_path`
- `.env.example`: `KOCHWIKI_CSV_PATH`
- `scripts/import_csv_to_db.py`: CLI-Default fuer `--file`

## Dokumentationskonsolidierung
Neu:
- `docs/README.md` als zentraler Doku-Index
- `docs/internal/README.md` fuer interne Dokuabgrenzung

README neu aufgebaut als Single Source of Truth:
- Produktbeschreibung
- Kernfunktionen
- Tech-Stack
- lokaler Start
- Konfiguration
- Tests
- Deployment-Hinweise
- Repo-Struktur

## Bewusst nicht umgesetzt in diesem Block
1. Kein Split grosser Python-Module.
2. Kein tiefes Refactoring von Router-/Service-Logik.
3. Keine inhaltliche Bereinigung historischer Legacy-Dokumente unter `docs/internal/legacy/`.
4. Keine CI-Pipeline-Neuverdrahtung.

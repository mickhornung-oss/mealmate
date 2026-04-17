# Technical Baseline Hardening - 2026-04-16

## Ziel dieses Blocks
Herstellung eines reproduzierbaren, technisch belastbaren Basiszustands nach dem Repo-Reframe:
- reproduzierbarer Setup-/Run-/Test-Pfad
- minimale, stabile CI-Basis
- extern nutzbare Hauptdokumentation (Englisch)

## Umgesetzte technische Haertungen
1. **Reproduzierbarer Local-Setup-Pfad festgelegt**
   - Python 3.12 als Basis dokumentiert.
   - neuer kanonischer Setup in `docs/development/SETUP.md`.
   - `.env.example` und Import-Skript auf neuen Seed-Pfad ausgerichtet (`data/seed/...`).

2. **Startpfad verifiziert**
   - lokaler Start mit `python -m uvicorn app.main:app`.
   - Healthcheck `/healthz` erfolgreich (`{"status":"ok"}`).

3. **Testbasis gehaertet**
   - kompletter Basistestlauf erfolgreich: `129 passed, 4 skipped`.
   - Skip-Verhalten fuer Playwright-Browser bleibt explizit erwartbar und dokumentiert.

4. **CI-Basis eingefuehrt**
   - `.github/workflows/ci.yml` hinzugefuegt.
   - Pipeline: Python 3.12, `pip install -r requirements.txt`, `compileall`, `pytest -q`.

5. **Alembic-Konfiguration bereinigt**
   - `alembic.ini`: `path_separator = os` gesetzt.
   - vorheriger Alembic-Deprecation-Hinweis im Testlauf entfernt.

6. **Repo-Hygiene fuer lokale Testumgebungen verbessert**
   - `.gitignore`: `.venv*/` aufgenommen (neben `.venv/`).
   - verhindert erneute versehentliche Aufnahme lokaler Repro-venvs.
7. **Onboarding fuer externe Mitwirkende ergaenzt**
   - `CONTRIBUTING.md` mit minimalem Beitrags- und Qualitaetsablauf.

## Oeffentliche Doku-/Sprachentscheidungen
1. Oeffentliche Einstiegstexte sind auf Englisch konsolidiert:
   - `README.md`
   - `docs/README.md`
   - `docs/architecture/ARCHITECTURE.md`
   - `docs/development/SETUP.md`
   - `docs/development/TESTING.md`
   - `docs/deployment/DEPLOYMENT.md`
   - `docs/deployment/SECURITY.md`
2. Interne Audit-/Historien-Dokumente bleiben weiterhin deutsch/intern.
3. Sprachmischung in den oeffentlichen Kernpfaden wurde reduziert.

## Real gepruefte Runs (dieser Block)
1. **Fresh venv Repro (Python 3.12)**
   - `py -3.12 -m venv .venv_repro`
   - `pip install -r requirements.txt`
   - `python -m alembic -c alembic.ini upgrade head`
   - `python scripts/seed_admin.py`
2. **Voller Testlauf**
   - `pytest -q`
   - Ergebnis: `129 passed, 4 skipped, 2 warnings`
3. **Compile-Check**
   - `python -m compileall app tests scripts tools`
   - erfolgreich.
4. **Start-/Health-Check**
   - `python -m uvicorn app.main:app ...`
   - `GET /healthz` -> `{"status":"ok"}`.

## Gruener Status
1. Setup-Pfad ist reproduzierbar und dokumentiert.
2. Run-Pfad ist funktional geprueft.
3. Test-Basispfad ist gruen.
4. CI-Minimum ist vorhanden und passt zum real getesteten Basispfad.
5. Oeffentliche Hauptdoku ist fuer externe Leser nutzbar (englisch).

## Bewusst offen / nicht Teil dieses Blocks
1. Kein tiefes Zerlegen grosser Fachmodule.
2. Keine fachliche Redesign-Arbeit an Business-Logik.
3. Zwei verbleibende Python-3.12-SQLite-Deprecation-Warnings aus SQLAlchemy/stdlib-Kontext.
4. Interne Legacy-Dokumente wurden nicht inhaltlich bereinigt, nur sauber abgegrenzt.

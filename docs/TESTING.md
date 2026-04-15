# Testing Guide

Dieses Dokument beschreibt die wichtigsten Test-Kommandos fuer MealMate.

## Voraussetzungen

1. Virtuelle Umgebung aktivieren.
2. Abhaengigkeiten installieren: `pip install -r requirements.txt`.
3. Fuer Browser-E2E Playwright-Paket installieren: `python -m pip install playwright`.
4. Fuer Browser-E2E Chromium installieren: `python -m playwright install chromium`.

## Basis-Testlauf

Der komplette Testlauf:

```bash
pytest -q
```

## Warning-Management (Default)

Die Standard-Konfiguration in `pytest.ini` ist auf lesbare Tests ausgelegt:
- `DeprecationWarning` und `FutureWarning` aus bekannten Drittlibs werden gefiltert.
- Betroffene Module: `fastapi`, `starlette`, `slowapi`, `limits`, `pydantic`, `anyio`, `httpx`.
- Eigene Warnings bleiben sichtbar, weil nur diese Drittmodule gezielt gefiltert werden.
- `UserWarning` und `RuntimeWarning` werden nicht global unterdrueckt.

## Strict-Warnings Modus (optional fuer CI)

Wenn du zusaetzlich alle nicht gefilterten Deprecations/FutureWarnings als Fehler behandeln willst:

```bash
pytest -q -c pytest_strict.ini
```

Alternative ohne extra Config:

```bash
pytest -q -W error::DeprecationWarning -W error::FutureWarning
```

Hinweis:
- `pytest_strict.ini` behaelt die Drittlib-Filter bei, macht aber alle anderen Deprecations/FutureWarnings hart (`error`).

## Aggressivtests (Integration)

Nur User-Ende-zu-Ende auf HTTP-Ebene:

```bash
pytest -q tests/test_beta_aggressive_user_flow.py
```

Nur Admin-Ende-zu-Ende auf HTTP-Ebene:

```bash
pytest -q tests/test_beta_aggressive_admin_flow.py
```

## E2E Smoke (Playwright)

Kurzer Browser-Smoke fuer User/Admin:

```bash
pytest -q tests/e2e/test_beta_smoke.py
```

## Warum E2E als "skipped" erscheinen kann

E2E-Tests werden absichtlich als `skipped` markiert, wenn:
- das Python-Paket `playwright` nicht installiert ist.
- der Browser-Binary (Chromium) nicht installiert ist.

Das ist in lokalen Umgebungen ohne Browser-Setup normal und kein Produktivfehler.

## Playwright Setup und E2E ausfuehren

1. Paket installieren:

```bash
python -m pip install playwright
```

2. Browser installieren:

```bash
python -m playwright install chromium
```

3. E2E Smoke starten:

```bash
pytest -q tests/e2e/test_beta_smoke.py
```

Hinweise:
- Die E2E-Fixtures starten einen eigenen Uvicorn-Testserver auf freiem Port.
- Integrationstests ohne Browser laufen weiterhin normal, auch wenn E2E geskippt wird.

## Passwort-Reset / E-Mail-Versand testen

DEV-Modus (Outbox statt SMTP):
- Stelle sicher, dass `MAIL_OUTBOX_PATH` gesetzt ist (z. B. `outbox/reset_links.txt`).
- Nach `POST /auth/forgot-password` steht der Reset-Link in dieser Datei.
- Fuer E-Mail-Aenderung wird `MAIL_OUTBOX_EMAIL_CHANGE_PATH` verwendet.

PROD-Modus (SMTP):
- Setze `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`.
- Tokens gehoeren nur in die Mail, nicht in Logs oder Frontend.

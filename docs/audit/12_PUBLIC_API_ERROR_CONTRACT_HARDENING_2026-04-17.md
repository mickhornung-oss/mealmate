# Block 12 - Public/API-Contract-Hardening und Fehlervertrag-Standardisierung

Datum: 2026-04-17  
Status: Abgeschlossen (gruen)

## Ziel des Blocks
In einem zusammenhaengenden Schritt mehrere oeffentliche und API-nahe Endpunktbereiche vertraglich haerten:

1. Response-Entscheidungen (Redirect vs. HTMX-Render vs. API) expliziter machen  
2. Fehlervertraege in kritischen Formular-/Admin-Pfaden konsistenter machen  
3. Fehlerpfade regressionsfest absichern

## Umgesetzte Strukturentscheidungen

### 1) Image-Write-Endpunkte mit explizitem Response-Vertrag (`app/routers/recipes.py`)
- Neue zentrale Router-Helfer eingefuehrt:
  - `_is_hx_request(...)`
  - `_normalize_image_response_mode(...)`
  - `_render_recipe_image_feedback_response(...)`
- Wirkung:
  - Einheitlicher Entscheidungsweg fuer `card`/`detail`-Render bei HTMX.
  - Einheitliche Redirect-Entscheidung ausserhalb HTMX.
  - Fehlerpfade bei HTMX-Upload/-Change-Request liefern jetzt gezielt denselben Partial-Rendervertrag statt impliziter JSON-Exception.
- Betroffene Endpunkte:
  - `POST /recipes/{recipe_id}/images`
  - `POST /recipes/{recipe_id}/image-change-request`
  - `POST /images/{image_id}/delete`
  - `POST /images/{image_id}/set-primary`

### 2) Submit-Formular Fehlervertrag konsolidiert (`app/routers/submissions.py`)
- Neuer zentraler Formular-Fehler-Renderer:
  - `render_submit_recipe_error(...)`
- Wirkung:
  - Einheitlicher Template-Fehlervertrag fuer:
    - Pflichtfeldvalidierung
    - numerische Feldvalidierung
    - Bildvalidierungsfehler
  - Keine verstreute duplizierte Fehler-TemplateResponse-Logik mehr im Router.
- Betroffener Endpunkt:
  - `POST /submit`

### 3) Translation-Admin Runtime-Fehlerklassifikation vereinheitlicht (`app/routers/translations.py`)
- Neue helperbasierte Fehlerklassifikation:
  - `_render_translation_runtime_error(...)`
- Wirkung:
  - Einheitliche Runtime-/DB-Fehlerbehandlung fuer schwere Ausfuehrungspfade.
  - `OperationalError` bleibt klar als `503` klassifiziert.
  - generische Laufzeitfehler bleiben pro Use-Case kontrollierbar (`500` bzw. bestehend `502` beim Batch-Start).
- Betroffene Endpunkte:
  - `POST /admin/translations/run`
  - `POST /admin/translations/batch/start`

## Neue Vertrags-/Fehlerpfad-/Regressionstests

Datei: `tests/test_api_error_contracts.py`

- `test_submit_recipe_invalid_image_renders_html_error_contract`
  - Validiert HTML-Fehlervertrag fuer `POST /submit` bei Upload-Validierungsfehler.
- `test_recipe_image_upload_hx_invalid_file_renders_partial_error`
  - Validiert HTMX-Partial-Fehlerantwort fuer Upload.
- `test_recipe_image_upload_hx_card_response_contract`
  - Validiert `card`-Rendervertrag bei HTMX-Erfolg.
- `test_recipe_image_upload_non_hx_success_redirect_contract`
  - Validiert Redirect-Vertrag ausserhalb HTMX.
- `test_translation_run_operational_error_uses_503_contract`
  - Validiert DB-Lock-Fehlerklassifikation als `503`.
- `test_translation_batch_start_runtime_error_uses_502_contract`
  - Validiert bestehende Batch-Start-Runtime-Semantik (`502`) nach Konsolidierung.
- `test_recipe_change_request_hx_invalid_file_renders_partial_error`
  - Validiert HTMX-Partial-Fehlervertrag fuer Change-Request-Upload.

## Reale Verifikation

Ausgefuehrt:

1. `python -m compileall app tests`  
2. gezielte Regression:
   - `pytest -q tests/test_api_error_contracts.py tests/test_router_write_path_contracts.py tests/test_router_read_query_contracts.py tests/test_router_render_context_contracts.py`
   - Ergebnis: `21 passed`
3. Vollsuite:
   - `pytest -q` -> `159 passed, 4 skipped`
4. Warning-strict:
   - `pytest -q -W error` -> `159 passed, 4 skipped`
5. Health:
   - `/healthz` -> `200 {"status":"ok"}`

Hinweis:
- Die 4 Skips sind weiterhin erwartete Playwright-Skips (lokal fehlende Browser-Binaries).

## Verhaltensgleichheit und Oberflaechenstabilitaet

- Keine neuen Endpunkte.
- Keine neuen Payload- oder Query-Parameter.
- Keine Aenderung an Erfolgspfaden der priorisierten Endpunkte.
- Fehlerpfade wurden strukturell vereinheitlicht und testseitig abgesichert, ohne Feature-Erweiterung.

## Bewusst offen gelassen

- Keine globale Vereinheitlichung aller verbliebenen historischen Fehlerdetails (z. B. sprachlich gemischte Detailtexte in Altpfaden).
- Keine Public-API-Versionierung und kein formales Problem-JSON-Schema in diesem Block.
- Keine Erweiterung der E2E-Abdeckung auf Playwright in dieser Umgebung.

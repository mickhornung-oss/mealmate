# Block 11 - Template-Context-Contract-Hardening, Admin-Diagnose-Entkopplung, Render-Path-Konsolidierung

Datum: 2026-04-17  
Status: Abgeschlossen (gruen)

## Ziel des Blocks
Mehrere schwere Admin-/Diagnose-Renderpfade in einem zusammenhaengenden Schritt verhaltensgleich haerten:

1. Template-Context-Vertraege expliziter machen  
2. Diagnose-/Read-Aufbereitung aus Router-Glue entkoppeln  
3. Render-Path-Verwendung konsolidieren

## Gehaertete Bereiche

### 1) Admin-Dashboard Render-Vertrag (`app/routers/admin.py`)
- Render-Pfad konsolidiert:
  - `render_admin_dashboard(...)` als einheitlicher Entry fuer `admin.html`.
- Dashboard-Context-Aufbau entkoppelt und lesbarer:
  - `load_pending_image_change_requests(...)` fuer Queue-Snapshot + Count.
  - bestehender `admin_dashboard_context(...)` nutzt jetzt explizite Snapshot-Helfer.
- Folge: weniger duplizierte TemplateResponse-/Context-Bausteine in:
  - `GET /admin`
  - `POST /admin/run-kochwiki-seed`
  - `POST /admin/import-recipes`

### 2) Admin Image-Change Read-/Render-Vertrag (`app/routers/admin.py`)
- Query-/Paging-/Statusvertraege explizit gemacht:
  - `normalize_image_change_status_filter(...)`
  - `resolve_paged_request(...)`
  - `build_image_change_status_stats(...)`
- Detail-Render-Kontext entkoppelt:
  - `build_image_change_detail_context(...)`
- Betroffene Read-Routen:
  - `GET /admin/image-change-requests`
  - `GET /admin/image-change-requests/{request_id}`

### 3) Admin Translations Diagnose-/Render-Konsolidierung (`app/routers/translations.py`)
- Snapshot-Lesen getrennt von Kontextaufbau:
  - `_load_translations_admin_snapshot(...)`
- Zentraler Render-Pfad eingefuehrt:
  - `_render_translations_page(...)`
- Bestehende Kontextlogik stabilisiert:
  - `_build_translations_context(...)` verwendet Snapshot statt inline-Mischung.
- Read-/Diagnose-/Fehler-Routen auf konsistenten Renderpfad gezogen:
  - `GET /admin/translations`
  - `GET /admin/translations/audit-de`
  - `POST /admin/translations/repair-de`
  - `POST /admin/translations/run`
  - `POST /admin/translations/batch/start`
  - `POST /admin/translations/queue/run`
  - `POST /admin/translations/test`

## Neue Vertrags-/Regressionstests

Datei: `tests/test_router_render_context_contracts.py`

- `test_admin_dashboard_render_contract_exposes_diagnostic_sections`
  - Dashboard enthält erwartete Diagnose-/Admin-Sektionen.
- `test_admin_image_change_queue_invalid_filter_defaults_to_pending`
  - Ungueltiger Statusfilter faellt stabil auf `pending` zurueck.
- `test_admin_image_change_queue_page_contract_clamps_to_last_page`
  - Paging-Vertrag der Queue clamp't auf letzte Seite.
- `test_admin_translations_batch_started_message_without_job_id`
  - Read-Query-Vertrag fuer Batch-Start-Message ohne Job-ID bleibt stabil.
- `test_admin_translations_default_read_does_not_render_last_run_block`
  - Default-Read ohne Run-Daten rendert den Last-Run-Block nicht.

## Reale Verifikation

Ausgefuehrt:

1. `python -m compileall app tests`  
2. gezielte Regression:
   - `pytest -q tests/test_router_render_context_contracts.py tests/test_router_read_query_contracts.py tests/test_translation_queue.py tests/test_translations_admin_diagnose.py`
   - Ergebnis: `14 passed`
3. Vollsuite:
   - `pytest -q` -> `152 passed, 4 skipped`
4. Warning-strict:
   - `pytest -q -W error` -> `152 passed, 4 skipped`
5. Health:
   - `/healthz` -> `200 {"status":"ok"}`

Hinweis:
- Die 4 Skips sind weiterhin die erwarteten Playwright-E2E-Skips wegen lokal fehlender Browser-Binaries.

## Verhaltensgleichheit

- Keine neuen Endpunkte.
- Keine neuen Query-Parameter.
- Keine absichtliche Aenderung von Template-/Response-Semantik.
- Schwerpunkt war nur Entkopplung, Kontextklarheit und Renderpfad-Konsistenz.

## Bewusst offen gelassen

- Keine Umstrukturierung der HTML-Templates selbst (nur Router-/Kontextkanten gehaertet).
- Keine inhaltliche Erweiterung von Admin-/Diagnosedaten.
- Keine E2E-Browser-Provisionierung in diesem Block.

# Block 10 - Read-Path- und Query-Contract-Hardening (Router-Use-Cases)

Datum: 2026-04-17  
Status: Abgeschlossen (gruen)

## Ziel des Blocks
Read-Pfade in Routern auf explizite Query-/Filter-/Paging-/Render-Vertraege schneiden, ohne aussen sichtbare Verhaltensaenderung.

## Gehaertete Bereiche

### 1) Discover/Home Read-Use-Case (`app/routers/recipes.py`)
- Query-Vertrag explizit gemacht:
  - `DiscoverQueryContract`
  - `normalize_discover_query_contract(...)`
- Query-/Filter-/Sort-Logik vom Handler getrennt:
  - `build_discover_recipe_stmt(...)`
- Featured-Read-Pfad als separater Query-Vertrag:
  - `build_featured_recipe_stmt(...)`
- Paging-Vertrag explizit:
  - `resolve_pagination_contract(...)`
- Render-Kartenaufbau entkoppelt:
  - `build_recipe_cards(...)`
  - `build_featured_recipe_cards(...)`

Wirkung:
- `home_page` ist jetzt Router-Orchestrierung statt gemischte Query+Render-Sammelstelle.
- Filter-/Paging-Defaults sind zentralisiert und testbar.

### 2) Submission Read-Use-Cases (`app/routers/submissions.py`)
- Statusfilter-Vertrag zentralisiert:
  - `normalize_submission_status_filter(...)`
- Paging-Vertrag zentralisiert:
  - `resolve_paged_request(...)`
  - `load_submission_list_page(...)`
- Betroffene Read-Routen:
  - `GET /my-submissions`
  - `GET /admin/submissions`

Wirkung:
- Query-Parameter-Verarbeitung und Listenabfrage sind klar getrennt.
- Page-Clamping und Filter-Default sind explizit und wiederverwendbar.

### 3) Admin Translation Read-Query-Vertrag (`app/routers/translations.py`)
- Report-Aufbereitung aus Query-Parametern extrahiert:
  - `_build_translation_run_report(...)`
- Batch-Start-Message-Vertrag extrahiert:
  - `_build_batch_started_message(...)`
- Betroffene Route:
  - `GET /admin/translations`

Wirkung:
- Read-Query -> Report/Message -> Render-Kontext ist explizit, ohne Template-Vertrag zu aendern.

## Neue Regression-/Vertragstests

Datei: `tests/test_router_read_query_contracts.py`

- Home-Query-Vertrag:
  - `test_home_query_contract_normalizes_per_page_and_image_filter`
  - `test_home_query_contract_clamps_page_to_last_page`
- Submission-Read-Vertrag:
  - `test_admin_submissions_invalid_status_filter_defaults_to_pending`
  - `test_admin_submissions_page_contract_clamps_to_last_page`
- Translation-Read-Vertrag:
  - `test_admin_translations_read_query_contract_builds_report_and_batch_message`

## Reale Verifikation

1. `python -m compileall app tests`  
2. `pytest -q`  
   - Ergebnis: `147 passed, 4 skipped`
3. `pytest -q -W error`  
   - Ergebnis: `147 passed, 4 skipped`
4. `/healthz` via TestClient  
   - Ergebnis: `200 {"status":"ok"}`

Hinweis:
- Die 4 Skips sind weiterhin erwartete Playwright-E2E-Skips wegen lokal fehlender Browser-Binaries.

## Verhaltensgleichheit
- Keine neuen Endpunkte.
- Keine neuen Query-Parameter.
- Keine extern sichtbaren API-/Template- oder Redirect-Vertragsaenderungen.
- Fokus war rein strukturelle Entkopplung und testbare Vertragsklarheit in Read-Pfaden.

## Bewusst offen gelassen
- Kein Refactoring der Admin-Template-Dateien selbst (nur Router-Vertragsschicht gehaertet).
- Keine E2E-Browser-Provisionierung als Teil dieses Blocks.
- Keine fachliche Umstellung von Diagnoseinhalten oder Admin-Read-Informationen.

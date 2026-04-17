# Block 09 - Write-Path-Contract-Hardening (Router-Use-Cases)

Datum: 2026-04-17  
Status: Abgeschlossen (gruen)

## Ziel des Blocks
Router-nahe Write-Pfade in Admin-, Submission- und Translation-Flows vertraglich haerten, ohne API- oder Verhaltensaenderung.

## Umgesetzte Strukturhaertungen

### 1) Submission-Router: explizite Write-Use-Case-Bausteine
Datei: `app/routers/submissions.py`

- Write-Guard fuer erlaubte Statusuebergaenge zentralisiert:
  - `ensure_submission_editable(...)`
- Edit-Pfad in klarere Phasen getrennt:
  - `parse_submission_edit_payload(...)` (Validation/Normalize)
  - `apply_submission_edit_payload(...)` (Mutation)
  - `attach_submission_image_if_present(...)` (optionaler Seiteneffekt)
- Review-Write-Phase (approve/reject) vereinheitlicht:
  - `mark_submission_reviewed(...)`
- Image-Write-Entry (set-primary/delete) auf konsistente Lookup-Grenze gebracht:
  - `fetch_submission_image_or_404(...)`

Bewusster Vertrag:
- Router orchestriert.
- Status-/Write-Mutation ist explizit separiert.
- Folgeaktion `publish_submission_as_recipe(...)` bleibt einmaliger Trigger im Approve-Use-Case.

### 2) Translation-Router: fatal-error/commit/redirect-Vertrag vereinheitlicht
Datei: `app/routers/translations.py`

- Duplizierte Run-Report-Kontrolle vereinheitlicht:
  - `_is_translation_report_fatal(...)`
  - `_render_translation_report_error(...)`
  - `_redirect_translation_report(...)`
- Betroffene Write-Routen:
  - `POST /admin/translations/run`
  - `POST /admin/translations/queue/run`
  - `POST /admin/translations/recipes/{recipe_id}/run`

Bewusster Vertrag:
- Fataler Report ohne Write-Erfolg => rollback + 400-Response.
- Erfolgs-/Teilerfolgs-Report => commit-Pfad + stabiles Redirect-Shape.
- Keine Aenderung der externen Route-Form oder Query-Parameter.

## Neue/erweiterte Absicherungstests
Datei: `tests/test_router_write_path_contracts.py`

- `test_submission_approve_triggers_publish_once_and_blocks_second_transition`
  - Approve triggert Publish genau einmal.
  - Nach erfolgreichem Approve wird ein zweiter Statuswechsel (Reject) als 409 blockiert.
- `test_submission_reject_requires_reason_and_keeps_status_on_validation_error`
  - Reject ohne Grund bleibt 400.
  - Status/Admin-Note bleiben unveraendert.
- `test_translation_single_recipe_run_uses_stable_contract_and_redirect_shape`
  - Single-Recipe-Run nutzt stabilen Runner-Vertrag und erwartetes Redirect-Shape.
- `test_translation_queue_run_fatal_report_returns_400_without_commit_redirect`
  - Fataler Queue-Run-Report fuehrt zu 400 statt Redirect-Commit-Pfad.

## Reale Verifikation

Ausgefuehrte Checks:

1. `python -m compileall app tests`  
2. `pytest -q`  
   - Ergebnis: `142 passed, 4 skipped`  
3. `pytest -q -W error`  
   - Ergebnis: `142 passed, 4 skipped`  
4. `/healthz` via TestClient  
   - Ergebnis: `200 {"status":"ok"}`

Hinweis zu Skips:
- Die 4 Skips sind weiterhin Playwright-E2E-Skips wegen lokal fehlender Browser-Binaries; keine Regression in diesem Block.

## Verhaltensgleichheit / API-Stabilitaet

- Keine neuen Endpunkte.
- Keine geaenderten Request-/Response-Vertraege an den gehaerteten Routen.
- Keine absichtliche Seiteneffekt-Semantik-Aenderung.
- Fokus rein auf explizitere Use-Case-Vertragsgrenzen und Fehlerpfad-Klarheit.

## Bewusst offen gelassen (naechster Block)

- Kein tiefes Entkoppeln von Router/Template-Kontext in `admin_translations` (Read-/Render-Seite).
- Kein Refactoring der verbleibenden grossen Read-Diagnosepfade.
- Kein E2E-Browser-Provisioning (`playwright install`) als Teil dieses Blocks.

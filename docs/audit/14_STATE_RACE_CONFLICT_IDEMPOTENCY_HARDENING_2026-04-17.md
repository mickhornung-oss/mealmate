# Block 14 - State-/Race-/Conflict-/Idempotenz-Hardening

Datum: 2026-04-17  
Status: Abgeschlossen (gruen)

## Ziel des Blocks
Mehrere zusammenhaengende Mutations-Hotspots in einem grossen Block auf Konflikt-, Replay- und Zustandssicherheit haerten:

1. explizitere Precondition-/State-Guards  
2. konsistentere Conflict-Semantik (insb. 409)  
3. robustere Wiederholungs-/Replay-Regeln  
4. sichtbare Reduktion von doppelten Seiteneffekten bei konkurrierenden Aktionen

## Gehaertete Bereiche

### 1) Translation-Batch-Start: aktiver Job als expliziter Konflikt
Dateien:
- `app/translation_service.py`
- `app/translation_batch_service.py`
- `app/routers/translations.py`

Umsetzung:
- neue Konfliktklasse: `TranslationBatchConflictError`
- neuer Guard: `_find_active_translation_batch_job(...)` in `translation_batch_service`
- `start_translation_batch_job(...)` blockiert Start, wenn bereits ein nicht-terminaler Job existiert (`queued/running/...`)
- Router mapping:
  - `POST /admin/translations/batch/start`
  - `TranslationBatchConflictError` -> konsistente `409`-Antwort mit Render-Vertrag

Nutzen:
- verhindert doppelte Batch-Starts als implizite Replay-Aktion
- macht "already running"-Zustand explizit und testbar

### 2) Image-Change-Moderation: atomarer Pending-Claim vor Mutation
Datei:
- `app/routers/admin.py`

Umsetzung:
- neuer Guard:
  - `claim_image_change_transition_or_conflict(...)`
  - atomare Transition nur bei `status == pending` via SQL-`UPDATE ... WHERE ...`
- `approve` und `reject` nutzen denselben Claim-Mechanismus
- bei fehlendem Claim (bereits verarbeitet / stale) konsistent `409 image_change_request_not_pending`

Nutzen:
- reduziert Race-Fenster bei parallelem Approve/Reject
- verhindert doppelte Seiteneffekte (z. B. mehrfaches Erzeugen von Rezeptbildern)

### 3) Submission-Moderation: explizite Replay-/Conflict-Vertraege
Datei:
- `app/routers/submissions.py`

Umsetzung:
- neue Guards:
  - `claim_submission_approval_or_conflict(...)`
  - `claim_submission_reject_if_pending(...)`
- Approve:
  - atomarer Claim vor Publish
  - `publish_submission_as_recipe(...)`-Race (`ValueError`) wird auf `409 submission_already_published` gemappt (statt unklarem Laufzeitfehler)
- Reject:
  - wiederholter Reject wird als idempotenter Redirect behandelt (no-op, kein zweiter State-Write)
  - stale/non-pending beim Claim fuehrt ebenfalls in denselben idempotenten Redirect-Vertrag
- tote Altfunktion `mark_submission_reviewed(...)` entfernt

Nutzen:
- klarere "already handled"-Regeln
- weniger doppelte/redundante Mutationen bei Replay/Doppelklick

## Neue Konflikt-/Replay-/Regressionstests

Datei:
- `tests/test_state_conflict_contracts.py`

Abgedeckt:
- `test_translation_batch_start_conflicts_when_active_job_exists`
  - aktiver Job -> `409` auf Batch-Start
- `test_image_change_approve_second_call_conflicts_without_duplicate_side_effect`
  - zweites Approve -> `409`; keine doppelte Bild-Seitenwirkung
- `test_submission_reject_replay_is_idempotent_redirect`
  - zweites Reject -> idempotenter Redirect, kein zweiter inhaltlicher Statuswrite
- `test_submission_approve_value_error_is_mapped_to_conflict`
  - Publish-Race/ValueError -> `409`, kein inkonsistenter Persistenzzustand

## Reale Verifikation

Ausgefuehrt:

1. `python -m compileall app tests`  
2. gezielte Regression:
   - `pytest -q tests/test_state_conflict_contracts.py tests/test_translation_batch_jobs.py tests/test_translation_batch_mutation_boundaries.py tests/test_router_write_path_contracts.py tests/test_auth_permission_contracts.py`
   - Ergebnis: `16 passed`
3. Vollsuite:
   - `pytest -q` -> `167 passed, 4 skipped`
4. Warning-strict:
   - `pytest -q -W error` -> `167 passed, 4 skipped`
5. Health:
   - `/healthz` -> `200 {"status":"ok"}`

Hinweis:
- Die 4 Skips sind weiterhin erwartete Playwright-Skips (lokal fehlende Browser-Binaries).

## Verhaltensgleichheit / bewusste Konsolidierungen

- Keine neuen Features, APIs oder Datenmodelle.
- Erfolgspfade der priorisierten Mutationen bleiben stabil.
- Bewusste Vereinheitlichung:
  - aktiver Translation-Batch-Start ist jetzt explizit `409` statt uneinheitlicher Folgeeffekte
  - Race-nahe Approve-/Reject-Kanten nutzen atomare Pending-Claims
  - Reject-Replay ist explizit idempotent (no-op Redirect)

## Bewusst offen gelassen

- Keine globale 412-Einfuehrung (If-Match/Version-Preconditions) ohne API-weit einheitlichen Header-/Payload-Vertrag.
- Keine Datenbankweiten Sperr-/Locking-Strategien oder Queue-Neuarchitektur.
- Keine erweiterten Multi-Worker-Lasttests in diesem Block.

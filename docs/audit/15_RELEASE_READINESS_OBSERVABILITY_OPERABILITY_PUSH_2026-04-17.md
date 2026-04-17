# Block 15 - Release-Readiness Push (Observability/Operability/Config/Docs)

Datum: 2026-04-17  
Status: Abgeschlossen (gruen)

## Ziel des Blocks
Den Sprung von "technisch stark gehaertet" zu "realistisch veroeffentlichungsreif" in einem grossen, zusammenhaengenden Endspurt umsetzen:

1. Operability-/Observability-Hardening in kritischen Mutations-/Konfliktpfaden  
2. Config-/Env-/Deploy-Kanten auf release-nahe Klarheit ziehen  
3. Public-Docs und Repo-Einstieg auf aktuellen Realstand konsolidieren  
4. zusaetzliche Release-/Operability-Absicherungen per Tests

## Umgesetzte Bereiche

### 1) Operability-/Conflict-Logging in kritischen Mutationspfaden

#### Translation Batch Start
Dateien:
- `app/routers/translations.py`
- `app/translation_batch_service.py`

Verbesserungen:
- strukturierte Events fuer Start/Block/Conflict:
  - `translation_batch_started`
  - `translation_batch_start_conflict`
  - `translation_batch_start_blocked`
  - `translation_batch_job_created`
- `request_id`, `admin_id`, `mode`, `limit`, `external_job_id` werden in den Hotspots mitgeloggt.

Wirkung:
- Konflikte (`409`) und Batch-Start-Probleme sind im Betrieb deutlich schneller korrelierbar.

#### Submission Moderation
Datei:
- `app/routers/submissions.py`

Verbesserungen:
- strukturierte State-/Replay-Events:
  - `submission_approve_claimed`
  - `submission_approve_publish_conflict`
  - `submission_approve_completed`
  - `submission_reject_claimed`
  - `submission_reject_noop`
  - `submission_reject_replay`
  - `submission_reject_completed`
- Korrelation ueber `request_id`.

Wirkung:
- Doppelklick-/Replay-/Conflict-Verhalten ist operativ nachvollziehbar statt implizit.

#### Image-Change Moderation
Datei:
- `app/routers/admin.py`

Verbesserungen:
- strukturierte Transition-Events:
  - `image_change_transition_claimed`
  - `image_change_transition_conflict`
  - `image_change_approve_completed`
  - `image_change_reject_completed`
- `request_trace_id`, `request_id`, `target_status`, `admin_id` in Konflikt-/Transition-Logs.

Wirkung:
- Race-/Stale-State-Konflikte in der Moderation sind unmittelbar diagnostizierbar.

### 2) Config-/Env-/Runtime-Kanten release-nah konsolidiert

#### `.env.example` neu strukturiert
Datei:
- `.env.example`

Verbesserungen:
- klare Sektionen (core runtime, database, security, translation, seed/import)
- runtime-nahe Container-Variablen explizit:
  - `PORT`
  - `WEB_CONCURRENCY`
  - `WEB_TIMEOUT`
  - `APP_MODULE`
- Pflicht-/Sicherheitskanten sichtbar (`SECRET_KEY`, `COOKIE_SECURE`, `FORCE_HTTPS`, `ALLOWED_HOSTS`)

Wirkung:
- fremde Entwickler/Reviewer sehen sofort den realen Runtime-/Deploy-Vertrag.

### 3) Docs-/Public-Readiness konsolidiert

Aktualisierte Dateien:
- `README.md`
- `docs/README.md`
- `docs/development/SETUP.md`
- `docs/development/TESTING.md`
- `docs/development/RUNBOOK.md`
- `docs/deployment/DEPLOYMENT.md`
- `CONTRIBUTING.md`

Neu:
- `docs/development/OPERABILITY.md`

Verbesserungen:
- konsistente Baseline fuer `pytest -q -W error`
- expliziter Verweis auf Operability-/Konfliktdiagnose
- deployment-nahe Diagnosehinweise (`X-Request-ID`, relevante Logger)
- release-minimale Verifikationsschritte nach Deployment

Wirkung:
- Repo-Auftritt ist sichtbarer release-/ops-orientiert, nicht nur entwicklungsintern.

## Neue Tests / Absicherungen

### Erweiterte State-/Operability-Contracts
Datei:
- `tests/test_state_conflict_contracts.py`

Ergaenzt:
- Logging-Absicherung per Monkeypatch fuer Konflikt-/Replay-Events:
  - `translation_batch_start_conflict`
  - `submission_reject_replay`

### Release-Readiness-Contracts
Neu:
- `tests/test_release_readiness_contracts.py`

Abgedeckt:
- `.env.example` enthaelt zentrale runtime-/security-/translation-Schluessel
- Operability-Doku enthaelt die kritischen Konflikt-/Korrelationseintraege

## Reale Verifikation

Ausgefuehrt:

1. `python -m compileall app tests`  
2. gezielte Regression:
   - `pytest -q tests/test_state_conflict_contracts.py tests/test_translation_batch_jobs.py tests/test_translation_batch_mutation_boundaries.py tests/test_release_readiness_contracts.py`
   - Ergebnis: `10 passed`
3. Vollsuite:
   - `pytest -q` -> `169 passed, 4 skipped`
4. Warning-strict:
   - `pytest -q -W error` -> `169 passed, 4 skipped`
5. Health:
   - `/healthz` -> `200 {"status":"ok"}`

Hinweis:
- Die 4 Skips bleiben erwartete Playwright-Skips (lokal fehlende Browser-Binaries).

## Verhaltensgleichheit

- Keine neuen Features.
- Keine API-/Payload-/Query-Erweiterungen.
- Keine absichtliche Aenderung zentraler Erfolgspfade.
- Schwerpunkt lag auf operativer Nachvollziehbarkeit, Release-Dokumentation und Runtime-Klarheit.

## Bewusst offen gelassen

- Keine vollstaendige Release-Automation (Tagging, changelog automation, artifact signing).
- Keine zentralisierte externe Logaggregation/metrics pipeline (nur Code-/Repo-seitige Operability-Haertung).
- Keine Plattform-spezifische Produktionsorchestrierung ausser vorhandener Baselines (Docker/Render).

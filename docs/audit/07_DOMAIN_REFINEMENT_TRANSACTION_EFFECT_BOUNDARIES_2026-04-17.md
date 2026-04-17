# 07_DOMAIN_REFINEMENT_TRANSACTION_EFFECT_BOUNDARIES_2026-04-17

## Scope dieses Blocks
Ziel war verhaltensgleiches Domain-Refinement auf Transaktions-, Mutations- und Seiteneffekt-Grenzen.
Fokus: kritische Write-Pfade expliziter machen, Orchestrierung von Mutationen trennen, Regressionen gezielt absichern.

## Umgesetzte Refinements

### 1) Translation-Batch: Poll-Orchestrierung von Write-Mutationen getrennt
Neue Datei: `app/translation_batch_mutations.py`

Neu gekapselte Write-/Mutation-Verantwortungen:
- `apply_job_poll_snapshot(...)` (Job-Progress/Status-Update als expliziter Mutation-Schritt)
- `apply_translateapi_job_results(...)` (Upsert von `RecipeTranslation` aus Batch-Resultaten)
- `finalize_completed_job(...)` (Completion-Finalisierung inkl. Counters/Fehleraggregation)
- `finalize_terminal_job(...)` (failed/cancelled-Finalisierung)
- `finalize_timeout_job(...)` (Timeout-Finalisierung)

`app/translation_batch_service.py` ist jetzt klarer orchestration-first:
- Polling + API-Fetch + Kontrollfluss bleiben dort
- konkrete DB-Mutationen laufen ueber `translation_batch_mutations`
- bestehende Entry-Points bleiben stabil

Ergebnis:
- Seiteneffekt-Orte sind expliziter und zentralisiert
- Poll-Control-Flow und Write-Logik sind sauberer trennbar/testbar

### 2) Submission-Publish: Datenaufbereitung von persistierenden Transfers getrennt
Datei: `app/services_submission.py`

Neu eingefuehrte Trennungen:
- `_build_submission_recipe_values(...)` (reine Aufbereitung der Recipe-Write-Daten)
- `_copy_submission_ingredients_to_recipe(...)` (persistierender Ingredient-Transfer)
- `_copy_submission_images_to_recipe(...)` (persistierender Image-Transfer)
- `publish_submission_as_recipe(...)` bleibt orchestrierender Entry-Point

Ergebnis:
- Build-/Compute-Teil und Write-/Transfer-Teil sind explizit getrennt
- Mutationspfad fuer Submission->Recipe ist kontrollierter und lesbarer

## Verhaltensgleichheit / Kompatibilitaet
- Bestehende Service-Entry-Points wurden nicht gebrochen.
- Keine neue Feature-Logik eingefuehrt.
- Keine absichtliche Aenderung von Produktfluss/Benutzerverhalten.
- Regressionen wurden nach den Schnitten voll auf Gruen zurueckgefahren.

## Neue/erweiterte Vertrags- und Grenztests

### Neu: `tests/test_translation_batch_mutation_boundaries.py`
- `test_poll_job_uses_poll_snapshot_and_timeout_finalizer`
  - sichert, dass Poll-Orchestrierung den Snapshot-Mutationsschritt und Timeout-Finalizer nutzt
- `test_poll_job_uses_completed_finalizer`
  - sichert, dass Completion ueber den dedizierten Completion-Finalizer laeuft

### Neu: `tests/test_submission_mutation_boundaries.py`
- `test_publish_submission_orchestrates_build_and_copy_steps`
  - sichert expliziten Orchestrierungsvertrag im Submission-Publish-Write-Pfad

### Bereits bestehende Grenztests bleiben wirksam
- `tests/test_service_architecture_boundaries.py`

## Doku-Nachzug
`docs/architecture/ARCHITECTURE.md` aktualisiert:
- `app/translation_batch_mutations.py` als dedizierter Write-/Mutation-Bereich dokumentiert

## Real geprueft
1. Compile:
- `python -m compileall app tests`

2. Fokussierte Regression (kritische Bereiche):
- `pytest -q tests/test_translation_batch_jobs.py tests/test_translation_batch_mutation_boundaries.py tests/test_submission_mutation_boundaries.py tests/test_service_architecture_boundaries.py`
- Ergebnis: `8 passed`

3. Vollsuite:
- `pytest -q`
- Ergebnis: `135 passed, 4 skipped`

4. Warning-strict:
- `pytest -q -W error`
- Ergebnis: `135 passed, 4 skipped`

5. Health:
- `/healthz` -> `200 {"status":"ok"}`

## Gruenstatus nach diesem Block
- Kritische Mutations- und Seiteneffekt-Pfade (Translation-Batch + Submission-Publish) sind klarer lokalisiert.
- Orchestrierung und konkrete Writes sind technisch nachvollziehbarer getrennt.
- Vertrags-/Grenztests decken die neuen Trennlinien explizit ab.
- Basispfad bleibt voll gruen inkl. warning-strict.

## Bewusst offen fuer naechsten Block
- Kein Redesign des gesamten Session-/Event-Transaktionsmodells (nur gezielte Pfadhaertung).
- Keine E2E-Browser-Installation (Playwright-Skips bleiben environment-bedingt).
- Keine weitere CI-Ausweitung ueber stabilen Kern hinaus.

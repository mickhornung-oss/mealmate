# 08_TRANSACTION_HOOK_CONTRACT_REFINEMENT_2026-04-17

## Scope dieses Blocks
Ziel war verhaltensgleiches Refinement der Hook- und Commit-nahen Transaktionsvertraege.
Fokus:
- explizite Prepare/Write/Finalize-Grenzen
- kontrollierte Seiteneffekt-Ausloesung
- Failure-/Rollback-Vertraege testbar absichern

## Verfeinerte Commit-/Hook-Bereiche

### 1) Post-Commit Auto-Translate (`app/translation_service.py`)
Die `after_commit`-Logik wurde in explizite Vertragsphasen zerlegt:

- `_prepare_post_commit_auto_translate_context(session)`
  - poppt pending IDs
  - prueft Feature-/Config-Voraussetzungen
  - liefert bind/provider/language-Kontext oder `None`

- `_run_post_commit_auto_translate_write_phase(auto_session, ...)`
  - fuehrt ausschliesslich die Write-Phase fuer betroffene Recipes aus

- `_finalize_post_commit_auto_translate_session(auto_session, failed=...)`
  - commit bei Erfolg, rollback bei Fehler

- `_after_commit_auto_translate(session)`
  - orchestriert nur noch Prepare -> Write -> Finalize
  - Fehler bleiben best-effort gescoped und werden nicht nach aussen propagiert (verhaltensgleich)

Ergebnis:
- Commit-/Rollback-Vertrag ist explizit nachvollziehbar
- Seiteneffekt-Ausloesung bleibt post-commit und kontrolliert
- keine implizite Mischlogik in einer monolithischen Hook-Funktion

### 2) Submission-Publish Transaktionsvertrag (`app/services_submission.py`)
Vertrag bleibt: Service mutiert/flush't, aber commit't nicht selbst.
Dieser Vertrag ist jetzt explizit regressionsabgesichert (siehe Tests unten).

## Failure-/Vertragstests (neu)

### `tests/test_translation_post_commit_contracts.py`
1. `test_after_commit_auto_translate_rolls_back_on_write_phase_error`
- simuliert Fehler in der post-commit Write-Phase
- erwartet rollback der Auto-Session
- verifiziert: keine partiell persistierten `RecipeTranslation`-Rows
- verifiziert: pending recipe IDs werden konsumiert (kein stilles Re-Trigger-Artefakt)

2. `test_after_commit_auto_translate_noop_when_auto_disabled`
- verifiziert, dass Write-Phase nicht laeuft, wenn Auto-Translate deaktiviert ist
- konsumierte pending IDs bleiben trotzdem konsistent behandelt

### `tests/test_submission_transaction_contracts.py`
1. `test_publish_submission_service_does_not_commit_transaction`
- verifiziert den Service-Vertrag: `publish_submission_as_recipe` fuehrt ohne externen commit nicht zur Persistenz
- rollback nach Service-Aufruf entfernt den erzeugten Recipe-Zustand wie erwartet

## Bereits vorhandene relevante Verträge bleiben gruen
- `tests/test_translation_batch_mutation_boundaries.py`
- `tests/test_translation_batch_jobs.py`
- `tests/test_submission_mutation_boundaries.py`
- `tests/test_service_architecture_boundaries.py`

## Real geprueft
1. Compile:
- `python -m compileall app tests`

2. Fokussierte Regression:
- `pytest -q tests/test_translation_post_commit_contracts.py tests/test_submission_transaction_contracts.py tests/test_translation_batch_mutation_boundaries.py tests/test_translation_batch_jobs.py`
- Ergebnis: `7 passed`

3. Vollsuite:
- `pytest -q`
- Ergebnis: `138 passed, 4 skipped`

4. Warning-strict:
- `pytest -q -W error`
- Ergebnis: `138 passed, 4 skipped`

5. Health:
- `/healthz` -> `200 {"status":"ok"}`

## Gruenstatus nach diesem Block
- Hook-/Commit-nahe Seiteneffektvertraege sind expliziter und kontrollierter.
- Rollback-/Failure-Verhalten fuer post-commit Write-Phase ist testbar abgesichert.
- Submission-Service-Transaktionsvertrag (kein implizites commit) ist explizit validiert.
- Kein Feature-Verhalten geaendert; Basispfad bleibt voll gruen.

## Bewusst offen fuer naechsten Block
- Keine Einfuehrung eines dedizierten Job-/Outbox-Systems (bewusst ausserhalb dieses Blocks).
- Keine Erweiterung auf globale transaktionale Orchestrierung ueber alle Router hinaus.
- E2E-Playwright bleibt environment-abhaengig geskippt.

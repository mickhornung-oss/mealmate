# 06_DOMAIN_SERVICE_HARDENING_EXECUTION_2026-04-17

## Scope dieses Blocks
Ziel war verhaltensgleiches Domain-Hardening mit klareren Service-Grenzen in den verbleibenden Kernmodulen.
Keine Feature-Erweiterung, keine absichtliche Verhaltensaenderung.

## Strukturentscheidungen

### 1) `app/services.py` von Sammelstelle zu stabiler Entry-Layer
`app/services.py` wurde auf klare Entry-Points und Wrapper konsolidiert.
Fachlogik wurde entlang stabiler Verantwortungsgrenzen ausgelagert.

Neue Service-Grenzen:
- `app/services_import.py` (bereits vorhanden): CSV/KochWiki-Import
- `app/services_submission.py` (neu): Submission-Publishing und Submission-Ingredient-Transfer
- `app/services_runtime.py` (neu): Runtime-Infrastrukturhelfer (Upload, Image-URL-Resolution, Token/Meta)

In `app/services.py` verbleiben:
- Domain-Kern fuer Kategorien und Ingredient-Normalisierung
- kompatible Entry-Points fuer bestehende Aufrufer (Wrapper-Pattern)
- weiterhin verhaltensgleiche Signaturen

### 2) `app/translation_service.py` entlang Batch-Orchestrierung geschnitten
Batch-Job-orientierte Logik wurde nach `app/translation_batch_service.py` (neu) ausgelagert.

Ausgelagerte Verantwortlichkeit (Batch-Orchestrierung + Persistenz):
- Batch-Item-Aufbereitung
- Start externer Batch-Jobs
- Job-Lookup/Recent-Jobs
- Result-Payload-Normalisierung
- Result-Apply auf `RecipeTranslation`
- Polling-Lifecycle

In `app/translation_service.py` verbleiben:
- Translation-Domain-Entry-Points
- API-Client-/Provider-Basis
- Queue-/Run-Orchestrierung (non-batch)
- Event-Hooks
- kompatible Wrapper fuer die ausgelagerten Batch-Entry-Points

### 3) Deduplizierung lokaler Heuristik-Reste
In `translation_service.py` verbliebene lokale Stopword-/Tokenisierungs-Helfer wurden entfernt, da diese bereits in `app/translation_helpers.py` zentralisiert sind.
Damit sind die Sprachheuristik-Grenzen eindeutiger und ohne interne Doppelhaltung.

## Verhaltensgleichheit / API-Stabilitaet
- Öffentliche/etablierte Aufrufer bleiben stabil ueber Wrapper in `app/services.py` und `app/translation_service.py`.
- Keine Aenderung an Endpunktverhalten oder Produktfluss beabsichtigt/eingefuehrt.
- Interne Aufrufpfade wurden kompatibel gehalten, nicht gebrochen.

## Architektur-/Grenztests
Neue Tests in `tests/test_service_architecture_boundaries.py`:
- Delegation `app.services.extract_token` -> `app.services_runtime.extract_token`
- Delegation `app.services.get_submission_status_stats` -> `app.services_submission.get_submission_status_stats`
- Delegation `app.translation_service._build_batch_external_id` -> `app.translation_batch_service._build_batch_external_id`

Ziel:
- stabile Entry-Points trotz interner Modultrennung
- Absicherung gegen versehentliche Rueckverschmelzung oder direkte Logikdrift

## Doku-Nachzug
`docs/architecture/ARCHITECTURE.md` wurde im Modul-Layout aktualisiert:
- neue Service-Schnitte (`services_submission`, `services_runtime`, `translation_batch_service`)
- `services.py` explizit als stabiler Entry-/Compatibility-Layer gekennzeichnet

## Real geprueft
1. Compile/Syntax:
- `python -m compileall app tests`

2. Fokussierte Regression:
- `pytest -q tests/test_service_architecture_boundaries.py tests/test_translation_batch_jobs.py tests/test_translation_de_audit_repair.py tests/test_security_csrf_cookie.py tests/test_i18n_umlaut_rendering.py`
- Ergebnis: `17 passed`

3. Voller Basispfad:
- `pytest -q`
- Ergebnis: `132 passed, 4 skipped`

4. Warning-Haerte:
- `pytest -q -W error`
- Ergebnis: `132 passed, 4 skipped`

5. Health-Check:
- `/healthz` -> `200 {"status":"ok"}`

## Gruenstatus nach diesem Block
- Domain-/Service-Grenzen in Kernmodulen sind klarer und technisch nachvollziehbar.
- API-Kompatibilitaet der bisherigen Entry-Points ist gehalten.
- Architekturgrenzen sind durch gezielte Tests abgesichert.
- Basispfad bleibt voll gruen inkl. `-W error`.

## Bewusst offen fuer naechsten Block
- Kein tiefes fachliches Redesign der verbleibenden Domain-Kernlogik (nur strukturelle Haertung).
- Keine funktionale Erweiterung im Translation-/Moderation-Domainverhalten.
- Keine E2E-Browser-Installation (Playwright-Skips bleiben umgebungsabhaengig).

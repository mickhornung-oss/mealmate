# 05_CODEBASE_HARDENING_EXECUTION_2026-04-17

## Scope dieses Blocks
Ziel dieses Blocks war interne Codebase-Haertung ohne Feature-Erweiterung und ohne beabsichtigte Verhaltensaenderung.
Fokus:
- Warnungen im Basispfad eliminieren
- grosse historisch gewachsene Module strukturell schneiden
- gruene technische Basis nach Refactoring erneut real absichern

## Umgesetzte Strukturhaertung

### 1) `app/routers/recipes.py` geschnitten
- Extraktion der nicht-endpoint-spezifischen Support-Logik nach `app/routers/recipes_support.py`.
- `recipes.py` enthaelt danach primär Routing- und Endpoint-Flows.
- `recipes_support.py` enthaelt u. a.:
  - Pagination-/Request-Sprach-Helfer
  - Sichtbarkeits-/Access-Pruefungen
  - Bild-Render-/Fallback-Helfer
  - Translation-Lade-/Display-Helfer
- Nachgezogen:
  - zentrale Imports bereinigt
  - fehlenden `normalize_category`-Import in `recipes.py` korrigiert

### 2) `app/services.py` CSV-Import-Bereich getrennt
- CSV/KochWiki-Importlogik nach `app/services_import.py` ausgelagert.
- In `app/services.py` verbleiben verhaltensgleiche Delegate-Wrapper fuer:
  - `normalize_columns`
  - `read_kochwiki_csv`
  - `read_kochwiki_csv_bytes`
  - `import_kochwiki_csv`
- Ziel: klarere Verantwortlichkeit und kleinere Kern-Datei ohne API-Bruch fuer Aufrufer.

### 3) `app/translation_service.py` Helper entkoppelt
- Parser-/Heuristik-Helfer nach `app/translation_helpers.py` ausgelagert.
- `translation_service.py` nutzt diese per Wrapper weiter.
- Nach einem initialen Regressionseintrag wurden die extrahierten Helper explizit auf verhaltensgleiches Originalniveau zurueckgefuehrt (insb. Payload/Job-Parser).

## Warnungsbehandlung

### SQLite Datetime Adapter Warning
- Datei: `tests/test_db_migration_safety.py`
- Massnahme:
  - explizite sqlite-Adapter-Registrierung fuer `datetime` eingefuehrt:
    - `sqlite3.register_adapter(datetime, lambda value: value.isoformat(sep=" "))`
- Ergebnis:
  - vorherige vermeidbare Warnung im regulären Test-Basispfad beseitigt
  - Testlauf ist auch mit `-W error` gruen

## Stabilitaets-/Session-Haertung in Tests

Beim Refactoring traten reproduzierbare Fehlerszenarien durch Cookie-Domain-Mismatch in TestClient-Szenarien auf.
Um den bestehenden Sicherheitsanspruch testbar korrekt abzubilden, wurden Cookie-Setzungen in relevanten Tests/Helpern auf konsistente Domain+Path-Setzung gebracht (`testserver.local`, `/`).

Betroffene Dateien:
- `tests/helpers.py`
- `tests/test_security_csrf_cookie.py`
- `tests/test_security_session_hygiene.py`

Hinweis:
- Keine Produktfeature-Aenderung.
- Ziel war reproduzierbare, korrekte Abbildung der bereits intendierten Session-/CSRF-Pruefungen im Testlauf.

## CI-Schaerfung
- Datei: `.github/workflows/ci.yml`
- Anpassung:
  - Testschritt von `pytest -q` auf `pytest -q -W error` verschaerft.
- Begruendung:
  - Basispfad ist lokal vollstaendig warning-frei verifiziert.

## Real geprueft

1. Voller Basistestlauf:
- `pytest -q`
- Ergebnis: `129 passed, 4 skipped`

2. Warning-Haerte:
- `pytest -q -W error`
- Ergebnis: `129 passed, 4 skipped`

3. Gesundheitscheck:
- `GET /healthz`
- Ergebnis: `200 {"status":"ok"}`

## Gruenstatus nach diesem Block
- Verhaltensgleiches Refactoring der grossen Zielmodule umgesetzt.
- Vermeidbare Warnungen im Basispfad beseitigt.
- Testbasis weiterhin gruen.
- Run-/Health-Pfad weiterhin gruen.
- CI-Basis konservativ geschaerft (Warnings als Fehler).

## Bewusst offen fuer naechsten Block
- Kein tiefes fachliches Refactoring der Business-Logik in grossen Domain-Dateien.
- Keine Feature-Erweiterungen.
- Keine E2E-Browser-Installation im CI/Local (Playwright-Tests bleiben wie vorgesehen environment-abhaengig geskippt).

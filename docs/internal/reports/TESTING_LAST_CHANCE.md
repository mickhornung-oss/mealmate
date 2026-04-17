# Testing of Last Chance

Dieses Dokument beschreibt den finalen Diagnose- und Konsistenzlauf fuer MealMate ohne Produktivlogik-Aenderungen.

## Ziel

- Translation-Probleme sichtbar machen (ENV, DB-Rows, optionaler Provider-Preview).
- Bild-Fallback-Probleme sichtbar machen (DB primary, source URL, Placeholder, CSP, Wiederholungsbilder).
- User/Admin End-to-End Flows ohne Browser ausfuehren und in einem Gesamtbericht dokumentieren.

## Wichtige Prinzipien

- Standardlauf macht **keine echten externen Translation-API Calls**.
- Externe Translation-Calls laufen nur mit `--real-api`.
- Reports werden unter `diagnostics/` geschrieben.

## Einzel-Tools

### 1) Translation Smoke

```bash
python -m tools.diagnostics.translation_smoke
```

Optional:

```bash
python -m tools.diagnostics.translation_smoke --mock-write
python -m tools.diagnostics.translation_smoke --real-api
```

Output:
- `diagnostics/translation_smoke.md`

### 2) Image Smoke

```bash
python -m tools.diagnostics.image_smoke
```

Output:
- `diagnostics/image_smoke.md`

### 3) Last Chance Run (orchestriert alles)

```bash
python -m tools.diagnostics.last_chance_run
```

Optional:

```bash
python -m tools.diagnostics.last_chance_run --mock-translation-write
python -m tools.diagnostics.last_chance_run --real-api
```

Output:
- `diagnostics/LAST_CHANCE_REPORT.md`
- plus die beiden Teilreports (`translation_smoke.md`, `image_smoke.md`)

## Pytest-Checks (erganzend)

```bash
pytest -q tests/test_translation_consistency.py
pytest -q tests/test_image_consistency.py
pytest -q
```

## Report-Leselogik

In `diagnostics/LAST_CHANCE_REPORT.md`:

- `ENV Summary`: nur Schluesselwerte, keine Secrets.
- `DB Counts`: Vorher/Nachher der kritischen Tabellen.
- `Smoke Tool Status`: Translation/Image Diagnosen.
- `User Flow Steps`: Register/Login/Passwort/Favorites/Review/PDF/Submission/Image-Request.
- `Admin Flow Steps`: Moderation Approve/Reject, Image-Approve, Translation-Sanity.
- `Top Suspects`: konkrete Fehlpunkte.
- `Recommendations`: wahrscheinlichste Ursachen und naechste Debug-Schritte.

## Typische Ursachen

- Translation:
  - `TRANSLATEAPI_ENABLED` aus.
  - Zielsprachen nicht passend gesetzt.
  - Auto-Trigger/Batch-Run nicht ausgefuehrt.
  - UI bindet vorhandene `recipe_translations` noch nicht in allen Ansichten.

- Bilder:
  - Fallback-Reihenfolge nicht eingehalten.
  - Mehrere Cards nutzen denselben `src` durch Template-Variable/Caching-Effekt.
  - CSP `img-src` zu restriktiv fuer externe URLs.

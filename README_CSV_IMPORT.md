# MealMate CSV Import

## Zweck

Dieses Dokument beschreibt den manuellen Admin-CSV-Import fuer neue Rezeptpakete.
Die KochWiki-Seed-Logik ist standardmaessig deaktiviert und wird nicht fuer den Regelbetrieb verwendet.

## CSV Spezifikation (kanonisch)

- Encoding: `utf-8-sig`
- Delimiter: `;` (`,` wird als Fallback akzeptiert)
- Pflichtspalten:
  - `title`
  - `instructions`
- Empfohlene Spalten:
  - `description`
  - `category`
  - `difficulty` (`easy|medium|hard`)
  - `prep_time_minutes` (Integer > 0)
  - `servings_text`
  - `ingredients`
  - `image_url` (nur URL speichern, kein Download)
  - `source_uuid` (fuer eindeutige Zuordnung)

## Ingredients Format

Akzeptiert werden beide Varianten:

1. Pipe-Liste:
   - `2 Eier | 200g Mehl | 1 Prise Salz`
2. JSON-Liste:
   - `["2 Eier", "200g Mehl", "1 Prise Salz"]`

## Import Regeln

- Default: `INSERT ONLY` (nur neue Rezepte)
- Optional: `UPDATE EXISTING` (nur bewusst aktivieren)
- Dry Run verfuegbar: Validierung und Vorschau ohne DB-Schreibvorgaenge
- Dedup:
  - zuerst ueber `source_uuid`
  - fallback ueber normalisierte Kombination aus `title + category + instructions-hash`
- Kategorie wird normalisiert (trim, `_` -> Leerzeichen, Mehrfachspaces reduziert)
- Schwierigkeit wird intern auf `easy|medium|hard` normalisiert

## Admin Workflow

1. Im Admin Panel den Bereich `CSV manuell importieren` oeffnen.
2. Optional `CSV Template herunterladen` oder `CSV Beispiel herunterladen`.
3. Datei hochladen.
4. Optionen setzen:
   - `Nur neue hinzufuegen` (Standard)
   - `Existierende aktualisieren` (nur bewusst)
   - `Nur pruefen (Dry Run)`
5. `Vorschau erstellen` klicken.
6. Vorschau/Fehler/Warnungen pruefen.
7. Fuer echten Import `Import starten` klicken.
8. Bei Warnungen optional `Trotz Warnungen fortsetzen` setzen.

## Haeufige Fehler

- Falsches Encoding:
  - Datei muss als `utf-8-sig` gespeichert sein.
- Falscher Delimiter:
  - Standard ist `;`.
- Ungueltige Difficulty:
  - nur `easy`, `medium`, `hard`.
- Fehlende Pflichtfelder:
  - `title` oder `instructions` fehlt.
- Ungueltige `prep_time_minutes`:
  - muss eine positive ganze Zahl sein.

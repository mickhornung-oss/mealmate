# Import Kitchen Folder

## Zweck
Dieses Tool importiert Rezepte und passende Bilder aus einem lokalen Windows-Ordner in die MealMate-Datenbank.

## Unterstützte Formate
- Rezeptdateien: `JSON`, `HTML/HTM`, `TXT`, `MD/MARKDOWN`
- Bilddateien: `JPG/JPEG`, `PNG`, `WEBP`
- Nicht unterstützte Dateien (z.B. PDF) werden im Report als `unknown_files` geführt.

## Funktionsweise
1. Der Ordner wird rekursiv gescannt.
2. Rezeptdaten werden per Parser + Heuristik extrahiert.
3. Bilder werden bevorzugt über gleichen Dateistamm im selben Ordner gematcht.
4. Dedup läuft über `source_uuid = sha1(relative_path + title)` mit `source=\"kitchen_folder\"`.
5. Ergebnis landet entweder:
   - direkt in `recipes` (default), oder
   - als `pending` in `recipe_submissions` mit `--as-submissions`.
6. Es wird immer ein JSON-Report geschrieben.

## CLI Beispiele
Dry-Run (empfohlen zuerst):

```bash
py -m tools.import_kitchen_folder --folder "C:\Users\mickh\Downloads\Kitchen Hell and Heaven (1)" --dry-run
```

Direkt veröffentlichen (Default-Verhalten):

```bash
py -m tools.import_kitchen_folder --folder "C:\Users\mickh\Downloads\Kitchen Hell and Heaven (1)" --publish
```

Als Moderations-Einreichungen:

```bash
py -m tools.import_kitchen_folder --folder "C:\Users\mickh\Downloads\Kitchen Hell and Heaven (1)" --as-submissions
```

Mit Limit und Report-Pfad:

```bash
py -m tools.import_kitchen_folder --folder "C:\Users\mickh\Downloads\Kitchen Hell and Heaven (1)" --limit 100 --report "diagnostics/kitchen_import_report.json"
```

## Optionen
- `--folder` (required): Root-Ordner
- `--dry-run`: Keine DB-Writes
- `--as-submissions`: Import in `recipe_submissions` statt `recipes`
- `--publish / --no-publish`: `is_published` für direkte Recipe-Imports
- `--creator-email`: Admin-Creator (Default aus `SEED_ADMIN_EMAIL`)
- `--limit`: Maximalzahl Rezeptdateien
- `--match-strategy stem|nearest`: Bild-Matching-Strategie
- `--report`: JSON-Report-Ausgabepfad

## Troubleshooting
- **PDF-Dateien werden nicht importiert:** bitte vorher in `TXT`, `HTML` oder `JSON` exportieren.
- **Bilder werden nicht gematcht:** Dateinamen angleichen (gleicher Stem im selben Ordner).
- **Duplicate Skips:** kommt von bestehendem `source_uuid` in der DB.
- **HTML-Parsing schwach:** `beautifulsoup4` installieren/aktualisieren.

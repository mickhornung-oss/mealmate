# Import Kitchen Folder

## Zweck
Dieses Tool importiert Rezepte und passende Bilder aus einem lokalen Windows-Ordner in die MealMate-Datenbank.

## UnterstÃ¼tzte Formate
- Rezeptdateien: `JSON`, `HTML/HTM`, `TXT`, `MD/MARKDOWN`
- Bilddateien: `JPG/JPEG`, `PNG`, `WEBP`
- Nicht unterstÃ¼tzte Dateien (z.B. PDF) werden im Report als `unknown_files` gefÃ¼hrt.

## Funktionsweise
1. Der Ordner wird rekursiv gescannt.
2. Rezeptdaten werden per Parser + Heuristik extrahiert.
3. Bilder werden bevorzugt Ã¼ber gleichen Dateistamm im selben Ordner gematcht.
4. Dedup lÃ¤uft Ã¼ber `source_uuid = sha1(relative_path + title)` mit `source=\"kitchen_folder\"`.
5. Ergebnis landet entweder:
   - direkt in `recipes` (default), oder
   - als `pending` in `recipe_submissions` mit `--as-submissions`.
6. Es wird immer ein JSON-Report geschrieben.

## CLI Beispiele
Dry-Run (empfohlen zuerst):

```bash
py -m tools.import_kitchen_folder --folder "C:\\path\\to\\recipe-source-folder" --dry-run
```

Direkt verÃ¶ffentlichen (Default-Verhalten):

```bash
py -m tools.import_kitchen_folder --folder "C:\\path\\to\\recipe-source-folder" --publish
```

Als Moderations-Einreichungen:

```bash
py -m tools.import_kitchen_folder --folder "C:\\path\\to\\recipe-source-folder" --as-submissions
```

Mit Limit und Report-Pfad:

```bash
py -m tools.import_kitchen_folder --folder "C:\\path\\to\\recipe-source-folder" --limit 100 --report "tmp/kitchen_import_report.json"
```

## Optionen
- `--folder` (required): Root-Ordner
- `--dry-run`: Keine DB-Writes
- `--as-submissions`: Import in `recipe_submissions` statt `recipes`
- `--publish / --no-publish`: `is_published` fÃ¼r direkte Recipe-Imports
- `--creator-email`: Admin-Creator (Default aus `SEED_ADMIN_EMAIL`)
- `--limit`: Maximalzahl Rezeptdateien
- `--match-strategy stem|nearest`: Bild-Matching-Strategie
- `--report`: JSON-Report-Ausgabepfad

## Troubleshooting
- **PDF-Dateien werden nicht importiert:** bitte vorher in `TXT`, `HTML` oder `JSON` exportieren.
- **Bilder werden nicht gematcht:** Dateinamen angleichen (gleicher Stem im selben Ordner).
- **Duplicate Skips:** kommt von bestehendem `source_uuid` in der DB.
- **HTML-Parsing schwach:** `beautifulsoup4` installieren/aktualisieren.


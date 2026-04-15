# Deliverable: CSV-Import Ausbau + Seed-UI Entfernung

## Betroffene Dateien

- `app/csv_import.py`
- `app/routers/admin.py`
- `app/templates/admin.html`
- `app/config.py`
- `app/main.py`
- `app/i18n/de.py`
- `.env.example`
- `README_CSV_IMPORT.md`
- `README_RUNBOOK.md`

## app/csv_import.py
```python
import csv
import hashlib
import io
import json
import re
from dataclasses import dataclass, field
from typing import Any, Literal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Recipe
from app.services import (
    DEFAULT_CATEGORY,
    get_or_create_ingredient,
    normalize_category,
    normalize_ingredient_name,
    parse_ingredient_text,
    parse_list_like,
    parse_optional_int,
    replace_recipe_ingredients,
    sanitize_difficulty,
)

ADMIN_IMPORT_MODE = Literal["insert_only", "update_existing"]

CANONICAL_CSV_COLUMNS = [
    "title",
    "instructions",
    "description",
    "category",
    "difficulty",
    "prep_time_minutes",
    "servings_text",
    "ingredients",
    "image_url",
    "source_uuid",
]


@dataclass
class AdminCSVPreviewRow:
    row_number: int
    title: str
    category: str
    difficulty: str
    prep_time_minutes: str
    source_uuid: str
    status: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class AdminCSVImportReport:
    mode: ADMIN_IMPORT_MODE
    dry_run: bool
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    preview_rows: list[AdminCSVPreviewRow] = field(default_factory=list)
    total_rows: int = 0
    fatal_error_rows: int = 0
    delimiter: str = ";"
    encoding: str = "utf-8-sig"


@dataclass
class _PreparedRow:
    row_number: int
    title: str
    title_normalized: str
    description: str
    instructions: str
    instruction_hash: str
    category: str
    category_normalized: str
    difficulty: str
    prep_time_minutes: int
    servings_text: str | None
    ingredients: list[dict[str, Any]]
    image_url: str | None
    source_uuid: str | None
    skip_reason: str | None = None


def _normalize_header(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", str(name or "").strip().lower())
    return normalized.strip("_")


def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def _normalize_text_lower(value: Any) -> str:
    return _normalize_text(value).lower()


def _instruction_hash(value: str) -> str:
    normalized = _normalize_text_lower(value)
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]


def _detect_delimiter(text: str) -> str:
    sample_lines = [line for line in text.splitlines() if line.strip()][:5]
    sample = "\n".join(sample_lines)
    return ";" if sample.count(";") >= sample.count(",") else ","


def _parse_csv_rows(csv_bytes: bytes) -> tuple[list[dict[str, str]], str]:
    text = csv_bytes.decode("utf-8-sig", errors="replace")
    delimiter = _detect_delimiter(text)
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    rows: list[dict[str, str]] = []
    for row in reader:
        normalized_row: dict[str, str] = {}
        for key, value in row.items():
            normalized_row[_normalize_header(key)] = _normalize_text(value)
        rows.append(normalized_row)
    if delimiter == ";" and rows and len(rows[0]) <= 1:
        fallback_reader = csv.DictReader(io.StringIO(text), delimiter=",")
        fallback_rows: list[dict[str, str]] = []
        for row in fallback_reader:
            normalized_row = {}
            for key, value in row.items():
                normalized_row[_normalize_header(key)] = _normalize_text(value)
            fallback_rows.append(normalized_row)
        if fallback_rows and len(fallback_rows[0]) > 1:
            return fallback_rows, ","
    return rows, delimiter


def _pick_value(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = row.get(key, "")
        if value:
            return value
    return ""


def _parse_admin_ingredients(raw_value: str) -> list[dict[str, Any]]:
    cleaned = str(raw_value or "").strip()
    if not cleaned:
        return []
    if cleaned.startswith("[") and cleaned.endswith("]"):
        try:
            loaded = json.loads(cleaned)
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, list):
            tokens = [str(item).strip() for item in loaded if str(item).strip()]
        else:
            tokens = parse_list_like(cleaned)
    elif "\n" in cleaned:
        return parse_ingredient_text(cleaned)
    elif " | " in cleaned:
        tokens = [token.strip() for token in cleaned.split(" | ") if token.strip()]
    else:
        tokens = [token.strip() for token in parse_list_like(cleaned) if token.strip()]
    entries: list[dict[str, Any]] = []
    for token in tokens:
        match = re.match(r"^\s*([\d.,/\-]+\s*[A-Za-z%]*)\s+(.+)$", token)
        if match:
            quantity_text = match.group(1).strip()
            name = match.group(2).strip()
        else:
            quantity_text = ""
            name = token.strip()
        if not name:
            continue
        entries.append(
            {
                "name": name[:200],
                "quantity_text": quantity_text[:120],
                "grams": parse_optional_int(token),
            }
        )
    return entries


def _find_existing_recipe_for_admin(db: Session, payload: _PreparedRow) -> Recipe | None:
    if payload.source_uuid:
        existing = db.scalar(select(Recipe).where(Recipe.source_uuid == payload.source_uuid))
        if existing:
            return existing
    candidates = db.scalars(
        select(Recipe).where(
            func.lower(Recipe.title) == payload.title_normalized,
            func.lower(Recipe.category) == payload.category_normalized,
        )
    ).all()
    for recipe in candidates:
        if _instruction_hash(recipe.instructions) == payload.instruction_hash:
            return recipe
    return None


def _prepare_rows(
    rows: list[dict[str, str]],
    mode: ADMIN_IMPORT_MODE,
    preview_limit: int,
) -> tuple[list[_PreparedRow], AdminCSVImportReport]:
    report = AdminCSVImportReport(mode=mode, dry_run=True)
    prepared_rows: list[_PreparedRow] = []
    seen_source_uuid: set[str] = set()
    seen_fallback: set[tuple[str, str, str]] = set()
    for index, row in enumerate(rows, start=2):
        report.total_rows += 1
        row_errors: list[str] = []
        row_warnings: list[str] = []
        title_raw = _pick_value(row, "title", "name")
        instructions_raw = _pick_value(row, "instructions", "steps")
        if not title_raw:
            row_errors.append("title fehlt")
        if not instructions_raw:
            row_errors.append("instructions fehlt")
        title = _normalize_text(title_raw)[:255]
        title_normalized = _normalize_text_lower(title)
        instructions = instructions_raw.strip()
        instruction_hash = _instruction_hash(instructions)
        description = _pick_value(row, "description") or "Importiert ueber Admin CSV."
        category = normalize_category(_pick_value(row, "category") or DEFAULT_CATEGORY)
        category_normalized = _normalize_text_lower(category)
        difficulty_raw = _pick_value(row, "difficulty")
        difficulty = sanitize_difficulty(difficulty_raw or "medium")
        if difficulty_raw and difficulty not in {"easy", "medium", "hard"}:
            row_warnings.append(f"difficulty '{difficulty_raw}' wurde auf '{difficulty}' gesetzt")
        prep_time_raw = _pick_value(row, "prep_time_minutes")
        prep_time_minutes = 30
        if prep_time_raw:
            parsed_prep = parse_optional_int(prep_time_raw)
            if parsed_prep is None or parsed_prep <= 0:
                row_errors.append("prep_time_minutes ist ungueltig")
            else:
                prep_time_minutes = parsed_prep
        servings_text = _pick_value(row, "servings_text")[:120] or None
        image_url_raw = _pick_value(row, "image_url")
        image_url = image_url_raw[:1024] if image_url_raw else None
        if image_url and not (image_url.startswith("http://") or image_url.startswith("https://")):
            row_warnings.append("image_url ist ungueltig und wurde ignoriert")
            image_url = None
        source_uuid = _pick_value(row, "source_uuid")[:120] or None
        ingredients = _parse_admin_ingredients(_pick_value(row, "ingredients"))
        if source_uuid:
            if source_uuid in seen_source_uuid:
                row_warnings.append("doppelte source_uuid in der CSV, Zeile wird uebersprungen")
                skip_reason = "duplicate-source-uuid"
            else:
                seen_source_uuid.add(source_uuid)
                skip_reason = None
        else:
            fallback_key = (title_normalized, category_normalized, instruction_hash)
            if fallback_key in seen_fallback:
                row_warnings.append("doppeltes Rezept in der CSV, Zeile wird uebersprungen")
                skip_reason = "duplicate-fallback-key"
            else:
                seen_fallback.add(fallback_key)
                skip_reason = None
        if row_errors:
            report.fatal_error_rows += 1
            report.errors.extend([f"Zeile {index}: {reason}" for reason in row_errors])
        if row_warnings:
            report.warnings.extend([f"Zeile {index}: {reason}" for reason in row_warnings])
        status = "ok"
        if row_errors:
            status = "error"
        elif skip_reason:
            status = "skip"
        elif row_warnings:
            status = "warning"
        if len(report.preview_rows) < preview_limit:
            report.preview_rows.append(
                AdminCSVPreviewRow(
                    row_number=index,
                    title=title,
                    category=category,
                    difficulty=difficulty,
                    prep_time_minutes=str(prep_time_minutes),
                    source_uuid=source_uuid or "",
                    status=status,
                    errors=row_errors,
                    warnings=row_warnings,
                )
            )
        prepared_rows.append(
            _PreparedRow(
                row_number=index,
                title=title,
                title_normalized=title_normalized,
                description=description.strip(),
                instructions=instructions,
                instruction_hash=instruction_hash,
                category=category,
                category_normalized=category_normalized,
                difficulty=difficulty,
                prep_time_minutes=prep_time_minutes,
                servings_text=servings_text,
                ingredients=ingredients,
                image_url=image_url,
                source_uuid=source_uuid,
                skip_reason=skip_reason,
            )
        )
    return prepared_rows, report


def _create_recipe_from_payload(db: Session, payload: _PreparedRow, creator_id: int) -> Recipe:
    recipe = Recipe(
        title=payload.title,
        description=payload.description,
        instructions=payload.instructions,
        category=payload.category,
        prep_time_minutes=payload.prep_time_minutes,
        difficulty=payload.difficulty,
        creator_id=creator_id,
        source="admin_csv",
        source_uuid=payload.source_uuid,
        source_url=None,
        source_image_url=payload.image_url,
        title_image_url=payload.image_url,
        servings_text=payload.servings_text,
        total_time_minutes=None,
    )
    db.add(recipe)
    db.flush()
    if payload.ingredients:
        replace_recipe_ingredients(db, recipe, payload.ingredients)
    return recipe


def _update_recipe_from_payload(db: Session, recipe: Recipe, payload: _PreparedRow) -> None:
    recipe.description = payload.description
    recipe.instructions = payload.instructions
    recipe.category = payload.category
    recipe.prep_time_minutes = payload.prep_time_minutes
    recipe.difficulty = payload.difficulty
    recipe.servings_text = payload.servings_text
    if payload.image_url:
        recipe.title_image_url = payload.image_url
        recipe.source_image_url = payload.image_url
    if payload.source_uuid and not recipe.source_uuid:
        recipe.source_uuid = payload.source_uuid
    if payload.ingredients:
        replace_recipe_ingredients(db, recipe, payload.ingredients)
    db.add(recipe)


def import_admin_csv(
    db: Session,
    csv_bytes: bytes,
    creator_id: int,
    mode: ADMIN_IMPORT_MODE = "insert_only",
    dry_run: bool = True,
    batch_size: int = 200,
    preview_limit: int = 20,
    autocommit: bool = False,
) -> AdminCSVImportReport:
    if mode not in {"insert_only", "update_existing"}:
        raise ValueError("mode must be 'insert_only' or 'update_existing'")
    rows, delimiter = _parse_csv_rows(csv_bytes)
    prepared_rows, report = _prepare_rows(rows, mode, preview_limit)
    report.delimiter = delimiter
    report.dry_run = dry_run
    if report.fatal_error_rows > 0:
        return report
    pending_writes = 0
    for payload in prepared_rows:
        if payload.skip_reason:
            report.skipped += 1
            continue
        existing = _find_existing_recipe_for_admin(db, payload)
        if existing and mode == "insert_only":
            report.skipped += 1
            continue
        if existing and mode == "update_existing":
            if not dry_run:
                _update_recipe_from_payload(db, existing, payload)
                pending_writes += 1
            report.updated += 1
        else:
            if not dry_run:
                _create_recipe_from_payload(db, payload, creator_id)
                pending_writes += 1
            report.inserted += 1
        if not dry_run and pending_writes >= batch_size:
            if autocommit:
                db.commit()
            else:
                db.flush()
            pending_writes = 0
    if not dry_run and pending_writes > 0:
        if autocommit:
            db.commit()
        else:
            db.flush()
    return report


def build_csv_template_bytes() -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(CANONICAL_CSV_COLUMNS)
    writer.writerow(
        [
            "Spaghetti Carbonara",
            "Pasta kochen. Speck anbraten. Mit Ei-Kaese-Mischung verruehren.",
            "Klassische Carbonara mit Ei und Pecorino.",
            "Pasta",
            "medium",
            "25",
            "2 Portionen",
            "200g Spaghetti | 120g Guanciale | 2 Eier | 50g Pecorino",
            "https://example.com/carbonara.jpg",
            "admin-demo-001",
        ]
    )
    content = buffer.getvalue()
    return ("\ufeff" + content).encode("utf-8")


def build_csv_example_bytes() -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer, delimiter=";")
    writer.writerow(CANONICAL_CSV_COLUMNS)
    writer.writerow(
        [
            "Linsensuppe",
            "Zwiebeln anschwitzen. Linsen dazugeben. Mit Bruehe kochen.",
            "Herzhafte Suppe fuer kalte Tage.",
            "Suppen",
            "easy",
            "35",
            "4 Portionen",
            "250g Linsen | 1 Zwiebel | 2 Karotten | 1L Gemuesebruehe",
            "",
            "admin-demo-002",
        ]
    )
    writer.writerow(
        [
            "Schneller Obstsalat",
            "Obst schneiden und mit Zitronensaft vermengen.",
            "Frischer Salat mit saisonalem Obst.",
            "Dessert",
            "easy",
            "10",
            "3 Portionen",
            "[\"2 Aepfel\", \"1 Banane\", \"1 Orange\", \"1 TL Zitronensaft\"]",
            "https://example.com/obstsalat.jpg",
            "admin-demo-003",
        ]
    )
    writer.writerow(
        [
            "Ofengemuese",
            "Gemuese schneiden, wuerzen und 30 Minuten backen.",
            "Knackiges Ofengemuese.",
            "Hauptgericht",
            "medium",
            "40",
            "2 Portionen",
            "2 Karotten | 1 Zucchini | 1 Paprika | 2 EL Olivenoel",
            "",
            "",
        ]
    )
    content = buffer.getvalue()
    return ("\ufeff" + content).encode("utf-8")
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import csv'.
2. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import hashlib'.
3. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import io'.
4. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import json'.
5. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import re'.
6. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from dataclasses import dataclass, field'.
7. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from typing import Any, Literal'.
8. Diese Zeile ist leer und trennt den Inhalt strukturiert.
9. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from sqlalchemy import func, select'.
10. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from sqlalchemy.orm import Session'.
11. Diese Zeile ist leer und trennt den Inhalt strukturiert.
12. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.models import Recipe'.
13. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.services import ('.
14. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'DEFAULT_CATEGORY,'.
15. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'get_or_create_ingredient,'.
16. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'normalize_category,'.
17. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'normalize_ingredient_name,'.
18. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'parse_ingredient_text,'.
19. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'parse_list_like,'.
20. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'parse_optional_int,'.
21. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'replace_recipe_ingredients,'.
22. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'sanitize_difficulty,'.
23. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
24. Diese Zeile ist leer und trennt den Inhalt strukturiert.
25. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ADMIN_IMPORT_MODE = Literal["insert_only", "update_existing"]'.
26. Diese Zeile ist leer und trennt den Inhalt strukturiert.
27. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'CANONICAL_CSV_COLUMNS = ['.
28. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"title",'.
29. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"instructions",'.
30. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"description",'.
31. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"category",'.
32. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"difficulty",'.
33. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"prep_time_minutes",'.
34. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"servings_text",'.
35. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"ingredients",'.
36. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"image_url",'.
37. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"source_uuid",'.
38. Diese Zeile enth?lt den konkreten Code/Textabschnitt ']'.
39. Diese Zeile ist leer und trennt den Inhalt strukturiert.
40. Diese Zeile ist leer und trennt den Inhalt strukturiert.
41. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@dataclass'.
42. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'class AdminCSVPreviewRow:'.
43. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_number: int'.
44. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title: str'.
45. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'category: str'.
46. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'difficulty: str'.
47. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prep_time_minutes: str'.
48. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'source_uuid: str'.
49. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status: str'.
50. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'errors: list[str] = field(default_factory=list)'.
51. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'warnings: list[str] = field(default_factory=list)'.
52. Diese Zeile ist leer und trennt den Inhalt strukturiert.
53. Diese Zeile ist leer und trennt den Inhalt strukturiert.
54. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@dataclass'.
55. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'class AdminCSVImportReport:'.
56. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'mode: ADMIN_IMPORT_MODE'.
57. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'dry_run: bool'.
58. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'inserted: int = 0'.
59. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'updated: int = 0'.
60. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'skipped: int = 0'.
61. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'errors: list[str] = field(default_factory=list)'.
62. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'warnings: list[str] = field(default_factory=list)'.
63. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_rows: list[AdminCSVPreviewRow] = field(default_factory=list)'.
64. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'total_rows: int = 0'.
65. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'fatal_error_rows: int = 0'.
66. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'delimiter: str = ";"'.
67. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'encoding: str = "utf-8-sig"'.
68. Diese Zeile ist leer und trennt den Inhalt strukturiert.
69. Diese Zeile ist leer und trennt den Inhalt strukturiert.
70. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@dataclass'.
71. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'class _PreparedRow:'.
72. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_number: int'.
73. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title: str'.
74. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title_normalized: str'.
75. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'description: str'.
76. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'instructions: str'.
77. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'instruction_hash: str'.
78. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'category: str'.
79. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'category_normalized: str'.
80. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'difficulty: str'.
81. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prep_time_minutes: int'.
82. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'servings_text: str | None'.
83. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ingredients: list[dict[str, Any]]'.
84. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'image_url: str | None'.
85. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'source_uuid: str | None'.
86. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'skip_reason: str | None = None'.
87. Diese Zeile ist leer und trennt den Inhalt strukturiert.
88. Diese Zeile ist leer und trennt den Inhalt strukturiert.
89. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _normalize_header(name: str) -> str:'.
90. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'normalized = re.sub(r"[^a-z0-9]+", "_", str(name or "").strip().lower())'.
91. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return normalized.strip("_")'.
92. Diese Zeile ist leer und trennt den Inhalt strukturiert.
93. Diese Zeile ist leer und trennt den Inhalt strukturiert.
94. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _normalize_text(value: Any) -> str:'.
95. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return re.sub(r"\s+", " ", str(value or "").strip())'.
96. Diese Zeile ist leer und trennt den Inhalt strukturiert.
97. Diese Zeile ist leer und trennt den Inhalt strukturiert.
98. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _normalize_text_lower(value: Any) -> str:'.
99. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return _normalize_text(value).lower()'.
100. Diese Zeile ist leer und trennt den Inhalt strukturiert.
101. Diese Zeile ist leer und trennt den Inhalt strukturiert.
102. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _instruction_hash(value: str) -> str:'.
103. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'normalized = _normalize_text_lower(value)'.
104. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]'.
105. Diese Zeile ist leer und trennt den Inhalt strukturiert.
106. Diese Zeile ist leer und trennt den Inhalt strukturiert.
107. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _detect_delimiter(text: str) -> str:'.
108. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'sample_lines = [line for line in text.splitlines() if line.strip()][:5]'.
109. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'sample = "\n".join(sample_lines)'.
110. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return ";" if sample.count(";") >= sample.count(",") else ","'.
111. Diese Zeile ist leer und trennt den Inhalt strukturiert.
112. Diese Zeile ist leer und trennt den Inhalt strukturiert.
113. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _parse_csv_rows(csv_bytes: bytes) -> tuple[list[dict[str, str]], str]:'.
114. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'text = csv_bytes.decode("utf-8-sig", errors="replace")'.
115. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'delimiter = _detect_delimiter(text)'.
116. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)'.
117. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'rows: list[dict[str, str]] = []'.
118. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'for row in reader:'.
119. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'normalized_row: dict[str, str] = {}'.
120. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'for key, value in row.items():'.
121. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'normalized_row[_normalize_header(key)] = _normalize_text(value)'.
122. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'rows.append(normalized_row)'.
123. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if delimiter == ";" and rows and len(rows[0]) <= 1:'.
124. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'fallback_reader = csv.DictReader(io.StringIO(text), delimiter=",")'.
125. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'fallback_rows: list[dict[str, str]] = []'.
126. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'for row in fallback_reader:'.
127. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'normalized_row = {}'.
128. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'for key, value in row.items():'.
129. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'normalized_row[_normalize_header(key)] = _normalize_text(value)'.
130. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'fallback_rows.append(normalized_row)'.
131. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if fallback_rows and len(fallback_rows[0]) > 1:'.
132. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return fallback_rows, ","'.
133. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return rows, delimiter'.
134. Diese Zeile ist leer und trennt den Inhalt strukturiert.
135. Diese Zeile ist leer und trennt den Inhalt strukturiert.
136. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _pick_value(row: dict[str, str], *keys: str) -> str:'.
137. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'for key in keys:'.
138. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'value = row.get(key, "")'.
139. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if value:'.
140. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return value'.
141. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return ""'.
142. Diese Zeile ist leer und trennt den Inhalt strukturiert.
143. Diese Zeile ist leer und trennt den Inhalt strukturiert.
144. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _parse_admin_ingredients(raw_value: str) -> list[dict[str, Any]]:'.
145. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'cleaned = str(raw_value or "").strip()'.
146. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not cleaned:'.
147. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return []'.
148. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if cleaned.startswith("[") and cleaned.endswith("]"):'.
149. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'try:'.
150. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'loaded = json.loads(cleaned)'.
151. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'except json.JSONDecodeError:'.
152. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'loaded = None'.
153. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if isinstance(loaded, list):'.
154. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'tokens = [str(item).strip() for item in loaded if str(item).strip()]'.
155. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
156. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'tokens = parse_list_like(cleaned)'.
157. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'elif "\n" in cleaned:'.
158. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return parse_ingredient_text(cleaned)'.
159. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'elif " | " in cleaned:'.
160. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'tokens = [token.strip() for token in cleaned.split(" | ") if token.strip()]'.
161. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
162. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'tokens = [token.strip() for token in parse_list_like(cleaned) if token.strip()]'.
163. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'entries: list[dict[str, Any]] = []'.
164. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'for token in tokens:'.
165. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'match = re.match(r"^\s*([\d.,/\-]+\s*[A-Za-z%]*)\s+(.+)$", token)'.
166. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if match:'.
167. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'quantity_text = match.group(1).strip()'.
168. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'name = match.group(2).strip()'.
169. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
170. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'quantity_text = ""'.
171. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'name = token.strip()'.
172. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not name:'.
173. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'continue'.
174. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'entries.append('.
175. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{'.
176. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"name": name[:200],'.
177. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"quantity_text": quantity_text[:120],'.
178. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"grams": parse_optional_int(token),'.
179. Diese Zeile enth?lt den konkreten Code/Textabschnitt '}'.
180. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
181. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return entries'.
182. Diese Zeile ist leer und trennt den Inhalt strukturiert.
183. Diese Zeile ist leer und trennt den Inhalt strukturiert.
184. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _find_existing_recipe_for_admin(db: Session, payload: _PreparedRow) -> Re...'.
185. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if payload.source_uuid:'.
186. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'existing = db.scalar(select(Recipe).where(Recipe.source_uuid == payload.sourc...'.
187. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if existing:'.
188. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return existing'.
189. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'candidates = db.scalars('.
190. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'select(Recipe).where('.
191. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'func.lower(Recipe.title) == payload.title_normalized,'.
192. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'func.lower(Recipe.category) == payload.category_normalized,'.
193. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
194. Diese Zeile enth?lt den konkreten Code/Textabschnitt ').all()'.
195. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'for recipe in candidates:'.
196. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if _instruction_hash(recipe.instructions) == payload.instruction_hash:'.
197. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return recipe'.
198. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return None'.
199. Diese Zeile ist leer und trennt den Inhalt strukturiert.
200. Diese Zeile ist leer und trennt den Inhalt strukturiert.
201. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _prepare_rows('.
202. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'rows: list[dict[str, str]],'.
203. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'mode: ADMIN_IMPORT_MODE,'.
204. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_limit: int,'.
205. Diese Zeile enth?lt den konkreten Code/Textabschnitt ') -> tuple[list[_PreparedRow], AdminCSVImportReport]:'.
206. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report = AdminCSVImportReport(mode=mode, dry_run=True)'.
207. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prepared_rows: list[_PreparedRow] = []'.
208. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'seen_source_uuid: set[str] = set()'.
209. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'seen_fallback: set[tuple[str, str, str]] = set()'.
210. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'for index, row in enumerate(rows, start=2):'.
211. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.total_rows += 1'.
212. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_errors: list[str] = []'.
213. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_warnings: list[str] = []'.
214. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title_raw = _pick_value(row, "title", "name")'.
215. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'instructions_raw = _pick_value(row, "instructions", "steps")'.
216. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not title_raw:'.
217. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_errors.append("title fehlt")'.
218. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not instructions_raw:'.
219. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_errors.append("instructions fehlt")'.
220. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title = _normalize_text(title_raw)[:255]'.
221. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title_normalized = _normalize_text_lower(title)'.
222. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'instructions = instructions_raw.strip()'.
223. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'instruction_hash = _instruction_hash(instructions)'.
224. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'description = _pick_value(row, "description") or "Importiert ueber Admin CSV."'.
225. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'category = normalize_category(_pick_value(row, "category") or DEFAULT_CATEGORY)'.
226. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'category_normalized = _normalize_text_lower(category)'.
227. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'difficulty_raw = _pick_value(row, "difficulty")'.
228. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'difficulty = sanitize_difficulty(difficulty_raw or "medium")'.
229. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if difficulty_raw and difficulty not in {"easy", "medium", "hard"}:'.
230. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_warnings.append(f"difficulty '{difficulty_raw}' wurde auf '{difficulty}' ...'.
231. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prep_time_raw = _pick_value(row, "prep_time_minutes")'.
232. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prep_time_minutes = 30'.
233. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if prep_time_raw:'.
234. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'parsed_prep = parse_optional_int(prep_time_raw)'.
235. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if parsed_prep is None or parsed_prep <= 0:'.
236. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_errors.append("prep_time_minutes ist ungueltig")'.
237. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
238. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prep_time_minutes = parsed_prep'.
239. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'servings_text = _pick_value(row, "servings_text")[:120] or None'.
240. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'image_url_raw = _pick_value(row, "image_url")'.
241. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'image_url = image_url_raw[:1024] if image_url_raw else None'.
242. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if image_url and not (image_url.startswith("http://") or image_url.startswith...'.
243. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_warnings.append("image_url ist ungueltig und wurde ignoriert")'.
244. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'image_url = None'.
245. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'source_uuid = _pick_value(row, "source_uuid")[:120] or None'.
246. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ingredients = _parse_admin_ingredients(_pick_value(row, "ingredients"))'.
247. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if source_uuid:'.
248. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if source_uuid in seen_source_uuid:'.
249. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_warnings.append("doppelte source_uuid in der CSV, Zeile wird uebersprungen")'.
250. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'skip_reason = "duplicate-source-uuid"'.
251. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
252. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'seen_source_uuid.add(source_uuid)'.
253. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'skip_reason = None'.
254. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
255. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'fallback_key = (title_normalized, category_normalized, instruction_hash)'.
256. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if fallback_key in seen_fallback:'.
257. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_warnings.append("doppeltes Rezept in der CSV, Zeile wird uebersprungen")'.
258. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'skip_reason = "duplicate-fallback-key"'.
259. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
260. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'seen_fallback.add(fallback_key)'.
261. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'skip_reason = None'.
262. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if row_errors:'.
263. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.fatal_error_rows += 1'.
264. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.errors.extend([f"Zeile {index}: {reason}" for reason in row_errors])'.
265. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if row_warnings:'.
266. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.warnings.extend([f"Zeile {index}: {reason}" for reason in row_warnings])'.
267. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status = "ok"'.
268. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if row_errors:'.
269. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status = "error"'.
270. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'elif skip_reason:'.
271. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status = "skip"'.
272. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'elif row_warnings:'.
273. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status = "warning"'.
274. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if len(report.preview_rows) < preview_limit:'.
275. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.preview_rows.append('.
276. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'AdminCSVPreviewRow('.
277. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_number=index,'.
278. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title=title,'.
279. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'category=category,'.
280. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'difficulty=difficulty,'.
281. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prep_time_minutes=str(prep_time_minutes),'.
282. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'source_uuid=source_uuid or "",'.
283. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status=status,'.
284. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'errors=row_errors,'.
285. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'warnings=row_warnings,'.
286. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
287. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
288. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prepared_rows.append('.
289. Diese Zeile enth?lt den konkreten Code/Textabschnitt '_PreparedRow('.
290. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'row_number=index,'.
291. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title=title,'.
292. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title_normalized=title_normalized,'.
293. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'description=description.strip(),'.
294. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'instructions=instructions,'.
295. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'instruction_hash=instruction_hash,'.
296. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'category=category,'.
297. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'category_normalized=category_normalized,'.
298. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'difficulty=difficulty,'.
299. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prep_time_minutes=prep_time_minutes,'.
300. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'servings_text=servings_text,'.
301. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ingredients=ingredients,'.
302. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'image_url=image_url,'.
303. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'source_uuid=source_uuid,'.
304. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'skip_reason=skip_reason,'.
305. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
306. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
307. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return prepared_rows, report'.
308. Diese Zeile ist leer und trennt den Inhalt strukturiert.
309. Diese Zeile ist leer und trennt den Inhalt strukturiert.
310. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _create_recipe_from_payload(db: Session, payload: _PreparedRow, creator_i...'.
311. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe = Recipe('.
312. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title=payload.title,'.
313. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'description=payload.description,'.
314. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'instructions=payload.instructions,'.
315. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'category=payload.category,'.
316. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prep_time_minutes=payload.prep_time_minutes,'.
317. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'difficulty=payload.difficulty,'.
318. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'creator_id=creator_id,'.
319. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'source="admin_csv",'.
320. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'source_uuid=payload.source_uuid,'.
321. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'source_url=None,'.
322. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'source_image_url=payload.image_url,'.
323. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'title_image_url=payload.image_url,'.
324. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'servings_text=payload.servings_text,'.
325. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'total_time_minutes=None,'.
326. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
327. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.add(recipe)'.
328. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.flush()'.
329. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if payload.ingredients:'.
330. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'replace_recipe_ingredients(db, recipe, payload.ingredients)'.
331. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return recipe'.
332. Diese Zeile ist leer und trennt den Inhalt strukturiert.
333. Diese Zeile ist leer und trennt den Inhalt strukturiert.
334. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _update_recipe_from_payload(db: Session, recipe: Recipe, payload: _Prepar...'.
335. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe.description = payload.description'.
336. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe.instructions = payload.instructions'.
337. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe.category = payload.category'.
338. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe.prep_time_minutes = payload.prep_time_minutes'.
339. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe.difficulty = payload.difficulty'.
340. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe.servings_text = payload.servings_text'.
341. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if payload.image_url:'.
342. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe.title_image_url = payload.image_url'.
343. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe.source_image_url = payload.image_url'.
344. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if payload.source_uuid and not recipe.source_uuid:'.
345. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe.source_uuid = payload.source_uuid'.
346. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if payload.ingredients:'.
347. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'replace_recipe_ingredients(db, recipe, payload.ingredients)'.
348. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.add(recipe)'.
349. Diese Zeile ist leer und trennt den Inhalt strukturiert.
350. Diese Zeile ist leer und trennt den Inhalt strukturiert.
351. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def import_admin_csv('.
352. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db: Session,'.
353. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'csv_bytes: bytes,'.
354. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'creator_id: int,'.
355. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'mode: ADMIN_IMPORT_MODE = "insert_only",'.
356. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'dry_run: bool = True,'.
357. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'batch_size: int = 200,'.
358. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_limit: int = 20,'.
359. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'autocommit: bool = False,'.
360. Diese Zeile enth?lt den konkreten Code/Textabschnitt ') -> AdminCSVImportReport:'.
361. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if mode not in {"insert_only", "update_existing"}:'.
362. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raise ValueError("mode must be 'insert_only' or 'update_existing'")'.
363. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'rows, delimiter = _parse_csv_rows(csv_bytes)'.
364. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'prepared_rows, report = _prepare_rows(rows, mode, preview_limit)'.
365. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.delimiter = delimiter'.
366. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.dry_run = dry_run'.
367. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if report.fatal_error_rows > 0:'.
368. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return report'.
369. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'pending_writes = 0'.
370. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'for payload in prepared_rows:'.
371. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if payload.skip_reason:'.
372. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.skipped += 1'.
373. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'continue'.
374. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'existing = _find_existing_recipe_for_admin(db, payload)'.
375. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if existing and mode == "insert_only":'.
376. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.skipped += 1'.
377. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'continue'.
378. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if existing and mode == "update_existing":'.
379. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not dry_run:'.
380. Diese Zeile enth?lt den konkreten Code/Textabschnitt '_update_recipe_from_payload(db, existing, payload)'.
381. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'pending_writes += 1'.
382. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.updated += 1'.
383. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
384. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not dry_run:'.
385. Diese Zeile enth?lt den konkreten Code/Textabschnitt '_create_recipe_from_payload(db, payload, creator_id)'.
386. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'pending_writes += 1'.
387. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.inserted += 1'.
388. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not dry_run and pending_writes >= batch_size:'.
389. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if autocommit:'.
390. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.commit()'.
391. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
392. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.flush()'.
393. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'pending_writes = 0'.
394. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not dry_run and pending_writes > 0:'.
395. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if autocommit:'.
396. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.commit()'.
397. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
398. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.flush()'.
399. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return report'.
400. Diese Zeile ist leer und trennt den Inhalt strukturiert.
401. Diese Zeile ist leer und trennt den Inhalt strukturiert.
402. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def build_csv_template_bytes() -> bytes:'.
403. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'buffer = io.StringIO()'.
404. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'writer = csv.writer(buffer, delimiter=";")'.
405. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'writer.writerow(CANONICAL_CSV_COLUMNS)'.
406. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'writer.writerow('.
407. Diese Zeile enth?lt den konkreten Code/Textabschnitt '['.
408. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Spaghetti Carbonara",'.
409. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Pasta kochen. Speck anbraten. Mit Ei-Kaese-Mischung verruehren.",'.
410. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Klassische Carbonara mit Ei und Pecorino.",'.
411. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Pasta",'.
412. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"medium",'.
413. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"25",'.
414. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"2 Portionen",'.
415. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"200g Spaghetti | 120g Guanciale | 2 Eier | 50g Pecorino",'.
416. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"https://example.com/carbonara.jpg",'.
417. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin-demo-001",'.
418. Diese Zeile enth?lt den konkreten Code/Textabschnitt ']'.
419. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
420. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'content = buffer.getvalue()'.
421. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return ("\ufeff" + content).encode("utf-8")'.
422. Diese Zeile ist leer und trennt den Inhalt strukturiert.
423. Diese Zeile ist leer und trennt den Inhalt strukturiert.
424. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def build_csv_example_bytes() -> bytes:'.
425. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'buffer = io.StringIO()'.
426. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'writer = csv.writer(buffer, delimiter=";")'.
427. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'writer.writerow(CANONICAL_CSV_COLUMNS)'.
428. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'writer.writerow('.
429. Diese Zeile enth?lt den konkreten Code/Textabschnitt '['.
430. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Linsensuppe",'.
431. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Zwiebeln anschwitzen. Linsen dazugeben. Mit Bruehe kochen.",'.
432. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Herzhafte Suppe fuer kalte Tage.",'.
433. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Suppen",'.
434. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"easy",'.
435. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"35",'.
436. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"4 Portionen",'.
437. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"250g Linsen | 1 Zwiebel | 2 Karotten | 1L Gemuesebruehe",'.
438. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"",'.
439. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin-demo-002",'.
440. Diese Zeile enth?lt den konkreten Code/Textabschnitt ']'.
441. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
442. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'writer.writerow('.
443. Diese Zeile enth?lt den konkreten Code/Textabschnitt '['.
444. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Schneller Obstsalat",'.
445. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Obst schneiden und mit Zitronensaft vermengen.",'.
446. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Frischer Salat mit saisonalem Obst.",'.
447. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Dessert",'.
448. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"easy",'.
449. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"10",'.
450. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"3 Portionen",'.
451. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"[\"2 Aepfel\", \"1 Banane\", \"1 Orange\", \"1 TL Zitronensaft\"]",'.
452. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"https://example.com/obstsalat.jpg",'.
453. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin-demo-003",'.
454. Diese Zeile enth?lt den konkreten Code/Textabschnitt ']'.
455. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
456. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'writer.writerow('.
457. Diese Zeile enth?lt den konkreten Code/Textabschnitt '['.
458. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Ofengemuese",'.
459. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Gemuese schneiden, wuerzen und 30 Minuten backen.",'.
460. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Knackiges Ofengemuese.",'.
461. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"Hauptgericht",'.
462. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"medium",'.
463. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"40",'.
464. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"2 Portionen",'.
465. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"2 Karotten | 1 Zucchini | 1 Paprika | 2 EL Olivenoel",'.
466. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"",'.
467. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"",'.
468. Diese Zeile enth?lt den konkreten Code/Textabschnitt ']'.
469. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
470. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'content = buffer.getvalue()'.
471. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return ("\ufeff" + content).encode("utf-8")'.

## app/routers/admin.py
```python
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import Response as RawResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.csv_import import build_csv_example_bytes, build_csv_template_bytes, import_admin_csv
from app.database import get_db
from app.dependencies import get_admin_user, template_context
from app.i18n import t
from app.models import Recipe, User
from app.rate_limit import key_by_user_or_ip, limiter
from app.services import get_category_stats, import_kochwiki_csv, is_meta_true, set_meta_value
from app.views import redirect, templates

router = APIRouter(tags=["admin"])
settings = get_settings()
logger = logging.getLogger("mealmate.admin")


def admin_dashboard_context(
    request: Request,
    db: Session,
    current_user: User,
    report=None,
    preview_report=None,
    error: str | None = None,
    message: str | None = None,
    import_mode: str = "insert_only",
    import_dry_run: bool = False,
    import_force_with_warnings: bool = False,
):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    recipes = db.scalars(
        select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.creator))
    ).all()
    distinct_category_count, top_categories = get_category_stats(db, limit=10)
    logger.info(
        "category_stats distinct=%s top=%s",
        distinct_category_count,
        top_categories,
    )
    return template_context(
        request,
        current_user,
        users=users,
        recipes=recipes,
        report=report,
        preview_report=preview_report,
        error=error,
        message=message,
        import_mode=import_mode,
        import_dry_run=import_dry_run,
        import_force_with_warnings=import_force_with_warnings,
        distinct_category_count=distinct_category_count,
        top_categories=top_categories,
    )


@router.get("/admin")
def admin_panel(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return templates.TemplateResponse("admin.html", admin_dashboard_context(request, db, current_user))


@router.post("/admin/users/{user_id}/role")
def change_user_role(
    user_id: int,
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    if role not in {"user", "admin"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.role_invalid"))
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.user_not_found"))
    user.role = role
    db.commit()
    return redirect("/admin")


@router.post("/admin/recipes/{recipe_id}/delete")
def delete_recipe_admin(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found"))
    db.delete(recipe)
    db.commit()
    return redirect("/admin")


@router.post("/admin/run-kochwiki-seed")
def run_kochwiki_seed(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    if not settings.enable_kochwiki_seed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.not_found"))
    if is_meta_true(db, "kochwiki_seed_done"):
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, error=t("error.seed_already_done")),
            status_code=status.HTTP_409_CONFLICT,
        )
    recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0
    if recipes_count > 0:
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=t("error.seed_not_empty"),
            ),
            status_code=status.HTTP_409_CONFLICT,
        )
    seed_path = Path(settings.kochwiki_csv_path)
    if not seed_path.exists():
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=f"{t('error.csv_not_found_prefix')}: {seed_path}",
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    report = import_kochwiki_csv(db, seed_path, current_user.id, mode="insert_only")
    if report.errors:
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                report=report,
                error=t("error.seed_finished_errors"),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    set_meta_value(db, "kochwiki_seed_done", "1")
    db.commit()
    return templates.TemplateResponse(
        "admin.html",
        admin_dashboard_context(
            request,
            db,
            current_user,
            report=report,
            message=t("error.seed_success"),
        ),
    )


@router.post("/admin/import-recipes")
@limiter.limit("2/minute", key_func=key_by_user_or_ip)
async def import_recipes_admin(
    request: Request,
    response: Response,
    file: UploadFile | None = File(None),
    insert_only: str | None = Form("on"),
    update_existing: str | None = Form(None),
    dry_run: str | None = Form(None),
    force_with_warnings: str | None = Form(None),
    action: str = Form("preview"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = response
    max_bytes = settings.max_csv_upload_mb * 1024 * 1024
    mode = "update_existing" if update_existing else "insert_only"
    dry_run_flag = bool(dry_run)
    force_warnings_flag = bool(force_with_warnings)
    if insert_only and mode != "update_existing":
        mode = "insert_only"
    try:
        if not file or not file.filename:
            raise ValueError(t("error.csv_upload_required"))
        if not file.filename.lower().endswith(".csv"):
            raise ValueError(t("error.csv_only"))
        raw_bytes = await file.read(max_bytes + 1)
        if len(raw_bytes) > max_bytes:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=t("error.csv_too_large"))
        if not raw_bytes:
            raise ValueError(t("error.csv_empty"))
        preview_report = import_admin_csv(
            db,
            raw_bytes,
            current_user.id,
            mode=mode,
            dry_run=True,
            autocommit=False,
        )
        if action == "preview":
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    message=t("admin.preview_done"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
            )
        if preview_report.fatal_error_rows > 0:
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    error=t("admin.import_blocked_errors"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if dry_run_flag:
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    message=t("admin.dry_run_done"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
            )
        if preview_report.warnings and not force_warnings_flag:
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    error=t("admin.confirm_warnings_required"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        report = import_admin_csv(
            db,
            raw_bytes,
            current_user.id,
            mode=mode,
            dry_run=False,
            autocommit=False,
        )
        db.commit()
        message = t("error.import_finished_insert") if mode == "insert_only" else t("error.import_finished_update")
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                report=report,
                preview_report=report,
                message=message,
                import_mode=mode,
                import_dry_run=dry_run_flag,
                import_force_with_warnings=force_warnings_flag,
            ),
        )
    except (FileNotFoundError, ValueError) as exc:
        db.rollback()
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=str(exc),
                import_mode=mode,
                import_dry_run=dry_run_flag,
                import_force_with_warnings=force_warnings_flag,
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        db.rollback()
        raise


@router.get("/admin/import-template.csv")
def admin_import_template_csv(current_user: User = Depends(get_admin_user)):
    _ = current_user
    content = build_csv_template_bytes()
    headers = {"Content-Disposition": 'attachment; filename="mealmate_import_template.csv"'}
    return RawResponse(content=content, media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/admin/import-example.csv")
def admin_import_example_csv(current_user: User = Depends(get_admin_user)):
    _ = current_user
    content = build_csv_example_bytes()
    headers = {"Content-Disposition": 'attachment; filename="mealmate_import_beispiel.csv"'}
    return RawResponse(content=content, media_type="text/csv; charset=utf-8", headers=headers)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import logging'.
2. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from pathlib import Path'.
3. Diese Zeile ist leer und trennt den Inhalt strukturiert.
4. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, R...'.
5. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from fastapi.responses import Response as RawResponse'.
6. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from sqlalchemy import func, select'.
7. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from sqlalchemy.orm import Session, selectinload'.
8. Diese Zeile ist leer und trennt den Inhalt strukturiert.
9. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.config import get_settings'.
10. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.csv_import import build_csv_example_bytes, build_csv_template_bytes,...'.
11. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.database import get_db'.
12. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.dependencies import get_admin_user, template_context'.
13. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.i18n import t'.
14. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.models import Recipe, User'.
15. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.rate_limit import key_by_user_or_ip, limiter'.
16. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.services import get_category_stats, import_kochwiki_csv, is_meta_tru...'.
17. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.views import redirect, templates'.
18. Diese Zeile ist leer und trennt den Inhalt strukturiert.
19. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'router = APIRouter(tags=["admin"])'.
20. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'settings = get_settings()'.
21. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'logger = logging.getLogger("mealmate.admin")'.
22. Diese Zeile ist leer und trennt den Inhalt strukturiert.
23. Diese Zeile ist leer und trennt den Inhalt strukturiert.
24. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def admin_dashboard_context('.
25. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request: Request,'.
26. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db: Session,'.
27. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user: User,'.
28. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report=None,'.
29. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_report=None,'.
30. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'error: str | None = None,'.
31. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'message: str | None = None,'.
32. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_mode: str = "insert_only",'.
33. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_dry_run: bool = False,'.
34. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_force_with_warnings: bool = False,'.
35. Diese Zeile enth?lt den konkreten Code/Textabschnitt '):'.
36. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'users = db.scalars(select(User).order_by(User.created_at.desc())).all()'.
37. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipes = db.scalars('.
38. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe...'.
39. Diese Zeile enth?lt den konkreten Code/Textabschnitt ').all()'.
40. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'distinct_category_count, top_categories = get_category_stats(db, limit=10)'.
41. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'logger.info('.
42. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"category_stats distinct=%s top=%s",'.
43. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'distinct_category_count,'.
44. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'top_categories,'.
45. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
46. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return template_context('.
47. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
48. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
49. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'users=users,'.
50. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipes=recipes,'.
51. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report=report,'.
52. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_report=preview_report,'.
53. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'error=error,'.
54. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'message=message,'.
55. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_mode=import_mode,'.
56. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_dry_run=import_dry_run,'.
57. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_force_with_warnings=import_force_with_warnings,'.
58. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'distinct_category_count=distinct_category_count,'.
59. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'top_categories=top_categories,'.
60. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
61. Diese Zeile ist leer und trennt den Inhalt strukturiert.
62. Diese Zeile ist leer und trennt den Inhalt strukturiert.
63. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@router.get("/admin")'.
64. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def admin_panel('.
65. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request: Request,'.
66. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db: Session = Depends(get_db),'.
67. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user: User = Depends(get_admin_user),'.
68. Diese Zeile enth?lt den konkreten Code/Textabschnitt '):'.
69. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse("admin.html", admin_dashboard_context(reque...'.
70. Diese Zeile ist leer und trennt den Inhalt strukturiert.
71. Diese Zeile ist leer und trennt den Inhalt strukturiert.
72. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@router.post("/admin/users/{user_id}/role")'.
73. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def change_user_role('.
74. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'user_id: int,'.
75. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'role: str = Form(...),'.
76. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db: Session = Depends(get_db),'.
77. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user: User = Depends(get_admin_user),'.
78. Diese Zeile enth?lt den konkreten Code/Textabschnitt '):'.
79. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if role not in {"user", "admin"}:'.
80. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error....'.
81. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'user = db.scalar(select(User).where(User.id == user_id))'.
82. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not user:'.
83. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.us...'.
84. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'user.role = role'.
85. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.commit()'.
86. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return redirect("/admin")'.
87. Diese Zeile ist leer und trennt den Inhalt strukturiert.
88. Diese Zeile ist leer und trennt den Inhalt strukturiert.
89. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@router.post("/admin/recipes/{recipe_id}/delete")'.
90. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def delete_recipe_admin('.
91. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe_id: int,'.
92. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db: Session = Depends(get_db),'.
93. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user: User = Depends(get_admin_user),'.
94. Diese Zeile enth?lt den konkreten Code/Textabschnitt '):'.
95. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))'.
96. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not recipe:'.
97. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.re...'.
98. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.delete(recipe)'.
99. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.commit()'.
100. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return redirect("/admin")'.
101. Diese Zeile ist leer und trennt den Inhalt strukturiert.
102. Diese Zeile ist leer und trennt den Inhalt strukturiert.
103. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@router.post("/admin/run-kochwiki-seed")'.
104. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def run_kochwiki_seed('.
105. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request: Request,'.
106. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db: Session = Depends(get_db),'.
107. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user: User = Depends(get_admin_user),'.
108. Diese Zeile enth?lt den konkreten Code/Textabschnitt '):'.
109. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not settings.enable_kochwiki_seed:'.
110. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.no...'.
111. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if is_meta_true(db, "kochwiki_seed_done"):'.
112. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
113. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
114. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context(request, db, current_user, error=t("error.seed_alread...'.
115. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status_code=status.HTTP_409_CONFLICT,'.
116. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
117. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0'.
118. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if recipes_count > 0:'.
119. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
120. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
121. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context('.
122. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
123. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
124. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
125. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'error=t("error.seed_not_empty"),'.
126. Diese Zeile enth?lt den konkreten Code/Textabschnitt '),'.
127. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status_code=status.HTTP_409_CONFLICT,'.
128. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
129. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'seed_path = Path(settings.kochwiki_csv_path)'.
130. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not seed_path.exists():'.
131. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
132. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
133. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context('.
134. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
135. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
136. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
137. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'error=f"{t('error.csv_not_found_prefix')}: {seed_path}",'.
138. Diese Zeile enth?lt den konkreten Code/Textabschnitt '),'.
139. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
140. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
141. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report = import_kochwiki_csv(db, seed_path, current_user.id, mode="insert_only")'.
142. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if report.errors:'.
143. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
144. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
145. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context('.
146. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
147. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
148. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
149. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report=report,'.
150. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'error=t("error.seed_finished_errors"),'.
151. Diese Zeile enth?lt den konkreten Code/Textabschnitt '),'.
152. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
153. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
154. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'set_meta_value(db, "kochwiki_seed_done", "1")'.
155. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.commit()'.
156. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
157. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
158. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context('.
159. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
160. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
161. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
162. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report=report,'.
163. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'message=t("error.seed_success"),'.
164. Diese Zeile enth?lt den konkreten Code/Textabschnitt '),'.
165. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
166. Diese Zeile ist leer und trennt den Inhalt strukturiert.
167. Diese Zeile ist leer und trennt den Inhalt strukturiert.
168. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@router.post("/admin/import-recipes")'.
169. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@limiter.limit("2/minute", key_func=key_by_user_or_ip)'.
170. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'async def import_recipes_admin('.
171. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request: Request,'.
172. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'response: Response,'.
173. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'file: UploadFile | None = File(None),'.
174. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'insert_only: str | None = Form("on"),'.
175. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'update_existing: str | None = Form(None),'.
176. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'dry_run: str | None = Form(None),'.
177. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'force_with_warnings: str | None = Form(None),'.
178. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'action: str = Form("preview"),'.
179. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db: Session = Depends(get_db),'.
180. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user: User = Depends(get_admin_user),'.
181. Diese Zeile enth?lt den konkreten Code/Textabschnitt '):'.
182. Diese Zeile enth?lt den konkreten Code/Textabschnitt '_ = response'.
183. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'max_bytes = settings.max_csv_upload_mb * 1024 * 1024'.
184. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'mode = "update_existing" if update_existing else "insert_only"'.
185. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'dry_run_flag = bool(dry_run)'.
186. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'force_warnings_flag = bool(force_with_warnings)'.
187. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if insert_only and mode != "update_existing":'.
188. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'mode = "insert_only"'.
189. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'try:'.
190. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not file or not file.filename:'.
191. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raise ValueError(t("error.csv_upload_required"))'.
192. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not file.filename.lower().endswith(".csv"):'.
193. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raise ValueError(t("error.csv_only"))'.
194. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raw_bytes = await file.read(max_bytes + 1)'.
195. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if len(raw_bytes) > max_bytes:'.
196. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, det...'.
197. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not raw_bytes:'.
198. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raise ValueError(t("error.csv_empty"))'.
199. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_report = import_admin_csv('.
200. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
201. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raw_bytes,'.
202. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user.id,'.
203. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'mode=mode,'.
204. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'dry_run=True,'.
205. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'autocommit=False,'.
206. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
207. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if action == "preview":'.
208. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
209. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
210. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context('.
211. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
212. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
213. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
214. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_report=preview_report,'.
215. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'message=t("admin.preview_done"),'.
216. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_mode=mode,'.
217. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_dry_run=dry_run_flag,'.
218. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_force_with_warnings=force_warnings_flag,'.
219. Diese Zeile enth?lt den konkreten Code/Textabschnitt '),'.
220. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
221. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if preview_report.fatal_error_rows > 0:'.
222. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
223. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
224. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context('.
225. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
226. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
227. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
228. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_report=preview_report,'.
229. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'error=t("admin.import_blocked_errors"),'.
230. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_mode=mode,'.
231. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_dry_run=dry_run_flag,'.
232. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_force_with_warnings=force_warnings_flag,'.
233. Diese Zeile enth?lt den konkreten Code/Textabschnitt '),'.
234. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
235. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
236. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if dry_run_flag:'.
237. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
238. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
239. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context('.
240. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
241. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
242. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
243. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_report=preview_report,'.
244. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'message=t("admin.dry_run_done"),'.
245. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_mode=mode,'.
246. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_dry_run=dry_run_flag,'.
247. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_force_with_warnings=force_warnings_flag,'.
248. Diese Zeile enth?lt den konkreten Code/Textabschnitt '),'.
249. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
250. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if preview_report.warnings and not force_warnings_flag:'.
251. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
252. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
253. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context('.
254. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
255. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
256. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
257. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_report=preview_report,'.
258. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'error=t("admin.confirm_warnings_required"),'.
259. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_mode=mode,'.
260. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_dry_run=dry_run_flag,'.
261. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_force_with_warnings=force_warnings_flag,'.
262. Diese Zeile enth?lt den konkreten Code/Textabschnitt '),'.
263. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
264. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
265. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report = import_admin_csv('.
266. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
267. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raw_bytes,'.
268. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user.id,'.
269. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'mode=mode,'.
270. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'dry_run=False,'.
271. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'autocommit=False,'.
272. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
273. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.commit()'.
274. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'message = t("error.import_finished_insert") if mode == "insert_only" else t("...'.
275. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
276. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
277. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context('.
278. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
279. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
280. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
281. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report=report,'.
282. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'preview_report=report,'.
283. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'message=message,'.
284. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_mode=mode,'.
285. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_dry_run=dry_run_flag,'.
286. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_force_with_warnings=force_warnings_flag,'.
287. Diese Zeile enth?lt den konkreten Code/Textabschnitt '),'.
288. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
289. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'except (FileNotFoundError, ValueError) as exc:'.
290. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.rollback()'.
291. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
292. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.html",'.
293. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_dashboard_context('.
294. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request,'.
295. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db,'.
296. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'current_user,'.
297. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'error=str(exc),'.
298. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_mode=mode,'.
299. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_dry_run=dry_run_flag,'.
300. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_force_with_warnings=force_warnings_flag,'.
301. Diese Zeile enth?lt den konkreten Code/Textabschnitt '),'.
302. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
303. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
304. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'except Exception:'.
305. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.rollback()'.
306. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'raise'.
307. Diese Zeile ist leer und trennt den Inhalt strukturiert.
308. Diese Zeile ist leer und trennt den Inhalt strukturiert.
309. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@router.get("/admin/import-template.csv")'.
310. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def admin_import_template_csv(current_user: User = Depends(get_admin_user)):'.
311. Diese Zeile enth?lt den konkreten Code/Textabschnitt '_ = current_user'.
312. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'content = build_csv_template_bytes()'.
313. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'headers = {"Content-Disposition": 'attachment; filename="mealmate_import_temp...'.
314. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return RawResponse(content=content, media_type="text/csv; charset=utf-8", hea...'.
315. Diese Zeile ist leer und trennt den Inhalt strukturiert.
316. Diese Zeile ist leer und trennt den Inhalt strukturiert.
317. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@router.get("/admin/import-example.csv")'.
318. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def admin_import_example_csv(current_user: User = Depends(get_admin_user)):'.
319. Diese Zeile enth?lt den konkreten Code/Textabschnitt '_ = current_user'.
320. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'content = build_csv_example_bytes()'.
321. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'headers = {"Content-Disposition": 'attachment; filename="mealmate_import_beis...'.
322. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return RawResponse(content=content, media_type="text/csv; charset=utf-8", hea...'.

## app/templates/admin.html
```jinja2
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("admin.title") }}</h1>
  {% if message %}
  <p class="meta">{{ message }}</p>
  {% endif %}
  {% if error %}
  <p class="error">{{ error }}</p>
  {% endif %}
  <p><a href="/admin/submissions">{{ t("submission.admin_queue_link") }}</a></p>
</section>
<section class="panel">
  <h2>{{ t("admin.import_title") }}</h2>
  <div class="stack">
    <h3>{{ t("admin.import_help_title") }}</h3>
    <p class="meta">{{ t("admin.import_help_intro") }}</p>
    <ul>
      <li>{{ t("admin.import_required_columns") }}</li>
      <li>{{ t("admin.import_optional_columns") }}</li>
      <li>{{ t("admin.import_difficulty_values") }}</li>
      <li>{{ t("admin.import_ingredients_example") }}</li>
      <li>{{ t("admin.import_encoding_delimiter") }}</li>
    </ul>
    <div class="actions">
      <a href="/admin/import-template.csv">{{ t("admin.download_template") }}</a>
      <a href="/admin/import-example.csv">{{ t("admin.download_example") }}</a>
    </div>
  </div>
  <form method="post" action="/admin/import-recipes" enctype="multipart/form-data" class="stack">
    <label>{{ t("admin.upload_label") }}
      <input type="file" name="file" accept=".csv" required>
    </label>
    <label class="inline">
      <input type="checkbox" name="insert_only" {% if import_mode == "insert_only" %}checked{% endif %}>
      {{ t("admin.insert_only") }}
    </label>
    <label class="inline">
      <input type="checkbox" name="update_existing" {% if import_mode == "update_existing" %}checked{% endif %}>
      {{ t("admin.update_existing") }}
    </label>
    <label class="inline">
      <input type="checkbox" name="dry_run" {% if import_dry_run %}checked{% endif %}>
      {{ t("admin.dry_run") }}
    </label>
    <label class="inline">
      <input type="checkbox" name="force_with_warnings" {% if import_force_with_warnings %}checked{% endif %}>
      {{ t("admin.force_with_warnings") }}
    </label>
    <p class="meta">{{ t("admin.import_warning_text") }}</p>
    <div class="actions">
      <button type="submit" name="action" value="preview">{{ t("admin.preview_button") }}</button>
      <button type="submit" name="action" value="import">{{ t("admin.start_import") }}</button>
    </div>
  </form>
  {% if preview_report %}
  <h3>{{ t("admin.preview_title") }}</h3>
  <p class="meta">
    {{ t("admin.preview_total_rows") }}: {{ preview_report.total_rows }},
    {{ t("admin.preview_delimiter") }}: {{ preview_report.delimiter }},
    {{ t("admin.preview_fatal_rows") }}: {{ preview_report.fatal_error_rows }}
  </p>
  <p class="meta">
    {{ t("admin.report_inserted") }}: {{ preview_report.inserted }},
    {{ t("admin.report_updated") }}: {{ preview_report.updated }},
    {{ t("admin.report_skipped") }}: {{ preview_report.skipped }},
    {{ t("admin.report_errors") }}: {{ preview_report.errors|length }},
    {{ t("admin.report_warnings") }}: {{ preview_report.warnings|length }}
  </p>
  <table>
    <thead>
      <tr>
        <th>{{ t("admin.preview_row") }}</th>
        <th>{{ t("admin.title_column") }}</th>
        <th>{{ t("home.category") }}</th>
        <th>{{ t("home.difficulty") }}</th>
        <th>{{ t("recipe_form.prep_time") }}</th>
        <th>{{ t("admin.preview_status") }}</th>
        <th>{{ t("admin.preview_notes") }}</th>
      </tr>
    </thead>
    <tbody>
      {% for row in preview_report.preview_rows %}
      <tr>
        <td>{{ row.row_number }}</td>
        <td>{{ row.title }}</td>
        <td>{{ row.category }}</td>
        <td>{{ difficulty_label(row.difficulty) }}</td>
        <td>{{ row.prep_time_minutes }}</td>
        <td>{{ row.status }}</td>
        <td>
          {% if row.errors %}
          {{ row.errors|join("; ") }}
          {% elif row.warnings %}
          {{ row.warnings|join("; ") }}
          {% else %}
          -
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% if preview_report.errors %}
  <h4>{{ t("admin.preview_errors_title") }}</h4>
  <ul>
    {% for item in preview_report.errors %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
  {% endif %}
  {% if preview_report.warnings %}
  <h4>{{ t("admin.preview_warnings_title") }}</h4>
  <ul>
    {% for item in preview_report.warnings %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
  {% endif %}
  {% endif %}
  {% if report %}
  <h3>{{ t("admin.import_result_title") }}</h3>
  <p class="meta">
    {{ t("admin.report_inserted") }}: {{ report.inserted }},
    {{ t("admin.report_updated") }}: {{ report.updated }},
    {{ t("admin.report_skipped") }}: {{ report.skipped }},
    {{ t("admin.report_errors") }}: {{ report.errors|length }},
    {{ t("admin.report_warnings") }}: {{ report.warnings|length }}
  </p>
  {% endif %}
</section>
<section class="panel">
  <h2>{{ t("admin.category_stats_title") }}</h2>
  <p class="meta">{{ t("admin.category_distinct_count") }}: {{ distinct_category_count }}</p>
  <h3>{{ t("admin.category_top") }}</h3>
  <ul>
    {% for category_name, category_count in top_categories %}
    <li>{{ category_name }} ({{ category_count }})</li>
    {% endfor %}
  </ul>
</section>
<section class="panel">
  <h2>{{ t("admin.users") }}</h2>
  <table>
    <thead>
      <tr><th>{{ t("admin.id") }}</th><th>{{ t("admin.email") }}</th><th>{{ t("admin.role") }}</th><th>{{ t("admin.action") }}</th></tr>
    </thead>
    <tbody>
      {% for user in users %}
      <tr>
        <td>{{ user.id }}</td>
        <td>{{ user.email }}</td>
        <td>{{ role_label(user.role) }}</td>
        <td>
          <form method="post" action="/admin/users/{{ user.id }}/role" class="inline">
            <select name="role">
              <option value="user" {% if user.role == "user" %}selected{% endif %}>{{ t("role.user") }}</option>
              <option value="admin" {% if user.role == "admin" %}selected{% endif %}>{{ t("role.admin") }}</option>
            </select>
            <button type="submit">{{ t("admin.save") }}</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
<section class="panel">
  <h2>{{ t("admin.recipes") }}</h2>
  <table>
    <thead>
      <tr><th>{{ t("admin.id") }}</th><th>{{ t("admin.title_column") }}</th><th>{{ t("admin.creator") }}</th><th>{{ t("admin.source") }}</th><th>{{ t("admin.action") }}</th></tr>
    </thead>
    <tbody>
      {% for recipe in recipes %}
      <tr>
        <td>{{ recipe.id }}</td>
        <td><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></td>
        <td>{{ recipe.creator.email }}</td>
        <td>{{ recipe.source }}</td>
        <td>
          <form method="post" action="/admin/recipes/{{ recipe.id }}/delete">
            <button type="submit">{{ t("recipe.delete") }}</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% extends "base.html" %}'.
2. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% block content %}'.
3. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<section class="panel">'.
4. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h1>{{ t("admin.title") }}</h1>'.
5. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% if message %}'.
6. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<p class="meta">{{ message }}</p>'.
7. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endif %}'.
8. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% if error %}'.
9. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<p class="error">{{ error }}</p>'.
10. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endif %}'.
11. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<p><a href="/admin/submissions">{{ t("submission.admin_queue_link") }}</a></p>'.
12. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</section>'.
13. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<section class="panel">'.
14. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h2>{{ t("admin.import_title") }}</h2>'.
15. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<div class="stack">'.
16. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h3>{{ t("admin.import_help_title") }}</h3>'.
17. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<p class="meta">{{ t("admin.import_help_intro") }}</p>'.
18. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<ul>'.
19. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<li>{{ t("admin.import_required_columns") }}</li>'.
20. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<li>{{ t("admin.import_optional_columns") }}</li>'.
21. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<li>{{ t("admin.import_difficulty_values") }}</li>'.
22. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<li>{{ t("admin.import_ingredients_example") }}</li>'.
23. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<li>{{ t("admin.import_encoding_delimiter") }}</li>'.
24. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</ul>'.
25. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<div class="actions">'.
26. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<a href="/admin/import-template.csv">{{ t("admin.download_template") }}</a>'.
27. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<a href="/admin/import-example.csv">{{ t("admin.download_example") }}</a>'.
28. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</div>'.
29. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</div>'.
30. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<form method="post" action="/admin/import-recipes" enctype="multipart/form-da...'.
31. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<label>{{ t("admin.upload_label") }}'.
32. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<input type="file" name="file" accept=".csv" required>'.
33. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</label>'.
34. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<label class="inline">'.
35. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<input type="checkbox" name="insert_only" {% if import_mode == "insert_only" ...'.
36. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.insert_only") }}'.
37. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</label>'.
38. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<label class="inline">'.
39. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<input type="checkbox" name="update_existing" {% if import_mode == "update_ex...'.
40. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.update_existing") }}'.
41. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</label>'.
42. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<label class="inline">'.
43. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<input type="checkbox" name="dry_run" {% if import_dry_run %}checked{% endif %}>'.
44. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.dry_run") }}'.
45. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</label>'.
46. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<label class="inline">'.
47. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<input type="checkbox" name="force_with_warnings" {% if import_force_with_war...'.
48. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.force_with_warnings") }}'.
49. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</label>'.
50. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<p class="meta">{{ t("admin.import_warning_text") }}</p>'.
51. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<div class="actions">'.
52. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<button type="submit" name="action" value="preview">{{ t("admin.preview_butto...'.
53. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<button type="submit" name="action" value="import">{{ t("admin.start_import")...'.
54. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</div>'.
55. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</form>'.
56. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% if preview_report %}'.
57. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h3>{{ t("admin.preview_title") }}</h3>'.
58. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<p class="meta">'.
59. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.preview_total_rows") }}: {{ preview_report.total_rows }},'.
60. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.preview_delimiter") }}: {{ preview_report.delimiter }},'.
61. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.preview_fatal_rows") }}: {{ preview_report.fatal_error_rows }}'.
62. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</p>'.
63. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<p class="meta">'.
64. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.report_inserted") }}: {{ preview_report.inserted }},'.
65. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.report_updated") }}: {{ preview_report.updated }},'.
66. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.report_skipped") }}: {{ preview_report.skipped }},'.
67. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.report_errors") }}: {{ preview_report.errors|length }},'.
68. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.report_warnings") }}: {{ preview_report.warnings|length }}'.
69. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</p>'.
70. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<table>'.
71. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<thead>'.
72. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<tr>'.
73. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<th>{{ t("admin.preview_row") }}</th>'.
74. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<th>{{ t("admin.title_column") }}</th>'.
75. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<th>{{ t("home.category") }}</th>'.
76. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<th>{{ t("home.difficulty") }}</th>'.
77. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<th>{{ t("recipe_form.prep_time") }}</th>'.
78. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<th>{{ t("admin.preview_status") }}</th>'.
79. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<th>{{ t("admin.preview_notes") }}</th>'.
80. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</tr>'.
81. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</thead>'.
82. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<tbody>'.
83. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% for row in preview_report.preview_rows %}'.
84. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<tr>'.
85. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ row.row_number }}</td>'.
86. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ row.title }}</td>'.
87. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ row.category }}</td>'.
88. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ difficulty_label(row.difficulty) }}</td>'.
89. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ row.prep_time_minutes }}</td>'.
90. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ row.status }}</td>'.
91. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>'.
92. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% if row.errors %}'.
93. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ row.errors|join("; ") }}'.
94. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% elif row.warnings %}'.
95. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ row.warnings|join("; ") }}'.
96. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% else %}'.
97. Diese Zeile enth?lt den konkreten Code/Textabschnitt '-'.
98. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endif %}'.
99. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</td>'.
100. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</tr>'.
101. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endfor %}'.
102. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</tbody>'.
103. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</table>'.
104. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% if preview_report.errors %}'.
105. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h4>{{ t("admin.preview_errors_title") }}</h4>'.
106. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<ul>'.
107. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% for item in preview_report.errors %}'.
108. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<li>{{ item }}</li>'.
109. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endfor %}'.
110. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</ul>'.
111. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endif %}'.
112. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% if preview_report.warnings %}'.
113. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h4>{{ t("admin.preview_warnings_title") }}</h4>'.
114. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<ul>'.
115. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% for item in preview_report.warnings %}'.
116. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<li>{{ item }}</li>'.
117. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endfor %}'.
118. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</ul>'.
119. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endif %}'.
120. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endif %}'.
121. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% if report %}'.
122. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h3>{{ t("admin.import_result_title") }}</h3>'.
123. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<p class="meta">'.
124. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.report_inserted") }}: {{ report.inserted }},'.
125. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.report_updated") }}: {{ report.updated }},'.
126. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.report_skipped") }}: {{ report.skipped }},'.
127. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.report_errors") }}: {{ report.errors|length }},'.
128. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{{ t("admin.report_warnings") }}: {{ report.warnings|length }}'.
129. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</p>'.
130. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endif %}'.
131. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</section>'.
132. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<section class="panel">'.
133. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h2>{{ t("admin.category_stats_title") }}</h2>'.
134. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<p class="meta">{{ t("admin.category_distinct_count") }}: {{ distinct_categor...'.
135. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h3>{{ t("admin.category_top") }}</h3>'.
136. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<ul>'.
137. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% for category_name, category_count in top_categories %}'.
138. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<li>{{ category_name }} ({{ category_count }})</li>'.
139. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endfor %}'.
140. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</ul>'.
141. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</section>'.
142. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<section class="panel">'.
143. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h2>{{ t("admin.users") }}</h2>'.
144. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<table>'.
145. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<thead>'.
146. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<tr><th>{{ t("admin.id") }}</th><th>{{ t("admin.email") }}</th><th>{{ t("admi...'.
147. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</thead>'.
148. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<tbody>'.
149. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% for user in users %}'.
150. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<tr>'.
151. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ user.id }}</td>'.
152. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ user.email }}</td>'.
153. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ role_label(user.role) }}</td>'.
154. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>'.
155. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<form method="post" action="/admin/users/{{ user.id }}/role" class="inline">'.
156. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<select name="role">'.
157. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<option value="user" {% if user.role == "user" %}selected{% endif %}>{{ t("ro...'.
158. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<option value="admin" {% if user.role == "admin" %}selected{% endif %}>{{ t("...'.
159. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</select>'.
160. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<button type="submit">{{ t("admin.save") }}</button>'.
161. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</form>'.
162. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</td>'.
163. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</tr>'.
164. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endfor %}'.
165. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</tbody>'.
166. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</table>'.
167. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</section>'.
168. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<section class="panel">'.
169. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<h2>{{ t("admin.recipes") }}</h2>'.
170. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<table>'.
171. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<thead>'.
172. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<tr><th>{{ t("admin.id") }}</th><th>{{ t("admin.title_column") }}</th><th>{{ ...'.
173. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</thead>'.
174. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<tbody>'.
175. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% for recipe in recipes %}'.
176. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<tr>'.
177. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ recipe.id }}</td>'.
178. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></td>'.
179. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ recipe.creator.email }}</td>'.
180. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>{{ recipe.source }}</td>'.
181. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<td>'.
182. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<form method="post" action="/admin/recipes/{{ recipe.id }}/delete">'.
183. Diese Zeile enth?lt den konkreten Code/Textabschnitt '<button type="submit">{{ t("recipe.delete") }}</button>'.
184. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</form>'.
185. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</td>'.
186. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</tr>'.
187. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endfor %}'.
188. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</tbody>'.
189. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</table>'.
190. Diese Zeile enth?lt den konkreten Code/Textabschnitt '</section>'.
191. Diese Zeile enth?lt den konkreten Code/Textabschnitt '{% endblock %}'.

## app/config.py
```python
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    app_name: str = "MealMate"
    app_env: Literal["dev", "prod"] = "dev"
    app_url: AnyHttpUrl = "http://localhost:8000"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    token_expire_minutes: int = 60
    database_url: str = "sqlite:///./mealmate.db"
    allowed_hosts: Annotated[list[str], NoDecode] = ["*"]
    cookie_secure: bool | None = None
    force_https: bool | None = None
    log_level: str = "INFO"
    csrf_cookie_name: str = "csrf_token"
    csrf_header_name: str = "X-CSRF-Token"
    max_upload_mb: int = 4
    max_csv_upload_mb: int = 10
    allowed_image_types: Annotated[list[str], NoDecode] = ["image/png", "image/jpeg", "image/webp"]
    enable_kochwiki_seed: bool = False
    auto_seed_kochwiki: bool = False
    kochwiki_csv_path: str = "rezepte_kochwiki_clean_3713.csv"
    import_download_images: bool = False
    seed_admin_email: str = "admin@mealmate.local"
    seed_admin_password: str = "AdminPass123!"

    @field_validator("allowed_image_types", mode="before")
    @classmethod
    def parse_allowed_image_types(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return [item.strip() for item in value if item.strip()]
        return [item.strip() for item in value.split(",") if item.strip()]

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            hosts = [item.strip() for item in value if item.strip()]
        else:
            hosts = [item.strip() for item in value.split(",") if item.strip()]
        return hosts or ["*"]

    @field_validator("log_level", mode="before")
    @classmethod
    def parse_log_level(cls, value: str) -> str:
        return str(value).strip().upper() or "INFO"

    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.database_url.strip()
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @property
    def is_sqlite(self) -> bool:
        return self.sqlalchemy_database_url.startswith("sqlite")

    @property
    def prod_mode(self) -> bool:
        return self.app_env == "prod"

    @property
    def resolved_cookie_secure(self) -> bool:
        if self.cookie_secure is None:
            return self.prod_mode
        return self.cookie_secure

    @property
    def resolved_force_https(self) -> bool:
        if self.force_https is None:
            return self.prod_mode
        return self.force_https


@lru_cache
def get_settings() -> Settings:
    return Settings()
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from functools import lru_cache'.
2. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from typing import Annotated, Literal'.
3. Diese Zeile ist leer und trennt den Inhalt strukturiert.
4. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from pydantic import AnyHttpUrl, field_validator'.
5. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict'.
6. Diese Zeile ist leer und trennt den Inhalt strukturiert.
7. Diese Zeile ist leer und trennt den Inhalt strukturiert.
8. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'class Settings(BaseSettings):'.
9. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8",...'.
10. Diese Zeile ist leer und trennt den Inhalt strukturiert.
11. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app_name: str = "MealMate"'.
12. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app_env: Literal["dev", "prod"] = "dev"'.
13. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app_url: AnyHttpUrl = "http://localhost:8000"'.
14. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'secret_key: str = "change-me"'.
15. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'algorithm: str = "HS256"'.
16. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'token_expire_minutes: int = 60'.
17. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'database_url: str = "sqlite:///./mealmate.db"'.
18. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'allowed_hosts: Annotated[list[str], NoDecode] = ["*"]'.
19. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'cookie_secure: bool | None = None'.
20. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'force_https: bool | None = None'.
21. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'log_level: str = "INFO"'.
22. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'csrf_cookie_name: str = "csrf_token"'.
23. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'csrf_header_name: str = "X-CSRF-Token"'.
24. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'max_upload_mb: int = 4'.
25. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'max_csv_upload_mb: int = 10'.
26. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'allowed_image_types: Annotated[list[str], NoDecode] = ["image/png", "image/jp...'.
27. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'enable_kochwiki_seed: bool = False'.
28. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'auto_seed_kochwiki: bool = False'.
29. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'kochwiki_csv_path: str = "rezepte_kochwiki_clean_3713.csv"'.
30. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import_download_images: bool = False'.
31. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'seed_admin_email: str = "admin@mealmate.local"'.
32. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'seed_admin_password: str = "AdminPass123!"'.
33. Diese Zeile ist leer und trennt den Inhalt strukturiert.
34. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@field_validator("allowed_image_types", mode="before")'.
35. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@classmethod'.
36. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def parse_allowed_image_types(cls, value: str | list[str]) -> list[str]:'.
37. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if isinstance(value, list):'.
38. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return [item.strip() for item in value if item.strip()]'.
39. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return [item.strip() for item in value.split(",") if item.strip()]'.
40. Diese Zeile ist leer und trennt den Inhalt strukturiert.
41. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@field_validator("allowed_hosts", mode="before")'.
42. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@classmethod'.
43. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:'.
44. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if isinstance(value, list):'.
45. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'hosts = [item.strip() for item in value if item.strip()]'.
46. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'else:'.
47. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'hosts = [item.strip() for item in value.split(",") if item.strip()]'.
48. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return hosts or ["*"]'.
49. Diese Zeile ist leer und trennt den Inhalt strukturiert.
50. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@field_validator("log_level", mode="before")'.
51. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@classmethod'.
52. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def parse_log_level(cls, value: str) -> str:'.
53. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return str(value).strip().upper() or "INFO"'.
54. Diese Zeile ist leer und trennt den Inhalt strukturiert.
55. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@property'.
56. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def sqlalchemy_database_url(self) -> str:'.
57. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'url = self.database_url.strip()'.
58. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if url.startswith("postgres://"):'.
59. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return "postgresql+psycopg://" + url[len("postgres://") :]'.
60. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if url.startswith("postgresql://"):'.
61. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return "postgresql+psycopg://" + url[len("postgresql://") :]'.
62. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return url'.
63. Diese Zeile ist leer und trennt den Inhalt strukturiert.
64. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@property'.
65. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def is_sqlite(self) -> bool:'.
66. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return self.sqlalchemy_database_url.startswith("sqlite")'.
67. Diese Zeile ist leer und trennt den Inhalt strukturiert.
68. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@property'.
69. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def prod_mode(self) -> bool:'.
70. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return self.app_env == "prod"'.
71. Diese Zeile ist leer und trennt den Inhalt strukturiert.
72. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@property'.
73. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def resolved_cookie_secure(self) -> bool:'.
74. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if self.cookie_secure is None:'.
75. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return self.prod_mode'.
76. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return self.cookie_secure'.
77. Diese Zeile ist leer und trennt den Inhalt strukturiert.
78. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@property'.
79. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def resolved_force_https(self) -> bool:'.
80. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if self.force_https is None:'.
81. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return self.prod_mode'.
82. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return self.force_https'.
83. Diese Zeile ist leer und trennt den Inhalt strukturiert.
84. Diese Zeile ist leer und trennt den Inhalt strukturiert.
85. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@lru_cache'.
86. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def get_settings() -> Settings:'.
87. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return Settings()'.

## app/main.py
```python
import logging
import traceback
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import func, select
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.config import get_settings
from app.database import SessionLocal
from app.dependencies import template_context
from app.i18n import t, translate_error_message
from app.logging_config import configure_logging
from app.middleware import CSRFMiddleware, HTTPSRedirectMiddleware, RequestContextMiddleware, SecurityHeadersMiddleware
from app.models import Recipe, User
from app.rate_limit import limiter
from app.routers import admin, auth, recipes, submissions
from app.security import hash_password
from app.services import import_kochwiki_csv, is_meta_true, set_meta_value
from app.views import templates

settings = get_settings()
configure_logging()
logger = logging.getLogger("mealmate.app")

app = FastAPI(title=settings.app_name, version="1.0.0", debug=not settings.prod_mode)


class CacheControlStaticFiles(StaticFiles):
    def __init__(self, *args, cache_control: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_control = cache_control

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if self.cache_control and response.status_code == 200:
            response.headers.setdefault("Cache-Control", self.cache_control)
        return response


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
if settings.allowed_hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)

static_dir = Path("app/static")
static_dir.mkdir(parents=True, exist_ok=True)
static_cache = "public, max-age=3600" if settings.prod_mode else None
app.mount("/static", CacheControlStaticFiles(directory=str(static_dir), cache_control=static_cache), name="static")

app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(submissions.router)
app.include_router(admin.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    accept = request.headers.get("accept", "")
    if exc.status_code == 404 and "text/html" in accept:
        return templates.TemplateResponse(
            "error_404.html",
            template_context(request, None, title=t("error.404_title")),
            status_code=404,
        )
    detail = translate_error_message(exc.detail)
    return JSONResponse({"detail": detail}, status_code=exc.status_code)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "-")
    logger.exception("unhandled_exception request_id=%s path=%s", request_id, request.url.path)
    accept = request.headers.get("accept", "")
    if settings.prod_mode:
        if "text/html" in accept:
            return templates.TemplateResponse(
                "error_500.html",
                template_context(request, None, title=t("error.500_title"), show_trace=False, error_trace=None),
                status_code=500,
            )
        return JSONResponse({"detail": t("error.internal")}, status_code=500)
    trace = traceback.format_exc()
    if "text/html" in accept:
        return templates.TemplateResponse(
            "error_500.html",
            template_context(request, None, title=t("error.500_title"), show_trace=True, error_trace=trace),
            status_code=500,
        )
    return JSONResponse({"detail": t("error.internal"), "trace": trace}, status_code=500)


def _ensure_seed_admin(db) -> User:
    admin = db.scalar(select(User).where(User.role == "admin").order_by(User.id))
    if admin:
        return admin
    fallback_email = settings.seed_admin_email.strip().lower()
    admin = db.scalar(select(User).where(User.email == fallback_email))
    if admin:
        admin.role = "admin"
        db.commit()
        db.refresh(admin)
        return admin
    admin = User(
        email=fallback_email,
        hashed_password=hash_password(settings.seed_admin_password),
        role="admin",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def run_auto_seed_if_enabled() -> None:
    if not settings.enable_kochwiki_seed:
        return
    if not settings.auto_seed_kochwiki:
        return
    db = SessionLocal()
    try:
        if is_meta_true(db, "kochwiki_seed_done"):
            return
        recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0
        if recipes_count > 0:
            return
        csv_path = Path(settings.kochwiki_csv_path)
        if not csv_path.exists():
            return
        admin_user = _ensure_seed_admin(db)
        report = import_kochwiki_csv(db, csv_path, admin_user.id, mode="insert_only")
        if report.errors:
            logger.warning("auto_seed_finished_with_errors errors=%s", len(report.errors))
            return
        set_meta_value(db, "kochwiki_seed_done", "1")
        db.commit()
        logger.info(
            "auto_seed_done inserted=%s updated=%s skipped=%s",
            report.inserted,
            report.updated,
            report.skipped,
        )
    finally:
        db.close()


@app.on_event("startup")
def startup_event() -> None:
    run_auto_seed_if_enabled()


@app.get("/health")
@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import logging'.
2. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'import traceback'.
3. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from pathlib import Path'.
4. Diese Zeile ist leer und trennt den Inhalt strukturiert.
5. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from fastapi import FastAPI, Request'.
6. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from fastapi.responses import JSONResponse'.
7. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from fastapi.staticfiles import StaticFiles'.
8. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from slowapi import _rate_limit_exceeded_handler'.
9. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from slowapi.errors import RateLimitExceeded'.
10. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from slowapi.middleware import SlowAPIMiddleware'.
11. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from sqlalchemy import func, select'.
12. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from starlette.exceptions import HTTPException as StarletteHTTPException'.
13. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from starlette.middleware.trustedhost import TrustedHostMiddleware'.
14. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware'.
15. Diese Zeile ist leer und trennt den Inhalt strukturiert.
16. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.config import get_settings'.
17. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.database import SessionLocal'.
18. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.dependencies import template_context'.
19. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.i18n import t, translate_error_message'.
20. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.logging_config import configure_logging'.
21. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.middleware import CSRFMiddleware, HTTPSRedirectMiddleware, RequestCo...'.
22. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.models import Recipe, User'.
23. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.rate_limit import limiter'.
24. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.routers import admin, auth, recipes, submissions'.
25. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.security import hash_password'.
26. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.services import import_kochwiki_csv, is_meta_true, set_meta_value'.
27. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'from app.views import templates'.
28. Diese Zeile ist leer und trennt den Inhalt strukturiert.
29. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'settings = get_settings()'.
30. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'configure_logging()'.
31. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'logger = logging.getLogger("mealmate.app")'.
32. Diese Zeile ist leer und trennt den Inhalt strukturiert.
33. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app = FastAPI(title=settings.app_name, version="1.0.0", debug=not settings.pr...'.
34. Diese Zeile ist leer und trennt den Inhalt strukturiert.
35. Diese Zeile ist leer und trennt den Inhalt strukturiert.
36. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'class CacheControlStaticFiles(StaticFiles):'.
37. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def __init__(self, *args, cache_control: str | None = None, **kwargs):'.
38. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'super().__init__(*args, **kwargs)'.
39. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'self.cache_control = cache_control'.
40. Diese Zeile ist leer und trennt den Inhalt strukturiert.
41. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'async def get_response(self, path: str, scope):'.
42. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'response = await super().get_response(path, scope)'.
43. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if self.cache_control and response.status_code == 200:'.
44. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'response.headers.setdefault("Cache-Control", self.cache_control)'.
45. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return response'.
46. Diese Zeile ist leer und trennt den Inhalt strukturiert.
47. Diese Zeile ist leer und trennt den Inhalt strukturiert.
48. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.state.limiter = limiter'.
49. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)'.
50. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")'.
51. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if settings.allowed_hosts != ["*"]:'.
52. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)'.
53. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.add_middleware(SlowAPIMiddleware)'.
54. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.add_middleware(CSRFMiddleware)'.
55. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.add_middleware(HTTPSRedirectMiddleware)'.
56. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.add_middleware(SecurityHeadersMiddleware)'.
57. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.add_middleware(RequestContextMiddleware)'.
58. Diese Zeile ist leer und trennt den Inhalt strukturiert.
59. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'static_dir = Path("app/static")'.
60. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'static_dir.mkdir(parents=True, exist_ok=True)'.
61. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'static_cache = "public, max-age=3600" if settings.prod_mode else None'.
62. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.mount("/static", CacheControlStaticFiles(directory=str(static_dir), cache...'.
63. Diese Zeile ist leer und trennt den Inhalt strukturiert.
64. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.include_router(auth.router)'.
65. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.include_router(recipes.router)'.
66. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.include_router(submissions.router)'.
67. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'app.include_router(admin.router)'.
68. Diese Zeile ist leer und trennt den Inhalt strukturiert.
69. Diese Zeile ist leer und trennt den Inhalt strukturiert.
70. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@app.exception_handler(StarletteHTTPException)'.
71. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'async def http_exception_handler(request: Request, exc: StarletteHTTPException):'.
72. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'accept = request.headers.get("accept", "")'.
73. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if exc.status_code == 404 and "text/html" in accept:'.
74. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
75. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error_404.html",'.
76. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'template_context(request, None, title=t("error.404_title")),'.
77. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status_code=404,'.
78. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
79. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'detail = translate_error_message(exc.detail)'.
80. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return JSONResponse({"detail": detail}, status_code=exc.status_code)'.
81. Diese Zeile ist leer und trennt den Inhalt strukturiert.
82. Diese Zeile ist leer und trennt den Inhalt strukturiert.
83. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@app.exception_handler(Exception)'.
84. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'async def unhandled_exception_handler(request: Request, exc: Exception):'.
85. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'request_id = getattr(request.state, "request_id", "-")'.
86. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'logger.exception("unhandled_exception request_id=%s path=%s", request_id, req...'.
87. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'accept = request.headers.get("accept", "")'.
88. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if settings.prod_mode:'.
89. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if "text/html" in accept:'.
90. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
91. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error_500.html",'.
92. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'template_context(request, None, title=t("error.500_title"), show_trace=False,...'.
93. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status_code=500,'.
94. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
95. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return JSONResponse({"detail": t("error.internal")}, status_code=500)'.
96. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'trace = traceback.format_exc()'.
97. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if "text/html" in accept:'.
98. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return templates.TemplateResponse('.
99. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error_500.html",'.
100. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'template_context(request, None, title=t("error.500_title"), show_trace=True, ...'.
101. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'status_code=500,'.
102. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
103. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return JSONResponse({"detail": t("error.internal"), "trace": trace}, status_c...'.
104. Diese Zeile ist leer und trennt den Inhalt strukturiert.
105. Diese Zeile ist leer und trennt den Inhalt strukturiert.
106. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def _ensure_seed_admin(db) -> User:'.
107. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin = db.scalar(select(User).where(User.role == "admin").order_by(User.id))'.
108. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if admin:'.
109. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return admin'.
110. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'fallback_email = settings.seed_admin_email.strip().lower()'.
111. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin = db.scalar(select(User).where(User.email == fallback_email))'.
112. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if admin:'.
113. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin.role = "admin"'.
114. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.commit()'.
115. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.refresh(admin)'.
116. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return admin'.
117. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin = User('.
118. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'email=fallback_email,'.
119. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'hashed_password=hash_password(settings.seed_admin_password),'.
120. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'role="admin",'.
121. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
122. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.add(admin)'.
123. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.commit()'.
124. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.refresh(admin)'.
125. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return admin'.
126. Diese Zeile ist leer und trennt den Inhalt strukturiert.
127. Diese Zeile ist leer und trennt den Inhalt strukturiert.
128. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def run_auto_seed_if_enabled() -> None:'.
129. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not settings.enable_kochwiki_seed:'.
130. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return'.
131. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not settings.auto_seed_kochwiki:'.
132. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return'.
133. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db = SessionLocal()'.
134. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'try:'.
135. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if is_meta_true(db, "kochwiki_seed_done"):'.
136. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return'.
137. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0'.
138. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if recipes_count > 0:'.
139. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return'.
140. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'csv_path = Path(settings.kochwiki_csv_path)'.
141. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if not csv_path.exists():'.
142. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return'.
143. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'admin_user = _ensure_seed_admin(db)'.
144. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report = import_kochwiki_csv(db, csv_path, admin_user.id, mode="insert_only")'.
145. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'if report.errors:'.
146. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'logger.warning("auto_seed_finished_with_errors errors=%s", len(report.errors))'.
147. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return'.
148. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'set_meta_value(db, "kochwiki_seed_done", "1")'.
149. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.commit()'.
150. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'logger.info('.
151. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"auto_seed_done inserted=%s updated=%s skipped=%s",'.
152. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.inserted,'.
153. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.updated,'.
154. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'report.skipped,'.
155. Diese Zeile enth?lt den konkreten Code/Textabschnitt ')'.
156. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'finally:'.
157. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'db.close()'.
158. Diese Zeile ist leer und trennt den Inhalt strukturiert.
159. Diese Zeile ist leer und trennt den Inhalt strukturiert.
160. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@app.on_event("startup")'.
161. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def startup_event() -> None:'.
162. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'run_auto_seed_if_enabled()'.
163. Diese Zeile ist leer und trennt den Inhalt strukturiert.
164. Diese Zeile ist leer und trennt den Inhalt strukturiert.
165. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@app.get("/health")'.
166. Diese Zeile enth?lt den konkreten Code/Textabschnitt '@app.get("/healthz")'.
167. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'def healthcheck():'.
168. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'return {"status": "ok"}'.

## app/i18n/de.py
```python
DE_TEXTS: dict[str, str] = {
    "app.name": "MealMate",
    "nav.discover": "Rezepte entdecken",
    "nav.submit_recipe": "Rezept einreichen",
    "nav.create_recipe": "Rezept erstellen",
    "nav.my_recipes": "Meine Rezepte",
    "nav.my_submissions": "Meine Einreichungen",
    "nav.favorites": "Favoriten",
    "nav.profile": "Mein Profil",
    "nav.admin": "Admin",
    "nav.admin_submissions": "Moderation",
    "nav.login": "Anmelden",
    "nav.register": "Registrieren",
    "nav.logout": "Abmelden",
    "home.title": "Rezepte entdecken",
    "home.title_contains": "Titel enthaelt",
    "home.category": "Kategorie",
    "home.all_categories": "Alle Kategorien",
    "home.difficulty": "Schwierigkeit",
    "home.ingredient": "Zutat",
    "home.per_page": "Pro Seite",
    "home.apply": "Anwenden",
    "sort.newest": "Neueste",
    "sort.oldest": "Aelteste",
    "sort.highest_rated": "Beste Bewertung",
    "sort.lowest_rated": "Schlechteste Bewertung",
    "sort.prep_time": "Zubereitungszeit",
    "pagination.previous": "Zurueck",
    "pagination.next": "Weiter",
    "pagination.first": "Erste",
    "pagination.last": "Letzte",
    "pagination.page": "Seite",
    "pagination.results_range": "Zeige {start}-{end} von {total} Rezepten",
    "difficulty.easy": "Einfach",
    "difficulty.medium": "Mittel",
    "difficulty.hard": "Schwer",
    "role.user": "Nutzer",
    "role.admin": "Administrator",
    "auth.login_title": "Anmelden",
    "auth.register_title": "Registrieren",
    "auth.email": "E-Mail",
    "auth.password": "Passwort",
    "auth.login_button": "Anmelden",
    "auth.register_button": "Konto erstellen",
    "profile.title": "Mein Profil",
    "profile.email": "E-Mail",
    "profile.role": "Rolle",
    "profile.joined": "Registriert am",
    "favorites.title": "Favoriten",
    "favorites.remove": "Favorit entfernen",
    "favorites.empty": "Keine Favoriten gespeichert.",
    "my_recipes.title": "Meine Rezepte",
    "my_recipes.empty": "Noch keine Rezepte vorhanden.",
    "recipe.edit": "Bearbeiten",
    "recipe.delete": "Loeschen",
    "recipe.pdf_download": "PDF herunterladen",
    "recipe.average_rating": "Durchschnittliche Bewertung",
    "recipe.review_count_label": "Bewertungen",
    "recipe.ingredients": "Zutaten",
    "recipe.instructions": "Anleitung",
    "recipe.reviews": "Bewertungen",
    "recipe.rating": "Bewertung",
    "recipe.comment": "Kommentar",
    "recipe.save_review": "Bewertung speichern",
    "recipe.no_ingredients": "Keine Zutaten gespeichert.",
    "recipe.no_reviews": "Noch keine Bewertungen vorhanden.",
    "recipe.no_results": "Keine Rezepte gefunden.",
    "recipe.rating_short": "Bewertung",
    "recipe_form.create_title": "Rezept erstellen",
    "recipe_form.edit_title": "Rezept bearbeiten",
    "recipe_form.title": "Titel",
    "recipe_form.title_image_url": "Titelbild-URL",
    "recipe_form.description": "Beschreibung",
    "recipe_form.instructions": "Anleitung",
    "recipe_form.category": "Kategorie",
    "recipe_form.new_category_option": "Neue Kategorie...",
    "recipe_form.new_category_label": "Neue Kategorie",
    "recipe_form.prep_time": "Zubereitungszeit (Minuten)",
    "recipe_form.difficulty": "Schwierigkeit",
    "recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",
    "recipe_form.optional_image": "Optionales Bild",
    "recipe_form.save": "Speichern",
    "recipe_form.create": "Erstellen",
    "submission.submit_title": "Rezept einreichen",
    "submission.submit_hint": "Einreichungen werden vor der Veroeffentlichung durch das Admin-Team geprueft.",
    "submission.submitter_email": "Kontakt-E-Mail (optional)",
    "submission.title": "Titel",
    "submission.description": "Beschreibung",
    "submission.instructions": "Anleitung",
    "submission.category": "Kategorie",
    "submission.new_category_option": "Neue Kategorie...",
    "submission.new_category_label": "Neue Kategorie",
    "submission.difficulty": "Schwierigkeit",
    "submission.prep_time": "Zubereitungszeit (Minuten, optional)",
    "submission.servings": "Portionen (optional)",
    "submission.ingredients": "Zutaten (Format: name|menge|gramm)",
    "submission.image_optional": "Optionales Bild",
    "submission.submit_button": "Zur Pruefung einreichen",
    "submission.default_description": "Rezept-Einreichung",
    "submission.thank_you": "Vielen Dank! Dein Rezept wurde eingereicht und wird geprueft.",
    "submission.my_title": "Meine Einreichungen",
    "submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",
    "submission.my_empty": "Du hast noch keine Einreichungen.",
    "submission.admin_note": "Admin-Notiz",
    "submission.status_pending": "Ausstehend",
    "submission.status_approved": "Freigegeben",
    "submission.status_rejected": "Abgelehnt",
    "submission.status_all": "Alle",
    "submission.admin_queue_title": "Moderations-Warteschlange",
    "submission.status_filter": "Status",
    "submission.stats_pending": "Ausstehend",
    "submission.stats_approved": "Freigegeben",
    "submission.stats_rejected": "Abgelehnt",
    "submission.table_date": "Datum",
    "submission.table_title": "Titel",
    "submission.table_submitter": "Einreicher",
    "submission.table_status": "Status",
    "submission.table_action": "Aktion",
    "submission.open_detail": "Details",
    "submission.admin_empty": "Keine Einreichungen gefunden.",
    "submission.admin_detail_title": "Einreichung",
    "submission.back_to_queue": "Zurueck zur Warteschlange",
    "submission.preview": "Vorschau",
    "submission.edit_submission": "Einreichung bearbeiten",
    "submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",
    "submission.save_changes": "Aenderungen speichern",
    "submission.moderation_actions": "Moderations-Aktionen",
    "submission.optional_admin_note": "Admin-Notiz (optional)",
    "submission.approve_button": "Freigeben",
    "submission.reject_reason": "Ablehnungsgrund",
    "submission.reject_button": "Ablehnen",
    "submission.approved": "Einreichung wurde freigegeben.",
    "submission.rejected": "Einreichung wurde abgelehnt.",
    "submission.updated": "Einreichung wurde aktualisiert.",
    "submission.image_deleted": "Bild wurde entfernt.",
    "submission.image_primary": "Hauptbild wurde gesetzt.",
    "submission.admin_queue_link": "Zur Moderations-Warteschlange",
    "submission.guest": "Gast",
    "images.title": "Bilder",
    "images.new_file": "Neue Bilddatei",
    "images.set_primary": "Als Hauptbild setzen",
    "images.upload": "Bild hochladen",
    "images.primary": "Hauptbild",
    "images.delete": "Loeschen",
    "images.empty": "Noch keine Bilder vorhanden.",
    "favorite.add": "Zu Favoriten",
    "favorite.remove": "Aus Favoriten entfernen",
    "admin.title": "Admin-Bereich",
    "admin.seed_title": "KochWiki-Seed (einmalig)",
    "admin.csv_path": "CSV-Pfad",
    "admin.seed_done": "Seed-Status: bereits ausgefuehrt.",
    "admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",
    "admin.import_title": "CSV manuell importieren",
    "admin.import_help_title": "CSV-Format Hilfe",
    "admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import stabil und ohne Duplikate laeuft.",
    "admin.import_required_columns": "Pflichtspalten: title, instructions",
    "admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty, prep_time_minutes, servings_text, ingredients, image_url, source_uuid",
    "admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",
    "admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise Salz oder JSON-Liste",
    "admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' (',' als Fallback)",
    "admin.download_template": "CSV Template herunterladen",
    "admin.download_example": "CSV Beispiel herunterladen",
    "admin.upload_label": "CSV-Upload",
    "admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",
    "admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",
    "admin.dry_run": "Nur pruefen (Dry Run)",
    "admin.force_with_warnings": "Trotz Warnungen fortsetzen",
    "admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren, wenn bewusst gewuenscht.",
    "admin.preview_button": "Vorschau erstellen",
    "admin.preview_done": "Vorschau wurde erstellt.",
    "admin.preview_title": "Import-Vorschau",
    "admin.preview_total_rows": "Gesamtzeilen",
    "admin.preview_delimiter": "Erkannter Delimiter",
    "admin.preview_fatal_rows": "Zeilen mit Fehlern",
    "admin.preview_row": "Zeile",
    "admin.preview_status": "Status",
    "admin.preview_notes": "Hinweise",
    "admin.preview_errors_title": "Fehlerliste",
    "admin.preview_warnings_title": "Warnungsliste",
    "admin.import_result_title": "Import-Ergebnis",
    "admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften Zeilen.",
    "admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortsetzen', um den Import zu starten.",
    "admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",
    "admin.start_import": "Import starten",
    "admin.report_inserted": "Neu",
    "admin.report_updated": "Aktualisiert",
    "admin.report_skipped": "Uebersprungen",
    "admin.report_errors": "Fehler",
    "admin.report_warnings": "Warnungen",
    "admin.users": "Nutzer",
    "admin.recipes": "Rezepte",
    "admin.category_stats_title": "Kategorien-Status",
    "admin.category_distinct_count": "Anzahl eindeutiger Kategorien",
    "admin.category_top": "Top 10 Kategorien",
    "admin.id": "ID",
    "admin.email": "E-Mail",
    "admin.role": "Rolle",
    "admin.action": "Aktion",
    "admin.save": "Speichern",
    "admin.title_column": "Titel",
    "admin.creator": "Ersteller",
    "admin.source": "Quelle",
    "error.404_title": "404 - Seite nicht gefunden",
    "error.404_text": "Die angeforderte Seite existiert nicht oder wurde verschoben.",
    "error.500_title": "500 - Interner Fehler",
    "error.500_text": "Beim Verarbeiten der Anfrage ist ein unerwarteter Fehler aufgetreten.",
    "error.home_link": "Zur Startseite",
    "error.trace": "Stacktrace (nur Dev)",
    "error.auth_required": "Anmeldung erforderlich.",
    "error.admin_required": "Administratorrechte erforderlich.",
    "error.invalid_credentials": "Ungueltige Zugangsdaten.",
    "error.email_registered": "Diese E-Mail ist bereits registriert.",
    "error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",
    "error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",
    "error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",
    "error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",
    "error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",
    "error.user_not_found": "Nutzer nicht gefunden.",
    "error.recipe_not_found": "Rezept nicht gefunden.",
    "error.submission_not_found": "Einreichung nicht gefunden.",
    "error.review_not_found": "Bewertung nicht gefunden.",
    "error.image_not_found": "Bild nicht gefunden.",
    "error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",
    "error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",
    "error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",
    "error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",
    "error.title_instructions_required": "Titel und Anleitung sind erforderlich.",
    "error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",
    "error.no_image_url": "Keine Bild-URL verfuegbar.",
    "error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",
    "error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",
    "error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",
    "error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",
    "error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",
    "error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",
    "error.csv_only": "Es sind nur CSV-Uploads erlaubt.",
    "error.csv_too_large": "CSV-Upload ist zu gross.",
    "error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",
    "error.csv_not_found_prefix": "CSV-Datei nicht gefunden",
    "error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",
    "error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",
    "error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",
    "error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",
    "error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",
    "error.internal": "Interner Serverfehler.",
    "error.not_found": "Ressource nicht gefunden.",
    "error.field_int": "{field} muss eine ganze Zahl sein.",
    "error.field_positive": "{field} muss groesser als null sein.",
    "error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",
    "error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",
    "error.webp_signature": "Ungueltige WEBP-Dateisignatur.",
    "error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",
    "error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",
    "error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",
    "error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",
}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'DE_TEXTS: dict[str, str] = {'.
2. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"app.name": "MealMate",'.
3. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.discover": "Rezepte entdecken",'.
4. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.submit_recipe": "Rezept einreichen",'.
5. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.create_recipe": "Rezept erstellen",'.
6. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.my_recipes": "Meine Rezepte",'.
7. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.my_submissions": "Meine Einreichungen",'.
8. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.favorites": "Favoriten",'.
9. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.profile": "Mein Profil",'.
10. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.admin": "Admin",'.
11. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.admin_submissions": "Moderation",'.
12. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.login": "Anmelden",'.
13. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.register": "Registrieren",'.
14. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"nav.logout": "Abmelden",'.
15. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"home.title": "Rezepte entdecken",'.
16. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"home.title_contains": "Titel enthaelt",'.
17. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"home.category": "Kategorie",'.
18. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"home.all_categories": "Alle Kategorien",'.
19. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"home.difficulty": "Schwierigkeit",'.
20. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"home.ingredient": "Zutat",'.
21. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"home.per_page": "Pro Seite",'.
22. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"home.apply": "Anwenden",'.
23. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"sort.newest": "Neueste",'.
24. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"sort.oldest": "Aelteste",'.
25. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"sort.highest_rated": "Beste Bewertung",'.
26. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"sort.lowest_rated": "Schlechteste Bewertung",'.
27. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"sort.prep_time": "Zubereitungszeit",'.
28. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"pagination.previous": "Zurueck",'.
29. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"pagination.next": "Weiter",'.
30. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"pagination.first": "Erste",'.
31. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"pagination.last": "Letzte",'.
32. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"pagination.page": "Seite",'.
33. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"pagination.results_range": "Zeige {start}-{end} von {total} Rezepten",'.
34. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"difficulty.easy": "Einfach",'.
35. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"difficulty.medium": "Mittel",'.
36. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"difficulty.hard": "Schwer",'.
37. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"role.user": "Nutzer",'.
38. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"role.admin": "Administrator",'.
39. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"auth.login_title": "Anmelden",'.
40. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"auth.register_title": "Registrieren",'.
41. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"auth.email": "E-Mail",'.
42. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"auth.password": "Passwort",'.
43. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"auth.login_button": "Anmelden",'.
44. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"auth.register_button": "Konto erstellen",'.
45. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"profile.title": "Mein Profil",'.
46. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"profile.email": "E-Mail",'.
47. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"profile.role": "Rolle",'.
48. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"profile.joined": "Registriert am",'.
49. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"favorites.title": "Favoriten",'.
50. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"favorites.remove": "Favorit entfernen",'.
51. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"favorites.empty": "Keine Favoriten gespeichert.",'.
52. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"my_recipes.title": "Meine Rezepte",'.
53. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
54. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.edit": "Bearbeiten",'.
55. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.delete": "Loeschen",'.
56. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.pdf_download": "PDF herunterladen",'.
57. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.average_rating": "Durchschnittliche Bewertung",'.
58. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.review_count_label": "Bewertungen",'.
59. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.ingredients": "Zutaten",'.
60. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.instructions": "Anleitung",'.
61. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.reviews": "Bewertungen",'.
62. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.rating": "Bewertung",'.
63. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.comment": "Kommentar",'.
64. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.save_review": "Bewertung speichern",'.
65. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
66. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
67. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.no_results": "Keine Rezepte gefunden.",'.
68. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe.rating_short": "Bewertung",'.
69. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.create_title": "Rezept erstellen",'.
70. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.edit_title": "Rezept bearbeiten",'.
71. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.title": "Titel",'.
72. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.title_image_url": "Titelbild-URL",'.
73. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.description": "Beschreibung",'.
74. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.instructions": "Anleitung",'.
75. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.category": "Kategorie",'.
76. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.new_category_option": "Neue Kategorie...",'.
77. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.new_category_label": "Neue Kategorie",'.
78. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
79. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.difficulty": "Schwierigkeit",'.
80. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
81. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.optional_image": "Optionales Bild",'.
82. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.save": "Speichern",'.
83. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"recipe_form.create": "Erstellen",'.
84. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.submit_title": "Rezept einreichen",'.
85. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.submit_hint": "Einreichungen werden vor der Veroeffentlichung dur...'.
86. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
87. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.title": "Titel",'.
88. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.description": "Beschreibung",'.
89. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.instructions": "Anleitung",'.
90. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.category": "Kategorie",'.
91. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.new_category_option": "Neue Kategorie...",'.
92. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.new_category_label": "Neue Kategorie",'.
93. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.difficulty": "Schwierigkeit",'.
94. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
95. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.servings": "Portionen (optional)",'.
96. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
97. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.image_optional": "Optionales Bild",'.
98. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.submit_button": "Zur Pruefung einreichen",'.
99. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.default_description": "Rezept-Einreichung",'.
100. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.thank_you": "Vielen Dank! Dein Rezept wurde eingereicht und wird ...'.
101. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.my_title": "Meine Einreichungen",'.
102. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und w...'.
103. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
104. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.admin_note": "Admin-Notiz",'.
105. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.status_pending": "Ausstehend",'.
106. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.status_approved": "Freigegeben",'.
107. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.status_rejected": "Abgelehnt",'.
108. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.status_all": "Alle",'.
109. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.admin_queue_title": "Moderations-Warteschlange",'.
110. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.status_filter": "Status",'.
111. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.stats_pending": "Ausstehend",'.
112. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.stats_approved": "Freigegeben",'.
113. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.stats_rejected": "Abgelehnt",'.
114. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.table_date": "Datum",'.
115. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.table_title": "Titel",'.
116. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.table_submitter": "Einreicher",'.
117. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.table_status": "Status",'.
118. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.table_action": "Aktion",'.
119. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.open_detail": "Details",'.
120. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
121. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.admin_detail_title": "Einreichung",'.
122. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
123. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.preview": "Vorschau",'.
124. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.edit_submission": "Einreichung bearbeiten",'.
125. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
126. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.save_changes": "Aenderungen speichern",'.
127. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.moderation_actions": "Moderations-Aktionen",'.
128. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
129. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.approve_button": "Freigeben",'.
130. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.reject_reason": "Ablehnungsgrund",'.
131. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.reject_button": "Ablehnen",'.
132. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.approved": "Einreichung wurde freigegeben.",'.
133. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.rejected": "Einreichung wurde abgelehnt.",'.
134. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.updated": "Einreichung wurde aktualisiert.",'.
135. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.image_deleted": "Bild wurde entfernt.",'.
136. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
137. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
138. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"submission.guest": "Gast",'.
139. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"images.title": "Bilder",'.
140. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"images.new_file": "Neue Bilddatei",'.
141. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"images.set_primary": "Als Hauptbild setzen",'.
142. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"images.upload": "Bild hochladen",'.
143. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"images.primary": "Hauptbild",'.
144. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"images.delete": "Loeschen",'.
145. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"images.empty": "Noch keine Bilder vorhanden.",'.
146. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"favorite.add": "Zu Favoriten",'.
147. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"favorite.remove": "Aus Favoriten entfernen",'.
148. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.title": "Admin-Bereich",'.
149. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.seed_title": "KochWiki-Seed (einmalig)",'.
150. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.csv_path": "CSV-Pfad",'.
151. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.seed_done": "Seed-Status: bereits ausgefuehrt.",'.
152. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",'.
153. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_title": "CSV manuell importieren",'.
154. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_help_title": "CSV-Format Hilfe",'.
155. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit de...'.
156. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_required_columns": "Pflichtspalten: title, instructions",'.
157. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_optional_columns": "Empfohlene Spalten: description, category, ...'.
158. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",'.
159. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl...'.
160. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardma...'.
161. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.download_template": "CSV Template herunterladen",'.
162. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.download_example": "CSV Beispiel herunterladen",'.
163. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.upload_label": "CSV-Upload",'.
164. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",'.
165. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehl...'.
166. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.dry_run": "Nur pruefen (Dry Run)",'.
167. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.force_with_warnings": "Trotz Warnungen fortsetzen",'.
168. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur a...'.
169. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_button": "Vorschau erstellen",'.
170. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_done": "Vorschau wurde erstellt.",'.
171. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_title": "Import-Vorschau",'.
172. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_total_rows": "Gesamtzeilen",'.
173. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_delimiter": "Erkannter Delimiter",'.
174. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_fatal_rows": "Zeilen mit Fehlern",'.
175. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_row": "Zeile",'.
176. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_status": "Status",'.
177. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_notes": "Hinweise",'.
178. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_errors_title": "Fehlerliste",'.
179. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.preview_warnings_title": "Warnungsliste",'.
180. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_result_title": "Import-Ergebnis",'.
181. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die feh...'.
182. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnung...'.
183. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieb...'.
184. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.start_import": "Import starten",'.
185. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.report_inserted": "Neu",'.
186. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.report_updated": "Aktualisiert",'.
187. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.report_skipped": "Uebersprungen",'.
188. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.report_errors": "Fehler",'.
189. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.report_warnings": "Warnungen",'.
190. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.users": "Nutzer",'.
191. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.recipes": "Rezepte",'.
192. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.category_stats_title": "Kategorien-Status",'.
193. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.category_distinct_count": "Anzahl eindeutiger Kategorien",'.
194. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.category_top": "Top 10 Kategorien",'.
195. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.id": "ID",'.
196. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.email": "E-Mail",'.
197. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.role": "Rolle",'.
198. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.action": "Aktion",'.
199. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.save": "Speichern",'.
200. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.title_column": "Titel",'.
201. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.creator": "Ersteller",'.
202. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"admin.source": "Quelle",'.
203. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.404_title": "404 - Seite nicht gefunden",'.
204. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.404_text": "Die angeforderte Seite existiert nicht oder wurde verschob...'.
205. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.500_title": "500 - Interner Fehler",'.
206. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.500_text": "Beim Verarbeiten der Anfrage ist ein unerwarteter Fehler a...'.
207. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.home_link": "Zur Startseite",'.
208. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.trace": "Stacktrace (nur Dev)",'.
209. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.auth_required": "Anmeldung erforderlich.",'.
210. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.admin_required": "Administratorrechte erforderlich.",'.
211. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.invalid_credentials": "Ungueltige Zugangsdaten.",'.
212. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.email_registered": "Diese E-Mail ist bereits registriert.",'.
213. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalt...'.
214. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben e...'.
215. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
216. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen ent...'.
217. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
218. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.user_not_found": "Nutzer nicht gefunden.",'.
219. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.recipe_not_found": "Rezept nicht gefunden.",'.
220. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.submission_not_found": "Einreichung nicht gefunden.",'.
221. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.review_not_found": "Bewertung nicht gefunden.",'.
222. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.image_not_found": "Bild nicht gefunden.",'.
223. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
224. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreic...'.
225. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
226. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
227. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
228. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https://...'.
229. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
230. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
231. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen m...'.
232. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
233. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wur...'.
234. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und ...'.
235. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
236. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
237. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
238. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
239. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
240. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
241. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' a...'.
242. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.submission_already_published": "Diese Einreichung wurde bereits veroef...'.
243. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeb...'.
244. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
245. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.internal": "Interner Serverfehler.",'.
246. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.not_found": "Ressource nicht gefunden.",'.
247. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
248. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.field_positive": "{field} muss groesser als null sein.",'.
249. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
250. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
251. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
252. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
253. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein guelti...'.
254. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
255. Diese Zeile enth?lt den konkreten Code/Textabschnitt '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
256. Diese Zeile enth?lt den konkreten Code/Textabschnitt '}'.

## .env.example
```dotenv
APP_NAME=MealMate
APP_ENV=dev
APP_URL=http://localhost:8000
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=60
# DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/mealmate
DATABASE_URL=sqlite:///./mealmate.db
ALLOWED_HOSTS=*
COOKIE_SECURE=0
FORCE_HTTPS=0
LOG_LEVEL=INFO
CSRF_COOKIE_NAME=csrf_token
CSRF_HEADER_NAME=X-CSRF-Token
MAX_UPLOAD_MB=4
MAX_CSV_UPLOAD_MB=10
ALLOWED_IMAGE_TYPES=image/png,image/jpeg,image/webp
ENABLE_KOCHWIKI_SEED=0
AUTO_SEED_KOCHWIKI=0
KOCHWIKI_CSV_PATH=rezepte_kochwiki_clean_3713.csv
IMPORT_DOWNLOAD_IMAGES=0
SEED_ADMIN_EMAIL=admin@mealmate.local
SEED_ADMIN_PASSWORD=AdminPass123!
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'APP_NAME=MealMate'.
2. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'APP_ENV=dev'.
3. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'APP_URL=http://localhost:8000'.
4. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'SECRET_KEY=change-this-in-production'.
5. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ALGORITHM=HS256'.
6. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'TOKEN_EXPIRE_MINUTES=60'.
7. Diese Zeile enth?lt den konkreten Code/Textabschnitt '# DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/mealmate'.
8. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'DATABASE_URL=sqlite:///./mealmate.db'.
9. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ALLOWED_HOSTS=*'.
10. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'COOKIE_SECURE=0'.
11. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'FORCE_HTTPS=0'.
12. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'LOG_LEVEL=INFO'.
13. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'CSRF_COOKIE_NAME=csrf_token'.
14. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'CSRF_HEADER_NAME=X-CSRF-Token'.
15. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'MAX_UPLOAD_MB=4'.
16. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'MAX_CSV_UPLOAD_MB=10'.
17. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ALLOWED_IMAGE_TYPES=image/png,image/jpeg,image/webp'.
18. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ENABLE_KOCHWIKI_SEED=0'.
19. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'AUTO_SEED_KOCHWIKI=0'.
20. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'KOCHWIKI_CSV_PATH=rezepte_kochwiki_clean_3713.csv'.
21. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'IMPORT_DOWNLOAD_IMAGES=0'.
22. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'SEED_ADMIN_EMAIL=admin@mealmate.local'.
23. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'SEED_ADMIN_PASSWORD=AdminPass123!'.

## README_CSV_IMPORT.md
```markdown
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
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt den konkreten Code/Textabschnitt '# MealMate CSV Import'.
2. Diese Zeile ist leer und trennt den Inhalt strukturiert.
3. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## Zweck'.
4. Diese Zeile ist leer und trennt den Inhalt strukturiert.
5. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Dieses Dokument beschreibt den manuellen Admin-CSV-Import fuer neue Rezeptpak...'.
6. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Die KochWiki-Seed-Logik ist standardmaessig deaktiviert und wird nicht fuer d...'.
7. Diese Zeile ist leer und trennt den Inhalt strukturiert.
8. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## CSV Spezifikation (kanonisch)'.
9. Diese Zeile ist leer und trennt den Inhalt strukturiert.
10. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Encoding: 'utf-8-sig''.
11. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Delimiter: ';' (',' wird als Fallback akzeptiert)'.
12. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Pflichtspalten:'.
13. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'title''.
14. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'instructions''.
15. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Empfohlene Spalten:'.
16. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'description''.
17. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'category''.
18. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'difficulty' ('easy|medium|hard')'.
19. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'prep_time_minutes' (Integer > 0)'.
20. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'servings_text''.
21. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'ingredients''.
22. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'image_url' (nur URL speichern, kein Download)'.
23. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'source_uuid' (fuer eindeutige Zuordnung)'.
24. Diese Zeile ist leer und trennt den Inhalt strukturiert.
25. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## Ingredients Format'.
26. Diese Zeile ist leer und trennt den Inhalt strukturiert.
27. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Akzeptiert werden beide Varianten:'.
28. Diese Zeile ist leer und trennt den Inhalt strukturiert.
29. Diese Zeile enth?lt den konkreten Code/Textabschnitt '1. Pipe-Liste:'.
30. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- '2 Eier | 200g Mehl | 1 Prise Salz''.
31. Diese Zeile enth?lt den konkreten Code/Textabschnitt '2. JSON-Liste:'.
32. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- '["2 Eier", "200g Mehl", "1 Prise Salz"]''.
33. Diese Zeile ist leer und trennt den Inhalt strukturiert.
34. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## Import Regeln'.
35. Diese Zeile ist leer und trennt den Inhalt strukturiert.
36. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Default: 'INSERT ONLY' (nur neue Rezepte)'.
37. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Optional: 'UPDATE EXISTING' (nur bewusst aktivieren)'.
38. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Dry Run verfuegbar: Validierung und Vorschau ohne DB-Schreibvorgaenge'.
39. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Dedup:'.
40. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- zuerst ueber 'source_uuid''.
41. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- fallback ueber normalisierte Kombination aus 'title + category + instructio...'.
42. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Kategorie wird normalisiert (trim, '_' -> Leerzeichen, Mehrfachspaces reduz...'.
43. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Schwierigkeit wird intern auf 'easy|medium|hard' normalisiert'.
44. Diese Zeile ist leer und trennt den Inhalt strukturiert.
45. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## Admin Workflow'.
46. Diese Zeile ist leer und trennt den Inhalt strukturiert.
47. Diese Zeile enth?lt den konkreten Code/Textabschnitt '1. Im Admin Panel den Bereich 'CSV manuell importieren' oeffnen.'.
48. Diese Zeile enth?lt den konkreten Code/Textabschnitt '2. Optional 'CSV Template herunterladen' oder 'CSV Beispiel herunterladen'.'.
49. Diese Zeile enth?lt den konkreten Code/Textabschnitt '3. Datei hochladen.'.
50. Diese Zeile enth?lt den konkreten Code/Textabschnitt '4. Optionen setzen:'.
51. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'Nur neue hinzufuegen' (Standard)'.
52. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'Existierende aktualisieren' (nur bewusst)'.
53. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'Nur pruefen (Dry Run)''.
54. Diese Zeile enth?lt den konkreten Code/Textabschnitt '5. 'Vorschau erstellen' klicken.'.
55. Diese Zeile enth?lt den konkreten Code/Textabschnitt '6. Vorschau/Fehler/Warnungen pruefen.'.
56. Diese Zeile enth?lt den konkreten Code/Textabschnitt '7. Fuer echten Import 'Import starten' klicken.'.
57. Diese Zeile enth?lt den konkreten Code/Textabschnitt '8. Bei Warnungen optional 'Trotz Warnungen fortsetzen' setzen.'.
58. Diese Zeile ist leer und trennt den Inhalt strukturiert.
59. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## Haeufige Fehler'.
60. Diese Zeile ist leer und trennt den Inhalt strukturiert.
61. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Falsches Encoding:'.
62. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Datei muss als 'utf-8-sig' gespeichert sein.'.
63. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Falscher Delimiter:'.
64. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Standard ist ';'.'.
65. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Ungueltige Difficulty:'.
66. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- nur 'easy', 'medium', 'hard'.'.
67. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Fehlende Pflichtfelder:'.
68. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- 'title' oder 'instructions' fehlt.'.
69. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Ungueltige 'prep_time_minutes':'.
70. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- muss eine positive ganze Zahl sein.'.

## README_RUNBOOK.md
```markdown
# MealMate Runbook

Dieses Runbook zeigt Setup, Start und einen durchgehenden Demo-Flow inklusive Security-Smoketests.

## 1) Lokales Setup (venv)

```bash
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
py -m alembic -c alembic.ini upgrade head
py scripts/seed_admin.py
py -m uvicorn app.main:app --reload
```

Danach:
- App: `http://localhost:8000`
- Healthcheck: `http://localhost:8000/healthz`
- Admin: `admin@mealmate.local` / `AdminPass123!`

## 2) Lokales Setup mit Docker

```bash
docker compose up --build
```

Danach:
- App: `http://localhost:8000`
- Postgres: `localhost:5432`
- Healthcheck: `http://localhost:8000/healthz`

## 3) ENV Beispiele

### Dev (SQLite)

```dotenv
APP_ENV=dev
APP_URL=http://localhost:8000
SECRET_KEY=change-me-dev
DATABASE_URL=sqlite:///./mealmate.db
ALLOWED_HOSTS=*
COOKIE_SECURE=0
FORCE_HTTPS=0
ENABLE_KOCHWIKI_SEED=0
AUTO_SEED_KOCHWIKI=0
```

### Prod (Postgres)

```dotenv
APP_ENV=prod
APP_URL=https://mealmate.example.com
SECRET_KEY=<lange-zufaellige-zeichenkette>
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname
ALLOWED_HOSTS=mealmate.example.com
COOKIE_SECURE=1
FORCE_HTTPS=1
ENABLE_KOCHWIKI_SEED=0
AUTO_SEED_KOCHWIKI=0
```

## 4) Demo Flow (End-to-End)

1. Starte die App lokal oder via Docker.
2. Oeffne `http://localhost:8000/login` und melde dich als Admin an.
3. Oeffne `http://localhost:8000/admin`.
4. Seed nur bewusst und nur bei leerer DB:
   - Setze `ENABLE_KOCHWIKI_SEED=1` und `AUTO_SEED_KOCHWIKI=1` nur gezielt und starte neu.
   - Der Seed laeuft einmalig nur ohne Rezepte und mit Meta-Flag.
5. Manueller CSV Import:
   - Im Admin Panel CSV hochladen.
   - Standard ist `insert_only`; optional `update_existing`.
6. Oeffne ein Rezept im Detail.
7. Lade ein Bild hoch, setze optional Hauptbild, pruefe Anzeige.
8. Klicke `PDF herunterladen` und pruefe Download.
9. Registriere einen normalen User.
10. Als User Favorite setzen und eine Review schreiben.
11. Pruefe Discover mit Filtern, Sortierung und Pagination.

## 5) Security Checks

### CSRF Fail

```bash
curl -i -X POST http://localhost:8000/logout
```

Erwartung: `403` wegen fehlendem CSRF Token.

### CSRF Pass (mit Browser-Session)

- Seite per Browser laden, damit `csrf_token` Cookie gesetzt wird.
- Normale Form-POSTs oder HTMX-Requests senden danach Token automatisch.

### Rate Limit (Login)

- Sende 6 fehlerhafte Login-Versuche innerhalb 1 Minute.
- Erwartung: spaetestens der 6. Request liefert `429`.

### Security Headers

```bash
curl -I http://localhost:8000/
```

Erwartung: `Content-Security-Policy`, `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`, `X-Request-ID`.

### Healthcheck

```bash
curl http://localhost:8000/healthz
```

Erwartung: `{"status":"ok"}`.

## 6) Smoke Test Script

Das Script testet:
- `/healthz`
- Register/Login inkl. `access_token` Cookie
- CSRF Token holen und Rezept per POST erstellen
- PDF Endpoint mit `application/pdf`

Start:

```bash
py scripts/smoke_test.py
```

Optional gegen laufende URL:

```bash
set SMOKE_BASE_URL=http://localhost:8000
py scripts/smoke_test.py
```
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enth?lt den konkreten Code/Textabschnitt '# MealMate Runbook'.
2. Diese Zeile ist leer und trennt den Inhalt strukturiert.
3. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Dieses Runbook zeigt Setup, Start und einen durchgehenden Demo-Flow inklusive...'.
4. Diese Zeile ist leer und trennt den Inhalt strukturiert.
5. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## 1) Lokales Setup (venv)'.
6. Diese Zeile ist leer und trennt den Inhalt strukturiert.
7. Diese Zeile enth?lt den konkreten Code/Textabschnitt ''''bash'.
8. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'py -m venv .venv'.
9. Diese Zeile enth?lt den konkreten Code/Textabschnitt '.venv\Scripts\activate'.
10. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'pip install -r requirements.txt'.
11. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'copy .env.example .env'.
12. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'py -m alembic -c alembic.ini upgrade head'.
13. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'py scripts/seed_admin.py'.
14. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'py -m uvicorn app.main:app --reload'.
15. Diese Zeile enth?lt den konkreten Code/Textabschnitt '''''.
16. Diese Zeile ist leer und trennt den Inhalt strukturiert.
17. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Danach:'.
18. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- App: 'http://localhost:8000''.
19. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Healthcheck: 'http://localhost:8000/healthz''.
20. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Admin: 'admin@mealmate.local' / 'AdminPass123!''.
21. Diese Zeile ist leer und trennt den Inhalt strukturiert.
22. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## 2) Lokales Setup mit Docker'.
23. Diese Zeile ist leer und trennt den Inhalt strukturiert.
24. Diese Zeile enth?lt den konkreten Code/Textabschnitt ''''bash'.
25. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'docker compose up --build'.
26. Diese Zeile enth?lt den konkreten Code/Textabschnitt '''''.
27. Diese Zeile ist leer und trennt den Inhalt strukturiert.
28. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Danach:'.
29. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- App: 'http://localhost:8000''.
30. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Postgres: 'localhost:5432''.
31. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Healthcheck: 'http://localhost:8000/healthz''.
32. Diese Zeile ist leer und trennt den Inhalt strukturiert.
33. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## 3) ENV Beispiele'.
34. Diese Zeile ist leer und trennt den Inhalt strukturiert.
35. Diese Zeile enth?lt den konkreten Code/Textabschnitt '### Dev (SQLite)'.
36. Diese Zeile ist leer und trennt den Inhalt strukturiert.
37. Diese Zeile enth?lt den konkreten Code/Textabschnitt ''''dotenv'.
38. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'APP_ENV=dev'.
39. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'APP_URL=http://localhost:8000'.
40. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'SECRET_KEY=change-me-dev'.
41. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'DATABASE_URL=sqlite:///./mealmate.db'.
42. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ALLOWED_HOSTS=*'.
43. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'COOKIE_SECURE=0'.
44. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'FORCE_HTTPS=0'.
45. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ENABLE_KOCHWIKI_SEED=0'.
46. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'AUTO_SEED_KOCHWIKI=0'.
47. Diese Zeile enth?lt den konkreten Code/Textabschnitt '''''.
48. Diese Zeile ist leer und trennt den Inhalt strukturiert.
49. Diese Zeile enth?lt den konkreten Code/Textabschnitt '### Prod (Postgres)'.
50. Diese Zeile ist leer und trennt den Inhalt strukturiert.
51. Diese Zeile enth?lt den konkreten Code/Textabschnitt ''''dotenv'.
52. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'APP_ENV=prod'.
53. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'APP_URL=https://mealmate.example.com'.
54. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'SECRET_KEY=<lange-zufaellige-zeichenkette>'.
55. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'DATABASE_URL=postgresql+psycopg://user:pass@host:5432/dbname'.
56. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ALLOWED_HOSTS=mealmate.example.com'.
57. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'COOKIE_SECURE=1'.
58. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'FORCE_HTTPS=1'.
59. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'ENABLE_KOCHWIKI_SEED=0'.
60. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'AUTO_SEED_KOCHWIKI=0'.
61. Diese Zeile enth?lt den konkreten Code/Textabschnitt '''''.
62. Diese Zeile ist leer und trennt den Inhalt strukturiert.
63. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## 4) Demo Flow (End-to-End)'.
64. Diese Zeile ist leer und trennt den Inhalt strukturiert.
65. Diese Zeile enth?lt den konkreten Code/Textabschnitt '1. Starte die App lokal oder via Docker.'.
66. Diese Zeile enth?lt den konkreten Code/Textabschnitt '2. Oeffne 'http://localhost:8000/login' und melde dich als Admin an.'.
67. Diese Zeile enth?lt den konkreten Code/Textabschnitt '3. Oeffne 'http://localhost:8000/admin'.'.
68. Diese Zeile enth?lt den konkreten Code/Textabschnitt '4. Seed nur bewusst und nur bei leerer DB:'.
69. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Setze 'ENABLE_KOCHWIKI_SEED=1' und 'AUTO_SEED_KOCHWIKI=1' nur gezielt und s...'.
70. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Der Seed laeuft einmalig nur ohne Rezepte und mit Meta-Flag.'.
71. Diese Zeile enth?lt den konkreten Code/Textabschnitt '5. Manueller CSV Import:'.
72. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Im Admin Panel CSV hochladen.'.
73. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Standard ist 'insert_only'; optional 'update_existing'.'.
74. Diese Zeile enth?lt den konkreten Code/Textabschnitt '6. Oeffne ein Rezept im Detail.'.
75. Diese Zeile enth?lt den konkreten Code/Textabschnitt '7. Lade ein Bild hoch, setze optional Hauptbild, pruefe Anzeige.'.
76. Diese Zeile enth?lt den konkreten Code/Textabschnitt '8. Klicke 'PDF herunterladen' und pruefe Download.'.
77. Diese Zeile enth?lt den konkreten Code/Textabschnitt '9. Registriere einen normalen User.'.
78. Diese Zeile enth?lt den konkreten Code/Textabschnitt '10. Als User Favorite setzen und eine Review schreiben.'.
79. Diese Zeile enth?lt den konkreten Code/Textabschnitt '11. Pruefe Discover mit Filtern, Sortierung und Pagination.'.
80. Diese Zeile ist leer und trennt den Inhalt strukturiert.
81. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## 5) Security Checks'.
82. Diese Zeile ist leer und trennt den Inhalt strukturiert.
83. Diese Zeile enth?lt den konkreten Code/Textabschnitt '### CSRF Fail'.
84. Diese Zeile ist leer und trennt den Inhalt strukturiert.
85. Diese Zeile enth?lt den konkreten Code/Textabschnitt ''''bash'.
86. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'curl -i -X POST http://localhost:8000/logout'.
87. Diese Zeile enth?lt den konkreten Code/Textabschnitt '''''.
88. Diese Zeile ist leer und trennt den Inhalt strukturiert.
89. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Erwartung: '403' wegen fehlendem CSRF Token.'.
90. Diese Zeile ist leer und trennt den Inhalt strukturiert.
91. Diese Zeile enth?lt den konkreten Code/Textabschnitt '### CSRF Pass (mit Browser-Session)'.
92. Diese Zeile ist leer und trennt den Inhalt strukturiert.
93. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Seite per Browser laden, damit 'csrf_token' Cookie gesetzt wird.'.
94. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Normale Form-POSTs oder HTMX-Requests senden danach Token automatisch.'.
95. Diese Zeile ist leer und trennt den Inhalt strukturiert.
96. Diese Zeile enth?lt den konkreten Code/Textabschnitt '### Rate Limit (Login)'.
97. Diese Zeile ist leer und trennt den Inhalt strukturiert.
98. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Sende 6 fehlerhafte Login-Versuche innerhalb 1 Minute.'.
99. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Erwartung: spaetestens der 6. Request liefert '429'.'.
100. Diese Zeile ist leer und trennt den Inhalt strukturiert.
101. Diese Zeile enth?lt den konkreten Code/Textabschnitt '### Security Headers'.
102. Diese Zeile ist leer und trennt den Inhalt strukturiert.
103. Diese Zeile enth?lt den konkreten Code/Textabschnitt ''''bash'.
104. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'curl -I http://localhost:8000/'.
105. Diese Zeile enth?lt den konkreten Code/Textabschnitt '''''.
106. Diese Zeile ist leer und trennt den Inhalt strukturiert.
107. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Erwartung: 'Content-Security-Policy', 'X-Content-Type-Options', 'X-Frame-Opti...'.
108. Diese Zeile ist leer und trennt den Inhalt strukturiert.
109. Diese Zeile enth?lt den konkreten Code/Textabschnitt '### Healthcheck'.
110. Diese Zeile ist leer und trennt den Inhalt strukturiert.
111. Diese Zeile enth?lt den konkreten Code/Textabschnitt ''''bash'.
112. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'curl http://localhost:8000/healthz'.
113. Diese Zeile enth?lt den konkreten Code/Textabschnitt '''''.
114. Diese Zeile ist leer und trennt den Inhalt strukturiert.
115. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Erwartung: '{"status":"ok"}'.'.
116. Diese Zeile ist leer und trennt den Inhalt strukturiert.
117. Diese Zeile enth?lt den konkreten Code/Textabschnitt '## 6) Smoke Test Script'.
118. Diese Zeile ist leer und trennt den Inhalt strukturiert.
119. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Das Script testet:'.
120. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- '/healthz''.
121. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- Register/Login inkl. 'access_token' Cookie'.
122. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- CSRF Token holen und Rezept per POST erstellen'.
123. Diese Zeile enth?lt den konkreten Code/Textabschnitt '- PDF Endpoint mit 'application/pdf''.
124. Diese Zeile ist leer und trennt den Inhalt strukturiert.
125. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Start:'.
126. Diese Zeile ist leer und trennt den Inhalt strukturiert.
127. Diese Zeile enth?lt den konkreten Code/Textabschnitt ''''bash'.
128. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'py scripts/smoke_test.py'.
129. Diese Zeile enth?lt den konkreten Code/Textabschnitt '''''.
130. Diese Zeile ist leer und trennt den Inhalt strukturiert.
131. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'Optional gegen laufende URL:'.
132. Diese Zeile ist leer und trennt den Inhalt strukturiert.
133. Diese Zeile enth?lt den konkreten Code/Textabschnitt ''''bash'.
134. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'set SMOKE_BASE_URL=http://localhost:8000'.
135. Diese Zeile enth?lt den konkreten Code/Textabschnitt 'py scripts/smoke_test.py'.
136. Diese Zeile enth?lt den konkreten Code/Textabschnitt '''''.

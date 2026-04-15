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
    get_enabled_category_mappings,
    get_or_create_ingredient,
    guess_canonical_category,
    normalize_category,
    normalize_raw_category,
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


def _create_recipe_from_payload(
    db: Session,
    payload: _PreparedRow,
    creator_id: int,
    category_mappings,
) -> Recipe:
    normalized_raw_category = normalize_raw_category(payload.category)
    guessed_canonical = guess_canonical_category(
        raw_category=normalized_raw_category,
        title=payload.title,
        description=payload.description,
        mappings=category_mappings,
    )
    recipe = Recipe(
        title=payload.title,
        description=payload.description,
        instructions=payload.instructions,
        category=normalized_raw_category,
        canonical_category=guessed_canonical,
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
        is_published=True,
    )
    db.add(recipe)
    db.flush()
    if payload.ingredients:
        replace_recipe_ingredients(db, recipe, payload.ingredients)
    return recipe


def _update_recipe_from_payload(
    db: Session,
    recipe: Recipe,
    payload: _PreparedRow,
    category_mappings,
) -> None:
    recipe.description = payload.description
    recipe.instructions = payload.instructions
    normalized_raw_category = normalize_raw_category(payload.category)
    recipe.category = normalized_raw_category
    recipe.canonical_category = guess_canonical_category(
        raw_category=normalized_raw_category,
        title=recipe.title,
        description=payload.description,
        mappings=category_mappings,
    )
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
    category_mappings = get_enabled_category_mappings(db)
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
                _update_recipe_from_payload(db, existing, payload, category_mappings)
                pending_writes += 1
            report.updated += 1
        else:
            if not dry_run:
                _create_recipe_from_payload(db, payload, creator_id, category_mappings)
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

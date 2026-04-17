from __future__ import annotations

import csv
import io
import re
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Recipe, RecipeImage
from app import services as legacy_services

settings = get_settings()

IMPORT_MODE = Literal["insert_only", "update_existing"]

# Bound references to legacy helpers keep behavior identical while allowing module split.
normalize_raw_category = legacy_services.normalize_raw_category
get_enabled_category_mappings = legacy_services.get_enabled_category_mappings
guess_canonical_category = legacy_services.guess_canonical_category
parse_optional_int = legacy_services.parse_optional_int
sanitize_difficulty = legacy_services.sanitize_difficulty
parse_text_block = legacy_services.parse_text_block
replace_recipe_ingredients = legacy_services.replace_recipe_ingredients
resolve_title_image_url = legacy_services.resolve_title_image_url
validate_upload = legacy_services.validate_upload
CSVImportReport = legacy_services.CSVImportReport
parse_list_like = legacy_services.parse_list_like
DEFAULT_CATEGORY = legacy_services.DEFAULT_CATEGORY

def normalize_columns(row: dict[str, Any]) -> dict[str, Any]:
    return {str(key).strip().lower(): value for key, value in row.items()}


def read_kochwiki_csv(csv_path: str | Path) -> list[dict[str, Any]]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    data = path.read_bytes()
    return read_kochwiki_csv_bytes(data)


def _read_csv_rows(text: str, delimiter: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    return [normalize_columns(row) for row in reader]


def read_kochwiki_csv_bytes(csv_bytes: bytes) -> list[dict[str, Any]]:
    text = csv_bytes.decode("utf-8-sig", errors="replace")
    sample_lines = [line for line in text.splitlines() if line.strip()][:5]
    sample = "\n".join(sample_lines)
    delimiter = ";" if sample.count(";") >= sample.count(",") else ","
    rows = _read_csv_rows(text, delimiter)
    if delimiter == ";" and rows and len(rows[0]) <= 1:
        fallback_rows = _read_csv_rows(text, ",")
        if fallback_rows and len(fallback_rows[0]) > 1:
            rows = fallback_rows
    return rows


def _pick_value(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _clean_title(value: Any) -> str:
    title = re.sub(r"\s+", " ", str(value or "").strip())
    return title[:255]


def _normalize_title_for_match(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())


def _parse_source_image_url(raw_value: Any) -> str | None:
    candidate = str(raw_value or "").strip()
    if not candidate:
        return None
    if "kein_bild" in candidate.lower():
        return None
    return candidate[:1024]


def _parse_kochwiki_ingredients(raw_value: Any) -> list[dict[str, Any]]:
    entries = []
    for item in parse_list_like(raw_value):
        cleaned = re.sub(r"\s+", " ", item.strip())
        if not cleaned:
            continue
        match = re.match(r"^\s*([\d.,/\-]+\s*[A-Za-z%]*)\s+(.+)$", cleaned)
        if match:
            quantity_text = match.group(1).strip()
            name = match.group(2).strip()
        else:
            quantity_text = ""
            name = cleaned
        entries.append({"name": name, "quantity_text": quantity_text, "grams": parse_optional_int(cleaned)})
    return entries


def _build_category(row: dict[str, Any]) -> str:
    categories = parse_list_like(row.get("kategorien"))
    if categories:
        return normalize_raw_category(categories[0])
    for key in ("mahlzeit", "landkuche", "landkueche", "category"):
        value = str(row.get(key) or "").strip()
        if value:
            return normalize_raw_category(value)
    return DEFAULT_CATEGORY


def _build_instructions(row: dict[str, Any]) -> str:
    instructions = parse_text_block(row.get("zubereitung") or row.get("instructions") or row.get("steps"))
    return instructions or "No instructions provided."


def _build_description(row: dict[str, Any]) -> str:
    description = str(row.get("beschreibung") or row.get("description") or "").strip()
    return description or "Imported from KochWiki."


def _find_existing_recipe(
    db: Session,
    source_uuid: str | None,
    title_normalized: str,
    source_url: str | None,
) -> Recipe | None:
    if source_uuid:
        recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))
        if recipe:
            return recipe
    if source_url:
        return db.scalar(
            select(Recipe).where(
                func.lower(Recipe.title) == title_normalized,
                Recipe.source_url == source_url,
            )
        )
    return None


def _apply_update_fields(recipe: Recipe, payload: dict[str, Any]) -> None:
    recipe.description = payload["description"]
    recipe.instructions = payload["instructions"]
    recipe.category = normalize_raw_category(payload["category"])
    recipe.canonical_category = guess_canonical_category(
        raw_category=recipe.category,
        title=payload["title"],
        description=payload["description"],
        mappings=payload["category_mappings"],
    )
    recipe.total_time_minutes = payload["total_time_minutes"]
    recipe.prep_time_minutes = payload["prep_time_minutes"]
    recipe.difficulty = payload["difficulty"]
    recipe.servings_text = payload["servings_text"]
    if payload["source_url"] and not recipe.source_url:
        recipe.source_url = payload["source_url"]
    if payload["source_uuid"] and not recipe.source_uuid:
        recipe.source_uuid = payload["source_uuid"]
    if payload["source_image_url"]:
        recipe.source_image_url = payload["source_image_url"]
        recipe.title_image_url = payload["source_image_url"]
    recipe.source = recipe.source or "kochwiki"


def _download_image_if_enabled(db: Session, recipe: Recipe, source_image_url: str | None) -> None:
    if not settings.import_download_images or not source_image_url:
        return
    resolved_url = resolve_title_image_url(source_image_url)
    if not resolved_url:
        return
    request = Request(resolved_url, headers={"User-Agent": "MealMate/1.0"})
    with urlopen(request, timeout=12) as response:
        content_type = str(response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        data = response.read(settings.max_upload_mb * 1024 * 1024 + 1)
    validate_upload(content_type, len(data), data)
    filename = Path(urlparse(resolved_url).path).name or "import-image"
    db.add(
        RecipeImage(
            recipe_id=recipe.id,
            filename=filename[:255],
            content_type=content_type,
            data=data,
        )
    )


def _prepare_kochwiki_payload(row: dict[str, Any]) -> dict[str, Any]:
    title = _clean_title(row.get("titel") or row.get("title") or row.get("name"))
    if not title:
        raise ValueError("missing title")
    source_url = str(row.get("quelle_url") or row.get("source_url") or "").strip()[:1024] or None
    source_uuid = str(row.get("rezept_uuid") or row.get("source_uuid") or "").strip()[:120] or None
    source_image_url = _parse_source_image_url(row.get("titelbild") or row.get("source_image_url"))
    prep_time_minutes = parse_optional_int(row.get("zeit_prep_min"))
    if prep_time_minutes is None:
        prep_time_minutes = parse_optional_int(row.get("arbeitszeit")) or 30
    total_time_minutes = parse_optional_int(row.get("zeit_total_min"))
    if total_time_minutes is None:
        total_time_minutes = parse_optional_int(row.get("arbeitszeit"))
    servings_text = str(row.get("portionen_text") or row.get("portionen") or "").strip()[:120] or None
    payload = {
        "title": title,
        "title_normalized": _normalize_title_for_match(title),
        "source": "kochwiki",
        "source_uuid": source_uuid,
        "source_url": source_url,
        "source_image_url": source_image_url,
        "description": _build_description(row),
        "instructions": _build_instructions(row),
        "category": _build_category(row),
        "prep_time_minutes": prep_time_minutes,
        "difficulty": sanitize_difficulty(str(row.get("schwierigkeit") or row.get("difficulty") or "medium")),
        "servings_text": servings_text,
        "total_time_minutes": total_time_minutes,
        "ingredients": _parse_kochwiki_ingredients(row.get("zutaten")),
    }
    return payload


def import_kochwiki_csv(
    db: Session,
    csv_source: str | Path | bytes,
    creator_id: int,
    mode: IMPORT_MODE = "insert_only",
    batch_size: int = 200,
    autocommit: bool = True,
) -> CSVImportReport:
    if mode not in {"insert_only", "update_existing"}:
        raise ValueError("mode must be 'insert_only' or 'update_existing'")
    rows = read_kochwiki_csv_bytes(csv_source) if isinstance(csv_source, bytes) else read_kochwiki_csv(csv_source)
    report = CSVImportReport()
    category_mappings = get_enabled_category_mappings(db)
    pending_writes = 0
    for row_index, row in enumerate(rows, start=2):
        try:
            payload = _prepare_kochwiki_payload(row)
            payload["category_mappings"] = category_mappings
            with db.begin_nested():
                existing = _find_existing_recipe(
                    db,
                    payload["source_uuid"],
                    payload["title_normalized"],
                    payload["source_url"],
                )
                if existing and mode == "insert_only":
                    report.skipped += 1
                    continue
                if existing and mode == "update_existing":
                    _apply_update_fields(existing, payload)
                    replace_recipe_ingredients(db, existing, payload["ingredients"])
                    db.add(existing)
                    report.updated += 1
                    pending_writes += 1
                    continue
                recipe = Recipe(
                    title=payload["title"],
                    title_image_url=payload["source_image_url"],
                    source=payload["source"],
                    source_uuid=payload["source_uuid"],
                    source_url=payload["source_url"],
                    source_image_url=payload["source_image_url"],
                    servings_text=payload["servings_text"],
                    total_time_minutes=payload["total_time_minutes"],
                    is_published=True,
                    description=payload["description"],
                    instructions=payload["instructions"],
                    category=normalize_raw_category(payload["category"]),
                    canonical_category=guess_canonical_category(
                        raw_category=payload["category"],
                        title=payload["title"],
                        description=payload["description"],
                        mappings=category_mappings,
                    ),
                    prep_time_minutes=payload["prep_time_minutes"],
                    difficulty=payload["difficulty"],
                    creator_id=creator_id,
                )
                db.add(recipe)
                db.flush()
                replace_recipe_ingredients(db, recipe, payload["ingredients"])
                _download_image_if_enabled(db, recipe, payload["source_image_url"])
                report.inserted += 1
                pending_writes += 1
            if pending_writes >= batch_size:
                if autocommit:
                    db.commit()
                else:
                    db.flush()
                pending_writes = 0
        except Exception as exc:
            report.skipped += 1
            report.errors.append(f"Row {row_index}: {exc}")
    if pending_writes > 0:
        if autocommit:
            db.commit()
        else:
            db.flush()
    return report

__all__ = [
    "normalize_columns",
    "read_kochwiki_csv",
    "read_kochwiki_csv_bytes",
    "import_kochwiki_csv",
]

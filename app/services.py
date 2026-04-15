import csv
import html
import io
import json
import re
from collections import Counter
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from PIL import Image, UnidentifiedImageError
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy import event, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import (
    AppMeta,
    CategoryMapping,
    Ingredient,
    Recipe,
    RecipeImage,
    RecipeIngredient,
    RecipeSubmission,
    SubmissionImage,
    SubmissionIngredient,
    User,
)

settings = get_settings()

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
DEFAULT_CATEGORY = "Unkategorisiert"
STANDARD_CANONICAL_CATEGORIES = [
    "Frühstück",
    "Mittagessen",
    "Abendessen",
    "Snack",
    "Dessert",
    "Getränke",
    "Suppe & Eintopf",
    "Salat",
    "Beilage",
    "Backen",
    "Hauptgericht",
    "Unkategorisiert",
]
IMPORT_MODE = Literal["insert_only", "update_existing"]
SUBMISSION_STATUS = Literal["pending", "approved", "rejected"]


@dataclass
class CSVImportReport:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def parse_ingredient_text(raw: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in raw.splitlines():
        normalized = line.strip()
        if not normalized:
            continue
        parts = [part.strip() for part in normalized.split("|")]
        if len(parts) == 1:
            items.append({"name": parts[0], "quantity_text": "", "grams": None})
            continue
        if len(parts) == 2:
            items.append({"name": parts[0], "quantity_text": parts[1], "grams": None})
            continue
        grams = parse_optional_int(parts[2])
        items.append({"name": parts[0], "quantity_text": parts[1], "grams": grams})
    return items


def parse_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"\d+", text)
    return int(match.group(0)) if match else None


def sanitize_difficulty(value: str) -> str:
    normalized = value.strip().lower()
    german_map = {"leicht": "easy", "mittel": "medium", "schwer": "hard"}
    normalized = german_map.get(normalized, normalized)
    if normalized not in ALLOWED_DIFFICULTIES:
        return "medium"
    return normalized


def normalize_raw_category(value: Any, fallback: str = DEFAULT_CATEGORY, allow_empty: bool = False) -> str:
    text = str(value or "").replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^((rezepte|schwierigkeit|kategorie)\s*[:\-]?\s*)+", "", text, flags=re.IGNORECASE).strip()
    if not text:
        return "" if allow_empty else fallback
    lowered = text.casefold()
    if lowered in {"general", "allgemein", "uncategorized", "unkategorisiert"}:
        return fallback
    return text[:120]


def normalize_category(value: Any, fallback: str = DEFAULT_CATEGORY, allow_empty: bool = False) -> str:
    return normalize_raw_category(value, fallback=fallback, allow_empty=allow_empty)


def normalize_canonical_category(value: Any, fallback: str = "Hauptgericht") -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip())
    if not text:
        return fallback
    if text not in STANDARD_CANONICAL_CATEGORIES:
        for category in STANDARD_CANONICAL_CATEGORIES:
            if category.casefold() == text.casefold():
                return category
    return text[:60]


def get_enabled_category_mappings(db: Session) -> list[CategoryMapping]:
    return db.scalars(
        select(CategoryMapping)
        .where(CategoryMapping.enabled.is_(True))
        .order_by(CategoryMapping.priority.asc(), CategoryMapping.id.asc())
    ).all()


def guess_canonical_category(
    *,
    raw_category: str | None,
    title: str | None = None,
    description: str | None = None,
    mappings: list[CategoryMapping] | None = None,
) -> str:
    normalized_raw = normalize_raw_category(raw_category, allow_empty=True)
    title_text = re.sub(r"\s+", " ", str(title or "").strip())
    description_text = re.sub(r"\s+", " ", str(description or "").strip())
    corpus = " | ".join(part for part in [normalized_raw, title_text, description_text] if part).casefold()

    if mappings:
        for mapping in mappings:
            pattern = re.sub(r"\s+", " ", str(mapping.pattern or "").strip()).casefold()
            if not pattern:
                continue
            if pattern in corpus:
                canonical_raw = str(mapping.canonical_category or "").strip()
                upper = canonical_raw.upper()
                if upper in {"IGNORE", "__IGNORE__"} or "IGNORE" in upper:
                    continue
                return normalize_canonical_category(mapping.canonical_category)

    if not corpus:
        return "Unkategorisiert"
    if normalized_raw.casefold() in {"unkategorisiert", "uncategorized", "general", "allgemein"} and not title_text and not description_text:
        return "Unkategorisiert"

    breakfast_keywords = ["frühstück", "fruehstueck", "brunch", "müsli", "muesli", "porridge"]
    if any(keyword in corpus for keyword in breakfast_keywords):
        return "Frühstück"

    baking_keywords = ["kuchen", "torte", "plätzchen", "plaetzchen", "gebäck", "gebaeck", "brot", "bröt", "broet", "hefe"]
    dessert_keywords = ["dessert", "nachspeise", "pudding", "creme", "mousse", "eis"]
    if any(keyword in corpus for keyword in baking_keywords):
        return "Backen"
    if any(keyword in corpus for keyword in dessert_keywords):
        return "Dessert"

    soup_keywords = ["suppe", "eintopf", "brühe", "bruehe", "gulasch", "chili"]
    if any(keyword in corpus for keyword in soup_keywords):
        return "Suppe & Eintopf"

    if "salat" in corpus:
        return "Salat"

    drink_keywords = ["getränk", "getraenk", "cocktail", "smoothie", "saft", "tee", "kaffee"]
    if any(keyword in corpus for keyword in drink_keywords):
        return "Getränke"

    side_keywords = ["beilage", "sauce", "soße", "sosse", "dip", "pesto", "reis", "kartoffel", "knödel", "knoedel"]
    if any(keyword in corpus for keyword in side_keywords):
        return "Beilage"

    snack_keywords = ["snack", "fingerfood", "häpp", "haepp", "wrap"]
    if any(keyword in corpus for keyword in snack_keywords):
        return "Snack"

    main_keywords = ["vegetar", "vegan"]
    if any(keyword in corpus for keyword in main_keywords):
        return "Hauptgericht"

    if "mittag" in corpus or "lunch" in corpus:
        return "Mittagessen"
    if "abend" in corpus or "dinner" in corpus:
        return "Abendessen"

    return "Hauptgericht"

def ensure_recipe_canonical_category(db: Session, recipe: Recipe) -> str:
    recipe.category = normalize_raw_category(recipe.category)
    mappings = get_enabled_category_mappings(db)
    recipe.canonical_category = guess_canonical_category(
        raw_category=recipe.category,
        title=recipe.title,
        description=recipe.description,
        mappings=mappings,
    )
    return recipe.canonical_category


def rebuild_recipe_canonical_categories(db: Session, batch_size: int = 200) -> tuple[int, int]:
    mappings = get_enabled_category_mappings(db)
    recipes = db.scalars(select(Recipe).order_by(Recipe.id.asc())).all()
    updated_count = 0
    skipped_count = 0
    pending = 0
    for recipe in recipes:
        normalized_raw = normalize_raw_category(recipe.category)
        guessed = guess_canonical_category(
            raw_category=normalized_raw,
            title=recipe.title,
            description=recipe.description,
            mappings=mappings,
        )
        changed = recipe.category != normalized_raw or recipe.canonical_category != guessed
        if changed:
            recipe.category = normalized_raw
            recipe.canonical_category = guessed
            updated_count += 1
            pending += 1
            if pending >= batch_size:
                db.flush()
                pending = 0
        else:
            skipped_count += 1
    if pending > 0:
        db.flush()
    return updated_count, skipped_count


def build_category_index(db: Session, only_published: bool = False) -> dict[str, list[str]]:
    stmt = select(Recipe.category, Recipe.canonical_category)
    if only_published:
        stmt = stmt.where(Recipe.is_published.is_(True))
    rows = db.execute(stmt).all()
    variants: dict[str, set[str]] = {}
    for raw_value, canonical_value in rows:
        raw_clean = normalize_raw_category(raw_value, allow_empty=True) or DEFAULT_CATEGORY
        canonical_clean = normalize_canonical_category(canonical_value, fallback=guess_canonical_category(raw_category=raw_clean))
        variants.setdefault(canonical_clean, set()).add(raw_clean)
    if not variants:
        variants[DEFAULT_CATEGORY] = {DEFAULT_CATEGORY}
    return {key: sorted(values) for key, values in variants.items()}


def get_distinct_categories(db: Session, only_published: bool = False) -> list[str]:
    stmt = select(Recipe.canonical_category)
    if only_published:
        stmt = stmt.where(Recipe.is_published.is_(True))
    canonical_values = [
        normalize_canonical_category(value, fallback="")
        for value in db.scalars(stmt).all()
        if str(value or "").strip()
    ]
    categories = sorted({value for value in canonical_values if value}, key=str.casefold)
    if only_published:
        return categories or STANDARD_CANONICAL_CATEGORIES.copy()
    merged = set(categories).union(STANDARD_CANONICAL_CATEGORIES)
    return sorted(merged, key=str.casefold)


def get_category_stats(db: Session, limit: int = 10) -> tuple[int, list[tuple[str, int]]]:
    raw_categories = db.scalars(select(Recipe.category)).all()
    counter = Counter(normalize_raw_category(value) for value in raw_categories)
    if not counter:
        counter = Counter({DEFAULT_CATEGORY: 0})
    top_categories = sorted(counter.items(), key=lambda item: (-item[1], item[0].casefold()))[:limit]
    return len(counter), top_categories


def get_raw_category_overview(db: Session, limit: int = 30) -> list[dict[str, Any]]:
    mappings = get_enabled_category_mappings(db)
    rows = db.execute(
        select(Recipe.category, func.count(Recipe.id))
        .group_by(Recipe.category)
        .order_by(func.count(Recipe.id).desc(), Recipe.category.asc())
        .limit(limit)
    ).all()
    overview: list[dict[str, Any]] = []
    for raw_value, count in rows:
        raw_clean = normalize_raw_category(raw_value)
        guessed = guess_canonical_category(raw_category=raw_clean, mappings=mappings)
        overview.append({"raw_category": raw_clean, "count": int(count), "guessed_canonical": guessed})
    return overview


@event.listens_for(Session, "before_flush")
def assign_canonical_category_before_flush(session: Session, flush_context, instances) -> None:
    _ = flush_context
    _ = instances
    mappings_cache: list[CategoryMapping] | None = None
    for obj in session.new.union(session.dirty):
        if not isinstance(obj, Recipe):
            continue
        if mappings_cache is None:
            with session.no_autoflush:
                mappings_cache = get_enabled_category_mappings(session)
        obj.category = normalize_raw_category(obj.category)
        obj.canonical_category = guess_canonical_category(
            raw_category=obj.category,
            title=obj.title,
            description=obj.description,
            mappings=mappings_cache,
        )


def normalize_ingredient_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def parse_list_like(raw_value: Any) -> list[str]:
    if isinstance(raw_value, list):
        return [str(item).strip() for item in raw_value if str(item).strip()]
    if raw_value is None:
        return []
    value = str(raw_value).strip()
    if not value:
        return []
    if value.startswith("[") and value.endswith("]"):
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, list):
            return [str(item).strip() for item in loaded if str(item).strip()]
    separator = "\n" if "\n" in value else ","
    return [item.strip().strip('"') for item in value.split(separator) if item.strip()]


def parse_text_block(raw_value: Any) -> str:
    parts = parse_list_like(raw_value)
    if parts:
        return "\n".join(parts)
    return str(raw_value or "").strip()


def get_or_create_ingredient(db: Session, name: str) -> Ingredient:
    normalized = normalize_ingredient_name(name)
    ingredient = db.scalar(select(Ingredient).where(Ingredient.name == normalized))
    if ingredient:
        return ingredient
    ingredient = Ingredient(name=normalized)
    db.add(ingredient)
    db.flush()
    return ingredient


def replace_recipe_ingredients(db: Session, recipe: Recipe, ingredient_entries: list[dict[str, Any]]) -> None:
    recipe.recipe_ingredients.clear()
    merged_entries: dict[str, dict[str, Any]] = {}
    for entry in ingredient_entries:
        name = str(entry.get("name") or "").strip()
        if not name:
            continue
        key = normalize_ingredient_name(name)
        quantity_text = str(entry.get("quantity_text") or "").strip()
        grams = parse_optional_int(entry.get("grams"))
        if key not in merged_entries:
            merged_entries[key] = {"name": name, "quantity_text": quantity_text, "grams": grams}
            continue
        current = merged_entries[key]
        if quantity_text:
            if current["quantity_text"]:
                current["quantity_text"] = f"{current['quantity_text']} | {quantity_text}"
            else:
                current["quantity_text"] = quantity_text
        if current["grams"] is None and grams is not None:
            current["grams"] = grams
    for merged in merged_entries.values():
        ingredient = get_or_create_ingredient(db, merged["name"])
        db.add(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                quantity_text=merged["quantity_text"],
                grams=merged["grams"],
            )
        )


def replace_submission_ingredients(
    db: Session,
    submission: RecipeSubmission,
    ingredient_entries: list[dict[str, Any]],
) -> None:
    submission.ingredients.clear()
    merged_entries: dict[str, dict[str, Any]] = {}
    for entry in ingredient_entries:
        name = str(entry.get("name") or "").strip()
        if not name:
            continue
        key = normalize_ingredient_name(name)
        quantity_text = str(entry.get("quantity_text") or "").strip()[:120]
        grams = parse_optional_int(entry.get("grams"))
        if key not in merged_entries:
            merged_entries[key] = {"name": name[:200], "quantity_text": quantity_text, "grams": grams}
            continue
        current = merged_entries[key]
        if quantity_text:
            if current["quantity_text"]:
                current["quantity_text"] = f"{current['quantity_text']} | {quantity_text}"[:120]
            else:
                current["quantity_text"] = quantity_text
        if current["grams"] is None and grams is not None:
            current["grams"] = grams
    for merged in merged_entries.values():
        db.add(
            SubmissionIngredient(
                submission=submission,
                ingredient_name=merged["name"],
                quantity_text=merged["quantity_text"],
                grams=merged["grams"],
                ingredient_name_normalized=normalize_ingredient_name(merged["name"]),
            )
        )


def build_submission_ingredients_text(ingredients: list[SubmissionIngredient]) -> str:
    lines: list[str] = []
    for ingredient in ingredients:
        name = ingredient.ingredient_name.strip()
        if not name:
            continue
        if ingredient.grams is not None:
            lines.append(f"{name}|{ingredient.quantity_text}|{ingredient.grams}")
            continue
        if ingredient.quantity_text:
            lines.append(f"{name}|{ingredient.quantity_text}")
            continue
        lines.append(name)
    return "\n".join(lines)


def get_submission_primary_image(submission: RecipeSubmission) -> SubmissionImage | None:
    for image in submission.images:
        if image.is_primary:
            return image
    return submission.images[0] if submission.images else None


def publish_submission_as_recipe(db: Session, submission: RecipeSubmission, admin_id: int) -> Recipe:
    source_uuid = f"submission:{submission.id}"
    existing = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))
    if existing:
        raise ValueError("Submission has already been published.")
    normalized_raw_category = normalize_raw_category(submission.category)
    guessed_canonical = guess_canonical_category(
        raw_category=normalized_raw_category,
        title=submission.title,
        description=submission.description,
        mappings=get_enabled_category_mappings(db),
    )
    recipe = Recipe(
        title=submission.title.strip()[:255],
        description=submission.description.strip(),
        instructions=submission.instructions.strip(),
        category=normalized_raw_category,
        canonical_category=guessed_canonical,
        prep_time_minutes=max(int(submission.prep_time_minutes or 30), 1),
        difficulty=sanitize_difficulty(submission.difficulty),
        creator_id=admin_id,
        source="submission",
        source_uuid=source_uuid,
        source_url=None,
        source_image_url=None,
        title_image_url=None,
        servings_text=(submission.servings_text or "").strip()[:120] or None,
        total_time_minutes=None,
        is_published=True,
    )
    db.add(recipe)
    db.flush()
    for item in submission.ingredients:
        ingredient_name = item.ingredient_name.strip()
        if not ingredient_name:
            continue
        ingredient = get_or_create_ingredient(db, ingredient_name)
        db.add(
            RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity_text=(item.quantity_text or "").strip()[:120],
                grams=item.grams,
            )
        )
    any_primary = False
    for image in submission.images:
        db.add(
            RecipeImage(
                recipe_id=recipe.id,
                filename=image.filename,
                content_type=image.content_type,
                data=image.data,
                is_primary=image.is_primary,
            )
        )
        if image.is_primary:
            any_primary = True
    if submission.images and not any_primary:
        first_recipe_image = db.scalar(
            select(RecipeImage).where(RecipeImage.recipe_id == recipe.id).order_by(RecipeImage.id.asc())
        )
        if first_recipe_image:
            first_recipe_image.is_primary = True
    return recipe


def get_submission_status_stats(db: Session) -> dict[str, int]:
    rows = db.execute(
        select(RecipeSubmission.status, func.count(RecipeSubmission.id)).group_by(RecipeSubmission.status)
    ).all()
    base = {"pending": 0, "approved": 0, "rejected": 0}
    for status, count in rows:
        base[str(status)] = int(count)
    return base


def validate_upload(content_type: str, file_size_bytes: int, file_bytes: bytes | None = None) -> None:
    if content_type not in settings.allowed_image_types:
        raise ValueError(f"Unsupported MIME type '{content_type}'.")
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise ValueError(f"Image too large. Max size is {settings.max_upload_mb} MB.")
    if file_bytes is not None:
        try:
            with Image.open(io.BytesIO(file_bytes)) as image:
                image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("Uploaded file is not a valid image.") from exc


@lru_cache(maxsize=4096)
def resolve_title_image_url(image_url: str) -> str | None:
    cleaned = image_url.strip()
    if not cleaned:
        return None
    lower = cleaned.lower()
    if "kein_bild" in lower:
        return None
    if lower.endswith((".jpg", ".jpeg", ".png", ".webp")) and "/wiki/" not in lower:
        return cleaned
    parsed = urlparse(cleaned)
    host = parsed.netloc.lower()
    path = unquote(parsed.path).lower()
    if "kochwiki.org" in host and "/wiki/" in parsed.path and "datei" in path:
        request = Request(cleaned, headers={"User-Agent": "MealMate/1.0"})
        with urlopen(request, timeout=12) as response:
            html_text = response.read(300_000).decode("utf-8", errors="ignore")
        match = re.search(
            r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
            html_text,
            flags=re.IGNORECASE,
        )
        if match:
            return html.unescape(match.group(1))
    return cleaned


def extract_token(raw_header: str | None) -> str | None:
    if not raw_header:
        return None
    prefix = "Bearer "
    if raw_header.startswith(prefix):
        return raw_header[len(prefix) :].strip()
    return raw_header.strip()


def can_manage_recipe(current_user: User, recipe: Recipe) -> bool:
    return current_user.role == "admin" or recipe.creator_id == current_user.id


def get_meta_value(db: Session, key: str) -> str | None:
    meta = db.scalar(select(AppMeta).where(AppMeta.key == key))
    return meta.value if meta else None


def set_meta_value(db: Session, key: str, value: str) -> None:
    meta = db.scalar(select(AppMeta).where(AppMeta.key == key))
    if not meta:
        db.add(AppMeta(key=key, value=value))
        return
    meta.value = value


def is_meta_true(db: Session, key: str) -> bool:
    return get_meta_value(db, key) == "1"


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


def build_recipe_pdf(recipe: Recipe, avg_rating: float, review_count: int) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    top = height - 50
    if recipe.images:
        image = recipe.images[0]
        image_reader = ImageReader(io.BytesIO(image.data))
        pdf.drawImage(image_reader, 50, top - 120, width=120, height=90, preserveAspectRatio=True, mask="auto")
        top -= 130
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, top, recipe.title)
    top -= 24
    pdf.setFont("Helvetica", 11)
    meta = f"Category: {recipe.category} | Difficulty: {recipe.difficulty} | Prep: {recipe.prep_time_minutes} min"
    pdf.drawString(50, top, meta)
    top -= 18
    rating_line = f"Average rating: {avg_rating:.2f} ({review_count} reviews)"
    pdf.drawString(50, top, rating_line)
    top -= 26
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, top, "Ingredients")
    top -= 18
    pdf.setFont("Helvetica", 11)
    for link in recipe.recipe_ingredients:
        line = f"- {link.ingredient.name} {link.quantity_text}".strip()
        if link.grams:
            line = f"{line} ({link.grams} g)"
        top = draw_wrapped_line(pdf, line, 50, top, width - 100)
        if top < 100:
            pdf.showPage()
            top = height - 50
            pdf.setFont("Helvetica", 11)
    top -= 6
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, top, "Instructions")
    top -= 18
    pdf.setFont("Helvetica", 11)
    for paragraph in [piece.strip() for piece in recipe.instructions.splitlines() if piece.strip()]:
        top = draw_wrapped_line(pdf, paragraph, 50, top, width - 100)
        top -= 4
        if top < 80:
            pdf.showPage()
            top = height - 50
            pdf.setFont("Helvetica", 11)
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def draw_wrapped_line(pdf: canvas.Canvas, text: str, x: int, y: int, max_width: int) -> int:
    words = text.split()
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if pdf.stringWidth(trial, "Helvetica", 11) <= max_width:
            current = trial
            continue
        pdf.drawString(x, y, current)
        y -= 14
        current = word
    if current:
        pdf.drawString(x, y, current)
        y -= 14
    return y


def readable_file_size(size_bytes: int) -> str:
    return f"{size_bytes / (1024 * 1024):.2f} MB"


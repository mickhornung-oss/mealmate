import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from sqlalchemy import event, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import (
    CategoryMapping,
    Ingredient,
    Recipe,
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
    from app.services_submission import replace_submission_ingredients as _impl

    return _impl(db, submission, ingredient_entries)


def build_submission_ingredients_text(ingredients: list[SubmissionIngredient]) -> str:
    from app.services_submission import build_submission_ingredients_text as _impl

    return _impl(ingredients)


def get_submission_primary_image(submission: RecipeSubmission) -> SubmissionImage | None:
    from app.services_submission import get_submission_primary_image as _impl

    return _impl(submission)


def publish_submission_as_recipe(db: Session, submission: RecipeSubmission, admin_id: int) -> Recipe:
    from app.services_submission import publish_submission_as_recipe as _impl

    return _impl(db, submission, admin_id)


def get_submission_status_stats(db: Session) -> dict[str, int]:
    from app.services_submission import get_submission_status_stats as _impl

    return _impl(db)


def validate_upload(content_type: str, file_size_bytes: int, file_bytes: bytes | None = None) -> None:
    from app.services_runtime import validate_upload as _impl

    return _impl(content_type, file_size_bytes, file_bytes)

def resolve_title_image_url(image_url: str) -> str | None:
    from app.services_runtime import resolve_title_image_url as _impl

    return _impl(image_url)


def extract_token(raw_header: str | None) -> str | None:
    from app.services_runtime import extract_token as _impl

    return _impl(raw_header)


def can_manage_recipe(current_user: User, recipe: Recipe) -> bool:
    from app.services_runtime import can_manage_recipe as _impl

    return _impl(current_user, recipe)


def get_meta_value(db: Session, key: str) -> str | None:
    from app.services_runtime import get_meta_value as _impl

    return _impl(db, key)


def set_meta_value(db: Session, key: str, value: str) -> None:
    from app.services_runtime import set_meta_value as _impl

    return _impl(db, key, value)


def is_meta_true(db: Session, key: str) -> bool:
    from app.services_runtime import is_meta_true as _impl

    return _impl(db, key)


def normalize_columns(row: dict[str, Any]) -> dict[str, Any]:
    from app.services_import import normalize_columns as _impl

    return _impl(row)


def read_kochwiki_csv(csv_path: str | Path) -> list[dict[str, Any]]:
    from app.services_import import read_kochwiki_csv as _impl

    return _impl(csv_path)


def read_kochwiki_csv_bytes(csv_bytes: bytes) -> list[dict[str, Any]]:
    from app.services_import import read_kochwiki_csv_bytes as _impl

    return _impl(csv_bytes)


def import_kochwiki_csv(
    db: Session,
    csv_source: str | Path | bytes,
    creator_id: int,
    mode: IMPORT_MODE = "insert_only",
    batch_size: int = 200,
    autocommit: bool = True,
) -> CSVImportReport:
    from app.services_import import import_kochwiki_csv as _impl

    return _impl(
        db=db,
        csv_source=csv_source,
        creator_id=creator_id,
        mode=mode,
        batch_size=batch_size,
        autocommit=autocommit,
    )


def readable_file_size(size_bytes: int) -> str:
    return f"{size_bytes / (1024 * 1024):.2f} MB"


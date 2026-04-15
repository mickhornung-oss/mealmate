from dataclasses import dataclass
import re
from typing import Any, Iterable, Literal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app import services as legacy_services
from app.models import CategoryMapping, Recipe

MappingScope = Literal["raw", "fulltext"]
RebuildMode = Literal["full", "suspicious"]

PATTERN_MIN_LEN = 4
PATTERN_MIN_LEN_WHITELIST = {"tee", "eis", "dip"}

UNSPECIFIC_RAW_VALUES = {
    "",
    "unkategorisiert",
    "uncategorized",
    "allgemein",
    "general",
    "kategorie",
    "rezepte",
    "schwierig",
    "schwierigkeit",
}

SAVOURY_KEYWORDS = {"suppe", "eintopf", "salat", "beilage", "soße", "sosse", "sauce", "brühe", "bruehe"}
SWEET_KEYWORDS = {"kuchen", "torte", "plätzchen", "plaetzchen", "dessert", "pudding"}
DRINK_CONFLICT_KEYWORDS = {"suppe", "auflauf", "braten"}
SIDE_CONFLICT_KEYWORDS = {"kuchen", "torte"}


@dataclass(frozen=True)
class CategoryMappingRule:
    id: int
    pattern: str
    canonical_category: str
    priority: int
    enabled: bool
    scope: str


@dataclass(frozen=True)
class CanonicalSuggestion:
    canonical_category: str
    reason: str
    cleaned_raw_category: str


@dataclass(frozen=True)
class CategoryQARow:
    recipe_id: int
    title: str
    raw_category: str
    canonical_category: str
    suggested_canonical: str
    reason: str
    suspicious_reason: str


def _normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def _normalize_match_text(value: Any) -> str:
    return _normalize_text(value).casefold()


def _normalize_scope(scope: Any) -> str:
    normalized = _normalize_text(scope).lower()
    if normalized not in {"raw", "fulltext"}:
        return "raw"
    return normalized


def _normalize_mapping_pattern(pattern: Any) -> str:
    return _normalize_match_text(pattern)


def _is_ignore_canonical(canonical_category: Any) -> bool:
    value = _normalize_text(canonical_category).upper()
    if not value:
        return False
    if value in {"IGNORE", "__IGNORE__", "(IGNORE)"}:
        return True
    return "IGNORE" in value


def _is_unspecific_raw(cleaned_raw_category: str) -> bool:
    if not cleaned_raw_category:
        return True
    lowered = cleaned_raw_category.casefold()
    if lowered in UNSPECIFIC_RAW_VALUES:
        return True
    alnum = re.sub(r"[^a-z0-9äöüß]+", "", lowered)
    return len(alnum) < 2


def _contains_any(text_value: str, keywords: set[str]) -> bool:
    return any(keyword in text_value for keyword in keywords)


def _coerce_mapping_rule(item: Any) -> CategoryMappingRule:
    if isinstance(item, CategoryMappingRule):
        return item
    return CategoryMappingRule(
        id=int(getattr(item, "id", 0) or 0),
        pattern=_normalize_text(getattr(item, "pattern", "")),
        canonical_category=_normalize_text(getattr(item, "canonical_category", "")),
        priority=int(getattr(item, "priority", 100) or 100),
        enabled=bool(getattr(item, "enabled", True)),
        scope=_normalize_scope(getattr(item, "scope", "raw")),
    )


def coerce_mapping_rules(items: Iterable[Any]) -> list[CategoryMappingRule]:
    rules = [_coerce_mapping_rule(item) for item in items]
    return sorted(rules, key=lambda rule: (rule.priority, rule.id, rule.pattern.casefold()))


def load_category_mapping_rules(db: Session, include_disabled: bool = False) -> list[CategoryMappingRule]:
    stmt = select(CategoryMapping).order_by(CategoryMapping.priority.asc(), CategoryMapping.id.asc())
    if not include_disabled:
        stmt = stmt.where(CategoryMapping.enabled.is_(True))
    records = db.scalars(stmt).all()
    return coerce_mapping_rules(records)


def _apply_mapping_rules(
    mapping_rules: list[CategoryMappingRule],
    *,
    match_text: str,
    scope: MappingScope,
    cleaned_raw: str,
) -> CanonicalSuggestion | None:
    if not match_text:
        return None
    for rule in mapping_rules:
        if not rule.enabled:
            continue
        if _normalize_scope(rule.scope) != scope:
            continue
        pattern = _normalize_mapping_pattern(rule.pattern)
        if not pattern:
            continue
        if pattern not in match_text:
            continue
        if _is_ignore_canonical(rule.canonical_category):
            continue
        canonical = legacy_services.normalize_canonical_category(rule.canonical_category)
        return CanonicalSuggestion(
            canonical_category=canonical,
            reason=f"mapping:{scope}:{rule.pattern}",
            cleaned_raw_category=cleaned_raw,
        )
    return None


def _heuristic_from_text(match_text: str) -> str | None:
    if not match_text:
        return None

    breakfast_keywords = {"frühstück", "fruehstueck", "brunch", "müsli", "muesli", "porridge"}
    if _contains_any(match_text, breakfast_keywords):
        return "Frühstück"

    if "mittagessen" in match_text or "mittag" in match_text or "lunch" in match_text:
        return "Mittagessen"
    if "abendessen" in match_text or "abend" in match_text or "dinner" in match_text:
        return "Abendessen"

    baking_keywords = {
        "kuchen",
        "torte",
        "plätzchen",
        "plaetzchen",
        "gebäck",
        "gebaeck",
        "brot",
        "bröt",
        "broet",
        "hefe",
        "laugen",
    }
    if _contains_any(match_text, baking_keywords):
        return "Backen"

    dessert_keywords = {"dessert", "nachspeise", "pudding", "creme", "mousse", "eis"}
    if _contains_any(match_text, dessert_keywords):
        return "Dessert"

    soup_keywords = {"suppe", "eintopf", "brühe", "bruehe", "gulasch", "chili"}
    if _contains_any(match_text, soup_keywords):
        return "Suppe & Eintopf"

    if "salat" in match_text:
        return "Salat"

    drink_keywords = {"getränk", "getraenk", "cocktail", "smoothie", "saft", "tee", "kaffee"}
    if _contains_any(match_text, drink_keywords):
        return "Getränke"

    side_keywords = {"beilage", "sauce", "soße", "sosse", "dip", "pesto", "reis", "kartoffel", "knödel", "knoedel"}
    if _contains_any(match_text, side_keywords):
        return "Beilage"

    snack_keywords = {"snack", "fingerfood", "häpp", "haepp", "wrap"}
    if _contains_any(match_text, snack_keywords):
        return "Snack"

    if "vegetar" in match_text or "vegan" in match_text:
        return "Hauptgericht"
    return None


def suggest_canonical_category(
    *,
    raw_category: Any,
    title: Any = "",
    description: Any = "",
    mapping_rules: Iterable[Any] | None = None,
) -> CanonicalSuggestion:
    cleaned_raw = legacy_services.normalize_raw_category(raw_category, allow_empty=True)
    cleaned_title = _normalize_text(title)
    cleaned_description = _normalize_text(description)

    raw_match_text = _normalize_match_text(cleaned_raw)
    full_match_text = _normalize_match_text(
        " | ".join(part for part in [cleaned_raw, cleaned_title, cleaned_description] if part)
    )
    rules = coerce_mapping_rules(mapping_rules or [])

    raw_mapping = _apply_mapping_rules(rules, match_text=raw_match_text, scope="raw", cleaned_raw=cleaned_raw)
    if raw_mapping:
        return raw_mapping

    raw_is_unspecific = _is_unspecific_raw(cleaned_raw)
    if raw_match_text and not raw_is_unspecific:
        raw_heuristic = _heuristic_from_text(raw_match_text)
        if raw_heuristic:
            return CanonicalSuggestion(raw_heuristic, "heuristic:raw", cleaned_raw)
        return CanonicalSuggestion("Hauptgericht", "fallback:raw-default", cleaned_raw)

    full_mapping = _apply_mapping_rules(rules, match_text=full_match_text, scope="fulltext", cleaned_raw=cleaned_raw)
    if full_mapping:
        return full_mapping

    full_heuristic = _heuristic_from_text(full_match_text)
    if full_heuristic:
        return CanonicalSuggestion(full_heuristic, "heuristic:fulltext", cleaned_raw)

    if full_match_text:
        return CanonicalSuggestion("Hauptgericht", "fallback:fulltext-default", cleaned_raw)
    return CanonicalSuggestion("Unkategorisiert", "fallback:empty", cleaned_raw)


def detect_suspicious_reason(recipe: Recipe, suggested: CanonicalSuggestion) -> str:
    current = legacy_services.normalize_canonical_category(recipe.canonical_category, fallback="Unkategorisiert")
    title_match = _normalize_match_text(recipe.title)
    raw_match = _normalize_match_text(suggested.cleaned_raw_category)
    merged = f"{raw_match} | {title_match}"

    if current in {"Dessert", "Backen"} and _contains_any(merged, SAVOURY_KEYWORDS):
        return "dessert_or_backen_with_savoury_signals"
    if current == "Suppe & Eintopf" and _contains_any(title_match, SWEET_KEYWORDS):
        return "soup_with_sweet_title_signals"
    if current == "Getränke" and _contains_any(title_match, DRINK_CONFLICT_KEYWORDS):
        return "drink_with_solid_food_title_signals"
    if current == "Beilage" and _contains_any(title_match, SIDE_CONFLICT_KEYWORDS):
        return "side_with_sweet_title_signals"
    if "laugen" in title_match and current == "Dessert":
        return "laugen_must_not_be_dessert"
    return ""


def build_category_qa_rows(db: Session, limit: int = 200) -> list[CategoryQARow]:
    rules = load_category_mapping_rules(db, include_disabled=False)
    recipes = db.scalars(select(Recipe).order_by(Recipe.id.desc())).all()
    rows: list[CategoryQARow] = []
    for recipe in recipes:
        suggested = suggest_canonical_category(
            raw_category=recipe.category,
            title=recipe.title,
            description=recipe.description,
            mapping_rules=rules,
        )
        suspicious_reason = detect_suspicious_reason(recipe, suggested)
        if not suspicious_reason:
            continue
        rows.append(
            CategoryQARow(
                recipe_id=recipe.id,
                title=recipe.title,
                raw_category=suggested.cleaned_raw_category or "",
                canonical_category=recipe.canonical_category or "",
                suggested_canonical=suggested.canonical_category,
                reason=suggested.reason,
                suspicious_reason=suspicious_reason,
            )
        )
        if len(rows) >= limit:
            break
    return rows


def rebuild_canonical_categories(
    db: Session,
    *,
    mode: RebuildMode = "full",
    batch_size: int = 200,
) -> dict[str, int | str]:
    if mode not in {"full", "suspicious"}:
        raise ValueError("mode must be 'full' or 'suspicious'")

    rules = load_category_mapping_rules(db, include_disabled=False)
    suspicious_rows = build_category_qa_rows(db, limit=200000) if mode == "suspicious" else []
    suspicious_ids = {row.recipe_id for row in suspicious_rows}

    recipes = db.scalars(select(Recipe).order_by(Recipe.id.asc())).all()
    updated = 0
    skipped = 0
    pending = 0

    for recipe in recipes:
        if mode == "suspicious" and recipe.id not in suspicious_ids:
            skipped += 1
            continue
        suggested = suggest_canonical_category(
            raw_category=recipe.category,
            title=recipe.title,
            description=recipe.description,
            mapping_rules=rules,
        )
        normalized_raw = legacy_services.normalize_raw_category(recipe.category)
        changed = recipe.category != normalized_raw or (recipe.canonical_category or "") != suggested.canonical_category
        if not changed:
            skipped += 1
            continue
        recipe.category = normalized_raw
        recipe.canonical_category = suggested.canonical_category
        updated += 1
        pending += 1
        if pending >= batch_size:
            db.flush()
            pending = 0
    if pending > 0:
        db.flush()

    return {
        "mode": mode,
        "updated": updated,
        "skipped": skipped,
        "total": len(recipes),
        "suspicious_count": len(suspicious_ids),
    }


def validate_mapping_pattern(pattern: str) -> str:
    normalized = _normalize_text(pattern)
    if not normalized:
        raise ValueError("Pattern ist erforderlich.")
    compact = normalized.casefold()
    if len(compact) < PATTERN_MIN_LEN and compact not in PATTERN_MIN_LEN_WHITELIST:
        raise ValueError("Pattern muss mindestens 4 Zeichen haben (Ausnahmen: tee, eis, dip).")
    return normalized


def _guess_wrapper(
    *,
    raw_category: str | None,
    title: str | None = None,
    description: str | None = None,
    mappings=None,
) -> str:
    suggestion = suggest_canonical_category(
        raw_category=raw_category,
        title=title or "",
        description=description or "",
        mapping_rules=mappings or [],
    )
    return suggestion.canonical_category


def _rebuild_wrapper(db: Session, batch_size: int = 200) -> tuple[int, int]:
    report = rebuild_canonical_categories(db, mode="full", batch_size=batch_size)
    return int(report["updated"]), int(report["skipped"])


def install_canonical_category_overrides() -> None:
    legacy_services.guess_canonical_category = _guess_wrapper
    legacy_services.rebuild_recipe_canonical_categories = _rebuild_wrapper

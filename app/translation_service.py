from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

import httpx
from sqlalchemy import event, select
from sqlalchemy.orm import Session, selectinload, sessionmaker

from app.config import get_settings
from app.models import Recipe, RecipeIngredient
import app.translation_helpers as translation_helpers
from app.translation_provider import TranslationProvider, resolve_translation_provider
from app.translation_models import RecipeTranslation, TranslationBatchJob

AUTO_TRANSLATION_RECIPE_IDS_KEY = "translation_auto_recipe_ids"
AUTO_TRANSLATION_NEW_RECIPES_KEY = "translation_auto_new_recipes"
_HOOKS_REGISTERED = False
_PROVIDER_OVERRIDE: TranslationProvider | None = None
TERMINAL_JOB_STATUSES = {"completed", "failed", "cancelled", "timeout"}
SUSPECT_FLAG = "suspect_lang_mismatch"
OK_FLAG = "ok"


@dataclass
class TranslationStats:
    published_recipes: int
    target_languages: list[str]
    missing_translations: int
    stale_translations: int


@dataclass
class TranslationRunReport:
    mode: str
    limit: int
    processed_recipes: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass
class TranslationQueueItem:
    recipe_id: int
    title: str
    created_at: datetime
    missing_languages: list[str]
    stale_languages: list[str]


@dataclass
class TranslationBatchStartResult:
    mode: str
    limit: int
    recipe_count: int
    item_count: int
    external_job_id: str
    status: str


@dataclass
class GermanTranslationAuditItem:
    translation_id: int
    recipe_id: int
    recipe_title: str
    quality_flag: str
    english_score: float
    german_score: float
    marker_hits: int
    reason: str
    title_preview: str
    instructions_preview: str
    updated_at: datetime


@dataclass
class GermanTranslationAuditReport:
    scanned_count: int
    total_de_rows: int
    suspect_count: int
    items: list[GermanTranslationAuditItem]
    flagged_count: int = 0


@dataclass
class GermanTranslationRepairReport:
    dry_run: bool
    limit: int
    candidate_count: int
    updated_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    errors: list[str] = field(default_factory=list)


class TranslateApiError(RuntimeError):
    pass


class TranslationBatchConflictError(RuntimeError):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def set_translation_provider_for_testing(provider: TranslationProvider | None) -> None:
    global _PROVIDER_OVERRIDE
    _PROVIDER_OVERRIDE = provider


def get_translation_provider() -> TranslationProvider:
    if _PROVIDER_OVERRIDE is not None:
        return _PROVIDER_OVERRIDE
    return resolve_translation_provider(get_settings())


def normalize_lang(value: str, fallback: str = "de") -> str:
    token = str(value or "").strip().lower().replace("_", "-")
    if not token:
        return fallback
    return token.split("-", 1)[0]


def get_source_language() -> str:
    runtime_settings = get_settings()
    return normalize_lang(runtime_settings.translate_source_lang, fallback="de")


def get_target_languages() -> list[str]:
    runtime_settings = get_settings()
    source_lang = get_source_language()
    normalized: list[str] = []
    for value in runtime_settings.translate_target_langs:
        lang = normalize_lang(str(value), fallback="")
        if not lang or lang == source_lang:
            continue
        if lang not in normalized:
            normalized.append(lang)
    return normalized


def is_probably_english(text: str) -> bool:
    return translation_helpers.is_probably_english(text)

def is_probably_german(text: str) -> bool:
    return translation_helpers.is_probably_german(text)

def _analyze_de_translation_language(title: str, instructions: str) -> tuple[bool, float, float, int, str]:
    return translation_helpers._analyze_de_translation_language(title, instructions)

def get_effective_batch_limit(limit: int | None) -> int:
    runtime_settings = get_settings()
    configured = int(runtime_settings.translate_max_recipes_per_run or 20)
    if configured <= 0:
        configured = 20
    if limit is None:
        return configured
    return max(1, min(int(limit), configured))


def can_translate() -> bool:
    runtime_settings = get_settings()
    return bool(runtime_settings.translateapi_enabled)


def should_auto_translate_on_publish() -> bool:
    runtime_settings = get_settings()
    return can_translate() and bool(runtime_settings.translate_auto_on_publish)


def _api_base_url() -> str:
    runtime_settings = get_settings()
    return str(runtime_settings.translateapi_base_url or "https://api.translateapi.ai/api/v1").rstrip("/")


def _build_translateapi_headers() -> dict[str, str]:
    runtime_settings = get_settings()
    api_key = (runtime_settings.translateapi_api_key or "").strip()
    if not api_key:
        raise TranslateApiError("TRANSLATEAPI_API_KEY fehlt.")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def _unwrap_payload(payload: Any) -> dict[str, Any]:
    return translation_helpers._unwrap_payload(payload)

def _extract_job_id(payload: Any) -> str | None:
    return translation_helpers._extract_job_id(payload)

def _normalize_job_status(value: Any) -> str:
    return translation_helpers._normalize_job_status(value)

def _to_int(value: Any, default: int = 0) -> int:
    return translation_helpers._to_int(value, default)

def _extract_progress(payload: Any, total_default: int = 0, completed_default: int = 0) -> tuple[int, int]:
    return translation_helpers._extract_progress(payload, total_default, completed_default)

def _extract_errors(payload: Any) -> list[str]:
    return translation_helpers._extract_errors(payload)

def _extract_result_items(payload: Any) -> list[dict[str, Any]]:
    return translation_helpers._extract_result_items(payload)

def submit_translateapi_batch_request(items: list[dict[str, Any]]) -> TranslationBatchStartResult:
    if not items:
        raise TranslateApiError("Es wurden keine Batch-Items erzeugt.")
    headers = _build_translateapi_headers()
    endpoint = f"{_api_base_url()}/translate/batch/"
    payload = {
        "items": items,
        "source_language": get_source_language(),
        "target_languages": get_target_languages(),
    }
    with httpx.Client(timeout=30.0) as client:
        response = client.post(endpoint, json=payload, headers=headers)
    response.raise_for_status()
    data = response.json()
    external_job_id = _extract_job_id(data)
    if not external_job_id:
        raise TranslateApiError("TranslateAPI hat keine job_id geliefert.")
    status = _normalize_job_status(_unwrap_payload(data).get("status") if isinstance(_unwrap_payload(data), dict) else "queued")
    return TranslationBatchStartResult(
        mode="batch",
        limit=0,
        recipe_count=0,
        item_count=len(items),
        external_job_id=external_job_id,
        status=status,
    )


def fetch_translateapi_job_status(external_job_id: str) -> dict[str, Any]:
    headers = _build_translateapi_headers()
    endpoint = f"{_api_base_url()}/jobs/{external_job_id}/"
    with httpx.Client(timeout=30.0) as client:
        response = client.get(endpoint, headers=headers)
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise TranslateApiError("Ungueltige Job-Antwort von TranslateAPI.")
    return payload


def build_recipe_ingredients_text(recipe: Recipe) -> str:
    lines: list[str] = []
    links = sorted(
        list(recipe.recipe_ingredients or []),
        key=lambda link: ((link.ingredient.name if link.ingredient else "").casefold(), link.quantity_text or ""),
    )
    for link in links:
        ingredient_name = (link.ingredient.name if link.ingredient else "").strip()
        if not ingredient_name:
            continue
        quantity = (link.quantity_text or "").strip()
        grams = f"|{int(link.grams)}g" if link.grams is not None else ""
        if quantity:
            lines.append(f"{quantity} {ingredient_name}{grams}".strip())
        else:
            lines.append(f"{ingredient_name}{grams}".strip())
    return "\n".join(lines)


def build_recipe_source_payload(recipe: Recipe) -> dict[str, str]:
    return {
        "title": (recipe.title or "").strip(),
        "description": (recipe.description or "").strip(),
        "instructions": (recipe.instructions or "").strip(),
        "ingredients_text": build_recipe_ingredients_text(recipe),
    }


def build_source_hash(payload: dict[str, str]) -> str:
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8", errors="ignore")).hexdigest()


def mark_recipe_translations_stale_if_needed(db: Session, recipe: Recipe) -> tuple[str, int]:
    payload = build_recipe_source_payload(recipe)
    source_hash = build_source_hash(payload)
    translations = db.scalars(select(RecipeTranslation).where(RecipeTranslation.recipe_id == recipe.id)).all()
    marked = 0
    for translation in translations:
        if translation.source_hash == source_hash:
            continue
        if not translation.stale:
            marked += 1
        translation.stale = True
    return source_hash, marked


def translate_payload(
    provider: TranslationProvider,
    payload: dict[str, str],
    *,
    source_lang: str,
    target_lang: str,
) -> dict[str, str]:
    translated: dict[str, str] = {}
    for key, value in payload.items():
        text = str(value or "")
        if not text:
            translated[key] = ""
            continue
        translations = provider.translate(text, [target_lang], source_lang=source_lang)
        translated[key] = str(translations.get(target_lang, text))
    return translated


def translate_recipe_languages(
    db: Session,
    recipe: Recipe,
    languages: list[str],
    *,
    source_lang: str,
    provider: TranslationProvider,
    source_hash: str | None = None,
    only_missing: bool = False,
    only_stale: bool = False,
) -> tuple[int, int, int]:
    if not languages:
        return 0, 0, 0
    payload = build_recipe_source_payload(recipe)
    current_hash = source_hash or build_source_hash(payload)
    existing_rows = db.scalars(select(RecipeTranslation).where(RecipeTranslation.recipe_id == recipe.id)).all()
    existing_by_lang = {row.language: row for row in existing_rows}
    created = 0
    updated = 0
    skipped = 0

    for language in languages:
        existing = existing_by_lang.get(language)
        if only_missing and existing is not None:
            skipped += 1
            continue
        if only_stale and (existing is None or not existing.stale):
            skipped += 1
            continue
        translated = translate_payload(provider, payload, source_lang=source_lang, target_lang=language)
        if existing is None:
            db.add(
                RecipeTranslation(
                    recipe_id=recipe.id,
                    language=language,
                    title=translated["title"][:255],
                    description=translated["description"],
                    instructions=translated["instructions"],
                    ingredients_text=translated["ingredients_text"],
                    source_hash=current_hash,
                    stale=False,
                    quality_flag=OK_FLAG,
                )
            )
            created += 1
            continue
        existing.title = translated["title"][:255]
        existing.description = translated["description"]
        existing.instructions = translated["instructions"]
        existing.ingredients_text = translated["ingredients_text"]
        existing.source_hash = current_hash
        existing.stale = False
        existing.quality_flag = OK_FLAG
        updated += 1
    return created, updated, skipped


def compute_translation_stats(db: Session) -> TranslationStats:
    target_languages = get_target_languages()
    published_ids = db.scalars(select(Recipe.id).where(Recipe.is_published.is_(True))).all()
    if not published_ids or not target_languages:
        return TranslationStats(
            published_recipes=len(published_ids),
            target_languages=target_languages,
            missing_translations=0,
            stale_translations=0,
        )
    rows = db.scalars(
        select(RecipeTranslation).where(
            RecipeTranslation.recipe_id.in_(published_ids),
            RecipeTranslation.language.in_(target_languages),
        )
    ).all()
    by_recipe: dict[int, set[str]] = {}
    stale_count = 0
    for row in rows:
        by_recipe.setdefault(int(row.recipe_id), set()).add(row.language)
        if row.stale:
            stale_count += 1
    missing_count = 0
    for recipe_id in published_ids:
        existing = by_recipe.get(int(recipe_id), set())
        missing_count += max(len(target_languages) - len(existing), 0)
    return TranslationStats(
        published_recipes=len(published_ids),
        target_languages=target_languages,
        missing_translations=missing_count,
        stale_translations=stale_count,
    )


def audit_german_translations(
    db: Session,
    *,
    limit: int = 50,
    persist_flags: bool = False,
) -> GermanTranslationAuditReport:
    safe_limit = max(1, min(int(limit or 50), 500))
    rows = db.scalars(
        select(RecipeTranslation)
        .where(RecipeTranslation.language == "de")
        .order_by(RecipeTranslation.updated_at.desc(), RecipeTranslation.id.desc())
    ).all()
    recipe_ids = sorted({int(row.recipe_id) for row in rows})
    recipe_map = {
        int(recipe.id): recipe
        for recipe in db.scalars(select(Recipe).where(Recipe.id.in_(recipe_ids))).all()
    }
    suspect_count = 0
    flagged_count = 0
    items: list[GermanTranslationAuditItem] = []
    for row in rows:
        suspect, english_score, german_score, marker_hits, reason = _analyze_de_translation_language(
            row.title,
            row.instructions,
        )
        expected_flag = SUSPECT_FLAG if suspect else OK_FLAG
        if persist_flags and row.quality_flag != expected_flag:
            row.quality_flag = expected_flag
            flagged_count += 1
        if not suspect:
            continue
        suspect_count += 1
        if len(items) >= safe_limit:
            continue
        recipe_title = ""
        recipe = recipe_map.get(int(row.recipe_id))
        if recipe:
            recipe_title = str(recipe.title or "").strip()
        items.append(
            GermanTranslationAuditItem(
                translation_id=int(row.id),
                recipe_id=int(row.recipe_id),
                recipe_title=recipe_title or f"Rezept #{row.recipe_id}",
                quality_flag=str(row.quality_flag or OK_FLAG),
                english_score=float(english_score),
                german_score=float(german_score),
                marker_hits=int(marker_hits),
                reason=reason,
                title_preview=str(row.title or "")[:120],
                instructions_preview=str(row.instructions or "")[:240],
                updated_at=row.updated_at,
            )
        )
    if persist_flags and flagged_count > 0:
        db.flush()
    return GermanTranslationAuditReport(
        scanned_count=len(rows),
        total_de_rows=len(rows),
        suspect_count=suspect_count,
        items=items,
        flagged_count=flagged_count,
    )


def _build_repair_source_payload(
    recipe: Recipe,
    en_translation: RecipeTranslation | None,
) -> tuple[dict[str, str], str]:
    source_payload = build_recipe_source_payload(recipe)
    has_native_source = bool(source_payload.get("title")) and bool(source_payload.get("instructions"))
    if has_native_source:
        return source_payload, get_source_language()
    if en_translation is not None:
        return (
            {
                "title": str(en_translation.title or "").strip(),
                "description": str(en_translation.description or "").strip(),
                "instructions": str(en_translation.instructions or "").strip(),
                "ingredients_text": str(en_translation.ingredients_text or "").strip(),
            },
            "en",
        )
    return source_payload, get_source_language()


def repair_suspect_german_translations(
    db: Session,
    *,
    limit: int = 50,
    dry_run: bool = False,
) -> GermanTranslationRepairReport:
    safe_limit = max(1, min(int(limit or 50), 500))
    audit_report = audit_german_translations(db, limit=safe_limit, persist_flags=not dry_run)
    candidate_count = min(audit_report.suspect_count, safe_limit)
    report = GermanTranslationRepairReport(
        dry_run=bool(dry_run),
        limit=safe_limit,
        candidate_count=candidate_count,
    )
    if dry_run:
        return report
    if not can_translate():
        report.error_count += 1
        report.errors.append("TRANSLATEAPI_ENABLED ist deaktiviert.")
        return report
    provider = get_translation_provider()
    suspect_rows = db.scalars(
        select(RecipeTranslation)
        .where(
            RecipeTranslation.language == "de",
            RecipeTranslation.quality_flag == SUSPECT_FLAG,
        )
        .order_by(RecipeTranslation.updated_at.desc(), RecipeTranslation.id.desc())
        .limit(safe_limit)
    ).all()
    if not suspect_rows:
        return report
    recipe_ids = sorted({int(row.recipe_id) for row in suspect_rows})
    recipe_map = {
        int(recipe.id): recipe
        for recipe in db.scalars(
            select(Recipe)
            .where(Recipe.id.in_(recipe_ids), Recipe.is_published.is_(True))
            .options(selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient))
        ).all()
    }
    en_map = {
        int(row.recipe_id): row
        for row in db.scalars(
            select(RecipeTranslation).where(
                RecipeTranslation.recipe_id.in_(recipe_ids),
                RecipeTranslation.language == "en",
            )
        ).all()
    }
    for index, row in enumerate(suspect_rows, start=1):
        recipe = recipe_map.get(int(row.recipe_id))
        if recipe is None:
            report.skipped_count += 1
            report.error_count += 1
            report.errors.append(f"recipe_id={row.recipe_id}: published recipe not found.")
            continue
        try:
            source_payload, source_lang = _build_repair_source_payload(recipe, en_map.get(int(row.recipe_id)))
            translated = translate_payload(
                provider,
                source_payload,
                source_lang=source_lang,
                target_lang="de",
            )
            row.title = str(translated.get("title") or source_payload.get("title") or "")[:255]
            row.description = str(translated.get("description") or source_payload.get("description") or "")
            row.instructions = str(translated.get("instructions") or source_payload.get("instructions") or "")
            row.ingredients_text = str(translated.get("ingredients_text") or source_payload.get("ingredients_text") or "")
            row.source_hash = build_source_hash(source_payload)
            row.stale = False
            row.quality_flag = OK_FLAG
            report.updated_count += 1
            if index % 10 == 0:
                db.flush()
        except Exception as exc:
            report.skipped_count += 1
            report.error_count += 1
            report.errors.append(f"translation_id={row.id}: {exc}")
    db.flush()
    return report


def _get_candidate_recipe_ids(db: Session, mode: str, target_languages: list[str]) -> list[int]:
    published_ids = db.scalars(
        select(Recipe.id).where(Recipe.is_published.is_(True)).order_by(Recipe.created_at.desc(), Recipe.id.desc())
    ).all()
    if not published_ids or not target_languages:
        return []
    rows = db.scalars(
        select(RecipeTranslation).where(
            RecipeTranslation.recipe_id.in_(published_ids),
            RecipeTranslation.language.in_(target_languages),
        )
    ).all()
    lang_map: dict[int, set[str]] = {}
    stale_map: dict[int, bool] = {}
    for row in rows:
        recipe_id = int(row.recipe_id)
        lang_map.setdefault(recipe_id, set()).add(row.language)
        stale_map[recipe_id] = stale_map.get(recipe_id, False) or bool(row.stale)
    candidates: list[int] = []
    for recipe_id in published_ids:
        recipe_key = int(recipe_id)
        if mode == "stale":
            if stale_map.get(recipe_key):
                candidates.append(recipe_key)
            continue
        existing_langs = lang_map.get(recipe_key, set())
        if len(existing_langs) < len(target_languages):
            candidates.append(recipe_key)
    return candidates


def get_translation_queue(db: Session, limit: int = 50) -> list[TranslationQueueItem]:
    safe_limit = max(1, min(int(limit), 500))
    target_languages = get_target_languages()
    if not target_languages:
        return []
    recipes = db.scalars(
        select(Recipe)
        .where(Recipe.is_published.is_(True))
        .order_by(Recipe.created_at.desc(), Recipe.id.desc())
        .limit(safe_limit)
    ).all()
    if not recipes:
        return []
    recipe_ids = [int(recipe.id) for recipe in recipes]
    translation_rows = db.scalars(
        select(RecipeTranslation).where(
            RecipeTranslation.recipe_id.in_(recipe_ids),
            RecipeTranslation.language.in_(target_languages),
        )
    ).all()
    by_recipe_lang: dict[int, dict[str, RecipeTranslation]] = {}
    for row in translation_rows:
        by_recipe_lang.setdefault(int(row.recipe_id), {})[row.language] = row
    queue: list[TranslationQueueItem] = []
    for recipe in recipes:
        lang_rows = by_recipe_lang.get(int(recipe.id), {})
        missing_languages = [lang for lang in target_languages if lang not in lang_rows]
        stale_languages = [lang for lang in target_languages if lang in lang_rows and bool(lang_rows[lang].stale)]
        if not missing_languages and not stale_languages:
            continue
        queue.append(
            TranslationQueueItem(
                recipe_id=int(recipe.id),
                title=str(recipe.title or "").strip(),
                created_at=recipe.created_at,
                missing_languages=missing_languages,
                stale_languages=stale_languages,
            )
        )
    return queue


def run_translation_for_recipe_ids(
    db: Session,
    recipe_ids: list[int],
    *,
    mode: str = "missing",
    limit: int | None = None,
) -> TranslationRunReport:
    normalized_mode = "stale" if str(mode).strip().lower() == "stale" else "missing"
    effective_limit = get_effective_batch_limit(limit)
    report = TranslationRunReport(mode=normalized_mode, limit=effective_limit)
    if not can_translate():
        report.errors.append("TRANSLATEAPI_ENABLED ist deaktiviert.")
        return report
    source_lang = get_source_language()
    target_languages = get_target_languages()
    if not target_languages:
        report.errors.append("Keine Zielsprachen konfiguriert.")
        return report
    provider = get_translation_provider()
    ordered_ids: list[int] = []
    seen: set[int] = set()
    for item in recipe_ids:
        try:
            recipe_id = int(item)
        except (TypeError, ValueError):
            continue
        if recipe_id <= 0 or recipe_id in seen:
            continue
        seen.add(recipe_id)
        ordered_ids.append(recipe_id)
    for index, recipe_id in enumerate(ordered_ids[:effective_limit], start=1):
        recipe = db.scalar(
            select(Recipe)
            .where(Recipe.id == recipe_id, Recipe.is_published.is_(True))
            .options(selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient))
        )
        if not recipe:
            report.skipped += 1
            continue
        try:
            source_hash, _ = mark_recipe_translations_stale_if_needed(db, recipe)
            created, updated, skipped = translate_recipe_languages(
                db,
                recipe,
                target_languages,
                source_lang=source_lang,
                provider=provider,
                source_hash=source_hash,
                only_missing=normalized_mode == "missing",
                only_stale=normalized_mode == "stale",
            )
            report.created += created
            report.updated += updated
            report.skipped += skipped
            report.processed_recipes += 1
            if index % 10 == 0:
                db.flush()
        except Exception as exc:
            report.errors.append(f"recipe_id={recipe_id}: {exc}")
    db.flush()
    return report


def run_translation_batch(db: Session, *, mode: str, limit: int | None = None) -> TranslationRunReport:
    normalized_mode = "stale" if str(mode).strip().lower() == "stale" else "missing"
    effective_limit = get_effective_batch_limit(limit)
    report = TranslationRunReport(mode=normalized_mode, limit=effective_limit)
    if not can_translate():
        report.errors.append("TRANSLATEAPI_ENABLED ist deaktiviert.")
        return report

    target_languages = get_target_languages()
    if not target_languages:
        report.errors.append("Keine Zielsprachen konfiguriert.")
        return report

    candidate_ids = _get_candidate_recipe_ids(db, normalized_mode, target_languages)[:effective_limit]
    return run_translation_for_recipe_ids(
        db,
        candidate_ids,
        mode=normalized_mode,
        limit=effective_limit,
    )


def _build_batch_external_id(recipe_id: int, language: str, source_hash: str) -> str:
    from app.translation_batch_service import _build_batch_external_id as _impl

    return _impl(recipe_id, language, source_hash)


def _prepare_batch_items(db: Session, *, mode: str, limit: int | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    from app.translation_batch_service import _prepare_batch_items as _impl

    return _impl(db, mode=mode, limit=limit)


def start_translation_batch_job(
    db: Session,
    *,
    mode: str,
    limit: int | None,
    admin_id: int,
) -> TranslationBatchJob:
    from app.translation_batch_service import start_translation_batch_job as _impl

    return _impl(db, mode=mode, limit=limit, admin_id=admin_id)


def get_recent_translation_jobs(db: Session, limit: int = 20) -> list[TranslationBatchJob]:
    from app.translation_batch_service import get_recent_translation_jobs as _impl

    return _impl(db, limit=limit)


def find_translation_batch_job(db: Session, job_id: str) -> TranslationBatchJob | None:
    from app.translation_batch_service import find_translation_batch_job as _impl

    return _impl(db, job_id)


def _parse_result_payload(item: dict[str, Any]) -> dict[str, str]:
    from app.translation_batch_service import _parse_result_payload as _impl

    return _impl(item)


def apply_translateapi_job_results(
    db: Session,
    job: TranslationBatchJob,
    payload: dict[str, Any],
) -> tuple[int, int, int, list[str]]:
    from app.translation_batch_service import apply_translateapi_job_results as _impl

    return _impl(db, job, payload)


def poll_translation_batch_job(
    db: Session,
    job: TranslationBatchJob,
    *,
    max_polls: int | None = None,
    poll_interval_seconds: float | None = None,
) -> TranslationBatchJob:
    from app.translation_batch_service import poll_translation_batch_job as _impl

    return _impl(
        db,
        job,
        max_polls=max_polls,
        poll_interval_seconds=poll_interval_seconds,
    )


def _before_flush_mark_stale(session: Session, flush_context: Any, instances: Any) -> None:
    _ = flush_context
    _ = instances
    new_published_recipes = session.info.setdefault(AUTO_TRANSLATION_NEW_RECIPES_KEY, [])
    for obj in session.new:
        if not isinstance(obj, Recipe):
            continue
        if not obj.is_published:
            continue
        if obj.source not in {"admin_manual", "submission"}:
            continue
        new_published_recipes.append(obj)

    for obj in session.dirty:
        if not isinstance(obj, Recipe):
            continue
        if not obj.id or not obj.is_published:
            continue
        if obj in session.new:
            continue
        if not session.is_modified(obj, include_collections=True):
            continue
        mark_recipe_translations_stale_if_needed(session, obj)


def _after_flush_collect_new_published(session: Session, flush_context: Any) -> None:
    _ = flush_context
    pending_recipes = session.info.pop(AUTO_TRANSLATION_NEW_RECIPES_KEY, [])
    if not pending_recipes:
        return
    pending_ids = session.info.setdefault(AUTO_TRANSLATION_RECIPE_IDS_KEY, set())
    for recipe in pending_recipes:
        if recipe.id:
            pending_ids.add(int(recipe.id))


def _prepare_post_commit_auto_translate_context(
    session: Session,
) -> tuple[list[int], str, list[str], TranslationProvider, Any] | None:
    recipe_ids = session.info.pop(AUTO_TRANSLATION_RECIPE_IDS_KEY, set())
    if not recipe_ids:
        return None
    if not should_auto_translate_on_publish():
        return None

    target_languages = get_target_languages()
    if not target_languages:
        return None
    provider = get_translation_provider()
    bind = session.get_bind()
    if bind is None:
        return None
    source_lang = get_source_language()
    return sorted(int(recipe_id) for recipe_id in recipe_ids), source_lang, target_languages, provider, bind


def _run_post_commit_auto_translate_write_phase(
    auto_session: Session,
    *,
    recipe_ids: list[int],
    source_lang: str,
    target_languages: list[str],
    provider: TranslationProvider,
) -> None:
    for recipe_id in recipe_ids:
        recipe = auto_session.scalar(
            select(Recipe)
            .where(Recipe.id == recipe_id, Recipe.is_published.is_(True))
            .options(selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient))
        )
        if not recipe:
            continue
        source_hash, _ = mark_recipe_translations_stale_if_needed(auto_session, recipe)
        translate_recipe_languages(
            auto_session,
            recipe,
            target_languages,
            source_lang=source_lang,
            provider=provider,
            source_hash=source_hash,
            only_missing=True,
            only_stale=False,
        )


def _finalize_post_commit_auto_translate_session(auto_session: Session, *, failed: bool) -> None:
    if failed:
        auto_session.rollback()
        return
    auto_session.commit()


def _after_commit_auto_translate(session: Session) -> None:
    context = _prepare_post_commit_auto_translate_context(session)
    if not context:
        return
    recipe_ids, source_lang, target_languages, provider, bind = context

    auto_session_factory = sessionmaker(bind=bind, autoflush=False, autocommit=False)
    auto_session = auto_session_factory()
    failed = False
    try:
        _run_post_commit_auto_translate_write_phase(
            auto_session,
            recipe_ids=recipe_ids,
            source_lang=source_lang,
            target_languages=target_languages,
            provider=provider,
        )
    except Exception:
        failed = True
    finally:
        _finalize_post_commit_auto_translate_session(auto_session, failed=failed)
        auto_session.close()


def register_translation_event_hooks() -> None:
    global _HOOKS_REGISTERED
    if _HOOKS_REGISTERED:
        return
    event.listen(Session, "before_flush", _before_flush_mark_stale)
    event.listen(Session, "after_flush", _after_flush_collect_new_published)
    event.listen(Session, "after_commit", _after_commit_auto_translate)
    _HOOKS_REGISTERED = True

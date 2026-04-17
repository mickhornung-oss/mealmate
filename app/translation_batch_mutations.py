from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import translation_service as legacy_translation
from app.models import Recipe, RecipeIngredient
from app.translation_models import RecipeTranslation, TranslationBatchJob


def apply_job_poll_snapshot(
    job: TranslationBatchJob,
    *,
    status_value: str,
    total_value: int,
    completed_value: int,
    error_messages: list[str],
    now: datetime,
) -> None:
    job.status = status_value
    if total_value > 0:
        job.total_items = total_value
    if completed_value > 0:
        upper_bound = max(job.total_items, completed_value)
        job.completed_items = min(completed_value, upper_bound)
    job.last_polled_at = now
    if error_messages:
        job.error_count = len(error_messages)
        job.error_message = " | ".join(error_messages)[:2000]


def _parse_result_payload(item: dict[str, Any]) -> dict[str, str]:
    candidates = [
        item.get("translated_payload"),
        item.get("translation"),
        item.get("result"),
        item.get("output"),
        item.get("payload"),
        item.get("content"),
    ]
    for candidate in candidates:
        if isinstance(candidate, dict):
            if isinstance(candidate.get("content"), dict):
                candidate = candidate["content"]
            return {
                "title": str(candidate.get("title") or candidate.get("name") or "").strip(),
                "description": str(candidate.get("description") or candidate.get("summary") or "").strip(),
                "instructions": str(candidate.get("instructions") or candidate.get("steps") or "").strip(),
                "ingredients_text": str(candidate.get("ingredients_text") or candidate.get("ingredients") or "").strip(),
            }
        if isinstance(candidate, str) and candidate.strip():
            text = candidate.strip()
            return {
                "title": text,
                "description": text,
                "instructions": text,
                "ingredients_text": "",
            }

    return {
        "title": str(item.get("title") or "").strip(),
        "description": str(item.get("description") or "").strip(),
        "instructions": str(item.get("instructions") or "").strip(),
        "ingredients_text": str(item.get("ingredients_text") or "").strip(),
    }


def apply_translateapi_job_results(
    db: Session,
    job: TranslationBatchJob,
    payload: dict[str, Any],
) -> tuple[int, int, int, list[str]]:
    try:
        metadata_items = json.loads(job.items_json or "[]")
    except json.JSONDecodeError:
        metadata_items = []
    by_external_id = {
        str(item.get("external_id") or "").strip(): item
        for item in metadata_items
        if isinstance(item, dict) and str(item.get("external_id") or "").strip()
    }
    if not by_external_id:
        return 0, 0, 0, ["Job-Metadaten fehlen oder sind ungueltig."]

    recipe_ids = sorted({int(item.get("recipe_id")) for item in by_external_id.values() if str(item.get("recipe_id", "")).isdigit()})
    recipes = db.scalars(
        select(Recipe)
        .where(Recipe.id.in_(recipe_ids), Recipe.is_published.is_(True))
        .options(selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient))
    ).all()
    recipe_map = {int(recipe.id): recipe for recipe in recipes}

    target_languages = sorted({str(item.get("language") or "").strip() for item in by_external_id.values() if str(item.get("language") or "").strip()})
    existing_rows = db.scalars(
        select(RecipeTranslation).where(
            RecipeTranslation.recipe_id.in_(recipe_ids),
            RecipeTranslation.language.in_(target_languages),
        )
    ).all()
    existing_map = {(int(row.recipe_id), row.language): row for row in existing_rows}

    created = 0
    updated = 0
    skipped = 0
    errors: list[str] = []

    for result in legacy_translation._extract_result_items(payload):
        external_id = str(result.get("external_id") or result.get("id") or result.get("item_id") or "").strip()
        if not external_id:
            skipped += 1
            errors.append("Result item ohne external_id uebersprungen.")
            continue
        mapping = by_external_id.get(external_id)
        if not mapping:
            skipped += 1
            continue

        recipe_id = legacy_translation._to_int(mapping.get("recipe_id"), 0)
        language = str(mapping.get("language") or "").strip()
        source_hash = str(mapping.get("source_hash") or "").strip()
        recipe = recipe_map.get(recipe_id)
        if not recipe or not language:
            skipped += 1
            continue

        source_payload = legacy_translation.build_recipe_source_payload(recipe)
        translated_payload = _parse_result_payload(result)
        title_value = translated_payload["title"] or source_payload["title"]
        description_value = translated_payload["description"] or source_payload["description"]
        instructions_value = translated_payload["instructions"] or source_payload["instructions"]
        ingredients_value = translated_payload["ingredients_text"] or source_payload["ingredients_text"]

        row = existing_map.get((recipe_id, language))
        if row is None:
            row = RecipeTranslation(
                recipe_id=recipe_id,
                language=language,
                title=title_value[:255],
                description=description_value,
                instructions=instructions_value,
                ingredients_text=ingredients_value,
                source_hash=source_hash or legacy_translation.build_source_hash(source_payload),
                stale=False,
                quality_flag=legacy_translation.OK_FLAG,
            )
            db.add(row)
            existing_map[(recipe_id, language)] = row
            created += 1
            continue

        row.title = title_value[:255]
        row.description = description_value
        row.instructions = instructions_value
        row.ingredients_text = ingredients_value
        row.source_hash = source_hash or row.source_hash
        row.stale = False
        row.quality_flag = legacy_translation.OK_FLAG
        updated += 1

    return created, updated, skipped, errors


def finalize_completed_job(
    db: Session,
    job: TranslationBatchJob,
    payload: dict[str, Any],
    *,
    now: datetime,
) -> TranslationBatchJob:
    created, updated, skipped, apply_errors = apply_translateapi_job_results(db, job, payload)
    job.created_items = created
    job.updated_items = updated
    job.skipped_items = skipped
    if apply_errors:
        job.error_count = max(job.error_count, len(apply_errors))
        combined = (job.error_message or "") + " | " + " | ".join(apply_errors)
        job.error_message = combined.strip(" |")[:2000]
    if job.total_items <= 0:
        job.total_items = created + updated + skipped
    if job.completed_items <= 0:
        job.completed_items = job.total_items
    job.finished_at = now
    db.flush()
    return job


def finalize_terminal_job(job: TranslationBatchJob, *, status_value: str, now: datetime) -> TranslationBatchJob:
    job.status = status_value
    job.finished_at = now
    return job


def finalize_timeout_job(job: TranslationBatchJob, *, now: datetime) -> TranslationBatchJob:
    job.status = "timeout"
    job.finished_at = now
    return job


from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app import translation_service as legacy_translation
from app import translation_batch_mutations as batch_mutations
from app.models import Recipe, RecipeIngredient
from app.translation_models import RecipeTranslation, TranslationBatchJob

logger = logging.getLogger("mealmate.translation.batch")


def _build_batch_external_id(recipe_id: int, language: str, source_hash: str) -> str:
    return f"recipe:{recipe_id}:lang:{language}:hash:{source_hash[:12]}"


def _prepare_batch_items(db: Session, *, mode: str, limit: int | None) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int]:
    normalized_mode = "stale" if str(mode).strip().lower() == "stale" else "missing"
    source_lang = legacy_translation.get_source_language()
    target_languages = legacy_translation.get_target_languages()
    if not target_languages:
        return [], [], 0

    candidate_ids = legacy_translation._get_candidate_recipe_ids(db, normalized_mode, target_languages)[
        : legacy_translation.get_effective_batch_limit(limit)
    ]
    if not candidate_ids:
        return [], [], 0

    recipes = db.scalars(
        select(Recipe)
        .where(Recipe.id.in_(candidate_ids), Recipe.is_published.is_(True))
        .options(selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient))
        .order_by(Recipe.created_at.desc(), Recipe.id.desc())
    ).all()
    if not recipes:
        return [], [], 0

    recipe_map = {int(recipe.id): recipe for recipe in recipes}
    translation_rows = db.scalars(
        select(RecipeTranslation).where(
            RecipeTranslation.recipe_id.in_(candidate_ids),
            RecipeTranslation.language.in_(target_languages),
        )
    ).all()
    existing_by_key = {(int(row.recipe_id), row.language): row for row in translation_rows}

    items: list[dict[str, Any]] = []
    metadata: list[dict[str, Any]] = []
    recipes_with_items: set[int] = set()

    for recipe_id in candidate_ids:
        recipe = recipe_map.get(int(recipe_id))
        if not recipe:
            continue
        payload = legacy_translation.build_recipe_source_payload(recipe)
        source_hash = legacy_translation.build_source_hash(payload)
        for language in target_languages:
            existing = existing_by_key.get((int(recipe.id), language))
            if normalized_mode == "missing" and existing is not None:
                continue
            if normalized_mode == "stale" and (existing is None or not existing.stale):
                continue
            external_id = _build_batch_external_id(recipe.id, language, source_hash)
            items.append(
                {
                    "external_id": external_id,
                    "source_lang": source_lang,
                    "source_language": source_lang,
                    "target_lang": language,
                    "target_language": language,
                    "payload": payload,
                    "content": payload,
                }
            )
            metadata.append(
                {
                    "external_id": external_id,
                    "recipe_id": int(recipe.id),
                    "language": language,
                    "source_hash": source_hash,
                }
            )
            recipes_with_items.add(int(recipe.id))
    return items, metadata, len(recipes_with_items)


def _find_active_translation_batch_job(db: Session) -> TranslationBatchJob | None:
    return db.scalar(
        select(TranslationBatchJob)
        .where(TranslationBatchJob.status.notin_(legacy_translation.TERMINAL_JOB_STATUSES))
        .order_by(TranslationBatchJob.created_at.desc())
    )


def start_translation_batch_job(
    db: Session,
    *,
    mode: str,
    limit: int | None,
    admin_id: int,
) -> TranslationBatchJob:
    if not legacy_translation.can_translate():
        raise ValueError("TRANSLATEAPI_ENABLED ist deaktiviert.")
    runtime_settings = legacy_translation.get_settings()
    if not (runtime_settings.translateapi_api_key or "").strip():
        raise ValueError("TRANSLATEAPI_API_KEY ist nicht gesetzt.")
    normalized_mode = "stale" if str(mode).strip().lower() == "stale" else "missing"
    active_job = _find_active_translation_batch_job(db)
    if active_job is not None:
        logger.warning(
            "translation_batch_start_blocked active_job_id=%s active_status=%s mode=%s limit=%s admin_id=%s",
            active_job.external_job_id,
            active_job.status,
            normalized_mode,
            limit if limit is not None else "default",
            admin_id,
        )
        raise legacy_translation.TranslationBatchConflictError(
            f"Ein Translation-Batch-Job laeuft bereits (ID: {active_job.external_job_id})."
        )

    items, metadata, recipe_count = _prepare_batch_items(db, mode=normalized_mode, limit=limit)
    if not items:
        raise ValueError("Keine passenden veroeffentlichten Rezepte fuer diesen Batch-Run gefunden.")

    api_result = legacy_translation.submit_translateapi_batch_request(items)
    job = TranslationBatchJob(
        external_job_id=api_result.external_job_id,
        mode=normalized_mode,
        status=api_result.status,
        requested_recipe_count=recipe_count,
        total_items=len(items),
        completed_items=0,
        created_items=0,
        updated_items=0,
        skipped_items=0,
        error_count=0,
        error_message=None,
        items_json=legacy_translation.json.dumps(metadata, ensure_ascii=False),
        requested_by_admin_id=admin_id,
        started_at=legacy_translation.utc_now(),
        finished_at=None,
        last_polled_at=None,
    )
    db.add(job)
    db.flush()
    logger.info(
        "translation_batch_job_created external_job_id=%s mode=%s requested_recipe_count=%s total_items=%s admin_id=%s",
        job.external_job_id,
        normalized_mode,
        job.requested_recipe_count,
        job.total_items,
        admin_id,
    )
    return job


def get_recent_translation_jobs(db: Session, limit: int = 20) -> list[TranslationBatchJob]:
    safe_limit = max(1, min(int(limit), 200))
    return db.scalars(select(TranslationBatchJob).order_by(TranslationBatchJob.created_at.desc()).limit(safe_limit)).all()


def find_translation_batch_job(db: Session, job_id: str) -> TranslationBatchJob | None:
    token = str(job_id or "").strip()
    if not token:
        return None
    if token.isdigit():
        found = db.scalar(select(TranslationBatchJob).where(TranslationBatchJob.id == int(token)))
        if found:
            return found
    return db.scalar(select(TranslationBatchJob).where(TranslationBatchJob.external_job_id == token))


def _parse_result_payload(item: dict[str, Any]) -> dict[str, str]:
    return batch_mutations._parse_result_payload(item)


def apply_translateapi_job_results(
    db: Session,
    job: TranslationBatchJob,
    payload: dict[str, Any],
) -> tuple[int, int, int, list[str]]:
    return batch_mutations.apply_translateapi_job_results(db, job, payload)


def poll_translation_batch_job(
    db: Session,
    job: TranslationBatchJob,
    *,
    max_polls: int | None = None,
    poll_interval_seconds: float | None = None,
) -> TranslationBatchJob:
    if job.status in legacy_translation.TERMINAL_JOB_STATUSES:
        return job
    if not job.external_job_id:
        raise legacy_translation.TranslateApiError("Batch-Job hat keine externe Job-ID.")

    runtime_settings = legacy_translation.get_settings()
    poll_limit = max(1, int(max_polls or runtime_settings.translateapi_max_polls or 200))
    poll_interval = float(
        poll_interval_seconds if poll_interval_seconds is not None else runtime_settings.translateapi_poll_interval_seconds
    )
    poll_interval = max(0.0, poll_interval)

    for _ in range(poll_limit):
        payload = legacy_translation.fetch_translateapi_job_status(job.external_job_id)
        top = legacy_translation._unwrap_payload(payload)
        status_value = legacy_translation._normalize_job_status(top.get("status") if isinstance(top, dict) else None)
        total_value, completed_value = legacy_translation._extract_progress(
            payload, total_default=job.total_items, completed_default=job.completed_items
        )
        error_messages = legacy_translation._extract_errors(payload)
        now = legacy_translation.utc_now()

        batch_mutations.apply_job_poll_snapshot(
            job,
            status_value=status_value,
            total_value=total_value,
            completed_value=completed_value,
            error_messages=error_messages,
            now=now,
        )

        if status_value == "completed":
            return batch_mutations.finalize_completed_job(db, job, payload, now=now)

        if status_value in {"failed", "cancelled"}:
            batch_mutations.finalize_terminal_job(job, status_value=status_value, now=now)
            db.flush()
            return job

        db.flush()
        if poll_interval > 0:
            time.sleep(poll_interval)

    batch_mutations.finalize_timeout_job(job, now=legacy_translation.utc_now())
    db.flush()
    return job

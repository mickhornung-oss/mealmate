from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.config import get_settings
from app.translation_models import TranslationBatchJob
from app.translation_service import TranslationBatchStartResult, poll_translation_batch_job, start_translation_batch_job
from tests.helpers import create_admin_user, create_published_recipe, unique_email


def _configure_batch_settings(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "translateapi_enabled", True)
    monkeypatch.setattr(settings, "translate_auto_on_publish", False)
    monkeypatch.setattr(settings, "translate_target_langs", ["en"])
    monkeypatch.setattr(settings, "translate_source_lang", "de")
    monkeypatch.setattr(settings, "translate_max_recipes_per_run", 20)
    monkeypatch.setattr(settings, "translateapi_api_key", "test-api-key")
    monkeypatch.setattr(settings, "translateapi_poll_interval_seconds", 0)
    monkeypatch.setattr(settings, "translateapi_max_polls", 5)


def test_poll_job_uses_poll_snapshot_and_timeout_finalizer(db_session_factory, monkeypatch):
    _configure_batch_settings(monkeypatch)

    monkeypatch.setattr(
        "app.translation_service.submit_translateapi_batch_request",
        lambda items: TranslationBatchStartResult(
            mode="batch",
            limit=0,
            recipe_count=0,
            item_count=len(items),
            external_job_id="job-boundary-running-001",
            status="queued",
        ),
    )

    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("admin"), "AdminPass123!")
        create_published_recipe(db, admin.id, title="Boundary Running Recipe", is_published=True)
        start_translation_batch_job(db, mode="missing", limit=10, admin_id=admin.id)
        db.commit()

    monkeypatch.setattr(
        "app.translation_service.fetch_translateapi_job_status",
        lambda _external_job_id: {
            "job_id": "job-boundary-running-001",
            "status": "running",
            "progress": {"total": 1, "completed": 0},
        },
    )

    calls = {"snapshot": 0, "timeout": 0}

    def fake_snapshot(job, *, status_value, total_value, completed_value, error_messages, now):
        calls["snapshot"] += 1
        job.status = status_value
        job.total_items = total_value
        job.completed_items = completed_value
        job.last_polled_at = now
        if error_messages:
            job.error_message = " | ".join(error_messages)

    def fake_timeout(job, *, now):
        calls["timeout"] += 1
        job.status = "timeout"
        job.finished_at = now
        return job

    monkeypatch.setattr("app.translation_batch_mutations.apply_job_poll_snapshot", fake_snapshot)
    monkeypatch.setattr("app.translation_batch_mutations.finalize_timeout_job", fake_timeout)

    with db_session_factory() as db:
        job = db.scalar(select(TranslationBatchJob).where(TranslationBatchJob.external_job_id == "job-boundary-running-001"))
        assert job is not None
        poll_translation_batch_job(db, job, max_polls=1, poll_interval_seconds=0)
        db.commit()

    assert calls["snapshot"] == 1
    assert calls["timeout"] == 1


def test_poll_job_uses_completed_finalizer(db_session_factory, monkeypatch):
    _configure_batch_settings(monkeypatch)

    monkeypatch.setattr(
        "app.translation_service.submit_translateapi_batch_request",
        lambda items: TranslationBatchStartResult(
            mode="batch",
            limit=0,
            recipe_count=0,
            item_count=len(items),
            external_job_id="job-boundary-complete-001",
            status="queued",
        ),
    )

    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("admin"), "AdminPass123!")
        create_published_recipe(db, admin.id, title="Boundary Complete Recipe", is_published=True)
        start_translation_batch_job(db, mode="missing", limit=10, admin_id=admin.id)
        db.commit()

    monkeypatch.setattr(
        "app.translation_service.fetch_translateapi_job_status",
        lambda _external_job_id: {
            "job_id": "job-boundary-complete-001",
            "status": "completed",
            "progress": {"total": 1, "completed": 1},
            "results": [],
        },
    )

    calls = {"completed": 0}

    def fake_completed(db, job, payload, *, now):
        _ = db
        _ = payload
        calls["completed"] += 1
        job.status = "completed"
        job.finished_at = now or datetime.now(timezone.utc)
        return job

    monkeypatch.setattr("app.translation_batch_mutations.finalize_completed_job", fake_completed)

    with db_session_factory() as db:
        job = db.scalar(select(TranslationBatchJob).where(TranslationBatchJob.external_job_id == "job-boundary-complete-001"))
        assert job is not None
        poll_translation_batch_job(db, job, max_polls=1, poll_interval_seconds=0)
        db.commit()

    assert calls["completed"] == 1


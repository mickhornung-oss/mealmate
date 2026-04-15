import json

from sqlalchemy import select

from app.config import get_settings
from app.translation_models import RecipeTranslation, TranslationBatchJob
from app.translation_service import (
    TranslationBatchStartResult,
    poll_translation_batch_job,
    start_translation_batch_job,
)
from tests.helpers import create_admin_user, create_published_recipe, post_form, set_auth_cookie, unique_email


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


def test_admin_start_batch_creates_job(client, db_session_factory, monkeypatch):
    _configure_batch_settings(monkeypatch)

    captured = {"items": []}

    def fake_submit(items):
        captured["items"] = list(items)
        return TranslationBatchStartResult(
            mode="batch",
            limit=0,
            recipe_count=0,
            item_count=len(items),
            external_job_id="job-batch-start-001",
            status="queued",
        )

    monkeypatch.setattr("app.translation_service.submit_translateapi_batch_request", fake_submit)

    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("admin"), "AdminPass123!")
        create_published_recipe(db, admin.id, title="Batch Start Recipe", is_published=True)
        admin_uid = admin.user_uid
        admin_role = admin.role

    set_auth_cookie(client, admin_uid, admin_role)
    response = post_form(
        client,
        "/admin/translations/batch/start",
        {"mode": "missing", "limit": "10"},
        referer_page="/admin/translations",
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert "batch_started=1" in response.headers.get("location", "")
    assert captured["items"]

    with db_session_factory() as db:
        job = db.scalar(select(TranslationBatchJob).where(TranslationBatchJob.external_job_id == "job-batch-start-001"))
        assert job is not None
        assert job.status == "queued"
        assert job.mode == "missing"
        assert job.requested_recipe_count == 1
        assert job.total_items == 1


def test_poll_batch_job_writes_translations(db_session_factory, monkeypatch):
    _configure_batch_settings(monkeypatch)

    def fake_submit(items):
        return TranslationBatchStartResult(
            mode="batch",
            limit=0,
            recipe_count=0,
            item_count=len(items),
            external_job_id="job-poll-001",
            status="queued",
        )

    monkeypatch.setattr("app.translation_service.submit_translateapi_batch_request", fake_submit)

    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("admin"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="Batch Poll Recipe", is_published=True)
        recipe_id = recipe.id
        job = start_translation_batch_job(db, mode="missing", limit=10, admin_id=admin.id)
        db.commit()
        db.refresh(job)
        metadata = json.loads(job.items_json)
        external_id = metadata[0]["external_id"]

    def fake_status(_external_job_id: str):
        return {
            "job_id": "job-poll-001",
            "status": "completed",
            "progress": {"total": 1, "completed": 1},
            "results": [
                {
                    "external_id": external_id,
                    "payload": {
                        "title": "English Title",
                        "description": "English Description",
                        "instructions": "English Instructions",
                        "ingredients_text": "English Ingredients",
                    },
                }
            ],
        }

    monkeypatch.setattr("app.translation_service.fetch_translateapi_job_status", fake_status)

    with db_session_factory() as db:
        job = db.scalar(select(TranslationBatchJob).where(TranslationBatchJob.external_job_id == "job-poll-001"))
        assert job is not None
        poll_translation_batch_job(db, job, max_polls=1, poll_interval_seconds=0)
        db.commit()

    with db_session_factory() as db:
        job = db.scalar(select(TranslationBatchJob).where(TranslationBatchJob.external_job_id == "job-poll-001"))
        assert job is not None
        assert job.status == "completed"
        assert job.created_items == 1
        assert job.updated_items == 0
        assert job.skipped_items == 0
        row = db.scalar(
            select(RecipeTranslation).where(
                RecipeTranslation.recipe_id == recipe_id,
                RecipeTranslation.language == "en",
            )
        )
        assert row is not None
        assert row.title == "English Title"
        assert row.stale is False

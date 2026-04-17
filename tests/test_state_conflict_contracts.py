from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.config import get_settings
from app.models import RecipeImage, RecipeImageChangeFile, RecipeImageChangeRequest, RecipeSubmission
from app.translation_models import TranslationBatchJob
from tests.helpers import (
    SMALL_PNG_BYTES,
    create_admin_user,
    create_normal_user,
    create_pending_submission,
    create_published_recipe,
    post_form,
    set_auth_cookie,
    unique_email,
)


def _configure_translation_settings(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "translateapi_enabled", True)
    monkeypatch.setattr(settings, "translate_auto_on_publish", False)
    monkeypatch.setattr(settings, "translate_target_langs", ["en"])
    monkeypatch.setattr(settings, "translate_source_lang", "de")
    monkeypatch.setattr(settings, "translate_max_recipes_per_run", 20)
    monkeypatch.setattr(settings, "translateapi_api_key", "test-api-key")
    monkeypatch.setattr(settings, "translateapi_poll_interval_seconds", 0)
    monkeypatch.setattr(settings, "translateapi_max_polls", 5)


def test_translation_batch_start_conflicts_when_active_job_exists(client, db_session_factory, monkeypatch):
    _configure_translation_settings(monkeypatch)
    calls = {"warning": 0}

    def fake_warning(message, *args, **kwargs):
        _ = args
        _ = kwargs
        if "translation_batch_start_conflict" in str(message):
            calls["warning"] += 1

    monkeypatch.setattr("app.routers.translations.logger.warning", fake_warning)

    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("state-batch-admin"), "AdminPass123!")
        create_published_recipe(db, admin.id, title="State Batch Recipe", is_published=True)
        db.add(
            TranslationBatchJob(
                external_job_id="job-running-contract-001",
                mode="missing",
                status="running",
                requested_recipe_count=1,
                total_items=1,
                completed_items=0,
                created_items=0,
                updated_items=0,
                skipped_items=0,
                error_count=0,
                items_json="[]",
                requested_by_admin_id=admin.id,
                started_at=datetime.now(timezone.utc),
            )
        )
        db.commit()
        set_auth_cookie(client, admin.user_uid, admin.role)

    response = post_form(
        client,
        "/admin/translations/batch/start",
        {"mode": "missing", "limit": "10"},
        referer_page="/admin/translations",
        follow_redirects=False,
    )
    assert response.status_code == 409
    assert "laeuft bereits" in response.text
    assert calls["warning"] == 1


def test_image_change_approve_second_call_conflicts_without_duplicate_side_effect(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("state-img-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("state-img-user"), "UserPass123!")
        recipe = create_published_recipe(db, admin.id, title="State Image Conflict", is_published=True)
        db.add(
            RecipeImage(
                recipe_id=recipe.id,
                filename="existing.png",
                content_type="image/png",
                data=SMALL_PNG_BYTES,
                is_primary=True,
            )
        )
        request_row = RecipeImageChangeRequest(
            recipe_id=recipe.id,
            requester_user_id=user.id,
            status="pending",
        )
        db.add(request_row)
        db.flush()
        db.add(
            RecipeImageChangeFile(
                request_id=request_row.id,
                filename="proposal.png",
                content_type="image/png",
                data=SMALL_PNG_BYTES,
            )
        )
        db.commit()
        request_id = request_row.id
        recipe_id = recipe.id
        set_auth_cookie(client, admin.user_uid, admin.role)

    first = post_form(
        client,
        f"/admin/image-change-requests/{request_id}/approve",
        {"admin_note": "approved-first"},
        referer_page=f"/admin/image-change-requests/{request_id}",
        follow_redirects=False,
    )
    assert first.status_code == 303

    second = post_form(
        client,
        f"/admin/image-change-requests/{request_id}/approve",
        {"admin_note": "approved-second"},
        referer_page=f"/admin/image-change-requests/{request_id}",
        follow_redirects=False,
    )
    assert second.status_code == 409

    with db_session_factory() as db:
        persisted = db.scalar(select(RecipeImageChangeRequest).where(RecipeImageChangeRequest.id == request_id))
        assert persisted is not None
        assert persisted.status == "approved"
        images = db.scalars(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id)).all()
        assert len(images) == 2


def test_submission_reject_replay_is_idempotent_redirect(client, db_session_factory, monkeypatch):
    calls = {"replay": 0}

    def fake_info(message, *args, **kwargs):
        _ = args
        _ = kwargs
        if "submission_reject_replay" in str(message):
            calls["replay"] += 1

    monkeypatch.setattr("app.routers.submissions.logger.info", fake_info)

    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("state-reject-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("state-reject-user"), "UserPass123!")
        submission = create_pending_submission(db, user.id, "State Reject Replay")
        submission_id = submission.id
        set_auth_cookie(client, admin.user_uid, admin.role)

    first = post_form(
        client,
        f"/admin/submissions/{submission_id}/reject",
        {"admin_note": "first-reject-note"},
        referer_page=f"/admin/submissions/{submission_id}",
        follow_redirects=False,
    )
    assert first.status_code == 303

    second = post_form(
        client,
        f"/admin/submissions/{submission_id}/reject",
        {"admin_note": "second-reject-note"},
        referer_page=f"/admin/submissions/{submission_id}",
        follow_redirects=False,
    )
    assert second.status_code == 303

    with db_session_factory() as db:
        persisted = db.scalar(select(RecipeSubmission).where(RecipeSubmission.id == submission_id))
        assert persisted is not None
        assert persisted.status == "rejected"
        assert persisted.admin_note == "first-reject-note"
    assert calls["replay"] >= 1


def test_submission_approve_value_error_is_mapped_to_conflict(client, db_session_factory, monkeypatch):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("state-approve-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("state-approve-user"), "UserPass123!")
        submission = create_pending_submission(db, user.id, "State Approve Conflict")
        submission_id = submission.id
        set_auth_cookie(client, admin.user_uid, admin.role)

    def fake_publish_submission_as_recipe(db, submission, actor_admin_id):
        _ = db
        _ = submission
        _ = actor_admin_id
        raise ValueError("Submission has already been published.")

    monkeypatch.setattr("app.routers.submissions.publish_submission_as_recipe", fake_publish_submission_as_recipe)

    response = post_form(
        client,
        f"/admin/submissions/{submission_id}/approve",
        {"admin_note": "approve"},
        referer_page=f"/admin/submissions/{submission_id}",
        follow_redirects=False,
    )
    assert response.status_code == 409

    with db_session_factory() as db:
        persisted = db.scalar(select(RecipeSubmission).where(RecipeSubmission.id == submission_id))
        assert persisted is not None
        assert persisted.status == "pending"

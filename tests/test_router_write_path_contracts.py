from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

from sqlalchemy import select

from app.models import RecipeSubmission
from tests.helpers import (
    create_admin_user,
    create_normal_user,
    create_pending_submission,
    post_form,
    set_auth_cookie,
    unique_email,
)


def _auth_as_admin(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("router-admin"), "AdminPass123!")
        admin_uid = admin.user_uid
        admin_role = admin.role
    set_auth_cookie(client, admin_uid, admin_role)


def test_submission_approve_triggers_publish_once_and_blocks_second_transition(client, db_session_factory, monkeypatch):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("approve-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("approve-user"), "UserPass123!")
        submission = create_pending_submission(db, user.id, "Router Approve Contract")
        submission_id = submission.id
        admin_uid = admin.user_uid
        admin_role = admin.role
        admin_id = admin.id

    set_auth_cookie(client, admin_uid, admin_role)

    calls = {"publish": 0}

    def fake_publish_submission_as_recipe(db, submission, actor_admin_id):
        _ = db
        _ = submission
        assert actor_admin_id == admin_id
        calls["publish"] += 1
        return SimpleNamespace(id=12345)

    monkeypatch.setattr("app.routers.submissions.publish_submission_as_recipe", fake_publish_submission_as_recipe)

    first = post_form(
        client,
        f"/admin/submissions/{submission_id}/approve",
        {"admin_note": "approved"},
        referer_page=f"/admin/submissions/{submission_id}",
        follow_redirects=False,
    )
    assert first.status_code == 303
    assert f"/admin/submissions/{submission_id}?message=approved&recipe_id=12345" in first.headers.get("location", "")

    second = post_form(
        client,
        f"/admin/submissions/{submission_id}/reject",
        {"admin_note": "must fail after approve"},
        referer_page=f"/admin/submissions/{submission_id}",
        follow_redirects=False,
    )
    assert second.status_code == 409
    assert calls["publish"] == 1

    with db_session_factory() as db:
        persisted = db.scalar(select(RecipeSubmission).where(RecipeSubmission.id == submission_id))
        assert persisted is not None
        assert persisted.status == "approved"


def test_submission_reject_requires_reason_and_keeps_status_on_validation_error(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("reject-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("reject-user"), "UserPass123!")
        submission = create_pending_submission(db, user.id, "Router Reject Contract")
        submission_id = submission.id
        admin_uid = admin.user_uid
        admin_role = admin.role

    set_auth_cookie(client, admin_uid, admin_role)

    response = post_form(
        client,
        f"/admin/submissions/{submission_id}/reject",
        {"admin_note": "   "},
        referer_page=f"/admin/submissions/{submission_id}",
        follow_redirects=False,
    )
    assert response.status_code == 400

    with db_session_factory() as db:
        persisted = db.scalar(select(RecipeSubmission).where(RecipeSubmission.id == submission_id))
        assert persisted is not None
        assert persisted.status == "pending"
        assert persisted.admin_note is None


def test_translation_single_recipe_run_uses_stable_contract_and_redirect_shape(client, db_session_factory, monkeypatch):
    _auth_as_admin(client, db_session_factory)

    calls = {"runner": 0}

    def fake_run_translation_for_recipe_ids(db, recipe_ids, *, mode, limit):
        _ = db
        calls["runner"] += 1
        assert recipe_ids == [77]
        assert mode == "missing"
        assert limit == 1
        return SimpleNamespace(
            processed_recipes=1,
            created=1,
            updated=0,
            skipped=0,
            errors=[],
        )

    monkeypatch.setattr("app.routers.translations.run_translation_for_recipe_ids", fake_run_translation_for_recipe_ids)

    response = post_form(
        client,
        "/admin/translations/recipes/77/run",
        {"mode": "missing"},
        referer_page="/admin/translations",
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert (
        "/admin/translations?mode=missing&processed=1&created=1&updated=0&skipped=0&errors=0"
        == response.headers.get("location", "")
    )
    assert calls["runner"] == 1


def test_translation_queue_run_fatal_report_returns_400_without_commit_redirect(client, db_session_factory, monkeypatch):
    _auth_as_admin(client, db_session_factory)

    monkeypatch.setattr(
        "app.routers.translations.get_translation_queue",
        lambda db, limit=10: [
            SimpleNamespace(
                recipe_id=11,
                title="Queue Contract Recipe",
                created_at=datetime.now(timezone.utc),
                missing_languages=["en"],
                stale_languages=[],
            )
        ],
    )
    monkeypatch.setattr(
        "app.routers.translations.run_translation_for_recipe_ids",
        lambda db, recipe_ids, *, mode, limit: SimpleNamespace(
            processed_recipes=0,
            created=0,
            updated=0,
            skipped=0,
            errors=["fatal-run-error"],
        ),
    )

    response = post_form(
        client,
        "/admin/translations/queue/run",
        {"mode": "missing", "limit": "10"},
        referer_page="/",
        follow_redirects=False,
    )
    assert response.status_code == 400
    assert "fatal-run-error" in response.text

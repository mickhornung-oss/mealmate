from __future__ import annotations

from uuid import uuid4

from sqlalchemy import and_, select

from app.models import Recipe, RecipeImage, RecipeImageChangeRequest, RecipeSubmission
from tests.helpers import (
    SMALL_PNG_BYTES,
    create_admin_user,
    create_normal_user,
    create_pending_submission,
    create_published_recipe,
    post_form,
    unique_email,
)


def test_beta_aggressive_admin_flow(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("beta-admin-flow"), "AdminPass123!")
        user = create_normal_user(db, unique_email("beta-user-flow"), "UserPass123!")
        published_recipe = create_published_recipe(db, admin.id, title=f"Beta Published {uuid4().hex[:8]}")
        pending_for_approve = create_pending_submission(
            db,
            user.id,
            title=f"Beta Pending Approve {uuid4().hex[:8]}",
            instructions="Erster Schritt\nZweiter Schritt",
        )
        pending_for_reject = create_pending_submission(
            db,
            user.id,
            title=f"Beta Pending Reject {uuid4().hex[:8]}",
            instructions="Ablehnen Schritt 1\nAblehnen Schritt 2",
        )
        admin_email = admin.email
        user_email = user.email
        recipe_id = published_recipe.id
        recipe_title = published_recipe.title
        approve_submission_id = pending_for_approve.id
        approve_submission_title = pending_for_approve.title
        reject_submission_id = pending_for_reject.id
        reject_submission_title = pending_for_reject.title

    user_login = post_form(
        client,
        "/login",
        data={"identifier": user_email, "password": "UserPass123!"},
        referer_page="/login",
        follow_redirects=False,
    )
    assert user_login.status_code in {302, 303}

    image_change_request_response = post_form(
        client,
        f"/recipes/{recipe_id}/image-change-request",
        data={},
        referer_page=f"/recipes/{recipe_id}",
        files={"file": ("beta-change.png", SMALL_PNG_BYTES, "image/png")},
        follow_redirects=False,
    )
    assert image_change_request_response.status_code in {302, 303}

    user_logout = post_form(
        client,
        "/logout",
        data={},
        referer_page="/",
        follow_redirects=False,
    )
    assert user_logout.status_code in {302, 303}

    admin_login = post_form(
        client,
        "/login",
        data={"identifier": admin_email, "password": "AdminPass123!"},
        referer_page="/login",
        follow_redirects=False,
    )
    assert admin_login.status_code in {302, 303}

    queue_page = client.get("/admin/submissions?status_filter=pending")
    assert queue_page.status_code == 200
    assert approve_submission_title in queue_page.text
    assert reject_submission_title in queue_page.text

    approve_response = post_form(
        client,
        f"/admin/submissions/{approve_submission_id}/approve",
        data={"admin_note": "Freigabe im Aggressivtest."},
        referer_page=f"/admin/submissions/{approve_submission_id}",
        follow_redirects=False,
    )
    assert approve_response.status_code in {302, 303}

    with db_session_factory() as db:
        approved_submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.id == approve_submission_id))
        assert approved_submission is not None
        assert approved_submission.status == "approved"
        published_from_submission = db.scalar(
            select(Recipe).where(Recipe.source_uuid == f"submission:{approve_submission_id}")
        )
        assert published_from_submission is not None
        assert published_from_submission.is_published is True

    discover_after_approve = client.get("/", params={"title": approve_submission_title})
    assert discover_after_approve.status_code == 200
    assert approve_submission_title in discover_after_approve.text

    reject_note = "Ablehnung im Aggressivtest."
    reject_response = post_form(
        client,
        f"/admin/submissions/{reject_submission_id}/reject",
        data={"admin_note": reject_note},
        referer_page=f"/admin/submissions/{reject_submission_id}",
        follow_redirects=False,
    )
    assert reject_response.status_code in {302, 303}

    with db_session_factory() as db:
        rejected_submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.id == reject_submission_id))
        assert rejected_submission is not None
        assert rejected_submission.status == "rejected"
        assert rejected_submission.admin_note == reject_note

    discover_after_reject = client.get("/")
    assert discover_after_reject.status_code == 200
    assert reject_submission_title not in discover_after_reject.text

    with db_session_factory() as db:
        pending_image_change_request = db.scalar(
            select(RecipeImageChangeRequest).where(
                and_(
                    RecipeImageChangeRequest.recipe_id == recipe_id,
                    RecipeImageChangeRequest.status == "pending",
                )
            )
        )
        assert pending_image_change_request is not None
        pending_image_change_request_id = pending_image_change_request.id

    image_queue_page = client.get("/admin/image-change-requests?status_filter=pending")
    assert image_queue_page.status_code == 200
    assert recipe_title in image_queue_page.text

    approve_image_response = post_form(
        client,
        f"/admin/image-change-requests/{pending_image_change_request_id}/approve",
        data={"admin_note": "Bildfreigabe im Aggressivtest."},
        referer_page=f"/admin/image-change-requests/{pending_image_change_request_id}",
        follow_redirects=False,
    )
    assert approve_image_response.status_code in {302, 303}

    with db_session_factory() as db:
        approved_image_change_request = db.scalar(
            select(RecipeImageChangeRequest).where(RecipeImageChangeRequest.id == pending_image_change_request_id)
        )
        assert approved_image_change_request is not None
        assert approved_image_change_request.status == "approved"
        primary_image = db.scalar(
            select(RecipeImage).where(
                RecipeImage.recipe_id == recipe_id,
                RecipeImage.is_primary.is_(True),
            )
        )
        assert primary_image is not None

    direct_recipe_title = f"Beta Admin Direct {uuid4().hex[:8]}"
    direct_create_response = post_form(
        client,
        "/recipes/new",
        data={
            "title": direct_recipe_title,
            "description": "Direkt durch Admin erstellt.",
            "instructions": "Direkt Schritt 1\nDirekt Schritt 2",
            "category_select": "Unkategorisiert",
            "category_new": "",
            "category": "",
            "title_image_url": "",
            "prep_time_minutes": "22",
            "difficulty": "medium",
            "ingredients_text": "Mehl|200 g\nSalz|1 Prise",
        },
        referer_page="/recipes/new",
        follow_redirects=False,
    )
    assert direct_create_response.status_code in {302, 303}

    discover_after_direct_create = client.get("/", params={"title": direct_recipe_title})
    assert discover_after_direct_create.status_code == 200
    assert direct_recipe_title in discover_after_direct_create.text

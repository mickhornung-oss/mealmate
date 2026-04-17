from __future__ import annotations

from app.models import RecipeImageChangeRequest
from tests.helpers import create_admin_user, create_normal_user, create_published_recipe, set_auth_cookie, unique_email


def _auth_admin(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("render-admin"), "AdminPass123!")
        set_auth_cookie(client, admin.user_uid, admin.role)
        return admin.id


def test_admin_dashboard_render_contract_exposes_diagnostic_sections(client, db_session_factory):
    _auth_admin(client, db_session_factory)
    response = client.get("/admin")
    assert response.status_code == 200
    assert "/admin/translations/run" in response.text
    assert "/admin/image-change-requests" in response.text
    assert "Suspect DE translations:" in response.text


def test_admin_image_change_queue_invalid_filter_defaults_to_pending(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("imgq-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("imgq-user"), "UserPass123!")
        pending_recipe = create_published_recipe(db, admin.id, title="Render Pending Image Change", is_published=True)
        approved_recipe = create_published_recipe(db, admin.id, title="Render Approved Image Change", is_published=True)
        db.add(
            RecipeImageChangeRequest(
                recipe_id=pending_recipe.id,
                requester_user_id=user.id,
                status="pending",
            )
        )
        db.add(
            RecipeImageChangeRequest(
                recipe_id=approved_recipe.id,
                requester_user_id=user.id,
                status="approved",
            )
        )
        db.commit()
        set_auth_cookie(client, admin.user_uid, admin.role)

    response = client.get("/admin/image-change-requests?status_filter=INVALID")
    assert response.status_code == 200
    assert 'option value="pending" selected' in response.text
    assert "Render Pending Image Change" in response.text
    assert "Render Approved Image Change" not in response.text


def test_admin_image_change_queue_page_contract_clamps_to_last_page(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("imgq-page-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("imgq-page-user"), "UserPass123!")
        for index in range(21):
            recipe = create_published_recipe(
                db,
                admin.id,
                title=f"Render Queue Recipe {index:02d}",
                is_published=True,
            )
            db.add(
                RecipeImageChangeRequest(
                    recipe_id=recipe.id,
                    requester_user_id=user.id,
                    status="pending",
                )
            )
        db.commit()
        set_auth_cookie(client, admin.user_uid, admin.role)

    response = client.get("/admin/image-change-requests?status_filter=pending&page=999")
    assert response.status_code == 200
    assert "2 / 2" in response.text


def test_admin_translations_batch_started_message_without_job_id(client, db_session_factory):
    _auth_admin(client, db_session_factory)
    response = client.get("/admin/translations?batch_started=1")
    assert response.status_code == 200
    assert "Batch-Job gestartet." in response.text


def test_admin_translations_default_read_does_not_render_last_run_block(client, db_session_factory):
    _auth_admin(client, db_session_factory)
    response = client.get("/admin/translations")
    assert response.status_code == 200
    assert "Letzter Lauf" not in response.text

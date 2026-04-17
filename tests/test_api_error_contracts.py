from __future__ import annotations

from sqlalchemy.exc import OperationalError

from tests.helpers import (
    SMALL_PNG_BYTES,
    create_admin_user,
    create_normal_user,
    create_published_recipe,
    post_form,
    set_auth_cookie,
    unique_email,
)


def _auth_admin(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("api-contract-admin"), "AdminPass123!")
        set_auth_cookie(client, admin.user_uid, admin.role)
        return admin.id


def test_submit_recipe_invalid_image_renders_html_error_contract(client):
    response = post_form(
        client,
        "/submit",
        {
            "title": "Contract Submit",
            "instructions": "Contract Instructions",
            "description": "desc",
            "category_select": "Test",
            "difficulty": "easy",
        },
        files={"image": ("invalid.png", b"not-an-image", "image/png")},
        referer_page="/submit",
    )
    assert response.status_code == 400
    assert response.headers.get("content-type", "").startswith("text/html")
    assert '<form method="post" action="/submit"' in response.text
    assert "<p class=\"error\">" in response.text


def test_recipe_image_upload_hx_invalid_file_renders_partial_error(client, db_session_factory):
    admin_id = _auth_admin(client, db_session_factory)
    with db_session_factory() as db:
        recipe = create_published_recipe(db, admin_id, title="API Upload Contract", is_published=True)
        recipe_id = recipe.id

    response = post_form(
        client,
        f"/recipes/{recipe_id}/images",
        {"response_mode": "detail", "set_primary": "true"},
        files={"file": ("invalid.png", b"tiny", "image/png")},
        referer_page=f"/recipes/{recipe_id}",
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 400
    assert "recipe-images-section" in response.text
    assert "<p class=\"error\">" in response.text


def test_recipe_image_upload_hx_card_response_contract(client, db_session_factory):
    admin_id = _auth_admin(client, db_session_factory)
    with db_session_factory() as db:
        recipe = create_published_recipe(db, admin_id, title="API Card Contract", is_published=True)
        recipe_id = recipe.id

    response = post_form(
        client,
        f"/recipes/{recipe_id}/images",
        {"response_mode": "card", "set_primary": "true"},
        files={"file": ("valid.png", SMALL_PNG_BYTES, "image/png")},
        referer_page=f"/recipes/{recipe_id}",
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert f'id="card-image-{recipe_id}"' in response.text


def test_recipe_image_upload_non_hx_success_redirect_contract(client, db_session_factory):
    admin_id = _auth_admin(client, db_session_factory)
    with db_session_factory() as db:
        recipe = create_published_recipe(db, admin_id, title="API Redirect Contract", is_published=True)
        recipe_id = recipe.id

    response = post_form(
        client,
        f"/recipes/{recipe_id}/images",
        {"response_mode": "detail", "set_primary": "true"},
        files={"file": ("valid.png", SMALL_PNG_BYTES, "image/png")},
        referer_page=f"/recipes/{recipe_id}",
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers.get("location", "") == f"/recipes/{recipe_id}?message=image_upload_done"


def test_translation_run_operational_error_uses_503_contract(client, db_session_factory, monkeypatch):
    _auth_admin(client, db_session_factory)

    def fake_run_translation_batch(db, mode, limit):
        _ = db
        _ = mode
        _ = limit
        raise OperationalError("select 1", {}, Exception("database is locked"))

    monkeypatch.setattr("app.routers.translations.run_translation_batch", fake_run_translation_batch)

    response = post_form(
        client,
        "/admin/translations/run",
        {"mode": "missing", "limit": "1"},
        referer_page="/admin/translations",
        follow_redirects=False,
    )
    assert response.status_code == 503
    assert "Datenbank ist gerade gesperrt" in response.text


def test_translation_batch_start_runtime_error_uses_502_contract(client, db_session_factory, monkeypatch):
    _auth_admin(client, db_session_factory)

    def fake_start_translation_batch_job(db, mode, limit, admin_id):
        _ = db
        _ = mode
        _ = limit
        _ = admin_id
        raise RuntimeError("queue transport down")

    monkeypatch.setattr("app.routers.translations.start_translation_batch_job", fake_start_translation_batch_job)

    response = post_form(
        client,
        "/admin/translations/batch/start",
        {"mode": "missing", "limit": "1"},
        referer_page="/admin/translations",
        follow_redirects=False,
    )
    assert response.status_code == 502
    assert "Batch-start fehlgeschlagen" in response.text


def test_recipe_change_request_hx_invalid_file_renders_partial_error(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("api-contract-admin2"), "AdminPass123!")
        user = create_normal_user(db, unique_email("api-contract-user"), "UserPass123!")
        recipe = create_published_recipe(db, admin.id, title="API Change Request Contract", is_published=True)
        set_auth_cookie(client, user.user_uid, user.role)
        recipe_id = recipe.id

    response = post_form(
        client,
        f"/recipes/{recipe_id}/image-change-request",
        {"response_mode": "detail"},
        files={"file": ("invalid.png", b"tiny", "image/png")},
        referer_page=f"/recipes/{recipe_id}",
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 400
    assert "recipe-images-section" in response.text
    assert "<p class=\"error\">" in response.text

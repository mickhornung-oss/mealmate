from __future__ import annotations

from pathlib import Path

from sqlalchemy import select

from app.config import get_settings
from app.models import RecipeImage
from tests.helpers import (
    SMALL_PNG_BYTES,
    create_admin_user,
    create_normal_user,
    create_published_recipe,
    extract_token_from_link,
    get_csrf,
    post_form,
    read_last_link,
    unique_email,
)


def _csrf_headers(token: str) -> dict[str, str]:
    return {
        "X-CSRF-Token": token,
        "HX-Request": "true",
        "HX-Target": "favorite-box",
        "HX-Current-URL": "/",
    }


def test_state_change_post_without_csrf_is_blocked(client):
    response = client.post("/logout", data={})
    assert response.status_code == 403


def test_state_change_post_with_csrf_succeeds(client):
    response = post_form(client, "/logout", data={}, referer_page="/", follow_redirects=False)
    assert response.status_code in {302, 303}


def test_htmx_request_without_csrf_is_blocked(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("csrf-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("csrf-user"), "UserPass123!")
        recipe = create_published_recipe(db, admin.id, title="CSRF HTMX Test")
        user_email = user.email
        recipe_id = recipe.id

    login = post_form(
        client,
        "/login",
        data={"identifier": user_email, "password": "UserPass123!"},
        referer_page="/login",
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}

    response = client.post(
        f"/recipes/{recipe_id}/favorite",
        data={"favorite_box_id": f"favorite-box-card-{recipe_id}"},
        headers={"HX-Request": "true", "HX-Target": "favorite-box", "HX-Current-URL": f"/recipes/{recipe_id}"},
    )
    assert response.status_code == 403


def test_htmx_request_with_csrf_succeeds(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("csrf-admin-ok"), "AdminPass123!")
        user = create_normal_user(db, unique_email("csrf-user-ok"), "UserPass123!")
        recipe = create_published_recipe(db, admin.id, title="CSRF HTMX OK")
        user_email = user.email
        recipe_id = recipe.id

    login = post_form(
        client,
        "/login",
        data={"identifier": user_email, "password": "UserPass123!"},
        referer_page="/login",
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}

    csrf = get_csrf(client, f"/recipes/{recipe_id}")
    response = client.post(
        f"/recipes/{recipe_id}/favorite",
        data={"favorite_box_id": f"favorite-box-card-{recipe_id}", "csrf_token": csrf},
        headers=_csrf_headers(csrf) | {"HX-Current-URL": f"/recipes/{recipe_id}"},
        follow_redirects=False,
    )
    assert response.status_code == 200


def test_delete_without_csrf_blocked_with_csrf_allows_delete(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("csrf-del-admin"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="CSRF Delete")
        image = RecipeImage(
            recipe_id=recipe.id,
            filename="one.png",
            content_type="image/png",
            data=SMALL_PNG_BYTES,
            is_primary=True,
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        admin_email = admin.email
        recipe_id = recipe.id
        image_id = image.id

    login = post_form(
        client,
        "/login",
        data={"identifier": admin_email, "password": "AdminPass123!"},
        referer_page="/login",
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}

    blocked = client.delete(f"/images/{image_id}")
    assert blocked.status_code == 403

    csrf = get_csrf(client, f"/recipes/{recipe_id}")
    deleted = client.delete(f"/images/{image_id}", headers={"X-CSRF-Token": csrf})
    assert deleted.status_code == 200

    with db_session_factory() as db:
        image_after = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id))
        assert image_after is None


def test_login_cookie_flags_http_only_same_site_and_secure_override(client, db_session_factory):
    with db_session_factory() as db:
        user = create_normal_user(db, unique_email("csrf-cookie"), "UserPass123!")
        user_email = user.email

    response = post_form(
        client,
        "/login",
        data={"identifier": user_email, "password": "UserPass123!"},
        referer_page="/login",
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}
    set_cookie = response.headers.get("set-cookie", "").lower()
    assert "access_token=" in set_cookie
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie

    from app.routers import auth as auth_router

    original_cookie_secure = auth_router.settings.cookie_secure
    try:
        auth_router.settings.cookie_secure = True
        csrf = "csrf-secure-test-token"
        client.cookies.set("csrf_token", csrf, domain="testserver.local", path="/")
        response_secure = client.post(
            "/login",
            data={
                "identifier": user_email,
                "password": "UserPass123!",
                "csrf_token": csrf,
            },
            headers={"X-CSRF-Token": csrf},
            follow_redirects=False,
        )
        assert response_secure.status_code in {302, 303}
        secure_cookie = response_secure.headers.get("set-cookie", "").lower()
        assert "secure" in secure_cookie
    finally:
        auth_router.settings.cookie_secure = original_cookie_secure


def test_old_token_invalid_after_password_change(client, db_session_factory):
    with db_session_factory() as db:
        user = create_normal_user(db, unique_email("csrf-pwd-change"), "StartPass123!")
        user_email = user.email

    login = post_form(
        client,
        "/login",
        data={"identifier": user_email, "password": "StartPass123!"},
        referer_page="/login",
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}
    old_token = client.cookies.get("access_token")
    assert old_token

    changed = post_form(
        client,
        "/auth/change-password",
        data={
            "old_password": "StartPass123!",
            "new_password": "ChangedPass123!",
            "confirm_password": "ChangedPass123!",
        },
        referer_page="/me",
        follow_redirects=False,
    )
    assert changed.status_code in {302, 303}

    client.cookies.set("access_token", old_token, domain="testserver.local", path="/")
    old_session = client.get("/api/me")
    assert old_session.status_code == 401


def test_old_token_invalid_after_password_reset(client, db_session_factory, tmp_path):
    settings = get_settings()
    original_outbox = settings.mail_outbox_path
    reset_outbox = tmp_path / "reset_links_csrf_cookie.txt"
    reset_outbox.write_text("", encoding="utf-8")
    settings.mail_outbox_path = str(reset_outbox)

    try:
        with db_session_factory() as db:
            user = create_normal_user(db, unique_email("csrf-pwd-reset"), "ResetStart123!")
            user_email = user.email

        login = post_form(
            client,
            "/login",
            data={"identifier": user_email, "password": "ResetStart123!"},
            referer_page="/login",
            follow_redirects=False,
        )
        assert login.status_code in {302, 303}
        old_token = client.cookies.get("access_token")
        assert old_token

        forgot = post_form(
            client,
            "/auth/forgot-password",
            data={"identifier": user_email},
            referer_page="/auth/forgot-password",
        )
        assert forgot.status_code == 200

        reset_link = read_last_link(Path(settings.mail_outbox_path))
        reset_token = extract_token_from_link(reset_link)
        reset = post_form(
            client,
            "/auth/reset-password",
            data={
                "token": reset_token,
                "new_password": "ResetDone123!",
                "confirm_password": "ResetDone123!",
            },
            referer_page=f"/auth/reset-password?token={reset_token}",
            follow_redirects=False,
        )
        assert reset.status_code in {302, 303}

        client.cookies.set("access_token", old_token, domain="testserver.local", path="/")
        old_session = client.get("/api/me")
        assert old_session.status_code == 401
    finally:
        settings.mail_outbox_path = original_outbox

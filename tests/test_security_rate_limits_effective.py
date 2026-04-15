from __future__ import annotations

from tests.helpers import SMALL_PNG_BYTES, create_admin_user, create_normal_user, create_published_recipe, post_form, unique_email


def _login(client, email: str, password: str) -> None:
    response = post_form(
        client,
        "/login",
        data={"identifier": email, "password": password},
        referer_page="/login",
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}


def test_bruteforce_login_is_effectively_rate_limited(client, db_session_factory):
    with db_session_factory() as db:
        user = create_normal_user(db, unique_email("rl-login-user"), "CorrectPass123!")
        email = user.email

    statuses: list[int] = []
    for _ in range(20):
        response = post_form(
            client,
            "/login",
            data={"identifier": email, "password": "wrong-password"},
            referer_page="/login",
            follow_redirects=False,
        )
        statuses.append(response.status_code)

    assert 401 in statuses
    assert 429 in statuses


def test_pdf_export_spam_is_effectively_rate_limited(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("rl-pdf-admin"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="Rate Limit PDF Recipe", is_published=True)
        admin_email = admin.email
        recipe_id = recipe.id

    _login(client, admin_email, "AdminPass123!")

    statuses: list[int] = []
    for _ in range(35):
        response = client.get(f"/recipes/{recipe_id}/pdf")
        statuses.append(response.status_code)

    assert 200 in statuses
    assert 429 in statuses


def test_upload_spam_is_effectively_rate_limited(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("rl-upload-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("rl-upload-user"), "UserPass123!")
        recipe = create_published_recipe(db, admin.id, title="Rate Limit Upload Recipe", is_published=True)
        user_email = user.email
        recipe_id = recipe.id

    _login(client, user_email, "UserPass123!")

    statuses: list[int] = []
    for _ in range(12):
        response = post_form(
            client,
            f"/recipes/{recipe_id}/image-change-request",
            data={},
            referer_page=f"/recipes/{recipe_id}",
            files={"file": ("spam.png", SMALL_PNG_BYTES, "image/png")},
            follow_redirects=False,
        )
        statuses.append(response.status_code)

    assert any(status in {200, 302, 303} for status in statuses)
    assert 429 in statuses

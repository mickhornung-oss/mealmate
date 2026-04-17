from __future__ import annotations

import re
import time

from tests.helpers import create_normal_user, post_form, unique_email


def _login_user(client, email: str, password: str):
    response = post_form(
        client,
        "/login",
        data={"identifier": email, "password": password},
        referer_page="/login",
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}
    token = client.cookies.get("access_token")
    assert token
    return response, str(token)


def test_logout_clears_cookie_and_blocks_protected_endpoint(client, db_session_factory):
    with db_session_factory() as db:
        user = create_normal_user(db, unique_email("sess-logout"), "LogoutPass123!")
        email = user.email

    login_response, _ = _login_user(client, email, "LogoutPass123!")
    assert login_response.status_code in {302, 303}
    assert client.get("/api/me").status_code == 200

    logout_response = post_form(client, "/logout", data={}, referer_page="/", follow_redirects=False)
    assert logout_response.status_code in {302, 303}
    set_cookie = (logout_response.headers.get("set-cookie") or "").lower()
    assert "access_token=" in set_cookie
    assert "max-age=0" in set_cookie or "expires=" in set_cookie
    assert client.get("/api/me").status_code == 401


def test_password_change_invalidates_previous_session_token(client, db_session_factory):
    with db_session_factory() as db:
        user = create_normal_user(db, unique_email("sess-pwd"), "BeforePass123!")
        email = user.email

    _, old_token = _login_user(client, email, "BeforePass123!")
    changed = post_form(
        client,
        "/auth/change-password",
        data={
            "old_password": "BeforePass123!",
            "new_password": "AfterPass123!",
            "confirm_password": "AfterPass123!",
        },
        referer_page="/me",
        follow_redirects=False,
    )
    assert changed.status_code in {302, 303}

    client.cookies.set("access_token", old_token, domain="testserver.local", path="/")
    assert client.get("/api/me").status_code == 401


def test_session_fixation_login_rotates_cookie_value(client, db_session_factory):
    with db_session_factory() as db:
        user = create_normal_user(db, unique_email("sess-fix"), "FixPass123!")
        email = user.email

    fixed_token = "Bearer fixed.attacker.token"
    client.cookies.set("access_token", fixed_token, domain="testserver.local", path="/")
    _, first_token = _login_user(client, email, "FixPass123!")
    assert first_token != fixed_token

    logout_response = post_form(client, "/logout", data={}, referer_page="/", follow_redirects=False)
    assert logout_response.status_code in {302, 303}
    time.sleep(1.1)
    _, second_token = _login_user(client, email, "FixPass123!")
    assert second_token != first_token


def test_expired_jwt_is_rejected_even_if_cookie_exists(client, db_session_factory):
    with db_session_factory() as db:
        user = create_normal_user(db, unique_email("sess-exp"), "ExpirePass123!")
        email = user.email

    from app import security as security_module

    original_minutes = security_module.settings.token_expire_minutes
    try:
        security_module.settings.token_expire_minutes = -1
        _, expired_token = _login_user(client, email, "ExpirePass123!")
        assert expired_token
        assert client.get("/api/me").status_code == 401
    finally:
        security_module.settings.token_expire_minutes = original_minutes


def test_no_remember_me_and_cookie_lifetime_is_bounded(client, db_session_factory):
    login_page = client.get("/login")
    assert login_page.status_code == 200
    assert 'name="remember_me"' not in login_page.text.lower()

    with db_session_factory() as db:
        user = create_normal_user(db, unique_email("sess-maxage"), "MaxAgePass123!")
        email = user.email

    login_response, _ = _login_user(client, email, "MaxAgePass123!")
    set_cookie = (login_response.headers.get("set-cookie") or "").lower()
    match = re.search(r"max-age=(\d+)", set_cookie)
    assert match
    max_age_seconds = int(match.group(1))
    assert 0 < max_age_seconds <= 60 * 60 * 24 * 30

from __future__ import annotations

from tests.helpers import create_normal_user, post_form, unique_email


def _assert_internal_redirect(response, expected_prefix: str) -> None:
    assert response.status_code in {302, 303}
    location = response.headers.get("location") or ""
    assert location.startswith(expected_prefix), location
    assert "evil.com" not in location.lower(), location
    assert not location.lower().startswith("http://"), location
    assert not location.lower().startswith("https://"), location
    assert not location.startswith("//"), location


def test_login_next_blocks_external_redirects(client, db_session_factory):
    email = unique_email("open-redirect-login")
    with db_session_factory() as db:
        create_normal_user(db, email, "UserPass123!")

    response = post_form(
        client,
        "/login",
        data={
            "identifier": email,
            "password": "UserPass123!",
            "next": "https://evil.com/steal",
        },
        referer_page="/login",
        follow_redirects=False,
    )
    _assert_internal_redirect(response, "/")


def test_login_next_allows_relative_internal_path(client, db_session_factory):
    email = unique_email("open-redirect-login-ok")
    with db_session_factory() as db:
        create_normal_user(db, email, "UserPass123!")

    response = post_form(
        client,
        "/login",
        data={
            "identifier": email,
            "password": "UserPass123!",
            "next": "/me?tab=security",
        },
        referer_page="/login",
        follow_redirects=False,
    )
    _assert_internal_redirect(response, "/me")


def test_register_next_blocks_scheme_relative_redirects(client):
    response = post_form(
        client,
        "/register",
        data={
            "email": unique_email("open-redirect-register"),
            "username": "open.redirect.user",
            "password": "UserPass123!",
            "next": "//evil.com/hijack",
        },
        referer_page="/register",
        follow_redirects=False,
    )
    _assert_internal_redirect(response, "/")


def test_register_next_allows_relative_path(client):
    response = post_form(
        client,
        "/register",
        data={
            "email": unique_email("open-redirect-register-ok"),
            "username": "open.redirect.user.ok",
            "password": "UserPass123!",
            "next": "/submit",
        },
        referer_page="/register",
        follow_redirects=False,
    )
    _assert_internal_redirect(response, "/submit")


def test_logout_next_blocks_external_redirect(client, db_session_factory):
    email = unique_email("open-redirect-logout")
    with db_session_factory() as db:
        create_normal_user(db, email, "UserPass123!")

    login_response = post_form(
        client,
        "/login",
        data={"identifier": email, "password": "UserPass123!"},
        referer_page="/login",
        follow_redirects=False,
    )
    assert login_response.status_code in {302, 303}

    logout_response = post_form(
        client,
        "/logout",
        data={"next": "https://evil.com/post-logout"},
        referer_page="/",
        follow_redirects=False,
    )
    _assert_internal_redirect(logout_response, "/")


def test_logout_next_allows_relative_internal_path(client, db_session_factory):
    email = unique_email("open-redirect-logout-ok")
    with db_session_factory() as db:
        create_normal_user(db, email, "UserPass123!")

    login_response = post_form(
        client,
        "/login",
        data={"identifier": email, "password": "UserPass123!"},
        referer_page="/login",
        follow_redirects=False,
    )
    assert login_response.status_code in {302, 303}

    logout_response = post_form(
        client,
        "/logout",
        data={"next": "/login?message=signed_out"},
        referer_page="/",
        follow_redirects=False,
    )
    _assert_internal_redirect(logout_response, "/login")

from __future__ import annotations

from tests.helpers import create_normal_user, get_csrf, unique_email


def test_host_header_is_not_reflected_in_rendered_links(client):
    response = client.get("/", headers={"host": "evil.example"})
    assert response.status_code == 200
    assert "evil.example" not in response.text.lower()
    assert 'href="/?lang=de"' in response.text
    assert 'href="/?lang=en"' in response.text
    assert 'href="/?lang=fr"' in response.text


def test_host_header_does_not_influence_redirect_location(client, db_session_factory):
    with db_session_factory() as db:
        email = unique_email("host-redirect")
        create_normal_user(db, email, "HostPass123!")

    csrf = get_csrf(client, "/login")
    response = client.post(
        "/login",
        data={
            "identifier": email,
            "password": "HostPass123!",
            "next": "https://evil.example/hijack",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf, "host": "evil.example"},
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}
    location = response.headers.get("location") or ""
    assert location.startswith("/")
    assert "evil.example" not in location.lower()
    assert "http://" not in location.lower()
    assert "https://" not in location.lower()


def test_csrf_token_validation_works_without_origin_policy(client, db_session_factory):
    with db_session_factory() as db:
        email = unique_email("origin-csrf")
        create_normal_user(db, email, "OriginPass123!")

    login_csrf = get_csrf(client, "/login")
    login = client.post(
        "/login",
        data={"identifier": email, "password": "OriginPass123!", "csrf_token": login_csrf},
        headers={"X-CSRF-Token": login_csrf},
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}

    profile_csrf = get_csrf(client, "/me")
    username_update = client.post(
        "/profile/username",
        data={"username": "origin.user", "csrf_token": profile_csrf},
        headers={"X-CSRF-Token": profile_csrf, "Origin": "https://evil.example"},
        follow_redirects=False,
    )
    assert username_update.status_code in {302, 303}


def test_preflight_has_no_cors_allow_origin_header(client):
    response = client.options(
        "/api/me",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code in {200, 204, 401, 403, 405}
    headers = {key.lower(): value for key, value in response.headers.items()}
    assert "access-control-allow-origin" not in headers

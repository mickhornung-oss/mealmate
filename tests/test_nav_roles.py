from app.models import User
from app.security import hash_password, normalize_username


def _create_user(db, *, email: str, password: str, role: str = "user", username: str | None = None) -> User:
    user = User(
        email=email.strip().lower(),
        username=username,
        username_normalized=normalize_username(username) if username else None,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _csrf_token(client, path: str = "/login") -> str:
    response = client.get(path)
    assert response.status_code == 200
    token = client.cookies.get("csrf_token")
    assert token
    return str(token)


def _login(client, *, identifier: str, password: str) -> None:
    csrf = _csrf_token(client, "/login")
    response = client.post(
        "/login",
        data={
            "identifier": identifier,
            "password": password,
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}


def _extract_nav_block(html: str) -> str:
    for marker in ('<nav class="header-nav"', '<nav class="main-nav">'):
        start = html.find(marker)
        if start >= 0:
            end = html.find("</nav>", start)
            assert end > start
            return html[start:end]
    raise AssertionError("No navigation block found")


def test_guest_nav_has_submit_but_not_publish(client):
    response = client.get("/")
    assert response.status_code == 200
    nav_html = _extract_nav_block(response.text)
    assert 'href="/submit"' in nav_html
    assert 'href="/recipes/new"' not in nav_html
    assert 'href="/login"' in response.text
    assert 'href="/register"' in response.text


def test_user_nav_has_submit_and_my_submissions_but_not_publish(client, db_session_factory):
    with db_session_factory() as db:
        _create_user(
            db,
            email="nav-user@example.local",
            password="NavUserPass123!",
            role="user",
            username="nav.user",
        )

    _login(client, identifier="nav-user@example.local", password="NavUserPass123!")
    response = client.get("/")
    assert response.status_code == 200
    nav_html = _extract_nav_block(response.text)
    assert 'href="/submit"' in nav_html
    assert 'href="/my-submissions"' in nav_html
    assert 'href="/favorites"' in nav_html
    assert 'href="/me"' in nav_html
    assert 'href="/recipes/new"' not in nav_html


def test_admin_nav_has_publish_and_admin_but_not_submit(client, db_session_factory):
    with db_session_factory() as db:
        _create_user(
            db,
            email="nav-admin@example.local",
            password="NavAdminPass123!",
            role="admin",
            username="nav.admin",
        )

    _login(client, identifier="nav-admin@example.local", password="NavAdminPass123!")
    response = client.get("/")
    assert response.status_code == 200
    nav_html = _extract_nav_block(response.text)
    assert 'href="/recipes/new"' in nav_html
    assert 'href="/admin"' in nav_html
    assert 'href="/admin/submissions"' in nav_html
    assert 'href="/submit"' not in nav_html

from pathlib import Path
from uuid import UUID

from sqlalchemy import select

from app.config import get_settings
from app.models import PasswordResetToken, User
from app.security import hash_password, normalize_username


def create_user(
    db,
    *,
    email: str,
    password: str,
    role: str = "user",
    username: str | None = None,
) -> User:
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


def csrf_token(client, path: str = "/login") -> str:
    response = client.get(path)
    assert response.status_code == 200
    token = client.cookies.get("csrf_token")
    assert token
    return str(token)


def parse_reset_token_from_outbox(outbox_path: Path) -> str:
    content = outbox_path.read_text(encoding="utf-8")
    marker = "/auth/reset-password?token="
    index = content.rfind(marker)
    assert index >= 0
    token_start = index + len(marker)
    token = []
    for char in content[token_start:]:
        if char in "\n\r ":
            break
        token.append(char)
    result = "".join(token).strip()
    assert result
    return result


def test_login_with_email_and_username(client, db_session_factory):
    raw_password = "LoginPass123!"
    with db_session_factory() as db:
        create_user(db, email="dual-login@example.local", password=raw_password, username="Dual.Login")

    csrf = csrf_token(client, "/login")
    login_email = client.post(
        "/login",
        data={"identifier": "dual-login@example.local", "password": raw_password, "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert login_email.status_code in {302, 303}

    csrf = csrf_token(client, "/login")
    login_username = client.post(
        "/login",
        data={"identifier": "Dual.Login", "password": raw_password, "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert login_username.status_code in {302, 303}


def test_forgot_password_leaks_no_account_existence(client, db_session_factory, tmp_path):
    settings = get_settings()
    settings.mail_outbox_path = str(tmp_path / "reset_links.txt")

    with db_session_factory() as db:
        create_user(db, email="exists@example.local", password="ForgotPass123!", username="exists.user")

    csrf = csrf_token(client, "/auth/forgot-password")
    known = client.post(
        "/auth/forgot-password",
        data={"identifier": "exists@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert known.status_code == 200

    csrf = csrf_token(client, "/auth/forgot-password")
    unknown = client.post(
        "/auth/forgot-password",
        data={"identifier": "missing@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert unknown.status_code == 200
    expected_message = "Wenn der Account existiert, wurde eine E-Mail gesendet."
    assert expected_message in known.text
    assert expected_message in unknown.text


def test_reset_token_single_use(client, db_session_factory, tmp_path):
    settings = get_settings()
    outbox_file = tmp_path / "reset_links.txt"
    settings.mail_outbox_path = str(outbox_file)

    with db_session_factory() as db:
        create_user(db, email="reset-single-use@example.local", password="OldPass123!", username="reset.user")

    csrf = csrf_token(client, "/auth/forgot-password")
    forgot = client.post(
        "/auth/forgot-password",
        data={"identifier": "reset-single-use@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert forgot.status_code == 200
    token = parse_reset_token_from_outbox(outbox_file)

    csrf = csrf_token(client, f"/auth/reset-password?token={token}")
    reset_once = client.post(
        "/auth/reset-password",
        data={
            "token": token,
            "new_password": "BrandNewPass123!",
            "confirm_password": "BrandNewPass123!",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert reset_once.status_code in {302, 303}

    with db_session_factory() as db:
        db_token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash.is_not(None)))
        assert db_token is not None
        assert db_token.used_at is not None

    csrf = csrf_token(client, f"/auth/reset-password?token={token}")
    reset_twice = client.post(
        "/auth/reset-password",
        data={
            "token": token,
            "new_password": "AnotherPass123!",
            "confirm_password": "AnotherPass123!",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert reset_twice.status_code == 400


def test_change_password_requires_old_password(client, db_session_factory):
    with db_session_factory() as db:
        create_user(db, email="change-pass@example.local", password="OldPass123!", username="change.user")

    csrf = csrf_token(client, "/login")
    login = client.post(
        "/login",
        data={"identifier": "change.user", "password": "OldPass123!", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}

    csrf = csrf_token(client, "/me")
    bad_change = client.post(
        "/auth/change-password",
        data={
            "old_password": "WrongOld123!",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert bad_change.status_code == 400

    good_change = client.post(
        "/auth/change-password",
        data={
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert good_change.status_code in {302, 303}


def test_username_unique_and_pattern(client, db_session_factory):
    with db_session_factory() as db:
        create_user(db, email="first@example.local", password="UserPass123!", username="first.user")
        create_user(db, email="taken@example.local", password="UserPass123!", username="taken_name")

    csrf = csrf_token(client, "/login")
    login = client.post(
        "/login",
        data={"identifier": "first@example.local", "password": "UserPass123!", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}

    csrf = csrf_token(client, "/me")
    invalid = client.post(
        "/profile/username",
        data={"username": "ab", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert invalid.status_code == 400

    duplicate = client.post(
        "/profile/username",
        data={"username": "taken_name", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert duplicate.status_code == 409

    success = client.post(
        "/profile/username",
        data={"username": "valid.Name-22", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert success.status_code in {302, 303}

    with db_session_factory() as db:
        user = db.scalar(select(User).where(User.email == "first@example.local"))
        assert user is not None
        assert user.username == "valid.Name-22"
        assert user.username_normalized == "valid.name-22"


def test_user_uid_is_set_for_new_user(client, db_session_factory):
    csrf = csrf_token(client, "/register")
    register = client.post(
        "/register",
        data={
            "email": "uid-check@example.local",
            "username": "uid.checker",
            "password": "UidCheck123!",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert register.status_code in {302, 303}

    with db_session_factory() as db:
        user = db.scalar(select(User).where(User.email == "uid-check@example.local"))
        assert user is not None
        assert user.user_uid
        UUID(user.user_uid)

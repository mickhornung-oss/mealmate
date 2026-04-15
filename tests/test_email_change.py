from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select

from app.config import get_settings
from app.models import PasswordResetToken, User
from app.security import create_access_token, create_raw_reset_token, hash_password, hash_reset_token, normalize_username


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


def authenticate_client(client, user_uid: str, role: str = "user") -> None:
    token = create_access_token(user_uid, role)
    client.cookies.set("access_token", f"Bearer {token}")


def csrf_token(client, path: str = "/login") -> str:
    response = client.get(path)
    assert response.status_code == 200
    token = client.cookies.get("csrf_token")
    assert token
    return str(token)


def parse_email_change_token_from_outbox(outbox_path: Path) -> str:
    content = outbox_path.read_text(encoding="utf-8")
    marker = "/auth/change-email/confirm?token="
    index = content.rfind(marker)
    assert index >= 0
    token_start = index + len(marker)
    token_chars: list[str] = []
    for char in content[token_start:]:
        if char in "\n\r ":
            break
        token_chars.append(char)
    token = "".join(token_chars).strip()
    assert token
    return token


def test_request_email_change_creates_token_and_sends_mail(client, db_session_factory, tmp_path):
    settings = get_settings()
    outbox_file = tmp_path / "email_change_links.txt"
    settings.mail_outbox_email_change_path = str(outbox_file)

    with db_session_factory() as db:
        user = create_user(db, email="request-change@example.local", password="RequestPass123!", username="request.change")
        user_uid = user.user_uid

    authenticate_client(client, user_uid)
    csrf = csrf_token(client, "/auth/change-email")
    response = client.post(
        "/auth/change-email/request",
        data={"new_email": "new-address@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 200
    assert outbox_file.exists()

    raw_token = parse_email_change_token_from_outbox(outbox_file)

    with db_session_factory() as db:
        db_user = db.scalar(select(User).where(User.email == "request-change@example.local"))
        assert db_user is not None
        token_row = db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == db_user.id,
                PasswordResetToken.purpose == "email_change",
            )
        )
        assert token_row is not None
        assert token_row.token_hash == hash_reset_token(raw_token)
        assert token_row.new_email_normalized == "new-address@example.local"
        assert token_row.used_at is None


def test_confirm_email_change_updates_email_and_invalidates_token(client, db_session_factory, tmp_path):
    settings = get_settings()
    outbox_file = tmp_path / "email_change_links.txt"
    settings.mail_outbox_email_change_path = str(outbox_file)

    with db_session_factory() as db:
        user = create_user(db, email="confirm-change@example.local", password="ConfirmPass123!", username="confirm.change")
        user_uid = user.user_uid

    authenticate_client(client, user_uid)
    csrf = csrf_token(client, "/auth/change-email")
    request_response = client.post(
        "/auth/change-email/request",
        data={"new_email": "confirmed-address@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert request_response.status_code == 200

    raw_token = parse_email_change_token_from_outbox(outbox_file)

    csrf = csrf_token(client, f"/auth/change-email/confirm?token={raw_token}")
    confirm_response = client.post(
        "/auth/change-email/confirm",
        data={"token": raw_token, "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert confirm_response.status_code in {302, 303}

    with db_session_factory() as db:
        updated_user = db.scalar(select(User).where(User.user_uid == user_uid))
        assert updated_user is not None
        assert updated_user.email == "confirmed-address@example.local"
        token_row = db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == hash_reset_token(raw_token),
                PasswordResetToken.purpose == "email_change",
            )
        )
        assert token_row is not None
        assert token_row.used_at is not None

    csrf = csrf_token(client, "/login")
    second_try = client.post(
        "/auth/change-email/confirm",
        data={"token": raw_token, "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert second_try.status_code == 400


def test_email_change_conflict_fails(client, db_session_factory):
    with db_session_factory() as db:
        requester = create_user(db, email="owner@example.local", password="OwnerPass123!", username="owner.user")
        create_user(db, email="already-used@example.local", password="TakenPass123!", username="taken.user")
        requester_uid = requester.user_uid

    authenticate_client(client, requester_uid)
    csrf = csrf_token(client, "/auth/change-email")
    response = client.post(
        "/auth/change-email/request",
        data={"new_email": "already-used@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 409

    with db_session_factory() as db:
        db_requester = db.scalar(select(User).where(User.user_uid == requester.user_uid))
        assert db_requester is not None
        token_rows = db.scalars(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == db_requester.id,
                PasswordResetToken.purpose == "email_change",
            )
        ).all()
        assert token_rows == []


def test_email_change_expired_token_fails(client, db_session_factory):
    raw_token = create_raw_reset_token()
    with db_session_factory() as db:
        user = create_user(db, email="expired-change@example.local", password="ExpiredPass123!", username="expired.user")
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_reset_token(raw_token),
                new_email_normalized="after-expire@example.local",
                expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
                purpose="email_change",
            )
        )
        db.commit()

    invalid_page = client.get(f"/auth/change-email/confirm?token={raw_token}")
    assert invalid_page.status_code == 400

    csrf = csrf_token(client, "/login")
    invalid_post = client.post(
        "/auth/change-email/confirm",
        data={"token": raw_token, "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert invalid_post.status_code == 400

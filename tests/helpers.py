from __future__ import annotations

import base64
from pathlib import Path
import re
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import Recipe, RecipeSubmission, User
from app.security import create_access_token, hash_password

SMALL_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
)


def unique_email(prefix: str = "testuser") -> str:
    return f"{prefix}-{uuid4().hex[:10]}@example.local"


def get_csrf(client: TestClient, url: str = "/") -> str:
    response = client.get(url)
    assert response.status_code < 500
    settings = get_settings()
    cookie_name = getattr(settings, "csrf_cookie_name", None) or "csrf_token"
    token = client.cookies.get(cookie_name) or client.cookies.get("csrf_token")
    assert token
    return str(token)


def post_form(
    client: TestClient,
    url: str,
    data: dict[str, str] | None = None,
    *,
    referer_page: str = "/",
    files: dict | None = None,
    **kwargs,
):
    csrf = get_csrf(client, referer_page)
    payload = dict(data or {})
    payload.setdefault("csrf_token", csrf)
    headers = dict(kwargs.pop("headers", {}))
    headers["X-CSRF-Token"] = csrf
    return client.post(url, data=payload, files=files, headers=headers, **kwargs)


def read_last_link(path: Path) -> str:
    content = path.read_text(encoding="utf-8")
    candidates = re.findall(r"https?://[^\s]+", content)
    if not candidates:
        raise AssertionError(f"No link found in outbox file: {path}")
    return candidates[-1].strip()


def extract_token_from_link(link: str) -> str:
    query = urlparse(link).query
    values = parse_qs(query).get("token", [])
    if not values:
        raise AssertionError(f"No token query parameter in link: {link}")
    token = values[0].strip()
    if not token:
        raise AssertionError("Token in link is empty.")
    return token


def create_admin_user(db: Session, email: str, password: str, role: str = "admin") -> User:
    user = User(email=email.strip().lower(), hashed_password=hash_password(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_normal_user(db: Session, email: str, password: str) -> User:
    user = User(email=email.strip().lower(), hashed_password=hash_password(password), role="user")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_published_recipe(
    db: Session,
    admin_id: int,
    title: str = "Test Published",
    *,
    is_published: bool = True,
) -> Recipe:
    recipe = Recipe(
        title=title,
        description="Integration test recipe description.",
        instructions="Step 1\nStep 2",
        category="Test",
        prep_time_minutes=20,
        difficulty="medium",
        creator_id=admin_id,
        source="test",
        is_published=is_published,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


def create_pending_submission(
    db: Session,
    user_id: int,
    title: str,
    *,
    instructions: str = "Moderation step one\nModeration step two",
) -> RecipeSubmission:
    submission = RecipeSubmission(
        submitter_user_id=user_id,
        title=title,
        description="Pending moderation submission.",
        category="Test",
        difficulty="easy",
        prep_time_minutes=15,
        servings_text="2",
        instructions=instructions,
        status="pending",
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


def set_auth_cookie(client: TestClient, user_uid: str, role: str) -> None:
    token = create_access_token(user_uid, role)
    client.cookies.set("access_token", f"Bearer {token}")

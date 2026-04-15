from __future__ import annotations

from sqlalchemy import select

from app.models import Recipe, RecipeSubmission, User
from app.security import create_access_token, hash_password


def _create_user(db, *, email: str, role: str, password: str = "StrongPass123!") -> User:
    user = User(email=email.strip().lower(), role=role, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _auth_as(client, user: User) -> str:
    csrf_token = "api-test-csrf-token"
    token = create_access_token(user.user_uid, user.role)
    client.cookies.set("access_token", f"Bearer {token}")
    client.cookies.set("csrf_token", csrf_token)
    return csrf_token


def test_api_user_cannot_publish_recipe_directly(client, db_session_factory):
    with db_session_factory() as db:
        user = _create_user(db, email="api-publish-block@example.local", role="user")
    csrf = _auth_as(client, user)

    response = client.post(
        "/recipes",
        data={
            "title": "API Direct Publish Block",
            "description": "Soll als User nicht direkt live gehen.",
            "instructions": "Schritt 1\nSchritt 2",
            "category_select": "Unkategorisiert",
            "category_new": "",
            "category": "",
            "title_image_url": "",
            "prep_time_minutes": "15",
            "difficulty": "easy",
            "ingredients_text": "Mehl|100 g",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 403


def test_api_discover_never_lists_pending_submissions(client, db_session_factory):
    with db_session_factory() as db:
        admin = _create_user(db, email="api-admin@example.local", role="admin")
        user = _create_user(db, email="api-user@example.local", role="user")
        db.add(
            Recipe(
                title="API Sichtbares Rezept",
                description="Dies ist sichtbar.",
                instructions="Schritt 1",
                category="Test",
                prep_time_minutes=12,
                difficulty="medium",
                creator_id=admin.id,
                source="test",
                is_published=True,
            )
        )
        db.add(
            RecipeSubmission(
                submitter_user_id=user.id,
                title="API Pending Nur Moderation",
                description="Darf nicht in Discover erscheinen.",
                category="Test",
                difficulty="easy",
                instructions="Schritt A",
                status="pending",
            )
        )
        db.commit()

    discover_response = client.get("/")
    assert discover_response.status_code == 200
    assert "API Sichtbares Rezept" in discover_response.text
    assert "API Pending Nur Moderation" not in discover_response.text

    with db_session_factory() as db:
        pending_submission = db.scalar(
            select(RecipeSubmission).where(RecipeSubmission.title == "API Pending Nur Moderation")
        )
        assert pending_submission is not None
        assert pending_submission.status == "pending"

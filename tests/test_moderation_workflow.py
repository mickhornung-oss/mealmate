from datetime import datetime, timezone

from sqlalchemy import select

from app.moderation_repair import run_moderation_repair
from app.models import Recipe, RecipeSubmission, User
from app.security import create_access_token, hash_password


def create_user(db, email: str, role: str) -> tuple[int, str, str]:
    user = User(email=email, hashed_password=hash_password("StrongTestPass123!"), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id, user.email, user.role


def auth_client(client, email: str, role: str) -> str:
    token = create_access_token(email, role)
    csrf_token = "test-csrf-token"
    client.cookies.set("access_token", f"Bearer {token}")
    client.cookies.set("csrf_token", csrf_token)
    return csrf_token


def test_user_submit_goes_to_pending_not_discover(client, db_session_factory):
    with db_session_factory() as db:
        _, user_email, user_role = create_user(db, "submitter@example.local", "user")
    csrf = auth_client(client, user_email, user_role)

    response = client.post(
        "/submit",
        data={
            "title": "Pending Rezept Alpha",
            "description": "Nur zur Moderation.",
            "instructions": "Testschritt 1\nTestschritt 2",
            "difficulty": "medium",
            "category_select": "Unkategorisiert",
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 303

    with db_session_factory() as db:
        submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.title == "Pending Rezept Alpha"))
        assert submission is not None
        assert submission.status == "pending"
        recipe = db.scalar(select(Recipe).where(Recipe.title == "Pending Rezept Alpha"))
        assert recipe is None

    discover = client.get("/")
    assert discover.status_code == 200
    assert "Pending Rezept Alpha" not in discover.text


def test_user_cannot_publish_recipe_directly(client, db_session_factory):
    with db_session_factory() as db:
        _, user_email, user_role = create_user(db, "publisher-denied@example.local", "user")
    csrf = auth_client(client, user_email, user_role)

    response = client.post(
        "/recipes",
        data={
            "title": "Direkt Publizieren Verboten",
            "description": "Darf nicht live gehen.",
            "instructions": "Keine direkte Freigabe.",
            "category_select": "Unkategorisiert",
            "category_new": "",
            "category": "",
            "title_image_url": "",
            "prep_time_minutes": "20",
            "difficulty": "easy",
            "ingredients_text": "",
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 403


def test_admin_can_approve_submission_and_then_it_appears(client, db_session_factory):
    with db_session_factory() as db:
        _, admin_email, admin_role = create_user(db, "moderator@example.local", "admin")
        _, user_email, user_role = create_user(db, "user-for-approval@example.local", "user")
    user_csrf = auth_client(client, user_email, user_role)

    submit_response = client.post(
        "/submit",
        data={
            "title": "Freigabe Kandidat",
            "description": "Wird nach Freigabe sichtbar.",
            "instructions": "Schritt A\nSchritt B",
            "difficulty": "easy",
            "category_select": "Unkategorisiert",
        },
        headers={"X-CSRF-Token": user_csrf},
        follow_redirects=False,
    )
    assert submit_response.status_code == 303

    with db_session_factory() as db:
        submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.title == "Freigabe Kandidat"))
        assert submission is not None
        submission_id = submission.id
        assert submission.status == "pending"

    admin_csrf = auth_client(client, admin_email, admin_role)
    approve_response = client.post(
        f"/admin/submissions/{submission_id}/approve",
        data={"admin_note": "Freigegeben im Test."},
        headers={"X-CSRF-Token": admin_csrf},
        follow_redirects=False,
    )
    assert approve_response.status_code == 303

    with db_session_factory() as db:
        approved_submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.id == submission_id))
        assert approved_submission is not None
        assert approved_submission.status == "approved"
        recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == f"submission:{submission_id}"))
        assert recipe is not None
        assert recipe.is_published is True

    discover = client.get("/")
    assert discover.status_code == 200
    assert "Freigabe Kandidat" in discover.text


def test_repair_script_marks_non_admin_recipes_unpublished(db_session_factory):
    with db_session_factory() as db:
        user_id, _, _ = create_user(db, "legacy-user@example.local", "user")
        _ = create_user(db, "legacy-admin@example.local", "admin")
        legacy_recipe = Recipe(
            title="Legacy Direkt Veroeffentlicht",
            description="War faelschlich live.",
            instructions="Legacy Schritte",
            category="Legacy",
            prep_time_minutes=30,
            difficulty="medium",
            creator_id=user_id,
            source="user",
            source_uuid="legacy-direct-001",
            is_published=True,
        )
        db.add(legacy_recipe)
        db.commit()
        db.refresh(legacy_recipe)
        legacy_recipe_id = legacy_recipe.id

        dry_report = run_moderation_repair(db, dry_run=True)
        assert dry_report.affected_count == 1
        assert dry_report.moved_to_pending_count == 0
        db.rollback()

        apply_report = run_moderation_repair(db, dry_run=False)
        assert apply_report.affected_count == 1
        assert apply_report.moved_to_pending_count == 1
        db.commit()

    with db_session_factory() as db:
        repaired_recipe = db.scalar(select(Recipe).where(Recipe.id == legacy_recipe_id))
        assert repaired_recipe is not None
        assert repaired_recipe.is_published is False
        pending_submission = db.scalar(
            select(RecipeSubmission).where(
                RecipeSubmission.title == "Legacy Direkt Veroeffentlicht",
                RecipeSubmission.status == "pending",
            )
        )
        assert pending_submission is not None
        assert pending_submission.submitter_user_id is not None

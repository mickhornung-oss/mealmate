import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.config import get_settings
from app.database import SessionLocal
from app.models import Recipe, RecipeSubmission, User
from app.security import hash_password
from app.services import normalize_category, publish_submission_as_recipe, sanitize_difficulty

TEST_PASSWORD = "TestPass123!"
USER_COUNT = 15
ADMIN_COUNT = 3
RECIPES_PER_ADMIN = 3

CATEGORIES = [
    "Pasta",
    "Salat",
    "Suppe",
    "Dessert",
    "Fruehstueck",
    "Vegetarisch",
]
DIFFICULTIES = ["easy", "medium", "hard"]


def allow_moderation_fixtures() -> bool:
    settings = get_settings()
    return settings.app_env == "dev" or os.getenv("TESTING") == "1"


def ensure_user(db, email: str, role: str) -> tuple[User, str]:
    existing = db.scalar(select(User).where(User.email == email))
    if existing:
        changed = False
        if existing.role != role:
            existing.role = role
            changed = True
        if not existing.hashed_password:
            existing.hashed_password = hash_password(TEST_PASSWORD)
            changed = True
        return existing, "updated" if changed else "unchanged"
    user = User(email=email, hashed_password=hash_password(TEST_PASSWORD), role=role)
    db.add(user)
    db.flush()
    return user, "created"


def ensure_admin_recipe(db, owner: User, owner_index: int, recipe_index: int) -> bool:
    source_uuid = f"test-seed:admin:{owner_index:02d}:recipe:{recipe_index}"
    existing = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))
    if existing:
        return False
    category = normalize_category(CATEGORIES[(owner_index + recipe_index) % len(CATEGORIES)])
    difficulty = sanitize_difficulty(DIFFICULTIES[(owner_index + recipe_index - 1) % len(DIFFICULTIES)])
    db.add(
        Recipe(
            title=f"Testrezept ADMIN {owner_index:02d}-{recipe_index}",
            title_image_url=f"https://picsum.photos/seed/admin{owner_index:02d}{recipe_index}/640/360",
            description="Automatisch erzeugtes Admin-Testrezept fuer UI- und Workflow-Tests.",
            instructions=(
                "1. Zutaten vorbereiten.\n"
                "2. Alles nach Rezeptschritten kombinieren.\n"
                "3. Abschmecken und servieren."
            ),
            category=category,
            prep_time_minutes=15 + recipe_index * 10,
            difficulty=difficulty,
            creator_id=owner.id,
            source="test_seed",
            source_uuid=source_uuid,
            is_published=True,
        )
    )
    return True


def ensure_submission_fixture(
    db,
    *,
    title: str,
    submitter: User,
    admin: User,
    status: str,
    admin_note: str | None = None,
) -> tuple[RecipeSubmission, bool]:
    submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.title == title))
    created = False
    if not submission:
        submission = RecipeSubmission(
            submitter_user_id=submitter.id,
            submitter_email=None,
            title=title,
            description="Gezielte Moderations-Testeinreichung.",
            category=normalize_category("Test Kategorie"),
            difficulty="medium",
            prep_time_minutes=25,
            servings_text="2 Portionen",
            instructions="1. Testeinreichung vorbereiten.\n2. Speichern und Moderation pruefen.",
            status="pending",
        )
        db.add(submission)
        db.flush()
        created = True

    if status == "pending":
        if submission.status != "pending":
            submission.status = "pending"
            submission.admin_note = None
            submission.reviewed_by_admin_id = None
            submission.reviewed_at = None
        return submission, created

    if status == "rejected":
        submission.status = "rejected"
        submission.admin_note = admin_note or "Nicht ausreichend beschrieben."
        submission.reviewed_by_admin_id = admin.id
        submission.reviewed_at = datetime.now(timezone.utc)
        return submission, created

    if status == "approved":
        recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == f"submission:{submission.id}"))
        if recipe is None:
            publish_submission_as_recipe(db, submission, admin.id)
        submission.status = "approved"
        submission.admin_note = admin_note or "Freigegeben fuer Discover."
        submission.reviewed_by_admin_id = admin.id
        submission.reviewed_at = datetime.now(timezone.utc)
        return submission, created

    raise ValueError(f"Unknown status: {status}")


def seed_test_data() -> None:
    db = SessionLocal()
    try:
        users_created = 0
        users_updated = 0
        admin_recipes_created = 0
        moderation_fixtures_created = 0

        test_users: list[User] = []
        test_admins: list[User] = []

        for index in range(1, USER_COUNT + 1):
            email = f"test.user{index:02d}@mealmate.local"
            user, state = ensure_user(db, email, "user")
            test_users.append(user)
            if state == "created":
                users_created += 1
            elif state == "updated":
                users_updated += 1

        for index in range(1, ADMIN_COUNT + 1):
            email = f"test.admin{index:02d}@mealmate.local"
            admin, state = ensure_user(db, email, "admin")
            test_admins.append(admin)
            if state == "created":
                users_created += 1
            elif state == "updated":
                users_updated += 1
            for recipe_index in range(1, RECIPES_PER_ADMIN + 1):
                if ensure_admin_recipe(db, admin, index, recipe_index):
                    admin_recipes_created += 1

        if allow_moderation_fixtures() and test_users and test_admins:
            submitter = test_users[0]
            reviewer = test_admins[0]
            for idx in range(1, 4):
                _, created = ensure_submission_fixture(
                    db,
                    title=f"Moderation Pending {idx}",
                    submitter=submitter,
                    admin=reviewer,
                    status="pending",
                )
                if created:
                    moderation_fixtures_created += 1
            _, created_rejected = ensure_submission_fixture(
                db,
                title="Moderation Rejected 1",
                submitter=submitter,
                admin=reviewer,
                status="rejected",
                admin_note="Ablehnung: Zutatenliste unvollstaendig.",
            )
            if created_rejected:
                moderation_fixtures_created += 1
            _, created_approved = ensure_submission_fixture(
                db,
                title="Moderation Approved 1",
                submitter=submitter,
                admin=reviewer,
                status="approved",
                admin_note="Freigabe: Inhalt geprueft.",
            )
            if created_approved:
                moderation_fixtures_created += 1

        db.commit()
        print("Seed abgeschlossen.")
        print(f"Passwort fuer alle neuen Test-Accounts: {TEST_PASSWORD}")
        print(f"Neue Benutzer/Admins: {users_created}")
        print(f"Aktualisierte Benutzer/Admins: {users_updated}")
        print(f"Neue Admin-Rezepte (published): {admin_recipes_created}")
        print(f"Neue Moderations-Fixtures: {moderation_fixtures_created}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_test_data()

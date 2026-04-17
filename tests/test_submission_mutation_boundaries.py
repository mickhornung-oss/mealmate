from __future__ import annotations

from app import services_submission
from tests.helpers import create_admin_user, create_normal_user, create_pending_submission, unique_email


def test_publish_submission_orchestrates_build_and_copy_steps(db_session_factory, monkeypatch):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("submitter"), "UserPass123!")
        submission = create_pending_submission(db, user.id, "Boundary Submission Title")
        admin_id = admin.id
        submission_id = submission.id

    calls = {"build": 0, "copy_ingredients": 0, "copy_images": 0}

    def fake_build(submission, *, admin_id, normalized_raw_category, guessed_canonical, source_uuid):
        calls["build"] += 1
        return {
            "title": submission.title.strip()[:255],
            "description": submission.description.strip(),
            "instructions": submission.instructions.strip(),
            "category": normalized_raw_category,
            "canonical_category": guessed_canonical,
            "prep_time_minutes": max(int(submission.prep_time_minutes or 30), 1),
            "difficulty": submission.difficulty,
            "creator_id": admin_id,
            "source": "submission",
            "source_uuid": source_uuid,
            "source_url": None,
            "source_image_url": None,
            "title_image_url": None,
            "servings_text": (submission.servings_text or "").strip()[:120] or None,
            "total_time_minutes": None,
            "is_published": True,
        }

    def fake_copy_ingredients(db, submission, recipe):
        _ = db
        _ = submission
        _ = recipe
        calls["copy_ingredients"] += 1

    def fake_copy_images(db, submission, recipe):
        _ = db
        _ = submission
        _ = recipe
        calls["copy_images"] += 1

    monkeypatch.setattr(services_submission, "_build_submission_recipe_values", fake_build)
    monkeypatch.setattr(services_submission, "_copy_submission_ingredients_to_recipe", fake_copy_ingredients)
    monkeypatch.setattr(services_submission, "_copy_submission_images_to_recipe", fake_copy_images)

    with db_session_factory() as db:
        submission = db.get(services_submission.RecipeSubmission, submission_id)
        recipe = services_submission.publish_submission_as_recipe(db, submission, admin_id)
        db.commit()
        assert recipe.id is not None

    assert calls["build"] == 1
    assert calls["copy_ingredients"] == 1
    assert calls["copy_images"] == 1

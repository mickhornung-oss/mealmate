from __future__ import annotations

from sqlalchemy import select

from app.models import Recipe, RecipeSubmission
from app.services_submission import publish_submission_as_recipe
from tests.helpers import create_admin_user, create_normal_user, create_pending_submission, unique_email


def test_publish_submission_service_does_not_commit_transaction(db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("submitter"), "UserPass123!")
        submission = create_pending_submission(db, user.id, title="Txn Contract Submission")
        admin_id = admin.id
        submission_id = submission.id

    with db_session_factory() as db:
        submission = db.get(RecipeSubmission, submission_id)
        recipe = publish_submission_as_recipe(db, submission, admin_id)
        source_uuid = recipe.source_uuid
        assert source_uuid == f"submission:{submission_id}"
        db.rollback()

    with db_session_factory() as verify_db:
        persisted = verify_db.scalar(select(Recipe).where(Recipe.source_uuid == f"submission:{submission_id}"))
        assert persisted is None

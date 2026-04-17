from __future__ import annotations

from sqlalchemy import select

from app.models import RecipeImage, SubmissionImage
from tests.helpers import (
    SMALL_PNG_BYTES,
    create_admin_user,
    create_normal_user,
    create_pending_submission,
    create_published_recipe,
    get_csrf,
    post_form,
    set_auth_cookie,
    unique_email,
)


def _seed_recipe_with_image(db, *, admin_id: int, title: str) -> tuple[int, int]:
    recipe = create_published_recipe(db, admin_id, title=title, is_published=True)
    image = RecipeImage(
        recipe_id=recipe.id,
        filename="contract.png",
        content_type="image/png",
        data=SMALL_PNG_BYTES,
        is_primary=True,
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return recipe.id, image.id


def test_recipe_image_delete_api_non_admin_returns_403_for_existing_and_missing(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("perm-del-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("perm-del-user"), "UserPass123!")
        recipe_id, image_id = _seed_recipe_with_image(db, admin_id=admin.id, title="Permission Delete API")
        set_auth_cookie(client, user.user_uid, user.role)

    csrf = get_csrf(client, f"/recipes/{recipe_id}")
    existing = client.delete(f"/images/{image_id}", headers={"X-CSRF-Token": csrf})
    missing = client.delete("/images/999999", headers={"X-CSRF-Token": csrf})
    assert existing.status_code == 403
    assert missing.status_code == 403


def test_recipe_image_set_primary_form_non_admin_returns_403_for_existing_and_missing(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("perm-primary-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("perm-primary-user"), "UserPass123!")
        recipe_id, image_id = _seed_recipe_with_image(db, admin_id=admin.id, title="Permission Set Primary")
        set_auth_cookie(client, user.user_uid, user.role)

    existing = post_form(
        client,
        f"/images/{image_id}/set-primary",
        data={},
        referer_page=f"/recipes/{recipe_id}",
        follow_redirects=False,
    )
    missing = post_form(
        client,
        "/images/999999/set-primary",
        data={},
        referer_page=f"/recipes/{recipe_id}",
        follow_redirects=False,
    )
    assert existing.status_code == 403
    assert missing.status_code == 403


def test_submission_image_requires_auth_and_masks_non_owner_as_404(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("perm-sub-admin"), "AdminPass123!")
        owner = create_normal_user(db, unique_email("perm-sub-owner"), "UserPass123!")
        outsider = create_normal_user(db, unique_email("perm-sub-outsider"), "UserPass123!")
        submission = create_pending_submission(db, owner.id, "Permission Submission Image")
        image = SubmissionImage(
            submission_id=submission.id,
            filename="submission.png",
            content_type="image/png",
            data=SMALL_PNG_BYTES,
            is_primary=True,
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        image_id = image.id

        owner_uid, owner_role = owner.user_uid, owner.role
        outsider_uid, outsider_role = outsider.user_uid, outsider.role
        admin_uid, admin_role = admin.user_uid, admin.role

    unauthenticated = client.get(f"/submission-images/{image_id}")
    assert unauthenticated.status_code == 401

    set_auth_cookie(client, outsider_uid, outsider_role)
    outsider_response = client.get(f"/submission-images/{image_id}")
    assert outsider_response.status_code == 404

    set_auth_cookie(client, owner_uid, owner_role)
    owner_response = client.get(f"/submission-images/{image_id}")
    assert owner_response.status_code == 200
    assert owner_response.headers.get("content-type", "").startswith("image/png")

    set_auth_cookie(client, admin_uid, admin_role)
    admin_response = client.get(f"/submission-images/{image_id}")
    assert admin_response.status_code == 200


def test_submission_image_owner_query_does_not_load_foreign_rows(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("perm-sub-sql-admin"), "AdminPass123!")
        owner = create_normal_user(db, unique_email("perm-sub-sql-owner"), "UserPass123!")
        outsider = create_normal_user(db, unique_email("perm-sub-sql-outsider"), "UserPass123!")
        submission = create_pending_submission(db, owner.id, "Permission Submission SQL")
        image = SubmissionImage(
            submission_id=submission.id,
            filename="submission-sql.png",
            content_type="image/png",
            data=SMALL_PNG_BYTES,
            is_primary=True,
        )
        db.add(image)
        db.commit()
        db.refresh(image)
        image_id = image.id
        outsider_uid, outsider_role = outsider.user_uid, outsider.role
        admin_uid, admin_role = admin.user_uid, admin.role

    set_auth_cookie(client, outsider_uid, outsider_role)
    response = client.get(f"/submission-images/{image_id}")
    assert response.status_code == 404

    set_auth_cookie(client, admin_uid, admin_role)
    response_admin = client.get(f"/submission-images/{image_id}")
    assert response_admin.status_code == 200

    with db_session_factory() as db:
        persisted = db.scalar(select(SubmissionImage).where(SubmissionImage.id == image_id))
        assert persisted is not None

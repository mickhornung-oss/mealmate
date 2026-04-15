from __future__ import annotations

from sqlalchemy import and_, func, select

from app.config import get_settings
from app.models import RecipeImage, RecipeImageChangeFile, RecipeImageChangeRequest
from tests.helpers import (
    SMALL_PNG_BYTES,
    create_admin_user,
    create_normal_user,
    create_published_recipe,
    post_form,
    unique_email,
)


SUCCESS_CODES = {200, 302, 303}


def _login(client, email: str, password: str) -> None:
    response = post_form(
        client,
        "/login",
        data={"identifier": email, "password": password},
        referer_page="/login",
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}


def test_upload_rejects_png_extension_with_html_payload(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("upload-admin-html"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="Upload HTML as PNG")
        admin_email = admin.email
        recipe_id = recipe.id

    _login(client, admin_email, "AdminPass123!")

    response = post_form(
        client,
        f"/recipes/{recipe_id}/images",
        data={"set_primary": "true"},
        referer_page=f"/recipes/{recipe_id}",
        files={"file": ("recipe.png", b"<html><script>alert(1)</script></html>", "image/png")},
        follow_redirects=False,
    )
    assert response.status_code not in SUCCESS_CODES

    with db_session_factory() as db:
        count = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id == recipe_id)) or 0
        assert int(count) == 0


def test_upload_rejects_fake_png_with_wrong_bytes(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("upload-admin-fake"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="Upload Fake PNG")
        admin_email = admin.email
        recipe_id = recipe.id

    _login(client, admin_email, "AdminPass123!")

    response = post_form(
        client,
        f"/recipes/{recipe_id}/images",
        data={"set_primary": "true"},
        referer_page=f"/recipes/{recipe_id}",
        files={"file": ("fake.png", b"RIFFxxxxWEBPbad", "image/png")},
        follow_redirects=False,
    )
    assert response.status_code not in SUCCESS_CODES

    with db_session_factory() as db:
        count = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id == recipe_id)) or 0
        assert int(count) == 0


def test_upload_rejects_oversized_payload(client, db_session_factory):
    settings = get_settings()
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("upload-admin-large"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="Upload Large Payload")
        admin_email = admin.email
        recipe_id = recipe.id

    _login(client, admin_email, "AdminPass123!")

    oversized = b"\x89PNG\r\n\x1a\n" + (b"A" * (settings.max_upload_mb * 1024 * 1024 + 1024))
    response = post_form(
        client,
        f"/recipes/{recipe_id}/images",
        data={"set_primary": "true"},
        referer_page=f"/recipes/{recipe_id}",
        files={"file": ("large.png", oversized, "image/png")},
        follow_redirects=False,
    )
    assert response.status_code == 413

    with db_session_factory() as db:
        count = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id == recipe_id)) or 0
        assert int(count) == 0


def test_svg_upload_is_blocked_in_image_change_request(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("upload-admin-svg"), "AdminPass123!")
        user = create_normal_user(db, unique_email("upload-user-svg"), "UserPass123!")
        recipe = create_published_recipe(db, admin.id, title="SVG Block Test")
        user_email = user.email
        user_id = user.id
        recipe_id = recipe.id

    _login(client, user_email, "UserPass123!")

    svg_payload = b"<svg xmlns='http://www.w3.org/2000/svg'><script>alert(1)</script></svg>"
    response = post_form(
        client,
        f"/recipes/{recipe_id}/image-change-request",
        data={},
        referer_page=f"/recipes/{recipe_id}",
        files={"file": ("evil.svg", svg_payload, "image/svg+xml")},
        follow_redirects=False,
    )
    assert response.status_code not in SUCCESS_CODES

    with db_session_factory() as db:
        count = db.scalar(
            select(func.count())
            .select_from(RecipeImageChangeRequest)
            .where(
                RecipeImageChangeRequest.recipe_id == recipe_id,
                RecipeImageChangeRequest.requester_user_id == user_id,
            )
        ) or 0
        assert int(count) == 0


def test_filename_traversal_is_sanitized_for_admin_upload(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("upload-admin-name"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="Filename sanitize admin")
        admin_email = admin.email
        recipe_id = recipe.id

    _login(client, admin_email, "AdminPass123!")

    response = post_form(
        client,
        f"/recipes/{recipe_id}/images",
        data={"set_primary": "true"},
        referer_page=f"/recipes/{recipe_id}",
        files={"file": ("..\\..\\evil.png", SMALL_PNG_BYTES, "image/png")},
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}

    with db_session_factory() as db:
        image = db.scalar(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id).order_by(RecipeImage.id.desc()))
        assert image is not None
        assert ".." not in image.filename
        assert "/" not in image.filename
        assert "\\" not in image.filename
        assert image.filename.endswith(".png")


def test_filename_traversal_is_sanitized_for_user_image_change_request(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("upload-admin-name-user"), "AdminPass123!")
        user = create_normal_user(db, unique_email("upload-user-name"), "UserPass123!")
        recipe = create_published_recipe(db, admin.id, title="Filename sanitize user")
        user_email = user.email
        user_id = user.id
        recipe_id = recipe.id

    _login(client, user_email, "UserPass123!")

    response = post_form(
        client,
        f"/recipes/{recipe_id}/image-change-request",
        data={},
        referer_page=f"/recipes/{recipe_id}",
        files={"file": ("C:\\temp\\..\\evil.png", SMALL_PNG_BYTES, "image/png")},
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}

    with db_session_factory() as db:
        file_row = db.scalar(
            select(RecipeImageChangeFile)
            .join(RecipeImageChangeRequest, RecipeImageChangeRequest.id == RecipeImageChangeFile.request_id)
            .where(
                and_(
                    RecipeImageChangeRequest.recipe_id == recipe_id,
                    RecipeImageChangeRequest.requester_user_id == user_id,
                )
            )
            .order_by(RecipeImageChangeFile.id.desc())
        )
        assert file_row is not None
        assert ".." not in file_row.filename
        assert "/" not in file_row.filename
        assert "\\" not in file_row.filename
        assert file_row.filename.endswith(".png")

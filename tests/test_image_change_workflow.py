from io import BytesIO
from urllib.parse import quote

from PIL import Image
from sqlalchemy import select

from app.config import get_settings
from app.models import Recipe, RecipeImage, RecipeImageChangeRequest, User
from app.security import create_access_token, hash_password


def build_png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (2, 2), color=(32, 128, 96)).save(buffer, format="PNG")
    return buffer.getvalue()


PNG_BYTES = build_png_bytes()


def create_user(db, email: str, role: str = "user") -> tuple[int, str, str]:
    user = User(
        email=email.strip().lower(),
        hashed_password=hash_password("StrongPass123!"),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id, user.user_uid, user.role


def create_recipe(db, creator_id: int, *, source_image_url: str | None = None) -> int:
    recipe = Recipe(
        title="Bildtest Rezept",
        description="Beschreibung",
        instructions="Schritt 1",
        category="Test",
        prep_time_minutes=20,
        difficulty="easy",
        creator_id=creator_id,
        source="test",
        source_image_url=source_image_url,
        is_published=True,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe.id


def auth_client(client, user_uid: str, role: str) -> str:
    token = create_access_token(user_uid, role)
    client.cookies.set("access_token", f"Bearer {token}")
    page = client.get("/")
    assert page.status_code == 200
    csrf = client.cookies.get("csrf_token")
    assert csrf
    return str(csrf)


def test_image_fallback_order(client, db_session_factory):
    with db_session_factory() as db:
        admin_id, _, _ = create_user(db, "fallback-admin@example.local", "admin")
        external_url = "https://upload.wikimedia.org/source-image.jpg"
        recipe_id = create_recipe(db, admin_id, source_image_url=external_url)

    response = client.get("/")
    assert response.status_code == 200
    assert f"/external-image?url={quote(external_url, safe='')}" in response.text

    with db_session_factory() as db:
        db.add(
            RecipeImage(
                recipe_id=recipe_id,
                filename="primary.png",
                content_type="image/png",
                data=PNG_BYTES,
                is_primary=True,
            )
        )
        db.commit()
        primary_image = db.scalar(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id))
        assert primary_image is not None
        image_id = primary_image.id

    response_with_db_image = client.get("/")
    assert response_with_db_image.status_code == 200
    assert f"/images/{image_id}" in response_with_db_image.text


def test_user_cannot_upload_direct_recipe_image(client, db_session_factory):
    with db_session_factory() as db:
        admin_id, _, _ = create_user(db, "img-admin@example.local", "admin")
        recipe_id = create_recipe(db, admin_id)
        _, user_uid, user_role = create_user(db, "img-user@example.local", "user")

    csrf = auth_client(client, user_uid, user_role)
    response = client.post(
        f"/recipes/{recipe_id}/images",
        data={"set_primary": "true", "csrf_token": csrf},
        files={"file": ("test.png", PNG_BYTES, "image/png")},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 403


def test_user_image_change_request_pending(client, db_session_factory):
    with db_session_factory() as db:
        admin_id, _, _ = create_user(db, "request-admin@example.local", "admin")
        recipe_id = create_recipe(db, admin_id)
        _, user_uid, user_role = create_user(db, "request-user@example.local", "user")

    csrf = auth_client(client, user_uid, user_role)
    response = client.post(
        f"/recipes/{recipe_id}/image-change-request",
        data={"csrf_token": csrf},
        files={"file": ("proposal.png", PNG_BYTES, "image/png")},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}

    with db_session_factory() as db:
        request_row = db.scalar(select(RecipeImageChangeRequest).where(RecipeImageChangeRequest.recipe_id == recipe_id))
        assert request_row is not None
        assert request_row.status == "pending"
        recipe_images = db.scalars(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id)).all()
        assert len(recipe_images) == 0


def test_admin_approves_image_change_creates_primary_image(client, db_session_factory):
    with db_session_factory() as db:
        admin_id, admin_uid, admin_role = create_user(db, "approve-admin@example.local", "admin")
        recipe_id = create_recipe(db, admin_id, source_image_url="https://upload.wikimedia.org/old.jpg")
        existing_image = RecipeImage(
            recipe_id=recipe_id,
            filename="existing.png",
            content_type="image/png",
            data=PNG_BYTES,
            is_primary=True,
        )
        db.add(existing_image)
        _, user_uid, user_role = create_user(db, "approve-user@example.local", "user")
        db.commit()

    csrf_user = auth_client(client, user_uid, user_role)
    create_request = client.post(
        f"/recipes/{recipe_id}/image-change-request",
        data={"csrf_token": csrf_user},
        files={"file": ("new-primary.png", PNG_BYTES, "image/png")},
        headers={"X-CSRF-Token": csrf_user},
        follow_redirects=False,
    )
    assert create_request.status_code in {302, 303}

    with db_session_factory() as db:
        pending_request = db.scalar(
            select(RecipeImageChangeRequest).where(
                RecipeImageChangeRequest.recipe_id == recipe_id,
                RecipeImageChangeRequest.status == "pending",
            )
        )
        assert pending_request is not None
        request_id = pending_request.id

    csrf_admin = auth_client(client, admin_uid, admin_role)
    approve_response = client.post(
        f"/admin/image-change-requests/{request_id}/approve",
        data={"admin_note": "Freigegeben", "csrf_token": csrf_admin},
        headers={"X-CSRF-Token": csrf_admin},
        follow_redirects=False,
    )
    assert approve_response.status_code in {302, 303}

    with db_session_factory() as db:
        approved_request = db.scalar(select(RecipeImageChangeRequest).where(RecipeImageChangeRequest.id == request_id))
        assert approved_request is not None
        assert approved_request.status == "approved"
        images = db.scalars(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id).order_by(RecipeImage.id.asc())).all()
        assert len(images) == 2
        primary_images = [item for item in images if item.is_primary]
        assert len(primary_images) == 1
        assert primary_images[0].filename != "existing.png"


def test_csp_allows_external_images_when_configured(client):
    settings = get_settings()
    original_value = settings.csp_img_src
    settings.csp_img_src = "'self' data: https://upload.wikimedia.org https://kochwiki.org"
    try:
        response = client.get("/")
        assert response.status_code == 200
        csp = response.headers.get("content-security-policy", "")
        assert "img-src 'self' data: https://upload.wikimedia.org https://kochwiki.org" in csp
    finally:
        settings.csp_img_src = original_value

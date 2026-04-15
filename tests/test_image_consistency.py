from __future__ import annotations

import re
from urllib.parse import quote

from sqlalchemy import select

from app.models import RecipeImage
from tests.helpers import SMALL_PNG_BYTES, create_admin_user, create_published_recipe, unique_email

IMAGES_SECTION_RE = re.compile(r'<section class="panel" id="recipe-images-section">(.*?)</section>', re.DOTALL)


def _extract_images_section(html_text: str) -> str:
    match = IMAGES_SECTION_RE.search(html_text)
    return match.group(1) if match else html_text


def test_image_fallback_order_primary_over_external_over_placeholder(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("img-cons-admin"), "AdminPass123!")
        recipe_primary = create_published_recipe(db, admin.id, title="Primary Beats External")
        recipe_primary.source_image_url = "https://upload.wikimedia.org/a-primary.jpg"
        db.add(recipe_primary)
        db.flush()
        db.add(
            RecipeImage(
                recipe_id=recipe_primary.id,
                filename="primary.png",
                content_type="image/png",
                data=SMALL_PNG_BYTES,
                is_primary=True,
            )
        )
        recipe_external_only = create_published_recipe(db, admin.id, title="External Fallback Only")
        recipe_external_only.source_image_url = "https://upload.wikimedia.org/external-only.jpg"
        db.add(recipe_external_only)
        recipe_placeholder = create_published_recipe(db, admin.id, title="No Image Placeholder")
        recipe_placeholder.source_image_url = None
        recipe_placeholder.title_image_url = None
        db.add(recipe_placeholder)
        db.commit()
        db.refresh(recipe_primary)
        db.refresh(recipe_external_only)
        db.refresh(recipe_placeholder)
        primary_image = db.scalar(select(RecipeImage).where(RecipeImage.recipe_id == recipe_primary.id))
        assert primary_image is not None

    primary_detail = client.get(f"/recipes/{recipe_primary.id}")
    assert primary_detail.status_code == 200
    primary_section = _extract_images_section(primary_detail.text)
    assert f"/images/{primary_image.id}" in primary_section

    external_detail = client.get(f"/recipes/{recipe_external_only.id}")
    assert external_detail.status_code == 200
    external_section = _extract_images_section(external_detail.text)
    expected_external_proxy = f"/external-image?url={quote(recipe_external_only.source_image_url, safe='')}"
    assert expected_external_proxy in external_section

    placeholder_detail = client.get(f"/recipes/{recipe_placeholder.id}")
    assert placeholder_detail.status_code == 200
    placeholder_section = _extract_images_section(placeholder_detail.text)
    assert "/images/" not in placeholder_section
    assert "/external-image?url=" not in placeholder_section


def test_home_page_has_multiple_distinct_card_image_sources(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("img-grid-admin"), "AdminPass123!")
        created_recipe_ids: list[int] = []
        for index in range(3):
            recipe = create_published_recipe(db, admin.id, title=f"Grid Image Recipe {index}")
            db.add(
                RecipeImage(
                    recipe_id=recipe.id,
                    filename=f"grid-{index}.png",
                    content_type="image/png",
                    data=SMALL_PNG_BYTES,
                    is_primary=True,
                )
            )
            created_recipe_ids.append(recipe.id)
        db.commit()
        _ = created_recipe_ids

    response = client.get("/?per_page=80")
    assert response.status_code == 200
    image_paths = re.findall(r"/images/\d+", response.text)
    assert len(image_paths) >= 3
    assert len(set(image_paths)) >= 3

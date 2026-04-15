from __future__ import annotations

from pathlib import Path

from app.models import Review
from app.translation_models import RecipeTranslation
from tests.helpers import create_admin_user, create_normal_user, create_published_recipe, unique_email


def test_recipe_translation_xss_payload_is_escaped_in_detail(client, db_session_factory):
    payload_script = "<script>alert(1)</script>"
    payload_img = "<img src=x onerror=alert(1)>"

    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("xss-admin-tr"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="XSS Translation Recipe")
        db.add(
            RecipeTranslation(
                recipe_id=recipe.id,
                language="en",
                title=payload_script,
                description=payload_img,
                instructions=f"Step 1 {payload_script}\nStep 2 {payload_img}",
                ingredients_text=payload_img,
                source_hash="a" * 64,
                stale=False,
                quality_flag="ok",
            )
        )
        db.commit()
        recipe_id = recipe.id

    response = client.get(f"/recipes/{recipe_id}?lang=en")
    assert response.status_code == 200
    body = response.text

    assert payload_script not in body
    assert payload_img not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
    assert "&lt;img src=x onerror=alert(1)&gt;" in body


def test_user_generated_recipe_and_review_xss_is_escaped(client, db_session_factory):
    payload_script = "<script>alert(1)</script>"
    payload_img = "<img src=x onerror=alert(1)>"

    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("xss-admin-ugc"), "AdminPass123!")
        user = create_normal_user(db, unique_email("xss-user-ugc"), "UserPass123!")
        recipe = create_published_recipe(db, admin.id, title=payload_script)
        recipe.description = payload_img
        recipe.instructions = f"{payload_script}\n{payload_img}"
        db.add(recipe)
        db.flush()
        db.add(Review(recipe_id=recipe.id, user_id=user.id, rating=5, comment=payload_img))
        db.commit()
        recipe_id = recipe.id

    response = client.get(f"/recipes/{recipe_id}")
    assert response.status_code == 200
    body = response.text

    assert payload_script not in body
    assert payload_img not in body
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in body
    assert "&lt;img src=x onerror=alert(1)&gt;" in body


def test_templates_do_not_use_safe_filter_for_untrusted_content():
    templates_root = Path("app/templates")
    html_files = list(templates_root.rglob("*.html"))
    offenders: list[str] = []

    for file_path in html_files:
        content = file_path.read_text(encoding="utf-8")
        if "|safe" in content:
            offenders.append(str(file_path).replace("\\", "/"))

    assert offenders == []


def test_no_raw_i18n_keys_are_shown_in_ui_pages(client):
    urls = ["/", "/login", "/register"]
    forbidden_key_tokens = [
        "home.hero_title",
        "home.hero_subtitle",
        "nav.discover",
        "HOME.HERO_EYEBROW",
    ]

    for url in urls:
        response = client.get(url)
        assert response.status_code == 200
        body = response.text
        for token in forbidden_key_tokens:
            assert token not in body

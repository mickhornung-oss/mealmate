from __future__ import annotations

from dataclasses import dataclass

import pytest
from sqlalchemy import func, select

from app.main import app
from app.models import Recipe, User
from tests.helpers import create_admin_user, post_form, unique_email


MOJIBAKE_MARKERS = ("Ã", "Â", "â€", "\ufffd")
LEAK_MARKERS = ("home.hero_title", "nav.discover", "HOME.HERO_EYEBROW")


@dataclass
class SeededQA:
    admin_email: str
    admin_password: str
    recipe_titles: list[str]
    user_like_title: str


def _seed_ten_test_recipes(db_session_factory) -> SeededQA:
    admin_password = "AdminPass123!"
    admin_email = unique_email("zz-admin")
    recipes = [
        ("ZZ_TEST_01_Fruehstueck_Bowl", "Frühstück", None),
        ("ZZ_TEST_02_Abendessen_Pasta", "Abendessen", None),
        ("ZZ_TEST_03_Aepfel_Oel_ÄÖÜß", "Dessert", "https://example.com/test-03.jpg"),
        ("ZZ_TEST_04_Getraenk_Smoothie", "Getränke", "https://example.com/test-04.jpg"),
        ("ZZ_TEST_05_Salat_Gruen", "Salat", None),
        ("ZZ_TEST_06_Suppe_Eintopf", "Suppe & Eintopf", None),
        ("ZZ_TEST_07_Uebergroesse_Größe", "Hauptgericht", "https://example.com/test-07.jpg"),
        ("ZZ_TEST_08_Grosse_Variante", "Hauptgericht", "https://example.com/test-08.jpg"),
        ("ZZ_TEST_09_Snack_Wrap", "Snack", None),
        ("ZZ_TEST_10_Beilage_Kartoffel", "Beilage", None),
    ]
    with db_session_factory() as db:
        admin = create_admin_user(db, admin_email, admin_password)
        for index, (title, category, source_image_url) in enumerate(recipes, start=1):
            db.add(
                Recipe(
                    title=title,
                    description=f"ZZ QA Beschreibung {index}",
                    instructions=f"ZZ QA Schritt {index}A\nZZ QA Schritt {index}B",
                    category=category,
                    canonical_category=category if category != "Getränke" else "Getränke",
                    prep_time_minutes=20 + index,
                    difficulty="easy" if index % 3 == 0 else "medium",
                    creator_id=admin.id,
                    source="qa_roundup",
                    is_published=True,
                    source_image_url=source_image_url,
                )
            )
        db.commit()
        count_seeded = db.scalar(
            select(func.count()).select_from(Recipe).where(Recipe.title.like("ZZ_TEST_%"))
        )
        assert int(count_seeded or 0) == 10
    return SeededQA(
        admin_email=admin_email,
        admin_password=admin_password,
        recipe_titles=[title for title, _, _ in recipes],
        user_like_title="ZZ_TEST_CRUD_Ändern",
    )


def _cleanup_test_recipes(db_session_factory) -> int:
    with db_session_factory() as db:
        rows = db.scalars(select(Recipe).where(Recipe.title.like("ZZ_TEST_%"))).all()
        removed = len(rows)
        for recipe in rows:
            db.delete(recipe)
        db.commit()
        remaining = db.scalar(select(func.count()).select_from(Recipe).where(Recipe.title.like("ZZ_TEST_%")))
        assert int(remaining or 0) == 0
    return removed


@pytest.fixture()
def seeded_qa(db_session_factory):
    data = _seed_ten_test_recipes(db_session_factory)
    yield data
    _cleanup_test_recipes(db_session_factory)


def _login(client, email: str, password: str) -> None:
    response = post_form(
        client,
        "/login",
        data={"identifier": email, "password": password},
        referer_page="/login",
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}


def test_qa_seed_and_search_roundtrip(client, db_session_factory, seeded_qa):
    response_all = client.get("/")
    assert response_all.status_code == 200
    assert seeded_qa.recipe_titles[0] in response_all.text
    assert seeded_qa.recipe_titles[-1] in response_all.text

    response_case = client.get("/?title=zz_test_01")
    assert response_case.status_code == 200
    assert "ZZ_TEST_01_Fruehstueck_Bowl" in response_case.text

    response_umlaut_exact = client.get("/?title=ÄÖÜß")
    assert response_umlaut_exact.status_code == 200
    assert "ZZ_TEST_03_Aepfel_Oel_ÄÖÜß" in response_umlaut_exact.text

    response_variant_umlaut = client.get("/?title=Größe")
    assert response_variant_umlaut.status_code == 200
    assert "ZZ_TEST_07_Uebergroesse_Größe" in response_variant_umlaut.text

    response_variant_ascii = client.get("/?title=Grosse")
    assert response_variant_ascii.status_code == 200
    assert "ZZ_TEST_08_Grosse_Variante" in response_variant_ascii.text

    response_special = client.get("/?title=%25__")
    assert response_special.status_code == 200

    response_long = client.get("/?title=" + ("z" * 300))
    assert response_long.status_code == 200

    with db_session_factory() as db:
        cleanup_removed = _cleanup_test_recipes(db_session_factory)
        assert cleanup_removed == 10
        reseeded = _seed_ten_test_recipes(db_session_factory)
        assert len(reseeded.recipe_titles) == 10


def test_qa_admin_user_permissions_and_role_change(client, db_session_factory, seeded_qa):
    guest_admin = client.get("/admin", follow_redirects=False)
    assert guest_admin.status_code in {302, 303, 401, 403}

    user1_email = unique_email("zz-user1")
    user2_email = unique_email("zz-user2")
    user_password = "UserPass123!"

    register_user1 = post_form(
        client,
        "/register",
        data={"email": user1_email, "username": "zz.user1", "password": user_password},
        referer_page="/register",
        follow_redirects=False,
    )
    assert register_user1.status_code in {302, 303}
    post_form(client, "/logout", data={}, referer_page="/", follow_redirects=False)

    register_user2 = post_form(
        client,
        "/register",
        data={"email": user2_email, "username": "zz.user2", "password": user_password},
        referer_page="/register",
        follow_redirects=False,
    )
    assert register_user2.status_code in {302, 303}
    post_form(client, "/logout", data={}, referer_page="/", follow_redirects=False)

    _login(client, user2_email, user_password)
    user_admin_access = client.get("/admin", follow_redirects=False)
    assert user_admin_access.status_code in {302, 303, 401, 403}
    post_form(client, "/logout", data={}, referer_page="/", follow_redirects=False)

    _login(client, seeded_qa.admin_email, seeded_qa.admin_password)
    admin_page = client.get("/admin")
    assert admin_page.status_code == 200

    with db_session_factory() as db:
        user1 = db.scalar(select(User).where(User.email == user1_email))
        assert user1 is not None
        user1_id = int(user1.id)

    change_role = post_form(
        client,
        f"/admin/users/{user1_id}/role",
        data={"role": "admin"},
        referer_page="/admin",
        follow_redirects=False,
    )
    assert change_role.status_code in {302, 303}

    with db_session_factory() as db:
        promoted = db.scalar(select(User).where(User.id == user1_id))
        assert promoted is not None
        assert promoted.role == "admin"


def test_qa_recipe_crud_update_delete_flow(client, db_session_factory, seeded_qa):
    _login(client, seeded_qa.admin_email, seeded_qa.admin_password)
    create_response = post_form(
        client,
        "/recipes/new",
        data={
            "title": seeded_qa.user_like_title,
            "description": "ZZ CRUD Beschreibung",
            "instructions": "Öl erhitzen.\nÜber Nacht ziehen lassen.",
            "category_select": "Dessert",
            "category_new": "",
            "category": "",
            "title_image_url": "",
            "prep_time_minutes": "33",
            "difficulty": "easy",
            "ingredients_text": "Mehl|200 g\nÖl|1 EL",
        },
        referer_page="/recipes/new",
        follow_redirects=False,
    )
    assert create_response.status_code in {302, 303}

    with db_session_factory() as db:
        recipe = db.scalar(select(Recipe).where(Recipe.title == seeded_qa.user_like_title))
        assert recipe is not None
        recipe_id = int(recipe.id)

    detail = client.get(f"/recipes/{recipe_id}")
    assert detail.status_code == 200
    assert seeded_qa.user_like_title in detail.text

    update_title = "ZZ_TEST_CRUD_Ändern_Final"
    edit_response = post_form(
        client,
        f"/recipes/{recipe_id}/edit",
        data={
            "title": update_title,
            "description": "ZZ CRUD Update",
            "instructions": "Ändern Schritt 1\nÄndern Schritt 2",
            "category_select": "Abendessen",
            "category_new": "",
            "category": "",
            "title_image_url": "https://example.com/zz-crud.jpg",
            "prep_time_minutes": "36",
            "difficulty": "medium",
            "ingredients_text": "Kartoffel|300 g\nSalz|1 Prise",
        },
        referer_page=f"/recipes/{recipe_id}/edit",
        follow_redirects=False,
    )
    assert edit_response.status_code in {302, 303}

    with db_session_factory() as db:
        updated = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
        assert updated is not None
        assert updated.title == update_title
        assert updated.category == "Abendessen"
        assert updated.title_image_url == "https://example.com/zz-crud.jpg"

    remove_image_url = post_form(
        client,
        f"/recipes/{recipe_id}/edit",
        data={
            "title": update_title,
            "description": "ZZ CRUD Update 2",
            "instructions": "Ändern Schritt 3",
            "category_select": "Abendessen",
            "category_new": "",
            "category": "",
            "title_image_url": "",
            "prep_time_minutes": "36",
            "difficulty": "medium",
            "ingredients_text": "Kartoffel|300 g",
        },
        referer_page=f"/recipes/{recipe_id}/edit",
        follow_redirects=False,
    )
    assert remove_image_url.status_code in {302, 303}

    delete_response = post_form(
        client,
        f"/recipes/{recipe_id}/delete",
        data={},
        referer_page=f"/recipes/{recipe_id}",
        follow_redirects=False,
    )
    assert delete_response.status_code in {302, 303}

    deleted_detail = client.get(f"/recipes/{recipe_id}")
    assert deleted_detail.status_code == 404
    assert update_title not in client.get("/?title=ZZ_TEST_CRUD").text


def test_qa_i18n_and_encoding_smoke(client, seeded_qa):
    _login(client, seeded_qa.admin_email, seeded_qa.admin_password)
    pages = [
        "/?lang=de",
        "/?lang=en",
        "/login?lang=de",
        "/register?lang=de",
        "/admin?lang=de",
        "/admin/translations/run?lang=de",
    ]
    for url in pages:
        response = client.get(url, follow_redirects=True)
        assert response.status_code == 200
        content_type = (response.headers.get("content-type") or "").lower()
        assert "charset=utf-8" in content_type
        assert not any(marker in response.text for marker in MOJIBAKE_MARKERS)
        assert not any(marker in response.text for marker in LEAK_MARKERS)

    response_de = client.get("/?lang=de")
    assert "Rezepte entdecken" in response_de.text
    response_en = client.get("/?lang=en")
    assert "Discover Recipes" in response_en.text


def test_qa_admin_publish_permission_guard_for_user(client, db_session_factory, seeded_qa):
    user_email = unique_email("zz-perm")
    user_password = "UserPass123!"
    register_response = post_form(
        client,
        "/register",
        data={"email": user_email, "username": "zz.perm.user", "password": user_password},
        referer_page="/register",
        follow_redirects=False,
    )
    assert register_response.status_code in {302, 303}
    create_forbidden = post_form(
        client,
        "/recipes/new",
        data={
            "title": "ZZ_TEST_FORBIDDEN_USER_PUBLISH",
            "description": "User darf nicht publishen.",
            "instructions": "Schritt 1",
            "category_select": "Dessert",
            "category_new": "",
            "category": "",
            "title_image_url": "",
            "prep_time_minutes": "20",
            "difficulty": "easy",
            "ingredients_text": "Wasser|1 Glas",
        },
        referer_page="/recipes/new",
        follow_redirects=False,
    )
    assert create_forbidden.status_code == 403

    routes = {(method, path) for route in app.routes for method in getattr(route, "methods", set()) for path in [route.path]}
    assert ("POST", "/admin/users/{user_id}/role") in routes


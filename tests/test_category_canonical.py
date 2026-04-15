from app.models import CategoryMapping, Recipe, User
from app.security import hash_password
from app.services import (
    get_enabled_category_mappings,
    guess_canonical_category,
    normalize_raw_category,
    rebuild_recipe_canonical_categories,
)
from sqlalchemy import text


def test_category_normalization():
    assert normalize_raw_category("  Rezepte__Suppe   ") == "Suppe"
    assert normalize_raw_category("Schwierigkeit: Salat") == "Salat"
    assert normalize_raw_category("Kategorie: Dessert") == "Dessert"
    assert normalize_raw_category("", allow_empty=False) == "Unkategorisiert"


def test_mapping_priority(db_session_factory):
    with db_session_factory() as db:
        db.add(CategoryMapping(pattern="suppe", canonical_category="Suppe & Eintopf", priority=50, enabled=True))
        db.add(CategoryMapping(pattern="tomate", canonical_category="Salat", priority=10, enabled=True))
        db.commit()

        mappings = get_enabled_category_mappings(db)
        guessed = guess_canonical_category(
            raw_category="Tomatensuppe",
            title="Tomatensuppe",
            description="",
            mappings=mappings,
        )

        assert guessed == "Salat"


def test_ignore_mapping_is_skipped(db_session_factory):
    with db_session_factory() as db:
        db.add(CategoryMapping(pattern="rezepte", canonical_category="__IGNORE__", priority=1, enabled=True))
        db.add(CategoryMapping(pattern="suppe", canonical_category="Suppe & Eintopf", priority=50, enabled=True))
        db.commit()

        mappings = get_enabled_category_mappings(db)
        guessed = guess_canonical_category(
            raw_category="Rezepte Suppe",
            title="Kartoffelsuppe",
            description="",
            mappings=mappings,
        )

        assert guessed == "Suppe & Eintopf"


def test_guess_fallback():
    assert guess_canonical_category(raw_category="Dessert", title="Vanille Pudding", description="") == "Dessert"
    assert guess_canonical_category(raw_category="Irgendwas", title="Hausgericht", description="") == "Hauptgericht"
    assert guess_canonical_category(raw_category="", title="", description="") == "Unkategorisiert"


def test_categories_endpoint_returns_canonical(client, db_session_factory):
    with db_session_factory() as db:
        user = User(email="cat-admin@example.local", hashed_password=hash_password("StrongPass123!"), role="admin")
        db.add(user)
        db.flush()

        db.add(
            Recipe(
                title="Morgen Bowl",
                description="Frischer Start",
                instructions="Mischen",
                category="Fruehstueck Rezepte",
                prep_time_minutes=10,
                difficulty="easy",
                creator_id=user.id,
                source="test",
                is_published=True,
            )
        )
        db.add(
            Recipe(
                title="Kartoffelsuppe",
                description="Warmes Gericht",
                instructions="Kochen",
                category="Suppe",
                prep_time_minutes=30,
                difficulty="medium",
                creator_id=user.id,
                source="test",
                is_published=True,
            )
        )
        db.commit()

    response = client.get("/categories")
    assert response.status_code == 200
    categories = response.json().get("categories", [])
    assert "Fr\u00fchst\u00fcck" in categories
    assert "Suppe & Eintopf" in categories
    assert "Fruehstueck Rezepte" not in categories


def test_rebuild_updates_existing_recipes(db_session_factory):
    with db_session_factory() as db:
        admin = User(email="rebuild-admin@example.local", hashed_password=hash_password("StrongPass123!"), role="admin")
        db.add(admin)
        db.flush()
        db.add(CategoryMapping(pattern="fruehstueck", canonical_category="Frühstück", priority=20, enabled=True))
        recipe = Recipe(
            title="Muesli Bowl",
            description="Leichtes Fruehstueck",
            instructions="Mischen",
            category="Kategorie: Fruehstueck",
            prep_time_minutes=10,
            difficulty="easy",
            creator_id=admin.id,
            source="test",
            canonical_category=None,
            is_published=True,
        )
        db.add(recipe)
        db.commit()
        db.execute(
            text("UPDATE recipes SET category = :raw, canonical_category = NULL WHERE id = :recipe_id"),
            {"raw": "Kategorie: Fruehstueck", "recipe_id": recipe.id},
        )
        db.commit()

        updated, skipped = rebuild_recipe_canonical_categories(db)
        db.commit()
        db.refresh(recipe)

        assert updated == 1
        assert skipped == 0
        assert recipe.category == "Fruehstueck"
        assert recipe.canonical_category == "Frühstück"

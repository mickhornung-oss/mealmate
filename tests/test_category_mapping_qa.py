from app.category_canonical import (
    build_category_qa_rows,
    coerce_mapping_rules,
    rebuild_canonical_categories,
    suggest_canonical_category,
)
from app.models import CategoryMapping, Recipe, User
from app.security import hash_password
from sqlalchemy import text


def test_raw_first_prevents_fulltext_false_positive():
    rules = coerce_mapping_rules(
        [
            CategoryMapping(
                id=1,
                pattern="dessert",
                canonical_category="Dessert",
                priority=10,
                enabled=True,
                scope="fulltext",
            )
        ]
    )
    suggestion = suggest_canonical_category(
        raw_category="Suppe",
        title="Herzhafte Gemuesesuppe mit Dessert-Deko",
        description="",
        mapping_rules=rules,
    )
    assert suggestion.canonical_category == "Suppe & Eintopf"
    assert suggestion.reason == "heuristic:raw"


def test_ignore_patterns_do_not_assign():
    rules = coerce_mapping_rules(
        [
            CategoryMapping(
                id=1,
                pattern="rezepte",
                canonical_category="__IGNORE__",
                priority=10,
                enabled=True,
                scope="raw",
            ),
            CategoryMapping(
                id=2,
                pattern="suppe",
                canonical_category="Suppe & Eintopf",
                priority=20,
                enabled=True,
                scope="raw",
            ),
        ]
    )
    suggestion = suggest_canonical_category(
        raw_category="Rezepte Suppe",
        title="Kartoffelsuppe",
        description="",
        mapping_rules=rules,
    )
    assert suggestion.canonical_category == "Suppe & Eintopf"


def test_priority_order():
    rules = coerce_mapping_rules(
        [
            CategoryMapping(
                id=1,
                pattern="suppe",
                canonical_category="Suppe & Eintopf",
                priority=50,
                enabled=True,
                scope="raw",
            ),
            CategoryMapping(
                id=2,
                pattern="tomate",
                canonical_category="Salat",
                priority=10,
                enabled=True,
                scope="raw",
            ),
        ]
    )
    suggestion = suggest_canonical_category(
        raw_category="Tomatensuppe",
        title="Tomatensuppe",
        description="",
        mapping_rules=rules,
    )
    assert suggestion.canonical_category == "Salat"
    assert suggestion.reason.startswith("mapping:raw")


def test_laugen_not_dessert():
    suggestion = suggest_canonical_category(
        raw_category="",
        title="Laugenbrezel klassisch",
        description="Herzhaft und knusprig.",
        mapping_rules=[],
    )
    assert suggestion.canonical_category != "Dessert"
    assert suggestion.canonical_category == "Backen"


def test_rebuild_suspicious_updates_only_flagged(db_session_factory):
    with db_session_factory() as db:
        admin = User(email="qa-admin@example.local", hashed_password=hash_password("StrongPass123!"), role="admin")
        db.add(admin)
        db.flush()

        recipe_suspicious = Recipe(
            title="Lauchsuppe mit Kartoffeln",
            description="Herzhaftes Gericht",
            instructions="Kochen",
            category="Suppe",
            canonical_category="Dessert",
            prep_time_minutes=30,
            difficulty="medium",
            creator_id=admin.id,
            source="test",
            is_published=True,
        )
        recipe_ok = Recipe(
            title="Schokopudding",
            description="Suesse Nachspeise",
            instructions="Ruehren",
            category="Dessert",
            canonical_category="Dessert",
            prep_time_minutes=15,
            difficulty="easy",
            creator_id=admin.id,
            source="test",
            is_published=True,
        )
        db.add(recipe_suspicious)
        db.add(recipe_ok)
        db.commit()
        db.execute(
            text("UPDATE recipes SET canonical_category = :canonical WHERE id = :recipe_id"),
            {"canonical": "Dessert", "recipe_id": recipe_suspicious.id},
        )
        db.commit()
        db.refresh(recipe_suspicious)

        qa_rows = build_category_qa_rows(db, limit=200)
        assert any(row.recipe_id == recipe_suspicious.id for row in qa_rows)
        assert all(row.recipe_id != recipe_ok.id for row in qa_rows)

        report = rebuild_canonical_categories(db, mode="suspicious", batch_size=50)
        db.commit()
        db.refresh(recipe_suspicious)
        db.refresh(recipe_ok)

        assert report["mode"] == "suspicious"
        assert int(report["updated"]) == 1
        assert int(report["skipped"]) >= 1
        assert recipe_suspicious.canonical_category == "Suppe & Eintopf"
        assert recipe_ok.canonical_category == "Dessert"

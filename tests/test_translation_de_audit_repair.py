from __future__ import annotations

from sqlalchemy import select

from app.config import get_settings
from app.translation_models import RecipeTranslation
from app.translation_service import (
    audit_german_translations,
    repair_suspect_german_translations,
    set_translation_provider_for_testing,
)
from tests.helpers import create_admin_user, create_published_recipe, unique_email


class FakeTranslationProvider:
    def translate(self, text: str, targets: list[str], *, source_lang: str) -> dict[str, str]:
        _ = source_lang
        return {target: f"[{target}] {text}" for target in targets}


def _configure_settings(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "translateapi_enabled", True)
    monkeypatch.setattr(settings, "translate_target_langs", ["de", "en", "fr"])
    monkeypatch.setattr(settings, "translate_source_lang", "auto")
    monkeypatch.setattr(settings, "translate_auto_on_publish", False)
    monkeypatch.setattr(settings, "translate_max_recipes_per_run", 20)


def test_translation_audit_detects_english_in_de(db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("audit-admin"), "AdminPass123!")
        recipe_bad = create_published_recipe(db, admin.id, title="English DE Recipe", is_published=True)
        recipe_ok = create_published_recipe(db, admin.id, title="German DE Recipe", is_published=True)
        db.add(
            RecipeTranslation(
                recipe_id=recipe_bad.id,
                language="de",
                title="Heat oil and stir",
                description="Use medium heat.",
                instructions="Heat oil and stir onions for 10 minutes, then serve.",
                ingredients_text="oil\nonion",
                source_hash="hash-bad",
                stale=False,
            )
        )
        db.add(
            RecipeTranslation(
                recipe_id=recipe_ok.id,
                language="de",
                title="Zwiebeln anbraten",
                description="Kurz mit Oel arbeiten.",
                instructions="Zwiebeln im Topf anbraten und dann mit Salz ruehren.",
                ingredients_text="oel\nzwiebel",
                source_hash="hash-ok",
                stale=False,
            )
        )
        db.commit()
        report = audit_german_translations(db, limit=20, persist_flags=False)
        assert report.total_de_rows == 2
        assert report.suspect_count == 1
        assert len(report.items) == 1
        assert report.items[0].recipe_id == recipe_bad.id


def test_translation_repair_only_updates_suspect(db_session_factory, monkeypatch):
    _configure_settings(monkeypatch)
    set_translation_provider_for_testing(FakeTranslationProvider())
    try:
        with db_session_factory() as db:
            admin = create_admin_user(db, unique_email("repair-admin"), "AdminPass123!")
            recipe_bad = create_published_recipe(db, admin.id, title="Repair Bad Recipe", is_published=True)
            recipe_ok = create_published_recipe(db, admin.id, title="Repair Good Recipe", is_published=True)
            db.add(
                RecipeTranslation(
                    recipe_id=recipe_bad.id,
                    language="de",
                    title="Serve hot",
                    description="Heat quickly.",
                    instructions="Heat oil and stir meat for 15 minutes, then serve hot.",
                    ingredients_text="oil\nmeat",
                    source_hash="repair-hash-bad",
                    stale=False,
                )
            )
            db.add(
                RecipeTranslation(
                    recipe_id=recipe_ok.id,
                    language="de",
                    title="Kartoffeln kochen",
                    description="Mit Wasser kochen.",
                    instructions="Kartoffeln in Wasser geben und dann bei mittlerer Hitze kochen.",
                    ingredients_text="kartoffeln\nwasser",
                    source_hash="repair-hash-ok",
                    stale=False,
                )
            )
            db.commit()

            report = repair_suspect_german_translations(db, limit=20, dry_run=False)
            db.commit()
            assert report.candidate_count == 1
            assert report.updated_count == 1
            assert report.error_count == 0

            rows = db.scalars(
                select(RecipeTranslation)
                .where(RecipeTranslation.language == "de")
                .order_by(RecipeTranslation.recipe_id.asc())
            ).all()
            repaired = next(row for row in rows if row.recipe_id == recipe_bad.id)
            untouched = next(row for row in rows if row.recipe_id == recipe_ok.id)
            assert repaired.quality_flag == "ok"
            assert repaired.title.startswith("[de] ")
            assert untouched.title == "Kartoffeln kochen"
    finally:
        set_translation_provider_for_testing(None)

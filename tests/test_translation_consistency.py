from __future__ import annotations

import pytest
from sqlalchemy import select

from app.config import get_settings
from app.models import Recipe
from app.translation_models import RecipeTranslation
from app.translation_service import run_translation_batch, set_translation_provider_for_testing
from tests.helpers import create_admin_user, create_published_recipe, unique_email


class FakeTranslationProvider:
    def translate(self, text: str, targets: list[str], *, source_lang: str) -> dict[str, str]:
        _ = source_lang
        return {target: f"{target}:translated:{text}" for target in targets}


def _configure_translation_settings(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "translateapi_enabled", True)
    monkeypatch.setattr(settings, "translate_auto_on_publish", False)
    monkeypatch.setattr(settings, "translate_target_langs", ["en", "fr"])
    monkeypatch.setattr(settings, "translate_source_lang", "de")
    monkeypatch.setattr(settings, "translate_max_recipes_per_run", 20)


def test_translation_batch_mock_provider_writes_rows(db_session_factory, monkeypatch):
    _configure_translation_settings(monkeypatch)
    set_translation_provider_for_testing(FakeTranslationProvider())
    try:
        with db_session_factory() as db:
            admin = create_admin_user(db, unique_email("tr-admin"), "AdminPass123!")
            recipe = create_published_recipe(db, admin.id, title="Translation Consistency Recipe")
            recipe_id = recipe.id

        with db_session_factory() as db:
            report = run_translation_batch(db, mode="missing", limit=20)
            db.commit()
            assert report.processed_recipes >= 1
            assert report.created >= 2
            rows = db.scalars(
                select(RecipeTranslation)
                .where(RecipeTranslation.recipe_id == recipe_id)
                .order_by(RecipeTranslation.language.asc())
            ).all()
            assert [row.language for row in rows] == ["en", "fr"]
            assert all(row.title.startswith(f"{row.language}:translated:") for row in rows)
            assert all(bool(row.source_hash) for row in rows)
    finally:
        set_translation_provider_for_testing(None)


def test_recipe_detail_falls_back_to_source_text_without_translation_rows(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("detail-admin"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="Original Titel Nur Quelle")
        recipe_id = recipe.id

    response = client.get(f"/recipes/{recipe_id}?lang=en")
    assert response.status_code == 200
    assert "Original Titel Nur Quelle" in response.text


def test_recipe_detail_uses_translation_when_row_exists(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("detail-admin"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="Original Titel fuer UI")
        db.add(
            RecipeTranslation(
                recipe_id=recipe.id,
                language="de",
                title="Übersetzter DE Titel",
                description="Übersetzte DE Beschreibung",
                instructions="Übersetzte DE Anleitung",
                ingredients_text="Übersetzte DE Zutaten",
                source_hash="test-hash",
                stale=False,
            )
        )
        db.commit()
        db.refresh(recipe)
        recipe_id = int(recipe.id)
        _ = db.scalar(select(Recipe).where(Recipe.id == recipe_id))

    response = client.get(f"/recipes/{recipe_id}?lang=de")
    assert response.status_code == 200
    assert "Übersetzter DE Titel" in response.text

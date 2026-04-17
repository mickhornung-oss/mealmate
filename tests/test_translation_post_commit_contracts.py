from __future__ import annotations

from sqlalchemy import select

from app.config import get_settings
from app.translation_models import RecipeTranslation
from app.translation_service import (
    AUTO_TRANSLATION_RECIPE_IDS_KEY,
    _after_commit_auto_translate,
    set_translation_provider_for_testing,
)
from tests.helpers import create_admin_user, create_published_recipe, unique_email


class _FakeProvider:
    def translate(self, text: str, targets: list[str], *, source_lang: str) -> dict[str, str]:
        _ = source_lang
        return {target: f"{target}:{text}" for target in targets}


def _configure_auto_translate(monkeypatch, *, enabled: bool, auto_on_publish: bool):
    settings = get_settings()
    monkeypatch.setattr(settings, "translateapi_enabled", enabled)
    monkeypatch.setattr(settings, "translate_auto_on_publish", auto_on_publish)
    monkeypatch.setattr(settings, "translate_target_langs", ["en"])
    monkeypatch.setattr(settings, "translate_source_lang", "de")


def test_after_commit_auto_translate_rolls_back_on_write_phase_error(db_session_factory, monkeypatch):
    _configure_auto_translate(monkeypatch, enabled=True, auto_on_publish=True)
    set_translation_provider_for_testing(_FakeProvider())
    try:
        with db_session_factory() as db:
            admin = create_admin_user(db, unique_email("admin"), "AdminPass123!")
            recipe = create_published_recipe(db, admin.id, title="Post Commit Rollback", is_published=True)
            recipe_id = recipe.id

            def failing_translate(db_session, recipe_obj, languages, **kwargs):
                _ = languages
                _ = kwargs
                db_session.add(
                    RecipeTranslation(
                        recipe_id=recipe_obj.id,
                        language="en",
                        title="tmp",
                        description="tmp",
                        instructions="tmp",
                        ingredients_text="tmp",
                        source_hash="tmp-hash",
                        stale=False,
                        quality_flag="ok",
                    )
                )
                db_session.flush()
                raise RuntimeError("simulated write phase failure")

            monkeypatch.setattr("app.translation_service.translate_recipe_languages", failing_translate)
            db.info[AUTO_TRANSLATION_RECIPE_IDS_KEY] = {recipe_id}
            _after_commit_auto_translate(db)
            assert AUTO_TRANSLATION_RECIPE_IDS_KEY not in db.info

        with db_session_factory() as verify_db:
            row = verify_db.scalar(
                select(RecipeTranslation).where(
                    RecipeTranslation.recipe_id == recipe_id,
                    RecipeTranslation.language == "en",
                )
            )
            assert row is None
    finally:
        set_translation_provider_for_testing(None)


def test_after_commit_auto_translate_noop_when_auto_disabled(db_session_factory, monkeypatch):
    _configure_auto_translate(monkeypatch, enabled=True, auto_on_publish=False)
    set_translation_provider_for_testing(_FakeProvider())
    try:
        with db_session_factory() as db:
            admin = create_admin_user(db, unique_email("admin"), "AdminPass123!")
            recipe = create_published_recipe(db, admin.id, title="Post Commit Disabled", is_published=True)
            recipe_id = recipe.id

            def should_not_run(*args, **kwargs):
                raise AssertionError("write phase must not run when auto translate is disabled")

            monkeypatch.setattr("app.translation_service.translate_recipe_languages", should_not_run)
            db.info[AUTO_TRANSLATION_RECIPE_IDS_KEY] = {recipe_id}
            _after_commit_auto_translate(db)
            assert AUTO_TRANSLATION_RECIPE_IDS_KEY not in db.info
    finally:
        set_translation_provider_for_testing(None)


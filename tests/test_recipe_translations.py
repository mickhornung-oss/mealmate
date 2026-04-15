from sqlalchemy import select

from app.config import get_settings
from app.models import Recipe, RecipeSubmission
from app.translation_models import RecipeTranslation
from app.translation_service import set_translation_provider_for_testing
from tests.helpers import (
    create_admin_user,
    create_normal_user,
    create_pending_submission,
    create_published_recipe,
    post_form,
    set_auth_cookie,
    unique_email,
)


class FakeTranslationProvider:
    def translate(self, text: str, targets: list[str], *, source_lang: str) -> dict[str, str]:
        _ = source_lang
        return {target: f"{target}:{text}" for target in targets}


def _configure_translation_settings(monkeypatch, *, enabled: bool, auto_on_publish: bool, target_langs: list[str]) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "translateapi_enabled", enabled)
    monkeypatch.setattr(settings, "translate_auto_on_publish", auto_on_publish)
    monkeypatch.setattr(settings, "translate_target_langs", target_langs)
    monkeypatch.setattr(settings, "translate_source_lang", "auto")
    monkeypatch.setattr(settings, "translate_max_recipes_per_run", 20)


def test_auto_translation_trigger_on_approve(client, db_session_factory, monkeypatch):
    _configure_translation_settings(monkeypatch, enabled=True, auto_on_publish=True, target_langs=["de", "en", "fr"])
    set_translation_provider_for_testing(FakeTranslationProvider())
    try:
        with db_session_factory() as db:
            admin = create_admin_user(db, unique_email("admin"), "AdminPass123!")
            user = create_normal_user(db, unique_email("user"), "UserPass123!")
            submission = create_pending_submission(db, user.id, title="Auto Translate Submission")
            submission_id = submission.id
            admin_uid = admin.user_uid
            admin_role = admin.role

        set_auth_cookie(client, admin_uid, admin_role)
        response = post_form(
            client,
            f"/admin/submissions/{submission_id}/approve",
            {"admin_note": "Approved for translation."},
            referer_page=f"/admin/submissions/{submission_id}",
            follow_redirects=False,
        )
        assert response.status_code == 303

        with db_session_factory() as db:
            recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == f"submission:{submission_id}"))
            assert recipe is not None
            rows = db.scalars(
                select(RecipeTranslation)
                .where(RecipeTranslation.recipe_id == recipe.id)
                .order_by(RecipeTranslation.language.asc())
            ).all()
            assert [row.language for row in rows] == ["de", "en", "fr"]
            assert all(row.stale is False for row in rows)
            assert rows[0].title.startswith("de:")
    finally:
        set_translation_provider_for_testing(None)


def test_admin_run_translations_creates_rows(client, db_session_factory, monkeypatch):
    _configure_translation_settings(monkeypatch, enabled=True, auto_on_publish=False, target_langs=["de", "en", "fr"])
    set_translation_provider_for_testing(FakeTranslationProvider())
    try:
        with db_session_factory() as db:
            admin = create_admin_user(db, unique_email("admin"), "AdminPass123!")
            recipe = create_published_recipe(db, admin.id, title="Translate Batch Recipe", is_published=True)
            recipe_id = recipe.id
            admin_uid = admin.user_uid
            admin_role = admin.role

        set_auth_cookie(client, admin_uid, admin_role)
        response = post_form(
            client,
            "/admin/translations/run",
            {"mode": "missing", "limit": "20"},
            referer_page="/admin/translations",
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert "/admin/translations" in response.headers.get("location", "")

        with db_session_factory() as db:
            rows = db.scalars(
                select(RecipeTranslation)
                .where(RecipeTranslation.recipe_id == recipe_id)
                .order_by(RecipeTranslation.language.asc())
            ).all()
            assert [row.language for row in rows] == ["de", "en", "fr"]
            assert all(row.stale is False for row in rows)
    finally:
        set_translation_provider_for_testing(None)

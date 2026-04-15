from sqlalchemy import select

from app.config import get_settings
from app.translation_models import RecipeTranslation
from app.translation_service import set_translation_provider_for_testing
from tests.helpers import create_admin_user, create_published_recipe, post_form, set_auth_cookie, unique_email


class FakeQueueTranslationProvider:
    def translate(self, text: str, targets: list[str], *, source_lang: str) -> dict[str, str]:
        _ = source_lang
        return {target: f"{target}:{text}" for target in targets}


def _configure(monkeypatch) -> None:
    settings = get_settings()
    monkeypatch.setattr(settings, "translateapi_enabled", True)
    monkeypatch.setattr(settings, "translate_auto_on_publish", False)
    monkeypatch.setattr(settings, "translate_target_langs", ["en", "fr"])
    monkeypatch.setattr(settings, "translate_source_lang", "de")


def test_translation_queue_is_visible_for_new_uploaded_recipes(client, db_session_factory, monkeypatch):
    _configure(monkeypatch)
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("queue-admin"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="Queue Recipe One", is_published=True)
        admin_uid = admin.user_uid
        admin_role = admin.role
    set_auth_cookie(client, admin_uid, admin_role)
    response = client.get("/admin/translations")
    assert response.status_code == 200
    assert (
        "Neue Rezepte: Übersetzungs-Warteschlange" in response.text
        or "Neue Rezepte: Uebersetzungs-Warteschlange" in response.text
    )
    assert "Queue Recipe One" in response.text
    assert f"/admin/translations/recipes/{recipe.id}/run" in response.text


def test_translation_queue_single_recipe_run_creates_translations(client, db_session_factory, monkeypatch):
    _configure(monkeypatch)
    set_translation_provider_for_testing(FakeQueueTranslationProvider())
    try:
        with db_session_factory() as db:
            admin = create_admin_user(db, unique_email("queue-admin"), "AdminPass123!")
            recipe = create_published_recipe(db, admin.id, title="Queue Recipe Two", is_published=True)
            recipe_id = recipe.id
            admin_uid = admin.user_uid
            admin_role = admin.role
        set_auth_cookie(client, admin_uid, admin_role)
        response = post_form(
            client,
            f"/admin/translations/recipes/{recipe_id}/run",
            {"mode": "missing"},
            referer_page="/admin/translations",
            follow_redirects=False,
        )
        assert response.status_code == 303
        with db_session_factory() as db:
            rows = db.scalars(
                select(RecipeTranslation)
                .where(RecipeTranslation.recipe_id == recipe_id)
                .order_by(RecipeTranslation.language.asc())
            ).all()
            assert [row.language for row in rows] == ["en", "fr"]
    finally:
        set_translation_provider_for_testing(None)

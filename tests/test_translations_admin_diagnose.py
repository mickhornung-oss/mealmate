from __future__ import annotations

from app.config import get_settings
from app.translation_service import set_translation_provider_for_testing
from tests.helpers import create_admin_user, post_form, set_auth_cookie, unique_email


class FakeProvider:
    def translate(self, text: str, targets: list[str], *, source_lang: str) -> dict[str, str]:
        _ = source_lang
        return {lang: f"fake:{lang}:{text}" for lang in targets}


def test_admin_translation_test_route_shows_guidance_when_disabled(client, db_session_factory, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "translateapi_enabled", False)
    monkeypatch.setattr(settings, "translateapi_api_key", "")
    monkeypatch.setattr(settings, "translate_target_langs", ["en", "fr"])
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("tr-diag-admin"), "AdminPass123!")
    set_auth_cookie(client, admin.user_uid, admin.role)
    response = post_form(client, "/admin/translations/test", referer_page="/admin/translations")
    assert response.status_code == 200
    assert "Setze TRANSLATEAPI_ENABLED=1 und TRANSLATEAPI_API_KEY in .env." in response.text


def test_admin_translation_test_route_renders_mock_result_when_enabled(client, db_session_factory, monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "translateapi_enabled", True)
    monkeypatch.setattr(settings, "translateapi_api_key", "dummy-key")
    monkeypatch.setattr(settings, "translate_target_langs", ["en", "fr"])
    monkeypatch.setattr(settings, "translate_source_lang", "de")
    monkeypatch.setattr(settings, "translation_provider", "translateapi")
    set_translation_provider_for_testing(FakeProvider())
    try:
        with db_session_factory() as db:
            admin = create_admin_user(db, unique_email("tr-diag-admin"), "AdminPass123!")
        set_auth_cookie(client, admin.user_uid, admin.role)
        response = post_form(client, "/admin/translations/test", referer_page="/admin/translations")
        assert response.status_code == 200
        assert "Testübersetzung erfolgreich." in response.text
        assert "fake:en:Hello from Kitchen Hell and Heaven" in response.text
        assert "fake:fr:Hello from Kitchen Hell and Heaven" in response.text
    finally:
        set_translation_provider_for_testing(None)

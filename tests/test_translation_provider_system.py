from types import SimpleNamespace

from app.config import get_settings
from app.translation_provider import GoogleTranslatorsTranslationProvider, resolve_translation_provider
from app.translation_service import get_translation_provider, set_translation_provider_for_testing, translate_payload


class MockProvider:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[str, ...], str]] = []

    def translate(self, text: str, targets: list[str], *, source_lang: str) -> dict[str, str]:
        self.calls.append((text, tuple(targets), source_lang))
        return {target: f"mock-{target}:{text}" for target in targets}


def test_translation_service_can_use_mock_provider_override():
    provider = MockProvider()
    set_translation_provider_for_testing(provider)
    try:
        payload = {"title": "Hallo"}
        translated = translate_payload(get_translation_provider(), payload, source_lang="de", target_lang="en")
        assert translated["title"] == "mock-en:Hallo"
        assert provider.calls == [("Hallo", ("en",), "de")]
    finally:
        set_translation_provider_for_testing(None)


def test_provider_resolution_google_translators(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "translation_provider", "google_translators")

    fake_module = SimpleNamespace(
        translate_text=lambda text, translator, from_language, to_language: f"{to_language}:{text}"
    )
    monkeypatch.setattr("app.translation_provider.importlib.import_module", lambda _name: fake_module)

    provider = resolve_translation_provider(settings)
    assert isinstance(provider, GoogleTranslatorsTranslationProvider)
    result = provider.translate("Kartoffelsuppe", ["en", "fr"], source_lang="de")
    assert result == {"en": "en:Kartoffelsuppe", "fr": "fr:Kartoffelsuppe"}


def test_provider_resolution_translateapi(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "translation_provider", "translateapi")
    monkeypatch.setattr(settings, "translateapi_api_key", "dev-test-key")
    provider = resolve_translation_provider(settings)
    assert provider.__class__.__name__ == "TranslateApiTranslationProvider"

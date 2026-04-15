import json
import logging
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config import get_settings

DEFAULT_LANG = "de"
SUPPORTED_LANGS = ("de", "en", "fr")
LANG_LABELS = {
    "de": "Deutsch",
    "en": "English",
    "fr": "Français",
}

_current_lang: ContextVar[str] = ContextVar("mealmate_current_lang", default=DEFAULT_LANG)
settings = get_settings()
logger = logging.getLogger("mealmate.i18n")


def normalize_lang(value: str | None) -> str | None:
    if not value:
        return None
    token = str(value).strip().lower().replace("_", "-")
    if not token:
        return None
    primary = token.split("-", 1)[0]
    if primary in SUPPORTED_LANGS:
        return primary
    return None


def set_current_lang(lang: str) -> None:
    _current_lang.set(normalize_lang(lang) or DEFAULT_LANG)


def get_current_lang() -> str:
    return normalize_lang(_current_lang.get()) or DEFAULT_LANG


def available_langs() -> list[tuple[str, str]]:
    return [(code, LANG_LABELS.get(code, code)) for code in SUPPORTED_LANGS]


def parse_accept_language(header_value: str | None) -> list[str]:
    if not header_value:
        return []
    weighted: list[tuple[str, float]] = []
    for part in str(header_value).split(","):
        item = part.strip()
        if not item:
            continue
        lang_part = item
        q_value = 1.0
        if ";" in item:
            lang_part, *params = item.split(";")
            for param in params:
                key, _, value = param.strip().partition("=")
                if key == "q":
                    try:
                        q_value = float(value)
                    except ValueError:
                        q_value = 0.0
        normalized = normalize_lang(lang_part)
        if normalized:
            weighted.append((normalized, q_value))
    weighted.sort(key=lambda pair: pair[1], reverse=True)
    return [lang for lang, _ in weighted]


def resolve_lang(
    query_lang: str | None = None,
    cookie_lang: str | None = None,
    accept_language: str | None = None,
) -> tuple[str, bool]:
    query = normalize_lang(query_lang)
    if query:
        return query, True
    cookie = normalize_lang(cookie_lang)
    if cookie:
        return cookie, False
    for candidate in parse_accept_language(accept_language):
        normalized = normalize_lang(candidate)
        if normalized:
            return normalized, False
    return DEFAULT_LANG, False


@lru_cache(maxsize=1)
def load_locales() -> dict[str, dict[str, str]]:
    base_dir = Path(__file__).resolve().parent / "locales"
    locales: dict[str, dict[str, str]] = {}
    for lang in SUPPORTED_LANGS:
        locale_file = base_dir / f"{lang}.json"
        if not locale_file.exists():
            locales[lang] = {}
            continue
        with locale_file.open("r", encoding="utf-8") as handle:
            loaded = json.load(handle)
        locales[lang] = {str(key): str(value) for key, value in loaded.items()}
    return locales


def get_translation_text(key: str, lang: str | None = None) -> str:
    locales = load_locales()
    resolved_lang = normalize_lang(lang) or get_current_lang()
    primary = locales.get(resolved_lang, {})
    if key in primary:
        return str(primary.get(key, ""))
    german = locales.get(DEFAULT_LANG, {})
    if key in german:
        return str(german.get(key, ""))
    logger.debug("missing_translation key=%s lang=%s", key, resolved_lang)
    if settings.i18n_strict:
        return "⛔ missing translation"
    return ""


def translate(key: str, lang: str | None = None, **kwargs: Any) -> str:
    template = get_translation_text(key, lang=lang)
    if not kwargs:
        return template
    try:
        return template.format(**kwargs)
    except Exception:
        return template

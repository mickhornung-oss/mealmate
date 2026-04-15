# Deliverable: i18n DE/EN/FR

## Betroffene Dateien
- `app/i18n/service.py`
- `app/i18n/middleware.py`
- `app/i18n/__init__.py`
- `app/dependencies.py`
- `app/views.py`
- `app/main.py`
- `app/templates/base.html`
- `app/templates/home.html`
- `app/static/style.css`
- `app/i18n/locales/de.json`
- `app/i18n/locales/en.json`
- `app/i18n/locales/fr.json`
- `tests/test_i18n.py`
- `README_I18N.md`

## app/i18n/service.py
```python
import json
from contextvars import ContextVar
from functools import lru_cache
from pathlib import Path
from typing import Any

DEFAULT_LANG = "de"
SUPPORTED_LANGS = ("de", "en", "fr")
LANG_LABELS = {
    "de": "Deutsch",
    "en": "English",
    "fr": "Français",
}

_current_lang: ContextVar[str] = ContextVar("mealmate_current_lang", default=DEFAULT_LANG)


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
        return primary[key]
    german = locales.get(DEFAULT_LANG, {})
    if key in german:
        return german[key]
    return key


def translate(key: str, lang: str | None = None, **kwargs: Any) -> str:
    template = get_translation_text(key, lang=lang)
    if not kwargs:
        return template
    try:
        return template.format(**kwargs)
    except Exception:
        return template
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'import json'.
2. Diese Zeile definiert den Abschnitt 'from contextvars import ContextVar'.
3. Diese Zeile definiert den Abschnitt 'from functools import lru_cache'.
4. Diese Zeile definiert den Abschnitt 'from pathlib import Path'.
5. Diese Zeile definiert den Abschnitt 'from typing import Any'.
6. Diese Zeile ist leer und strukturiert den Inhalt.
7. Diese Zeile definiert den Abschnitt 'DEFAULT_LANG = "de"'.
8. Diese Zeile definiert den Abschnitt 'SUPPORTED_LANGS = ("de", "en", "fr")'.
9. Diese Zeile definiert den Abschnitt 'LANG_LABELS = {'.
10. Diese Zeile definiert den Abschnitt '"de": "Deutsch",'.
11. Diese Zeile definiert den Abschnitt '"en": "English",'.
12. Diese Zeile definiert den Abschnitt '"fr": "Français",'.
13. Diese Zeile definiert den Abschnitt '}'.
14. Diese Zeile ist leer und strukturiert den Inhalt.
15. Diese Zeile definiert den Abschnitt '_current_lang: ContextVar[str] = ContextVar("mealmate_current_lang", default=DEFAULT_LANG)'.
16. Diese Zeile ist leer und strukturiert den Inhalt.
17. Diese Zeile ist leer und strukturiert den Inhalt.
18. Diese Zeile definiert den Abschnitt 'def normalize_lang(value: str | None) -> str | None:'.
19. Diese Zeile definiert den Abschnitt 'if not value:'.
20. Diese Zeile definiert den Abschnitt 'return None'.
21. Diese Zeile definiert den Abschnitt 'token = str(value).strip().lower().replace("_", "-")'.
22. Diese Zeile definiert den Abschnitt 'if not token:'.
23. Diese Zeile definiert den Abschnitt 'return None'.
24. Diese Zeile definiert den Abschnitt 'primary = token.split("-", 1)[0]'.
25. Diese Zeile definiert den Abschnitt 'if primary in SUPPORTED_LANGS:'.
26. Diese Zeile definiert den Abschnitt 'return primary'.
27. Diese Zeile definiert den Abschnitt 'return None'.
28. Diese Zeile ist leer und strukturiert den Inhalt.
29. Diese Zeile ist leer und strukturiert den Inhalt.
30. Diese Zeile definiert den Abschnitt 'def set_current_lang(lang: str) -> None:'.
31. Diese Zeile definiert den Abschnitt '_current_lang.set(normalize_lang(lang) or DEFAULT_LANG)'.
32. Diese Zeile ist leer und strukturiert den Inhalt.
33. Diese Zeile ist leer und strukturiert den Inhalt.
34. Diese Zeile definiert den Abschnitt 'def get_current_lang() -> str:'.
35. Diese Zeile definiert den Abschnitt 'return normalize_lang(_current_lang.get()) or DEFAULT_LANG'.
36. Diese Zeile ist leer und strukturiert den Inhalt.
37. Diese Zeile ist leer und strukturiert den Inhalt.
38. Diese Zeile definiert den Abschnitt 'def available_langs() -> list[tuple[str, str]]:'.
39. Diese Zeile definiert den Abschnitt 'return [(code, LANG_LABELS.get(code, code)) for code in SUPPORTED_LANGS]'.
40. Diese Zeile ist leer und strukturiert den Inhalt.
41. Diese Zeile ist leer und strukturiert den Inhalt.
42. Diese Zeile definiert den Abschnitt 'def parse_accept_language(header_value: str | None) -> list[str]:'.
43. Diese Zeile definiert den Abschnitt 'if not header_value:'.
44. Diese Zeile definiert den Abschnitt 'return []'.
45. Diese Zeile definiert den Abschnitt 'weighted: list[tuple[str, float]] = []'.
46. Diese Zeile definiert den Abschnitt 'for part in str(header_value).split(","):'.
47. Diese Zeile definiert den Abschnitt 'item = part.strip()'.
48. Diese Zeile definiert den Abschnitt 'if not item:'.
49. Diese Zeile definiert den Abschnitt 'continue'.
50. Diese Zeile definiert den Abschnitt 'lang_part = item'.
51. Diese Zeile definiert den Abschnitt 'q_value = 1.0'.
52. Diese Zeile definiert den Abschnitt 'if ";" in item:'.
53. Diese Zeile definiert den Abschnitt 'lang_part, *params = item.split(";")'.
54. Diese Zeile definiert den Abschnitt 'for param in params:'.
55. Diese Zeile definiert den Abschnitt 'key, _, value = param.strip().partition("=")'.
56. Diese Zeile definiert den Abschnitt 'if key == "q":'.
57. Diese Zeile definiert den Abschnitt 'try:'.
58. Diese Zeile definiert den Abschnitt 'q_value = float(value)'.
59. Diese Zeile definiert den Abschnitt 'except ValueError:'.
60. Diese Zeile definiert den Abschnitt 'q_value = 0.0'.
61. Diese Zeile definiert den Abschnitt 'normalized = normalize_lang(lang_part)'.
62. Diese Zeile definiert den Abschnitt 'if normalized:'.
63. Diese Zeile definiert den Abschnitt 'weighted.append((normalized, q_value))'.
64. Diese Zeile definiert den Abschnitt 'weighted.sort(key=lambda pair: pair[1], reverse=True)'.
65. Diese Zeile definiert den Abschnitt 'return [lang for lang, _ in weighted]'.
66. Diese Zeile ist leer und strukturiert den Inhalt.
67. Diese Zeile ist leer und strukturiert den Inhalt.
68. Diese Zeile definiert den Abschnitt 'def resolve_lang('.
69. Diese Zeile definiert den Abschnitt 'query_lang: str | None = None,'.
70. Diese Zeile definiert den Abschnitt 'cookie_lang: str | None = None,'.
71. Diese Zeile definiert den Abschnitt 'accept_language: str | None = None,'.
72. Diese Zeile definiert den Abschnitt ') -> tuple[str, bool]:'.
73. Diese Zeile definiert den Abschnitt 'query = normalize_lang(query_lang)'.
74. Diese Zeile definiert den Abschnitt 'if query:'.
75. Diese Zeile definiert den Abschnitt 'return query, True'.
76. Diese Zeile definiert den Abschnitt 'cookie = normalize_lang(cookie_lang)'.
77. Diese Zeile definiert den Abschnitt 'if cookie:'.
78. Diese Zeile definiert den Abschnitt 'return cookie, False'.
79. Diese Zeile definiert den Abschnitt 'for candidate in parse_accept_language(accept_language):'.
80. Diese Zeile definiert den Abschnitt 'normalized = normalize_lang(candidate)'.
81. Diese Zeile definiert den Abschnitt 'if normalized:'.
82. Diese Zeile definiert den Abschnitt 'return normalized, False'.
83. Diese Zeile definiert den Abschnitt 'return DEFAULT_LANG, False'.
84. Diese Zeile ist leer und strukturiert den Inhalt.
85. Diese Zeile ist leer und strukturiert den Inhalt.
86. Diese Zeile definiert den Abschnitt '@lru_cache(maxsize=1)'.
87. Diese Zeile definiert den Abschnitt 'def load_locales() -> dict[str, dict[str, str]]:'.
88. Diese Zeile definiert den Abschnitt 'base_dir = Path(__file__).resolve().parent / "locales"'.
89. Diese Zeile definiert den Abschnitt 'locales: dict[str, dict[str, str]] = {}'.
90. Diese Zeile definiert den Abschnitt 'for lang in SUPPORTED_LANGS:'.
91. Diese Zeile definiert den Abschnitt 'locale_file = base_dir / f"{lang}.json"'.
92. Diese Zeile definiert den Abschnitt 'if not locale_file.exists():'.
93. Diese Zeile definiert den Abschnitt 'locales[lang] = {}'.
94. Diese Zeile definiert den Abschnitt 'continue'.
95. Diese Zeile definiert den Abschnitt 'with locale_file.open("r", encoding="utf-8") as handle:'.
96. Diese Zeile definiert den Abschnitt 'loaded = json.load(handle)'.
97. Diese Zeile definiert den Abschnitt 'locales[lang] = {str(key): str(value) for key, value in loaded.items()}'.
98. Diese Zeile definiert den Abschnitt 'return locales'.
99. Diese Zeile ist leer und strukturiert den Inhalt.
100. Diese Zeile ist leer und strukturiert den Inhalt.
101. Diese Zeile definiert den Abschnitt 'def get_translation_text(key: str, lang: str | None = None) -> str:'.
102. Diese Zeile definiert den Abschnitt 'locales = load_locales()'.
103. Diese Zeile definiert den Abschnitt 'resolved_lang = normalize_lang(lang) or get_current_lang()'.
104. Diese Zeile definiert den Abschnitt 'primary = locales.get(resolved_lang, {})'.
105. Diese Zeile definiert den Abschnitt 'if key in primary:'.
106. Diese Zeile definiert den Abschnitt 'return primary[key]'.
107. Diese Zeile definiert den Abschnitt 'german = locales.get(DEFAULT_LANG, {})'.
108. Diese Zeile definiert den Abschnitt 'if key in german:'.
109. Diese Zeile definiert den Abschnitt 'return german[key]'.
110. Diese Zeile definiert den Abschnitt 'return key'.
111. Diese Zeile ist leer und strukturiert den Inhalt.
112. Diese Zeile ist leer und strukturiert den Inhalt.
113. Diese Zeile definiert den Abschnitt 'def translate(key: str, lang: str | None = None, **kwargs: Any) -> str:'.
114. Diese Zeile definiert den Abschnitt 'template = get_translation_text(key, lang=lang)'.
115. Diese Zeile definiert den Abschnitt 'if not kwargs:'.
116. Diese Zeile definiert den Abschnitt 'return template'.
117. Diese Zeile definiert den Abschnitt 'try:'.
118. Diese Zeile definiert den Abschnitt 'return template.format(**kwargs)'.
119. Diese Zeile definiert den Abschnitt 'except Exception:'.
120. Diese Zeile definiert den Abschnitt 'return template'.

## app/i18n/middleware.py
```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.i18n.service import get_current_lang, resolve_lang, set_current_lang

settings = get_settings()


class LanguageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        resolved_lang, query_override = resolve_lang(
            query_lang=request.query_params.get("lang"),
            cookie_lang=request.cookies.get("lang"),
            accept_language=request.headers.get("accept-language"),
        )
        set_current_lang(resolved_lang)
        request.state.lang = get_current_lang()
        response = await call_next(request)
        if query_override:
            response.set_cookie(
                key="lang",
                value=request.state.lang,
                max_age=60 * 60 * 24 * 365,
                path="/",
                httponly=False,
                samesite="lax",
                secure=settings.resolved_cookie_secure,
            )
        return response
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'from fastapi import Request'.
2. Diese Zeile definiert den Abschnitt 'from starlette.middleware.base import BaseHTTPMiddleware'.
3. Diese Zeile ist leer und strukturiert den Inhalt.
4. Diese Zeile definiert den Abschnitt 'from app.config import get_settings'.
5. Diese Zeile definiert den Abschnitt 'from app.i18n.service import get_current_lang, resolve_lang, set_current_lang'.
6. Diese Zeile ist leer und strukturiert den Inhalt.
7. Diese Zeile definiert den Abschnitt 'settings = get_settings()'.
8. Diese Zeile ist leer und strukturiert den Inhalt.
9. Diese Zeile ist leer und strukturiert den Inhalt.
10. Diese Zeile definiert den Abschnitt 'class LanguageMiddleware(BaseHTTPMiddleware):'.
11. Diese Zeile definiert den Abschnitt 'async def dispatch(self, request: Request, call_next):'.
12. Diese Zeile definiert den Abschnitt 'resolved_lang, query_override = resolve_lang('.
13. Diese Zeile definiert den Abschnitt 'query_lang=request.query_params.get("lang"),'.
14. Diese Zeile definiert den Abschnitt 'cookie_lang=request.cookies.get("lang"),'.
15. Diese Zeile definiert den Abschnitt 'accept_language=request.headers.get("accept-language"),'.
16. Diese Zeile definiert den Abschnitt ')'.
17. Diese Zeile definiert den Abschnitt 'set_current_lang(resolved_lang)'.
18. Diese Zeile definiert den Abschnitt 'request.state.lang = get_current_lang()'.
19. Diese Zeile definiert den Abschnitt 'response = await call_next(request)'.
20. Diese Zeile definiert den Abschnitt 'if query_override:'.
21. Diese Zeile definiert den Abschnitt 'response.set_cookie('.
22. Diese Zeile definiert den Abschnitt 'key="lang",'.
23. Diese Zeile definiert den Abschnitt 'value=request.state.lang,'.
24. Diese Zeile definiert den Abschnitt 'max_age=60 * 60 * 24 * 365,'.
25. Diese Zeile definiert den Abschnitt 'path="/",'.
26. Diese Zeile definiert den Abschnitt 'httponly=False,'.
27. Diese Zeile definiert den Abschnitt 'samesite="lax",'.
28. Diese Zeile definiert den Abschnitt 'secure=settings.resolved_cookie_secure,'.
29. Diese Zeile definiert den Abschnitt ')'.
30. Diese Zeile definiert den Abschnitt 'return response'.

## app/i18n/__init__.py
```python
import re
from datetime import datetime
from typing import Any

from app.i18n.service import (
    DEFAULT_LANG,
    SUPPORTED_LANGS,
    available_langs,
    get_current_lang,
    normalize_lang,
    set_current_lang,
    translate,
)

DIFFICULTY_MAP = {
    "easy": "difficulty.easy",
    "medium": "difficulty.medium",
    "hard": "difficulty.hard",
}

ROLE_MAP = {
    "user": "role.user",
    "admin": "role.admin",
}

SUBMISSION_STATUS_MAP = {
    "pending": "submission.status_pending",
    "approved": "submission.status_approved",
    "rejected": "submission.status_rejected",
}

ERROR_MAP = {
    "Authentication required.": "error.auth_required",
    "Admin role required.": "error.admin_required",
    "Invalid credentials.": "error.invalid_credentials",
    "Email already registered.": "error.email_registered",
    "Role must be user or admin.": "error.role_invalid",
    "User not found.": "error.user_not_found",
    "Recipe not found.": "error.recipe_not_found",
    "Review not found.": "error.review_not_found",
    "Image not found.": "error.image_not_found",
    "Not enough permissions for this recipe.": "error.recipe_permission",
    "Not enough permissions for this review.": "error.review_permission",
    "Rating must be between 1 and 5.": "error.rating_range",
    "Title and instructions are required.": "error.title_instructions_required",
    "title_image_url must start with http:// or https://": "error.image_url_scheme",
    "No image URL available.": "error.no_image_url",
    "KochWiki seed is already marked as done.": "error.seed_already_done",
    "Seed can only run on an empty recipes table.": "error.seed_not_empty",
    "Seed finished with errors, marker was not set.": "error.seed_finished_errors",
    "KochWiki seed finished successfully and was marked as done.": "error.seed_success",
    "Please upload a CSV file.": "error.csv_upload_required",
    "Only CSV uploads are allowed.": "error.csv_only",
    "CSV upload too large.": "error.csv_too_large",
    "Uploaded CSV file is empty.": "error.csv_empty",
    "Submission has already been published.": "error.submission_already_published",
    "Import finished in insert-only mode.": "error.import_finished_insert",
    "Import finished in update-existing mode.": "error.import_finished_update",
    "CSRF validation failed.": "error.csrf_failed",
    "Internal server error.": "error.internal",
}


def _resolve_lang(lang: str | None = None, request: Any | None = None) -> str:
    if lang:
        return normalize_lang(lang) or DEFAULT_LANG
    if request is not None:
        request_lang = normalize_lang(getattr(getattr(request, "state", None), "lang", None))
        if request_lang:
            return request_lang
    return get_current_lang()


def t(key: str, lang: str | None = None, request: Any | None = None, **kwargs: Any) -> str:
    return translate(key, lang=_resolve_lang(lang=lang, request=request), **kwargs)


def difficulty_label(value: str | None, lang: str | None = None, request: Any | None = None) -> str:
    if not value:
        return "-"
    mapped = DIFFICULTY_MAP.get(value.strip().lower())
    return t(mapped, lang=lang, request=request) if mapped else value


def role_label(value: str | None, lang: str | None = None, request: Any | None = None) -> str:
    if not value:
        return "-"
    mapped = ROLE_MAP.get(value.strip().lower())
    return t(mapped, lang=lang, request=request) if mapped else value


def submission_status_label(value: str | None, lang: str | None = None, request: Any | None = None) -> str:
    if not value:
        return "-"
    mapped = SUBMISSION_STATUS_MAP.get(value.strip().lower())
    return t(mapped, lang=lang, request=request) if mapped else value


def datetime_de(value: datetime | None, lang: str | None = None, request: Any | None = None) -> str:
    if value is None:
        return "-"
    resolved_lang = _resolve_lang(lang=lang, request=request)
    if resolved_lang == "en":
        return value.strftime("%Y-%m-%d %H:%M")
    if resolved_lang == "fr":
        return value.strftime("%d/%m/%Y %H:%M")
    return value.strftime("%d.%m.%Y %H:%M")


def translate_error_message(message: Any, lang: str | None = None, request: Any | None = None) -> Any:
    if not isinstance(message, str):
        return message
    if message in ERROR_MAP:
        return t(ERROR_MAP[message], lang=lang, request=request)
    int_match = re.match(r"^(.+?) must be an integer\.$", message)
    if int_match:
        return t("error.field_int", lang=lang, request=request, field=int_match.group(1))
    positive_match = re.match(r"^(.+?) must be greater than zero\.$", message)
    if positive_match:
        return t("error.field_positive", lang=lang, request=request, field=positive_match.group(1))
    csv_missing_match = re.match(r"^CSV file not found:\s*(.+)$", message)
    if csv_missing_match:
        return f"{t('error.csv_not_found_prefix', lang=lang, request=request)}: {csv_missing_match.group(1)}"
    image_resolve_match = re.match(r"^Could not resolve image URL:\s*(.+)$", message)
    if image_resolve_match:
        return f"{t('error.image_resolve_prefix', lang=lang, request=request)}: {image_resolve_match.group(1)}"
    return message


__all__ = [
    "SUPPORTED_LANGS",
    "available_langs",
    "set_current_lang",
    "get_current_lang",
    "t",
    "difficulty_label",
    "role_label",
    "submission_status_label",
    "datetime_de",
    "translate_error_message",
]
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'import re'.
2. Diese Zeile definiert den Abschnitt 'from datetime import datetime'.
3. Diese Zeile definiert den Abschnitt 'from typing import Any'.
4. Diese Zeile ist leer und strukturiert den Inhalt.
5. Diese Zeile definiert den Abschnitt 'from app.i18n.service import ('.
6. Diese Zeile definiert den Abschnitt 'DEFAULT_LANG,'.
7. Diese Zeile definiert den Abschnitt 'SUPPORTED_LANGS,'.
8. Diese Zeile definiert den Abschnitt 'available_langs,'.
9. Diese Zeile definiert den Abschnitt 'get_current_lang,'.
10. Diese Zeile definiert den Abschnitt 'normalize_lang,'.
11. Diese Zeile definiert den Abschnitt 'set_current_lang,'.
12. Diese Zeile definiert den Abschnitt 'translate,'.
13. Diese Zeile definiert den Abschnitt ')'.
14. Diese Zeile ist leer und strukturiert den Inhalt.
15. Diese Zeile definiert den Abschnitt 'DIFFICULTY_MAP = {'.
16. Diese Zeile definiert den Abschnitt '"easy": "difficulty.easy",'.
17. Diese Zeile definiert den Abschnitt '"medium": "difficulty.medium",'.
18. Diese Zeile definiert den Abschnitt '"hard": "difficulty.hard",'.
19. Diese Zeile definiert den Abschnitt '}'.
20. Diese Zeile ist leer und strukturiert den Inhalt.
21. Diese Zeile definiert den Abschnitt 'ROLE_MAP = {'.
22. Diese Zeile definiert den Abschnitt '"user": "role.user",'.
23. Diese Zeile definiert den Abschnitt '"admin": "role.admin",'.
24. Diese Zeile definiert den Abschnitt '}'.
25. Diese Zeile ist leer und strukturiert den Inhalt.
26. Diese Zeile definiert den Abschnitt 'SUBMISSION_STATUS_MAP = {'.
27. Diese Zeile definiert den Abschnitt '"pending": "submission.status_pending",'.
28. Diese Zeile definiert den Abschnitt '"approved": "submission.status_approved",'.
29. Diese Zeile definiert den Abschnitt '"rejected": "submission.status_rejected",'.
30. Diese Zeile definiert den Abschnitt '}'.
31. Diese Zeile ist leer und strukturiert den Inhalt.
32. Diese Zeile definiert den Abschnitt 'ERROR_MAP = {'.
33. Diese Zeile definiert den Abschnitt '"Authentication required.": "error.auth_required",'.
34. Diese Zeile definiert den Abschnitt '"Admin role required.": "error.admin_required",'.
35. Diese Zeile definiert den Abschnitt '"Invalid credentials.": "error.invalid_credentials",'.
36. Diese Zeile definiert den Abschnitt '"Email already registered.": "error.email_registered",'.
37. Diese Zeile definiert den Abschnitt '"Role must be user or admin.": "error.role_invalid",'.
38. Diese Zeile definiert den Abschnitt '"User not found.": "error.user_not_found",'.
39. Diese Zeile definiert den Abschnitt '"Recipe not found.": "error.recipe_not_found",'.
40. Diese Zeile definiert den Abschnitt '"Review not found.": "error.review_not_found",'.
41. Diese Zeile definiert den Abschnitt '"Image not found.": "error.image_not_found",'.
42. Diese Zeile definiert den Abschnitt '"Not enough permissions for this recipe.": "error.recipe_permission",'.
43. Diese Zeile definiert den Abschnitt '"Not enough permissions for this review.": "error.review_permission",'.
44. Diese Zeile definiert den Abschnitt '"Rating must be between 1 and 5.": "error.rating_range",'.
45. Diese Zeile definiert den Abschnitt '"Title and instructions are required.": "error.title_instructions_required",'.
46. Diese Zeile definiert den Abschnitt '"title_image_url must start with http:// or https://": "error.image_url_scheme",'.
47. Diese Zeile definiert den Abschnitt '"No image URL available.": "error.no_image_url",'.
48. Diese Zeile definiert den Abschnitt '"KochWiki seed is already marked as done.": "error.seed_already_done",'.
49. Diese Zeile definiert den Abschnitt '"Seed can only run on an empty recipes table.": "error.seed_not_empty",'.
50. Diese Zeile definiert den Abschnitt '"Seed finished with errors, marker was not set.": "error.seed_finished_errors",'.
51. Diese Zeile definiert den Abschnitt '"KochWiki seed finished successfully and was marked as done.": "error.seed_success",'.
52. Diese Zeile definiert den Abschnitt '"Please upload a CSV file.": "error.csv_upload_required",'.
53. Diese Zeile definiert den Abschnitt '"Only CSV uploads are allowed.": "error.csv_only",'.
54. Diese Zeile definiert den Abschnitt '"CSV upload too large.": "error.csv_too_large",'.
55. Diese Zeile definiert den Abschnitt '"Uploaded CSV file is empty.": "error.csv_empty",'.
56. Diese Zeile definiert den Abschnitt '"Submission has already been published.": "error.submission_already_published",'.
57. Diese Zeile definiert den Abschnitt '"Import finished in insert-only mode.": "error.import_finished_insert",'.
58. Diese Zeile definiert den Abschnitt '"Import finished in update-existing mode.": "error.import_finished_update",'.
59. Diese Zeile definiert den Abschnitt '"CSRF validation failed.": "error.csrf_failed",'.
60. Diese Zeile definiert den Abschnitt '"Internal server error.": "error.internal",'.
61. Diese Zeile definiert den Abschnitt '}'.
62. Diese Zeile ist leer und strukturiert den Inhalt.
63. Diese Zeile ist leer und strukturiert den Inhalt.
64. Diese Zeile definiert den Abschnitt 'def _resolve_lang(lang: str | None = None, request: Any | None = None) -> str:'.
65. Diese Zeile definiert den Abschnitt 'if lang:'.
66. Diese Zeile definiert den Abschnitt 'return normalize_lang(lang) or DEFAULT_LANG'.
67. Diese Zeile definiert den Abschnitt 'if request is not None:'.
68. Diese Zeile definiert den Abschnitt 'request_lang = normalize_lang(getattr(getattr(request, "state", None), "lang", None))'.
69. Diese Zeile definiert den Abschnitt 'if request_lang:'.
70. Diese Zeile definiert den Abschnitt 'return request_lang'.
71. Diese Zeile definiert den Abschnitt 'return get_current_lang()'.
72. Diese Zeile ist leer und strukturiert den Inhalt.
73. Diese Zeile ist leer und strukturiert den Inhalt.
74. Diese Zeile definiert den Abschnitt 'def t(key: str, lang: str | None = None, request: Any | None = None, **kwargs: Any) -> ...'.
75. Diese Zeile definiert den Abschnitt 'return translate(key, lang=_resolve_lang(lang=lang, request=request), **kwargs)'.
76. Diese Zeile ist leer und strukturiert den Inhalt.
77. Diese Zeile ist leer und strukturiert den Inhalt.
78. Diese Zeile definiert den Abschnitt 'def difficulty_label(value: str | None, lang: str | None = None, request: Any | None = ...'.
79. Diese Zeile definiert den Abschnitt 'if not value:'.
80. Diese Zeile definiert den Abschnitt 'return "-"'.
81. Diese Zeile definiert den Abschnitt 'mapped = DIFFICULTY_MAP.get(value.strip().lower())'.
82. Diese Zeile definiert den Abschnitt 'return t(mapped, lang=lang, request=request) if mapped else value'.
83. Diese Zeile ist leer und strukturiert den Inhalt.
84. Diese Zeile ist leer und strukturiert den Inhalt.
85. Diese Zeile definiert den Abschnitt 'def role_label(value: str | None, lang: str | None = None, request: Any | None = None) ...'.
86. Diese Zeile definiert den Abschnitt 'if not value:'.
87. Diese Zeile definiert den Abschnitt 'return "-"'.
88. Diese Zeile definiert den Abschnitt 'mapped = ROLE_MAP.get(value.strip().lower())'.
89. Diese Zeile definiert den Abschnitt 'return t(mapped, lang=lang, request=request) if mapped else value'.
90. Diese Zeile ist leer und strukturiert den Inhalt.
91. Diese Zeile ist leer und strukturiert den Inhalt.
92. Diese Zeile definiert den Abschnitt 'def submission_status_label(value: str | None, lang: str | None = None, request: Any | ...'.
93. Diese Zeile definiert den Abschnitt 'if not value:'.
94. Diese Zeile definiert den Abschnitt 'return "-"'.
95. Diese Zeile definiert den Abschnitt 'mapped = SUBMISSION_STATUS_MAP.get(value.strip().lower())'.
96. Diese Zeile definiert den Abschnitt 'return t(mapped, lang=lang, request=request) if mapped else value'.
97. Diese Zeile ist leer und strukturiert den Inhalt.
98. Diese Zeile ist leer und strukturiert den Inhalt.
99. Diese Zeile definiert den Abschnitt 'def datetime_de(value: datetime | None, lang: str | None = None, request: Any | None = ...'.
100. Diese Zeile definiert den Abschnitt 'if value is None:'.
101. Diese Zeile definiert den Abschnitt 'return "-"'.
102. Diese Zeile definiert den Abschnitt 'resolved_lang = _resolve_lang(lang=lang, request=request)'.
103. Diese Zeile definiert den Abschnitt 'if resolved_lang == "en":'.
104. Diese Zeile definiert den Abschnitt 'return value.strftime("%Y-%m-%d %H:%M")'.
105. Diese Zeile definiert den Abschnitt 'if resolved_lang == "fr":'.
106. Diese Zeile definiert den Abschnitt 'return value.strftime("%d/%m/%Y %H:%M")'.
107. Diese Zeile definiert den Abschnitt 'return value.strftime("%d.%m.%Y %H:%M")'.
108. Diese Zeile ist leer und strukturiert den Inhalt.
109. Diese Zeile ist leer und strukturiert den Inhalt.
110. Diese Zeile definiert den Abschnitt 'def translate_error_message(message: Any, lang: str | None = None, request: Any | None ...'.
111. Diese Zeile definiert den Abschnitt 'if not isinstance(message, str):'.
112. Diese Zeile definiert den Abschnitt 'return message'.
113. Diese Zeile definiert den Abschnitt 'if message in ERROR_MAP:'.
114. Diese Zeile definiert den Abschnitt 'return t(ERROR_MAP[message], lang=lang, request=request)'.
115. Diese Zeile definiert den Abschnitt 'int_match = re.match(r"^(.+?) must be an integer\.$", message)'.
116. Diese Zeile definiert den Abschnitt 'if int_match:'.
117. Diese Zeile definiert den Abschnitt 'return t("error.field_int", lang=lang, request=request, field=int_match.group(1))'.
118. Diese Zeile definiert den Abschnitt 'positive_match = re.match(r"^(.+?) must be greater than zero\.$", message)'.
119. Diese Zeile definiert den Abschnitt 'if positive_match:'.
120. Diese Zeile definiert den Abschnitt 'return t("error.field_positive", lang=lang, request=request, field=positive_match.group...'.
121. Diese Zeile definiert den Abschnitt 'csv_missing_match = re.match(r"^CSV file not found:\s*(.+)$", message)'.
122. Diese Zeile definiert den Abschnitt 'if csv_missing_match:'.
123. Diese Zeile definiert den Abschnitt 'return f"{t('error.csv_not_found_prefix', lang=lang, request=request)}: {csv_missing_ma...'.
124. Diese Zeile definiert den Abschnitt 'image_resolve_match = re.match(r"^Could not resolve image URL:\s*(.+)$", message)'.
125. Diese Zeile definiert den Abschnitt 'if image_resolve_match:'.
126. Diese Zeile definiert den Abschnitt 'return f"{t('error.image_resolve_prefix', lang=lang, request=request)}: {image_resolve_...'.
127. Diese Zeile definiert den Abschnitt 'return message'.
128. Diese Zeile ist leer und strukturiert den Inhalt.
129. Diese Zeile ist leer und strukturiert den Inhalt.
130. Diese Zeile definiert den Abschnitt '__all__ = ['.
131. Diese Zeile definiert den Abschnitt '"SUPPORTED_LANGS",'.
132. Diese Zeile definiert den Abschnitt '"available_langs",'.
133. Diese Zeile definiert den Abschnitt '"set_current_lang",'.
134. Diese Zeile definiert den Abschnitt '"get_current_lang",'.
135. Diese Zeile definiert den Abschnitt '"t",'.
136. Diese Zeile definiert den Abschnitt '"difficulty_label",'.
137. Diese Zeile definiert den Abschnitt '"role_label",'.
138. Diese Zeile definiert den Abschnitt '"submission_status_label",'.
139. Diese Zeile definiert den Abschnitt '"datetime_de",'.
140. Diese Zeile definiert den Abschnitt '"translate_error_message",'.
141. Diese Zeile definiert den Abschnitt ']'.

## app/dependencies.py
```python
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.i18n import t
from app.i18n.service import available_langs
from app.models import User
from app.security import decode_access_token
from app.services import extract_token

settings = get_settings()


def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User | None:
    cookie_token = request.cookies.get("access_token")
    header_token = extract_token(request.headers.get("Authorization"))
    raw_token = cookie_token or header_token
    token = extract_token(raw_token)
    if not token:
        return None
    try:
        payload = decode_access_token(token)
    except ValueError:
        return None
    subject = str(payload.get("sub", ""))
    if not subject:
        return None
    user = db.scalar(select(User).where(User.email == subject))
    if user:
        request.state.current_user = user
        request.state.rate_limit_user_key = f"user:{user.id}"
    return user


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    user = get_current_user_optional(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("error.auth_required"))
    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))
    return current_user


def template_context(request: Request, current_user: User | None, **kwargs: Any) -> dict[str, Any]:
    csrf_token = getattr(request.state, "csrf_token", None) or request.cookies.get("csrf_token")
    request_id = getattr(request.state, "request_id", None)
    base = {
        "request": request,
        "current_user": current_user,
        "csrf_token": csrf_token,
        "csrf_header_name": settings.csrf_header_name,
        "request_id": request_id,
        "current_lang": getattr(getattr(request, "state", None), "lang", "de"),
        "available_langs": available_langs(),
    }
    base.update(kwargs)
    return base
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'from typing import Any'.
2. Diese Zeile ist leer und strukturiert den Inhalt.
3. Diese Zeile definiert den Abschnitt 'from fastapi import Depends, HTTPException, Request, status'.
4. Diese Zeile definiert den Abschnitt 'from sqlalchemy import select'.
5. Diese Zeile definiert den Abschnitt 'from sqlalchemy.orm import Session'.
6. Diese Zeile ist leer und strukturiert den Inhalt.
7. Diese Zeile definiert den Abschnitt 'from app.config import get_settings'.
8. Diese Zeile definiert den Abschnitt 'from app.database import get_db'.
9. Diese Zeile definiert den Abschnitt 'from app.i18n import t'.
10. Diese Zeile definiert den Abschnitt 'from app.i18n.service import available_langs'.
11. Diese Zeile definiert den Abschnitt 'from app.models import User'.
12. Diese Zeile definiert den Abschnitt 'from app.security import decode_access_token'.
13. Diese Zeile definiert den Abschnitt 'from app.services import extract_token'.
14. Diese Zeile ist leer und strukturiert den Inhalt.
15. Diese Zeile definiert den Abschnitt 'settings = get_settings()'.
16. Diese Zeile ist leer und strukturiert den Inhalt.
17. Diese Zeile ist leer und strukturiert den Inhalt.
18. Diese Zeile definiert den Abschnitt 'def get_current_user_optional(request: Request, db: Session = Depends(get_db)) -> User ...'.
19. Diese Zeile definiert den Abschnitt 'cookie_token = request.cookies.get("access_token")'.
20. Diese Zeile definiert den Abschnitt 'header_token = extract_token(request.headers.get("Authorization"))'.
21. Diese Zeile definiert den Abschnitt 'raw_token = cookie_token or header_token'.
22. Diese Zeile definiert den Abschnitt 'token = extract_token(raw_token)'.
23. Diese Zeile definiert den Abschnitt 'if not token:'.
24. Diese Zeile definiert den Abschnitt 'return None'.
25. Diese Zeile definiert den Abschnitt 'try:'.
26. Diese Zeile definiert den Abschnitt 'payload = decode_access_token(token)'.
27. Diese Zeile definiert den Abschnitt 'except ValueError:'.
28. Diese Zeile definiert den Abschnitt 'return None'.
29. Diese Zeile definiert den Abschnitt 'subject = str(payload.get("sub", ""))'.
30. Diese Zeile definiert den Abschnitt 'if not subject:'.
31. Diese Zeile definiert den Abschnitt 'return None'.
32. Diese Zeile definiert den Abschnitt 'user = db.scalar(select(User).where(User.email == subject))'.
33. Diese Zeile definiert den Abschnitt 'if user:'.
34. Diese Zeile definiert den Abschnitt 'request.state.current_user = user'.
35. Diese Zeile definiert den Abschnitt 'request.state.rate_limit_user_key = f"user:{user.id}"'.
36. Diese Zeile definiert den Abschnitt 'return user'.
37. Diese Zeile ist leer und strukturiert den Inhalt.
38. Diese Zeile ist leer und strukturiert den Inhalt.
39. Diese Zeile definiert den Abschnitt 'def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:'.
40. Diese Zeile definiert den Abschnitt 'user = get_current_user_optional(request, db)'.
41. Diese Zeile definiert den Abschnitt 'if not user:'.
42. Diese Zeile definiert den Abschnitt 'raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("error.auth_requ...'.
43. Diese Zeile definiert den Abschnitt 'return user'.
44. Diese Zeile ist leer und strukturiert den Inhalt.
45. Diese Zeile ist leer und strukturiert den Inhalt.
46. Diese Zeile definiert den Abschnitt 'def get_admin_user(current_user: User = Depends(get_current_user)) -> User:'.
47. Diese Zeile definiert den Abschnitt 'if current_user.role != "admin":'.
48. Diese Zeile definiert den Abschnitt 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_requir...'.
49. Diese Zeile definiert den Abschnitt 'return current_user'.
50. Diese Zeile ist leer und strukturiert den Inhalt.
51. Diese Zeile ist leer und strukturiert den Inhalt.
52. Diese Zeile definiert den Abschnitt 'def template_context(request: Request, current_user: User | None, **kwargs: Any) -> dic...'.
53. Diese Zeile definiert den Abschnitt 'csrf_token = getattr(request.state, "csrf_token", None) or request.cookies.get("csrf_to...'.
54. Diese Zeile definiert den Abschnitt 'request_id = getattr(request.state, "request_id", None)'.
55. Diese Zeile definiert den Abschnitt 'base = {'.
56. Diese Zeile definiert den Abschnitt '"request": request,'.
57. Diese Zeile definiert den Abschnitt '"current_user": current_user,'.
58. Diese Zeile definiert den Abschnitt '"csrf_token": csrf_token,'.
59. Diese Zeile definiert den Abschnitt '"csrf_header_name": settings.csrf_header_name,'.
60. Diese Zeile definiert den Abschnitt '"request_id": request_id,'.
61. Diese Zeile definiert den Abschnitt '"current_lang": getattr(getattr(request, "state", None), "lang", "de"),'.
62. Diese Zeile definiert den Abschnitt '"available_langs": available_langs(),'.
63. Diese Zeile definiert den Abschnitt '}'.
64. Diese Zeile definiert den Abschnitt 'base.update(kwargs)'.
65. Diese Zeile definiert den Abschnitt 'return base'.

## app/views.py
```python
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context

from app.i18n import datetime_de, difficulty_label, role_label, submission_status_label, t
from app.i18n.service import available_langs

templates = Jinja2Templates(directory="app/templates")


@pass_context
def jinja_t(context, key: str, **kwargs):
    request = context.get("request")
    return t(key, request=request, **kwargs)


@pass_context
def jinja_difficulty_label(context, value: str | None):
    request = context.get("request")
    return difficulty_label(value, request=request)


@pass_context
def jinja_role_label(context, value: str | None):
    request = context.get("request")
    return role_label(value, request=request)


@pass_context
def jinja_submission_status_label(context, value: str | None):
    request = context.get("request")
    return submission_status_label(value, request=request)


@pass_context
def jinja_datetime_label(context, value):
    request = context.get("request")
    return datetime_de(value, request=request)


def lang_url(request, code: str) -> str:
    return str(request.url.include_query_params(lang=code))


templates.env.globals["t"] = jinja_t
templates.env.globals["difficulty_label"] = jinja_difficulty_label
templates.env.globals["role_label"] = jinja_role_label
templates.env.globals["submission_status_label"] = jinja_submission_status_label
templates.env.globals["available_langs"] = available_langs()
templates.env.globals["lang_url"] = lang_url
templates.env.filters["datetime_de"] = jinja_datetime_label


def redirect(url: str, status_code: int = 303) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status_code)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'from fastapi.responses import RedirectResponse'.
2. Diese Zeile definiert den Abschnitt 'from fastapi.templating import Jinja2Templates'.
3. Diese Zeile definiert den Abschnitt 'from jinja2 import pass_context'.
4. Diese Zeile ist leer und strukturiert den Inhalt.
5. Diese Zeile definiert den Abschnitt 'from app.i18n import datetime_de, difficulty_label, role_label, submission_status_label, t'.
6. Diese Zeile definiert den Abschnitt 'from app.i18n.service import available_langs'.
7. Diese Zeile ist leer und strukturiert den Inhalt.
8. Diese Zeile definiert den Abschnitt 'templates = Jinja2Templates(directory="app/templates")'.
9. Diese Zeile ist leer und strukturiert den Inhalt.
10. Diese Zeile ist leer und strukturiert den Inhalt.
11. Diese Zeile definiert den Abschnitt '@pass_context'.
12. Diese Zeile definiert den Abschnitt 'def jinja_t(context, key: str, **kwargs):'.
13. Diese Zeile definiert den Abschnitt 'request = context.get("request")'.
14. Diese Zeile definiert den Abschnitt 'return t(key, request=request, **kwargs)'.
15. Diese Zeile ist leer und strukturiert den Inhalt.
16. Diese Zeile ist leer und strukturiert den Inhalt.
17. Diese Zeile definiert den Abschnitt '@pass_context'.
18. Diese Zeile definiert den Abschnitt 'def jinja_difficulty_label(context, value: str | None):'.
19. Diese Zeile definiert den Abschnitt 'request = context.get("request")'.
20. Diese Zeile definiert den Abschnitt 'return difficulty_label(value, request=request)'.
21. Diese Zeile ist leer und strukturiert den Inhalt.
22. Diese Zeile ist leer und strukturiert den Inhalt.
23. Diese Zeile definiert den Abschnitt '@pass_context'.
24. Diese Zeile definiert den Abschnitt 'def jinja_role_label(context, value: str | None):'.
25. Diese Zeile definiert den Abschnitt 'request = context.get("request")'.
26. Diese Zeile definiert den Abschnitt 'return role_label(value, request=request)'.
27. Diese Zeile ist leer und strukturiert den Inhalt.
28. Diese Zeile ist leer und strukturiert den Inhalt.
29. Diese Zeile definiert den Abschnitt '@pass_context'.
30. Diese Zeile definiert den Abschnitt 'def jinja_submission_status_label(context, value: str | None):'.
31. Diese Zeile definiert den Abschnitt 'request = context.get("request")'.
32. Diese Zeile definiert den Abschnitt 'return submission_status_label(value, request=request)'.
33. Diese Zeile ist leer und strukturiert den Inhalt.
34. Diese Zeile ist leer und strukturiert den Inhalt.
35. Diese Zeile definiert den Abschnitt '@pass_context'.
36. Diese Zeile definiert den Abschnitt 'def jinja_datetime_label(context, value):'.
37. Diese Zeile definiert den Abschnitt 'request = context.get("request")'.
38. Diese Zeile definiert den Abschnitt 'return datetime_de(value, request=request)'.
39. Diese Zeile ist leer und strukturiert den Inhalt.
40. Diese Zeile ist leer und strukturiert den Inhalt.
41. Diese Zeile definiert den Abschnitt 'def lang_url(request, code: str) -> str:'.
42. Diese Zeile definiert den Abschnitt 'return str(request.url.include_query_params(lang=code))'.
43. Diese Zeile ist leer und strukturiert den Inhalt.
44. Diese Zeile ist leer und strukturiert den Inhalt.
45. Diese Zeile definiert den Abschnitt 'templates.env.globals["t"] = jinja_t'.
46. Diese Zeile definiert den Abschnitt 'templates.env.globals["difficulty_label"] = jinja_difficulty_label'.
47. Diese Zeile definiert den Abschnitt 'templates.env.globals["role_label"] = jinja_role_label'.
48. Diese Zeile definiert den Abschnitt 'templates.env.globals["submission_status_label"] = jinja_submission_status_label'.
49. Diese Zeile definiert den Abschnitt 'templates.env.globals["available_langs"] = available_langs()'.
50. Diese Zeile definiert den Abschnitt 'templates.env.globals["lang_url"] = lang_url'.
51. Diese Zeile definiert den Abschnitt 'templates.env.filters["datetime_de"] = jinja_datetime_label'.
52. Diese Zeile ist leer und strukturiert den Inhalt.
53. Diese Zeile ist leer und strukturiert den Inhalt.
54. Diese Zeile definiert den Abschnitt 'def redirect(url: str, status_code: int = 303) -> RedirectResponse:'.
55. Diese Zeile definiert den Abschnitt 'return RedirectResponse(url=url, status_code=status_code)'.

## app/main.py
```python
import logging
import traceback
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import func, select
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.config import get_settings
from app.database import SessionLocal
from app.dependencies import template_context
from app.i18n.middleware import LanguageMiddleware
from app.i18n import t, translate_error_message
from app.logging_config import configure_logging
from app.middleware import CSRFMiddleware, HTTPSRedirectMiddleware, RequestContextMiddleware, SecurityHeadersMiddleware
from app.models import Recipe, User
from app.rate_limit import limiter
from app.routers import admin, auth, recipes, submissions
from app.security import hash_password
from app.services import import_kochwiki_csv, is_meta_true, set_meta_value
from app.views import templates

settings = get_settings()
configure_logging()
logger = logging.getLogger("mealmate.app")

app = FastAPI(title=settings.app_name, version="1.0.0", debug=not settings.prod_mode)


class CacheControlStaticFiles(StaticFiles):
    def __init__(self, *args, cache_control: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_control = cache_control

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if self.cache_control and response.status_code == 200:
            response.headers.setdefault("Cache-Control", self.cache_control)
        return response


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
if settings.allowed_hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(LanguageMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)

static_dir = Path("app/static")
static_dir.mkdir(parents=True, exist_ok=True)
static_cache = "public, max-age=3600" if settings.prod_mode else None
app.mount("/static", CacheControlStaticFiles(directory=str(static_dir), cache_control=static_cache), name="static")

app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(submissions.router)
app.include_router(admin.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    accept = request.headers.get("accept", "")
    if exc.status_code == 404 and "text/html" in accept:
        return templates.TemplateResponse(
            "error_404.html",
            template_context(request, None, title=t("error.404_title", request=request)),
            status_code=404,
        )
    detail = translate_error_message(exc.detail, request=request)
    return JSONResponse({"detail": detail}, status_code=exc.status_code)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "-")
    logger.exception("unhandled_exception request_id=%s path=%s", request_id, request.url.path)
    accept = request.headers.get("accept", "")
    if settings.prod_mode:
        if "text/html" in accept:
            return templates.TemplateResponse(
                "error_500.html",
                template_context(
                    request,
                    None,
                    title=t("error.500_title", request=request),
                    show_trace=False,
                    error_trace=None,
                ),
                status_code=500,
            )
        return JSONResponse({"detail": t("error.internal", request=request)}, status_code=500)
    trace = traceback.format_exc()
    if "text/html" in accept:
        return templates.TemplateResponse(
            "error_500.html",
            template_context(
                request,
                None,
                title=t("error.500_title", request=request),
                show_trace=True,
                error_trace=trace,
            ),
            status_code=500,
        )
    return JSONResponse({"detail": t("error.internal", request=request), "trace": trace}, status_code=500)


def _ensure_seed_admin(db) -> User:
    admin = db.scalar(select(User).where(User.role == "admin").order_by(User.id))
    if admin:
        return admin
    fallback_email = settings.seed_admin_email.strip().lower()
    admin = db.scalar(select(User).where(User.email == fallback_email))
    if admin:
        admin.role = "admin"
        db.commit()
        db.refresh(admin)
        return admin
    admin = User(
        email=fallback_email,
        hashed_password=hash_password(settings.seed_admin_password),
        role="admin",
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


def run_auto_seed_if_enabled() -> None:
    if not settings.enable_kochwiki_seed:
        return
    if not settings.auto_seed_kochwiki:
        return
    db = SessionLocal()
    try:
        if is_meta_true(db, "kochwiki_seed_done"):
            return
        recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0
        if recipes_count > 0:
            return
        csv_path = Path(settings.kochwiki_csv_path)
        if not csv_path.exists():
            return
        admin_user = _ensure_seed_admin(db)
        report = import_kochwiki_csv(db, csv_path, admin_user.id, mode="insert_only")
        if report.errors:
            logger.warning("auto_seed_finished_with_errors errors=%s", len(report.errors))
            return
        set_meta_value(db, "kochwiki_seed_done", "1")
        db.commit()
        logger.info(
            "auto_seed_done inserted=%s updated=%s skipped=%s",
            report.inserted,
            report.updated,
            report.skipped,
        )
    finally:
        db.close()


@app.on_event("startup")
def startup_event() -> None:
    run_auto_seed_if_enabled()


@app.get("/health")
@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'import logging'.
2. Diese Zeile definiert den Abschnitt 'import traceback'.
3. Diese Zeile definiert den Abschnitt 'from pathlib import Path'.
4. Diese Zeile ist leer und strukturiert den Inhalt.
5. Diese Zeile definiert den Abschnitt 'from fastapi import FastAPI, Request'.
6. Diese Zeile definiert den Abschnitt 'from fastapi.responses import JSONResponse'.
7. Diese Zeile definiert den Abschnitt 'from fastapi.staticfiles import StaticFiles'.
8. Diese Zeile definiert den Abschnitt 'from slowapi import _rate_limit_exceeded_handler'.
9. Diese Zeile definiert den Abschnitt 'from slowapi.errors import RateLimitExceeded'.
10. Diese Zeile definiert den Abschnitt 'from slowapi.middleware import SlowAPIMiddleware'.
11. Diese Zeile definiert den Abschnitt 'from sqlalchemy import func, select'.
12. Diese Zeile definiert den Abschnitt 'from starlette.exceptions import HTTPException as StarletteHTTPException'.
13. Diese Zeile definiert den Abschnitt 'from starlette.middleware.trustedhost import TrustedHostMiddleware'.
14. Diese Zeile definiert den Abschnitt 'from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware'.
15. Diese Zeile ist leer und strukturiert den Inhalt.
16. Diese Zeile definiert den Abschnitt 'from app.config import get_settings'.
17. Diese Zeile definiert den Abschnitt 'from app.database import SessionLocal'.
18. Diese Zeile definiert den Abschnitt 'from app.dependencies import template_context'.
19. Diese Zeile definiert den Abschnitt 'from app.i18n.middleware import LanguageMiddleware'.
20. Diese Zeile definiert den Abschnitt 'from app.i18n import t, translate_error_message'.
21. Diese Zeile definiert den Abschnitt 'from app.logging_config import configure_logging'.
22. Diese Zeile definiert den Abschnitt 'from app.middleware import CSRFMiddleware, HTTPSRedirectMiddleware, RequestContextMiddl...'.
23. Diese Zeile definiert den Abschnitt 'from app.models import Recipe, User'.
24. Diese Zeile definiert den Abschnitt 'from app.rate_limit import limiter'.
25. Diese Zeile definiert den Abschnitt 'from app.routers import admin, auth, recipes, submissions'.
26. Diese Zeile definiert den Abschnitt 'from app.security import hash_password'.
27. Diese Zeile definiert den Abschnitt 'from app.services import import_kochwiki_csv, is_meta_true, set_meta_value'.
28. Diese Zeile definiert den Abschnitt 'from app.views import templates'.
29. Diese Zeile ist leer und strukturiert den Inhalt.
30. Diese Zeile definiert den Abschnitt 'settings = get_settings()'.
31. Diese Zeile definiert den Abschnitt 'configure_logging()'.
32. Diese Zeile definiert den Abschnitt 'logger = logging.getLogger("mealmate.app")'.
33. Diese Zeile ist leer und strukturiert den Inhalt.
34. Diese Zeile definiert den Abschnitt 'app = FastAPI(title=settings.app_name, version="1.0.0", debug=not settings.prod_mode)'.
35. Diese Zeile ist leer und strukturiert den Inhalt.
36. Diese Zeile ist leer und strukturiert den Inhalt.
37. Diese Zeile definiert den Abschnitt 'class CacheControlStaticFiles(StaticFiles):'.
38. Diese Zeile definiert den Abschnitt 'def __init__(self, *args, cache_control: str | None = None, **kwargs):'.
39. Diese Zeile definiert den Abschnitt 'super().__init__(*args, **kwargs)'.
40. Diese Zeile definiert den Abschnitt 'self.cache_control = cache_control'.
41. Diese Zeile ist leer und strukturiert den Inhalt.
42. Diese Zeile definiert den Abschnitt 'async def get_response(self, path: str, scope):'.
43. Diese Zeile definiert den Abschnitt 'response = await super().get_response(path, scope)'.
44. Diese Zeile definiert den Abschnitt 'if self.cache_control and response.status_code == 200:'.
45. Diese Zeile definiert den Abschnitt 'response.headers.setdefault("Cache-Control", self.cache_control)'.
46. Diese Zeile definiert den Abschnitt 'return response'.
47. Diese Zeile ist leer und strukturiert den Inhalt.
48. Diese Zeile ist leer und strukturiert den Inhalt.
49. Diese Zeile definiert den Abschnitt 'app.state.limiter = limiter'.
50. Diese Zeile definiert den Abschnitt 'app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)'.
51. Diese Zeile definiert den Abschnitt 'app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")'.
52. Diese Zeile definiert den Abschnitt 'if settings.allowed_hosts != ["*"]:'.
53. Diese Zeile definiert den Abschnitt 'app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)'.
54. Diese Zeile definiert den Abschnitt 'app.add_middleware(SlowAPIMiddleware)'.
55. Diese Zeile definiert den Abschnitt 'app.add_middleware(LanguageMiddleware)'.
56. Diese Zeile definiert den Abschnitt 'app.add_middleware(CSRFMiddleware)'.
57. Diese Zeile definiert den Abschnitt 'app.add_middleware(HTTPSRedirectMiddleware)'.
58. Diese Zeile definiert den Abschnitt 'app.add_middleware(SecurityHeadersMiddleware)'.
59. Diese Zeile definiert den Abschnitt 'app.add_middleware(RequestContextMiddleware)'.
60. Diese Zeile ist leer und strukturiert den Inhalt.
61. Diese Zeile definiert den Abschnitt 'static_dir = Path("app/static")'.
62. Diese Zeile definiert den Abschnitt 'static_dir.mkdir(parents=True, exist_ok=True)'.
63. Diese Zeile definiert den Abschnitt 'static_cache = "public, max-age=3600" if settings.prod_mode else None'.
64. Diese Zeile definiert den Abschnitt 'app.mount("/static", CacheControlStaticFiles(directory=str(static_dir), cache_control=s...'.
65. Diese Zeile ist leer und strukturiert den Inhalt.
66. Diese Zeile definiert den Abschnitt 'app.include_router(auth.router)'.
67. Diese Zeile definiert den Abschnitt 'app.include_router(recipes.router)'.
68. Diese Zeile definiert den Abschnitt 'app.include_router(submissions.router)'.
69. Diese Zeile definiert den Abschnitt 'app.include_router(admin.router)'.
70. Diese Zeile ist leer und strukturiert den Inhalt.
71. Diese Zeile ist leer und strukturiert den Inhalt.
72. Diese Zeile definiert den Abschnitt '@app.exception_handler(StarletteHTTPException)'.
73. Diese Zeile definiert den Abschnitt 'async def http_exception_handler(request: Request, exc: StarletteHTTPException):'.
74. Diese Zeile definiert den Abschnitt 'accept = request.headers.get("accept", "")'.
75. Diese Zeile definiert den Abschnitt 'if exc.status_code == 404 and "text/html" in accept:'.
76. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
77. Diese Zeile definiert den Abschnitt '"error_404.html",'.
78. Diese Zeile definiert den Abschnitt 'template_context(request, None, title=t("error.404_title", request=request)),'.
79. Diese Zeile definiert den Abschnitt 'status_code=404,'.
80. Diese Zeile definiert den Abschnitt ')'.
81. Diese Zeile definiert den Abschnitt 'detail = translate_error_message(exc.detail, request=request)'.
82. Diese Zeile definiert den Abschnitt 'return JSONResponse({"detail": detail}, status_code=exc.status_code)'.
83. Diese Zeile ist leer und strukturiert den Inhalt.
84. Diese Zeile ist leer und strukturiert den Inhalt.
85. Diese Zeile definiert den Abschnitt '@app.exception_handler(Exception)'.
86. Diese Zeile definiert den Abschnitt 'async def unhandled_exception_handler(request: Request, exc: Exception):'.
87. Diese Zeile definiert den Abschnitt 'request_id = getattr(request.state, "request_id", "-")'.
88. Diese Zeile definiert den Abschnitt 'logger.exception("unhandled_exception request_id=%s path=%s", request_id, request.url.p...'.
89. Diese Zeile definiert den Abschnitt 'accept = request.headers.get("accept", "")'.
90. Diese Zeile definiert den Abschnitt 'if settings.prod_mode:'.
91. Diese Zeile definiert den Abschnitt 'if "text/html" in accept:'.
92. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
93. Diese Zeile definiert den Abschnitt '"error_500.html",'.
94. Diese Zeile definiert den Abschnitt 'template_context('.
95. Diese Zeile definiert den Abschnitt 'request,'.
96. Diese Zeile definiert den Abschnitt 'None,'.
97. Diese Zeile definiert den Abschnitt 'title=t("error.500_title", request=request),'.
98. Diese Zeile definiert den Abschnitt 'show_trace=False,'.
99. Diese Zeile definiert den Abschnitt 'error_trace=None,'.
100. Diese Zeile definiert den Abschnitt '),'.
101. Diese Zeile definiert den Abschnitt 'status_code=500,'.
102. Diese Zeile definiert den Abschnitt ')'.
103. Diese Zeile definiert den Abschnitt 'return JSONResponse({"detail": t("error.internal", request=request)}, status_code=500)'.
104. Diese Zeile definiert den Abschnitt 'trace = traceback.format_exc()'.
105. Diese Zeile definiert den Abschnitt 'if "text/html" in accept:'.
106. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
107. Diese Zeile definiert den Abschnitt '"error_500.html",'.
108. Diese Zeile definiert den Abschnitt 'template_context('.
109. Diese Zeile definiert den Abschnitt 'request,'.
110. Diese Zeile definiert den Abschnitt 'None,'.
111. Diese Zeile definiert den Abschnitt 'title=t("error.500_title", request=request),'.
112. Diese Zeile definiert den Abschnitt 'show_trace=True,'.
113. Diese Zeile definiert den Abschnitt 'error_trace=trace,'.
114. Diese Zeile definiert den Abschnitt '),'.
115. Diese Zeile definiert den Abschnitt 'status_code=500,'.
116. Diese Zeile definiert den Abschnitt ')'.
117. Diese Zeile definiert den Abschnitt 'return JSONResponse({"detail": t("error.internal", request=request), "trace": trace}, s...'.
118. Diese Zeile ist leer und strukturiert den Inhalt.
119. Diese Zeile ist leer und strukturiert den Inhalt.
120. Diese Zeile definiert den Abschnitt 'def _ensure_seed_admin(db) -> User:'.
121. Diese Zeile definiert den Abschnitt 'admin = db.scalar(select(User).where(User.role == "admin").order_by(User.id))'.
122. Diese Zeile definiert den Abschnitt 'if admin:'.
123. Diese Zeile definiert den Abschnitt 'return admin'.
124. Diese Zeile definiert den Abschnitt 'fallback_email = settings.seed_admin_email.strip().lower()'.
125. Diese Zeile definiert den Abschnitt 'admin = db.scalar(select(User).where(User.email == fallback_email))'.
126. Diese Zeile definiert den Abschnitt 'if admin:'.
127. Diese Zeile definiert den Abschnitt 'admin.role = "admin"'.
128. Diese Zeile definiert den Abschnitt 'db.commit()'.
129. Diese Zeile definiert den Abschnitt 'db.refresh(admin)'.
130. Diese Zeile definiert den Abschnitt 'return admin'.
131. Diese Zeile definiert den Abschnitt 'admin = User('.
132. Diese Zeile definiert den Abschnitt 'email=fallback_email,'.
133. Diese Zeile definiert den Abschnitt 'hashed_password=hash_password(settings.seed_admin_password),'.
134. Diese Zeile definiert den Abschnitt 'role="admin",'.
135. Diese Zeile definiert den Abschnitt ')'.
136. Diese Zeile definiert den Abschnitt 'db.add(admin)'.
137. Diese Zeile definiert den Abschnitt 'db.commit()'.
138. Diese Zeile definiert den Abschnitt 'db.refresh(admin)'.
139. Diese Zeile definiert den Abschnitt 'return admin'.
140. Diese Zeile ist leer und strukturiert den Inhalt.
141. Diese Zeile ist leer und strukturiert den Inhalt.
142. Diese Zeile definiert den Abschnitt 'def run_auto_seed_if_enabled() -> None:'.
143. Diese Zeile definiert den Abschnitt 'if not settings.enable_kochwiki_seed:'.
144. Diese Zeile definiert den Abschnitt 'return'.
145. Diese Zeile definiert den Abschnitt 'if not settings.auto_seed_kochwiki:'.
146. Diese Zeile definiert den Abschnitt 'return'.
147. Diese Zeile definiert den Abschnitt 'db = SessionLocal()'.
148. Diese Zeile definiert den Abschnitt 'try:'.
149. Diese Zeile definiert den Abschnitt 'if is_meta_true(db, "kochwiki_seed_done"):'.
150. Diese Zeile definiert den Abschnitt 'return'.
151. Diese Zeile definiert den Abschnitt 'recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0'.
152. Diese Zeile definiert den Abschnitt 'if recipes_count > 0:'.
153. Diese Zeile definiert den Abschnitt 'return'.
154. Diese Zeile definiert den Abschnitt 'csv_path = Path(settings.kochwiki_csv_path)'.
155. Diese Zeile definiert den Abschnitt 'if not csv_path.exists():'.
156. Diese Zeile definiert den Abschnitt 'return'.
157. Diese Zeile definiert den Abschnitt 'admin_user = _ensure_seed_admin(db)'.
158. Diese Zeile definiert den Abschnitt 'report = import_kochwiki_csv(db, csv_path, admin_user.id, mode="insert_only")'.
159. Diese Zeile definiert den Abschnitt 'if report.errors:'.
160. Diese Zeile definiert den Abschnitt 'logger.warning("auto_seed_finished_with_errors errors=%s", len(report.errors))'.
161. Diese Zeile definiert den Abschnitt 'return'.
162. Diese Zeile definiert den Abschnitt 'set_meta_value(db, "kochwiki_seed_done", "1")'.
163. Diese Zeile definiert den Abschnitt 'db.commit()'.
164. Diese Zeile definiert den Abschnitt 'logger.info('.
165. Diese Zeile definiert den Abschnitt '"auto_seed_done inserted=%s updated=%s skipped=%s",'.
166. Diese Zeile definiert den Abschnitt 'report.inserted,'.
167. Diese Zeile definiert den Abschnitt 'report.updated,'.
168. Diese Zeile definiert den Abschnitt 'report.skipped,'.
169. Diese Zeile definiert den Abschnitt ')'.
170. Diese Zeile definiert den Abschnitt 'finally:'.
171. Diese Zeile definiert den Abschnitt 'db.close()'.
172. Diese Zeile ist leer und strukturiert den Inhalt.
173. Diese Zeile ist leer und strukturiert den Inhalt.
174. Diese Zeile definiert den Abschnitt '@app.on_event("startup")'.
175. Diese Zeile definiert den Abschnitt 'def startup_event() -> None:'.
176. Diese Zeile definiert den Abschnitt 'run_auto_seed_if_enabled()'.
177. Diese Zeile ist leer und strukturiert den Inhalt.
178. Diese Zeile ist leer und strukturiert den Inhalt.
179. Diese Zeile definiert den Abschnitt '@app.get("/health")'.
180. Diese Zeile definiert den Abschnitt '@app.get("/healthz")'.
181. Diese Zeile definiert den Abschnitt 'def healthcheck():'.
182. Diese Zeile definiert den Abschnitt 'return {"status": "ok"}'.

## app/templates/base.html
```jinja2
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="csrf-token" content="{{ csrf_token or '' }}">
  <title>{{ title or t("app.name") }}</title>
  <link rel="stylesheet" href="/static/style.css">
  <script src="/static/htmx.min.js"></script>
  <script src="/static/security.js" defer></script>
</head>
<body>
  <header class="topbar">
    <a href="/" class="brand">{{ t("app.name") }}</a>
    <nav>
      <a href="/">{{ t("nav.discover") }}</a>
      <a href="/submit">{{ t("nav.submit") }}</a>
      {% if current_user %}
      {% if current_user.role == "admin" %}
      <a href="/recipes/new">{{ t("nav.publish_recipe") }}</a>
      {% endif %}
      <a href="/my-recipes">{{ t("nav.my_recipes") }}</a>
      <a href="/my-submissions">{{ t("nav.my_submissions") }}</a>
      <a href="/favorites">{{ t("nav.favorites") }}</a>
      <a href="/me">{{ t("nav.profile") }}</a>
      {% if current_user.role == "admin" %}
      <a href="/admin">{{ t("nav.admin") }}</a>
      <a href="/admin/submissions">{{ t("nav.admin_submissions") }}</a>
      {% endif %}
      <form method="post" action="/logout" class="inline">
        <button type="submit">{{ t("nav.logout") }}</button>
      </form>
      {% else %}
      <a href="/login">{{ t("nav.login") }}</a>
      <a href="/register">{{ t("nav.register") }}</a>
      {% endif %}
      <span class="lang-switch">
        {{ t("nav.language") }}:
        {% for code, label in available_langs %}
        <a href="{{ lang_url(request, code) }}" {% if current_lang == code %}class="active"{% endif %}>{{ label }}</a>
        {% endfor %}
      </span>
    </nav>
  </header>
  <main class="container">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '<!doctype html>'.
2. Diese Zeile definiert den Abschnitt '<html lang="de">'.
3. Diese Zeile definiert den Abschnitt '<head>'.
4. Diese Zeile definiert den Abschnitt '<meta charset="utf-8">'.
5. Diese Zeile definiert den Abschnitt '<meta name="viewport" content="width=device-width, initial-scale=1">'.
6. Diese Zeile definiert den Abschnitt '<meta name="csrf-token" content="{{ csrf_token or '' }}">'.
7. Diese Zeile definiert den Abschnitt '<title>{{ title or t("app.name") }}</title>'.
8. Diese Zeile definiert den Abschnitt '<link rel="stylesheet" href="/static/style.css">'.
9. Diese Zeile definiert den Abschnitt '<script src="/static/htmx.min.js"></script>'.
10. Diese Zeile definiert den Abschnitt '<script src="/static/security.js" defer></script>'.
11. Diese Zeile definiert den Abschnitt '</head>'.
12. Diese Zeile definiert den Abschnitt '<body>'.
13. Diese Zeile definiert den Abschnitt '<header class="topbar">'.
14. Diese Zeile definiert den Abschnitt '<a href="/" class="brand">{{ t("app.name") }}</a>'.
15. Diese Zeile definiert den Abschnitt '<nav>'.
16. Diese Zeile definiert den Abschnitt '<a href="/">{{ t("nav.discover") }}</a>'.
17. Diese Zeile definiert den Abschnitt '<a href="/submit">{{ t("nav.submit") }}</a>'.
18. Diese Zeile definiert den Abschnitt '{% if current_user %}'.
19. Diese Zeile definiert den Abschnitt '{% if current_user.role == "admin" %}'.
20. Diese Zeile definiert den Abschnitt '<a href="/recipes/new">{{ t("nav.publish_recipe") }}</a>'.
21. Diese Zeile definiert den Abschnitt '{% endif %}'.
22. Diese Zeile definiert den Abschnitt '<a href="/my-recipes">{{ t("nav.my_recipes") }}</a>'.
23. Diese Zeile definiert den Abschnitt '<a href="/my-submissions">{{ t("nav.my_submissions") }}</a>'.
24. Diese Zeile definiert den Abschnitt '<a href="/favorites">{{ t("nav.favorites") }}</a>'.
25. Diese Zeile definiert den Abschnitt '<a href="/me">{{ t("nav.profile") }}</a>'.
26. Diese Zeile definiert den Abschnitt '{% if current_user.role == "admin" %}'.
27. Diese Zeile definiert den Abschnitt '<a href="/admin">{{ t("nav.admin") }}</a>'.
28. Diese Zeile definiert den Abschnitt '<a href="/admin/submissions">{{ t("nav.admin_submissions") }}</a>'.
29. Diese Zeile definiert den Abschnitt '{% endif %}'.
30. Diese Zeile definiert den Abschnitt '<form method="post" action="/logout" class="inline">'.
31. Diese Zeile definiert den Abschnitt '<button type="submit">{{ t("nav.logout") }}</button>'.
32. Diese Zeile definiert den Abschnitt '</form>'.
33. Diese Zeile definiert den Abschnitt '{% else %}'.
34. Diese Zeile definiert den Abschnitt '<a href="/login">{{ t("nav.login") }}</a>'.
35. Diese Zeile definiert den Abschnitt '<a href="/register">{{ t("nav.register") }}</a>'.
36. Diese Zeile definiert den Abschnitt '{% endif %}'.
37. Diese Zeile definiert den Abschnitt '<span class="lang-switch">'.
38. Diese Zeile definiert den Abschnitt '{{ t("nav.language") }}:'.
39. Diese Zeile definiert den Abschnitt '{% for code, label in available_langs %}'.
40. Diese Zeile definiert den Abschnitt '<a href="{{ lang_url(request, code) }}" {% if current_lang == code %}class="active"{% e...'.
41. Diese Zeile definiert den Abschnitt '{% endfor %}'.
42. Diese Zeile definiert den Abschnitt '</span>'.
43. Diese Zeile definiert den Abschnitt '</nav>'.
44. Diese Zeile definiert den Abschnitt '</header>'.
45. Diese Zeile definiert den Abschnitt '<main class="container">'.
46. Diese Zeile definiert den Abschnitt '{% block content %}{% endblock %}'.
47. Diese Zeile definiert den Abschnitt '</main>'.
48. Diese Zeile definiert den Abschnitt '</body>'.
49. Diese Zeile definiert den Abschnitt '</html>'.

## app/templates/home.html
```jinja2
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("discover.title") }}</h1>
  <form class="grid" hx-get="/" hx-target="#recipe-list" hx-push-url="true">
    <input type="text" name="title" value="{{ title }}" placeholder="{{ t('discover.filter.title_contains') }}">
    <select name="category">
      <option value="">{{ t("home.all_categories") }}</option>
      {% for option in category_options %}
      <option value="{{ option }}" {% if category == option %}selected{% endif %}>{{ option }}</option>
      {% endfor %}
    </select>
    <select name="difficulty">
      <option value="">{{ t("discover.filter.difficulty") }}</option>
      <option value="easy" {% if difficulty == "easy" %}selected{% endif %}>{{ t("difficulty.easy") }}</option>
      <option value="medium" {% if difficulty == "medium" %}selected{% endif %}>{{ t("difficulty.medium") }}</option>
      <option value="hard" {% if difficulty == "hard" %}selected{% endif %}>{{ t("difficulty.hard") }}</option>
    </select>
    <input type="text" name="ingredient" value="{{ ingredient }}" placeholder="{{ t('discover.filter.ingredient') }}">
    <select name="sort">
      <option value="date" {% if sort == "date" %}selected{% endif %}>{{ t("discover.sort.newest") }}</option>
      <option value="prep_time" {% if sort == "prep_time" %}selected{% endif %}>{{ t("discover.sort.prep_time") }}</option>
      <option value="avg_rating" {% if sort == "avg_rating" %}selected{% endif %}>{{ t("discover.sort.rating_desc") }}</option>
    </select>
    <select name="per_page">
      {% for option in per_page_options %}
      <option value="{{ option }}" {% if per_page == option %}selected{% endif %}>{{ t("home.per_page") }}: {{ option }}</option>
      {% endfor %}
    </select>
    <button type="submit">{{ t("discover.filter.apply") }}</button>
  </form>
</section>
<section id="recipe-list">
  {% include "partials/recipe_list.html" %}
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '{% extends "base.html" %}'.
2. Diese Zeile definiert den Abschnitt '{% block content %}'.
3. Diese Zeile definiert den Abschnitt '<section class="panel">'.
4. Diese Zeile definiert den Abschnitt '<h1>{{ t("discover.title") }}</h1>'.
5. Diese Zeile definiert den Abschnitt '<form class="grid" hx-get="/" hx-target="#recipe-list" hx-push-url="true">'.
6. Diese Zeile definiert den Abschnitt '<input type="text" name="title" value="{{ title }}" placeholder="{{ t('discover.filter....'.
7. Diese Zeile definiert den Abschnitt '<select name="category">'.
8. Diese Zeile definiert den Abschnitt '<option value="">{{ t("home.all_categories") }}</option>'.
9. Diese Zeile definiert den Abschnitt '{% for option in category_options %}'.
10. Diese Zeile definiert den Abschnitt '<option value="{{ option }}" {% if category == option %}selected{% endif %}>{{ option }...'.
11. Diese Zeile definiert den Abschnitt '{% endfor %}'.
12. Diese Zeile definiert den Abschnitt '</select>'.
13. Diese Zeile definiert den Abschnitt '<select name="difficulty">'.
14. Diese Zeile definiert den Abschnitt '<option value="">{{ t("discover.filter.difficulty") }}</option>'.
15. Diese Zeile definiert den Abschnitt '<option value="easy" {% if difficulty == "easy" %}selected{% endif %}>{{ t("difficulty....'.
16. Diese Zeile definiert den Abschnitt '<option value="medium" {% if difficulty == "medium" %}selected{% endif %}>{{ t("difficu...'.
17. Diese Zeile definiert den Abschnitt '<option value="hard" {% if difficulty == "hard" %}selected{% endif %}>{{ t("difficulty....'.
18. Diese Zeile definiert den Abschnitt '</select>'.
19. Diese Zeile definiert den Abschnitt '<input type="text" name="ingredient" value="{{ ingredient }}" placeholder="{{ t('discov...'.
20. Diese Zeile definiert den Abschnitt '<select name="sort">'.
21. Diese Zeile definiert den Abschnitt '<option value="date" {% if sort == "date" %}selected{% endif %}>{{ t("discover.sort.new...'.
22. Diese Zeile definiert den Abschnitt '<option value="prep_time" {% if sort == "prep_time" %}selected{% endif %}>{{ t("discove...'.
23. Diese Zeile definiert den Abschnitt '<option value="avg_rating" {% if sort == "avg_rating" %}selected{% endif %}>{{ t("disco...'.
24. Diese Zeile definiert den Abschnitt '</select>'.
25. Diese Zeile definiert den Abschnitt '<select name="per_page">'.
26. Diese Zeile definiert den Abschnitt '{% for option in per_page_options %}'.
27. Diese Zeile definiert den Abschnitt '<option value="{{ option }}" {% if per_page == option %}selected{% endif %}>{{ t("home....'.
28. Diese Zeile definiert den Abschnitt '{% endfor %}'.
29. Diese Zeile definiert den Abschnitt '</select>'.
30. Diese Zeile definiert den Abschnitt '<button type="submit">{{ t("discover.filter.apply") }}</button>'.
31. Diese Zeile definiert den Abschnitt '</form>'.
32. Diese Zeile definiert den Abschnitt '</section>'.
33. Diese Zeile definiert den Abschnitt '<section id="recipe-list">'.
34. Diese Zeile definiert den Abschnitt '{% include "partials/recipe_list.html" %}'.
35. Diese Zeile definiert den Abschnitt '</section>'.
36. Diese Zeile definiert den Abschnitt '{% endblock %}'.

## app/static/style.css
```css
:root {
  --bg: #f8f7f3;
  --panel: #ffffff;
  --ink: #1d2433;
  --accent: #0f766e;
  --danger: #b91c1c;
  --border: #d1d5db;
  --font: "Segoe UI", "Trebuchet MS", sans-serif;
}

* {
  box-sizing: border-box;
}

body {
  margin: 0;
  color: var(--ink);
  background: radial-gradient(circle at top right, #e8f5f1, var(--bg));
  font-family: var(--font);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 9;
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  background: #fff;
  border-bottom: 1px solid var(--border);
}

.brand {
  text-decoration: none;
  color: var(--accent);
  font-weight: 700;
  font-size: 1.25rem;
}

nav {
  display: flex;
  flex-wrap: wrap;
  gap: 0.6rem;
  align-items: center;
}

a {
  color: var(--accent);
}

.container {
  max-width: 1080px;
  margin: 1.2rem auto;
  padding: 0 1rem 2rem;
}

.panel {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 1rem;
  box-shadow: 0 5px 14px rgba(0, 0, 0, 0.05);
}

.narrow {
  max-width: 480px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 0.5rem;
}

.stack {
  display: grid;
  gap: 0.7rem;
}

.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 0.8rem;
}

.card {
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.8rem;
  background: #fff;
}

.card h3 {
  margin: 0.2rem 0 0.4rem;
  font-size: 1rem;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  color: #4b5563;
  font-size: 0.95rem;
}

.summary {
  margin: 0.2rem 0 0.45rem;
  color: #24303f;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.thumb {
  width: 100%;
  height: 160px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.hero-image {
  width: 100%;
  max-height: 380px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 0.8rem;
}

input,
select,
textarea,
button {
  width: 100%;
  padding: 0.55rem 0.6rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  font: inherit;
}

button {
  cursor: pointer;
  background: var(--accent);
  color: #fff;
  border: none;
}

.inline {
  display: inline-flex;
  gap: 0.4rem;
  align-items: center;
}

.inline button,
.inline input,
.inline select {
  width: auto;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.7rem;
}

.hidden {
  display: none !important;
}

.error {
  color: var(--danger);
  font-weight: 700;
}

.pagination {
  display: grid;
  justify-items: center;
  gap: 0.55rem;
  margin-top: 1rem;
}

.list-summary {
  margin: 0.3rem 0 0.8rem;
  font-weight: 600;
}

.pagination-links {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 0.4rem;
  align-items: center;
}

.pagination-links a {
  min-width: 2rem;
  text-align: center;
  text-decoration: none;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.35rem 0.55rem;
  background: #fff;
}

.pagination-links .active {
  min-width: 2rem;
  text-align: center;
  border: 1px solid var(--accent);
  border-radius: 8px;
  padding: 0.35rem 0.55rem;
  background: var(--accent);
  color: #fff;
}

.pagination-links .disabled {
  min-width: 2rem;
  text-align: center;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.35rem 0.55rem;
  color: #9ca3af;
  background: #f3f4f6;
}

.pagination-links .ellipsis {
  min-width: 2rem;
  text-align: center;
  padding: 0.35rem 0.55rem;
  color: #6b7280;
}

.pagination-info {
  color: #4b5563;
  font-size: 0.95rem;
}

pre {
  white-space: pre-wrap;
  word-break: break-word;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: #f8fafc;
  padding: 0.7rem;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid var(--border);
  padding: 0.6rem 0.4rem;
  text-align: left;
}

.lang-switch {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  color: #4b5563;
  font-size: 0.92rem;
}

.lang-switch a {
  text-decoration: none;
  padding: 0.2rem 0.45rem;
  border: 1px solid var(--border);
  border-radius: 999px;
  color: var(--accent);
  background: #fff;
}

.lang-switch a.active {
  color: #fff;
  background: var(--accent);
  border-color: var(--accent);
}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt ':root {'.
2. Diese Zeile definiert den Abschnitt '--bg: #f8f7f3;'.
3. Diese Zeile definiert den Abschnitt '--panel: #ffffff;'.
4. Diese Zeile definiert den Abschnitt '--ink: #1d2433;'.
5. Diese Zeile definiert den Abschnitt '--accent: #0f766e;'.
6. Diese Zeile definiert den Abschnitt '--danger: #b91c1c;'.
7. Diese Zeile definiert den Abschnitt '--border: #d1d5db;'.
8. Diese Zeile definiert den Abschnitt '--font: "Segoe UI", "Trebuchet MS", sans-serif;'.
9. Diese Zeile definiert den Abschnitt '}'.
10. Diese Zeile ist leer und strukturiert den Inhalt.
11. Diese Zeile definiert den Abschnitt '* {'.
12. Diese Zeile definiert den Abschnitt 'box-sizing: border-box;'.
13. Diese Zeile definiert den Abschnitt '}'.
14. Diese Zeile ist leer und strukturiert den Inhalt.
15. Diese Zeile definiert den Abschnitt 'body {'.
16. Diese Zeile definiert den Abschnitt 'margin: 0;'.
17. Diese Zeile definiert den Abschnitt 'color: var(--ink);'.
18. Diese Zeile definiert den Abschnitt 'background: radial-gradient(circle at top right, #e8f5f1, var(--bg));'.
19. Diese Zeile definiert den Abschnitt 'font-family: var(--font);'.
20. Diese Zeile definiert den Abschnitt '}'.
21. Diese Zeile ist leer und strukturiert den Inhalt.
22. Diese Zeile definiert den Abschnitt '.topbar {'.
23. Diese Zeile definiert den Abschnitt 'position: sticky;'.
24. Diese Zeile definiert den Abschnitt 'top: 0;'.
25. Diese Zeile definiert den Abschnitt 'z-index: 9;'.
26. Diese Zeile definiert den Abschnitt 'display: flex;'.
27. Diese Zeile definiert den Abschnitt 'justify-content: space-between;'.
28. Diese Zeile definiert den Abschnitt 'gap: 1rem;'.
29. Diese Zeile definiert den Abschnitt 'align-items: center;'.
30. Diese Zeile definiert den Abschnitt 'padding: 1rem;'.
31. Diese Zeile definiert den Abschnitt 'background: #fff;'.
32. Diese Zeile definiert den Abschnitt 'border-bottom: 1px solid var(--border);'.
33. Diese Zeile definiert den Abschnitt '}'.
34. Diese Zeile ist leer und strukturiert den Inhalt.
35. Diese Zeile definiert den Abschnitt '.brand {'.
36. Diese Zeile definiert den Abschnitt 'text-decoration: none;'.
37. Diese Zeile definiert den Abschnitt 'color: var(--accent);'.
38. Diese Zeile definiert den Abschnitt 'font-weight: 700;'.
39. Diese Zeile definiert den Abschnitt 'font-size: 1.25rem;'.
40. Diese Zeile definiert den Abschnitt '}'.
41. Diese Zeile ist leer und strukturiert den Inhalt.
42. Diese Zeile definiert den Abschnitt 'nav {'.
43. Diese Zeile definiert den Abschnitt 'display: flex;'.
44. Diese Zeile definiert den Abschnitt 'flex-wrap: wrap;'.
45. Diese Zeile definiert den Abschnitt 'gap: 0.6rem;'.
46. Diese Zeile definiert den Abschnitt 'align-items: center;'.
47. Diese Zeile definiert den Abschnitt '}'.
48. Diese Zeile ist leer und strukturiert den Inhalt.
49. Diese Zeile definiert den Abschnitt 'a {'.
50. Diese Zeile definiert den Abschnitt 'color: var(--accent);'.
51. Diese Zeile definiert den Abschnitt '}'.
52. Diese Zeile ist leer und strukturiert den Inhalt.
53. Diese Zeile definiert den Abschnitt '.container {'.
54. Diese Zeile definiert den Abschnitt 'max-width: 1080px;'.
55. Diese Zeile definiert den Abschnitt 'margin: 1.2rem auto;'.
56. Diese Zeile definiert den Abschnitt 'padding: 0 1rem 2rem;'.
57. Diese Zeile definiert den Abschnitt '}'.
58. Diese Zeile ist leer und strukturiert den Inhalt.
59. Diese Zeile definiert den Abschnitt '.panel {'.
60. Diese Zeile definiert den Abschnitt 'background: var(--panel);'.
61. Diese Zeile definiert den Abschnitt 'border: 1px solid var(--border);'.
62. Diese Zeile definiert den Abschnitt 'border-radius: 12px;'.
63. Diese Zeile definiert den Abschnitt 'padding: 1rem;'.
64. Diese Zeile definiert den Abschnitt 'margin-bottom: 1rem;'.
65. Diese Zeile definiert den Abschnitt 'box-shadow: 0 5px 14px rgba(0, 0, 0, 0.05);'.
66. Diese Zeile definiert den Abschnitt '}'.
67. Diese Zeile ist leer und strukturiert den Inhalt.
68. Diese Zeile definiert den Abschnitt '.narrow {'.
69. Diese Zeile definiert den Abschnitt 'max-width: 480px;'.
70. Diese Zeile definiert den Abschnitt '}'.
71. Diese Zeile ist leer und strukturiert den Inhalt.
72. Diese Zeile definiert den Abschnitt '.grid {'.
73. Diese Zeile definiert den Abschnitt 'display: grid;'.
74. Diese Zeile definiert den Abschnitt 'grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));'.
75. Diese Zeile definiert den Abschnitt 'gap: 0.5rem;'.
76. Diese Zeile definiert den Abschnitt '}'.
77. Diese Zeile ist leer und strukturiert den Inhalt.
78. Diese Zeile definiert den Abschnitt '.stack {'.
79. Diese Zeile definiert den Abschnitt 'display: grid;'.
80. Diese Zeile definiert den Abschnitt 'gap: 0.7rem;'.
81. Diese Zeile definiert den Abschnitt '}'.
82. Diese Zeile ist leer und strukturiert den Inhalt.
83. Diese Zeile definiert den Abschnitt '.cards {'.
84. Diese Zeile definiert den Abschnitt 'display: grid;'.
85. Diese Zeile definiert den Abschnitt 'grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));'.
86. Diese Zeile definiert den Abschnitt 'gap: 0.8rem;'.
87. Diese Zeile definiert den Abschnitt '}'.
88. Diese Zeile ist leer und strukturiert den Inhalt.
89. Diese Zeile definiert den Abschnitt '.card {'.
90. Diese Zeile definiert den Abschnitt 'border: 1px solid var(--border);'.
91. Diese Zeile definiert den Abschnitt 'border-radius: 10px;'.
92. Diese Zeile definiert den Abschnitt 'padding: 0.8rem;'.
93. Diese Zeile definiert den Abschnitt 'background: #fff;'.
94. Diese Zeile definiert den Abschnitt '}'.
95. Diese Zeile ist leer und strukturiert den Inhalt.
96. Diese Zeile definiert den Abschnitt '.card h3 {'.
97. Diese Zeile definiert den Abschnitt 'margin: 0.2rem 0 0.4rem;'.
98. Diese Zeile definiert den Abschnitt 'font-size: 1rem;'.
99. Diese Zeile definiert den Abschnitt 'line-height: 1.3;'.
100. Diese Zeile definiert den Abschnitt 'display: -webkit-box;'.
101. Diese Zeile definiert den Abschnitt '-webkit-line-clamp: 2;'.
102. Diese Zeile definiert den Abschnitt '-webkit-box-orient: vertical;'.
103. Diese Zeile definiert den Abschnitt 'overflow: hidden;'.
104. Diese Zeile definiert den Abschnitt '}'.
105. Diese Zeile ist leer und strukturiert den Inhalt.
106. Diese Zeile definiert den Abschnitt '.meta {'.
107. Diese Zeile definiert den Abschnitt 'color: #4b5563;'.
108. Diese Zeile definiert den Abschnitt 'font-size: 0.95rem;'.
109. Diese Zeile definiert den Abschnitt '}'.
110. Diese Zeile ist leer und strukturiert den Inhalt.
111. Diese Zeile definiert den Abschnitt '.summary {'.
112. Diese Zeile definiert den Abschnitt 'margin: 0.2rem 0 0.45rem;'.
113. Diese Zeile definiert den Abschnitt 'color: #24303f;'.
114. Diese Zeile definiert den Abschnitt 'display: -webkit-box;'.
115. Diese Zeile definiert den Abschnitt '-webkit-line-clamp: 3;'.
116. Diese Zeile definiert den Abschnitt '-webkit-box-orient: vertical;'.
117. Diese Zeile definiert den Abschnitt 'overflow: hidden;'.
118. Diese Zeile definiert den Abschnitt '}'.
119. Diese Zeile ist leer und strukturiert den Inhalt.
120. Diese Zeile definiert den Abschnitt '.thumb {'.
121. Diese Zeile definiert den Abschnitt 'width: 100%;'.
122. Diese Zeile definiert den Abschnitt 'height: 160px;'.
123. Diese Zeile definiert den Abschnitt 'object-fit: cover;'.
124. Diese Zeile definiert den Abschnitt 'border-radius: 8px;'.
125. Diese Zeile definiert den Abschnitt 'margin-bottom: 0.5rem;'.
126. Diese Zeile definiert den Abschnitt '}'.
127. Diese Zeile ist leer und strukturiert den Inhalt.
128. Diese Zeile definiert den Abschnitt '.hero-image {'.
129. Diese Zeile definiert den Abschnitt 'width: 100%;'.
130. Diese Zeile definiert den Abschnitt 'max-height: 380px;'.
131. Diese Zeile definiert den Abschnitt 'object-fit: cover;'.
132. Diese Zeile definiert den Abschnitt 'border-radius: 10px;'.
133. Diese Zeile definiert den Abschnitt 'margin-bottom: 0.8rem;'.
134. Diese Zeile definiert den Abschnitt '}'.
135. Diese Zeile ist leer und strukturiert den Inhalt.
136. Diese Zeile definiert den Abschnitt 'input,'.
137. Diese Zeile definiert den Abschnitt 'select,'.
138. Diese Zeile definiert den Abschnitt 'textarea,'.
139. Diese Zeile definiert den Abschnitt 'button {'.
140. Diese Zeile definiert den Abschnitt 'width: 100%;'.
141. Diese Zeile definiert den Abschnitt 'padding: 0.55rem 0.6rem;'.
142. Diese Zeile definiert den Abschnitt 'border-radius: 8px;'.
143. Diese Zeile definiert den Abschnitt 'border: 1px solid var(--border);'.
144. Diese Zeile definiert den Abschnitt 'font: inherit;'.
145. Diese Zeile definiert den Abschnitt '}'.
146. Diese Zeile ist leer und strukturiert den Inhalt.
147. Diese Zeile definiert den Abschnitt 'button {'.
148. Diese Zeile definiert den Abschnitt 'cursor: pointer;'.
149. Diese Zeile definiert den Abschnitt 'background: var(--accent);'.
150. Diese Zeile definiert den Abschnitt 'color: #fff;'.
151. Diese Zeile definiert den Abschnitt 'border: none;'.
152. Diese Zeile definiert den Abschnitt '}'.
153. Diese Zeile ist leer und strukturiert den Inhalt.
154. Diese Zeile definiert den Abschnitt '.inline {'.
155. Diese Zeile definiert den Abschnitt 'display: inline-flex;'.
156. Diese Zeile definiert den Abschnitt 'gap: 0.4rem;'.
157. Diese Zeile definiert den Abschnitt 'align-items: center;'.
158. Diese Zeile definiert den Abschnitt '}'.
159. Diese Zeile ist leer und strukturiert den Inhalt.
160. Diese Zeile definiert den Abschnitt '.inline button,'.
161. Diese Zeile definiert den Abschnitt '.inline input,'.
162. Diese Zeile definiert den Abschnitt '.inline select {'.
163. Diese Zeile definiert den Abschnitt 'width: auto;'.
164. Diese Zeile definiert den Abschnitt '}'.
165. Diese Zeile ist leer und strukturiert den Inhalt.
166. Diese Zeile definiert den Abschnitt '.actions {'.
167. Diese Zeile definiert den Abschnitt 'display: flex;'.
168. Diese Zeile definiert den Abschnitt 'flex-wrap: wrap;'.
169. Diese Zeile definiert den Abschnitt 'gap: 0.5rem;'.
170. Diese Zeile definiert den Abschnitt 'margin-top: 0.7rem;'.
171. Diese Zeile definiert den Abschnitt '}'.
172. Diese Zeile ist leer und strukturiert den Inhalt.
173. Diese Zeile definiert den Abschnitt '.hidden {'.
174. Diese Zeile definiert den Abschnitt 'display: none !important;'.
175. Diese Zeile definiert den Abschnitt '}'.
176. Diese Zeile ist leer und strukturiert den Inhalt.
177. Diese Zeile definiert den Abschnitt '.error {'.
178. Diese Zeile definiert den Abschnitt 'color: var(--danger);'.
179. Diese Zeile definiert den Abschnitt 'font-weight: 700;'.
180. Diese Zeile definiert den Abschnitt '}'.
181. Diese Zeile ist leer und strukturiert den Inhalt.
182. Diese Zeile definiert den Abschnitt '.pagination {'.
183. Diese Zeile definiert den Abschnitt 'display: grid;'.
184. Diese Zeile definiert den Abschnitt 'justify-items: center;'.
185. Diese Zeile definiert den Abschnitt 'gap: 0.55rem;'.
186. Diese Zeile definiert den Abschnitt 'margin-top: 1rem;'.
187. Diese Zeile definiert den Abschnitt '}'.
188. Diese Zeile ist leer und strukturiert den Inhalt.
189. Diese Zeile definiert den Abschnitt '.list-summary {'.
190. Diese Zeile definiert den Abschnitt 'margin: 0.3rem 0 0.8rem;'.
191. Diese Zeile definiert den Abschnitt 'font-weight: 600;'.
192. Diese Zeile definiert den Abschnitt '}'.
193. Diese Zeile ist leer und strukturiert den Inhalt.
194. Diese Zeile definiert den Abschnitt '.pagination-links {'.
195. Diese Zeile definiert den Abschnitt 'display: flex;'.
196. Diese Zeile definiert den Abschnitt 'justify-content: center;'.
197. Diese Zeile definiert den Abschnitt 'flex-wrap: wrap;'.
198. Diese Zeile definiert den Abschnitt 'gap: 0.4rem;'.
199. Diese Zeile definiert den Abschnitt 'align-items: center;'.
200. Diese Zeile definiert den Abschnitt '}'.
201. Diese Zeile ist leer und strukturiert den Inhalt.
202. Diese Zeile definiert den Abschnitt '.pagination-links a {'.
203. Diese Zeile definiert den Abschnitt 'min-width: 2rem;'.
204. Diese Zeile definiert den Abschnitt 'text-align: center;'.
205. Diese Zeile definiert den Abschnitt 'text-decoration: none;'.
206. Diese Zeile definiert den Abschnitt 'border: 1px solid var(--border);'.
207. Diese Zeile definiert den Abschnitt 'border-radius: 8px;'.
208. Diese Zeile definiert den Abschnitt 'padding: 0.35rem 0.55rem;'.
209. Diese Zeile definiert den Abschnitt 'background: #fff;'.
210. Diese Zeile definiert den Abschnitt '}'.
211. Diese Zeile ist leer und strukturiert den Inhalt.
212. Diese Zeile definiert den Abschnitt '.pagination-links .active {'.
213. Diese Zeile definiert den Abschnitt 'min-width: 2rem;'.
214. Diese Zeile definiert den Abschnitt 'text-align: center;'.
215. Diese Zeile definiert den Abschnitt 'border: 1px solid var(--accent);'.
216. Diese Zeile definiert den Abschnitt 'border-radius: 8px;'.
217. Diese Zeile definiert den Abschnitt 'padding: 0.35rem 0.55rem;'.
218. Diese Zeile definiert den Abschnitt 'background: var(--accent);'.
219. Diese Zeile definiert den Abschnitt 'color: #fff;'.
220. Diese Zeile definiert den Abschnitt '}'.
221. Diese Zeile ist leer und strukturiert den Inhalt.
222. Diese Zeile definiert den Abschnitt '.pagination-links .disabled {'.
223. Diese Zeile definiert den Abschnitt 'min-width: 2rem;'.
224. Diese Zeile definiert den Abschnitt 'text-align: center;'.
225. Diese Zeile definiert den Abschnitt 'border: 1px solid var(--border);'.
226. Diese Zeile definiert den Abschnitt 'border-radius: 8px;'.
227. Diese Zeile definiert den Abschnitt 'padding: 0.35rem 0.55rem;'.
228. Diese Zeile definiert den Abschnitt 'color: #9ca3af;'.
229. Diese Zeile definiert den Abschnitt 'background: #f3f4f6;'.
230. Diese Zeile definiert den Abschnitt '}'.
231. Diese Zeile ist leer und strukturiert den Inhalt.
232. Diese Zeile definiert den Abschnitt '.pagination-links .ellipsis {'.
233. Diese Zeile definiert den Abschnitt 'min-width: 2rem;'.
234. Diese Zeile definiert den Abschnitt 'text-align: center;'.
235. Diese Zeile definiert den Abschnitt 'padding: 0.35rem 0.55rem;'.
236. Diese Zeile definiert den Abschnitt 'color: #6b7280;'.
237. Diese Zeile definiert den Abschnitt '}'.
238. Diese Zeile ist leer und strukturiert den Inhalt.
239. Diese Zeile definiert den Abschnitt '.pagination-info {'.
240. Diese Zeile definiert den Abschnitt 'color: #4b5563;'.
241. Diese Zeile definiert den Abschnitt 'font-size: 0.95rem;'.
242. Diese Zeile definiert den Abschnitt '}'.
243. Diese Zeile ist leer und strukturiert den Inhalt.
244. Diese Zeile definiert den Abschnitt 'pre {'.
245. Diese Zeile definiert den Abschnitt 'white-space: pre-wrap;'.
246. Diese Zeile definiert den Abschnitt 'word-break: break-word;'.
247. Diese Zeile definiert den Abschnitt 'border: 1px solid var(--border);'.
248. Diese Zeile definiert den Abschnitt 'border-radius: 8px;'.
249. Diese Zeile definiert den Abschnitt 'background: #f8fafc;'.
250. Diese Zeile definiert den Abschnitt 'padding: 0.7rem;'.
251. Diese Zeile definiert den Abschnitt '}'.
252. Diese Zeile ist leer und strukturiert den Inhalt.
253. Diese Zeile definiert den Abschnitt 'table {'.
254. Diese Zeile definiert den Abschnitt 'width: 100%;'.
255. Diese Zeile definiert den Abschnitt 'border-collapse: collapse;'.
256. Diese Zeile definiert den Abschnitt '}'.
257. Diese Zeile ist leer und strukturiert den Inhalt.
258. Diese Zeile definiert den Abschnitt 'th,'.
259. Diese Zeile definiert den Abschnitt 'td {'.
260. Diese Zeile definiert den Abschnitt 'border-bottom: 1px solid var(--border);'.
261. Diese Zeile definiert den Abschnitt 'padding: 0.6rem 0.4rem;'.
262. Diese Zeile definiert den Abschnitt 'text-align: left;'.
263. Diese Zeile definiert den Abschnitt '}'.
264. Diese Zeile ist leer und strukturiert den Inhalt.
265. Diese Zeile definiert den Abschnitt '.lang-switch {'.
266. Diese Zeile definiert den Abschnitt 'display: inline-flex;'.
267. Diese Zeile definiert den Abschnitt 'align-items: center;'.
268. Diese Zeile definiert den Abschnitt 'gap: 0.35rem;'.
269. Diese Zeile definiert den Abschnitt 'color: #4b5563;'.
270. Diese Zeile definiert den Abschnitt 'font-size: 0.92rem;'.
271. Diese Zeile definiert den Abschnitt '}'.
272. Diese Zeile ist leer und strukturiert den Inhalt.
273. Diese Zeile definiert den Abschnitt '.lang-switch a {'.
274. Diese Zeile definiert den Abschnitt 'text-decoration: none;'.
275. Diese Zeile definiert den Abschnitt 'padding: 0.2rem 0.45rem;'.
276. Diese Zeile definiert den Abschnitt 'border: 1px solid var(--border);'.
277. Diese Zeile definiert den Abschnitt 'border-radius: 999px;'.
278. Diese Zeile definiert den Abschnitt 'color: var(--accent);'.
279. Diese Zeile definiert den Abschnitt 'background: #fff;'.
280. Diese Zeile definiert den Abschnitt '}'.
281. Diese Zeile ist leer und strukturiert den Inhalt.
282. Diese Zeile definiert den Abschnitt '.lang-switch a.active {'.
283. Diese Zeile definiert den Abschnitt 'color: #fff;'.
284. Diese Zeile definiert den Abschnitt 'background: var(--accent);'.
285. Diese Zeile definiert den Abschnitt 'border-color: var(--accent);'.
286. Diese Zeile definiert den Abschnitt '}'.

## app/i18n/locales/de.json
```json
{
  "admin.action": "Aktion",
  "admin.category_distinct_count": "Anzahl eindeutiger Kategorien",
  "admin.category_stats_title": "Kategorien-Status",
  "admin.category_top": "Top 10 Kategorien",
  "admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortsetzen', um den Import zu starten.",
  "admin.creator": "Ersteller",
  "admin.csv_path": "CSV-Pfad",
  "admin.download_example": "CSV Beispiel herunterladen",
  "admin.download_template": "CSV Template herunterladen",
  "admin.dry_run": "Nur pruefen (Dry Run)",
  "admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",
  "admin.email": "E-Mail",
  "admin.force_with_warnings": "Trotz Warnungen fortsetzen",
  "admin.id": "ID",
  "admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften Zeilen.",
  "admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",
  "admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' (',' als Fallback)",
  "admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import stabil und ohne Duplikate laeuft.",
  "admin.import_help_title": "CSV-Format Hilfe",
  "admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise Salz oder JSON-Liste",
  "admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty, prep_time_minutes, servings_text, ingredients, image_url, source_uuid",
  "admin.import_required_columns": "Pflichtspalten: title, instructions",
  "admin.import_result_title": "Import-Ergebnis",
  "admin.import_title": "CSV manuell importieren",
  "admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren, wenn bewusst gewuenscht.",
  "admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",
  "admin.preview_button": "Vorschau erstellen",
  "admin.preview_delimiter": "Erkannter Delimiter",
  "admin.preview_done": "Vorschau wurde erstellt.",
  "admin.preview_errors_title": "Fehlerliste",
  "admin.preview_fatal_rows": "Zeilen mit Fehlern",
  "admin.preview_notes": "Hinweise",
  "admin.preview_row": "Zeile",
  "admin.preview_status": "Status",
  "admin.preview_title": "Import-Vorschau",
  "admin.preview_total_rows": "Gesamtzeilen",
  "admin.preview_warnings_title": "Warnungsliste",
  "admin.recipes": "Rezepte",
  "admin.report_errors": "Fehler",
  "admin.report_inserted": "Neu",
  "admin.report_skipped": "Uebersprungen",
  "admin.report_updated": "Aktualisiert",
  "admin.report_warnings": "Warnungen",
  "admin.role": "Rolle",
  "admin.save": "Speichern",
  "admin.seed_done": "Seed-Status: bereits ausgefuehrt.",
  "admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",
  "admin.seed_title": "KochWiki-Seed (einmalig)",
  "admin.source": "Quelle",
  "admin.start_import": "Import starten",
  "admin.title": "Admin-Bereich",
  "admin.title_column": "Titel",
  "admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",
  "admin.upload_label": "CSV-Upload",
  "admin.users": "Nutzer",
  "app.name": "MealMate",
  "auth.email": "E-Mail",
  "auth.login": "Anmelden",
  "auth.login_button": "Anmelden",
  "auth.login_title": "Anmelden",
  "auth.password": "Passwort",
  "auth.register": "Konto erstellen",
  "auth.register_button": "Konto erstellen",
  "auth.register_title": "Registrieren",
  "difficulty.easy": "Einfach",
  "difficulty.hard": "Schwer",
  "difficulty.medium": "Mittel",
  "discover.filter.apply": "Anwenden",
  "discover.filter.category": "Kategorie",
  "discover.filter.difficulty": "Schwierigkeit",
  "discover.filter.ingredient": "Zutat",
  "discover.filter.title_contains": "Titel enthaelt",
  "discover.sort.newest": "Neueste",
  "discover.sort.oldest": "Aelteste",
  "discover.sort.prep_time": "Zubereitungszeit",
  "discover.sort.rating_asc": "Schlechteste Bewertung",
  "discover.sort.rating_desc": "Beste Bewertung",
  "discover.title": "Rezepte entdecken",
  "empty.no_recipes": "Keine Rezepte gefunden.",
  "error.404_text": "Die angeforderte Seite existiert nicht oder wurde verschoben.",
  "error.404_title": "404 - Seite nicht gefunden",
  "error.500_text": "Beim Verarbeiten der Anfrage ist ein unerwarteter Fehler aufgetreten.",
  "error.500_title": "500 - Interner Fehler",
  "error.admin_required": "Administratorrechte erforderlich.",
  "error.auth_required": "Anmeldung erforderlich.",
  "error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",
  "error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",
  "error.csv_not_found_prefix": "CSV-Datei nicht gefunden",
  "error.csv_only": "Es sind nur CSV-Uploads erlaubt.",
  "error.csv_too_large": "CSV-Upload ist zu gross.",
  "error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",
  "error.email_registered": "Diese E-Mail ist bereits registriert.",
  "error.field_int": "{field} muss eine ganze Zahl sein.",
  "error.field_positive": "{field} muss groesser als null sein.",
  "error.home_link": "Zur Startseite",
  "error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",
  "error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",
  "error.image_not_found": "Bild nicht gefunden.",
  "error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",
  "error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",
  "error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",
  "error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",
  "error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",
  "error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",
  "error.internal": "Interner Serverfehler.",
  "error.invalid_credentials": "Ungueltige Zugangsdaten.",
  "error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",
  "error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",
  "error.no_image_url": "Keine Bild-URL verfuegbar.",
  "error.not_found": "Ressource nicht gefunden.",
  "error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",
  "error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",
  "error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",
  "error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",
  "error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",
  "error.recipe_not_found": "Rezept nicht gefunden.",
  "error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",
  "error.review_not_found": "Bewertung nicht gefunden.",
  "error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",
  "error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",
  "error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",
  "error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",
  "error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",
  "error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",
  "error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",
  "error.submission_not_found": "Einreichung nicht gefunden.",
  "error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",
  "error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",
  "error.title_instructions_required": "Titel und Anleitung sind erforderlich.",
  "error.trace": "Stacktrace (nur Dev)",
  "error.user_not_found": "Nutzer nicht gefunden.",
  "error.webp_signature": "Ungueltige WEBP-Dateisignatur.",
  "favorite.add": "Zu Favoriten",
  "favorite.remove": "Aus Favoriten entfernen",
  "favorites.empty": "Keine Favoriten gespeichert.",
  "favorites.remove": "Favorit entfernen",
  "favorites.title": "Favoriten",
  "home.all_categories": "Alle Kategorien",
  "home.apply": "Anwenden",
  "home.category": "Kategorie",
  "home.difficulty": "Schwierigkeit",
  "home.ingredient": "Zutat",
  "home.per_page": "Pro Seite",
  "home.title": "Rezepte entdecken",
  "home.title_contains": "Titel enthaelt",
  "images.delete": "Loeschen",
  "images.empty": "Noch keine Bilder vorhanden.",
  "images.new_file": "Neue Bilddatei",
  "images.primary": "Hauptbild",
  "images.set_primary": "Als Hauptbild setzen",
  "images.title": "Bilder",
  "images.upload": "Bild hochladen",
  "moderation.approve": "Freigeben",
  "moderation.pending": "Ausstehend",
  "moderation.reject": "Ablehnen",
  "moderation.title": "Moderations-Warteschlange",
  "my_recipes.empty": "Noch keine Rezepte vorhanden.",
  "my_recipes.title": "Meine Rezepte",
  "nav.admin": "Admin",
  "nav.admin_submissions": "Moderation",
  "nav.create_recipe": "Rezept erstellen",
  "nav.discover": "Rezepte entdecken",
  "nav.favorites": "Favoriten",
  "nav.language": "Sprache",
  "nav.login": "Anmelden",
  "nav.logout": "Abmelden",
  "nav.my_recipes": "Meine Rezepte",
  "nav.my_submissions": "Meine Einreichungen",
  "nav.profile": "Mein Profil",
  "nav.publish_recipe": "Rezept veroeffentlichen",
  "nav.register": "Registrieren",
  "nav.submit": "Rezept einreichen",
  "nav.submit_recipe": "Rezept einreichen",
  "pagination.first": "Erste",
  "pagination.last": "Letzte",
  "pagination.next": "Weiter",
  "pagination.page": "Seite",
  "pagination.prev": "Zurueck",
  "pagination.previous": "Zurueck",
  "pagination.results_range": "Zeige {start}-{end} von {total} Rezepten",
  "profile.email": "E-Mail",
  "profile.joined": "Registriert am",
  "profile.role": "Rolle",
  "profile.title": "Mein Profil",
  "recipe.average_rating": "Durchschnittliche Bewertung",
  "recipe.comment": "Kommentar",
  "recipe.delete": "Loeschen",
  "recipe.edit": "Bearbeiten",
  "recipe.ingredients": "Zutaten",
  "recipe.instructions": "Anleitung",
  "recipe.no_ingredients": "Keine Zutaten gespeichert.",
  "recipe.no_results": "Keine Rezepte gefunden.",
  "recipe.no_reviews": "Noch keine Bewertungen vorhanden.",
  "recipe.pdf_download": "PDF herunterladen",
  "recipe.rating": "Bewertung",
  "recipe.rating_short": "Bewertung",
  "recipe.review_count_label": "Bewertungen",
  "recipe.reviews": "Bewertungen",
  "recipe.save_review": "Bewertung speichern",
  "recipe_form.category": "Kategorie",
  "recipe_form.create": "Erstellen",
  "recipe_form.create_title": "Rezept veroeffentlichen",
  "recipe_form.description": "Beschreibung",
  "recipe_form.difficulty": "Schwierigkeit",
  "recipe_form.edit_title": "Rezept bearbeiten",
  "recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",
  "recipe_form.instructions": "Anleitung",
  "recipe_form.new_category_label": "Neue Kategorie",
  "recipe_form.new_category_option": "Neue Kategorie...",
  "recipe_form.optional_image": "Optionales Bild",
  "recipe_form.prep_time": "Zubereitungszeit (Minuten)",
  "recipe_form.save": "Speichern",
  "recipe_form.title": "Titel",
  "recipe_form.title_image_url": "Titelbild-URL",
  "role.admin": "Administrator",
  "role.user": "Nutzer",
  "sort.highest_rated": "Beste Bewertung",
  "sort.lowest_rated": "Schlechteste Bewertung",
  "sort.newest": "Neueste",
  "sort.oldest": "Aelteste",
  "sort.prep_time": "Zubereitungszeit",
  "submission.admin_detail_title": "Einreichung",
  "submission.admin_empty": "Keine Einreichungen gefunden.",
  "submission.admin_note": "Admin-Notiz",
  "submission.admin_queue_link": "Zur Moderations-Warteschlange",
  "submission.admin_queue_title": "Moderations-Warteschlange",
  "submission.approve_button": "Freigeben",
  "submission.approved": "Einreichung wurde freigegeben.",
  "submission.back_to_queue": "Zurueck zur Warteschlange",
  "submission.category": "Kategorie",
  "submission.default_description": "Rezept-Einreichung",
  "submission.description": "Beschreibung",
  "submission.difficulty": "Schwierigkeit",
  "submission.edit_submission": "Einreichung bearbeiten",
  "submission.guest": "Gast",
  "submission.image_deleted": "Bild wurde entfernt.",
  "submission.image_optional": "Optionales Bild",
  "submission.image_primary": "Hauptbild wurde gesetzt.",
  "submission.ingredients": "Zutaten (Format: name|menge|gramm)",
  "submission.instructions": "Anleitung",
  "submission.moderation_actions": "Moderations-Aktionen",
  "submission.my_empty": "Du hast noch keine Einreichungen.",
  "submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",
  "submission.my_title": "Meine Einreichungen",
  "submission.new_category_label": "Neue Kategorie",
  "submission.new_category_option": "Neue Kategorie...",
  "submission.open_detail": "Details",
  "submission.optional_admin_note": "Admin-Notiz (optional)",
  "submission.prep_time": "Zubereitungszeit (Minuten, optional)",
  "submission.preview": "Vorschau",
  "submission.reject_button": "Ablehnen",
  "submission.reject_reason": "Ablehnungsgrund",
  "submission.rejected": "Einreichung wurde abgelehnt.",
  "submission.save_changes": "Aenderungen speichern",
  "submission.servings": "Portionen (optional)",
  "submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",
  "submission.stats_approved": "Freigegeben",
  "submission.stats_pending": "Ausstehend",
  "submission.stats_rejected": "Abgelehnt",
  "submission.status_all": "Alle",
  "submission.status_approved": "Freigegeben",
  "submission.status_filter": "Status",
  "submission.status_pending": "Ausstehend",
  "submission.status_rejected": "Abgelehnt",
  "submission.submit_button": "Zur Pruefung einreichen",
  "submission.submit_hint": "Einreichungen werden vor der Veroeffentlichung durch das Admin-Team geprueft.",
  "submission.submit_title": "Rezept einreichen",
  "submission.submitter_email": "Kontakt-E-Mail (optional)",
  "submission.table_action": "Aktion",
  "submission.table_date": "Datum",
  "submission.table_status": "Status",
  "submission.table_submitter": "Einreicher",
  "submission.table_title": "Titel",
  "submission.thank_you": "Vielen Dank! Dein Rezept wurde eingereicht und wird geprueft.",
  "submission.title": "Titel",
  "submission.updated": "Einreichung wurde aktualisiert."
}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '{'.
2. Diese Zeile definiert den Abschnitt '"admin.action": "Aktion",'.
3. Diese Zeile definiert den Abschnitt '"admin.category_distinct_count": "Anzahl eindeutiger Kategorien",'.
4. Diese Zeile definiert den Abschnitt '"admin.category_stats_title": "Kategorien-Status",'.
5. Diese Zeile definiert den Abschnitt '"admin.category_top": "Top 10 Kategorien",'.
6. Diese Zeile definiert den Abschnitt '"admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortset...'.
7. Diese Zeile definiert den Abschnitt '"admin.creator": "Ersteller",'.
8. Diese Zeile definiert den Abschnitt '"admin.csv_path": "CSV-Pfad",'.
9. Diese Zeile definiert den Abschnitt '"admin.download_example": "CSV Beispiel herunterladen",'.
10. Diese Zeile definiert den Abschnitt '"admin.download_template": "CSV Template herunterladen",'.
11. Diese Zeile definiert den Abschnitt '"admin.dry_run": "Nur pruefen (Dry Run)",'.
12. Diese Zeile definiert den Abschnitt '"admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",'.
13. Diese Zeile definiert den Abschnitt '"admin.email": "E-Mail",'.
14. Diese Zeile definiert den Abschnitt '"admin.force_with_warnings": "Trotz Warnungen fortsetzen",'.
15. Diese Zeile definiert den Abschnitt '"admin.id": "ID",'.
16. Diese Zeile definiert den Abschnitt '"admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften ...'.
17. Diese Zeile definiert den Abschnitt '"admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",'.
18. Diese Zeile definiert den Abschnitt '"admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' ...'.
19. Diese Zeile definiert den Abschnitt '"admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import s...'.
20. Diese Zeile definiert den Abschnitt '"admin.import_help_title": "CSV-Format Hilfe",'.
21. Diese Zeile definiert den Abschnitt '"admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise...'.
22. Diese Zeile definiert den Abschnitt '"admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty...'.
23. Diese Zeile definiert den Abschnitt '"admin.import_required_columns": "Pflichtspalten: title, instructions",'.
24. Diese Zeile definiert den Abschnitt '"admin.import_result_title": "Import-Ergebnis",'.
25. Diese Zeile definiert den Abschnitt '"admin.import_title": "CSV manuell importieren",'.
26. Diese Zeile definiert den Abschnitt '"admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren,...'.
27. Diese Zeile definiert den Abschnitt '"admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",'.
28. Diese Zeile definiert den Abschnitt '"admin.preview_button": "Vorschau erstellen",'.
29. Diese Zeile definiert den Abschnitt '"admin.preview_delimiter": "Erkannter Delimiter",'.
30. Diese Zeile definiert den Abschnitt '"admin.preview_done": "Vorschau wurde erstellt.",'.
31. Diese Zeile definiert den Abschnitt '"admin.preview_errors_title": "Fehlerliste",'.
32. Diese Zeile definiert den Abschnitt '"admin.preview_fatal_rows": "Zeilen mit Fehlern",'.
33. Diese Zeile definiert den Abschnitt '"admin.preview_notes": "Hinweise",'.
34. Diese Zeile definiert den Abschnitt '"admin.preview_row": "Zeile",'.
35. Diese Zeile definiert den Abschnitt '"admin.preview_status": "Status",'.
36. Diese Zeile definiert den Abschnitt '"admin.preview_title": "Import-Vorschau",'.
37. Diese Zeile definiert den Abschnitt '"admin.preview_total_rows": "Gesamtzeilen",'.
38. Diese Zeile definiert den Abschnitt '"admin.preview_warnings_title": "Warnungsliste",'.
39. Diese Zeile definiert den Abschnitt '"admin.recipes": "Rezepte",'.
40. Diese Zeile definiert den Abschnitt '"admin.report_errors": "Fehler",'.
41. Diese Zeile definiert den Abschnitt '"admin.report_inserted": "Neu",'.
42. Diese Zeile definiert den Abschnitt '"admin.report_skipped": "Uebersprungen",'.
43. Diese Zeile definiert den Abschnitt '"admin.report_updated": "Aktualisiert",'.
44. Diese Zeile definiert den Abschnitt '"admin.report_warnings": "Warnungen",'.
45. Diese Zeile definiert den Abschnitt '"admin.role": "Rolle",'.
46. Diese Zeile definiert den Abschnitt '"admin.save": "Speichern",'.
47. Diese Zeile definiert den Abschnitt '"admin.seed_done": "Seed-Status: bereits ausgefuehrt.",'.
48. Diese Zeile definiert den Abschnitt '"admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",'.
49. Diese Zeile definiert den Abschnitt '"admin.seed_title": "KochWiki-Seed (einmalig)",'.
50. Diese Zeile definiert den Abschnitt '"admin.source": "Quelle",'.
51. Diese Zeile definiert den Abschnitt '"admin.start_import": "Import starten",'.
52. Diese Zeile definiert den Abschnitt '"admin.title": "Admin-Bereich",'.
53. Diese Zeile definiert den Abschnitt '"admin.title_column": "Titel",'.
54. Diese Zeile definiert den Abschnitt '"admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",'.
55. Diese Zeile definiert den Abschnitt '"admin.upload_label": "CSV-Upload",'.
56. Diese Zeile definiert den Abschnitt '"admin.users": "Nutzer",'.
57. Diese Zeile definiert den Abschnitt '"app.name": "MealMate",'.
58. Diese Zeile definiert den Abschnitt '"auth.email": "E-Mail",'.
59. Diese Zeile definiert den Abschnitt '"auth.login": "Anmelden",'.
60. Diese Zeile definiert den Abschnitt '"auth.login_button": "Anmelden",'.
61. Diese Zeile definiert den Abschnitt '"auth.login_title": "Anmelden",'.
62. Diese Zeile definiert den Abschnitt '"auth.password": "Passwort",'.
63. Diese Zeile definiert den Abschnitt '"auth.register": "Konto erstellen",'.
64. Diese Zeile definiert den Abschnitt '"auth.register_button": "Konto erstellen",'.
65. Diese Zeile definiert den Abschnitt '"auth.register_title": "Registrieren",'.
66. Diese Zeile definiert den Abschnitt '"difficulty.easy": "Einfach",'.
67. Diese Zeile definiert den Abschnitt '"difficulty.hard": "Schwer",'.
68. Diese Zeile definiert den Abschnitt '"difficulty.medium": "Mittel",'.
69. Diese Zeile definiert den Abschnitt '"discover.filter.apply": "Anwenden",'.
70. Diese Zeile definiert den Abschnitt '"discover.filter.category": "Kategorie",'.
71. Diese Zeile definiert den Abschnitt '"discover.filter.difficulty": "Schwierigkeit",'.
72. Diese Zeile definiert den Abschnitt '"discover.filter.ingredient": "Zutat",'.
73. Diese Zeile definiert den Abschnitt '"discover.filter.title_contains": "Titel enthaelt",'.
74. Diese Zeile definiert den Abschnitt '"discover.sort.newest": "Neueste",'.
75. Diese Zeile definiert den Abschnitt '"discover.sort.oldest": "Aelteste",'.
76. Diese Zeile definiert den Abschnitt '"discover.sort.prep_time": "Zubereitungszeit",'.
77. Diese Zeile definiert den Abschnitt '"discover.sort.rating_asc": "Schlechteste Bewertung",'.
78. Diese Zeile definiert den Abschnitt '"discover.sort.rating_desc": "Beste Bewertung",'.
79. Diese Zeile definiert den Abschnitt '"discover.title": "Rezepte entdecken",'.
80. Diese Zeile definiert den Abschnitt '"empty.no_recipes": "Keine Rezepte gefunden.",'.
81. Diese Zeile definiert den Abschnitt '"error.404_text": "Die angeforderte Seite existiert nicht oder wurde verschoben.",'.
82. Diese Zeile definiert den Abschnitt '"error.404_title": "404 - Seite nicht gefunden",'.
83. Diese Zeile definiert den Abschnitt '"error.500_text": "Beim Verarbeiten der Anfrage ist ein unerwarteter Fehler aufgetreten.",'.
84. Diese Zeile definiert den Abschnitt '"error.500_title": "500 - Interner Fehler",'.
85. Diese Zeile definiert den Abschnitt '"error.admin_required": "Administratorrechte erforderlich.",'.
86. Diese Zeile definiert den Abschnitt '"error.auth_required": "Anmeldung erforderlich.",'.
87. Diese Zeile definiert den Abschnitt '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
88. Diese Zeile definiert den Abschnitt '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
89. Diese Zeile definiert den Abschnitt '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
90. Diese Zeile definiert den Abschnitt '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
91. Diese Zeile definiert den Abschnitt '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
92. Diese Zeile definiert den Abschnitt '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
93. Diese Zeile definiert den Abschnitt '"error.email_registered": "Diese E-Mail ist bereits registriert.",'.
94. Diese Zeile definiert den Abschnitt '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
95. Diese Zeile definiert den Abschnitt '"error.field_positive": "{field} muss groesser als null sein.",'.
96. Diese Zeile definiert den Abschnitt '"error.home_link": "Zur Startseite",'.
97. Diese Zeile definiert den Abschnitt '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
98. Diese Zeile definiert den Abschnitt '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
99. Diese Zeile definiert den Abschnitt '"error.image_not_found": "Bild nicht gefunden.",'.
100. Diese Zeile definiert den Abschnitt '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
101. Diese Zeile definiert den Abschnitt '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
102. Diese Zeile definiert den Abschnitt '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
103. Diese Zeile definiert den Abschnitt '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
104. Diese Zeile definiert den Abschnitt '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
105. Diese Zeile definiert den Abschnitt '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschloss...'.
106. Diese Zeile definiert den Abschnitt '"error.internal": "Interner Serverfehler.",'.
107. Diese Zeile definiert den Abschnitt '"error.invalid_credentials": "Ungueltige Zugangsdaten.",'.
108. Diese Zeile definiert den Abschnitt '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
109. Diese Zeile definiert den Abschnitt '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
110. Diese Zeile definiert den Abschnitt '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
111. Diese Zeile definiert den Abschnitt '"error.not_found": "Ressource nicht gefunden.",'.
112. Diese Zeile definiert den Abschnitt '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
113. Diese Zeile definiert den Abschnitt '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
114. Diese Zeile definiert den Abschnitt '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
115. Diese Zeile definiert den Abschnitt '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
116. Diese Zeile definiert den Abschnitt '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
117. Diese Zeile definiert den Abschnitt '"error.recipe_not_found": "Rezept nicht gefunden.",'.
118. Diese Zeile definiert den Abschnitt '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
119. Diese Zeile definiert den Abschnitt '"error.review_not_found": "Bewertung nicht gefunden.",'.
120. Diese Zeile definiert den Abschnitt '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
121. Diese Zeile definiert den Abschnitt '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
122. Diese Zeile definiert den Abschnitt '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
123. Diese Zeile definiert den Abschnitt '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht g...'.
124. Diese Zeile definiert den Abschnitt '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
125. Diese Zeile definiert den Abschnitt '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
126. Diese Zeile definiert den Abschnitt '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
127. Diese Zeile definiert den Abschnitt '"error.submission_not_found": "Einreichung nicht gefunden.",'.
128. Diese Zeile definiert den Abschnitt '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
129. Diese Zeile definiert den Abschnitt '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
130. Diese Zeile definiert den Abschnitt '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
131. Diese Zeile definiert den Abschnitt '"error.trace": "Stacktrace (nur Dev)",'.
132. Diese Zeile definiert den Abschnitt '"error.user_not_found": "Nutzer nicht gefunden.",'.
133. Diese Zeile definiert den Abschnitt '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
134. Diese Zeile definiert den Abschnitt '"favorite.add": "Zu Favoriten",'.
135. Diese Zeile definiert den Abschnitt '"favorite.remove": "Aus Favoriten entfernen",'.
136. Diese Zeile definiert den Abschnitt '"favorites.empty": "Keine Favoriten gespeichert.",'.
137. Diese Zeile definiert den Abschnitt '"favorites.remove": "Favorit entfernen",'.
138. Diese Zeile definiert den Abschnitt '"favorites.title": "Favoriten",'.
139. Diese Zeile definiert den Abschnitt '"home.all_categories": "Alle Kategorien",'.
140. Diese Zeile definiert den Abschnitt '"home.apply": "Anwenden",'.
141. Diese Zeile definiert den Abschnitt '"home.category": "Kategorie",'.
142. Diese Zeile definiert den Abschnitt '"home.difficulty": "Schwierigkeit",'.
143. Diese Zeile definiert den Abschnitt '"home.ingredient": "Zutat",'.
144. Diese Zeile definiert den Abschnitt '"home.per_page": "Pro Seite",'.
145. Diese Zeile definiert den Abschnitt '"home.title": "Rezepte entdecken",'.
146. Diese Zeile definiert den Abschnitt '"home.title_contains": "Titel enthaelt",'.
147. Diese Zeile definiert den Abschnitt '"images.delete": "Loeschen",'.
148. Diese Zeile definiert den Abschnitt '"images.empty": "Noch keine Bilder vorhanden.",'.
149. Diese Zeile definiert den Abschnitt '"images.new_file": "Neue Bilddatei",'.
150. Diese Zeile definiert den Abschnitt '"images.primary": "Hauptbild",'.
151. Diese Zeile definiert den Abschnitt '"images.set_primary": "Als Hauptbild setzen",'.
152. Diese Zeile definiert den Abschnitt '"images.title": "Bilder",'.
153. Diese Zeile definiert den Abschnitt '"images.upload": "Bild hochladen",'.
154. Diese Zeile definiert den Abschnitt '"moderation.approve": "Freigeben",'.
155. Diese Zeile definiert den Abschnitt '"moderation.pending": "Ausstehend",'.
156. Diese Zeile definiert den Abschnitt '"moderation.reject": "Ablehnen",'.
157. Diese Zeile definiert den Abschnitt '"moderation.title": "Moderations-Warteschlange",'.
158. Diese Zeile definiert den Abschnitt '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
159. Diese Zeile definiert den Abschnitt '"my_recipes.title": "Meine Rezepte",'.
160. Diese Zeile definiert den Abschnitt '"nav.admin": "Admin",'.
161. Diese Zeile definiert den Abschnitt '"nav.admin_submissions": "Moderation",'.
162. Diese Zeile definiert den Abschnitt '"nav.create_recipe": "Rezept erstellen",'.
163. Diese Zeile definiert den Abschnitt '"nav.discover": "Rezepte entdecken",'.
164. Diese Zeile definiert den Abschnitt '"nav.favorites": "Favoriten",'.
165. Diese Zeile definiert den Abschnitt '"nav.language": "Sprache",'.
166. Diese Zeile definiert den Abschnitt '"nav.login": "Anmelden",'.
167. Diese Zeile definiert den Abschnitt '"nav.logout": "Abmelden",'.
168. Diese Zeile definiert den Abschnitt '"nav.my_recipes": "Meine Rezepte",'.
169. Diese Zeile definiert den Abschnitt '"nav.my_submissions": "Meine Einreichungen",'.
170. Diese Zeile definiert den Abschnitt '"nav.profile": "Mein Profil",'.
171. Diese Zeile definiert den Abschnitt '"nav.publish_recipe": "Rezept veroeffentlichen",'.
172. Diese Zeile definiert den Abschnitt '"nav.register": "Registrieren",'.
173. Diese Zeile definiert den Abschnitt '"nav.submit": "Rezept einreichen",'.
174. Diese Zeile definiert den Abschnitt '"nav.submit_recipe": "Rezept einreichen",'.
175. Diese Zeile definiert den Abschnitt '"pagination.first": "Erste",'.
176. Diese Zeile definiert den Abschnitt '"pagination.last": "Letzte",'.
177. Diese Zeile definiert den Abschnitt '"pagination.next": "Weiter",'.
178. Diese Zeile definiert den Abschnitt '"pagination.page": "Seite",'.
179. Diese Zeile definiert den Abschnitt '"pagination.prev": "Zurueck",'.
180. Diese Zeile definiert den Abschnitt '"pagination.previous": "Zurueck",'.
181. Diese Zeile definiert den Abschnitt '"pagination.results_range": "Zeige {start}-{end} von {total} Rezepten",'.
182. Diese Zeile definiert den Abschnitt '"profile.email": "E-Mail",'.
183. Diese Zeile definiert den Abschnitt '"profile.joined": "Registriert am",'.
184. Diese Zeile definiert den Abschnitt '"profile.role": "Rolle",'.
185. Diese Zeile definiert den Abschnitt '"profile.title": "Mein Profil",'.
186. Diese Zeile definiert den Abschnitt '"recipe.average_rating": "Durchschnittliche Bewertung",'.
187. Diese Zeile definiert den Abschnitt '"recipe.comment": "Kommentar",'.
188. Diese Zeile definiert den Abschnitt '"recipe.delete": "Loeschen",'.
189. Diese Zeile definiert den Abschnitt '"recipe.edit": "Bearbeiten",'.
190. Diese Zeile definiert den Abschnitt '"recipe.ingredients": "Zutaten",'.
191. Diese Zeile definiert den Abschnitt '"recipe.instructions": "Anleitung",'.
192. Diese Zeile definiert den Abschnitt '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
193. Diese Zeile definiert den Abschnitt '"recipe.no_results": "Keine Rezepte gefunden.",'.
194. Diese Zeile definiert den Abschnitt '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
195. Diese Zeile definiert den Abschnitt '"recipe.pdf_download": "PDF herunterladen",'.
196. Diese Zeile definiert den Abschnitt '"recipe.rating": "Bewertung",'.
197. Diese Zeile definiert den Abschnitt '"recipe.rating_short": "Bewertung",'.
198. Diese Zeile definiert den Abschnitt '"recipe.review_count_label": "Bewertungen",'.
199. Diese Zeile definiert den Abschnitt '"recipe.reviews": "Bewertungen",'.
200. Diese Zeile definiert den Abschnitt '"recipe.save_review": "Bewertung speichern",'.
201. Diese Zeile definiert den Abschnitt '"recipe_form.category": "Kategorie",'.
202. Diese Zeile definiert den Abschnitt '"recipe_form.create": "Erstellen",'.
203. Diese Zeile definiert den Abschnitt '"recipe_form.create_title": "Rezept veroeffentlichen",'.
204. Diese Zeile definiert den Abschnitt '"recipe_form.description": "Beschreibung",'.
205. Diese Zeile definiert den Abschnitt '"recipe_form.difficulty": "Schwierigkeit",'.
206. Diese Zeile definiert den Abschnitt '"recipe_form.edit_title": "Rezept bearbeiten",'.
207. Diese Zeile definiert den Abschnitt '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
208. Diese Zeile definiert den Abschnitt '"recipe_form.instructions": "Anleitung",'.
209. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_label": "Neue Kategorie",'.
210. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_option": "Neue Kategorie...",'.
211. Diese Zeile definiert den Abschnitt '"recipe_form.optional_image": "Optionales Bild",'.
212. Diese Zeile definiert den Abschnitt '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
213. Diese Zeile definiert den Abschnitt '"recipe_form.save": "Speichern",'.
214. Diese Zeile definiert den Abschnitt '"recipe_form.title": "Titel",'.
215. Diese Zeile definiert den Abschnitt '"recipe_form.title_image_url": "Titelbild-URL",'.
216. Diese Zeile definiert den Abschnitt '"role.admin": "Administrator",'.
217. Diese Zeile definiert den Abschnitt '"role.user": "Nutzer",'.
218. Diese Zeile definiert den Abschnitt '"sort.highest_rated": "Beste Bewertung",'.
219. Diese Zeile definiert den Abschnitt '"sort.lowest_rated": "Schlechteste Bewertung",'.
220. Diese Zeile definiert den Abschnitt '"sort.newest": "Neueste",'.
221. Diese Zeile definiert den Abschnitt '"sort.oldest": "Aelteste",'.
222. Diese Zeile definiert den Abschnitt '"sort.prep_time": "Zubereitungszeit",'.
223. Diese Zeile definiert den Abschnitt '"submission.admin_detail_title": "Einreichung",'.
224. Diese Zeile definiert den Abschnitt '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
225. Diese Zeile definiert den Abschnitt '"submission.admin_note": "Admin-Notiz",'.
226. Diese Zeile definiert den Abschnitt '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
227. Diese Zeile definiert den Abschnitt '"submission.admin_queue_title": "Moderations-Warteschlange",'.
228. Diese Zeile definiert den Abschnitt '"submission.approve_button": "Freigeben",'.
229. Diese Zeile definiert den Abschnitt '"submission.approved": "Einreichung wurde freigegeben.",'.
230. Diese Zeile definiert den Abschnitt '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
231. Diese Zeile definiert den Abschnitt '"submission.category": "Kategorie",'.
232. Diese Zeile definiert den Abschnitt '"submission.default_description": "Rezept-Einreichung",'.
233. Diese Zeile definiert den Abschnitt '"submission.description": "Beschreibung",'.
234. Diese Zeile definiert den Abschnitt '"submission.difficulty": "Schwierigkeit",'.
235. Diese Zeile definiert den Abschnitt '"submission.edit_submission": "Einreichung bearbeiten",'.
236. Diese Zeile definiert den Abschnitt '"submission.guest": "Gast",'.
237. Diese Zeile definiert den Abschnitt '"submission.image_deleted": "Bild wurde entfernt.",'.
238. Diese Zeile definiert den Abschnitt '"submission.image_optional": "Optionales Bild",'.
239. Diese Zeile definiert den Abschnitt '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
240. Diese Zeile definiert den Abschnitt '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
241. Diese Zeile definiert den Abschnitt '"submission.instructions": "Anleitung",'.
242. Diese Zeile definiert den Abschnitt '"submission.moderation_actions": "Moderations-Aktionen",'.
243. Diese Zeile definiert den Abschnitt '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
244. Diese Zeile definiert den Abschnitt '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf ...'.
245. Diese Zeile definiert den Abschnitt '"submission.my_title": "Meine Einreichungen",'.
246. Diese Zeile definiert den Abschnitt '"submission.new_category_label": "Neue Kategorie",'.
247. Diese Zeile definiert den Abschnitt '"submission.new_category_option": "Neue Kategorie...",'.
248. Diese Zeile definiert den Abschnitt '"submission.open_detail": "Details",'.
249. Diese Zeile definiert den Abschnitt '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
250. Diese Zeile definiert den Abschnitt '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
251. Diese Zeile definiert den Abschnitt '"submission.preview": "Vorschau",'.
252. Diese Zeile definiert den Abschnitt '"submission.reject_button": "Ablehnen",'.
253. Diese Zeile definiert den Abschnitt '"submission.reject_reason": "Ablehnungsgrund",'.
254. Diese Zeile definiert den Abschnitt '"submission.rejected": "Einreichung wurde abgelehnt.",'.
255. Diese Zeile definiert den Abschnitt '"submission.save_changes": "Aenderungen speichern",'.
256. Diese Zeile definiert den Abschnitt '"submission.servings": "Portionen (optional)",'.
257. Diese Zeile definiert den Abschnitt '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
258. Diese Zeile definiert den Abschnitt '"submission.stats_approved": "Freigegeben",'.
259. Diese Zeile definiert den Abschnitt '"submission.stats_pending": "Ausstehend",'.
260. Diese Zeile definiert den Abschnitt '"submission.stats_rejected": "Abgelehnt",'.
261. Diese Zeile definiert den Abschnitt '"submission.status_all": "Alle",'.
262. Diese Zeile definiert den Abschnitt '"submission.status_approved": "Freigegeben",'.
263. Diese Zeile definiert den Abschnitt '"submission.status_filter": "Status",'.
264. Diese Zeile definiert den Abschnitt '"submission.status_pending": "Ausstehend",'.
265. Diese Zeile definiert den Abschnitt '"submission.status_rejected": "Abgelehnt",'.
266. Diese Zeile definiert den Abschnitt '"submission.submit_button": "Zur Pruefung einreichen",'.
267. Diese Zeile definiert den Abschnitt '"submission.submit_hint": "Einreichungen werden vor der Veroeffentlichung durch das Adm...'.
268. Diese Zeile definiert den Abschnitt '"submission.submit_title": "Rezept einreichen",'.
269. Diese Zeile definiert den Abschnitt '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
270. Diese Zeile definiert den Abschnitt '"submission.table_action": "Aktion",'.
271. Diese Zeile definiert den Abschnitt '"submission.table_date": "Datum",'.
272. Diese Zeile definiert den Abschnitt '"submission.table_status": "Status",'.
273. Diese Zeile definiert den Abschnitt '"submission.table_submitter": "Einreicher",'.
274. Diese Zeile definiert den Abschnitt '"submission.table_title": "Titel",'.
275. Diese Zeile definiert den Abschnitt '"submission.thank_you": "Vielen Dank! Dein Rezept wurde eingereicht und wird geprueft.",'.
276. Diese Zeile definiert den Abschnitt '"submission.title": "Titel",'.
277. Diese Zeile definiert den Abschnitt '"submission.updated": "Einreichung wurde aktualisiert."'.
278. Diese Zeile definiert den Abschnitt '}'.

## app/i18n/locales/en.json
```json
{
  "admin.action": "Aktion",
  "admin.category_distinct_count": "Anzahl eindeutiger Kategorien",
  "admin.category_stats_title": "Kategorien-Status",
  "admin.category_top": "Top 10 Kategorien",
  "admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortsetzen', um den Import zu starten.",
  "admin.creator": "Ersteller",
  "admin.csv_path": "CSV-Pfad",
  "admin.download_example": "CSV Beispiel herunterladen",
  "admin.download_template": "CSV Template herunterladen",
  "admin.dry_run": "Nur pruefen (Dry Run)",
  "admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",
  "admin.email": "E-Mail",
  "admin.force_with_warnings": "Trotz Warnungen fortsetzen",
  "admin.id": "ID",
  "admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften Zeilen.",
  "admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",
  "admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' (',' als Fallback)",
  "admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import stabil und ohne Duplikate laeuft.",
  "admin.import_help_title": "CSV-Format Hilfe",
  "admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise Salz oder JSON-Liste",
  "admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty, prep_time_minutes, servings_text, ingredients, image_url, source_uuid",
  "admin.import_required_columns": "Pflichtspalten: title, instructions",
  "admin.import_result_title": "Import-Ergebnis",
  "admin.import_title": "Manual CSV Import",
  "admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren, wenn bewusst gewuenscht.",
  "admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",
  "admin.preview_button": "Vorschau erstellen",
  "admin.preview_delimiter": "Erkannter Delimiter",
  "admin.preview_done": "Vorschau wurde erstellt.",
  "admin.preview_errors_title": "Fehlerliste",
  "admin.preview_fatal_rows": "Zeilen mit Fehlern",
  "admin.preview_notes": "Hinweise",
  "admin.preview_row": "Zeile",
  "admin.preview_status": "Status",
  "admin.preview_title": "Import-Vorschau",
  "admin.preview_total_rows": "Gesamtzeilen",
  "admin.preview_warnings_title": "Warnungsliste",
  "admin.recipes": "Rezepte",
  "admin.report_errors": "Fehler",
  "admin.report_inserted": "Neu",
  "admin.report_skipped": "Uebersprungen",
  "admin.report_updated": "Aktualisiert",
  "admin.report_warnings": "Warnungen",
  "admin.role": "Rolle",
  "admin.save": "Speichern",
  "admin.seed_done": "Seed-Status: bereits ausgefuehrt.",
  "admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",
  "admin.seed_title": "KochWiki-Seed (einmalig)",
  "admin.source": "Quelle",
  "admin.start_import": "Import starten",
  "admin.title": "Admin Area",
  "admin.title_column": "Titel",
  "admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",
  "admin.upload_label": "CSV-Upload",
  "admin.users": "Nutzer",
  "app.name": "MealMate",
  "auth.email": "Email",
  "auth.login": "Login",
  "auth.login_button": "Login",
  "auth.login_title": "Login",
  "auth.password": "Password",
  "auth.register": "Register",
  "auth.register_button": "Create account",
  "auth.register_title": "Register",
  "difficulty.easy": "Easy",
  "difficulty.hard": "Hard",
  "difficulty.medium": "Medium",
  "discover.filter.apply": "Apply",
  "discover.filter.category": "Category",
  "discover.filter.difficulty": "Difficulty",
  "discover.filter.ingredient": "Ingredient",
  "discover.filter.title_contains": "Title contains",
  "discover.sort.newest": "Newest",
  "discover.sort.oldest": "Oldest",
  "discover.sort.prep_time": "Prep time",
  "discover.sort.rating_asc": "Lowest rated",
  "discover.sort.rating_desc": "Highest rated",
  "discover.title": "Discover Recipes",
  "empty.no_recipes": "No recipes found.",
  "error.404_text": "The requested page does not exist or has been moved.",
  "error.404_title": "404 - Page Not Found",
  "error.500_text": "An unexpected error occurred while processing the request.",
  "error.500_title": "500 - Internal Error",
  "error.admin_required": "Admin role required.",
  "error.auth_required": "Authentication required.",
  "error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",
  "error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",
  "error.csv_not_found_prefix": "CSV-Datei nicht gefunden",
  "error.csv_only": "Es sind nur CSV-Uploads erlaubt.",
  "error.csv_too_large": "CSV-Upload ist zu gross.",
  "error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",
  "error.email_registered": "This email is already registered.",
  "error.field_int": "{field} muss eine ganze Zahl sein.",
  "error.field_positive": "{field} muss groesser als null sein.",
  "error.home_link": "Back to Home",
  "error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",
  "error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",
  "error.image_not_found": "Bild nicht gefunden.",
  "error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",
  "error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",
  "error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",
  "error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",
  "error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",
  "error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",
  "error.internal": "Interner Serverfehler.",
  "error.invalid_credentials": "Invalid credentials.",
  "error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",
  "error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",
  "error.no_image_url": "Keine Bild-URL verfuegbar.",
  "error.not_found": "Ressource nicht gefunden.",
  "error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",
  "error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",
  "error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",
  "error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",
  "error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",
  "error.recipe_not_found": "Rezept nicht gefunden.",
  "error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",
  "error.review_not_found": "Bewertung nicht gefunden.",
  "error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",
  "error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",
  "error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",
  "error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",
  "error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",
  "error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",
  "error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",
  "error.submission_not_found": "Einreichung nicht gefunden.",
  "error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",
  "error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",
  "error.title_instructions_required": "Titel und Anleitung sind erforderlich.",
  "error.trace": "Stacktrace (nur Dev)",
  "error.user_not_found": "Nutzer nicht gefunden.",
  "error.webp_signature": "Ungueltige WEBP-Dateisignatur.",
  "favorite.add": "Zu Favoriten",
  "favorite.remove": "Aus Favoriten entfernen",
  "favorites.empty": "Keine Favoriten gespeichert.",
  "favorites.remove": "Favorit entfernen",
  "favorites.title": "Favoriten",
  "home.all_categories": "All categories",
  "home.apply": "Apply",
  "home.category": "Category",
  "home.difficulty": "Difficulty",
  "home.ingredient": "Ingredient",
  "home.per_page": "Per page",
  "home.title": "Discover Recipes",
  "home.title_contains": "Title contains",
  "images.delete": "Loeschen",
  "images.empty": "Noch keine Bilder vorhanden.",
  "images.new_file": "Neue Bilddatei",
  "images.primary": "Hauptbild",
  "images.set_primary": "Als Hauptbild setzen",
  "images.title": "Bilder",
  "images.upload": "Bild hochladen",
  "moderation.approve": "Approve",
  "moderation.pending": "Pending",
  "moderation.reject": "Reject",
  "moderation.title": "Moderation Queue",
  "my_recipes.empty": "Noch keine Rezepte vorhanden.",
  "my_recipes.title": "Meine Rezepte",
  "nav.admin": "Admin",
  "nav.admin_submissions": "Moderation",
  "nav.create_recipe": "Create Recipe",
  "nav.discover": "Discover Recipes",
  "nav.favorites": "Favorites",
  "nav.language": "Language",
  "nav.login": "Login",
  "nav.logout": "Logout",
  "nav.my_recipes": "My Recipes",
  "nav.my_submissions": "My Submissions",
  "nav.profile": "My Profile",
  "nav.publish_recipe": "Publish Recipe",
  "nav.register": "Register",
  "nav.submit": "Submit Recipe",
  "nav.submit_recipe": "Submit Recipe",
  "pagination.first": "First",
  "pagination.last": "Last",
  "pagination.next": "Next",
  "pagination.page": "Page",
  "pagination.prev": "Previous",
  "pagination.previous": "Previous",
  "pagination.results_range": "Showing {start}-{end} of {total} recipes",
  "profile.email": "E-Mail",
  "profile.joined": "Registriert am",
  "profile.role": "Rolle",
  "profile.title": "Mein Profil",
  "recipe.average_rating": "Durchschnittliche Bewertung",
  "recipe.comment": "Kommentar",
  "recipe.delete": "Loeschen",
  "recipe.edit": "Bearbeiten",
  "recipe.ingredients": "Zutaten",
  "recipe.instructions": "Anleitung",
  "recipe.no_ingredients": "Keine Zutaten gespeichert.",
  "recipe.no_results": "No recipes found.",
  "recipe.no_reviews": "Noch keine Bewertungen vorhanden.",
  "recipe.pdf_download": "PDF herunterladen",
  "recipe.rating": "Bewertung",
  "recipe.rating_short": "Bewertung",
  "recipe.review_count_label": "Bewertungen",
  "recipe.reviews": "Bewertungen",
  "recipe.save_review": "Bewertung speichern",
  "recipe_form.category": "Kategorie",
  "recipe_form.create": "Erstellen",
  "recipe_form.create_title": "Rezept veroeffentlichen",
  "recipe_form.description": "Beschreibung",
  "recipe_form.difficulty": "Schwierigkeit",
  "recipe_form.edit_title": "Rezept bearbeiten",
  "recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",
  "recipe_form.instructions": "Anleitung",
  "recipe_form.new_category_label": "Neue Kategorie",
  "recipe_form.new_category_option": "Neue Kategorie...",
  "recipe_form.optional_image": "Optionales Bild",
  "recipe_form.prep_time": "Zubereitungszeit (Minuten)",
  "recipe_form.save": "Speichern",
  "recipe_form.title": "Titel",
  "recipe_form.title_image_url": "Titelbild-URL",
  "role.admin": "Administrator",
  "role.user": "Nutzer",
  "sort.highest_rated": "Highest rated",
  "sort.lowest_rated": "Lowest rated",
  "sort.newest": "Newest",
  "sort.oldest": "Oldest",
  "sort.prep_time": "Prep time",
  "submission.admin_detail_title": "Einreichung",
  "submission.admin_empty": "Keine Einreichungen gefunden.",
  "submission.admin_note": "Admin-Notiz",
  "submission.admin_queue_link": "Zur Moderations-Warteschlange",
  "submission.admin_queue_title": "Moderation Queue",
  "submission.approve_button": "Approve",
  "submission.approved": "Einreichung wurde freigegeben.",
  "submission.back_to_queue": "Zurueck zur Warteschlange",
  "submission.category": "Kategorie",
  "submission.default_description": "Rezept-Einreichung",
  "submission.description": "Beschreibung",
  "submission.difficulty": "Schwierigkeit",
  "submission.edit_submission": "Einreichung bearbeiten",
  "submission.guest": "Gast",
  "submission.image_deleted": "Bild wurde entfernt.",
  "submission.image_optional": "Optionales Bild",
  "submission.image_primary": "Hauptbild wurde gesetzt.",
  "submission.ingredients": "Zutaten (Format: name|menge|gramm)",
  "submission.instructions": "Anleitung",
  "submission.moderation_actions": "Moderations-Aktionen",
  "submission.my_empty": "Du hast noch keine Einreichungen.",
  "submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",
  "submission.my_title": "My Submissions",
  "submission.new_category_label": "Neue Kategorie",
  "submission.new_category_option": "Neue Kategorie...",
  "submission.open_detail": "Details",
  "submission.optional_admin_note": "Admin-Notiz (optional)",
  "submission.prep_time": "Zubereitungszeit (Minuten, optional)",
  "submission.preview": "Vorschau",
  "submission.reject_button": "Reject",
  "submission.reject_reason": "Ablehnungsgrund",
  "submission.rejected": "Einreichung wurde abgelehnt.",
  "submission.save_changes": "Aenderungen speichern",
  "submission.servings": "Portionen (optional)",
  "submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",
  "submission.stats_approved": "Freigegeben",
  "submission.stats_pending": "Ausstehend",
  "submission.stats_rejected": "Abgelehnt",
  "submission.status_all": "Alle",
  "submission.status_approved": "Approved",
  "submission.status_filter": "Status",
  "submission.status_pending": "Pending",
  "submission.status_rejected": "Rejected",
  "submission.submit_button": "Zur Pruefung einreichen",
  "submission.submit_hint": "Submissions are reviewed by admins before publication.",
  "submission.submit_title": "Submit Recipe",
  "submission.submitter_email": "Kontakt-E-Mail (optional)",
  "submission.table_action": "Aktion",
  "submission.table_date": "Datum",
  "submission.table_status": "Status",
  "submission.table_submitter": "Einreicher",
  "submission.table_title": "Titel",
  "submission.thank_you": "Thank you! Your recipe has been submitted for review.",
  "submission.title": "Titel",
  "submission.updated": "Einreichung wurde aktualisiert."
}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '{'.
2. Diese Zeile definiert den Abschnitt '"admin.action": "Aktion",'.
3. Diese Zeile definiert den Abschnitt '"admin.category_distinct_count": "Anzahl eindeutiger Kategorien",'.
4. Diese Zeile definiert den Abschnitt '"admin.category_stats_title": "Kategorien-Status",'.
5. Diese Zeile definiert den Abschnitt '"admin.category_top": "Top 10 Kategorien",'.
6. Diese Zeile definiert den Abschnitt '"admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortset...'.
7. Diese Zeile definiert den Abschnitt '"admin.creator": "Ersteller",'.
8. Diese Zeile definiert den Abschnitt '"admin.csv_path": "CSV-Pfad",'.
9. Diese Zeile definiert den Abschnitt '"admin.download_example": "CSV Beispiel herunterladen",'.
10. Diese Zeile definiert den Abschnitt '"admin.download_template": "CSV Template herunterladen",'.
11. Diese Zeile definiert den Abschnitt '"admin.dry_run": "Nur pruefen (Dry Run)",'.
12. Diese Zeile definiert den Abschnitt '"admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",'.
13. Diese Zeile definiert den Abschnitt '"admin.email": "E-Mail",'.
14. Diese Zeile definiert den Abschnitt '"admin.force_with_warnings": "Trotz Warnungen fortsetzen",'.
15. Diese Zeile definiert den Abschnitt '"admin.id": "ID",'.
16. Diese Zeile definiert den Abschnitt '"admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften ...'.
17. Diese Zeile definiert den Abschnitt '"admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",'.
18. Diese Zeile definiert den Abschnitt '"admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' ...'.
19. Diese Zeile definiert den Abschnitt '"admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import s...'.
20. Diese Zeile definiert den Abschnitt '"admin.import_help_title": "CSV-Format Hilfe",'.
21. Diese Zeile definiert den Abschnitt '"admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise...'.
22. Diese Zeile definiert den Abschnitt '"admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty...'.
23. Diese Zeile definiert den Abschnitt '"admin.import_required_columns": "Pflichtspalten: title, instructions",'.
24. Diese Zeile definiert den Abschnitt '"admin.import_result_title": "Import-Ergebnis",'.
25. Diese Zeile definiert den Abschnitt '"admin.import_title": "Manual CSV Import",'.
26. Diese Zeile definiert den Abschnitt '"admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren,...'.
27. Diese Zeile definiert den Abschnitt '"admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",'.
28. Diese Zeile definiert den Abschnitt '"admin.preview_button": "Vorschau erstellen",'.
29. Diese Zeile definiert den Abschnitt '"admin.preview_delimiter": "Erkannter Delimiter",'.
30. Diese Zeile definiert den Abschnitt '"admin.preview_done": "Vorschau wurde erstellt.",'.
31. Diese Zeile definiert den Abschnitt '"admin.preview_errors_title": "Fehlerliste",'.
32. Diese Zeile definiert den Abschnitt '"admin.preview_fatal_rows": "Zeilen mit Fehlern",'.
33. Diese Zeile definiert den Abschnitt '"admin.preview_notes": "Hinweise",'.
34. Diese Zeile definiert den Abschnitt '"admin.preview_row": "Zeile",'.
35. Diese Zeile definiert den Abschnitt '"admin.preview_status": "Status",'.
36. Diese Zeile definiert den Abschnitt '"admin.preview_title": "Import-Vorschau",'.
37. Diese Zeile definiert den Abschnitt '"admin.preview_total_rows": "Gesamtzeilen",'.
38. Diese Zeile definiert den Abschnitt '"admin.preview_warnings_title": "Warnungsliste",'.
39. Diese Zeile definiert den Abschnitt '"admin.recipes": "Rezepte",'.
40. Diese Zeile definiert den Abschnitt '"admin.report_errors": "Fehler",'.
41. Diese Zeile definiert den Abschnitt '"admin.report_inserted": "Neu",'.
42. Diese Zeile definiert den Abschnitt '"admin.report_skipped": "Uebersprungen",'.
43. Diese Zeile definiert den Abschnitt '"admin.report_updated": "Aktualisiert",'.
44. Diese Zeile definiert den Abschnitt '"admin.report_warnings": "Warnungen",'.
45. Diese Zeile definiert den Abschnitt '"admin.role": "Rolle",'.
46. Diese Zeile definiert den Abschnitt '"admin.save": "Speichern",'.
47. Diese Zeile definiert den Abschnitt '"admin.seed_done": "Seed-Status: bereits ausgefuehrt.",'.
48. Diese Zeile definiert den Abschnitt '"admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",'.
49. Diese Zeile definiert den Abschnitt '"admin.seed_title": "KochWiki-Seed (einmalig)",'.
50. Diese Zeile definiert den Abschnitt '"admin.source": "Quelle",'.
51. Diese Zeile definiert den Abschnitt '"admin.start_import": "Import starten",'.
52. Diese Zeile definiert den Abschnitt '"admin.title": "Admin Area",'.
53. Diese Zeile definiert den Abschnitt '"admin.title_column": "Titel",'.
54. Diese Zeile definiert den Abschnitt '"admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",'.
55. Diese Zeile definiert den Abschnitt '"admin.upload_label": "CSV-Upload",'.
56. Diese Zeile definiert den Abschnitt '"admin.users": "Nutzer",'.
57. Diese Zeile definiert den Abschnitt '"app.name": "MealMate",'.
58. Diese Zeile definiert den Abschnitt '"auth.email": "Email",'.
59. Diese Zeile definiert den Abschnitt '"auth.login": "Login",'.
60. Diese Zeile definiert den Abschnitt '"auth.login_button": "Login",'.
61. Diese Zeile definiert den Abschnitt '"auth.login_title": "Login",'.
62. Diese Zeile definiert den Abschnitt '"auth.password": "Password",'.
63. Diese Zeile definiert den Abschnitt '"auth.register": "Register",'.
64. Diese Zeile definiert den Abschnitt '"auth.register_button": "Create account",'.
65. Diese Zeile definiert den Abschnitt '"auth.register_title": "Register",'.
66. Diese Zeile definiert den Abschnitt '"difficulty.easy": "Easy",'.
67. Diese Zeile definiert den Abschnitt '"difficulty.hard": "Hard",'.
68. Diese Zeile definiert den Abschnitt '"difficulty.medium": "Medium",'.
69. Diese Zeile definiert den Abschnitt '"discover.filter.apply": "Apply",'.
70. Diese Zeile definiert den Abschnitt '"discover.filter.category": "Category",'.
71. Diese Zeile definiert den Abschnitt '"discover.filter.difficulty": "Difficulty",'.
72. Diese Zeile definiert den Abschnitt '"discover.filter.ingredient": "Ingredient",'.
73. Diese Zeile definiert den Abschnitt '"discover.filter.title_contains": "Title contains",'.
74. Diese Zeile definiert den Abschnitt '"discover.sort.newest": "Newest",'.
75. Diese Zeile definiert den Abschnitt '"discover.sort.oldest": "Oldest",'.
76. Diese Zeile definiert den Abschnitt '"discover.sort.prep_time": "Prep time",'.
77. Diese Zeile definiert den Abschnitt '"discover.sort.rating_asc": "Lowest rated",'.
78. Diese Zeile definiert den Abschnitt '"discover.sort.rating_desc": "Highest rated",'.
79. Diese Zeile definiert den Abschnitt '"discover.title": "Discover Recipes",'.
80. Diese Zeile definiert den Abschnitt '"empty.no_recipes": "No recipes found.",'.
81. Diese Zeile definiert den Abschnitt '"error.404_text": "The requested page does not exist or has been moved.",'.
82. Diese Zeile definiert den Abschnitt '"error.404_title": "404 - Page Not Found",'.
83. Diese Zeile definiert den Abschnitt '"error.500_text": "An unexpected error occurred while processing the request.",'.
84. Diese Zeile definiert den Abschnitt '"error.500_title": "500 - Internal Error",'.
85. Diese Zeile definiert den Abschnitt '"error.admin_required": "Admin role required.",'.
86. Diese Zeile definiert den Abschnitt '"error.auth_required": "Authentication required.",'.
87. Diese Zeile definiert den Abschnitt '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
88. Diese Zeile definiert den Abschnitt '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
89. Diese Zeile definiert den Abschnitt '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
90. Diese Zeile definiert den Abschnitt '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
91. Diese Zeile definiert den Abschnitt '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
92. Diese Zeile definiert den Abschnitt '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
93. Diese Zeile definiert den Abschnitt '"error.email_registered": "This email is already registered.",'.
94. Diese Zeile definiert den Abschnitt '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
95. Diese Zeile definiert den Abschnitt '"error.field_positive": "{field} muss groesser als null sein.",'.
96. Diese Zeile definiert den Abschnitt '"error.home_link": "Back to Home",'.
97. Diese Zeile definiert den Abschnitt '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
98. Diese Zeile definiert den Abschnitt '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
99. Diese Zeile definiert den Abschnitt '"error.image_not_found": "Bild nicht gefunden.",'.
100. Diese Zeile definiert den Abschnitt '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
101. Diese Zeile definiert den Abschnitt '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
102. Diese Zeile definiert den Abschnitt '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
103. Diese Zeile definiert den Abschnitt '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
104. Diese Zeile definiert den Abschnitt '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
105. Diese Zeile definiert den Abschnitt '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschloss...'.
106. Diese Zeile definiert den Abschnitt '"error.internal": "Interner Serverfehler.",'.
107. Diese Zeile definiert den Abschnitt '"error.invalid_credentials": "Invalid credentials.",'.
108. Diese Zeile definiert den Abschnitt '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
109. Diese Zeile definiert den Abschnitt '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
110. Diese Zeile definiert den Abschnitt '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
111. Diese Zeile definiert den Abschnitt '"error.not_found": "Ressource nicht gefunden.",'.
112. Diese Zeile definiert den Abschnitt '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
113. Diese Zeile definiert den Abschnitt '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
114. Diese Zeile definiert den Abschnitt '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
115. Diese Zeile definiert den Abschnitt '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
116. Diese Zeile definiert den Abschnitt '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
117. Diese Zeile definiert den Abschnitt '"error.recipe_not_found": "Rezept nicht gefunden.",'.
118. Diese Zeile definiert den Abschnitt '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
119. Diese Zeile definiert den Abschnitt '"error.review_not_found": "Bewertung nicht gefunden.",'.
120. Diese Zeile definiert den Abschnitt '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
121. Diese Zeile definiert den Abschnitt '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
122. Diese Zeile definiert den Abschnitt '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
123. Diese Zeile definiert den Abschnitt '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht g...'.
124. Diese Zeile definiert den Abschnitt '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
125. Diese Zeile definiert den Abschnitt '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
126. Diese Zeile definiert den Abschnitt '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
127. Diese Zeile definiert den Abschnitt '"error.submission_not_found": "Einreichung nicht gefunden.",'.
128. Diese Zeile definiert den Abschnitt '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
129. Diese Zeile definiert den Abschnitt '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
130. Diese Zeile definiert den Abschnitt '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
131. Diese Zeile definiert den Abschnitt '"error.trace": "Stacktrace (nur Dev)",'.
132. Diese Zeile definiert den Abschnitt '"error.user_not_found": "Nutzer nicht gefunden.",'.
133. Diese Zeile definiert den Abschnitt '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
134. Diese Zeile definiert den Abschnitt '"favorite.add": "Zu Favoriten",'.
135. Diese Zeile definiert den Abschnitt '"favorite.remove": "Aus Favoriten entfernen",'.
136. Diese Zeile definiert den Abschnitt '"favorites.empty": "Keine Favoriten gespeichert.",'.
137. Diese Zeile definiert den Abschnitt '"favorites.remove": "Favorit entfernen",'.
138. Diese Zeile definiert den Abschnitt '"favorites.title": "Favoriten",'.
139. Diese Zeile definiert den Abschnitt '"home.all_categories": "All categories",'.
140. Diese Zeile definiert den Abschnitt '"home.apply": "Apply",'.
141. Diese Zeile definiert den Abschnitt '"home.category": "Category",'.
142. Diese Zeile definiert den Abschnitt '"home.difficulty": "Difficulty",'.
143. Diese Zeile definiert den Abschnitt '"home.ingredient": "Ingredient",'.
144. Diese Zeile definiert den Abschnitt '"home.per_page": "Per page",'.
145. Diese Zeile definiert den Abschnitt '"home.title": "Discover Recipes",'.
146. Diese Zeile definiert den Abschnitt '"home.title_contains": "Title contains",'.
147. Diese Zeile definiert den Abschnitt '"images.delete": "Loeschen",'.
148. Diese Zeile definiert den Abschnitt '"images.empty": "Noch keine Bilder vorhanden.",'.
149. Diese Zeile definiert den Abschnitt '"images.new_file": "Neue Bilddatei",'.
150. Diese Zeile definiert den Abschnitt '"images.primary": "Hauptbild",'.
151. Diese Zeile definiert den Abschnitt '"images.set_primary": "Als Hauptbild setzen",'.
152. Diese Zeile definiert den Abschnitt '"images.title": "Bilder",'.
153. Diese Zeile definiert den Abschnitt '"images.upload": "Bild hochladen",'.
154. Diese Zeile definiert den Abschnitt '"moderation.approve": "Approve",'.
155. Diese Zeile definiert den Abschnitt '"moderation.pending": "Pending",'.
156. Diese Zeile definiert den Abschnitt '"moderation.reject": "Reject",'.
157. Diese Zeile definiert den Abschnitt '"moderation.title": "Moderation Queue",'.
158. Diese Zeile definiert den Abschnitt '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
159. Diese Zeile definiert den Abschnitt '"my_recipes.title": "Meine Rezepte",'.
160. Diese Zeile definiert den Abschnitt '"nav.admin": "Admin",'.
161. Diese Zeile definiert den Abschnitt '"nav.admin_submissions": "Moderation",'.
162. Diese Zeile definiert den Abschnitt '"nav.create_recipe": "Create Recipe",'.
163. Diese Zeile definiert den Abschnitt '"nav.discover": "Discover Recipes",'.
164. Diese Zeile definiert den Abschnitt '"nav.favorites": "Favorites",'.
165. Diese Zeile definiert den Abschnitt '"nav.language": "Language",'.
166. Diese Zeile definiert den Abschnitt '"nav.login": "Login",'.
167. Diese Zeile definiert den Abschnitt '"nav.logout": "Logout",'.
168. Diese Zeile definiert den Abschnitt '"nav.my_recipes": "My Recipes",'.
169. Diese Zeile definiert den Abschnitt '"nav.my_submissions": "My Submissions",'.
170. Diese Zeile definiert den Abschnitt '"nav.profile": "My Profile",'.
171. Diese Zeile definiert den Abschnitt '"nav.publish_recipe": "Publish Recipe",'.
172. Diese Zeile definiert den Abschnitt '"nav.register": "Register",'.
173. Diese Zeile definiert den Abschnitt '"nav.submit": "Submit Recipe",'.
174. Diese Zeile definiert den Abschnitt '"nav.submit_recipe": "Submit Recipe",'.
175. Diese Zeile definiert den Abschnitt '"pagination.first": "First",'.
176. Diese Zeile definiert den Abschnitt '"pagination.last": "Last",'.
177. Diese Zeile definiert den Abschnitt '"pagination.next": "Next",'.
178. Diese Zeile definiert den Abschnitt '"pagination.page": "Page",'.
179. Diese Zeile definiert den Abschnitt '"pagination.prev": "Previous",'.
180. Diese Zeile definiert den Abschnitt '"pagination.previous": "Previous",'.
181. Diese Zeile definiert den Abschnitt '"pagination.results_range": "Showing {start}-{end} of {total} recipes",'.
182. Diese Zeile definiert den Abschnitt '"profile.email": "E-Mail",'.
183. Diese Zeile definiert den Abschnitt '"profile.joined": "Registriert am",'.
184. Diese Zeile definiert den Abschnitt '"profile.role": "Rolle",'.
185. Diese Zeile definiert den Abschnitt '"profile.title": "Mein Profil",'.
186. Diese Zeile definiert den Abschnitt '"recipe.average_rating": "Durchschnittliche Bewertung",'.
187. Diese Zeile definiert den Abschnitt '"recipe.comment": "Kommentar",'.
188. Diese Zeile definiert den Abschnitt '"recipe.delete": "Loeschen",'.
189. Diese Zeile definiert den Abschnitt '"recipe.edit": "Bearbeiten",'.
190. Diese Zeile definiert den Abschnitt '"recipe.ingredients": "Zutaten",'.
191. Diese Zeile definiert den Abschnitt '"recipe.instructions": "Anleitung",'.
192. Diese Zeile definiert den Abschnitt '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
193. Diese Zeile definiert den Abschnitt '"recipe.no_results": "No recipes found.",'.
194. Diese Zeile definiert den Abschnitt '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
195. Diese Zeile definiert den Abschnitt '"recipe.pdf_download": "PDF herunterladen",'.
196. Diese Zeile definiert den Abschnitt '"recipe.rating": "Bewertung",'.
197. Diese Zeile definiert den Abschnitt '"recipe.rating_short": "Bewertung",'.
198. Diese Zeile definiert den Abschnitt '"recipe.review_count_label": "Bewertungen",'.
199. Diese Zeile definiert den Abschnitt '"recipe.reviews": "Bewertungen",'.
200. Diese Zeile definiert den Abschnitt '"recipe.save_review": "Bewertung speichern",'.
201. Diese Zeile definiert den Abschnitt '"recipe_form.category": "Kategorie",'.
202. Diese Zeile definiert den Abschnitt '"recipe_form.create": "Erstellen",'.
203. Diese Zeile definiert den Abschnitt '"recipe_form.create_title": "Rezept veroeffentlichen",'.
204. Diese Zeile definiert den Abschnitt '"recipe_form.description": "Beschreibung",'.
205. Diese Zeile definiert den Abschnitt '"recipe_form.difficulty": "Schwierigkeit",'.
206. Diese Zeile definiert den Abschnitt '"recipe_form.edit_title": "Rezept bearbeiten",'.
207. Diese Zeile definiert den Abschnitt '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
208. Diese Zeile definiert den Abschnitt '"recipe_form.instructions": "Anleitung",'.
209. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_label": "Neue Kategorie",'.
210. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_option": "Neue Kategorie...",'.
211. Diese Zeile definiert den Abschnitt '"recipe_form.optional_image": "Optionales Bild",'.
212. Diese Zeile definiert den Abschnitt '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
213. Diese Zeile definiert den Abschnitt '"recipe_form.save": "Speichern",'.
214. Diese Zeile definiert den Abschnitt '"recipe_form.title": "Titel",'.
215. Diese Zeile definiert den Abschnitt '"recipe_form.title_image_url": "Titelbild-URL",'.
216. Diese Zeile definiert den Abschnitt '"role.admin": "Administrator",'.
217. Diese Zeile definiert den Abschnitt '"role.user": "Nutzer",'.
218. Diese Zeile definiert den Abschnitt '"sort.highest_rated": "Highest rated",'.
219. Diese Zeile definiert den Abschnitt '"sort.lowest_rated": "Lowest rated",'.
220. Diese Zeile definiert den Abschnitt '"sort.newest": "Newest",'.
221. Diese Zeile definiert den Abschnitt '"sort.oldest": "Oldest",'.
222. Diese Zeile definiert den Abschnitt '"sort.prep_time": "Prep time",'.
223. Diese Zeile definiert den Abschnitt '"submission.admin_detail_title": "Einreichung",'.
224. Diese Zeile definiert den Abschnitt '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
225. Diese Zeile definiert den Abschnitt '"submission.admin_note": "Admin-Notiz",'.
226. Diese Zeile definiert den Abschnitt '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
227. Diese Zeile definiert den Abschnitt '"submission.admin_queue_title": "Moderation Queue",'.
228. Diese Zeile definiert den Abschnitt '"submission.approve_button": "Approve",'.
229. Diese Zeile definiert den Abschnitt '"submission.approved": "Einreichung wurde freigegeben.",'.
230. Diese Zeile definiert den Abschnitt '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
231. Diese Zeile definiert den Abschnitt '"submission.category": "Kategorie",'.
232. Diese Zeile definiert den Abschnitt '"submission.default_description": "Rezept-Einreichung",'.
233. Diese Zeile definiert den Abschnitt '"submission.description": "Beschreibung",'.
234. Diese Zeile definiert den Abschnitt '"submission.difficulty": "Schwierigkeit",'.
235. Diese Zeile definiert den Abschnitt '"submission.edit_submission": "Einreichung bearbeiten",'.
236. Diese Zeile definiert den Abschnitt '"submission.guest": "Gast",'.
237. Diese Zeile definiert den Abschnitt '"submission.image_deleted": "Bild wurde entfernt.",'.
238. Diese Zeile definiert den Abschnitt '"submission.image_optional": "Optionales Bild",'.
239. Diese Zeile definiert den Abschnitt '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
240. Diese Zeile definiert den Abschnitt '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
241. Diese Zeile definiert den Abschnitt '"submission.instructions": "Anleitung",'.
242. Diese Zeile definiert den Abschnitt '"submission.moderation_actions": "Moderations-Aktionen",'.
243. Diese Zeile definiert den Abschnitt '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
244. Diese Zeile definiert den Abschnitt '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf ...'.
245. Diese Zeile definiert den Abschnitt '"submission.my_title": "My Submissions",'.
246. Diese Zeile definiert den Abschnitt '"submission.new_category_label": "Neue Kategorie",'.
247. Diese Zeile definiert den Abschnitt '"submission.new_category_option": "Neue Kategorie...",'.
248. Diese Zeile definiert den Abschnitt '"submission.open_detail": "Details",'.
249. Diese Zeile definiert den Abschnitt '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
250. Diese Zeile definiert den Abschnitt '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
251. Diese Zeile definiert den Abschnitt '"submission.preview": "Vorschau",'.
252. Diese Zeile definiert den Abschnitt '"submission.reject_button": "Reject",'.
253. Diese Zeile definiert den Abschnitt '"submission.reject_reason": "Ablehnungsgrund",'.
254. Diese Zeile definiert den Abschnitt '"submission.rejected": "Einreichung wurde abgelehnt.",'.
255. Diese Zeile definiert den Abschnitt '"submission.save_changes": "Aenderungen speichern",'.
256. Diese Zeile definiert den Abschnitt '"submission.servings": "Portionen (optional)",'.
257. Diese Zeile definiert den Abschnitt '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
258. Diese Zeile definiert den Abschnitt '"submission.stats_approved": "Freigegeben",'.
259. Diese Zeile definiert den Abschnitt '"submission.stats_pending": "Ausstehend",'.
260. Diese Zeile definiert den Abschnitt '"submission.stats_rejected": "Abgelehnt",'.
261. Diese Zeile definiert den Abschnitt '"submission.status_all": "Alle",'.
262. Diese Zeile definiert den Abschnitt '"submission.status_approved": "Approved",'.
263. Diese Zeile definiert den Abschnitt '"submission.status_filter": "Status",'.
264. Diese Zeile definiert den Abschnitt '"submission.status_pending": "Pending",'.
265. Diese Zeile definiert den Abschnitt '"submission.status_rejected": "Rejected",'.
266. Diese Zeile definiert den Abschnitt '"submission.submit_button": "Zur Pruefung einreichen",'.
267. Diese Zeile definiert den Abschnitt '"submission.submit_hint": "Submissions are reviewed by admins before publication.",'.
268. Diese Zeile definiert den Abschnitt '"submission.submit_title": "Submit Recipe",'.
269. Diese Zeile definiert den Abschnitt '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
270. Diese Zeile definiert den Abschnitt '"submission.table_action": "Aktion",'.
271. Diese Zeile definiert den Abschnitt '"submission.table_date": "Datum",'.
272. Diese Zeile definiert den Abschnitt '"submission.table_status": "Status",'.
273. Diese Zeile definiert den Abschnitt '"submission.table_submitter": "Einreicher",'.
274. Diese Zeile definiert den Abschnitt '"submission.table_title": "Titel",'.
275. Diese Zeile definiert den Abschnitt '"submission.thank_you": "Thank you! Your recipe has been submitted for review.",'.
276. Diese Zeile definiert den Abschnitt '"submission.title": "Titel",'.
277. Diese Zeile definiert den Abschnitt '"submission.updated": "Einreichung wurde aktualisiert."'.
278. Diese Zeile definiert den Abschnitt '}'.

## app/i18n/locales/fr.json
```json
{
  "admin.action": "Aktion",
  "admin.category_distinct_count": "Anzahl eindeutiger Kategorien",
  "admin.category_stats_title": "Kategorien-Status",
  "admin.category_top": "Top 10 Kategorien",
  "admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortsetzen', um den Import zu starten.",
  "admin.creator": "Ersteller",
  "admin.csv_path": "CSV-Pfad",
  "admin.download_example": "CSV Beispiel herunterladen",
  "admin.download_template": "CSV Template herunterladen",
  "admin.dry_run": "Nur pruefen (Dry Run)",
  "admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",
  "admin.email": "E-Mail",
  "admin.force_with_warnings": "Trotz Warnungen fortsetzen",
  "admin.id": "ID",
  "admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften Zeilen.",
  "admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",
  "admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' (',' als Fallback)",
  "admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import stabil und ohne Duplikate laeuft.",
  "admin.import_help_title": "CSV-Format Hilfe",
  "admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise Salz oder JSON-Liste",
  "admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty, prep_time_minutes, servings_text, ingredients, image_url, source_uuid",
  "admin.import_required_columns": "Pflichtspalten: title, instructions",
  "admin.import_result_title": "Import-Ergebnis",
  "admin.import_title": "Import CSV manuel",
  "admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren, wenn bewusst gewuenscht.",
  "admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",
  "admin.preview_button": "Vorschau erstellen",
  "admin.preview_delimiter": "Erkannter Delimiter",
  "admin.preview_done": "Vorschau wurde erstellt.",
  "admin.preview_errors_title": "Fehlerliste",
  "admin.preview_fatal_rows": "Zeilen mit Fehlern",
  "admin.preview_notes": "Hinweise",
  "admin.preview_row": "Zeile",
  "admin.preview_status": "Status",
  "admin.preview_title": "Import-Vorschau",
  "admin.preview_total_rows": "Gesamtzeilen",
  "admin.preview_warnings_title": "Warnungsliste",
  "admin.recipes": "Rezepte",
  "admin.report_errors": "Fehler",
  "admin.report_inserted": "Neu",
  "admin.report_skipped": "Uebersprungen",
  "admin.report_updated": "Aktualisiert",
  "admin.report_warnings": "Warnungen",
  "admin.role": "Rolle",
  "admin.save": "Speichern",
  "admin.seed_done": "Seed-Status: bereits ausgefuehrt.",
  "admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",
  "admin.seed_title": "KochWiki-Seed (einmalig)",
  "admin.source": "Quelle",
  "admin.start_import": "Import starten",
  "admin.title": "Espace Admin",
  "admin.title_column": "Titel",
  "admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",
  "admin.upload_label": "CSV-Upload",
  "admin.users": "Nutzer",
  "app.name": "MealMate",
  "auth.email": "E-mail",
  "auth.login": "Connexion",
  "auth.login_button": "Connexion",
  "auth.login_title": "Connexion",
  "auth.password": "Mot de passe",
  "auth.register": "Inscription",
  "auth.register_button": "Creer un compte",
  "auth.register_title": "Inscription",
  "difficulty.easy": "Facile",
  "difficulty.hard": "Difficile",
  "difficulty.medium": "Moyen",
  "discover.filter.apply": "Appliquer",
  "discover.filter.category": "Categorie",
  "discover.filter.difficulty": "Difficulte",
  "discover.filter.ingredient": "Ingredient",
  "discover.filter.title_contains": "Le titre contient",
  "discover.sort.newest": "Plus recentes",
  "discover.sort.oldest": "Plus anciennes",
  "discover.sort.prep_time": "Temps de preparation",
  "discover.sort.rating_asc": "Moins bien notees",
  "discover.sort.rating_desc": "Mieux notees",
  "discover.title": "Decouvrir des recettes",
  "empty.no_recipes": "Aucune recette trouvee.",
  "error.404_text": "La page demandee n'existe pas ou a ete deplacee.",
  "error.404_title": "404 - Page introuvable",
  "error.500_text": "Une erreur inattendue est survenue pendant le traitement.",
  "error.500_title": "500 - Erreur interne",
  "error.admin_required": "Role admin requis.",
  "error.auth_required": "Authentification requise.",
  "error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",
  "error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",
  "error.csv_not_found_prefix": "CSV-Datei nicht gefunden",
  "error.csv_only": "Es sind nur CSV-Uploads erlaubt.",
  "error.csv_too_large": "CSV-Upload ist zu gross.",
  "error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",
  "error.email_registered": "Cet e-mail est deja utilise.",
  "error.field_int": "{field} muss eine ganze Zahl sein.",
  "error.field_positive": "{field} muss groesser als null sein.",
  "error.home_link": "Retour a l'accueil",
  "error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",
  "error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",
  "error.image_not_found": "Bild nicht gefunden.",
  "error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",
  "error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",
  "error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",
  "error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",
  "error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",
  "error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",
  "error.internal": "Interner Serverfehler.",
  "error.invalid_credentials": "Identifiants invalides.",
  "error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",
  "error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",
  "error.no_image_url": "Keine Bild-URL verfuegbar.",
  "error.not_found": "Ressource nicht gefunden.",
  "error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",
  "error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",
  "error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",
  "error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",
  "error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",
  "error.recipe_not_found": "Rezept nicht gefunden.",
  "error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",
  "error.review_not_found": "Bewertung nicht gefunden.",
  "error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",
  "error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",
  "error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",
  "error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",
  "error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",
  "error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",
  "error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",
  "error.submission_not_found": "Einreichung nicht gefunden.",
  "error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",
  "error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",
  "error.title_instructions_required": "Titel und Anleitung sind erforderlich.",
  "error.trace": "Stacktrace (nur Dev)",
  "error.user_not_found": "Nutzer nicht gefunden.",
  "error.webp_signature": "Ungueltige WEBP-Dateisignatur.",
  "favorite.add": "Zu Favoriten",
  "favorite.remove": "Aus Favoriten entfernen",
  "favorites.empty": "Keine Favoriten gespeichert.",
  "favorites.remove": "Favorit entfernen",
  "favorites.title": "Favoriten",
  "home.all_categories": "Toutes les categories",
  "home.apply": "Appliquer",
  "home.category": "Categorie",
  "home.difficulty": "Difficulte",
  "home.ingredient": "Ingredient",
  "home.per_page": "Par page",
  "home.title": "Decouvrir des recettes",
  "home.title_contains": "Le titre contient",
  "images.delete": "Loeschen",
  "images.empty": "Noch keine Bilder vorhanden.",
  "images.new_file": "Neue Bilddatei",
  "images.primary": "Hauptbild",
  "images.set_primary": "Als Hauptbild setzen",
  "images.title": "Bilder",
  "images.upload": "Bild hochladen",
  "moderation.approve": "Approuver",
  "moderation.pending": "En attente",
  "moderation.reject": "Rejeter",
  "moderation.title": "File de moderation",
  "my_recipes.empty": "Noch keine Rezepte vorhanden.",
  "my_recipes.title": "Meine Rezepte",
  "nav.admin": "Admin",
  "nav.admin_submissions": "Moderation",
  "nav.create_recipe": "Creer une recette",
  "nav.discover": "Decouvrir des recettes",
  "nav.favorites": "Favoris",
  "nav.language": "Langue",
  "nav.login": "Connexion",
  "nav.logout": "Deconnexion",
  "nav.my_recipes": "Mes recettes",
  "nav.my_submissions": "Mes soumissions",
  "nav.profile": "Mon profil",
  "nav.publish_recipe": "Publier une recette",
  "nav.register": "Inscription",
  "nav.submit": "Soumettre une recette",
  "nav.submit_recipe": "Soumettre une recette",
  "pagination.first": "Premier",
  "pagination.last": "Dernier",
  "pagination.next": "Suivant",
  "pagination.page": "Page",
  "pagination.prev": "Precedent",
  "pagination.previous": "Precedent",
  "pagination.results_range": "Affichage {start}-{end} sur {total} recettes",
  "profile.email": "E-Mail",
  "profile.joined": "Registriert am",
  "profile.role": "Rolle",
  "profile.title": "Mein Profil",
  "recipe.average_rating": "Durchschnittliche Bewertung",
  "recipe.comment": "Kommentar",
  "recipe.delete": "Loeschen",
  "recipe.edit": "Bearbeiten",
  "recipe.ingredients": "Zutaten",
  "recipe.instructions": "Anleitung",
  "recipe.no_ingredients": "Keine Zutaten gespeichert.",
  "recipe.no_results": "Aucune recette trouvee.",
  "recipe.no_reviews": "Noch keine Bewertungen vorhanden.",
  "recipe.pdf_download": "PDF herunterladen",
  "recipe.rating": "Bewertung",
  "recipe.rating_short": "Bewertung",
  "recipe.review_count_label": "Bewertungen",
  "recipe.reviews": "Bewertungen",
  "recipe.save_review": "Bewertung speichern",
  "recipe_form.category": "Kategorie",
  "recipe_form.create": "Erstellen",
  "recipe_form.create_title": "Rezept veroeffentlichen",
  "recipe_form.description": "Beschreibung",
  "recipe_form.difficulty": "Schwierigkeit",
  "recipe_form.edit_title": "Rezept bearbeiten",
  "recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",
  "recipe_form.instructions": "Anleitung",
  "recipe_form.new_category_label": "Neue Kategorie",
  "recipe_form.new_category_option": "Neue Kategorie...",
  "recipe_form.optional_image": "Optionales Bild",
  "recipe_form.prep_time": "Zubereitungszeit (Minuten)",
  "recipe_form.save": "Speichern",
  "recipe_form.title": "Titel",
  "recipe_form.title_image_url": "Titelbild-URL",
  "role.admin": "Administrator",
  "role.user": "Nutzer",
  "sort.highest_rated": "Mieux notees",
  "sort.lowest_rated": "Moins bien notees",
  "sort.newest": "Plus recentes",
  "sort.oldest": "Plus anciennes",
  "sort.prep_time": "Temps de preparation",
  "submission.admin_detail_title": "Einreichung",
  "submission.admin_empty": "Keine Einreichungen gefunden.",
  "submission.admin_note": "Admin-Notiz",
  "submission.admin_queue_link": "Zur Moderations-Warteschlange",
  "submission.admin_queue_title": "File de moderation",
  "submission.approve_button": "Approuver",
  "submission.approved": "Einreichung wurde freigegeben.",
  "submission.back_to_queue": "Zurueck zur Warteschlange",
  "submission.category": "Kategorie",
  "submission.default_description": "Rezept-Einreichung",
  "submission.description": "Beschreibung",
  "submission.difficulty": "Schwierigkeit",
  "submission.edit_submission": "Einreichung bearbeiten",
  "submission.guest": "Gast",
  "submission.image_deleted": "Bild wurde entfernt.",
  "submission.image_optional": "Optionales Bild",
  "submission.image_primary": "Hauptbild wurde gesetzt.",
  "submission.ingredients": "Zutaten (Format: name|menge|gramm)",
  "submission.instructions": "Anleitung",
  "submission.moderation_actions": "Moderations-Aktionen",
  "submission.my_empty": "Du hast noch keine Einreichungen.",
  "submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",
  "submission.my_title": "Mes soumissions",
  "submission.new_category_label": "Neue Kategorie",
  "submission.new_category_option": "Neue Kategorie...",
  "submission.open_detail": "Details",
  "submission.optional_admin_note": "Admin-Notiz (optional)",
  "submission.prep_time": "Zubereitungszeit (Minuten, optional)",
  "submission.preview": "Vorschau",
  "submission.reject_button": "Rejeter",
  "submission.reject_reason": "Ablehnungsgrund",
  "submission.rejected": "Einreichung wurde abgelehnt.",
  "submission.save_changes": "Aenderungen speichern",
  "submission.servings": "Portionen (optional)",
  "submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",
  "submission.stats_approved": "Freigegeben",
  "submission.stats_pending": "Ausstehend",
  "submission.stats_rejected": "Abgelehnt",
  "submission.status_all": "Alle",
  "submission.status_approved": "Approuvee",
  "submission.status_filter": "Status",
  "submission.status_pending": "En attente",
  "submission.status_rejected": "Rejetee",
  "submission.submit_button": "Zur Pruefung einreichen",
  "submission.submit_hint": "Les soumissions sont verifiees par les admins avant publication.",
  "submission.submit_title": "Soumettre une recette",
  "submission.submitter_email": "Kontakt-E-Mail (optional)",
  "submission.table_action": "Aktion",
  "submission.table_date": "Datum",
  "submission.table_status": "Status",
  "submission.table_submitter": "Einreicher",
  "submission.table_title": "Titel",
  "submission.thank_you": "Merci ! Votre recette a ete soumise pour moderation.",
  "submission.title": "Titel",
  "submission.updated": "Einreichung wurde aktualisiert."
}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '{'.
2. Diese Zeile definiert den Abschnitt '"admin.action": "Aktion",'.
3. Diese Zeile definiert den Abschnitt '"admin.category_distinct_count": "Anzahl eindeutiger Kategorien",'.
4. Diese Zeile definiert den Abschnitt '"admin.category_stats_title": "Kategorien-Status",'.
5. Diese Zeile definiert den Abschnitt '"admin.category_top": "Top 10 Kategorien",'.
6. Diese Zeile definiert den Abschnitt '"admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortset...'.
7. Diese Zeile definiert den Abschnitt '"admin.creator": "Ersteller",'.
8. Diese Zeile definiert den Abschnitt '"admin.csv_path": "CSV-Pfad",'.
9. Diese Zeile definiert den Abschnitt '"admin.download_example": "CSV Beispiel herunterladen",'.
10. Diese Zeile definiert den Abschnitt '"admin.download_template": "CSV Template herunterladen",'.
11. Diese Zeile definiert den Abschnitt '"admin.dry_run": "Nur pruefen (Dry Run)",'.
12. Diese Zeile definiert den Abschnitt '"admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",'.
13. Diese Zeile definiert den Abschnitt '"admin.email": "E-Mail",'.
14. Diese Zeile definiert den Abschnitt '"admin.force_with_warnings": "Trotz Warnungen fortsetzen",'.
15. Diese Zeile definiert den Abschnitt '"admin.id": "ID",'.
16. Diese Zeile definiert den Abschnitt '"admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften ...'.
17. Diese Zeile definiert den Abschnitt '"admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",'.
18. Diese Zeile definiert den Abschnitt '"admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' ...'.
19. Diese Zeile definiert den Abschnitt '"admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import s...'.
20. Diese Zeile definiert den Abschnitt '"admin.import_help_title": "CSV-Format Hilfe",'.
21. Diese Zeile definiert den Abschnitt '"admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise...'.
22. Diese Zeile definiert den Abschnitt '"admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty...'.
23. Diese Zeile definiert den Abschnitt '"admin.import_required_columns": "Pflichtspalten: title, instructions",'.
24. Diese Zeile definiert den Abschnitt '"admin.import_result_title": "Import-Ergebnis",'.
25. Diese Zeile definiert den Abschnitt '"admin.import_title": "Import CSV manuel",'.
26. Diese Zeile definiert den Abschnitt '"admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren,...'.
27. Diese Zeile definiert den Abschnitt '"admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",'.
28. Diese Zeile definiert den Abschnitt '"admin.preview_button": "Vorschau erstellen",'.
29. Diese Zeile definiert den Abschnitt '"admin.preview_delimiter": "Erkannter Delimiter",'.
30. Diese Zeile definiert den Abschnitt '"admin.preview_done": "Vorschau wurde erstellt.",'.
31. Diese Zeile definiert den Abschnitt '"admin.preview_errors_title": "Fehlerliste",'.
32. Diese Zeile definiert den Abschnitt '"admin.preview_fatal_rows": "Zeilen mit Fehlern",'.
33. Diese Zeile definiert den Abschnitt '"admin.preview_notes": "Hinweise",'.
34. Diese Zeile definiert den Abschnitt '"admin.preview_row": "Zeile",'.
35. Diese Zeile definiert den Abschnitt '"admin.preview_status": "Status",'.
36. Diese Zeile definiert den Abschnitt '"admin.preview_title": "Import-Vorschau",'.
37. Diese Zeile definiert den Abschnitt '"admin.preview_total_rows": "Gesamtzeilen",'.
38. Diese Zeile definiert den Abschnitt '"admin.preview_warnings_title": "Warnungsliste",'.
39. Diese Zeile definiert den Abschnitt '"admin.recipes": "Rezepte",'.
40. Diese Zeile definiert den Abschnitt '"admin.report_errors": "Fehler",'.
41. Diese Zeile definiert den Abschnitt '"admin.report_inserted": "Neu",'.
42. Diese Zeile definiert den Abschnitt '"admin.report_skipped": "Uebersprungen",'.
43. Diese Zeile definiert den Abschnitt '"admin.report_updated": "Aktualisiert",'.
44. Diese Zeile definiert den Abschnitt '"admin.report_warnings": "Warnungen",'.
45. Diese Zeile definiert den Abschnitt '"admin.role": "Rolle",'.
46. Diese Zeile definiert den Abschnitt '"admin.save": "Speichern",'.
47. Diese Zeile definiert den Abschnitt '"admin.seed_done": "Seed-Status: bereits ausgefuehrt.",'.
48. Diese Zeile definiert den Abschnitt '"admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",'.
49. Diese Zeile definiert den Abschnitt '"admin.seed_title": "KochWiki-Seed (einmalig)",'.
50. Diese Zeile definiert den Abschnitt '"admin.source": "Quelle",'.
51. Diese Zeile definiert den Abschnitt '"admin.start_import": "Import starten",'.
52. Diese Zeile definiert den Abschnitt '"admin.title": "Espace Admin",'.
53. Diese Zeile definiert den Abschnitt '"admin.title_column": "Titel",'.
54. Diese Zeile definiert den Abschnitt '"admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",'.
55. Diese Zeile definiert den Abschnitt '"admin.upload_label": "CSV-Upload",'.
56. Diese Zeile definiert den Abschnitt '"admin.users": "Nutzer",'.
57. Diese Zeile definiert den Abschnitt '"app.name": "MealMate",'.
58. Diese Zeile definiert den Abschnitt '"auth.email": "E-mail",'.
59. Diese Zeile definiert den Abschnitt '"auth.login": "Connexion",'.
60. Diese Zeile definiert den Abschnitt '"auth.login_button": "Connexion",'.
61. Diese Zeile definiert den Abschnitt '"auth.login_title": "Connexion",'.
62. Diese Zeile definiert den Abschnitt '"auth.password": "Mot de passe",'.
63. Diese Zeile definiert den Abschnitt '"auth.register": "Inscription",'.
64. Diese Zeile definiert den Abschnitt '"auth.register_button": "Creer un compte",'.
65. Diese Zeile definiert den Abschnitt '"auth.register_title": "Inscription",'.
66. Diese Zeile definiert den Abschnitt '"difficulty.easy": "Facile",'.
67. Diese Zeile definiert den Abschnitt '"difficulty.hard": "Difficile",'.
68. Diese Zeile definiert den Abschnitt '"difficulty.medium": "Moyen",'.
69. Diese Zeile definiert den Abschnitt '"discover.filter.apply": "Appliquer",'.
70. Diese Zeile definiert den Abschnitt '"discover.filter.category": "Categorie",'.
71. Diese Zeile definiert den Abschnitt '"discover.filter.difficulty": "Difficulte",'.
72. Diese Zeile definiert den Abschnitt '"discover.filter.ingredient": "Ingredient",'.
73. Diese Zeile definiert den Abschnitt '"discover.filter.title_contains": "Le titre contient",'.
74. Diese Zeile definiert den Abschnitt '"discover.sort.newest": "Plus recentes",'.
75. Diese Zeile definiert den Abschnitt '"discover.sort.oldest": "Plus anciennes",'.
76. Diese Zeile definiert den Abschnitt '"discover.sort.prep_time": "Temps de preparation",'.
77. Diese Zeile definiert den Abschnitt '"discover.sort.rating_asc": "Moins bien notees",'.
78. Diese Zeile definiert den Abschnitt '"discover.sort.rating_desc": "Mieux notees",'.
79. Diese Zeile definiert den Abschnitt '"discover.title": "Decouvrir des recettes",'.
80. Diese Zeile definiert den Abschnitt '"empty.no_recipes": "Aucune recette trouvee.",'.
81. Diese Zeile definiert den Abschnitt '"error.404_text": "La page demandee n'existe pas ou a ete deplacee.",'.
82. Diese Zeile definiert den Abschnitt '"error.404_title": "404 - Page introuvable",'.
83. Diese Zeile definiert den Abschnitt '"error.500_text": "Une erreur inattendue est survenue pendant le traitement.",'.
84. Diese Zeile definiert den Abschnitt '"error.500_title": "500 - Erreur interne",'.
85. Diese Zeile definiert den Abschnitt '"error.admin_required": "Role admin requis.",'.
86. Diese Zeile definiert den Abschnitt '"error.auth_required": "Authentification requise.",'.
87. Diese Zeile definiert den Abschnitt '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
88. Diese Zeile definiert den Abschnitt '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
89. Diese Zeile definiert den Abschnitt '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
90. Diese Zeile definiert den Abschnitt '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
91. Diese Zeile definiert den Abschnitt '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
92. Diese Zeile definiert den Abschnitt '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
93. Diese Zeile definiert den Abschnitt '"error.email_registered": "Cet e-mail est deja utilise.",'.
94. Diese Zeile definiert den Abschnitt '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
95. Diese Zeile definiert den Abschnitt '"error.field_positive": "{field} muss groesser als null sein.",'.
96. Diese Zeile definiert den Abschnitt '"error.home_link": "Retour a l'accueil",'.
97. Diese Zeile definiert den Abschnitt '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
98. Diese Zeile definiert den Abschnitt '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
99. Diese Zeile definiert den Abschnitt '"error.image_not_found": "Bild nicht gefunden.",'.
100. Diese Zeile definiert den Abschnitt '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
101. Diese Zeile definiert den Abschnitt '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
102. Diese Zeile definiert den Abschnitt '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
103. Diese Zeile definiert den Abschnitt '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
104. Diese Zeile definiert den Abschnitt '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
105. Diese Zeile definiert den Abschnitt '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschloss...'.
106. Diese Zeile definiert den Abschnitt '"error.internal": "Interner Serverfehler.",'.
107. Diese Zeile definiert den Abschnitt '"error.invalid_credentials": "Identifiants invalides.",'.
108. Diese Zeile definiert den Abschnitt '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
109. Diese Zeile definiert den Abschnitt '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
110. Diese Zeile definiert den Abschnitt '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
111. Diese Zeile definiert den Abschnitt '"error.not_found": "Ressource nicht gefunden.",'.
112. Diese Zeile definiert den Abschnitt '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
113. Diese Zeile definiert den Abschnitt '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
114. Diese Zeile definiert den Abschnitt '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
115. Diese Zeile definiert den Abschnitt '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
116. Diese Zeile definiert den Abschnitt '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
117. Diese Zeile definiert den Abschnitt '"error.recipe_not_found": "Rezept nicht gefunden.",'.
118. Diese Zeile definiert den Abschnitt '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
119. Diese Zeile definiert den Abschnitt '"error.review_not_found": "Bewertung nicht gefunden.",'.
120. Diese Zeile definiert den Abschnitt '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
121. Diese Zeile definiert den Abschnitt '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
122. Diese Zeile definiert den Abschnitt '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
123. Diese Zeile definiert den Abschnitt '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht g...'.
124. Diese Zeile definiert den Abschnitt '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
125. Diese Zeile definiert den Abschnitt '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
126. Diese Zeile definiert den Abschnitt '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
127. Diese Zeile definiert den Abschnitt '"error.submission_not_found": "Einreichung nicht gefunden.",'.
128. Diese Zeile definiert den Abschnitt '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
129. Diese Zeile definiert den Abschnitt '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
130. Diese Zeile definiert den Abschnitt '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
131. Diese Zeile definiert den Abschnitt '"error.trace": "Stacktrace (nur Dev)",'.
132. Diese Zeile definiert den Abschnitt '"error.user_not_found": "Nutzer nicht gefunden.",'.
133. Diese Zeile definiert den Abschnitt '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
134. Diese Zeile definiert den Abschnitt '"favorite.add": "Zu Favoriten",'.
135. Diese Zeile definiert den Abschnitt '"favorite.remove": "Aus Favoriten entfernen",'.
136. Diese Zeile definiert den Abschnitt '"favorites.empty": "Keine Favoriten gespeichert.",'.
137. Diese Zeile definiert den Abschnitt '"favorites.remove": "Favorit entfernen",'.
138. Diese Zeile definiert den Abschnitt '"favorites.title": "Favoriten",'.
139. Diese Zeile definiert den Abschnitt '"home.all_categories": "Toutes les categories",'.
140. Diese Zeile definiert den Abschnitt '"home.apply": "Appliquer",'.
141. Diese Zeile definiert den Abschnitt '"home.category": "Categorie",'.
142. Diese Zeile definiert den Abschnitt '"home.difficulty": "Difficulte",'.
143. Diese Zeile definiert den Abschnitt '"home.ingredient": "Ingredient",'.
144. Diese Zeile definiert den Abschnitt '"home.per_page": "Par page",'.
145. Diese Zeile definiert den Abschnitt '"home.title": "Decouvrir des recettes",'.
146. Diese Zeile definiert den Abschnitt '"home.title_contains": "Le titre contient",'.
147. Diese Zeile definiert den Abschnitt '"images.delete": "Loeschen",'.
148. Diese Zeile definiert den Abschnitt '"images.empty": "Noch keine Bilder vorhanden.",'.
149. Diese Zeile definiert den Abschnitt '"images.new_file": "Neue Bilddatei",'.
150. Diese Zeile definiert den Abschnitt '"images.primary": "Hauptbild",'.
151. Diese Zeile definiert den Abschnitt '"images.set_primary": "Als Hauptbild setzen",'.
152. Diese Zeile definiert den Abschnitt '"images.title": "Bilder",'.
153. Diese Zeile definiert den Abschnitt '"images.upload": "Bild hochladen",'.
154. Diese Zeile definiert den Abschnitt '"moderation.approve": "Approuver",'.
155. Diese Zeile definiert den Abschnitt '"moderation.pending": "En attente",'.
156. Diese Zeile definiert den Abschnitt '"moderation.reject": "Rejeter",'.
157. Diese Zeile definiert den Abschnitt '"moderation.title": "File de moderation",'.
158. Diese Zeile definiert den Abschnitt '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
159. Diese Zeile definiert den Abschnitt '"my_recipes.title": "Meine Rezepte",'.
160. Diese Zeile definiert den Abschnitt '"nav.admin": "Admin",'.
161. Diese Zeile definiert den Abschnitt '"nav.admin_submissions": "Moderation",'.
162. Diese Zeile definiert den Abschnitt '"nav.create_recipe": "Creer une recette",'.
163. Diese Zeile definiert den Abschnitt '"nav.discover": "Decouvrir des recettes",'.
164. Diese Zeile definiert den Abschnitt '"nav.favorites": "Favoris",'.
165. Diese Zeile definiert den Abschnitt '"nav.language": "Langue",'.
166. Diese Zeile definiert den Abschnitt '"nav.login": "Connexion",'.
167. Diese Zeile definiert den Abschnitt '"nav.logout": "Deconnexion",'.
168. Diese Zeile definiert den Abschnitt '"nav.my_recipes": "Mes recettes",'.
169. Diese Zeile definiert den Abschnitt '"nav.my_submissions": "Mes soumissions",'.
170. Diese Zeile definiert den Abschnitt '"nav.profile": "Mon profil",'.
171. Diese Zeile definiert den Abschnitt '"nav.publish_recipe": "Publier une recette",'.
172. Diese Zeile definiert den Abschnitt '"nav.register": "Inscription",'.
173. Diese Zeile definiert den Abschnitt '"nav.submit": "Soumettre une recette",'.
174. Diese Zeile definiert den Abschnitt '"nav.submit_recipe": "Soumettre une recette",'.
175. Diese Zeile definiert den Abschnitt '"pagination.first": "Premier",'.
176. Diese Zeile definiert den Abschnitt '"pagination.last": "Dernier",'.
177. Diese Zeile definiert den Abschnitt '"pagination.next": "Suivant",'.
178. Diese Zeile definiert den Abschnitt '"pagination.page": "Page",'.
179. Diese Zeile definiert den Abschnitt '"pagination.prev": "Precedent",'.
180. Diese Zeile definiert den Abschnitt '"pagination.previous": "Precedent",'.
181. Diese Zeile definiert den Abschnitt '"pagination.results_range": "Affichage {start}-{end} sur {total} recettes",'.
182. Diese Zeile definiert den Abschnitt '"profile.email": "E-Mail",'.
183. Diese Zeile definiert den Abschnitt '"profile.joined": "Registriert am",'.
184. Diese Zeile definiert den Abschnitt '"profile.role": "Rolle",'.
185. Diese Zeile definiert den Abschnitt '"profile.title": "Mein Profil",'.
186. Diese Zeile definiert den Abschnitt '"recipe.average_rating": "Durchschnittliche Bewertung",'.
187. Diese Zeile definiert den Abschnitt '"recipe.comment": "Kommentar",'.
188. Diese Zeile definiert den Abschnitt '"recipe.delete": "Loeschen",'.
189. Diese Zeile definiert den Abschnitt '"recipe.edit": "Bearbeiten",'.
190. Diese Zeile definiert den Abschnitt '"recipe.ingredients": "Zutaten",'.
191. Diese Zeile definiert den Abschnitt '"recipe.instructions": "Anleitung",'.
192. Diese Zeile definiert den Abschnitt '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
193. Diese Zeile definiert den Abschnitt '"recipe.no_results": "Aucune recette trouvee.",'.
194. Diese Zeile definiert den Abschnitt '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
195. Diese Zeile definiert den Abschnitt '"recipe.pdf_download": "PDF herunterladen",'.
196. Diese Zeile definiert den Abschnitt '"recipe.rating": "Bewertung",'.
197. Diese Zeile definiert den Abschnitt '"recipe.rating_short": "Bewertung",'.
198. Diese Zeile definiert den Abschnitt '"recipe.review_count_label": "Bewertungen",'.
199. Diese Zeile definiert den Abschnitt '"recipe.reviews": "Bewertungen",'.
200. Diese Zeile definiert den Abschnitt '"recipe.save_review": "Bewertung speichern",'.
201. Diese Zeile definiert den Abschnitt '"recipe_form.category": "Kategorie",'.
202. Diese Zeile definiert den Abschnitt '"recipe_form.create": "Erstellen",'.
203. Diese Zeile definiert den Abschnitt '"recipe_form.create_title": "Rezept veroeffentlichen",'.
204. Diese Zeile definiert den Abschnitt '"recipe_form.description": "Beschreibung",'.
205. Diese Zeile definiert den Abschnitt '"recipe_form.difficulty": "Schwierigkeit",'.
206. Diese Zeile definiert den Abschnitt '"recipe_form.edit_title": "Rezept bearbeiten",'.
207. Diese Zeile definiert den Abschnitt '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
208. Diese Zeile definiert den Abschnitt '"recipe_form.instructions": "Anleitung",'.
209. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_label": "Neue Kategorie",'.
210. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_option": "Neue Kategorie...",'.
211. Diese Zeile definiert den Abschnitt '"recipe_form.optional_image": "Optionales Bild",'.
212. Diese Zeile definiert den Abschnitt '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
213. Diese Zeile definiert den Abschnitt '"recipe_form.save": "Speichern",'.
214. Diese Zeile definiert den Abschnitt '"recipe_form.title": "Titel",'.
215. Diese Zeile definiert den Abschnitt '"recipe_form.title_image_url": "Titelbild-URL",'.
216. Diese Zeile definiert den Abschnitt '"role.admin": "Administrator",'.
217. Diese Zeile definiert den Abschnitt '"role.user": "Nutzer",'.
218. Diese Zeile definiert den Abschnitt '"sort.highest_rated": "Mieux notees",'.
219. Diese Zeile definiert den Abschnitt '"sort.lowest_rated": "Moins bien notees",'.
220. Diese Zeile definiert den Abschnitt '"sort.newest": "Plus recentes",'.
221. Diese Zeile definiert den Abschnitt '"sort.oldest": "Plus anciennes",'.
222. Diese Zeile definiert den Abschnitt '"sort.prep_time": "Temps de preparation",'.
223. Diese Zeile definiert den Abschnitt '"submission.admin_detail_title": "Einreichung",'.
224. Diese Zeile definiert den Abschnitt '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
225. Diese Zeile definiert den Abschnitt '"submission.admin_note": "Admin-Notiz",'.
226. Diese Zeile definiert den Abschnitt '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
227. Diese Zeile definiert den Abschnitt '"submission.admin_queue_title": "File de moderation",'.
228. Diese Zeile definiert den Abschnitt '"submission.approve_button": "Approuver",'.
229. Diese Zeile definiert den Abschnitt '"submission.approved": "Einreichung wurde freigegeben.",'.
230. Diese Zeile definiert den Abschnitt '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
231. Diese Zeile definiert den Abschnitt '"submission.category": "Kategorie",'.
232. Diese Zeile definiert den Abschnitt '"submission.default_description": "Rezept-Einreichung",'.
233. Diese Zeile definiert den Abschnitt '"submission.description": "Beschreibung",'.
234. Diese Zeile definiert den Abschnitt '"submission.difficulty": "Schwierigkeit",'.
235. Diese Zeile definiert den Abschnitt '"submission.edit_submission": "Einreichung bearbeiten",'.
236. Diese Zeile definiert den Abschnitt '"submission.guest": "Gast",'.
237. Diese Zeile definiert den Abschnitt '"submission.image_deleted": "Bild wurde entfernt.",'.
238. Diese Zeile definiert den Abschnitt '"submission.image_optional": "Optionales Bild",'.
239. Diese Zeile definiert den Abschnitt '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
240. Diese Zeile definiert den Abschnitt '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
241. Diese Zeile definiert den Abschnitt '"submission.instructions": "Anleitung",'.
242. Diese Zeile definiert den Abschnitt '"submission.moderation_actions": "Moderations-Aktionen",'.
243. Diese Zeile definiert den Abschnitt '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
244. Diese Zeile definiert den Abschnitt '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf ...'.
245. Diese Zeile definiert den Abschnitt '"submission.my_title": "Mes soumissions",'.
246. Diese Zeile definiert den Abschnitt '"submission.new_category_label": "Neue Kategorie",'.
247. Diese Zeile definiert den Abschnitt '"submission.new_category_option": "Neue Kategorie...",'.
248. Diese Zeile definiert den Abschnitt '"submission.open_detail": "Details",'.
249. Diese Zeile definiert den Abschnitt '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
250. Diese Zeile definiert den Abschnitt '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
251. Diese Zeile definiert den Abschnitt '"submission.preview": "Vorschau",'.
252. Diese Zeile definiert den Abschnitt '"submission.reject_button": "Rejeter",'.
253. Diese Zeile definiert den Abschnitt '"submission.reject_reason": "Ablehnungsgrund",'.
254. Diese Zeile definiert den Abschnitt '"submission.rejected": "Einreichung wurde abgelehnt.",'.
255. Diese Zeile definiert den Abschnitt '"submission.save_changes": "Aenderungen speichern",'.
256. Diese Zeile definiert den Abschnitt '"submission.servings": "Portionen (optional)",'.
257. Diese Zeile definiert den Abschnitt '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
258. Diese Zeile definiert den Abschnitt '"submission.stats_approved": "Freigegeben",'.
259. Diese Zeile definiert den Abschnitt '"submission.stats_pending": "Ausstehend",'.
260. Diese Zeile definiert den Abschnitt '"submission.stats_rejected": "Abgelehnt",'.
261. Diese Zeile definiert den Abschnitt '"submission.status_all": "Alle",'.
262. Diese Zeile definiert den Abschnitt '"submission.status_approved": "Approuvee",'.
263. Diese Zeile definiert den Abschnitt '"submission.status_filter": "Status",'.
264. Diese Zeile definiert den Abschnitt '"submission.status_pending": "En attente",'.
265. Diese Zeile definiert den Abschnitt '"submission.status_rejected": "Rejetee",'.
266. Diese Zeile definiert den Abschnitt '"submission.submit_button": "Zur Pruefung einreichen",'.
267. Diese Zeile definiert den Abschnitt '"submission.submit_hint": "Les soumissions sont verifiees par les admins avant publicat...'.
268. Diese Zeile definiert den Abschnitt '"submission.submit_title": "Soumettre une recette",'.
269. Diese Zeile definiert den Abschnitt '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
270. Diese Zeile definiert den Abschnitt '"submission.table_action": "Aktion",'.
271. Diese Zeile definiert den Abschnitt '"submission.table_date": "Datum",'.
272. Diese Zeile definiert den Abschnitt '"submission.table_status": "Status",'.
273. Diese Zeile definiert den Abschnitt '"submission.table_submitter": "Einreicher",'.
274. Diese Zeile definiert den Abschnitt '"submission.table_title": "Titel",'.
275. Diese Zeile definiert den Abschnitt '"submission.thank_you": "Merci ! Votre recette a ete soumise pour moderation.",'.
276. Diese Zeile definiert den Abschnitt '"submission.title": "Titel",'.
277. Diese Zeile definiert den Abschnitt '"submission.updated": "Einreichung wurde aktualisiert."'.
278. Diese Zeile definiert den Abschnitt '}'.

## tests/test_i18n.py
```python
def test_language_default_is_de(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Rezepte entdecken" in response.text


def test_language_query_param_sets_cookie(client):
    response = client.get("/?lang=en")
    assert response.status_code == 200
    assert "Discover Recipes" in response.text
    assert response.cookies.get("lang") == "en"


def test_accept_language_header_de_picks_de(client):
    response = client.get("/", headers={"Accept-Language": "de-DE,de;q=0.9,en;q=0.8"})
    assert response.status_code == 200
    assert "Rezepte entdecken" in response.text


def test_template_renders_translation_key(client):
    response = client.get("/?lang=fr")
    assert response.status_code == 200
    assert "Decouvrir des recettes" in response.text
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'def test_language_default_is_de(client):'.
2. Diese Zeile definiert den Abschnitt 'response = client.get("/")'.
3. Diese Zeile definiert den Abschnitt 'assert response.status_code == 200'.
4. Diese Zeile definiert den Abschnitt 'assert "Rezepte entdecken" in response.text'.
5. Diese Zeile ist leer und strukturiert den Inhalt.
6. Diese Zeile ist leer und strukturiert den Inhalt.
7. Diese Zeile definiert den Abschnitt 'def test_language_query_param_sets_cookie(client):'.
8. Diese Zeile definiert den Abschnitt 'response = client.get("/?lang=en")'.
9. Diese Zeile definiert den Abschnitt 'assert response.status_code == 200'.
10. Diese Zeile definiert den Abschnitt 'assert "Discover Recipes" in response.text'.
11. Diese Zeile definiert den Abschnitt 'assert response.cookies.get("lang") == "en"'.
12. Diese Zeile ist leer und strukturiert den Inhalt.
13. Diese Zeile ist leer und strukturiert den Inhalt.
14. Diese Zeile definiert den Abschnitt 'def test_accept_language_header_de_picks_de(client):'.
15. Diese Zeile definiert den Abschnitt 'response = client.get("/", headers={"Accept-Language": "de-DE,de;q=0.9,en;q=0.8"})'.
16. Diese Zeile definiert den Abschnitt 'assert response.status_code == 200'.
17. Diese Zeile definiert den Abschnitt 'assert "Rezepte entdecken" in response.text'.
18. Diese Zeile ist leer und strukturiert den Inhalt.
19. Diese Zeile ist leer und strukturiert den Inhalt.
20. Diese Zeile definiert den Abschnitt 'def test_template_renders_translation_key(client):'.
21. Diese Zeile definiert den Abschnitt 'response = client.get("/?lang=fr")'.
22. Diese Zeile definiert den Abschnitt 'assert response.status_code == 200'.
23. Diese Zeile definiert den Abschnitt 'assert "Decouvrir des recettes" in response.text'.

## README_I18N.md
```markdown
# MealMate i18n

## Zweck

MealMate nutzt JSON-basierte Lokalisierung fuer die Website-Texte.
Aktiv sind `de`, `en` und `fr`, Standard ist `de`.

## Aufloesung der Sprache

Die Sprache wird pro Request in dieser Reihenfolge bestimmt:

1. Query-Parameter `?lang=de|en|fr`
2. Cookie `lang`
3. Header `Accept-Language`
4. Default `de`

Wenn `?lang=...` gesetzt ist, schreibt die App den Cookie `lang` (1 Jahr).

## Struktur

- Locale-Dateien:
  - `app/i18n/locales/de.json`
  - `app/i18n/locales/en.json`
  - `app/i18n/locales/fr.json`
- Service:
  - `app/i18n/service.py`
- Middleware:
  - `app/i18n/middleware.py`

## Verwendung in Templates

In Jinja2 ist `t("key")` global verfuegbar.

Beispiele:

- `{{ t("nav.discover") }}`
- `{{ t("pagination.results_range", start=1, end=10, total=120) }}`

Zusaetzlich sind verfuegbar:

- `current_lang` (z. B. `de`)
- `available_langs` (Liste fuer Sprachumschalter)
- `lang_url(request, "en")` zum Erzeugen von Sprach-URLs

## Fallback-Logik

Wenn ein Key in der aktiven Sprache fehlt:

1. Fallback auf `de.json`
2. wenn dort auch fehlend: Rueckgabe des Keys selbst

## Neue Sprache hinzufuegen (it/es)

1. Neue Datei anlegen, z. B. `app/i18n/locales/it.json`
2. Alle benoetigten Keys ergaenzen
3. In `app/i18n/service.py`:
   - `SUPPORTED_LANGS` erweitern
   - `LANG_LABELS` erweitern
4. App neu starten

## Wichtige Keys (Auszug)

- `nav.discover`
- `nav.submit`
- `nav.admin`
- `discover.title`
- `discover.filter.title_contains`
- `discover.filter.category`
- `discover.filter.difficulty`
- `discover.filter.ingredient`
- `discover.filter.apply`
- `discover.sort.newest`
- `discover.sort.oldest`
- `discover.sort.rating_desc`
- `discover.sort.rating_asc`
- `discover.sort.prep_time`
- `pagination.prev`
- `pagination.next`
- `empty.no_recipes`
- `auth.login`
- `auth.register`
- `admin.title`
- `moderation.title`
- `moderation.pending`
- `moderation.approve`
- `moderation.reject`
- `difficulty.easy`
- `difficulty.medium`
- `difficulty.hard`
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '# MealMate i18n'.
2. Diese Zeile ist leer und strukturiert den Inhalt.
3. Diese Zeile definiert den Abschnitt '## Zweck'.
4. Diese Zeile ist leer und strukturiert den Inhalt.
5. Diese Zeile definiert den Abschnitt 'MealMate nutzt JSON-basierte Lokalisierung fuer die Website-Texte.'.
6. Diese Zeile definiert den Abschnitt 'Aktiv sind 'de', 'en' und 'fr', Standard ist 'de'.'.
7. Diese Zeile ist leer und strukturiert den Inhalt.
8. Diese Zeile definiert den Abschnitt '## Aufloesung der Sprache'.
9. Diese Zeile ist leer und strukturiert den Inhalt.
10. Diese Zeile definiert den Abschnitt 'Die Sprache wird pro Request in dieser Reihenfolge bestimmt:'.
11. Diese Zeile ist leer und strukturiert den Inhalt.
12. Diese Zeile definiert den Abschnitt '1. Query-Parameter '?lang=de|en|fr''.
13. Diese Zeile definiert den Abschnitt '2. Cookie 'lang''.
14. Diese Zeile definiert den Abschnitt '3. Header 'Accept-Language''.
15. Diese Zeile definiert den Abschnitt '4. Default 'de''.
16. Diese Zeile ist leer und strukturiert den Inhalt.
17. Diese Zeile definiert den Abschnitt 'Wenn '?lang=...' gesetzt ist, schreibt die App den Cookie 'lang' (1 Jahr).'.
18. Diese Zeile ist leer und strukturiert den Inhalt.
19. Diese Zeile definiert den Abschnitt '## Struktur'.
20. Diese Zeile ist leer und strukturiert den Inhalt.
21. Diese Zeile definiert den Abschnitt '- Locale-Dateien:'.
22. Diese Zeile definiert den Abschnitt '- 'app/i18n/locales/de.json''.
23. Diese Zeile definiert den Abschnitt '- 'app/i18n/locales/en.json''.
24. Diese Zeile definiert den Abschnitt '- 'app/i18n/locales/fr.json''.
25. Diese Zeile definiert den Abschnitt '- Service:'.
26. Diese Zeile definiert den Abschnitt '- 'app/i18n/service.py''.
27. Diese Zeile definiert den Abschnitt '- Middleware:'.
28. Diese Zeile definiert den Abschnitt '- 'app/i18n/middleware.py''.
29. Diese Zeile ist leer und strukturiert den Inhalt.
30. Diese Zeile definiert den Abschnitt '## Verwendung in Templates'.
31. Diese Zeile ist leer und strukturiert den Inhalt.
32. Diese Zeile definiert den Abschnitt 'In Jinja2 ist 't("key")' global verfuegbar.'.
33. Diese Zeile ist leer und strukturiert den Inhalt.
34. Diese Zeile definiert den Abschnitt 'Beispiele:'.
35. Diese Zeile ist leer und strukturiert den Inhalt.
36. Diese Zeile definiert den Abschnitt '- '{{ t("nav.discover") }}''.
37. Diese Zeile definiert den Abschnitt '- '{{ t("pagination.results_range", start=1, end=10, total=120) }}''.
38. Diese Zeile ist leer und strukturiert den Inhalt.
39. Diese Zeile definiert den Abschnitt 'Zusaetzlich sind verfuegbar:'.
40. Diese Zeile ist leer und strukturiert den Inhalt.
41. Diese Zeile definiert den Abschnitt '- 'current_lang' (z. B. 'de')'.
42. Diese Zeile definiert den Abschnitt '- 'available_langs' (Liste fuer Sprachumschalter)'.
43. Diese Zeile definiert den Abschnitt '- 'lang_url(request, "en")' zum Erzeugen von Sprach-URLs'.
44. Diese Zeile ist leer und strukturiert den Inhalt.
45. Diese Zeile definiert den Abschnitt '## Fallback-Logik'.
46. Diese Zeile ist leer und strukturiert den Inhalt.
47. Diese Zeile definiert den Abschnitt 'Wenn ein Key in der aktiven Sprache fehlt:'.
48. Diese Zeile ist leer und strukturiert den Inhalt.
49. Diese Zeile definiert den Abschnitt '1. Fallback auf 'de.json''.
50. Diese Zeile definiert den Abschnitt '2. wenn dort auch fehlend: Rueckgabe des Keys selbst'.
51. Diese Zeile ist leer und strukturiert den Inhalt.
52. Diese Zeile definiert den Abschnitt '## Neue Sprache hinzufuegen (it/es)'.
53. Diese Zeile ist leer und strukturiert den Inhalt.
54. Diese Zeile definiert den Abschnitt '1. Neue Datei anlegen, z. B. 'app/i18n/locales/it.json''.
55. Diese Zeile definiert den Abschnitt '2. Alle benoetigten Keys ergaenzen'.
56. Diese Zeile definiert den Abschnitt '3. In 'app/i18n/service.py':'.
57. Diese Zeile definiert den Abschnitt '- 'SUPPORTED_LANGS' erweitern'.
58. Diese Zeile definiert den Abschnitt '- 'LANG_LABELS' erweitern'.
59. Diese Zeile definiert den Abschnitt '4. App neu starten'.
60. Diese Zeile ist leer und strukturiert den Inhalt.
61. Diese Zeile definiert den Abschnitt '## Wichtige Keys (Auszug)'.
62. Diese Zeile ist leer und strukturiert den Inhalt.
63. Diese Zeile definiert den Abschnitt '- 'nav.discover''.
64. Diese Zeile definiert den Abschnitt '- 'nav.submit''.
65. Diese Zeile definiert den Abschnitt '- 'nav.admin''.
66. Diese Zeile definiert den Abschnitt '- 'discover.title''.
67. Diese Zeile definiert den Abschnitt '- 'discover.filter.title_contains''.
68. Diese Zeile definiert den Abschnitt '- 'discover.filter.category''.
69. Diese Zeile definiert den Abschnitt '- 'discover.filter.difficulty''.
70. Diese Zeile definiert den Abschnitt '- 'discover.filter.ingredient''.
71. Diese Zeile definiert den Abschnitt '- 'discover.filter.apply''.
72. Diese Zeile definiert den Abschnitt '- 'discover.sort.newest''.
73. Diese Zeile definiert den Abschnitt '- 'discover.sort.oldest''.
74. Diese Zeile definiert den Abschnitt '- 'discover.sort.rating_desc''.
75. Diese Zeile definiert den Abschnitt '- 'discover.sort.rating_asc''.
76. Diese Zeile definiert den Abschnitt '- 'discover.sort.prep_time''.
77. Diese Zeile definiert den Abschnitt '- 'pagination.prev''.
78. Diese Zeile definiert den Abschnitt '- 'pagination.next''.
79. Diese Zeile definiert den Abschnitt '- 'empty.no_recipes''.
80. Diese Zeile definiert den Abschnitt '- 'auth.login''.
81. Diese Zeile definiert den Abschnitt '- 'auth.register''.
82. Diese Zeile definiert den Abschnitt '- 'admin.title''.
83. Diese Zeile definiert den Abschnitt '- 'moderation.title''.
84. Diese Zeile definiert den Abschnitt '- 'moderation.pending''.
85. Diese Zeile definiert den Abschnitt '- 'moderation.approve''.
86. Diese Zeile definiert den Abschnitt '- 'moderation.reject''.
87. Diese Zeile definiert den Abschnitt '- 'difficulty.easy''.
88. Diese Zeile definiert den Abschnitt '- 'difficulty.medium''.
89. Diese Zeile definiert den Abschnitt '- 'difficulty.hard''.

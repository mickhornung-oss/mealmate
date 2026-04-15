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

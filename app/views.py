from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import pass_context
from urllib.parse import urlsplit

from app.i18n import datetime_de, difficulty_label, role_label, submission_status_label, t
from app.i18n.service import available_langs
from app.nav import build_nav_items


class MealMateTemplates(Jinja2Templates):
    def TemplateResponse(self, *args, **kwargs):
        if args and isinstance(args[0], str):
            name = args[0]
            context = args[1] if len(args) > 1 else kwargs.get("context")
            if isinstance(context, dict) and context.get("request") is not None:
                request = context["request"]
                return super().TemplateResponse(
                    request,
                    name,
                    context,
                    status_code=kwargs.get("status_code", 200),
                    headers=kwargs.get("headers"),
                    media_type=kwargs.get("media_type"),
                    background=kwargs.get("background"),
                )
        return super().TemplateResponse(*args, **kwargs)


templates = MealMateTemplates(directory="app/templates")


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
    updated = request.url.include_query_params(lang=code)
    query = updated.query
    if query:
        return f"{updated.path}?{query}"
    return updated.path


templates.env.globals["t"] = jinja_t
templates.env.globals["difficulty_label"] = jinja_difficulty_label
templates.env.globals["role_label"] = jinja_role_label
templates.env.globals["submission_status_label"] = jinja_submission_status_label
templates.env.globals["available_langs"] = available_langs()
templates.env.globals["lang_url"] = lang_url
templates.env.globals["get_nav_items"] = build_nav_items
templates.env.filters["datetime_de"] = jinja_datetime_label


def redirect(url: str, status_code: int = 303) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status_code)


def safe_redirect_path(next_value: str | None, default: str = "/") -> str:
    candidate = (next_value or "").strip()
    if not candidate:
        return default
    if "\r" in candidate or "\n" in candidate:
        return default
    if candidate.startswith("//"):
        return default
    if not candidate.startswith("/"):
        return default
    if candidate.startswith("\\"):
        return default
    parsed = urlsplit(candidate)
    if parsed.scheme or parsed.netloc:
        return default
    path = parsed.path if parsed.path.startswith("/") else default
    if path.startswith("//"):
        return default
    if parsed.query:
        return f"{path}?{parsed.query}"
    return path

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

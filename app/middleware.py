import logging
import secrets
import time
import uuid
from urllib.parse import parse_qs

from fastapi import Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.i18n import t

logger = logging.getLogger("mealmate.request")

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
CSRF_EXEMPT_PREFIXES = ("/health", "/healthz", "/static")


def _build_receive(body: bytes):
    sent = False

    async def receive():
        nonlocal sent
        if sent:
            return {"type": "http.request", "body": b"", "more_body": False}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    return receive


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
        request.state.request_id = request_id
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            logger.exception(
                "request_failed request_id=%s method=%s path=%s",
                request_id,
                request.method,
                request.url.path,
            )
            raise
        duration_ms = (time.perf_counter() - started) * 1000
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request_complete request_id=%s method=%s path=%s status=%s duration_ms=%.2f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


class CSRFMiddleware(BaseHTTPMiddleware):
    def _is_exempt(self, path: str) -> bool:
        return path.startswith(CSRF_EXEMPT_PREFIXES)

    async def _extract_csrf_from_request(self, request: Request, csrf_header_name: str) -> str:
        provided = request.headers.get(csrf_header_name)
        if provided:
            return provided
        content_type = (request.headers.get("content-type") or "").lower()
        if "application/x-www-form-urlencoded" not in content_type and "multipart/form-data" not in content_type:
            return ""
        body = await request.body()
        request._receive = _build_receive(body)
        if "application/x-www-form-urlencoded" in content_type:
            parsed = parse_qs(body.decode("utf-8", errors="ignore"), keep_blank_values=True)
            values = parsed.get("csrf_token", [""])
            return str(values[0] or "")
        try:
            form = await request.form()
        except Exception:
            return ""
        finally:
            request._receive = _build_receive(body)
        return str(form.get("csrf_token") or "")

    async def dispatch(self, request: Request, call_next):
        runtime_settings = get_settings()
        path = request.url.path
        cookie_name = runtime_settings.csrf_cookie_name
        csrf_cookie = request.cookies.get(cookie_name)
        if request.method in SAFE_METHODS:
            request.state.csrf_token = csrf_cookie or secrets.token_urlsafe(32)
        elif not self._is_exempt(path):
            provided = await self._extract_csrf_from_request(request, runtime_settings.csrf_header_name)
            if not csrf_cookie or not provided or not secrets.compare_digest(provided, csrf_cookie):
                return PlainTextResponse(t("error.csrf_failed"), status_code=403)
            request.state.csrf_token = csrf_cookie
        response = await call_next(request)
        if request.method in SAFE_METHODS and not self._is_exempt(path):
            token = getattr(request.state, "csrf_token", None) or secrets.token_urlsafe(32)
            response.set_cookie(
                key=cookie_name,
                value=token,
                httponly=False,
                secure=runtime_settings.resolved_cookie_secure,
                samesite="lax",
                max_age=60 * 60 * 24,
                path="/",
            )
        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        runtime_settings = get_settings()
        if runtime_settings.prod_mode and runtime_settings.resolved_force_https and request.url.scheme != "https":
            target_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(target_url), status_code=307)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        runtime_settings = get_settings()
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        img_src = runtime_settings.csp_img_src.strip() or "'self' data: https:"
        csp_parts = [
            "default-src 'self'",
            f"img-src {img_src}",
            "style-src 'self'",
            "script-src 'self'",
            "object-src 'none'",
            "base-uri 'self'",
            "frame-ancestors 'none'",
        ]
        response.headers.setdefault("Content-Security-Policy", "; ".join(csp_parts))
        if runtime_settings.prod_mode and request.url.scheme == "https":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response

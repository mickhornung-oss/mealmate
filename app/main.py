import logging
import traceback
from contextlib import asynccontextmanager
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
from app.routers import admin, auth, legal, recipes, submissions, translations
from app.security import hash_password
from app.services import import_kochwiki_csv, is_meta_true, set_meta_value
from app.translation_service import register_translation_event_hooks
from app import translation_models  # noqa: F401
from app.views import templates

settings = get_settings()
configure_logging()
logger = logging.getLogger("mealmate.app")
register_translation_event_hooks()


class CacheControlStaticFiles(StaticFiles):
    def __init__(self, *args, cache_control: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_control = cache_control

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if self.cache_control and response.status_code == 200:
            response.headers.setdefault("Cache-Control", self.cache_control)
        return response


@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    _ = app_instance
    run_auto_seed_if_enabled()
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", debug=False, lifespan=lifespan)


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
app.include_router(translations.router)
app.include_router(legal.router)


def _apply_security_headers(request: Request, response):
    runtime_settings = get_settings()
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


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    accept = request.headers.get("accept", "")
    if exc.status_code == 404 and "text/html" in accept:
        response = templates.TemplateResponse(
            "error_404.html",
            template_context(request, None, title=t("error.404_title", request=request)),
            status_code=404,
        )
        return _apply_security_headers(request, response)
    detail = translate_error_message(exc.detail, request=request)
    response = JSONResponse({"detail": detail}, status_code=exc.status_code)
    return _apply_security_headers(request, response)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    runtime_settings = get_settings()
    is_prod_mode = bool(settings.prod_mode or runtime_settings.prod_mode)
    request_id = getattr(request.state, "request_id", "-")
    logger.exception("unhandled_exception request_id=%s path=%s", request_id, request.url.path)
    accept = request.headers.get("accept", "")
    if is_prod_mode:
        if "text/html" in accept:
            response = templates.TemplateResponse(
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
            return _apply_security_headers(request, response)
        response = JSONResponse({"detail": t("error.internal", request=request)}, status_code=500)
        return _apply_security_headers(request, response)
    trace = traceback.format_exc()
    if "text/html" in accept:
        response = templates.TemplateResponse(
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
        return _apply_security_headers(request, response)
    response = JSONResponse({"detail": t("error.internal", request=request), "trace": trace}, status_code=500)
    return _apply_security_headers(request, response)


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


@app.get("/health")
@app.get("/healthz")
def healthcheck():
    return {"status": "ok"}

# DELIVERABLE_IMAGE_FALLBACK_UPLOAD_MODERATION

## Betroffene Dateien

- .env.example
- app/config.py
- app/middleware.py
- app/models.py
- app/image_utils.py
- app/routers/recipes.py
- app/routers/admin.py
- app/templates/admin.html
- app/templates/partials/recipe_list.html
- app/templates/partials/recipe_images.html
- app/templates/partials/recipe_card_image.html
- app/templates/admin_image_change_requests.html
- app/templates/admin_image_change_request_detail.html
- app/static/style.css
- app/i18n/locales/de.json
- app/i18n/locales/en.json
- app/i18n/locales/fr.json
- alembic/versions/20260303_0009_recipe_image_change_requests.py
- tests/test_image_change_workflow.py

## .env.example

```text
APP_NAME=MealMate
APP_ENV=dev
APP_URL=http://localhost:8000
SECRET_KEY=change-this-in-production
ALGORITHM=HS256
TOKEN_EXPIRE_MINUTES=60
# DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/mealmate
DATABASE_URL=sqlite:///./mealmate.db
ALLOWED_HOSTS=*
COOKIE_SECURE=0
FORCE_HTTPS=0
LOG_LEVEL=INFO
CSP_IMG_SRC='self' data: https:
CSRF_COOKIE_NAME=csrf_token
CSRF_HEADER_NAME=X-CSRF-Token
PASSWORD_RESET_TOKEN_MINUTES=30
MAX_UPLOAD_MB=4
MAX_CSV_UPLOAD_MB=10
ALLOWED_IMAGE_TYPES=image/png,image/jpeg,image/webp
MAIL_OUTBOX_PATH=outbox/reset_links.txt
MAIL_OUTBOX_EMAIL_CHANGE_PATH=outbox/email_change_links.txt
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=no-reply@mealmate.local
SECURITY_EVENT_RETENTION_DAYS=30
SECURITY_EVENT_MAX_ROWS=5000
ENABLE_KOCHWIKI_SEED=0
AUTO_SEED_KOCHWIKI=0
KOCHWIKI_CSV_PATH=rezepte_kochwiki_clean_3713.csv
IMPORT_DOWNLOAD_IMAGES=0
SEED_ADMIN_EMAIL=admin@mealmate.local
SEED_ADMIN_PASSWORD=AdminPass123!

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'APP_NAME=MealMate'.
2. Diese Zeile enthält den Code 'APP_ENV=dev'.
3. Diese Zeile enthält den Code 'APP_URL=http://localhost:8000'.
4. Diese Zeile enthält den Code 'SECRET_KEY=change-this-in-production'.
5. Diese Zeile enthält den Code 'ALGORITHM=HS256'.
6. Diese Zeile enthält den Code 'TOKEN_EXPIRE_MINUTES=60'.
7. Diese Zeile enthält den Code '# DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/mealmate'.
8. Diese Zeile enthält den Code 'DATABASE_URL=sqlite:///./mealmate.db'.
9. Diese Zeile enthält den Code 'ALLOWED_HOSTS=*'.
10. Diese Zeile enthält den Code 'COOKIE_SECURE=0'.
11. Diese Zeile enthält den Code 'FORCE_HTTPS=0'.
12. Diese Zeile enthält den Code 'LOG_LEVEL=INFO'.
13. Diese Zeile enthält den Code 'CSP_IMG_SRC='self' data: https:'.
14. Diese Zeile enthält den Code 'CSRF_COOKIE_NAME=csrf_token'.
15. Diese Zeile enthält den Code 'CSRF_HEADER_NAME=X-CSRF-Token'.
16. Diese Zeile enthält den Code 'PASSWORD_RESET_TOKEN_MINUTES=30'.
17. Diese Zeile enthält den Code 'MAX_UPLOAD_MB=4'.
18. Diese Zeile enthält den Code 'MAX_CSV_UPLOAD_MB=10'.
19. Diese Zeile enthält den Code 'ALLOWED_IMAGE_TYPES=image/png,image/jpeg,image/webp'.
20. Diese Zeile enthält den Code 'MAIL_OUTBOX_PATH=outbox/reset_links.txt'.
21. Diese Zeile enthält den Code 'MAIL_OUTBOX_EMAIL_CHANGE_PATH=outbox/email_change_links.txt'.
22. Diese Zeile enthält den Code 'SMTP_HOST='.
23. Diese Zeile enthält den Code 'SMTP_PORT=587'.
24. Diese Zeile enthält den Code 'SMTP_USER='.
25. Diese Zeile enthält den Code 'SMTP_PASSWORD='.
26. Diese Zeile enthält den Code 'SMTP_FROM=no-reply@mealmate.local'.
27. Diese Zeile enthält den Code 'SECURITY_EVENT_RETENTION_DAYS=30'.
28. Diese Zeile enthält den Code 'SECURITY_EVENT_MAX_ROWS=5000'.
29. Diese Zeile enthält den Code 'ENABLE_KOCHWIKI_SEED=0'.
30. Diese Zeile enthält den Code 'AUTO_SEED_KOCHWIKI=0'.
31. Diese Zeile enthält den Code 'KOCHWIKI_CSV_PATH=rezepte_kochwiki_clean_3713.csv'.
32. Diese Zeile enthält den Code 'IMPORT_DOWNLOAD_IMAGES=0'.
33. Diese Zeile enthält den Code 'SEED_ADMIN_EMAIL=admin@mealmate.local'.
34. Diese Zeile enthält den Code 'SEED_ADMIN_PASSWORD=AdminPass123!'.

## app/config.py

```python
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    app_name: str = "MealMate"
    app_env: Literal["dev", "prod"] = "dev"
    app_url: AnyHttpUrl = "http://localhost:8000"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    token_expire_minutes: int = 60
    database_url: str = "sqlite:///./mealmate.db"
    allowed_hosts: Annotated[list[str], NoDecode] = ["*"]
    cookie_secure: bool | None = None
    force_https: bool | None = None
    log_level: str = "INFO"
    csp_img_src: str = "'self' data: https:"
    csrf_cookie_name: str = "csrf_token"
    csrf_header_name: str = "X-CSRF-Token"
    password_reset_token_minutes: int = 30
    max_upload_mb: int = 4
    max_csv_upload_mb: int = 10
    allowed_image_types: Annotated[list[str], NoDecode] = ["image/png", "image/jpeg", "image/webp"]
    mail_outbox_path: str = "outbox/reset_links.txt"
    mail_outbox_email_change_path: str = "outbox/email_change_links.txt"
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "no-reply@mealmate.local"
    security_event_retention_days: int = 30
    security_event_max_rows: int = 5000
    enable_kochwiki_seed: bool = False
    auto_seed_kochwiki: bool = False
    kochwiki_csv_path: str = "rezepte_kochwiki_clean_3713.csv"
    import_download_images: bool = False
    seed_admin_email: str = "admin@mealmate.local"
    seed_admin_password: str = "AdminPass123!"

    @field_validator("allowed_image_types", mode="before")
    @classmethod
    def parse_allowed_image_types(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return [item.strip() for item in value if item.strip()]
        return [item.strip() for item in value.split(",") if item.strip()]

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            hosts = [item.strip() for item in value if item.strip()]
        else:
            hosts = [item.strip() for item in value.split(",") if item.strip()]
        return hosts or ["*"]

    @field_validator("log_level", mode="before")
    @classmethod
    def parse_log_level(cls, value: str) -> str:
        return str(value).strip().upper() or "INFO"

    @property
    def sqlalchemy_database_url(self) -> str:
        url = self.database_url.strip()
        if url.startswith("postgres://"):
            return "postgresql+psycopg://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            return "postgresql+psycopg://" + url[len("postgresql://") :]
        return url

    @property
    def is_sqlite(self) -> bool:
        return self.sqlalchemy_database_url.startswith("sqlite")

    @property
    def prod_mode(self) -> bool:
        return self.app_env == "prod"

    @property
    def resolved_cookie_secure(self) -> bool:
        if self.cookie_secure is None:
            return self.prod_mode
        return self.cookie_secure

    @property
    def resolved_force_https(self) -> bool:
        if self.force_https is None:
            return self.prod_mode
        return self.force_https


@lru_cache
def get_settings() -> Settings:
    return Settings()

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'from functools import lru_cache'.
2. Diese Zeile enthält den Code 'from typing import Annotated, Literal'.
3. Diese Zeile ist leer und trennt Abschnitte.
4. Diese Zeile enthält den Code 'from pydantic import AnyHttpUrl, field_validator'.
5. Diese Zeile enthält den Code 'from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict'.
6. Diese Zeile ist leer und trennt Abschnitte.
7. Diese Zeile ist leer und trennt Abschnitte.
8. Diese Zeile enthält den Code 'class Settings(BaseSettings):'.
9. Diese Zeile enthält den Code 'model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", cas...'.
10. Diese Zeile ist leer und trennt Abschnitte.
11. Diese Zeile enthält den Code 'app_name: str = "MealMate"'.
12. Diese Zeile enthält den Code 'app_env: Literal["dev", "prod"] = "dev"'.
13. Diese Zeile enthält den Code 'app_url: AnyHttpUrl = "http://localhost:8000"'.
14. Diese Zeile enthält den Code 'secret_key: str = "change-me"'.
15. Diese Zeile enthält den Code 'algorithm: str = "HS256"'.
16. Diese Zeile enthält den Code 'token_expire_minutes: int = 60'.
17. Diese Zeile enthält den Code 'database_url: str = "sqlite:///./mealmate.db"'.
18. Diese Zeile enthält den Code 'allowed_hosts: Annotated[list[str], NoDecode] = ["*"]'.
19. Diese Zeile enthält den Code 'cookie_secure: bool | None = None'.
20. Diese Zeile enthält den Code 'force_https: bool | None = None'.
21. Diese Zeile enthält den Code 'log_level: str = "INFO"'.
22. Diese Zeile enthält den Code 'csp_img_src: str = "'self' data: https:"'.
23. Diese Zeile enthält den Code 'csrf_cookie_name: str = "csrf_token"'.
24. Diese Zeile enthält den Code 'csrf_header_name: str = "X-CSRF-Token"'.
25. Diese Zeile enthält den Code 'password_reset_token_minutes: int = 30'.
26. Diese Zeile enthält den Code 'max_upload_mb: int = 4'.
27. Diese Zeile enthält den Code 'max_csv_upload_mb: int = 10'.
28. Diese Zeile enthält den Code 'allowed_image_types: Annotated[list[str], NoDecode] = ["image/png", "image/jpeg", "image/webp"]'.
29. Diese Zeile enthält den Code 'mail_outbox_path: str = "outbox/reset_links.txt"'.
30. Diese Zeile enthält den Code 'mail_outbox_email_change_path: str = "outbox/email_change_links.txt"'.
31. Diese Zeile enthält den Code 'smtp_host: str | None = None'.
32. Diese Zeile enthält den Code 'smtp_port: int = 587'.
33. Diese Zeile enthält den Code 'smtp_user: str | None = None'.
34. Diese Zeile enthält den Code 'smtp_password: str | None = None'.
35. Diese Zeile enthält den Code 'smtp_from: str = "no-reply@mealmate.local"'.
36. Diese Zeile enthält den Code 'security_event_retention_days: int = 30'.
37. Diese Zeile enthält den Code 'security_event_max_rows: int = 5000'.
38. Diese Zeile enthält den Code 'enable_kochwiki_seed: bool = False'.
39. Diese Zeile enthält den Code 'auto_seed_kochwiki: bool = False'.
40. Diese Zeile enthält den Code 'kochwiki_csv_path: str = "rezepte_kochwiki_clean_3713.csv"'.
41. Diese Zeile enthält den Code 'import_download_images: bool = False'.
42. Diese Zeile enthält den Code 'seed_admin_email: str = "admin@mealmate.local"'.
43. Diese Zeile enthält den Code 'seed_admin_password: str = "AdminPass123!"'.
44. Diese Zeile ist leer und trennt Abschnitte.
45. Diese Zeile enthält den Code '@field_validator("allowed_image_types", mode="before")'.
46. Diese Zeile enthält den Code '@classmethod'.
47. Diese Zeile enthält den Code 'def parse_allowed_image_types(cls, value: str | list[str]) -> list[str]:'.
48. Diese Zeile enthält den Code 'if isinstance(value, list):'.
49. Diese Zeile enthält den Code 'return [item.strip() for item in value if item.strip()]'.
50. Diese Zeile enthält den Code 'return [item.strip() for item in value.split(",") if item.strip()]'.
51. Diese Zeile ist leer und trennt Abschnitte.
52. Diese Zeile enthält den Code '@field_validator("allowed_hosts", mode="before")'.
53. Diese Zeile enthält den Code '@classmethod'.
54. Diese Zeile enthält den Code 'def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:'.
55. Diese Zeile enthält den Code 'if isinstance(value, list):'.
56. Diese Zeile enthält den Code 'hosts = [item.strip() for item in value if item.strip()]'.
57. Diese Zeile enthält den Code 'else:'.
58. Diese Zeile enthält den Code 'hosts = [item.strip() for item in value.split(",") if item.strip()]'.
59. Diese Zeile enthält den Code 'return hosts or ["*"]'.
60. Diese Zeile ist leer und trennt Abschnitte.
61. Diese Zeile enthält den Code '@field_validator("log_level", mode="before")'.
62. Diese Zeile enthält den Code '@classmethod'.
63. Diese Zeile enthält den Code 'def parse_log_level(cls, value: str) -> str:'.
64. Diese Zeile enthält den Code 'return str(value).strip().upper() or "INFO"'.
65. Diese Zeile ist leer und trennt Abschnitte.
66. Diese Zeile enthält den Code '@property'.
67. Diese Zeile enthält den Code 'def sqlalchemy_database_url(self) -> str:'.
68. Diese Zeile enthält den Code 'url = self.database_url.strip()'.
69. Diese Zeile enthält den Code 'if url.startswith("postgres://"):'.
70. Diese Zeile enthält den Code 'return "postgresql+psycopg://" + url[len("postgres://") :]'.
71. Diese Zeile enthält den Code 'if url.startswith("postgresql://"):'.
72. Diese Zeile enthält den Code 'return "postgresql+psycopg://" + url[len("postgresql://") :]'.
73. Diese Zeile enthält den Code 'return url'.
74. Diese Zeile ist leer und trennt Abschnitte.
75. Diese Zeile enthält den Code '@property'.
76. Diese Zeile enthält den Code 'def is_sqlite(self) -> bool:'.
77. Diese Zeile enthält den Code 'return self.sqlalchemy_database_url.startswith("sqlite")'.
78. Diese Zeile ist leer und trennt Abschnitte.
79. Diese Zeile enthält den Code '@property'.
80. Diese Zeile enthält den Code 'def prod_mode(self) -> bool:'.
81. Diese Zeile enthält den Code 'return self.app_env == "prod"'.
82. Diese Zeile ist leer und trennt Abschnitte.
83. Diese Zeile enthält den Code '@property'.
84. Diese Zeile enthält den Code 'def resolved_cookie_secure(self) -> bool:'.
85. Diese Zeile enthält den Code 'if self.cookie_secure is None:'.
86. Diese Zeile enthält den Code 'return self.prod_mode'.
87. Diese Zeile enthält den Code 'return self.cookie_secure'.
88. Diese Zeile ist leer und trennt Abschnitte.
89. Diese Zeile enthält den Code '@property'.
90. Diese Zeile enthält den Code 'def resolved_force_https(self) -> bool:'.
91. Diese Zeile enthält den Code 'if self.force_https is None:'.
92. Diese Zeile enthält den Code 'return self.prod_mode'.
93. Diese Zeile enthält den Code 'return self.force_https'.
94. Diese Zeile ist leer und trennt Abschnitte.
95. Diese Zeile ist leer und trennt Abschnitte.
96. Diese Zeile enthält den Code '@lru_cache'.
97. Diese Zeile enthält den Code 'def get_settings() -> Settings:'.
98. Diese Zeile enthält den Code 'return Settings()'.

## app/middleware.py

```python
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

settings = get_settings()
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

    async def _extract_csrf_from_request(self, request: Request) -> str:
        provided = request.headers.get(settings.csrf_header_name)
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
        path = request.url.path
        cookie_name = settings.csrf_cookie_name
        csrf_cookie = request.cookies.get(cookie_name)
        if request.method in SAFE_METHODS:
            request.state.csrf_token = csrf_cookie or secrets.token_urlsafe(32)
        elif not self._is_exempt(path):
            provided = await self._extract_csrf_from_request(request)
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
                secure=settings.resolved_cookie_secure,
                samesite="lax",
                max_age=60 * 60 * 24,
                path="/",
            )
        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if settings.prod_mode and settings.resolved_force_https and request.url.scheme != "https":
            target_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(target_url), status_code=307)
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        img_src = settings.csp_img_src.strip() or "'self' data: https:"
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
        if settings.prod_mode and request.url.scheme == "https":
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'import logging'.
2. Diese Zeile enthält den Code 'import secrets'.
3. Diese Zeile enthält den Code 'import time'.
4. Diese Zeile enthält den Code 'import uuid'.
5. Diese Zeile enthält den Code 'from urllib.parse import parse_qs'.
6. Diese Zeile ist leer und trennt Abschnitte.
7. Diese Zeile enthält den Code 'from fastapi import Request'.
8. Diese Zeile enthält den Code 'from fastapi.responses import PlainTextResponse, RedirectResponse'.
9. Diese Zeile enthält den Code 'from starlette.middleware.base import BaseHTTPMiddleware'.
10. Diese Zeile ist leer und trennt Abschnitte.
11. Diese Zeile enthält den Code 'from app.config import get_settings'.
12. Diese Zeile enthält den Code 'from app.i18n import t'.
13. Diese Zeile ist leer und trennt Abschnitte.
14. Diese Zeile enthält den Code 'settings = get_settings()'.
15. Diese Zeile enthält den Code 'logger = logging.getLogger("mealmate.request")'.
16. Diese Zeile ist leer und trennt Abschnitte.
17. Diese Zeile enthält den Code 'SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}'.
18. Diese Zeile enthält den Code 'CSRF_EXEMPT_PREFIXES = ("/health", "/healthz", "/static")'.
19. Diese Zeile ist leer und trennt Abschnitte.
20. Diese Zeile ist leer und trennt Abschnitte.
21. Diese Zeile enthält den Code 'def _build_receive(body: bytes):'.
22. Diese Zeile enthält den Code 'sent = False'.
23. Diese Zeile ist leer und trennt Abschnitte.
24. Diese Zeile enthält den Code 'async def receive():'.
25. Diese Zeile enthält den Code 'nonlocal sent'.
26. Diese Zeile enthält den Code 'if sent:'.
27. Diese Zeile enthält den Code 'return {"type": "http.request", "body": b"", "more_body": False}'.
28. Diese Zeile enthält den Code 'sent = True'.
29. Diese Zeile enthält den Code 'return {"type": "http.request", "body": body, "more_body": False}'.
30. Diese Zeile ist leer und trennt Abschnitte.
31. Diese Zeile enthält den Code 'return receive'.
32. Diese Zeile ist leer und trennt Abschnitte.
33. Diese Zeile ist leer und trennt Abschnitte.
34. Diese Zeile enthält den Code 'class RequestContextMiddleware(BaseHTTPMiddleware):'.
35. Diese Zeile enthält den Code 'async def dispatch(self, request: Request, call_next):'.
36. Diese Zeile enthält den Code 'request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex'.
37. Diese Zeile enthält den Code 'request.state.request_id = request_id'.
38. Diese Zeile enthält den Code 'started = time.perf_counter()'.
39. Diese Zeile enthält den Code 'try:'.
40. Diese Zeile enthält den Code 'response = await call_next(request)'.
41. Diese Zeile enthält den Code 'except Exception:'.
42. Diese Zeile enthält den Code 'logger.exception('.
43. Diese Zeile enthält den Code '"request_failed request_id=%s method=%s path=%s",'.
44. Diese Zeile enthält den Code 'request_id,'.
45. Diese Zeile enthält den Code 'request.method,'.
46. Diese Zeile enthält den Code 'request.url.path,'.
47. Diese Zeile enthält den Code ')'.
48. Diese Zeile enthält den Code 'raise'.
49. Diese Zeile enthält den Code 'duration_ms = (time.perf_counter() - started) * 1000'.
50. Diese Zeile enthält den Code 'response.headers["X-Request-ID"] = request_id'.
51. Diese Zeile enthält den Code 'logger.info('.
52. Diese Zeile enthält den Code '"request_complete request_id=%s method=%s path=%s status=%s duration_ms=%.2f",'.
53. Diese Zeile enthält den Code 'request_id,'.
54. Diese Zeile enthält den Code 'request.method,'.
55. Diese Zeile enthält den Code 'request.url.path,'.
56. Diese Zeile enthält den Code 'response.status_code,'.
57. Diese Zeile enthält den Code 'duration_ms,'.
58. Diese Zeile enthält den Code ')'.
59. Diese Zeile enthält den Code 'return response'.
60. Diese Zeile ist leer und trennt Abschnitte.
61. Diese Zeile ist leer und trennt Abschnitte.
62. Diese Zeile enthält den Code 'class CSRFMiddleware(BaseHTTPMiddleware):'.
63. Diese Zeile enthält den Code 'def _is_exempt(self, path: str) -> bool:'.
64. Diese Zeile enthält den Code 'return path.startswith(CSRF_EXEMPT_PREFIXES)'.
65. Diese Zeile ist leer und trennt Abschnitte.
66. Diese Zeile enthält den Code 'async def _extract_csrf_from_request(self, request: Request) -> str:'.
67. Diese Zeile enthält den Code 'provided = request.headers.get(settings.csrf_header_name)'.
68. Diese Zeile enthält den Code 'if provided:'.
69. Diese Zeile enthält den Code 'return provided'.
70. Diese Zeile enthält den Code 'content_type = (request.headers.get("content-type") or "").lower()'.
71. Diese Zeile enthält den Code 'if "application/x-www-form-urlencoded" not in content_type and "multipart/form-data" not in conte...'.
72. Diese Zeile enthält den Code 'return ""'.
73. Diese Zeile enthält den Code 'body = await request.body()'.
74. Diese Zeile enthält den Code 'request._receive = _build_receive(body)'.
75. Diese Zeile enthält den Code 'if "application/x-www-form-urlencoded" in content_type:'.
76. Diese Zeile enthält den Code 'parsed = parse_qs(body.decode("utf-8", errors="ignore"), keep_blank_values=True)'.
77. Diese Zeile enthält den Code 'values = parsed.get("csrf_token", [""])'.
78. Diese Zeile enthält den Code 'return str(values[0] or "")'.
79. Diese Zeile enthält den Code 'try:'.
80. Diese Zeile enthält den Code 'form = await request.form()'.
81. Diese Zeile enthält den Code 'except Exception:'.
82. Diese Zeile enthält den Code 'return ""'.
83. Diese Zeile enthält den Code 'finally:'.
84. Diese Zeile enthält den Code 'request._receive = _build_receive(body)'.
85. Diese Zeile enthält den Code 'return str(form.get("csrf_token") or "")'.
86. Diese Zeile ist leer und trennt Abschnitte.
87. Diese Zeile enthält den Code 'async def dispatch(self, request: Request, call_next):'.
88. Diese Zeile enthält den Code 'path = request.url.path'.
89. Diese Zeile enthält den Code 'cookie_name = settings.csrf_cookie_name'.
90. Diese Zeile enthält den Code 'csrf_cookie = request.cookies.get(cookie_name)'.
91. Diese Zeile enthält den Code 'if request.method in SAFE_METHODS:'.
92. Diese Zeile enthält den Code 'request.state.csrf_token = csrf_cookie or secrets.token_urlsafe(32)'.
93. Diese Zeile enthält den Code 'elif not self._is_exempt(path):'.
94. Diese Zeile enthält den Code 'provided = await self._extract_csrf_from_request(request)'.
95. Diese Zeile enthält den Code 'if not csrf_cookie or not provided or not secrets.compare_digest(provided, csrf_cookie):'.
96. Diese Zeile enthält den Code 'return PlainTextResponse(t("error.csrf_failed"), status_code=403)'.
97. Diese Zeile enthält den Code 'request.state.csrf_token = csrf_cookie'.
98. Diese Zeile enthält den Code 'response = await call_next(request)'.
99. Diese Zeile enthält den Code 'if request.method in SAFE_METHODS and not self._is_exempt(path):'.
100. Diese Zeile enthält den Code 'token = getattr(request.state, "csrf_token", None) or secrets.token_urlsafe(32)'.
101. Diese Zeile enthält den Code 'response.set_cookie('.
102. Diese Zeile enthält den Code 'key=cookie_name,'.
103. Diese Zeile enthält den Code 'value=token,'.
104. Diese Zeile enthält den Code 'httponly=False,'.
105. Diese Zeile enthält den Code 'secure=settings.resolved_cookie_secure,'.
106. Diese Zeile enthält den Code 'samesite="lax",'.
107. Diese Zeile enthält den Code 'max_age=60 * 60 * 24,'.
108. Diese Zeile enthält den Code 'path="/",'.
109. Diese Zeile enthält den Code ')'.
110. Diese Zeile enthält den Code 'return response'.
111. Diese Zeile ist leer und trennt Abschnitte.
112. Diese Zeile ist leer und trennt Abschnitte.
113. Diese Zeile enthält den Code 'class HTTPSRedirectMiddleware(BaseHTTPMiddleware):'.
114. Diese Zeile enthält den Code 'async def dispatch(self, request: Request, call_next):'.
115. Diese Zeile enthält den Code 'if settings.prod_mode and settings.resolved_force_https and request.url.scheme != "https":'.
116. Diese Zeile enthält den Code 'target_url = request.url.replace(scheme="https")'.
117. Diese Zeile enthält den Code 'return RedirectResponse(url=str(target_url), status_code=307)'.
118. Diese Zeile enthält den Code 'return await call_next(request)'.
119. Diese Zeile ist leer und trennt Abschnitte.
120. Diese Zeile ist leer und trennt Abschnitte.
121. Diese Zeile enthält den Code 'class SecurityHeadersMiddleware(BaseHTTPMiddleware):'.
122. Diese Zeile enthält den Code 'async def dispatch(self, request: Request, call_next):'.
123. Diese Zeile enthält den Code 'response = await call_next(request)'.
124. Diese Zeile enthält den Code 'response.headers.setdefault("X-Content-Type-Options", "nosniff")'.
125. Diese Zeile enthält den Code 'response.headers.setdefault("X-Frame-Options", "DENY")'.
126. Diese Zeile enthält den Code 'response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")'.
127. Diese Zeile enthält den Code 'response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")'.
128. Diese Zeile enthält den Code 'img_src = settings.csp_img_src.strip() or "'self' data: https:"'.
129. Diese Zeile enthält den Code 'csp_parts = ['.
130. Diese Zeile enthält den Code '"default-src 'self'",'.
131. Diese Zeile enthält den Code 'f"img-src {img_src}",'.
132. Diese Zeile enthält den Code '"style-src 'self'",'.
133. Diese Zeile enthält den Code '"script-src 'self'",'.
134. Diese Zeile enthält den Code '"object-src 'none'",'.
135. Diese Zeile enthält den Code '"base-uri 'self'",'.
136. Diese Zeile enthält den Code '"frame-ancestors 'none'",'.
137. Diese Zeile enthält den Code ']'.
138. Diese Zeile enthält den Code 'response.headers.setdefault("Content-Security-Policy", "; ".join(csp_parts))'.
139. Diese Zeile enthält den Code 'if settings.prod_mode and request.url.scheme == "https":'.
140. Diese Zeile enthält den Code 'response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")'.
141. Diese Zeile enthält den Code 'return response'.

## app/models.py

```python
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, LargeBinary, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


SUBMISSION_STATUS_ENUM = Enum(
    "pending",
    "approved",
    "rejected",
    name="submission_status",
    native_enum=False,
)

IMAGE_CHANGE_STATUS_ENUM = Enum(
    "pending",
    "approved",
    "rejected",
    name="image_change_status",
    native_enum=False,
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_uid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=lambda: str(uuid4()), index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, index=True)
    username_normalized: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_login_user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    recipes: Mapped[list["Recipe"]] = relationship(back_populates="creator", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    submissions: Mapped[list["RecipeSubmission"]] = relationship(
        back_populates="submitter_user",
        cascade="all, delete-orphan",
        foreign_keys="RecipeSubmission.submitter_user_id",
    )
    reviewed_submissions: Mapped[list["RecipeSubmission"]] = relationship(
        back_populates="reviewed_by_admin",
        foreign_keys="RecipeSubmission.reviewed_by_admin_id",
    )
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    security_events: Mapped[list["SecurityEvent"]] = relationship(
        back_populates="user",
    )
    image_change_requests: Mapped[list["RecipeImageChangeRequest"]] = relationship(
        back_populates="requester_user",
        foreign_keys="RecipeImageChangeRequest.requester_user_id",
    )
    reviewed_image_change_requests: Mapped[list["RecipeImageChangeRequest"]] = relationship(
        back_populates="reviewed_by_admin",
        foreign_keys="RecipeImageChangeRequest.reviewed_by_admin_id",
    )


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    title_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="user", index=True)
    source_uuid: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True, index=True)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)
    total_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    prep_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    difficulty: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    creator: Mapped["User"] = relationship(back_populates="recipes")
    recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
    reviews: Mapped[list["Review"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    favorites: Mapped[list["Favorite"]] = relationship(back_populates="recipe", cascade="all, delete-orphan")
    images: Mapped[list["RecipeImage"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeImage.created_at",
    )
    image_change_requests: Mapped[list["RecipeImageChangeRequest"]] = relationship(
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by="RecipeImageChangeRequest.created_at",
    )


class Ingredient(Base):
    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)

    recipe_links: Mapped[list["RecipeIngredient"]] = relationship(
        back_populates="ingredient",
        cascade="all, delete-orphan",
    )


class RecipeIngredient(Base):
    __tablename__ = "recipe_ingredients"

    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"), primary_key=True)
    quantity_text: Mapped[str] = mapped_column(String(120), default="", nullable=False)
    grams: Mapped[int | None] = mapped_column(Integer, nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")
    ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_links")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_reviews_user_recipe"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="reviews")
    user: Mapped["User"] = relationship(back_populates="reviews")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_recipe"),)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    user: Mapped["User"] = relationship(back_populates="favorites")
    recipe: Mapped["Recipe"] = relationship(back_populates="favorites")


class RecipeImage(Base):
    __tablename__ = "recipe_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    recipe: Mapped["Recipe"] = relationship(back_populates="images")


class RecipeImageChangeRequest(Base):
    __tablename__ = "recipe_image_change_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False, index=True)
    requester_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        IMAGE_CHANGE_STATUS_ENUM,
        nullable=False,
        default="pending",
        server_default="pending",
        index=True,
    )
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    recipe: Mapped["Recipe"] = relationship(back_populates="image_change_requests")
    requester_user: Mapped["User"] = relationship(
        back_populates="image_change_requests",
        foreign_keys=[requester_user_id],
    )
    reviewed_by_admin: Mapped["User"] = relationship(
        back_populates="reviewed_image_change_requests",
        foreign_keys=[reviewed_by_admin_id],
    )
    files: Mapped[list["RecipeImageChangeFile"]] = relationship(
        back_populates="request",
        cascade="all, delete-orphan",
        order_by="RecipeImageChangeFile.created_at",
    )


class RecipeImageChangeFile(Base):
    __tablename__ = "recipe_image_change_files"
    __table_args__ = (UniqueConstraint("request_id", name="uq_recipe_image_change_files_request"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    request_id: Mapped[int] = mapped_column(
        ForeignKey("recipe_image_change_requests.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    request: Mapped["RecipeImageChangeRequest"] = relationship(back_populates="files")


class RecipeSubmission(Base):
    __tablename__ = "recipe_submissions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submitter_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    submitter_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)
    difficulty: Mapped[str] = mapped_column(String(30), nullable=False, default="medium", index=True)
    prep_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)
    instructions: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(SUBMISSION_STATUS_ENUM, nullable=False, default="pending", server_default="pending", index=True)
    admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)

    submitter_user: Mapped["User"] = relationship(
        back_populates="submissions",
        foreign_keys=[submitter_user_id],
    )
    reviewed_by_admin: Mapped["User"] = relationship(
        back_populates="reviewed_submissions",
        foreign_keys=[reviewed_by_admin_id],
    )
    ingredients: Mapped[list["SubmissionIngredient"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionIngredient.id",
    )
    images: Mapped[list["SubmissionImage"]] = relationship(
        back_populates="submission",
        cascade="all, delete-orphan",
        order_by="SubmissionImage.created_at",
    )


class SubmissionIngredient(Base):
    __tablename__ = "submission_ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    ingredient_name: Mapped[str] = mapped_column(String(200), nullable=False)
    quantity_text: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    grams: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ingredient_name_normalized: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)

    submission: Mapped["RecipeSubmission"] = relationship(back_populates="ingredients")


class SubmissionImage(Base):
    __tablename__ = "submission_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), nullable=False)
    data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)

    submission: Mapped["RecipeSubmission"] = relationship(back_populates="images")


class AppMeta(Base):
    __tablename__ = "app_meta"

    key: Mapped[str] = mapped_column(String(120), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    new_email_normalized: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    created_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)
    purpose: Mapped[str] = mapped_column(String(50), nullable=False, default="password_reset", index=True)

    user: Mapped["User"] = relationship(back_populates="password_reset_tokens")


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False, index=True)
    ip: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)
    details: Mapped[str | None] = mapped_column(String(300), nullable=True)

    user: Mapped["User"] = relationship(back_populates="security_events")

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'from datetime import datetime, timezone'.
2. Diese Zeile enthält den Code 'from uuid import uuid4'.
3. Diese Zeile ist leer und trennt Abschnitte.
4. Diese Zeile enthält den Code 'from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, LargeBinary, String, Text, U...'.
5. Diese Zeile enthält den Code 'from sqlalchemy.orm import Mapped, mapped_column, relationship'.
6. Diese Zeile ist leer und trennt Abschnitte.
7. Diese Zeile enthält den Code 'from app.database import Base'.
8. Diese Zeile ist leer und trennt Abschnitte.
9. Diese Zeile ist leer und trennt Abschnitte.
10. Diese Zeile enthält den Code 'def utc_now() -> datetime:'.
11. Diese Zeile enthält den Code 'return datetime.now(timezone.utc)'.
12. Diese Zeile ist leer und trennt Abschnitte.
13. Diese Zeile ist leer und trennt Abschnitte.
14. Diese Zeile enthält den Code 'SUBMISSION_STATUS_ENUM = Enum('.
15. Diese Zeile enthält den Code '"pending",'.
16. Diese Zeile enthält den Code '"approved",'.
17. Diese Zeile enthält den Code '"rejected",'.
18. Diese Zeile enthält den Code 'name="submission_status",'.
19. Diese Zeile enthält den Code 'native_enum=False,'.
20. Diese Zeile enthält den Code ')'.
21. Diese Zeile ist leer und trennt Abschnitte.
22. Diese Zeile enthält den Code 'IMAGE_CHANGE_STATUS_ENUM = Enum('.
23. Diese Zeile enthält den Code '"pending",'.
24. Diese Zeile enthält den Code '"approved",'.
25. Diese Zeile enthält den Code '"rejected",'.
26. Diese Zeile enthält den Code 'name="image_change_status",'.
27. Diese Zeile enthält den Code 'native_enum=False,'.
28. Diese Zeile enthält den Code ')'.
29. Diese Zeile ist leer und trennt Abschnitte.
30. Diese Zeile ist leer und trennt Abschnitte.
31. Diese Zeile enthält den Code 'class User(Base):'.
32. Diese Zeile enthält den Code '__tablename__ = "users"'.
33. Diese Zeile ist leer und trennt Abschnitte.
34. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
35. Diese Zeile enthält den Code 'user_uid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=lambda: st...'.
36. Diese Zeile enthält den Code 'email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)'.
37. Diese Zeile enthält den Code 'username: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, index=True)'.
38. Diese Zeile enthält den Code 'username_normalized: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, i...'.
39. Diese Zeile enthält den Code 'hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)'.
40. Diese Zeile enthält den Code 'role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)'.
41. Diese Zeile enthält den Code 'last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)'.
42. Diese Zeile enthält den Code 'last_login_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)'.
43. Diese Zeile enthält den Code 'last_login_user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)'.
44. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
45. Diese Zeile ist leer und trennt Abschnitte.
46. Diese Zeile enthält den Code 'recipes: Mapped[list["Recipe"]] = relationship(back_populates="creator", cascade="all, delete-orp...'.
47. Diese Zeile enthält den Code 'reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")'.
48. Diese Zeile enthält den Code 'favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete-or...'.
49. Diese Zeile enthält den Code 'submissions: Mapped[list["RecipeSubmission"]] = relationship('.
50. Diese Zeile enthält den Code 'back_populates="submitter_user",'.
51. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
52. Diese Zeile enthält den Code 'foreign_keys="RecipeSubmission.submitter_user_id",'.
53. Diese Zeile enthält den Code ')'.
54. Diese Zeile enthält den Code 'reviewed_submissions: Mapped[list["RecipeSubmission"]] = relationship('.
55. Diese Zeile enthält den Code 'back_populates="reviewed_by_admin",'.
56. Diese Zeile enthält den Code 'foreign_keys="RecipeSubmission.reviewed_by_admin_id",'.
57. Diese Zeile enthält den Code ')'.
58. Diese Zeile enthält den Code 'password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship('.
59. Diese Zeile enthält den Code 'back_populates="user",'.
60. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
61. Diese Zeile enthält den Code ')'.
62. Diese Zeile enthält den Code 'security_events: Mapped[list["SecurityEvent"]] = relationship('.
63. Diese Zeile enthält den Code 'back_populates="user",'.
64. Diese Zeile enthält den Code ')'.
65. Diese Zeile enthält den Code 'image_change_requests: Mapped[list["RecipeImageChangeRequest"]] = relationship('.
66. Diese Zeile enthält den Code 'back_populates="requester_user",'.
67. Diese Zeile enthält den Code 'foreign_keys="RecipeImageChangeRequest.requester_user_id",'.
68. Diese Zeile enthält den Code ')'.
69. Diese Zeile enthält den Code 'reviewed_image_change_requests: Mapped[list["RecipeImageChangeRequest"]] = relationship('.
70. Diese Zeile enthält den Code 'back_populates="reviewed_by_admin",'.
71. Diese Zeile enthält den Code 'foreign_keys="RecipeImageChangeRequest.reviewed_by_admin_id",'.
72. Diese Zeile enthält den Code ')'.
73. Diese Zeile ist leer und trennt Abschnitte.
74. Diese Zeile ist leer und trennt Abschnitte.
75. Diese Zeile enthält den Code 'class Recipe(Base):'.
76. Diese Zeile enthält den Code '__tablename__ = "recipes"'.
77. Diese Zeile ist leer und trennt Abschnitte.
78. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
79. Diese Zeile enthält den Code 'title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)'.
80. Diese Zeile enthält den Code 'title_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
81. Diese Zeile enthält den Code 'source: Mapped[str] = mapped_column(String(50), nullable=False, default="user", index=True)'.
82. Diese Zeile enthält den Code 'source_uuid: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True, index=True)'.
83. Diese Zeile enthält den Code 'source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
84. Diese Zeile enthält den Code 'source_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
85. Diese Zeile enthält den Code 'servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)'.
86. Diese Zeile enthält den Code 'total_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
87. Diese Zeile enthält den Code 'is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)'.
88. Diese Zeile enthält den Code 'description: Mapped[str] = mapped_column(Text, nullable=False)'.
89. Diese Zeile enthält den Code 'instructions: Mapped[str] = mapped_column(Text, nullable=False)'.
90. Diese Zeile enthält den Code 'category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)'.
91. Diese Zeile enthält den Code 'prep_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, index=True)'.
92. Diese Zeile enthält den Code 'difficulty: Mapped[str] = mapped_column(String(30), nullable=False, index=True)'.
93. Diese Zeile enthält den Code 'creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=Fals...'.
94. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
95. Diese Zeile ist leer und trennt Abschnitte.
96. Diese Zeile enthält den Code 'creator: Mapped["User"] = relationship(back_populates="recipes")'.
97. Diese Zeile enthält den Code 'recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship('.
98. Diese Zeile enthält den Code 'back_populates="recipe",'.
99. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
100. Diese Zeile enthält den Code ')'.
101. Diese Zeile enthält den Code 'reviews: Mapped[list["Review"]] = relationship(back_populates="recipe", cascade="all, delete-orph...'.
102. Diese Zeile enthält den Code 'favorites: Mapped[list["Favorite"]] = relationship(back_populates="recipe", cascade="all, delete-...'.
103. Diese Zeile enthält den Code 'images: Mapped[list["RecipeImage"]] = relationship('.
104. Diese Zeile enthält den Code 'back_populates="recipe",'.
105. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
106. Diese Zeile enthält den Code 'order_by="RecipeImage.created_at",'.
107. Diese Zeile enthält den Code ')'.
108. Diese Zeile enthält den Code 'image_change_requests: Mapped[list["RecipeImageChangeRequest"]] = relationship('.
109. Diese Zeile enthält den Code 'back_populates="recipe",'.
110. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
111. Diese Zeile enthält den Code 'order_by="RecipeImageChangeRequest.created_at",'.
112. Diese Zeile enthält den Code ')'.
113. Diese Zeile ist leer und trennt Abschnitte.
114. Diese Zeile ist leer und trennt Abschnitte.
115. Diese Zeile enthält den Code 'class Ingredient(Base):'.
116. Diese Zeile enthält den Code '__tablename__ = "ingredients"'.
117. Diese Zeile ist leer und trennt Abschnitte.
118. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
119. Diese Zeile enthält den Code 'name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)'.
120. Diese Zeile ist leer und trennt Abschnitte.
121. Diese Zeile enthält den Code 'recipe_links: Mapped[list["RecipeIngredient"]] = relationship('.
122. Diese Zeile enthält den Code 'back_populates="ingredient",'.
123. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
124. Diese Zeile enthält den Code ')'.
125. Diese Zeile ist leer und trennt Abschnitte.
126. Diese Zeile ist leer und trennt Abschnitte.
127. Diese Zeile enthält den Code 'class RecipeIngredient(Base):'.
128. Diese Zeile enthält den Code '__tablename__ = "recipe_ingredients"'.
129. Diese Zeile ist leer und trennt Abschnitte.
130. Diese Zeile enthält den Code 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=...'.
131. Diese Zeile enthält den Code 'ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"), prim...'.
132. Diese Zeile enthält den Code 'quantity_text: Mapped[str] = mapped_column(String(120), default="", nullable=False)'.
133. Diese Zeile enthält den Code 'grams: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
134. Diese Zeile ist leer und trennt Abschnitte.
135. Diese Zeile enthält den Code 'recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")'.
136. Diese Zeile enthält den Code 'ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_links")'.
137. Diese Zeile ist leer und trennt Abschnitte.
138. Diese Zeile ist leer und trennt Abschnitte.
139. Diese Zeile enthält den Code 'class Review(Base):'.
140. Diese Zeile enthält den Code '__tablename__ = "reviews"'.
141. Diese Zeile enthält den Code '__table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_reviews_user_recipe"),)'.
142. Diese Zeile ist leer und trennt Abschnitte.
143. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
144. Diese Zeile enthält den Code 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=Fal...'.
145. Diese Zeile enthält den Code 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, ...'.
146. Diese Zeile enthält den Code 'rating: Mapped[int] = mapped_column(Integer, nullable=False)'.
147. Diese Zeile enthält den Code 'comment: Mapped[str] = mapped_column(Text, default="", nullable=False)'.
148. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
149. Diese Zeile ist leer und trennt Abschnitte.
150. Diese Zeile enthält den Code 'recipe: Mapped["Recipe"] = relationship(back_populates="reviews")'.
151. Diese Zeile enthält den Code 'user: Mapped["User"] = relationship(back_populates="reviews")'.
152. Diese Zeile ist leer und trennt Abschnitte.
153. Diese Zeile ist leer und trennt Abschnitte.
154. Diese Zeile enthält den Code 'class Favorite(Base):'.
155. Diese Zeile enthält den Code '__tablename__ = "favorites"'.
156. Diese Zeile enthält den Code '__table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_recipe"),)'.
157. Diese Zeile ist leer und trennt Abschnitte.
158. Diese Zeile enthält den Code 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)'.
159. Diese Zeile enthält den Code 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=...'.
160. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
161. Diese Zeile ist leer und trennt Abschnitte.
162. Diese Zeile enthält den Code 'user: Mapped["User"] = relationship(back_populates="favorites")'.
163. Diese Zeile enthält den Code 'recipe: Mapped["Recipe"] = relationship(back_populates="favorites")'.
164. Diese Zeile ist leer und trennt Abschnitte.
165. Diese Zeile ist leer und trennt Abschnitte.
166. Diese Zeile enthält den Code 'class RecipeImage(Base):'.
167. Diese Zeile enthält den Code '__tablename__ = "recipe_images"'.
168. Diese Zeile ist leer und trennt Abschnitte.
169. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
170. Diese Zeile enthält den Code 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=Fal...'.
171. Diese Zeile enthält den Code 'filename: Mapped[str] = mapped_column(String(255), nullable=False)'.
172. Diese Zeile enthält den Code 'content_type: Mapped[str] = mapped_column(String(50), nullable=False)'.
173. Diese Zeile enthält den Code 'data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)'.
174. Diese Zeile enthält den Code 'is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)'.
175. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
176. Diese Zeile ist leer und trennt Abschnitte.
177. Diese Zeile enthält den Code 'recipe: Mapped["Recipe"] = relationship(back_populates="images")'.
178. Diese Zeile ist leer und trennt Abschnitte.
179. Diese Zeile ist leer und trennt Abschnitte.
180. Diese Zeile enthält den Code 'class RecipeImageChangeRequest(Base):'.
181. Diese Zeile enthält den Code '__tablename__ = "recipe_image_change_requests"'.
182. Diese Zeile ist leer und trennt Abschnitte.
183. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
184. Diese Zeile enthält den Code 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=Fal...'.
185. Diese Zeile enthält den Code 'requester_user_id: Mapped[int | None] = mapped_column('.
186. Diese Zeile enthält den Code 'ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True'.
187. Diese Zeile enthält den Code ')'.
188. Diese Zeile enthält den Code 'status: Mapped[str] = mapped_column('.
189. Diese Zeile enthält den Code 'IMAGE_CHANGE_STATUS_ENUM,'.
190. Diese Zeile enthält den Code 'nullable=False,'.
191. Diese Zeile enthält den Code 'default="pending",'.
192. Diese Zeile enthält den Code 'server_default="pending",'.
193. Diese Zeile enthält den Code 'index=True,'.
194. Diese Zeile enthält den Code ')'.
195. Diese Zeile enthält den Code 'admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)'.
196. Diese Zeile enthält den Code 'reviewed_by_admin_id: Mapped[int | None] = mapped_column('.
197. Diese Zeile enthält den Code 'ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True'.
198. Diese Zeile enthält den Code ')'.
199. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
200. Diese Zeile enthält den Code 'reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)'.
201. Diese Zeile ist leer und trennt Abschnitte.
202. Diese Zeile enthält den Code 'recipe: Mapped["Recipe"] = relationship(back_populates="image_change_requests")'.
203. Diese Zeile enthält den Code 'requester_user: Mapped["User"] = relationship('.
204. Diese Zeile enthält den Code 'back_populates="image_change_requests",'.
205. Diese Zeile enthält den Code 'foreign_keys=[requester_user_id],'.
206. Diese Zeile enthält den Code ')'.
207. Diese Zeile enthält den Code 'reviewed_by_admin: Mapped["User"] = relationship('.
208. Diese Zeile enthält den Code 'back_populates="reviewed_image_change_requests",'.
209. Diese Zeile enthält den Code 'foreign_keys=[reviewed_by_admin_id],'.
210. Diese Zeile enthält den Code ')'.
211. Diese Zeile enthält den Code 'files: Mapped[list["RecipeImageChangeFile"]] = relationship('.
212. Diese Zeile enthält den Code 'back_populates="request",'.
213. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
214. Diese Zeile enthält den Code 'order_by="RecipeImageChangeFile.created_at",'.
215. Diese Zeile enthält den Code ')'.
216. Diese Zeile ist leer und trennt Abschnitte.
217. Diese Zeile ist leer und trennt Abschnitte.
218. Diese Zeile enthält den Code 'class RecipeImageChangeFile(Base):'.
219. Diese Zeile enthält den Code '__tablename__ = "recipe_image_change_files"'.
220. Diese Zeile enthält den Code '__table_args__ = (UniqueConstraint("request_id", name="uq_recipe_image_change_files_request"),)'.
221. Diese Zeile ist leer und trennt Abschnitte.
222. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
223. Diese Zeile enthält den Code 'request_id: Mapped[int] = mapped_column('.
224. Diese Zeile enthält den Code 'ForeignKey("recipe_image_change_requests.id", ondelete="CASCADE"), nullable=False, index=True'.
225. Diese Zeile enthält den Code ')'.
226. Diese Zeile enthält den Code 'filename: Mapped[str] = mapped_column(String(255), nullable=False)'.
227. Diese Zeile enthält den Code 'content_type: Mapped[str] = mapped_column(String(50), nullable=False)'.
228. Diese Zeile enthält den Code 'data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)'.
229. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
230. Diese Zeile ist leer und trennt Abschnitte.
231. Diese Zeile enthält den Code 'request: Mapped["RecipeImageChangeRequest"] = relationship(back_populates="files")'.
232. Diese Zeile ist leer und trennt Abschnitte.
233. Diese Zeile ist leer und trennt Abschnitte.
234. Diese Zeile enthält den Code 'class RecipeSubmission(Base):'.
235. Diese Zeile enthält den Code '__tablename__ = "recipe_submissions"'.
236. Diese Zeile ist leer und trennt Abschnitte.
237. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
238. Diese Zeile enthält den Code 'submitter_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL")...'.
239. Diese Zeile enthält den Code 'submitter_email: Mapped[str | None] = mapped_column(String(255), nullable=True)'.
240. Diese Zeile enthält den Code 'title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)'.
241. Diese Zeile enthält den Code 'description: Mapped[str] = mapped_column(Text, nullable=False)'.
242. Diese Zeile enthält den Code 'category: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)'.
243. Diese Zeile enthält den Code 'difficulty: Mapped[str] = mapped_column(String(30), nullable=False, default="medium", index=True)'.
244. Diese Zeile enthält den Code 'prep_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
245. Diese Zeile enthält den Code 'servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)'.
246. Diese Zeile enthält den Code 'instructions: Mapped[str] = mapped_column(Text, nullable=False)'.
247. Diese Zeile enthält den Code 'status: Mapped[str] = mapped_column(SUBMISSION_STATUS_ENUM, nullable=False, default="pending", se...'.
248. Diese Zeile enthält den Code 'admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)'.
249. Diese Zeile enthält den Code 'reviewed_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NUL...'.
250. Diese Zeile enthält den Code 'reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)'.
251. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
252. Diese Zeile ist leer und trennt Abschnitte.
253. Diese Zeile enthält den Code 'submitter_user: Mapped["User"] = relationship('.
254. Diese Zeile enthält den Code 'back_populates="submissions",'.
255. Diese Zeile enthält den Code 'foreign_keys=[submitter_user_id],'.
256. Diese Zeile enthält den Code ')'.
257. Diese Zeile enthält den Code 'reviewed_by_admin: Mapped["User"] = relationship('.
258. Diese Zeile enthält den Code 'back_populates="reviewed_submissions",'.
259. Diese Zeile enthält den Code 'foreign_keys=[reviewed_by_admin_id],'.
260. Diese Zeile enthält den Code ')'.
261. Diese Zeile enthält den Code 'ingredients: Mapped[list["SubmissionIngredient"]] = relationship('.
262. Diese Zeile enthält den Code 'back_populates="submission",'.
263. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
264. Diese Zeile enthält den Code 'order_by="SubmissionIngredient.id",'.
265. Diese Zeile enthält den Code ')'.
266. Diese Zeile enthält den Code 'images: Mapped[list["SubmissionImage"]] = relationship('.
267. Diese Zeile enthält den Code 'back_populates="submission",'.
268. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
269. Diese Zeile enthält den Code 'order_by="SubmissionImage.created_at",'.
270. Diese Zeile enthält den Code ')'.
271. Diese Zeile ist leer und trennt Abschnitte.
272. Diese Zeile ist leer und trennt Abschnitte.
273. Diese Zeile enthält den Code 'class SubmissionIngredient(Base):'.
274. Diese Zeile enthält den Code '__tablename__ = "submission_ingredients"'.
275. Diese Zeile ist leer und trennt Abschnitte.
276. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
277. Diese Zeile enthält den Code 'submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete="CASCADE"...'.
278. Diese Zeile enthält den Code 'ingredient_name: Mapped[str] = mapped_column(String(200), nullable=False)'.
279. Diese Zeile enthält den Code 'quantity_text: Mapped[str] = mapped_column(String(120), nullable=False, default="")'.
280. Diese Zeile enthält den Code 'grams: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
281. Diese Zeile enthält den Code 'ingredient_name_normalized: Mapped[str | None] = mapped_column(String(200), nullable=True, index=...'.
282. Diese Zeile ist leer und trennt Abschnitte.
283. Diese Zeile enthält den Code 'submission: Mapped["RecipeSubmission"] = relationship(back_populates="ingredients")'.
284. Diese Zeile ist leer und trennt Abschnitte.
285. Diese Zeile ist leer und trennt Abschnitte.
286. Diese Zeile enthält den Code 'class SubmissionImage(Base):'.
287. Diese Zeile enthält den Code '__tablename__ = "submission_images"'.
288. Diese Zeile ist leer und trennt Abschnitte.
289. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
290. Diese Zeile enthält den Code 'submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete="CASCADE"...'.
291. Diese Zeile enthält den Code 'filename: Mapped[str] = mapped_column(String(255), nullable=False)'.
292. Diese Zeile enthält den Code 'content_type: Mapped[str] = mapped_column(String(50), nullable=False)'.
293. Diese Zeile enthält den Code 'data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)'.
294. Diese Zeile enthält den Code 'is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)'.
295. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
296. Diese Zeile ist leer und trennt Abschnitte.
297. Diese Zeile enthält den Code 'submission: Mapped["RecipeSubmission"] = relationship(back_populates="images")'.
298. Diese Zeile ist leer und trennt Abschnitte.
299. Diese Zeile ist leer und trennt Abschnitte.
300. Diese Zeile enthält den Code 'class AppMeta(Base):'.
301. Diese Zeile enthält den Code '__tablename__ = "app_meta"'.
302. Diese Zeile ist leer und trennt Abschnitte.
303. Diese Zeile enthält den Code 'key: Mapped[str] = mapped_column(String(120), primary_key=True)'.
304. Diese Zeile enthält den Code 'value: Mapped[str] = mapped_column(Text, nullable=False)'.
305. Diese Zeile ist leer und trennt Abschnitte.
306. Diese Zeile ist leer und trennt Abschnitte.
307. Diese Zeile enthält den Code 'class PasswordResetToken(Base):'.
308. Diese Zeile enthält den Code '__tablename__ = "password_reset_tokens"'.
309. Diese Zeile ist leer und trennt Abschnitte.
310. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
311. Diese Zeile enthält den Code 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, ...'.
312. Diese Zeile enthält den Code 'new_email_normalized: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)'.
313. Diese Zeile enthält den Code 'token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)'.
314. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
315. Diese Zeile enthält den Code 'expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)'.
316. Diese Zeile enthält den Code 'used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)'.
317. Diese Zeile enthält den Code 'created_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)'.
318. Diese Zeile enthält den Code 'created_user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)'.
319. Diese Zeile enthält den Code 'purpose: Mapped[str] = mapped_column(String(50), nullable=False, default="password_reset", index=...'.
320. Diese Zeile ist leer und trennt Abschnitte.
321. Diese Zeile enthält den Code 'user: Mapped["User"] = relationship(back_populates="password_reset_tokens")'.
322. Diese Zeile ist leer und trennt Abschnitte.
323. Diese Zeile ist leer und trennt Abschnitte.
324. Diese Zeile enthält den Code 'class SecurityEvent(Base):'.
325. Diese Zeile enthält den Code '__tablename__ = "security_events"'.
326. Diese Zeile ist leer und trennt Abschnitte.
327. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
328. Diese Zeile enthält den Code 'user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable...'.
329. Diese Zeile enthält den Code 'event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)'.
330. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
331. Diese Zeile enthält den Code 'ip: Mapped[str | None] = mapped_column(String(64), nullable=True)'.
332. Diese Zeile enthält den Code 'user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)'.
333. Diese Zeile enthält den Code 'details: Mapped[str | None] = mapped_column(String(300), nullable=True)'.
334. Diese Zeile ist leer und trennt Abschnitte.
335. Diese Zeile enthält den Code 'user: Mapped["User"] = relationship(back_populates="security_events")'.

## app/image_utils.py

```python
import io
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from app.config import get_settings
from app.i18n import t

settings = get_settings()

MAGIC_SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}


class ImageValidationError(ValueError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _validate_magic_bytes(content_type: str, file_bytes: bytes) -> None:
    signatures = MAGIC_SIGNATURES.get(content_type, [])
    if not signatures:
        raise ImageValidationError(t("error.mime_unsupported", content_type=content_type))
    if content_type == "image/webp":
        if not (file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP"):
            raise ImageValidationError(t("error.webp_signature"))
        return
    if not any(file_bytes.startswith(sig) for sig in signatures):
        raise ImageValidationError(t("error.magic_mismatch"))


def _validate_image_decode(content_type: str, file_bytes: bytes) -> None:
    expected_format = {
        "image/jpeg": "JPEG",
        "image/png": "PNG",
        "image/webp": "WEBP",
    }.get(content_type)
    try:
        with Image.open(io.BytesIO(file_bytes)) as image:
            image.verify()
            actual_format = (image.format or "").upper()
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ImageValidationError(t("error.image_invalid")) from exc
    if expected_format and actual_format != expected_format:
        raise ImageValidationError(t("error.image_format_mismatch"))


def safe_image_filename(original_filename: str, content_type: str) -> str:
    extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }.get(content_type, "")
    clean_name = Path(original_filename or "").name
    if not extension:
        extension = Path(clean_name).suffix.lower()
    return f"{uuid4().hex}{extension[:10]}"


def validate_image_upload(content_type: str, file_bytes: bytes) -> None:
    if content_type not in settings.allowed_image_types:
        raise ImageValidationError(t("error.mime_unsupported", content_type=content_type))
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ImageValidationError(t("error.image_too_large", max_mb=settings.max_upload_mb), status_code=413)
    if len(file_bytes) < 12:
        raise ImageValidationError(t("error.image_too_small"))
    _validate_magic_bytes(content_type, file_bytes)
    _validate_image_decode(content_type, file_bytes)

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'import io'.
2. Diese Zeile enthält den Code 'from pathlib import Path'.
3. Diese Zeile enthält den Code 'from uuid import uuid4'.
4. Diese Zeile ist leer und trennt Abschnitte.
5. Diese Zeile enthält den Code 'from PIL import Image, UnidentifiedImageError'.
6. Diese Zeile ist leer und trennt Abschnitte.
7. Diese Zeile enthält den Code 'from app.config import get_settings'.
8. Diese Zeile enthält den Code 'from app.i18n import t'.
9. Diese Zeile ist leer und trennt Abschnitte.
10. Diese Zeile enthält den Code 'settings = get_settings()'.
11. Diese Zeile ist leer und trennt Abschnitte.
12. Diese Zeile enthält den Code 'MAGIC_SIGNATURES = {'.
13. Diese Zeile enthält den Code '"image/jpeg": [b"\xff\xd8\xff"],'.
14. Diese Zeile enthält den Code '"image/png": [b"\x89PNG\r\n\x1a\n"],'.
15. Diese Zeile enthält den Code '"image/webp": [b"RIFF"],'.
16. Diese Zeile enthält den Code '}'.
17. Diese Zeile ist leer und trennt Abschnitte.
18. Diese Zeile ist leer und trennt Abschnitte.
19. Diese Zeile enthält den Code 'class ImageValidationError(ValueError):'.
20. Diese Zeile enthält den Code 'def __init__(self, message: str, status_code: int = 400):'.
21. Diese Zeile enthält den Code 'super().__init__(message)'.
22. Diese Zeile enthält den Code 'self.status_code = status_code'.
23. Diese Zeile ist leer und trennt Abschnitte.
24. Diese Zeile ist leer und trennt Abschnitte.
25. Diese Zeile enthält den Code 'def _validate_magic_bytes(content_type: str, file_bytes: bytes) -> None:'.
26. Diese Zeile enthält den Code 'signatures = MAGIC_SIGNATURES.get(content_type, [])'.
27. Diese Zeile enthält den Code 'if not signatures:'.
28. Diese Zeile enthält den Code 'raise ImageValidationError(t("error.mime_unsupported", content_type=content_type))'.
29. Diese Zeile enthält den Code 'if content_type == "image/webp":'.
30. Diese Zeile enthält den Code 'if not (file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP"):'.
31. Diese Zeile enthält den Code 'raise ImageValidationError(t("error.webp_signature"))'.
32. Diese Zeile enthält den Code 'return'.
33. Diese Zeile enthält den Code 'if not any(file_bytes.startswith(sig) for sig in signatures):'.
34. Diese Zeile enthält den Code 'raise ImageValidationError(t("error.magic_mismatch"))'.
35. Diese Zeile ist leer und trennt Abschnitte.
36. Diese Zeile ist leer und trennt Abschnitte.
37. Diese Zeile enthält den Code 'def _validate_image_decode(content_type: str, file_bytes: bytes) -> None:'.
38. Diese Zeile enthält den Code 'expected_format = {'.
39. Diese Zeile enthält den Code '"image/jpeg": "JPEG",'.
40. Diese Zeile enthält den Code '"image/png": "PNG",'.
41. Diese Zeile enthält den Code '"image/webp": "WEBP",'.
42. Diese Zeile enthält den Code '}.get(content_type)'.
43. Diese Zeile enthält den Code 'try:'.
44. Diese Zeile enthält den Code 'with Image.open(io.BytesIO(file_bytes)) as image:'.
45. Diese Zeile enthält den Code 'image.verify()'.
46. Diese Zeile enthält den Code 'actual_format = (image.format or "").upper()'.
47. Diese Zeile enthält den Code 'except (UnidentifiedImageError, OSError, SyntaxError) as exc:'.
48. Diese Zeile enthält den Code 'raise ImageValidationError(t("error.image_invalid")) from exc'.
49. Diese Zeile enthält den Code 'if expected_format and actual_format != expected_format:'.
50. Diese Zeile enthält den Code 'raise ImageValidationError(t("error.image_format_mismatch"))'.
51. Diese Zeile ist leer und trennt Abschnitte.
52. Diese Zeile ist leer und trennt Abschnitte.
53. Diese Zeile enthält den Code 'def safe_image_filename(original_filename: str, content_type: str) -> str:'.
54. Diese Zeile enthält den Code 'extension = {'.
55. Diese Zeile enthält den Code '"image/jpeg": ".jpg",'.
56. Diese Zeile enthält den Code '"image/png": ".png",'.
57. Diese Zeile enthält den Code '"image/webp": ".webp",'.
58. Diese Zeile enthält den Code '}.get(content_type, "")'.
59. Diese Zeile enthält den Code 'clean_name = Path(original_filename or "").name'.
60. Diese Zeile enthält den Code 'if not extension:'.
61. Diese Zeile enthält den Code 'extension = Path(clean_name).suffix.lower()'.
62. Diese Zeile enthält den Code 'return f"{uuid4().hex}{extension[:10]}"'.
63. Diese Zeile ist leer und trennt Abschnitte.
64. Diese Zeile ist leer und trennt Abschnitte.
65. Diese Zeile enthält den Code 'def validate_image_upload(content_type: str, file_bytes: bytes) -> None:'.
66. Diese Zeile enthält den Code 'if content_type not in settings.allowed_image_types:'.
67. Diese Zeile enthält den Code 'raise ImageValidationError(t("error.mime_unsupported", content_type=content_type))'.
68. Diese Zeile enthält den Code 'max_bytes = settings.max_upload_mb * 1024 * 1024'.
69. Diese Zeile enthält den Code 'if len(file_bytes) > max_bytes:'.
70. Diese Zeile enthält den Code 'raise ImageValidationError(t("error.image_too_large", max_mb=settings.max_upload_mb), status_code...'.
71. Diese Zeile enthält den Code 'if len(file_bytes) < 12:'.
72. Diese Zeile enthält den Code 'raise ImageValidationError(t("error.image_too_small"))'.
73. Diese Zeile enthält den Code '_validate_magic_bytes(content_type, file_bytes)'.
74. Diese Zeile enthält den Code '_validate_image_decode(content_type, file_bytes)'.

## app/routers/recipes.py

```python
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.dependencies import get_admin_user, get_current_user, get_current_user_optional, template_context
from app.image_utils import ImageValidationError, safe_image_filename, validate_image_upload
from app.i18n import t
from app.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeImage,
    RecipeImageChangeFile,
    RecipeImageChangeRequest,
    RecipeIngredient,
    Review,
    User,
)
from app.pdf_service import build_recipe_pdf
from app.rate_limit import key_by_ip, key_by_user_or_ip, limiter
from app.services import (
    DEFAULT_CATEGORY,
    build_category_index,
    can_manage_recipe,
    get_distinct_categories,
    normalize_category,
    parse_ingredient_text,
    replace_recipe_ingredients,
    resolve_title_image_url,
    sanitize_difficulty,
)
from app.views import redirect, templates

router = APIRouter(tags=["recipes"])

PAGE_SIZE_DEFAULT = 20
PAGE_SIZE_OPTIONS = (10, 20, 40, 80)


def parse_positive_int(value: str, field_name: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} must be an integer.") from exc
    if parsed <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} must be greater than zero.")
    return parsed


def normalize_image_url(value: str) -> str | None:
    cleaned = value.strip()
    if not cleaned:
        return None
    if not (cleaned.startswith("http://") or cleaned.startswith("https://")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title_image_url must start with http:// or https://")
    return cleaned


def build_pagination_items(page: int, total_pages: int) -> list[int | None]:
    if total_pages <= 7:
        return list(range(1, total_pages + 1))
    if page <= 4:
        return [1, 2, 3, 4, 5, None, total_pages]
    if page >= total_pages - 3:
        return [1, None, total_pages - 4, total_pages - 3, total_pages - 2, total_pages - 1, total_pages]
    return [1, None, page - 1, page, page + 1, None, total_pages]


def resolve_category_value(category_select: str, category_new: str, category_legacy: str = "") -> str:
    if category_select and category_select != "__new__":
        return normalize_category(category_select)
    if category_new.strip():
        return normalize_category(category_new)
    if category_legacy.strip():
        return normalize_category(category_legacy)
    return DEFAULT_CATEGORY


def fetch_recipe_or_404(db: Session, recipe_id: int) -> Recipe:
    recipe = db.scalar(
        select(Recipe)
        .where(Recipe.id == recipe_id)
        .options(
            joinedload(Recipe.creator),
            selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),
            selectinload(Recipe.reviews).joinedload(Review.user),
            selectinload(Recipe.images),
        )
    )
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    return recipe


def ensure_recipe_visible(recipe: Recipe, current_user: User | None) -> None:
    if recipe.is_published:
        return
    if current_user and (current_user.role == "admin" or current_user.id == recipe.creator_id):
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")


def ensure_recipe_access(user: User, recipe: Recipe) -> None:
    if not can_manage_recipe(user, recipe):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this recipe.")


def get_primary_image(recipe: Recipe) -> RecipeImage | None:
    for image in recipe.images:
        if image.is_primary:
            return image
    return recipe.images[0] if recipe.images else None


def get_external_fallback_image_url(recipe: Recipe) -> str | None:
    if recipe.source_image_url:
        return recipe.source_image_url
    if recipe.title_image_url:
        return recipe.title_image_url
    return None


def resolve_recipe_display_image(recipe: Recipe, primary_image: RecipeImage | None) -> tuple[str | None, str]:
    if primary_image:
        return f"/images/{primary_image.id}", "db"
    external_url = get_external_fallback_image_url(recipe)
    if external_url:
        return external_url, "external"
    return None, "placeholder"


def can_direct_upload(user: User | None) -> bool:
    return bool(user and user.role == "admin")


def can_request_image_change(user: User | None) -> bool:
    return bool(user and user.role != "admin")


def user_has_pending_image_request(db: Session, recipe_id: int, current_user: User | None) -> bool:
    if not current_user or current_user.role == "admin":
        return False
    pending = db.scalar(
        select(func.count())
        .select_from(RecipeImageChangeRequest)
        .where(
            RecipeImageChangeRequest.recipe_id == recipe_id,
            RecipeImageChangeRequest.requester_user_id == current_user.id,
            RecipeImageChangeRequest.status == "pending",
        )
    )
    return bool(int(pending or 0))


def set_recipe_primary_image(db: Session, recipe: Recipe, image_id: int) -> None:
    for image in recipe.images:
        image.is_primary = image.id == image_id
    db.flush()


def maybe_promote_primary_after_delete(db: Session, recipe: Recipe) -> None:
    remaining = list(recipe.images)
    if not remaining:
        return
    if any(image.is_primary for image in remaining):
        return
    remaining[0].is_primary = True
    db.flush()


def render_image_section(
    request: Request,
    db: Session,
    recipe_id: int,
    current_user: User | None,
    *,
    feedback_message: str = "",
    feedback_error: str = "",
    status_code: int = status.HTTP_200_OK,
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    primary_image = get_primary_image(recipe)
    display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)
    return templates.TemplateResponse(
        "partials/recipe_images.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            primary_image=primary_image,
            display_image_url=display_image_url,
            display_image_kind=display_image_kind,
            can_upload_direct=can_direct_upload(current_user),
            can_request_change=can_request_image_change(current_user),
            has_pending_change_request=user_has_pending_image_request(db, recipe_id, current_user),
            image_feedback_message=feedback_message,
            image_feedback_error=feedback_error,
        ),
        status_code=status_code,
    )


def render_recipe_card_image(
    request: Request,
    db: Session,
    recipe_id: int,
    current_user: User | None,
    *,
    feedback_message: str = "",
    feedback_error: str = "",
    status_code: int = status.HTTP_200_OK,
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id).options(selectinload(Recipe.images)))
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found", request=request))
    primary_image = get_primary_image(recipe)
    display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)
    return templates.TemplateResponse(
        "partials/recipe_card_image.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            primary_image=primary_image,
            display_image_url=display_image_url,
            display_image_kind=display_image_kind,
            can_upload_direct=can_direct_upload(current_user),
            can_request_change=can_request_image_change(current_user),
            has_pending_change_request=user_has_pending_image_request(db, recipe_id, current_user),
            image_feedback_message=feedback_message,
            image_feedback_error=feedback_error,
        ),
        status_code=status_code,
    )


@router.get("/")
def home_page(
    request: Request,
    page: int = 1,
    per_page: int = PAGE_SIZE_DEFAULT,
    sort: str = "date",
    title: str = "",
    category: str = "",
    difficulty: str = "",
    ingredient: str = "",
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    page = max(page, 1)
    if per_page not in PAGE_SIZE_OPTIONS:
        per_page = PAGE_SIZE_DEFAULT
    category_index = build_category_index(db, only_published=True)
    category_options = sorted(category_index.keys(), key=str.casefold)
    selected_category = normalize_category(category, allow_empty=True)
    if selected_category and selected_category not in category_index:
        category_index[selected_category] = [selected_category]
        category_options = sorted(category_index.keys(), key=str.casefold)
    review_stats = (
        select(
            Review.recipe_id.label("recipe_id"),
            func.avg(Review.rating).label("avg_rating"),
            func.count(Review.id).label("review_count"),
        )
        .group_by(Review.recipe_id)
        .subquery()
    )
    stmt = (
        select(
            Recipe,
            func.coalesce(review_stats.c.avg_rating, 0).label("avg_rating"),
            func.coalesce(review_stats.c.review_count, 0).label("review_count"),
        )
        .outerjoin(review_stats, Recipe.id == review_stats.c.recipe_id)
        .where(Recipe.is_published.is_(True))
        .options(selectinload(Recipe.images))
    )
    if title.strip():
        like = f"%{title.strip()}%"
        stmt = stmt.where(Recipe.title.ilike(like))
    if selected_category:
        stmt = stmt.where(Recipe.category.in_(category_index.get(selected_category, [selected_category])))
    if difficulty.strip():
        stmt = stmt.where(Recipe.difficulty == sanitize_difficulty(difficulty))
    if ingredient.strip():
        like = f"%{ingredient.strip().lower()}%"
        ingredient_recipe_ids = (
            select(RecipeIngredient.recipe_id)
            .join(Ingredient, Ingredient.id == RecipeIngredient.ingredient_id)
            .where(Ingredient.name.ilike(like))
            .subquery()
        )
        stmt = stmt.where(Recipe.id.in_(select(ingredient_recipe_ids.c.recipe_id)))
    if sort == "prep_time":
        stmt = stmt.order_by(Recipe.prep_time_minutes.asc(), Recipe.created_at.desc())
    elif sort == "avg_rating":
        stmt = stmt.order_by(desc("avg_rating"), Recipe.created_at.desc())
    else:
        stmt = stmt.order_by(Recipe.created_at.desc())
    total = db.scalar(select(func.count()).select_from(stmt.subquery()))
    pages = max((total + per_page - 1) // per_page, 1)
    page = min(page, pages)
    rows = db.execute(stmt.offset((page - 1) * per_page).limit(per_page)).all()
    recipe_ids = [int(row[0].id) for row in rows]
    pending_recipe_ids: set[int] = set()
    if current_user and current_user.role != "admin" and recipe_ids:
        pending_rows = db.scalars(
            select(RecipeImageChangeRequest.recipe_id).where(
                RecipeImageChangeRequest.recipe_id.in_(recipe_ids),
                RecipeImageChangeRequest.requester_user_id == current_user.id,
                RecipeImageChangeRequest.status == "pending",
            )
        ).all()
        pending_recipe_ids = {int(item) for item in pending_rows}
    recipes_data = []
    for row in rows:
        recipe = row[0]
        primary_image = get_primary_image(recipe)
        display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)
        recipes_data.append(
            {
                "recipe": recipe,
                "avg_rating": float(row[1] or 0),
                "review_count": int(row[2] or 0),
                "primary_image": primary_image,
                "display_image_url": display_image_url,
                "display_image_kind": display_image_kind,
                "has_pending_change_request": recipe.id in pending_recipe_ids,
            }
        )
    start_item = ((page - 1) * per_page + 1) if total > 0 else 0
    end_item = min(page * per_page, total)
    pagination_items = build_pagination_items(page, pages)
    context = template_context(
        request,
        current_user,
        recipes_data=recipes_data,
        page=page,
        pages=pages,
        total_pages=pages,
        per_page=per_page,
        per_page_options=PAGE_SIZE_OPTIONS,
        category_options=category_options,
        total=total,
        total_count=total,
        start_item=start_item,
        end_item=end_item,
        pagination_items=pagination_items,
        sort=sort,
        title=title,
        category=selected_category,
        difficulty=difficulty,
        ingredient=ingredient,
    )
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse("partials/recipe_list.html", context)
    return templates.TemplateResponse("home.html", context)


@router.get("/recipes/new")
def create_recipe_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return templates.TemplateResponse(
        "recipe_form.html",
        template_context(
            request,
            current_user,
            recipe=None,
            error=None,
            form_mode="create",
            category_options=get_distinct_categories(db, only_published=False),
            selected_category=DEFAULT_CATEGORY,
            category_new_value="",
        ),
    )


@router.post("/recipes")
@router.post("/recipes/new")
async def create_recipe_submit(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    instructions: str = Form(...),
    category_select: str = Form(DEFAULT_CATEGORY),
    category_new: str = Form(""),
    category: str = Form(""),
    title_image_url: str = Form(""),
    prep_time_minutes: str = Form(...),
    difficulty: str = Form(...),
    ingredients_text: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    prep_time = parse_positive_int(prep_time_minutes, "prep_time_minutes")
    normalized_difficulty = sanitize_difficulty(difficulty)
    if not title.strip() or not instructions.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and instructions are required.")
    recipe = Recipe(
        title=title.strip(),
        title_image_url=normalize_image_url(title_image_url),
        source="admin_manual",
        description=description.strip(),
        instructions=instructions.strip(),
        category=resolve_category_value(category_select, category_new, category),
        prep_time_minutes=prep_time,
        difficulty=normalized_difficulty,
        creator_id=current_user.id,
        is_published=True,
    )
    db.add(recipe)
    db.flush()
    ingredient_entries = parse_ingredient_text(ingredients_text)
    replace_recipe_ingredients(db, recipe, ingredient_entries)
    if image and image.filename:
        data = await image.read()
        try:
            validate_image_upload((image.content_type or "").lower(), data)
        except ImageValidationError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        image_content_type = (image.content_type or "application/octet-stream").lower()
        db.add(
            RecipeImage(
                recipe_id=recipe.id,
                filename=safe_image_filename(image.filename or "", image_content_type),
                content_type=image_content_type,
                data=data,
                is_primary=True,
            )
        )
    db.commit()
    return redirect(f"/recipes/{recipe.id}")


@router.get("/recipes/{recipe_id}")
def recipe_detail(
    request: Request,
    recipe_id: int,
    message: str = "",
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_visible(recipe, current_user)
    avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.recipe_id == recipe_id)) or 0
    review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe_id)) or 0
    primary_image = get_primary_image(recipe)
    display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)
    is_favorite = False
    if current_user:
        is_favorite = db.scalar(
            select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id))
        ) is not None
    message_map = {
        "image_change_submitted": t("images.request_submitted", request=request),
        "image_upload_done": t("images.uploaded", request=request),
    }
    return templates.TemplateResponse(
        "recipe_detail.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            avg_rating=float(avg_rating),
            review_count=int(review_count),
            is_favorite=is_favorite,
            primary_image=primary_image,
            display_image_url=display_image_url,
            display_image_kind=display_image_kind,
            can_upload_direct=can_direct_upload(current_user),
            can_request_change=can_request_image_change(current_user),
            has_pending_change_request=user_has_pending_image_request(db, recipe_id, current_user),
            image_feedback_message=message_map.get(message, ""),
            image_feedback_error="",
        ),
    )


@router.get("/recipes/{recipe_id}/edit")
def edit_recipe_page(
    request: Request,
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_access(current_user, recipe)
    selected_category = normalize_category(recipe.category)
    category_options = get_distinct_categories(db)
    if selected_category not in category_options:
        category_options = sorted([*category_options, selected_category], key=str.casefold)
    ingredients_text = "\n".join(
        f"{link.ingredient.name}|{link.quantity_text}|{link.grams or ''}".rstrip("|")
        for link in recipe.recipe_ingredients
    )
    return templates.TemplateResponse(
        "recipe_form.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            ingredients_text=ingredients_text,
            error=None,
            form_mode="edit",
            category_options=category_options,
            selected_category=selected_category,
            category_new_value="",
        ),
    )


@router.post("/recipes/{recipe_id}/edit")
async def edit_recipe_submit(
    recipe_id: int,
    title: str = Form(...),
    description: str = Form(...),
    instructions: str = Form(...),
    category_select: str = Form(DEFAULT_CATEGORY),
    category_new: str = Form(""),
    category: str = Form(""),
    title_image_url: str = Form(""),
    prep_time_minutes: str = Form(...),
    difficulty: str = Form(...),
    ingredients_text: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_access(current_user, recipe)
    recipe.title = title.strip()
    recipe.title_image_url = normalize_image_url(title_image_url)
    recipe.description = description.strip()
    recipe.instructions = instructions.strip()
    recipe.category = resolve_category_value(category_select, category_new, category)
    recipe.prep_time_minutes = parse_positive_int(prep_time_minutes, "prep_time_minutes")
    recipe.difficulty = sanitize_difficulty(difficulty)
    replace_recipe_ingredients(db, recipe, parse_ingredient_text(ingredients_text))
    if image and image.filename:
        data = await image.read()
        try:
            validate_image_upload((image.content_type or "").lower(), data)
        except ImageValidationError as exc:
            raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
        image_content_type = (image.content_type or "application/octet-stream").lower()
        has_images = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id == recipe.id)) or 0
        db.add(
            RecipeImage(
                recipe_id=recipe.id,
                filename=safe_image_filename(image.filename or "", image_content_type),
                content_type=image_content_type,
                data=data,
                is_primary=has_images == 0,
            )
        )
    db.commit()
    return redirect(f"/recipes/{recipe.id}")


@router.post("/recipes/{recipe_id}/delete")
def delete_recipe(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_access(current_user, recipe)
    db.delete(recipe)
    db.commit()
    return redirect("/my-recipes")


@router.post("/recipes/{recipe_id}/reviews")
def upsert_review(
    recipe_id: int,
    rating: int = Form(...),
    comment: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    if not recipe.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    if rating < 1 or rating > 5:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 1 and 5.")
    review = db.scalar(select(Review).where(and_(Review.recipe_id == recipe_id, Review.user_id == current_user.id)))
    if review:
        review.rating = rating
        review.comment = comment.strip()
    else:
        db.add(Review(recipe_id=recipe_id, user_id=current_user.id, rating=rating, comment=comment.strip()))
    db.commit()
    return redirect(f"/recipes/{recipe_id}")


@router.post("/reviews/{review_id}/delete")
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    review = db.scalar(select(Review).where(Review.id == review_id).options(joinedload(Review.recipe)))
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    if current_user.role != "admin" and review.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this review.")
    recipe_id = review.recipe_id
    db.delete(review)
    db.commit()
    return redirect(f"/recipes/{recipe_id}")


@router.post("/recipes/{recipe_id}/favorite")
def toggle_favorite(
    request: Request,
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
    if not recipe or not recipe.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    favorite = db.scalar(
        select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id))
    )
    is_favorite = True
    if favorite:
        db.delete(favorite)
        is_favorite = False
    else:
        db.add(Favorite(user_id=current_user.id, recipe_id=recipe_id))
        is_favorite = True
    db.commit()
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse(
            "partials/favorite_button.html",
            template_context(request, current_user, recipe=recipe, is_favorite=is_favorite),
        )
    return redirect(f"/recipes/{recipe_id}")


@router.get("/favorites")
def favorites_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    favorite_recipes = db.scalars(
        select(Recipe)
        .join(Favorite, Favorite.recipe_id == Recipe.id)
        .where(Favorite.user_id == current_user.id, Recipe.is_published.is_(True))
        .order_by(Recipe.created_at.desc())
        .options(selectinload(Recipe.images))
    ).all()
    return templates.TemplateResponse(
        "favorites.html",
        template_context(request, current_user, favorite_recipes=favorite_recipes),
    )


@router.get("/my-recipes")
def my_recipes_page(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.images))
    if current_user.role != "admin":
        stmt = stmt.where(Recipe.creator_id == current_user.id)
    recipes = db.scalars(stmt).all()
    return templates.TemplateResponse(
        "my_recipes.html",
        template_context(request, current_user, recipes=recipes),
    )


@router.post("/recipes/{recipe_id}/images")
@limiter.limit("10/minute", key_func=key_by_user_or_ip)
async def upload_recipe_image(
    request: Request,
    response: Response,
    recipe_id: int,
    set_primary: bool = Form(False),
    response_mode: str = Form("detail"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = response
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required", request=request))
    recipe = fetch_recipe_or_404(db, recipe_id)
    data = await file.read()
    content_type = (file.content_type or "").lower()
    try:
        validate_image_upload(content_type, data)
    except ImageValidationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    has_images = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id == recipe_id)) or 0
    query_value = request.query_params.get("set_primary")
    if query_value is not None:
        set_primary = query_value.strip().lower() in {"1", "true", "yes", "on"}
    new_is_primary = set_primary or has_images == 0
    recipe_image = RecipeImage(
        recipe_id=recipe_id,
        filename=safe_image_filename(file.filename or "", content_type),
        content_type=content_type,
        data=data,
        is_primary=new_is_primary,
    )
    db.add(recipe_image)
    db.flush()
    if new_is_primary:
        set_recipe_primary_image(db, recipe, recipe_image.id)
    db.commit()
    if request.headers.get("HX-Request") == "true":
        if response_mode == "card":
            return render_recipe_card_image(
                request,
                db,
                recipe_id,
                current_user,
                feedback_message=t("images.uploaded", request=request),
            )
        return render_image_section(
            request,
            db,
            recipe_id,
            current_user,
            feedback_message=t("images.uploaded", request=request),
        )
    return redirect(f"/recipes/{recipe_id}?message=image_upload_done")


@router.post("/recipes/{recipe_id}/image-change-request")
@limiter.limit("10/minute", key_func=key_by_ip)
@limiter.limit("5/minute", key_func=key_by_user_or_ip)
async def request_recipe_image_change(
    request: Request,
    response: Response,
    recipe_id: int,
    response_mode: str = Form("detail"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = response
    if current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=t("images.admin_use_direct_upload", request=request),
        )
    recipe = fetch_recipe_or_404(db, recipe_id)
    if not recipe.is_published:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found", request=request))
    data = await file.read()
    content_type = (file.content_type or "").lower()
    try:
        validate_image_upload(content_type, data)
    except ImageValidationError as exc:
        raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc
    change_request = RecipeImageChangeRequest(
        recipe_id=recipe_id,
        requester_user_id=current_user.id,
        status="pending",
    )
    db.add(change_request)
    db.flush()
    db.add(
        RecipeImageChangeFile(
            request_id=change_request.id,
            filename=safe_image_filename(file.filename or "", content_type),
            content_type=content_type,
            data=data,
        )
    )
    db.commit()
    if request.headers.get("HX-Request") == "true":
        if response_mode == "card":
            return render_recipe_card_image(
                request,
                db,
                recipe_id,
                current_user,
                feedback_message=t("images.request_submitted", request=request),
            )
        return render_image_section(
            request,
            db,
            recipe_id,
            current_user,
            feedback_message=t("images.request_submitted", request=request),
        )
    return redirect(f"/recipes/{recipe_id}?message=image_change_submitted")


@router.get("/images/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    return Response(
        content=image.data,
        media_type=image.content_type,
        headers={"Cache-Control": "public, max-age=86400"},
    )


@router.get("/external-image")
def external_image(url: str):
    try:
        resolved_url = resolve_title_image_url(url)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not resolve image URL: {exc}") from exc
    if not resolved_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No image URL available.")
    return RedirectResponse(url=resolved_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@router.delete("/images/{image_id}")
def delete_image_api(
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedload(RecipeImage.recipe)))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))
    recipe = image.recipe
    db.delete(image)
    db.flush()
    maybe_promote_primary_after_delete(db, recipe)
    db.commit()
    return {"status": "deleted"}


@router.post("/images/{image_id}/delete")
def delete_image_form(
    request: Request,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedload(RecipeImage.recipe)))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    recipe = image.recipe
    recipe_id = image.recipe_id
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))
    db.delete(image)
    db.flush()
    maybe_promote_primary_after_delete(db, recipe)
    db.commit()
    if request.headers.get("HX-Request") == "true":
        return render_image_section(request, db, recipe_id, current_user)
    return redirect(f"/recipes/{recipe_id}")


@router.post("/images/{image_id}/set-primary")
def set_primary_image(
    request: Request,
    image_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedload(RecipeImage.recipe)))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    recipe = image.recipe
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))
    set_recipe_primary_image(db, recipe, image.id)
    db.commit()
    if request.headers.get("HX-Request") == "true":
        return render_image_section(request, db, recipe.id, current_user)
    return redirect(f"/recipes/{recipe.id}")


@router.get("/recipes/{recipe_id}/pdf")
def recipe_pdf(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_visible(recipe, current_user)
    avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.recipe_id == recipe_id)) or 0
    review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe_id)) or 0
    pdf_bytes = build_recipe_pdf(recipe, float(avg_rating), int(review_count))
    filename = f"mealmate_recipe_{recipe_id}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)


@router.get("/categories")
def categories_api(db: Session = Depends(get_db)):
    return {"categories": get_distinct_categories(db, only_published=True)}

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'from io import BytesIO'.
2. Diese Zeile ist leer und trennt Abschnitte.
3. Diese Zeile enthält den Code 'from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status'.
4. Diese Zeile enthält den Code 'from fastapi.responses import RedirectResponse, Response, StreamingResponse'.
5. Diese Zeile enthält den Code 'from sqlalchemy import and_, desc, func, select'.
6. Diese Zeile enthält den Code 'from sqlalchemy.orm import Session, joinedload, selectinload'.
7. Diese Zeile ist leer und trennt Abschnitte.
8. Diese Zeile enthält den Code 'from app.database import get_db'.
9. Diese Zeile enthält den Code 'from app.dependencies import get_admin_user, get_current_user, get_current_user_optional, templat...'.
10. Diese Zeile enthält den Code 'from app.image_utils import ImageValidationError, safe_image_filename, validate_image_upload'.
11. Diese Zeile enthält den Code 'from app.i18n import t'.
12. Diese Zeile enthält den Code 'from app.models import ('.
13. Diese Zeile enthält den Code 'Favorite,'.
14. Diese Zeile enthält den Code 'Ingredient,'.
15. Diese Zeile enthält den Code 'Recipe,'.
16. Diese Zeile enthält den Code 'RecipeImage,'.
17. Diese Zeile enthält den Code 'RecipeImageChangeFile,'.
18. Diese Zeile enthält den Code 'RecipeImageChangeRequest,'.
19. Diese Zeile enthält den Code 'RecipeIngredient,'.
20. Diese Zeile enthält den Code 'Review,'.
21. Diese Zeile enthält den Code 'User,'.
22. Diese Zeile enthält den Code ')'.
23. Diese Zeile enthält den Code 'from app.pdf_service import build_recipe_pdf'.
24. Diese Zeile enthält den Code 'from app.rate_limit import key_by_ip, key_by_user_or_ip, limiter'.
25. Diese Zeile enthält den Code 'from app.services import ('.
26. Diese Zeile enthält den Code 'DEFAULT_CATEGORY,'.
27. Diese Zeile enthält den Code 'build_category_index,'.
28. Diese Zeile enthält den Code 'can_manage_recipe,'.
29. Diese Zeile enthält den Code 'get_distinct_categories,'.
30. Diese Zeile enthält den Code 'normalize_category,'.
31. Diese Zeile enthält den Code 'parse_ingredient_text,'.
32. Diese Zeile enthält den Code 'replace_recipe_ingredients,'.
33. Diese Zeile enthält den Code 'resolve_title_image_url,'.
34. Diese Zeile enthält den Code 'sanitize_difficulty,'.
35. Diese Zeile enthält den Code ')'.
36. Diese Zeile enthält den Code 'from app.views import redirect, templates'.
37. Diese Zeile ist leer und trennt Abschnitte.
38. Diese Zeile enthält den Code 'router = APIRouter(tags=["recipes"])'.
39. Diese Zeile ist leer und trennt Abschnitte.
40. Diese Zeile enthält den Code 'PAGE_SIZE_DEFAULT = 20'.
41. Diese Zeile enthält den Code 'PAGE_SIZE_OPTIONS = (10, 20, 40, 80)'.
42. Diese Zeile ist leer und trennt Abschnitte.
43. Diese Zeile ist leer und trennt Abschnitte.
44. Diese Zeile enthält den Code 'def parse_positive_int(value: str, field_name: str) -> int:'.
45. Diese Zeile enthält den Code 'try:'.
46. Diese Zeile enthält den Code 'parsed = int(value)'.
47. Diese Zeile enthält den Code 'except ValueError as exc:'.
48. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} must be an int...'.
49. Diese Zeile enthält den Code 'if parsed <= 0:'.
50. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{field_name} must be greate...'.
51. Diese Zeile enthält den Code 'return parsed'.
52. Diese Zeile ist leer und trennt Abschnitte.
53. Diese Zeile ist leer und trennt Abschnitte.
54. Diese Zeile enthält den Code 'def normalize_image_url(value: str) -> str | None:'.
55. Diese Zeile enthält den Code 'cleaned = value.strip()'.
56. Diese Zeile enthält den Code 'if not cleaned:'.
57. Diese Zeile enthält den Code 'return None'.
58. Diese Zeile enthält den Code 'if not (cleaned.startswith("http://") or cleaned.startswith("https://")):'.
59. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title_image_url must start w...'.
60. Diese Zeile enthält den Code 'return cleaned'.
61. Diese Zeile ist leer und trennt Abschnitte.
62. Diese Zeile ist leer und trennt Abschnitte.
63. Diese Zeile enthält den Code 'def build_pagination_items(page: int, total_pages: int) -> list[int | None]:'.
64. Diese Zeile enthält den Code 'if total_pages <= 7:'.
65. Diese Zeile enthält den Code 'return list(range(1, total_pages + 1))'.
66. Diese Zeile enthält den Code 'if page <= 4:'.
67. Diese Zeile enthält den Code 'return [1, 2, 3, 4, 5, None, total_pages]'.
68. Diese Zeile enthält den Code 'if page >= total_pages - 3:'.
69. Diese Zeile enthält den Code 'return [1, None, total_pages - 4, total_pages - 3, total_pages - 2, total_pages - 1, total_pages]'.
70. Diese Zeile enthält den Code 'return [1, None, page - 1, page, page + 1, None, total_pages]'.
71. Diese Zeile ist leer und trennt Abschnitte.
72. Diese Zeile ist leer und trennt Abschnitte.
73. Diese Zeile enthält den Code 'def resolve_category_value(category_select: str, category_new: str, category_legacy: str = "") ->...'.
74. Diese Zeile enthält den Code 'if category_select and category_select != "__new__":'.
75. Diese Zeile enthält den Code 'return normalize_category(category_select)'.
76. Diese Zeile enthält den Code 'if category_new.strip():'.
77. Diese Zeile enthält den Code 'return normalize_category(category_new)'.
78. Diese Zeile enthält den Code 'if category_legacy.strip():'.
79. Diese Zeile enthält den Code 'return normalize_category(category_legacy)'.
80. Diese Zeile enthält den Code 'return DEFAULT_CATEGORY'.
81. Diese Zeile ist leer und trennt Abschnitte.
82. Diese Zeile ist leer und trennt Abschnitte.
83. Diese Zeile enthält den Code 'def fetch_recipe_or_404(db: Session, recipe_id: int) -> Recipe:'.
84. Diese Zeile enthält den Code 'recipe = db.scalar('.
85. Diese Zeile enthält den Code 'select(Recipe)'.
86. Diese Zeile enthält den Code '.where(Recipe.id == recipe_id)'.
87. Diese Zeile enthält den Code '.options('.
88. Diese Zeile enthält den Code 'joinedload(Recipe.creator),'.
89. Diese Zeile enthält den Code 'selectinload(Recipe.recipe_ingredients).joinedload(RecipeIngredient.ingredient),'.
90. Diese Zeile enthält den Code 'selectinload(Recipe.reviews).joinedload(Review.user),'.
91. Diese Zeile enthält den Code 'selectinload(Recipe.images),'.
92. Diese Zeile enthält den Code ')'.
93. Diese Zeile enthält den Code ')'.
94. Diese Zeile enthält den Code 'if not recipe:'.
95. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")'.
96. Diese Zeile enthält den Code 'return recipe'.
97. Diese Zeile ist leer und trennt Abschnitte.
98. Diese Zeile ist leer und trennt Abschnitte.
99. Diese Zeile enthält den Code 'def ensure_recipe_visible(recipe: Recipe, current_user: User | None) -> None:'.
100. Diese Zeile enthält den Code 'if recipe.is_published:'.
101. Diese Zeile enthält den Code 'return'.
102. Diese Zeile enthält den Code 'if current_user and (current_user.role == "admin" or current_user.id == recipe.creator_id):'.
103. Diese Zeile enthält den Code 'return'.
104. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")'.
105. Diese Zeile ist leer und trennt Abschnitte.
106. Diese Zeile ist leer und trennt Abschnitte.
107. Diese Zeile enthält den Code 'def ensure_recipe_access(user: User, recipe: Recipe) -> None:'.
108. Diese Zeile enthält den Code 'if not can_manage_recipe(user, recipe):'.
109. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for thi...'.
110. Diese Zeile ist leer und trennt Abschnitte.
111. Diese Zeile ist leer und trennt Abschnitte.
112. Diese Zeile enthält den Code 'def get_primary_image(recipe: Recipe) -> RecipeImage | None:'.
113. Diese Zeile enthält den Code 'for image in recipe.images:'.
114. Diese Zeile enthält den Code 'if image.is_primary:'.
115. Diese Zeile enthält den Code 'return image'.
116. Diese Zeile enthält den Code 'return recipe.images[0] if recipe.images else None'.
117. Diese Zeile ist leer und trennt Abschnitte.
118. Diese Zeile ist leer und trennt Abschnitte.
119. Diese Zeile enthält den Code 'def get_external_fallback_image_url(recipe: Recipe) -> str | None:'.
120. Diese Zeile enthält den Code 'if recipe.source_image_url:'.
121. Diese Zeile enthält den Code 'return recipe.source_image_url'.
122. Diese Zeile enthält den Code 'if recipe.title_image_url:'.
123. Diese Zeile enthält den Code 'return recipe.title_image_url'.
124. Diese Zeile enthält den Code 'return None'.
125. Diese Zeile ist leer und trennt Abschnitte.
126. Diese Zeile ist leer und trennt Abschnitte.
127. Diese Zeile enthält den Code 'def resolve_recipe_display_image(recipe: Recipe, primary_image: RecipeImage | None) -> tuple[str ...'.
128. Diese Zeile enthält den Code 'if primary_image:'.
129. Diese Zeile enthält den Code 'return f"/images/{primary_image.id}", "db"'.
130. Diese Zeile enthält den Code 'external_url = get_external_fallback_image_url(recipe)'.
131. Diese Zeile enthält den Code 'if external_url:'.
132. Diese Zeile enthält den Code 'return external_url, "external"'.
133. Diese Zeile enthält den Code 'return None, "placeholder"'.
134. Diese Zeile ist leer und trennt Abschnitte.
135. Diese Zeile ist leer und trennt Abschnitte.
136. Diese Zeile enthält den Code 'def can_direct_upload(user: User | None) -> bool:'.
137. Diese Zeile enthält den Code 'return bool(user and user.role == "admin")'.
138. Diese Zeile ist leer und trennt Abschnitte.
139. Diese Zeile ist leer und trennt Abschnitte.
140. Diese Zeile enthält den Code 'def can_request_image_change(user: User | None) -> bool:'.
141. Diese Zeile enthält den Code 'return bool(user and user.role != "admin")'.
142. Diese Zeile ist leer und trennt Abschnitte.
143. Diese Zeile ist leer und trennt Abschnitte.
144. Diese Zeile enthält den Code 'def user_has_pending_image_request(db: Session, recipe_id: int, current_user: User | None) -> bool:'.
145. Diese Zeile enthält den Code 'if not current_user or current_user.role == "admin":'.
146. Diese Zeile enthält den Code 'return False'.
147. Diese Zeile enthält den Code 'pending = db.scalar('.
148. Diese Zeile enthält den Code 'select(func.count())'.
149. Diese Zeile enthält den Code '.select_from(RecipeImageChangeRequest)'.
150. Diese Zeile enthält den Code '.where('.
151. Diese Zeile enthält den Code 'RecipeImageChangeRequest.recipe_id == recipe_id,'.
152. Diese Zeile enthält den Code 'RecipeImageChangeRequest.requester_user_id == current_user.id,'.
153. Diese Zeile enthält den Code 'RecipeImageChangeRequest.status == "pending",'.
154. Diese Zeile enthält den Code ')'.
155. Diese Zeile enthält den Code ')'.
156. Diese Zeile enthält den Code 'return bool(int(pending or 0))'.
157. Diese Zeile ist leer und trennt Abschnitte.
158. Diese Zeile ist leer und trennt Abschnitte.
159. Diese Zeile enthält den Code 'def set_recipe_primary_image(db: Session, recipe: Recipe, image_id: int) -> None:'.
160. Diese Zeile enthält den Code 'for image in recipe.images:'.
161. Diese Zeile enthält den Code 'image.is_primary = image.id == image_id'.
162. Diese Zeile enthält den Code 'db.flush()'.
163. Diese Zeile ist leer und trennt Abschnitte.
164. Diese Zeile ist leer und trennt Abschnitte.
165. Diese Zeile enthält den Code 'def maybe_promote_primary_after_delete(db: Session, recipe: Recipe) -> None:'.
166. Diese Zeile enthält den Code 'remaining = list(recipe.images)'.
167. Diese Zeile enthält den Code 'if not remaining:'.
168. Diese Zeile enthält den Code 'return'.
169. Diese Zeile enthält den Code 'if any(image.is_primary for image in remaining):'.
170. Diese Zeile enthält den Code 'return'.
171. Diese Zeile enthält den Code 'remaining[0].is_primary = True'.
172. Diese Zeile enthält den Code 'db.flush()'.
173. Diese Zeile ist leer und trennt Abschnitte.
174. Diese Zeile ist leer und trennt Abschnitte.
175. Diese Zeile enthält den Code 'def render_image_section('.
176. Diese Zeile enthält den Code 'request: Request,'.
177. Diese Zeile enthält den Code 'db: Session,'.
178. Diese Zeile enthält den Code 'recipe_id: int,'.
179. Diese Zeile enthält den Code 'current_user: User | None,'.
180. Diese Zeile enthält den Code '*,'.
181. Diese Zeile enthält den Code 'feedback_message: str = "",'.
182. Diese Zeile enthält den Code 'feedback_error: str = "",'.
183. Diese Zeile enthält den Code 'status_code: int = status.HTTP_200_OK,'.
184. Diese Zeile enthält den Code '):'.
185. Diese Zeile enthält den Code 'recipe = fetch_recipe_or_404(db, recipe_id)'.
186. Diese Zeile enthält den Code 'primary_image = get_primary_image(recipe)'.
187. Diese Zeile enthält den Code 'display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)'.
188. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
189. Diese Zeile enthält den Code '"partials/recipe_images.html",'.
190. Diese Zeile enthält den Code 'template_context('.
191. Diese Zeile enthält den Code 'request,'.
192. Diese Zeile enthält den Code 'current_user,'.
193. Diese Zeile enthält den Code 'recipe=recipe,'.
194. Diese Zeile enthält den Code 'primary_image=primary_image,'.
195. Diese Zeile enthält den Code 'display_image_url=display_image_url,'.
196. Diese Zeile enthält den Code 'display_image_kind=display_image_kind,'.
197. Diese Zeile enthält den Code 'can_upload_direct=can_direct_upload(current_user),'.
198. Diese Zeile enthält den Code 'can_request_change=can_request_image_change(current_user),'.
199. Diese Zeile enthält den Code 'has_pending_change_request=user_has_pending_image_request(db, recipe_id, current_user),'.
200. Diese Zeile enthält den Code 'image_feedback_message=feedback_message,'.
201. Diese Zeile enthält den Code 'image_feedback_error=feedback_error,'.
202. Diese Zeile enthält den Code '),'.
203. Diese Zeile enthält den Code 'status_code=status_code,'.
204. Diese Zeile enthält den Code ')'.
205. Diese Zeile ist leer und trennt Abschnitte.
206. Diese Zeile ist leer und trennt Abschnitte.
207. Diese Zeile enthält den Code 'def render_recipe_card_image('.
208. Diese Zeile enthält den Code 'request: Request,'.
209. Diese Zeile enthält den Code 'db: Session,'.
210. Diese Zeile enthält den Code 'recipe_id: int,'.
211. Diese Zeile enthält den Code 'current_user: User | None,'.
212. Diese Zeile enthält den Code '*,'.
213. Diese Zeile enthält den Code 'feedback_message: str = "",'.
214. Diese Zeile enthält den Code 'feedback_error: str = "",'.
215. Diese Zeile enthält den Code 'status_code: int = status.HTTP_200_OK,'.
216. Diese Zeile enthält den Code '):'.
217. Diese Zeile enthält den Code 'recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id).options(selectinload(Recipe.image...'.
218. Diese Zeile enthält den Code 'if not recipe:'.
219. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found", req...'.
220. Diese Zeile enthält den Code 'primary_image = get_primary_image(recipe)'.
221. Diese Zeile enthält den Code 'display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)'.
222. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
223. Diese Zeile enthält den Code '"partials/recipe_card_image.html",'.
224. Diese Zeile enthält den Code 'template_context('.
225. Diese Zeile enthält den Code 'request,'.
226. Diese Zeile enthält den Code 'current_user,'.
227. Diese Zeile enthält den Code 'recipe=recipe,'.
228. Diese Zeile enthält den Code 'primary_image=primary_image,'.
229. Diese Zeile enthält den Code 'display_image_url=display_image_url,'.
230. Diese Zeile enthält den Code 'display_image_kind=display_image_kind,'.
231. Diese Zeile enthält den Code 'can_upload_direct=can_direct_upload(current_user),'.
232. Diese Zeile enthält den Code 'can_request_change=can_request_image_change(current_user),'.
233. Diese Zeile enthält den Code 'has_pending_change_request=user_has_pending_image_request(db, recipe_id, current_user),'.
234. Diese Zeile enthält den Code 'image_feedback_message=feedback_message,'.
235. Diese Zeile enthält den Code 'image_feedback_error=feedback_error,'.
236. Diese Zeile enthält den Code '),'.
237. Diese Zeile enthält den Code 'status_code=status_code,'.
238. Diese Zeile enthält den Code ')'.
239. Diese Zeile ist leer und trennt Abschnitte.
240. Diese Zeile ist leer und trennt Abschnitte.
241. Diese Zeile enthält den Code '@router.get("/")'.
242. Diese Zeile enthält den Code 'def home_page('.
243. Diese Zeile enthält den Code 'request: Request,'.
244. Diese Zeile enthält den Code 'page: int = 1,'.
245. Diese Zeile enthält den Code 'per_page: int = PAGE_SIZE_DEFAULT,'.
246. Diese Zeile enthält den Code 'sort: str = "date",'.
247. Diese Zeile enthält den Code 'title: str = "",'.
248. Diese Zeile enthält den Code 'category: str = "",'.
249. Diese Zeile enthält den Code 'difficulty: str = "",'.
250. Diese Zeile enthält den Code 'ingredient: str = "",'.
251. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
252. Diese Zeile enthält den Code 'current_user: User | None = Depends(get_current_user_optional),'.
253. Diese Zeile enthält den Code '):'.
254. Diese Zeile enthält den Code 'page = max(page, 1)'.
255. Diese Zeile enthält den Code 'if per_page not in PAGE_SIZE_OPTIONS:'.
256. Diese Zeile enthält den Code 'per_page = PAGE_SIZE_DEFAULT'.
257. Diese Zeile enthält den Code 'category_index = build_category_index(db, only_published=True)'.
258. Diese Zeile enthält den Code 'category_options = sorted(category_index.keys(), key=str.casefold)'.
259. Diese Zeile enthält den Code 'selected_category = normalize_category(category, allow_empty=True)'.
260. Diese Zeile enthält den Code 'if selected_category and selected_category not in category_index:'.
261. Diese Zeile enthält den Code 'category_index[selected_category] = [selected_category]'.
262. Diese Zeile enthält den Code 'category_options = sorted(category_index.keys(), key=str.casefold)'.
263. Diese Zeile enthält den Code 'review_stats = ('.
264. Diese Zeile enthält den Code 'select('.
265. Diese Zeile enthält den Code 'Review.recipe_id.label("recipe_id"),'.
266. Diese Zeile enthält den Code 'func.avg(Review.rating).label("avg_rating"),'.
267. Diese Zeile enthält den Code 'func.count(Review.id).label("review_count"),'.
268. Diese Zeile enthält den Code ')'.
269. Diese Zeile enthält den Code '.group_by(Review.recipe_id)'.
270. Diese Zeile enthält den Code '.subquery()'.
271. Diese Zeile enthält den Code ')'.
272. Diese Zeile enthält den Code 'stmt = ('.
273. Diese Zeile enthält den Code 'select('.
274. Diese Zeile enthält den Code 'Recipe,'.
275. Diese Zeile enthält den Code 'func.coalesce(review_stats.c.avg_rating, 0).label("avg_rating"),'.
276. Diese Zeile enthält den Code 'func.coalesce(review_stats.c.review_count, 0).label("review_count"),'.
277. Diese Zeile enthält den Code ')'.
278. Diese Zeile enthält den Code '.outerjoin(review_stats, Recipe.id == review_stats.c.recipe_id)'.
279. Diese Zeile enthält den Code '.where(Recipe.is_published.is_(True))'.
280. Diese Zeile enthält den Code '.options(selectinload(Recipe.images))'.
281. Diese Zeile enthält den Code ')'.
282. Diese Zeile enthält den Code 'if title.strip():'.
283. Diese Zeile enthält den Code 'like = f"%{title.strip()}%"'.
284. Diese Zeile enthält den Code 'stmt = stmt.where(Recipe.title.ilike(like))'.
285. Diese Zeile enthält den Code 'if selected_category:'.
286. Diese Zeile enthält den Code 'stmt = stmt.where(Recipe.category.in_(category_index.get(selected_category, [selected_category])))'.
287. Diese Zeile enthält den Code 'if difficulty.strip():'.
288. Diese Zeile enthält den Code 'stmt = stmt.where(Recipe.difficulty == sanitize_difficulty(difficulty))'.
289. Diese Zeile enthält den Code 'if ingredient.strip():'.
290. Diese Zeile enthält den Code 'like = f"%{ingredient.strip().lower()}%"'.
291. Diese Zeile enthält den Code 'ingredient_recipe_ids = ('.
292. Diese Zeile enthält den Code 'select(RecipeIngredient.recipe_id)'.
293. Diese Zeile enthält den Code '.join(Ingredient, Ingredient.id == RecipeIngredient.ingredient_id)'.
294. Diese Zeile enthält den Code '.where(Ingredient.name.ilike(like))'.
295. Diese Zeile enthält den Code '.subquery()'.
296. Diese Zeile enthält den Code ')'.
297. Diese Zeile enthält den Code 'stmt = stmt.where(Recipe.id.in_(select(ingredient_recipe_ids.c.recipe_id)))'.
298. Diese Zeile enthält den Code 'if sort == "prep_time":'.
299. Diese Zeile enthält den Code 'stmt = stmt.order_by(Recipe.prep_time_minutes.asc(), Recipe.created_at.desc())'.
300. Diese Zeile enthält den Code 'elif sort == "avg_rating":'.
301. Diese Zeile enthält den Code 'stmt = stmt.order_by(desc("avg_rating"), Recipe.created_at.desc())'.
302. Diese Zeile enthält den Code 'else:'.
303. Diese Zeile enthält den Code 'stmt = stmt.order_by(Recipe.created_at.desc())'.
304. Diese Zeile enthält den Code 'total = db.scalar(select(func.count()).select_from(stmt.subquery()))'.
305. Diese Zeile enthält den Code 'pages = max((total + per_page - 1) // per_page, 1)'.
306. Diese Zeile enthält den Code 'page = min(page, pages)'.
307. Diese Zeile enthält den Code 'rows = db.execute(stmt.offset((page - 1) * per_page).limit(per_page)).all()'.
308. Diese Zeile enthält den Code 'recipe_ids = [int(row[0].id) for row in rows]'.
309. Diese Zeile enthält den Code 'pending_recipe_ids: set[int] = set()'.
310. Diese Zeile enthält den Code 'if current_user and current_user.role != "admin" and recipe_ids:'.
311. Diese Zeile enthält den Code 'pending_rows = db.scalars('.
312. Diese Zeile enthält den Code 'select(RecipeImageChangeRequest.recipe_id).where('.
313. Diese Zeile enthält den Code 'RecipeImageChangeRequest.recipe_id.in_(recipe_ids),'.
314. Diese Zeile enthält den Code 'RecipeImageChangeRequest.requester_user_id == current_user.id,'.
315. Diese Zeile enthält den Code 'RecipeImageChangeRequest.status == "pending",'.
316. Diese Zeile enthält den Code ')'.
317. Diese Zeile enthält den Code ').all()'.
318. Diese Zeile enthält den Code 'pending_recipe_ids = {int(item) for item in pending_rows}'.
319. Diese Zeile enthält den Code 'recipes_data = []'.
320. Diese Zeile enthält den Code 'for row in rows:'.
321. Diese Zeile enthält den Code 'recipe = row[0]'.
322. Diese Zeile enthält den Code 'primary_image = get_primary_image(recipe)'.
323. Diese Zeile enthält den Code 'display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)'.
324. Diese Zeile enthält den Code 'recipes_data.append('.
325. Diese Zeile enthält den Code '{'.
326. Diese Zeile enthält den Code '"recipe": recipe,'.
327. Diese Zeile enthält den Code '"avg_rating": float(row[1] or 0),'.
328. Diese Zeile enthält den Code '"review_count": int(row[2] or 0),'.
329. Diese Zeile enthält den Code '"primary_image": primary_image,'.
330. Diese Zeile enthält den Code '"display_image_url": display_image_url,'.
331. Diese Zeile enthält den Code '"display_image_kind": display_image_kind,'.
332. Diese Zeile enthält den Code '"has_pending_change_request": recipe.id in pending_recipe_ids,'.
333. Diese Zeile enthält den Code '}'.
334. Diese Zeile enthält den Code ')'.
335. Diese Zeile enthält den Code 'start_item = ((page - 1) * per_page + 1) if total > 0 else 0'.
336. Diese Zeile enthält den Code 'end_item = min(page * per_page, total)'.
337. Diese Zeile enthält den Code 'pagination_items = build_pagination_items(page, pages)'.
338. Diese Zeile enthält den Code 'context = template_context('.
339. Diese Zeile enthält den Code 'request,'.
340. Diese Zeile enthält den Code 'current_user,'.
341. Diese Zeile enthält den Code 'recipes_data=recipes_data,'.
342. Diese Zeile enthält den Code 'page=page,'.
343. Diese Zeile enthält den Code 'pages=pages,'.
344. Diese Zeile enthält den Code 'total_pages=pages,'.
345. Diese Zeile enthält den Code 'per_page=per_page,'.
346. Diese Zeile enthält den Code 'per_page_options=PAGE_SIZE_OPTIONS,'.
347. Diese Zeile enthält den Code 'category_options=category_options,'.
348. Diese Zeile enthält den Code 'total=total,'.
349. Diese Zeile enthält den Code 'total_count=total,'.
350. Diese Zeile enthält den Code 'start_item=start_item,'.
351. Diese Zeile enthält den Code 'end_item=end_item,'.
352. Diese Zeile enthält den Code 'pagination_items=pagination_items,'.
353. Diese Zeile enthält den Code 'sort=sort,'.
354. Diese Zeile enthält den Code 'title=title,'.
355. Diese Zeile enthält den Code 'category=selected_category,'.
356. Diese Zeile enthält den Code 'difficulty=difficulty,'.
357. Diese Zeile enthält den Code 'ingredient=ingredient,'.
358. Diese Zeile enthält den Code ')'.
359. Diese Zeile enthält den Code 'if request.headers.get("HX-Request") == "true":'.
360. Diese Zeile enthält den Code 'return templates.TemplateResponse("partials/recipe_list.html", context)'.
361. Diese Zeile enthält den Code 'return templates.TemplateResponse("home.html", context)'.
362. Diese Zeile ist leer und trennt Abschnitte.
363. Diese Zeile ist leer und trennt Abschnitte.
364. Diese Zeile enthält den Code '@router.get("/recipes/new")'.
365. Diese Zeile enthält den Code 'def create_recipe_page('.
366. Diese Zeile enthält den Code 'request: Request,'.
367. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
368. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
369. Diese Zeile enthält den Code '):'.
370. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
371. Diese Zeile enthält den Code '"recipe_form.html",'.
372. Diese Zeile enthält den Code 'template_context('.
373. Diese Zeile enthält den Code 'request,'.
374. Diese Zeile enthält den Code 'current_user,'.
375. Diese Zeile enthält den Code 'recipe=None,'.
376. Diese Zeile enthält den Code 'error=None,'.
377. Diese Zeile enthält den Code 'form_mode="create",'.
378. Diese Zeile enthält den Code 'category_options=get_distinct_categories(db, only_published=False),'.
379. Diese Zeile enthält den Code 'selected_category=DEFAULT_CATEGORY,'.
380. Diese Zeile enthält den Code 'category_new_value="",'.
381. Diese Zeile enthält den Code '),'.
382. Diese Zeile enthält den Code ')'.
383. Diese Zeile ist leer und trennt Abschnitte.
384. Diese Zeile ist leer und trennt Abschnitte.
385. Diese Zeile enthält den Code '@router.post("/recipes")'.
386. Diese Zeile enthält den Code '@router.post("/recipes/new")'.
387. Diese Zeile enthält den Code 'async def create_recipe_submit('.
388. Diese Zeile enthält den Code 'request: Request,'.
389. Diese Zeile enthält den Code 'title: str = Form(...),'.
390. Diese Zeile enthält den Code 'description: str = Form(...),'.
391. Diese Zeile enthält den Code 'instructions: str = Form(...),'.
392. Diese Zeile enthält den Code 'category_select: str = Form(DEFAULT_CATEGORY),'.
393. Diese Zeile enthält den Code 'category_new: str = Form(""),'.
394. Diese Zeile enthält den Code 'category: str = Form(""),'.
395. Diese Zeile enthält den Code 'title_image_url: str = Form(""),'.
396. Diese Zeile enthält den Code 'prep_time_minutes: str = Form(...),'.
397. Diese Zeile enthält den Code 'difficulty: str = Form(...),'.
398. Diese Zeile enthält den Code 'ingredients_text: str = Form(""),'.
399. Diese Zeile enthält den Code 'image: UploadFile | None = File(None),'.
400. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
401. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
402. Diese Zeile enthält den Code '):'.
403. Diese Zeile enthält den Code 'prep_time = parse_positive_int(prep_time_minutes, "prep_time_minutes")'.
404. Diese Zeile enthält den Code 'normalized_difficulty = sanitize_difficulty(difficulty)'.
405. Diese Zeile enthält den Code 'if not title.strip() or not instructions.strip():'.
406. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and instructions are r...'.
407. Diese Zeile enthält den Code 'recipe = Recipe('.
408. Diese Zeile enthält den Code 'title=title.strip(),'.
409. Diese Zeile enthält den Code 'title_image_url=normalize_image_url(title_image_url),'.
410. Diese Zeile enthält den Code 'source="admin_manual",'.
411. Diese Zeile enthält den Code 'description=description.strip(),'.
412. Diese Zeile enthält den Code 'instructions=instructions.strip(),'.
413. Diese Zeile enthält den Code 'category=resolve_category_value(category_select, category_new, category),'.
414. Diese Zeile enthält den Code 'prep_time_minutes=prep_time,'.
415. Diese Zeile enthält den Code 'difficulty=normalized_difficulty,'.
416. Diese Zeile enthält den Code 'creator_id=current_user.id,'.
417. Diese Zeile enthält den Code 'is_published=True,'.
418. Diese Zeile enthält den Code ')'.
419. Diese Zeile enthält den Code 'db.add(recipe)'.
420. Diese Zeile enthält den Code 'db.flush()'.
421. Diese Zeile enthält den Code 'ingredient_entries = parse_ingredient_text(ingredients_text)'.
422. Diese Zeile enthält den Code 'replace_recipe_ingredients(db, recipe, ingredient_entries)'.
423. Diese Zeile enthält den Code 'if image and image.filename:'.
424. Diese Zeile enthält den Code 'data = await image.read()'.
425. Diese Zeile enthält den Code 'try:'.
426. Diese Zeile enthält den Code 'validate_image_upload((image.content_type or "").lower(), data)'.
427. Diese Zeile enthält den Code 'except ImageValidationError as exc:'.
428. Diese Zeile enthält den Code 'raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc'.
429. Diese Zeile enthält den Code 'image_content_type = (image.content_type or "application/octet-stream").lower()'.
430. Diese Zeile enthält den Code 'db.add('.
431. Diese Zeile enthält den Code 'RecipeImage('.
432. Diese Zeile enthält den Code 'recipe_id=recipe.id,'.
433. Diese Zeile enthält den Code 'filename=safe_image_filename(image.filename or "", image_content_type),'.
434. Diese Zeile enthält den Code 'content_type=image_content_type,'.
435. Diese Zeile enthält den Code 'data=data,'.
436. Diese Zeile enthält den Code 'is_primary=True,'.
437. Diese Zeile enthält den Code ')'.
438. Diese Zeile enthält den Code ')'.
439. Diese Zeile enthält den Code 'db.commit()'.
440. Diese Zeile enthält den Code 'return redirect(f"/recipes/{recipe.id}")'.
441. Diese Zeile ist leer und trennt Abschnitte.
442. Diese Zeile ist leer und trennt Abschnitte.
443. Diese Zeile enthält den Code '@router.get("/recipes/{recipe_id}")'.
444. Diese Zeile enthält den Code 'def recipe_detail('.
445. Diese Zeile enthält den Code 'request: Request,'.
446. Diese Zeile enthält den Code 'recipe_id: int,'.
447. Diese Zeile enthält den Code 'message: str = "",'.
448. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
449. Diese Zeile enthält den Code 'current_user: User | None = Depends(get_current_user_optional),'.
450. Diese Zeile enthält den Code '):'.
451. Diese Zeile enthält den Code 'recipe = fetch_recipe_or_404(db, recipe_id)'.
452. Diese Zeile enthält den Code 'ensure_recipe_visible(recipe, current_user)'.
453. Diese Zeile enthält den Code 'avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.recipe_id =...'.
454. Diese Zeile enthält den Code 'review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe_id)) or 0'.
455. Diese Zeile enthält den Code 'primary_image = get_primary_image(recipe)'.
456. Diese Zeile enthält den Code 'display_image_url, display_image_kind = resolve_recipe_display_image(recipe, primary_image)'.
457. Diese Zeile enthält den Code 'is_favorite = False'.
458. Diese Zeile enthält den Code 'if current_user:'.
459. Diese Zeile enthält den Code 'is_favorite = db.scalar('.
460. Diese Zeile enthält den Code 'select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id))'.
461. Diese Zeile enthält den Code ') is not None'.
462. Diese Zeile enthält den Code 'message_map = {'.
463. Diese Zeile enthält den Code '"image_change_submitted": t("images.request_submitted", request=request),'.
464. Diese Zeile enthält den Code '"image_upload_done": t("images.uploaded", request=request),'.
465. Diese Zeile enthält den Code '}'.
466. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
467. Diese Zeile enthält den Code '"recipe_detail.html",'.
468. Diese Zeile enthält den Code 'template_context('.
469. Diese Zeile enthält den Code 'request,'.
470. Diese Zeile enthält den Code 'current_user,'.
471. Diese Zeile enthält den Code 'recipe=recipe,'.
472. Diese Zeile enthält den Code 'avg_rating=float(avg_rating),'.
473. Diese Zeile enthält den Code 'review_count=int(review_count),'.
474. Diese Zeile enthält den Code 'is_favorite=is_favorite,'.
475. Diese Zeile enthält den Code 'primary_image=primary_image,'.
476. Diese Zeile enthält den Code 'display_image_url=display_image_url,'.
477. Diese Zeile enthält den Code 'display_image_kind=display_image_kind,'.
478. Diese Zeile enthält den Code 'can_upload_direct=can_direct_upload(current_user),'.
479. Diese Zeile enthält den Code 'can_request_change=can_request_image_change(current_user),'.
480. Diese Zeile enthält den Code 'has_pending_change_request=user_has_pending_image_request(db, recipe_id, current_user),'.
481. Diese Zeile enthält den Code 'image_feedback_message=message_map.get(message, ""),'.
482. Diese Zeile enthält den Code 'image_feedback_error="",'.
483. Diese Zeile enthält den Code '),'.
484. Diese Zeile enthält den Code ')'.
485. Diese Zeile ist leer und trennt Abschnitte.
486. Diese Zeile ist leer und trennt Abschnitte.
487. Diese Zeile enthält den Code '@router.get("/recipes/{recipe_id}/edit")'.
488. Diese Zeile enthält den Code 'def edit_recipe_page('.
489. Diese Zeile enthält den Code 'request: Request,'.
490. Diese Zeile enthält den Code 'recipe_id: int,'.
491. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
492. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
493. Diese Zeile enthält den Code '):'.
494. Diese Zeile enthält den Code 'recipe = fetch_recipe_or_404(db, recipe_id)'.
495. Diese Zeile enthält den Code 'ensure_recipe_access(current_user, recipe)'.
496. Diese Zeile enthält den Code 'selected_category = normalize_category(recipe.category)'.
497. Diese Zeile enthält den Code 'category_options = get_distinct_categories(db)'.
498. Diese Zeile enthält den Code 'if selected_category not in category_options:'.
499. Diese Zeile enthält den Code 'category_options = sorted([*category_options, selected_category], key=str.casefold)'.
500. Diese Zeile enthält den Code 'ingredients_text = "\n".join('.
501. Diese Zeile enthält den Code 'f"{link.ingredient.name}|{link.quantity_text}|{link.grams or ''}".rstrip("|")'.
502. Diese Zeile enthält den Code 'for link in recipe.recipe_ingredients'.
503. Diese Zeile enthält den Code ')'.
504. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
505. Diese Zeile enthält den Code '"recipe_form.html",'.
506. Diese Zeile enthält den Code 'template_context('.
507. Diese Zeile enthält den Code 'request,'.
508. Diese Zeile enthält den Code 'current_user,'.
509. Diese Zeile enthält den Code 'recipe=recipe,'.
510. Diese Zeile enthält den Code 'ingredients_text=ingredients_text,'.
511. Diese Zeile enthält den Code 'error=None,'.
512. Diese Zeile enthält den Code 'form_mode="edit",'.
513. Diese Zeile enthält den Code 'category_options=category_options,'.
514. Diese Zeile enthält den Code 'selected_category=selected_category,'.
515. Diese Zeile enthält den Code 'category_new_value="",'.
516. Diese Zeile enthält den Code '),'.
517. Diese Zeile enthält den Code ')'.
518. Diese Zeile ist leer und trennt Abschnitte.
519. Diese Zeile ist leer und trennt Abschnitte.
520. Diese Zeile enthält den Code '@router.post("/recipes/{recipe_id}/edit")'.
521. Diese Zeile enthält den Code 'async def edit_recipe_submit('.
522. Diese Zeile enthält den Code 'recipe_id: int,'.
523. Diese Zeile enthält den Code 'title: str = Form(...),'.
524. Diese Zeile enthält den Code 'description: str = Form(...),'.
525. Diese Zeile enthält den Code 'instructions: str = Form(...),'.
526. Diese Zeile enthält den Code 'category_select: str = Form(DEFAULT_CATEGORY),'.
527. Diese Zeile enthält den Code 'category_new: str = Form(""),'.
528. Diese Zeile enthält den Code 'category: str = Form(""),'.
529. Diese Zeile enthält den Code 'title_image_url: str = Form(""),'.
530. Diese Zeile enthält den Code 'prep_time_minutes: str = Form(...),'.
531. Diese Zeile enthält den Code 'difficulty: str = Form(...),'.
532. Diese Zeile enthält den Code 'ingredients_text: str = Form(""),'.
533. Diese Zeile enthält den Code 'image: UploadFile | None = File(None),'.
534. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
535. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
536. Diese Zeile enthält den Code '):'.
537. Diese Zeile enthält den Code 'recipe = fetch_recipe_or_404(db, recipe_id)'.
538. Diese Zeile enthält den Code 'ensure_recipe_access(current_user, recipe)'.
539. Diese Zeile enthält den Code 'recipe.title = title.strip()'.
540. Diese Zeile enthält den Code 'recipe.title_image_url = normalize_image_url(title_image_url)'.
541. Diese Zeile enthält den Code 'recipe.description = description.strip()'.
542. Diese Zeile enthält den Code 'recipe.instructions = instructions.strip()'.
543. Diese Zeile enthält den Code 'recipe.category = resolve_category_value(category_select, category_new, category)'.
544. Diese Zeile enthält den Code 'recipe.prep_time_minutes = parse_positive_int(prep_time_minutes, "prep_time_minutes")'.
545. Diese Zeile enthält den Code 'recipe.difficulty = sanitize_difficulty(difficulty)'.
546. Diese Zeile enthält den Code 'replace_recipe_ingredients(db, recipe, parse_ingredient_text(ingredients_text))'.
547. Diese Zeile enthält den Code 'if image and image.filename:'.
548. Diese Zeile enthält den Code 'data = await image.read()'.
549. Diese Zeile enthält den Code 'try:'.
550. Diese Zeile enthält den Code 'validate_image_upload((image.content_type or "").lower(), data)'.
551. Diese Zeile enthält den Code 'except ImageValidationError as exc:'.
552. Diese Zeile enthält den Code 'raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc'.
553. Diese Zeile enthält den Code 'image_content_type = (image.content_type or "application/octet-stream").lower()'.
554. Diese Zeile enthält den Code 'has_images = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id ...'.
555. Diese Zeile enthält den Code 'db.add('.
556. Diese Zeile enthält den Code 'RecipeImage('.
557. Diese Zeile enthält den Code 'recipe_id=recipe.id,'.
558. Diese Zeile enthält den Code 'filename=safe_image_filename(image.filename or "", image_content_type),'.
559. Diese Zeile enthält den Code 'content_type=image_content_type,'.
560. Diese Zeile enthält den Code 'data=data,'.
561. Diese Zeile enthält den Code 'is_primary=has_images == 0,'.
562. Diese Zeile enthält den Code ')'.
563. Diese Zeile enthält den Code ')'.
564. Diese Zeile enthält den Code 'db.commit()'.
565. Diese Zeile enthält den Code 'return redirect(f"/recipes/{recipe.id}")'.
566. Diese Zeile ist leer und trennt Abschnitte.
567. Diese Zeile ist leer und trennt Abschnitte.
568. Diese Zeile enthält den Code '@router.post("/recipes/{recipe_id}/delete")'.
569. Diese Zeile enthält den Code 'def delete_recipe('.
570. Diese Zeile enthält den Code 'recipe_id: int,'.
571. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
572. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
573. Diese Zeile enthält den Code '):'.
574. Diese Zeile enthält den Code 'recipe = fetch_recipe_or_404(db, recipe_id)'.
575. Diese Zeile enthält den Code 'ensure_recipe_access(current_user, recipe)'.
576. Diese Zeile enthält den Code 'db.delete(recipe)'.
577. Diese Zeile enthält den Code 'db.commit()'.
578. Diese Zeile enthält den Code 'return redirect("/my-recipes")'.
579. Diese Zeile ist leer und trennt Abschnitte.
580. Diese Zeile ist leer und trennt Abschnitte.
581. Diese Zeile enthält den Code '@router.post("/recipes/{recipe_id}/reviews")'.
582. Diese Zeile enthält den Code 'def upsert_review('.
583. Diese Zeile enthält den Code 'recipe_id: int,'.
584. Diese Zeile enthält den Code 'rating: int = Form(...),'.
585. Diese Zeile enthält den Code 'comment: str = Form(""),'.
586. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
587. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
588. Diese Zeile enthält den Code '):'.
589. Diese Zeile enthält den Code 'recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))'.
590. Diese Zeile enthält den Code 'if not recipe:'.
591. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")'.
592. Diese Zeile enthält den Code 'if not recipe.is_published:'.
593. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")'.
594. Diese Zeile enthält den Code 'if rating < 1 or rating > 5:'.
595. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rating must be between 1 and...'.
596. Diese Zeile enthält den Code 'review = db.scalar(select(Review).where(and_(Review.recipe_id == recipe_id, Review.user_id == cur...'.
597. Diese Zeile enthält den Code 'if review:'.
598. Diese Zeile enthält den Code 'review.rating = rating'.
599. Diese Zeile enthält den Code 'review.comment = comment.strip()'.
600. Diese Zeile enthält den Code 'else:'.
601. Diese Zeile enthält den Code 'db.add(Review(recipe_id=recipe_id, user_id=current_user.id, rating=rating, comment=comment.strip()))'.
602. Diese Zeile enthält den Code 'db.commit()'.
603. Diese Zeile enthält den Code 'return redirect(f"/recipes/{recipe_id}")'.
604. Diese Zeile ist leer und trennt Abschnitte.
605. Diese Zeile ist leer und trennt Abschnitte.
606. Diese Zeile enthält den Code '@router.post("/reviews/{review_id}/delete")'.
607. Diese Zeile enthält den Code 'def delete_review('.
608. Diese Zeile enthält den Code 'review_id: int,'.
609. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
610. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
611. Diese Zeile enthält den Code '):'.
612. Diese Zeile enthält den Code 'review = db.scalar(select(Review).where(Review.id == review_id).options(joinedload(Review.recipe)))'.
613. Diese Zeile enthält den Code 'if not review:'.
614. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")'.
615. Diese Zeile enthält den Code 'if current_user.role != "admin" and review.user_id != current_user.id:'.
616. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for thi...'.
617. Diese Zeile enthält den Code 'recipe_id = review.recipe_id'.
618. Diese Zeile enthält den Code 'db.delete(review)'.
619. Diese Zeile enthält den Code 'db.commit()'.
620. Diese Zeile enthält den Code 'return redirect(f"/recipes/{recipe_id}")'.
621. Diese Zeile ist leer und trennt Abschnitte.
622. Diese Zeile ist leer und trennt Abschnitte.
623. Diese Zeile enthält den Code '@router.post("/recipes/{recipe_id}/favorite")'.
624. Diese Zeile enthält den Code 'def toggle_favorite('.
625. Diese Zeile enthält den Code 'request: Request,'.
626. Diese Zeile enthält den Code 'recipe_id: int,'.
627. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
628. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
629. Diese Zeile enthält den Code '):'.
630. Diese Zeile enthält den Code 'recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))'.
631. Diese Zeile enthält den Code 'if not recipe or not recipe.is_published:'.
632. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")'.
633. Diese Zeile enthält den Code 'favorite = db.scalar('.
634. Diese Zeile enthält den Code 'select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id))'.
635. Diese Zeile enthält den Code ')'.
636. Diese Zeile enthält den Code 'is_favorite = True'.
637. Diese Zeile enthält den Code 'if favorite:'.
638. Diese Zeile enthält den Code 'db.delete(favorite)'.
639. Diese Zeile enthält den Code 'is_favorite = False'.
640. Diese Zeile enthält den Code 'else:'.
641. Diese Zeile enthält den Code 'db.add(Favorite(user_id=current_user.id, recipe_id=recipe_id))'.
642. Diese Zeile enthält den Code 'is_favorite = True'.
643. Diese Zeile enthält den Code 'db.commit()'.
644. Diese Zeile enthält den Code 'if request.headers.get("HX-Request") == "true":'.
645. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
646. Diese Zeile enthält den Code '"partials/favorite_button.html",'.
647. Diese Zeile enthält den Code 'template_context(request, current_user, recipe=recipe, is_favorite=is_favorite),'.
648. Diese Zeile enthält den Code ')'.
649. Diese Zeile enthält den Code 'return redirect(f"/recipes/{recipe_id}")'.
650. Diese Zeile ist leer und trennt Abschnitte.
651. Diese Zeile ist leer und trennt Abschnitte.
652. Diese Zeile enthält den Code '@router.get("/favorites")'.
653. Diese Zeile enthält den Code 'def favorites_page('.
654. Diese Zeile enthält den Code 'request: Request,'.
655. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
656. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
657. Diese Zeile enthält den Code '):'.
658. Diese Zeile enthält den Code 'favorite_recipes = db.scalars('.
659. Diese Zeile enthält den Code 'select(Recipe)'.
660. Diese Zeile enthält den Code '.join(Favorite, Favorite.recipe_id == Recipe.id)'.
661. Diese Zeile enthält den Code '.where(Favorite.user_id == current_user.id, Recipe.is_published.is_(True))'.
662. Diese Zeile enthält den Code '.order_by(Recipe.created_at.desc())'.
663. Diese Zeile enthält den Code '.options(selectinload(Recipe.images))'.
664. Diese Zeile enthält den Code ').all()'.
665. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
666. Diese Zeile enthält den Code '"favorites.html",'.
667. Diese Zeile enthält den Code 'template_context(request, current_user, favorite_recipes=favorite_recipes),'.
668. Diese Zeile enthält den Code ')'.
669. Diese Zeile ist leer und trennt Abschnitte.
670. Diese Zeile ist leer und trennt Abschnitte.
671. Diese Zeile enthält den Code '@router.get("/my-recipes")'.
672. Diese Zeile enthält den Code 'def my_recipes_page('.
673. Diese Zeile enthält den Code 'request: Request,'.
674. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
675. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
676. Diese Zeile enthält den Code '):'.
677. Diese Zeile enthält den Code 'stmt = select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.images))'.
678. Diese Zeile enthält den Code 'if current_user.role != "admin":'.
679. Diese Zeile enthält den Code 'stmt = stmt.where(Recipe.creator_id == current_user.id)'.
680. Diese Zeile enthält den Code 'recipes = db.scalars(stmt).all()'.
681. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
682. Diese Zeile enthält den Code '"my_recipes.html",'.
683. Diese Zeile enthält den Code 'template_context(request, current_user, recipes=recipes),'.
684. Diese Zeile enthält den Code ')'.
685. Diese Zeile ist leer und trennt Abschnitte.
686. Diese Zeile ist leer und trennt Abschnitte.
687. Diese Zeile enthält den Code '@router.post("/recipes/{recipe_id}/images")'.
688. Diese Zeile enthält den Code '@limiter.limit("10/minute", key_func=key_by_user_or_ip)'.
689. Diese Zeile enthält den Code 'async def upload_recipe_image('.
690. Diese Zeile enthält den Code 'request: Request,'.
691. Diese Zeile enthält den Code 'response: Response,'.
692. Diese Zeile enthält den Code 'recipe_id: int,'.
693. Diese Zeile enthält den Code 'set_primary: bool = Form(False),'.
694. Diese Zeile enthält den Code 'response_mode: str = Form("detail"),'.
695. Diese Zeile enthält den Code 'file: UploadFile = File(...),'.
696. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
697. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
698. Diese Zeile enthält den Code '):'.
699. Diese Zeile enthält den Code '_ = response'.
700. Diese Zeile enthält den Code 'if current_user.role != "admin":'.
701. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required", reque...'.
702. Diese Zeile enthält den Code 'recipe = fetch_recipe_or_404(db, recipe_id)'.
703. Diese Zeile enthält den Code 'data = await file.read()'.
704. Diese Zeile enthält den Code 'content_type = (file.content_type or "").lower()'.
705. Diese Zeile enthält den Code 'try:'.
706. Diese Zeile enthält den Code 'validate_image_upload(content_type, data)'.
707. Diese Zeile enthält den Code 'except ImageValidationError as exc:'.
708. Diese Zeile enthält den Code 'raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc'.
709. Diese Zeile enthält den Code 'has_images = db.scalar(select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id ...'.
710. Diese Zeile enthält den Code 'query_value = request.query_params.get("set_primary")'.
711. Diese Zeile enthält den Code 'if query_value is not None:'.
712. Diese Zeile enthält den Code 'set_primary = query_value.strip().lower() in {"1", "true", "yes", "on"}'.
713. Diese Zeile enthält den Code 'new_is_primary = set_primary or has_images == 0'.
714. Diese Zeile enthält den Code 'recipe_image = RecipeImage('.
715. Diese Zeile enthält den Code 'recipe_id=recipe_id,'.
716. Diese Zeile enthält den Code 'filename=safe_image_filename(file.filename or "", content_type),'.
717. Diese Zeile enthält den Code 'content_type=content_type,'.
718. Diese Zeile enthält den Code 'data=data,'.
719. Diese Zeile enthält den Code 'is_primary=new_is_primary,'.
720. Diese Zeile enthält den Code ')'.
721. Diese Zeile enthält den Code 'db.add(recipe_image)'.
722. Diese Zeile enthält den Code 'db.flush()'.
723. Diese Zeile enthält den Code 'if new_is_primary:'.
724. Diese Zeile enthält den Code 'set_recipe_primary_image(db, recipe, recipe_image.id)'.
725. Diese Zeile enthält den Code 'db.commit()'.
726. Diese Zeile enthält den Code 'if request.headers.get("HX-Request") == "true":'.
727. Diese Zeile enthält den Code 'if response_mode == "card":'.
728. Diese Zeile enthält den Code 'return render_recipe_card_image('.
729. Diese Zeile enthält den Code 'request,'.
730. Diese Zeile enthält den Code 'db,'.
731. Diese Zeile enthält den Code 'recipe_id,'.
732. Diese Zeile enthält den Code 'current_user,'.
733. Diese Zeile enthält den Code 'feedback_message=t("images.uploaded", request=request),'.
734. Diese Zeile enthält den Code ')'.
735. Diese Zeile enthält den Code 'return render_image_section('.
736. Diese Zeile enthält den Code 'request,'.
737. Diese Zeile enthält den Code 'db,'.
738. Diese Zeile enthält den Code 'recipe_id,'.
739. Diese Zeile enthält den Code 'current_user,'.
740. Diese Zeile enthält den Code 'feedback_message=t("images.uploaded", request=request),'.
741. Diese Zeile enthält den Code ')'.
742. Diese Zeile enthält den Code 'return redirect(f"/recipes/{recipe_id}?message=image_upload_done")'.
743. Diese Zeile ist leer und trennt Abschnitte.
744. Diese Zeile ist leer und trennt Abschnitte.
745. Diese Zeile enthält den Code '@router.post("/recipes/{recipe_id}/image-change-request")'.
746. Diese Zeile enthält den Code '@limiter.limit("10/minute", key_func=key_by_ip)'.
747. Diese Zeile enthält den Code '@limiter.limit("5/minute", key_func=key_by_user_or_ip)'.
748. Diese Zeile enthält den Code 'async def request_recipe_image_change('.
749. Diese Zeile enthält den Code 'request: Request,'.
750. Diese Zeile enthält den Code 'response: Response,'.
751. Diese Zeile enthält den Code 'recipe_id: int,'.
752. Diese Zeile enthält den Code 'response_mode: str = Form("detail"),'.
753. Diese Zeile enthält den Code 'file: UploadFile = File(...),'.
754. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
755. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
756. Diese Zeile enthält den Code '):'.
757. Diese Zeile enthält den Code '_ = response'.
758. Diese Zeile enthält den Code 'if current_user.role == "admin":'.
759. Diese Zeile enthält den Code 'raise HTTPException('.
760. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
761. Diese Zeile enthält den Code 'detail=t("images.admin_use_direct_upload", request=request),'.
762. Diese Zeile enthält den Code ')'.
763. Diese Zeile enthält den Code 'recipe = fetch_recipe_or_404(db, recipe_id)'.
764. Diese Zeile enthält den Code 'if not recipe.is_published:'.
765. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found", req...'.
766. Diese Zeile enthält den Code 'data = await file.read()'.
767. Diese Zeile enthält den Code 'content_type = (file.content_type or "").lower()'.
768. Diese Zeile enthält den Code 'try:'.
769. Diese Zeile enthält den Code 'validate_image_upload(content_type, data)'.
770. Diese Zeile enthält den Code 'except ImageValidationError as exc:'.
771. Diese Zeile enthält den Code 'raise HTTPException(status_code=exc.status_code, detail=str(exc)) from exc'.
772. Diese Zeile enthält den Code 'change_request = RecipeImageChangeRequest('.
773. Diese Zeile enthält den Code 'recipe_id=recipe_id,'.
774. Diese Zeile enthält den Code 'requester_user_id=current_user.id,'.
775. Diese Zeile enthält den Code 'status="pending",'.
776. Diese Zeile enthält den Code ')'.
777. Diese Zeile enthält den Code 'db.add(change_request)'.
778. Diese Zeile enthält den Code 'db.flush()'.
779. Diese Zeile enthält den Code 'db.add('.
780. Diese Zeile enthält den Code 'RecipeImageChangeFile('.
781. Diese Zeile enthält den Code 'request_id=change_request.id,'.
782. Diese Zeile enthält den Code 'filename=safe_image_filename(file.filename or "", content_type),'.
783. Diese Zeile enthält den Code 'content_type=content_type,'.
784. Diese Zeile enthält den Code 'data=data,'.
785. Diese Zeile enthält den Code ')'.
786. Diese Zeile enthält den Code ')'.
787. Diese Zeile enthält den Code 'db.commit()'.
788. Diese Zeile enthält den Code 'if request.headers.get("HX-Request") == "true":'.
789. Diese Zeile enthält den Code 'if response_mode == "card":'.
790. Diese Zeile enthält den Code 'return render_recipe_card_image('.
791. Diese Zeile enthält den Code 'request,'.
792. Diese Zeile enthält den Code 'db,'.
793. Diese Zeile enthält den Code 'recipe_id,'.
794. Diese Zeile enthält den Code 'current_user,'.
795. Diese Zeile enthält den Code 'feedback_message=t("images.request_submitted", request=request),'.
796. Diese Zeile enthält den Code ')'.
797. Diese Zeile enthält den Code 'return render_image_section('.
798. Diese Zeile enthält den Code 'request,'.
799. Diese Zeile enthält den Code 'db,'.
800. Diese Zeile enthält den Code 'recipe_id,'.
801. Diese Zeile enthält den Code 'current_user,'.
802. Diese Zeile enthält den Code 'feedback_message=t("images.request_submitted", request=request),'.
803. Diese Zeile enthält den Code ')'.
804. Diese Zeile enthält den Code 'return redirect(f"/recipes/{recipe_id}?message=image_change_submitted")'.
805. Diese Zeile ist leer und trennt Abschnitte.
806. Diese Zeile ist leer und trennt Abschnitte.
807. Diese Zeile enthält den Code '@router.get("/images/{image_id}")'.
808. Diese Zeile enthält den Code 'def get_image(image_id: int, db: Session = Depends(get_db)):'.
809. Diese Zeile enthält den Code 'image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id))'.
810. Diese Zeile enthält den Code 'if not image:'.
811. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))'.
812. Diese Zeile enthält den Code 'return Response('.
813. Diese Zeile enthält den Code 'content=image.data,'.
814. Diese Zeile enthält den Code 'media_type=image.content_type,'.
815. Diese Zeile enthält den Code 'headers={"Cache-Control": "public, max-age=86400"},'.
816. Diese Zeile enthält den Code ')'.
817. Diese Zeile ist leer und trennt Abschnitte.
818. Diese Zeile ist leer und trennt Abschnitte.
819. Diese Zeile enthält den Code '@router.get("/external-image")'.
820. Diese Zeile enthält den Code 'def external_image(url: str):'.
821. Diese Zeile enthält den Code 'try:'.
822. Diese Zeile enthält den Code 'resolved_url = resolve_title_image_url(url)'.
823. Diese Zeile enthält den Code 'except Exception as exc:'.
824. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Could not resolve image URL...'.
825. Diese Zeile enthält den Code 'if not resolved_url:'.
826. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No image URL available.")'.
827. Diese Zeile enthält den Code 'return RedirectResponse(url=resolved_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)'.
828. Diese Zeile ist leer und trennt Abschnitte.
829. Diese Zeile ist leer und trennt Abschnitte.
830. Diese Zeile enthält den Code '@router.delete("/images/{image_id}")'.
831. Diese Zeile enthält den Code 'def delete_image_api('.
832. Diese Zeile enthält den Code 'image_id: int,'.
833. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
834. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
835. Diese Zeile enthält den Code '):'.
836. Diese Zeile enthält den Code 'image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedload(Recipe...'.
837. Diese Zeile enthält den Code 'if not image:'.
838. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))'.
839. Diese Zeile enthält den Code 'if current_user.role != "admin":'.
840. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))'.
841. Diese Zeile enthält den Code 'recipe = image.recipe'.
842. Diese Zeile enthält den Code 'db.delete(image)'.
843. Diese Zeile enthält den Code 'db.flush()'.
844. Diese Zeile enthält den Code 'maybe_promote_primary_after_delete(db, recipe)'.
845. Diese Zeile enthält den Code 'db.commit()'.
846. Diese Zeile enthält den Code 'return {"status": "deleted"}'.
847. Diese Zeile ist leer und trennt Abschnitte.
848. Diese Zeile ist leer und trennt Abschnitte.
849. Diese Zeile enthält den Code '@router.post("/images/{image_id}/delete")'.
850. Diese Zeile enthält den Code 'def delete_image_form('.
851. Diese Zeile enthält den Code 'request: Request,'.
852. Diese Zeile enthält den Code 'image_id: int,'.
853. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
854. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
855. Diese Zeile enthält den Code '):'.
856. Diese Zeile enthält den Code 'image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedload(Recipe...'.
857. Diese Zeile enthält den Code 'if not image:'.
858. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))'.
859. Diese Zeile enthält den Code 'recipe = image.recipe'.
860. Diese Zeile enthält den Code 'recipe_id = image.recipe_id'.
861. Diese Zeile enthält den Code 'if current_user.role != "admin":'.
862. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))'.
863. Diese Zeile enthält den Code 'db.delete(image)'.
864. Diese Zeile enthält den Code 'db.flush()'.
865. Diese Zeile enthält den Code 'maybe_promote_primary_after_delete(db, recipe)'.
866. Diese Zeile enthält den Code 'db.commit()'.
867. Diese Zeile enthält den Code 'if request.headers.get("HX-Request") == "true":'.
868. Diese Zeile enthält den Code 'return render_image_section(request, db, recipe_id, current_user)'.
869. Diese Zeile enthält den Code 'return redirect(f"/recipes/{recipe_id}")'.
870. Diese Zeile ist leer und trennt Abschnitte.
871. Diese Zeile ist leer und trennt Abschnitte.
872. Diese Zeile enthält den Code '@router.post("/images/{image_id}/set-primary")'.
873. Diese Zeile enthält den Code 'def set_primary_image('.
874. Diese Zeile enthält den Code 'request: Request,'.
875. Diese Zeile enthält den Code 'image_id: int,'.
876. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
877. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
878. Diese Zeile enthält den Code '):'.
879. Diese Zeile enthält den Code 'image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id).options(joinedload(Recipe...'.
880. Diese Zeile enthält den Code 'if not image:'.
881. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))'.
882. Diese Zeile enthält den Code 'recipe = image.recipe'.
883. Diese Zeile enthält den Code 'if current_user.role != "admin":'.
884. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required"))'.
885. Diese Zeile enthält den Code 'set_recipe_primary_image(db, recipe, image.id)'.
886. Diese Zeile enthält den Code 'db.commit()'.
887. Diese Zeile enthält den Code 'if request.headers.get("HX-Request") == "true":'.
888. Diese Zeile enthält den Code 'return render_image_section(request, db, recipe.id, current_user)'.
889. Diese Zeile enthält den Code 'return redirect(f"/recipes/{recipe.id}")'.
890. Diese Zeile ist leer und trennt Abschnitte.
891. Diese Zeile ist leer und trennt Abschnitte.
892. Diese Zeile enthält den Code '@router.get("/recipes/{recipe_id}/pdf")'.
893. Diese Zeile enthält den Code 'def recipe_pdf('.
894. Diese Zeile enthält den Code 'recipe_id: int,'.
895. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
896. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
897. Diese Zeile enthält den Code '):'.
898. Diese Zeile enthält den Code 'recipe = fetch_recipe_or_404(db, recipe_id)'.
899. Diese Zeile enthält den Code 'ensure_recipe_visible(recipe, current_user)'.
900. Diese Zeile enthält den Code 'avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.recipe_id =...'.
901. Diese Zeile enthält den Code 'review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe_id)) or 0'.
902. Diese Zeile enthält den Code 'pdf_bytes = build_recipe_pdf(recipe, float(avg_rating), int(review_count))'.
903. Diese Zeile enthält den Code 'filename = f"mealmate_recipe_{recipe_id}.pdf"'.
904. Diese Zeile enthält den Code 'headers = {"Content-Disposition": f'attachment; filename="{filename}"'}'.
905. Diese Zeile enthält den Code 'return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)'.
906. Diese Zeile ist leer und trennt Abschnitte.
907. Diese Zeile ist leer und trennt Abschnitte.
908. Diese Zeile enthält den Code '@router.get("/categories")'.
909. Diese Zeile enthält den Code 'def categories_api(db: Session = Depends(get_db)):'.
910. Diese Zeile enthält den Code 'return {"categories": get_distinct_categories(db, only_published=True)}'.

## app/routers/admin.py

```python
import logging
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from fastapi.responses import Response as RawResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.config import get_settings
from app.csv_import import build_csv_example_bytes, build_csv_template_bytes, import_admin_csv
from app.database import get_db
from app.dependencies import get_admin_user, template_context
from app.i18n import t
from app.models import Recipe, RecipeImage, RecipeImageChangeFile, RecipeImageChangeRequest, User
from app.rate_limit import key_by_user_or_ip, limiter
from app.services import get_category_stats, import_kochwiki_csv, is_meta_true, set_meta_value
from app.views import redirect, templates

router = APIRouter(tags=["admin"])
settings = get_settings()
logger = logging.getLogger("mealmate.admin")
IMAGE_CHANGE_PAGE_SIZE = 20


def get_recipe_primary_image(recipe: Recipe) -> RecipeImage | None:
    for image in recipe.images:
        if image.is_primary:
            return image
    return recipe.images[0] if recipe.images else None


def get_recipe_external_image_url(recipe: Recipe) -> str | None:
    if recipe.source_image_url:
        return recipe.source_image_url
    if recipe.title_image_url:
        return recipe.title_image_url
    return None


def fetch_image_change_request_or_404(db: Session, request_id: int) -> RecipeImageChangeRequest:
    image_change_request = db.scalar(
        select(RecipeImageChangeRequest)
        .where(RecipeImageChangeRequest.id == request_id)
        .options(
            joinedload(RecipeImageChangeRequest.recipe).selectinload(Recipe.images),
            joinedload(RecipeImageChangeRequest.requester_user),
            joinedload(RecipeImageChangeRequest.reviewed_by_admin),
            selectinload(RecipeImageChangeRequest.files),
        )
    )
    if not image_change_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_change_request_not_found"))
    return image_change_request


def admin_dashboard_context(
    request: Request,
    db: Session,
    current_user: User,
    report=None,
    preview_report=None,
    error: str | None = None,
    message: str | None = None,
    import_mode: str = "insert_only",
    import_dry_run: bool = False,
    import_force_with_warnings: bool = False,
):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    recipes = db.scalars(
        select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.creator))
    ).all()
    pending_image_change_requests = db.scalars(
        select(RecipeImageChangeRequest)
        .where(RecipeImageChangeRequest.status == "pending")
        .order_by(RecipeImageChangeRequest.created_at.desc())
        .limit(8)
        .options(
            joinedload(RecipeImageChangeRequest.recipe),
            joinedload(RecipeImageChangeRequest.requester_user),
        )
    ).all()
    pending_image_change_count = db.scalar(
        select(func.count()).select_from(RecipeImageChangeRequest).where(RecipeImageChangeRequest.status == "pending")
    )
    pending_image_change_count = int(pending_image_change_count or 0)
    distinct_category_count, top_categories = get_category_stats(db, limit=10)
    logger.info(
        "category_stats distinct=%s top=%s",
        distinct_category_count,
        top_categories,
    )
    return template_context(
        request,
        current_user,
        users=users,
        recipes=recipes,
        report=report,
        preview_report=preview_report,
        error=error,
        message=message,
        import_mode=import_mode,
        import_dry_run=import_dry_run,
        import_force_with_warnings=import_force_with_warnings,
        distinct_category_count=distinct_category_count,
        top_categories=top_categories,
        pending_image_change_count=pending_image_change_count,
        pending_image_change_requests=pending_image_change_requests,
    )


@router.get("/admin")
def admin_panel(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return templates.TemplateResponse("admin.html", admin_dashboard_context(request, db, current_user))


@router.post("/admin/users/{user_id}/role")
def change_user_role(
    user_id: int,
    role: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    if role not in {"user", "admin"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.role_invalid"))
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.user_not_found"))
    user.role = role
    db.commit()
    return redirect("/admin")


@router.post("/admin/recipes/{recipe_id}/delete")
def delete_recipe_admin(
    recipe_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found"))
    db.delete(recipe)
    db.commit()
    return redirect("/admin")


@router.post("/admin/run-kochwiki-seed")
def run_kochwiki_seed(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    if not settings.enable_kochwiki_seed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.not_found"))
    if is_meta_true(db, "kochwiki_seed_done"):
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, error=t("error.seed_already_done")),
            status_code=status.HTTP_409_CONFLICT,
        )
    recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0
    if recipes_count > 0:
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=t("error.seed_not_empty"),
            ),
            status_code=status.HTTP_409_CONFLICT,
        )
    seed_path = Path(settings.kochwiki_csv_path)
    if not seed_path.exists():
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=f"{t('error.csv_not_found_prefix')}: {seed_path}",
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    report = import_kochwiki_csv(db, seed_path, current_user.id, mode="insert_only")
    if report.errors:
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                report=report,
                error=t("error.seed_finished_errors"),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    set_meta_value(db, "kochwiki_seed_done", "1")
    db.commit()
    return templates.TemplateResponse(
        "admin.html",
        admin_dashboard_context(
            request,
            db,
            current_user,
            report=report,
            message=t("error.seed_success"),
        ),
    )


@router.post("/admin/import-recipes")
@limiter.limit("2/minute", key_func=key_by_user_or_ip)
async def import_recipes_admin(
    request: Request,
    response: Response,
    file: UploadFile | None = File(None),
    insert_only: str | None = Form("on"),
    update_existing: str | None = Form(None),
    dry_run: str | None = Form(None),
    force_with_warnings: str | None = Form(None),
    action: str = Form("preview"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = response
    max_bytes = settings.max_csv_upload_mb * 1024 * 1024
    mode = "update_existing" if update_existing else "insert_only"
    dry_run_flag = bool(dry_run)
    force_warnings_flag = bool(force_with_warnings)
    if insert_only and mode != "update_existing":
        mode = "insert_only"
    try:
        if not file or not file.filename:
            raise ValueError(t("error.csv_upload_required"))
        if not file.filename.lower().endswith(".csv"):
            raise ValueError(t("error.csv_only"))
        raw_bytes = await file.read(max_bytes + 1)
        if len(raw_bytes) > max_bytes:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=t("error.csv_too_large"))
        if not raw_bytes:
            raise ValueError(t("error.csv_empty"))
        preview_report = import_admin_csv(
            db,
            raw_bytes,
            current_user.id,
            mode=mode,
            dry_run=True,
            autocommit=False,
        )
        if action == "preview":
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    message=t("admin.preview_done"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
            )
        if preview_report.fatal_error_rows > 0:
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    error=t("admin.import_blocked_errors"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        if dry_run_flag:
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    message=t("admin.dry_run_done"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
            )
        if preview_report.warnings and not force_warnings_flag:
            return templates.TemplateResponse(
                "admin.html",
                admin_dashboard_context(
                    request,
                    db,
                    current_user,
                    preview_report=preview_report,
                    error=t("admin.confirm_warnings_required"),
                    import_mode=mode,
                    import_dry_run=dry_run_flag,
                    import_force_with_warnings=force_warnings_flag,
                ),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        report = import_admin_csv(
            db,
            raw_bytes,
            current_user.id,
            mode=mode,
            dry_run=False,
            autocommit=False,
        )
        db.commit()
        message = t("error.import_finished_insert") if mode == "insert_only" else t("error.import_finished_update")
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                report=report,
                preview_report=report,
                message=message,
                import_mode=mode,
                import_dry_run=dry_run_flag,
                import_force_with_warnings=force_warnings_flag,
            ),
        )
    except (FileNotFoundError, ValueError) as exc:
        db.rollback()
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(
                request,
                db,
                current_user,
                error=str(exc),
                import_mode=mode,
                import_dry_run=dry_run_flag,
                import_force_with_warnings=force_warnings_flag,
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        db.rollback()
        raise


@router.get("/admin/import-template.csv")
def admin_import_template_csv(current_user: User = Depends(get_admin_user)):
    _ = current_user
    content = build_csv_template_bytes()
    headers = {"Content-Disposition": 'attachment; filename="mealmate_import_template.csv"'}
    return RawResponse(content=content, media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/admin/import-example.csv")
def admin_import_example_csv(current_user: User = Depends(get_admin_user)):
    _ = current_user
    content = build_csv_example_bytes()
    headers = {"Content-Disposition": 'attachment; filename="mealmate_import_beispiel.csv"'}
    return RawResponse(content=content, media_type="text/csv; charset=utf-8", headers=headers)


@router.get("/admin/image-change-requests")
def admin_image_change_requests(
    request: Request,
    status_filter: str = "pending",
    page: int = 1,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    page = max(page, 1)
    valid_statuses = {"pending", "approved", "rejected", "all"}
    if status_filter not in valid_statuses:
        status_filter = "pending"
    stmt = (
        select(RecipeImageChangeRequest)
        .order_by(RecipeImageChangeRequest.created_at.desc())
        .options(
            joinedload(RecipeImageChangeRequest.recipe),
            joinedload(RecipeImageChangeRequest.requester_user),
            joinedload(RecipeImageChangeRequest.reviewed_by_admin),
            selectinload(RecipeImageChangeRequest.files),
        )
    )
    count_stmt = select(func.count()).select_from(RecipeImageChangeRequest)
    if status_filter != "all":
        stmt = stmt.where(RecipeImageChangeRequest.status == status_filter)
        count_stmt = count_stmt.where(RecipeImageChangeRequest.status == status_filter)
    total_count = int(db.scalar(count_stmt) or 0)
    total_pages = max((total_count + IMAGE_CHANGE_PAGE_SIZE - 1) // IMAGE_CHANGE_PAGE_SIZE, 1)
    page = min(page, total_pages)
    requests = db.scalars(stmt.offset((page - 1) * IMAGE_CHANGE_PAGE_SIZE).limit(IMAGE_CHANGE_PAGE_SIZE)).all()
    status_rows = db.execute(
        select(RecipeImageChangeRequest.status, func.count(RecipeImageChangeRequest.id)).group_by(
            RecipeImageChangeRequest.status
        )
    ).all()
    status_stats = {"pending": 0, "approved": 0, "rejected": 0}
    for row_status, count in status_rows:
        status_stats[str(row_status)] = int(count)
    return templates.TemplateResponse(
        "admin_image_change_requests.html",
        template_context(
            request,
            current_user,
            image_change_requests=requests,
            status_filter=status_filter,
            page=page,
            total_pages=total_pages,
            total_count=total_count,
            status_stats=status_stats,
        ),
    )


@router.get("/admin/image-change-requests/{request_id}")
def admin_image_change_request_detail(
    request: Request,
    request_id: int,
    message: str = "",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    image_change_request = fetch_image_change_request_or_404(db, request_id)
    recipe = image_change_request.recipe
    recipe_primary_image = get_recipe_primary_image(recipe)
    current_image_url = f"/images/{recipe_primary_image.id}" if recipe_primary_image else get_recipe_external_image_url(recipe)
    current_image_kind = "db" if recipe_primary_image else ("external" if current_image_url else "placeholder")
    proposed_file = image_change_request.files[0] if image_change_request.files else None
    message_map = {
        "approved": t("image_change.approved", request=request),
        "rejected": t("image_change.rejected", request=request),
    }
    return templates.TemplateResponse(
        "admin_image_change_request_detail.html",
        template_context(
            request,
            current_user,
            image_change_request=image_change_request,
            recipe=recipe,
            current_image_url=current_image_url,
            current_image_kind=current_image_kind,
            proposed_file=proposed_file,
            message=message_map.get(message, ""),
        ),
    )


@router.post("/admin/image-change-requests/{request_id}/approve")
@limiter.limit("30/minute", key_func=key_by_user_or_ip)
def admin_image_change_request_approve(
    request: Request,
    request_id: int,
    admin_note: str = Form(""),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    image_change_request = fetch_image_change_request_or_404(db, request_id)
    if image_change_request.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t("error.image_change_request_not_pending"))
    proposed_file = image_change_request.files[0] if image_change_request.files else None
    if not proposed_file:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.image_change_file_missing"))
    recipe = image_change_request.recipe
    for image in recipe.images:
        image.is_primary = False
    db.add(
        RecipeImage(
            recipe_id=recipe.id,
            filename=proposed_file.filename,
            content_type=proposed_file.content_type,
            data=proposed_file.data,
            is_primary=True,
        )
    )
    image_change_request.status = "approved"
    image_change_request.admin_note = admin_note.strip() or None
    image_change_request.reviewed_by_admin_id = current_user.id
    image_change_request.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    _ = request
    return redirect(f"/admin/image-change-requests/{request_id}?message=approved")


@router.post("/admin/image-change-requests/{request_id}/reject")
@limiter.limit("30/minute", key_func=key_by_user_or_ip)
def admin_image_change_request_reject(
    request: Request,
    request_id: int,
    admin_note: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    image_change_request = fetch_image_change_request_or_404(db, request_id)
    if image_change_request.status != "pending":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t("error.image_change_request_not_pending"))
    if not admin_note.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.submission_reject_reason_required"))
    image_change_request.status = "rejected"
    image_change_request.admin_note = admin_note.strip()
    image_change_request.reviewed_by_admin_id = current_user.id
    image_change_request.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    _ = request
    return redirect(f"/admin/image-change-requests/{request_id}?message=rejected")


@router.get("/admin/image-change-files/{file_id}")
def admin_image_change_file_get(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = current_user
    image_change_file = db.scalar(
        select(RecipeImageChangeFile)
        .where(RecipeImageChangeFile.id == file_id)
        .options(joinedload(RecipeImageChangeFile.request))
    )
    if not image_change_file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))
    return RawResponse(content=image_change_file.data, media_type=image_change_file.content_type)

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'import logging'.
2. Diese Zeile enthält den Code 'from datetime import datetime, timezone'.
3. Diese Zeile enthält den Code 'from pathlib import Path'.
4. Diese Zeile ist leer und trennt Abschnitte.
5. Diese Zeile enthält den Code 'from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile,...'.
6. Diese Zeile enthält den Code 'from fastapi.responses import Response as RawResponse'.
7. Diese Zeile enthält den Code 'from sqlalchemy import func, select'.
8. Diese Zeile enthält den Code 'from sqlalchemy.orm import Session, joinedload, selectinload'.
9. Diese Zeile ist leer und trennt Abschnitte.
10. Diese Zeile enthält den Code 'from app.config import get_settings'.
11. Diese Zeile enthält den Code 'from app.csv_import import build_csv_example_bytes, build_csv_template_bytes, import_admin_csv'.
12. Diese Zeile enthält den Code 'from app.database import get_db'.
13. Diese Zeile enthält den Code 'from app.dependencies import get_admin_user, template_context'.
14. Diese Zeile enthält den Code 'from app.i18n import t'.
15. Diese Zeile enthält den Code 'from app.models import Recipe, RecipeImage, RecipeImageChangeFile, RecipeImageChangeRequest, User'.
16. Diese Zeile enthält den Code 'from app.rate_limit import key_by_user_or_ip, limiter'.
17. Diese Zeile enthält den Code 'from app.services import get_category_stats, import_kochwiki_csv, is_meta_true, set_meta_value'.
18. Diese Zeile enthält den Code 'from app.views import redirect, templates'.
19. Diese Zeile ist leer und trennt Abschnitte.
20. Diese Zeile enthält den Code 'router = APIRouter(tags=["admin"])'.
21. Diese Zeile enthält den Code 'settings = get_settings()'.
22. Diese Zeile enthält den Code 'logger = logging.getLogger("mealmate.admin")'.
23. Diese Zeile enthält den Code 'IMAGE_CHANGE_PAGE_SIZE = 20'.
24. Diese Zeile ist leer und trennt Abschnitte.
25. Diese Zeile ist leer und trennt Abschnitte.
26. Diese Zeile enthält den Code 'def get_recipe_primary_image(recipe: Recipe) -> RecipeImage | None:'.
27. Diese Zeile enthält den Code 'for image in recipe.images:'.
28. Diese Zeile enthält den Code 'if image.is_primary:'.
29. Diese Zeile enthält den Code 'return image'.
30. Diese Zeile enthält den Code 'return recipe.images[0] if recipe.images else None'.
31. Diese Zeile ist leer und trennt Abschnitte.
32. Diese Zeile ist leer und trennt Abschnitte.
33. Diese Zeile enthält den Code 'def get_recipe_external_image_url(recipe: Recipe) -> str | None:'.
34. Diese Zeile enthält den Code 'if recipe.source_image_url:'.
35. Diese Zeile enthält den Code 'return recipe.source_image_url'.
36. Diese Zeile enthält den Code 'if recipe.title_image_url:'.
37. Diese Zeile enthält den Code 'return recipe.title_image_url'.
38. Diese Zeile enthält den Code 'return None'.
39. Diese Zeile ist leer und trennt Abschnitte.
40. Diese Zeile ist leer und trennt Abschnitte.
41. Diese Zeile enthält den Code 'def fetch_image_change_request_or_404(db: Session, request_id: int) -> RecipeImageChangeRequest:'.
42. Diese Zeile enthält den Code 'image_change_request = db.scalar('.
43. Diese Zeile enthält den Code 'select(RecipeImageChangeRequest)'.
44. Diese Zeile enthält den Code '.where(RecipeImageChangeRequest.id == request_id)'.
45. Diese Zeile enthält den Code '.options('.
46. Diese Zeile enthält den Code 'joinedload(RecipeImageChangeRequest.recipe).selectinload(Recipe.images),'.
47. Diese Zeile enthält den Code 'joinedload(RecipeImageChangeRequest.requester_user),'.
48. Diese Zeile enthält den Code 'joinedload(RecipeImageChangeRequest.reviewed_by_admin),'.
49. Diese Zeile enthält den Code 'selectinload(RecipeImageChangeRequest.files),'.
50. Diese Zeile enthält den Code ')'.
51. Diese Zeile enthält den Code ')'.
52. Diese Zeile enthält den Code 'if not image_change_request:'.
53. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_change_request_n...'.
54. Diese Zeile enthält den Code 'return image_change_request'.
55. Diese Zeile ist leer und trennt Abschnitte.
56. Diese Zeile ist leer und trennt Abschnitte.
57. Diese Zeile enthält den Code 'def admin_dashboard_context('.
58. Diese Zeile enthält den Code 'request: Request,'.
59. Diese Zeile enthält den Code 'db: Session,'.
60. Diese Zeile enthält den Code 'current_user: User,'.
61. Diese Zeile enthält den Code 'report=None,'.
62. Diese Zeile enthält den Code 'preview_report=None,'.
63. Diese Zeile enthält den Code 'error: str | None = None,'.
64. Diese Zeile enthält den Code 'message: str | None = None,'.
65. Diese Zeile enthält den Code 'import_mode: str = "insert_only",'.
66. Diese Zeile enthält den Code 'import_dry_run: bool = False,'.
67. Diese Zeile enthält den Code 'import_force_with_warnings: bool = False,'.
68. Diese Zeile enthält den Code '):'.
69. Diese Zeile enthält den Code 'users = db.scalars(select(User).order_by(User.created_at.desc())).all()'.
70. Diese Zeile enthält den Code 'recipes = db.scalars('.
71. Diese Zeile enthält den Code 'select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.creator))'.
72. Diese Zeile enthält den Code ').all()'.
73. Diese Zeile enthält den Code 'pending_image_change_requests = db.scalars('.
74. Diese Zeile enthält den Code 'select(RecipeImageChangeRequest)'.
75. Diese Zeile enthält den Code '.where(RecipeImageChangeRequest.status == "pending")'.
76. Diese Zeile enthält den Code '.order_by(RecipeImageChangeRequest.created_at.desc())'.
77. Diese Zeile enthält den Code '.limit(8)'.
78. Diese Zeile enthält den Code '.options('.
79. Diese Zeile enthält den Code 'joinedload(RecipeImageChangeRequest.recipe),'.
80. Diese Zeile enthält den Code 'joinedload(RecipeImageChangeRequest.requester_user),'.
81. Diese Zeile enthält den Code ')'.
82. Diese Zeile enthält den Code ').all()'.
83. Diese Zeile enthält den Code 'pending_image_change_count = db.scalar('.
84. Diese Zeile enthält den Code 'select(func.count()).select_from(RecipeImageChangeRequest).where(RecipeImageChangeRequest.status ...'.
85. Diese Zeile enthält den Code ')'.
86. Diese Zeile enthält den Code 'pending_image_change_count = int(pending_image_change_count or 0)'.
87. Diese Zeile enthält den Code 'distinct_category_count, top_categories = get_category_stats(db, limit=10)'.
88. Diese Zeile enthält den Code 'logger.info('.
89. Diese Zeile enthält den Code '"category_stats distinct=%s top=%s",'.
90. Diese Zeile enthält den Code 'distinct_category_count,'.
91. Diese Zeile enthält den Code 'top_categories,'.
92. Diese Zeile enthält den Code ')'.
93. Diese Zeile enthält den Code 'return template_context('.
94. Diese Zeile enthält den Code 'request,'.
95. Diese Zeile enthält den Code 'current_user,'.
96. Diese Zeile enthält den Code 'users=users,'.
97. Diese Zeile enthält den Code 'recipes=recipes,'.
98. Diese Zeile enthält den Code 'report=report,'.
99. Diese Zeile enthält den Code 'preview_report=preview_report,'.
100. Diese Zeile enthält den Code 'error=error,'.
101. Diese Zeile enthält den Code 'message=message,'.
102. Diese Zeile enthält den Code 'import_mode=import_mode,'.
103. Diese Zeile enthält den Code 'import_dry_run=import_dry_run,'.
104. Diese Zeile enthält den Code 'import_force_with_warnings=import_force_with_warnings,'.
105. Diese Zeile enthält den Code 'distinct_category_count=distinct_category_count,'.
106. Diese Zeile enthält den Code 'top_categories=top_categories,'.
107. Diese Zeile enthält den Code 'pending_image_change_count=pending_image_change_count,'.
108. Diese Zeile enthält den Code 'pending_image_change_requests=pending_image_change_requests,'.
109. Diese Zeile enthält den Code ')'.
110. Diese Zeile ist leer und trennt Abschnitte.
111. Diese Zeile ist leer und trennt Abschnitte.
112. Diese Zeile enthält den Code '@router.get("/admin")'.
113. Diese Zeile enthält den Code 'def admin_panel('.
114. Diese Zeile enthält den Code 'request: Request,'.
115. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
116. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
117. Diese Zeile enthält den Code '):'.
118. Diese Zeile enthält den Code 'return templates.TemplateResponse("admin.html", admin_dashboard_context(request, db, current_user))'.
119. Diese Zeile ist leer und trennt Abschnitte.
120. Diese Zeile ist leer und trennt Abschnitte.
121. Diese Zeile enthält den Code '@router.post("/admin/users/{user_id}/role")'.
122. Diese Zeile enthält den Code 'def change_user_role('.
123. Diese Zeile enthält den Code 'user_id: int,'.
124. Diese Zeile enthält den Code 'role: str = Form(...),'.
125. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
126. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
127. Diese Zeile enthält den Code '):'.
128. Diese Zeile enthält den Code 'if role not in {"user", "admin"}:'.
129. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.role_invalid"))'.
130. Diese Zeile enthält den Code 'user = db.scalar(select(User).where(User.id == user_id))'.
131. Diese Zeile enthält den Code 'if not user:'.
132. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.user_not_found"))'.
133. Diese Zeile enthält den Code 'user.role = role'.
134. Diese Zeile enthält den Code 'db.commit()'.
135. Diese Zeile enthält den Code 'return redirect("/admin")'.
136. Diese Zeile ist leer und trennt Abschnitte.
137. Diese Zeile ist leer und trennt Abschnitte.
138. Diese Zeile enthält den Code '@router.post("/admin/recipes/{recipe_id}/delete")'.
139. Diese Zeile enthält den Code 'def delete_recipe_admin('.
140. Diese Zeile enthält den Code 'recipe_id: int,'.
141. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
142. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
143. Diese Zeile enthält den Code '):'.
144. Diese Zeile enthält den Code 'recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))'.
145. Diese Zeile enthält den Code 'if not recipe:'.
146. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.recipe_not_found"))'.
147. Diese Zeile enthält den Code 'db.delete(recipe)'.
148. Diese Zeile enthält den Code 'db.commit()'.
149. Diese Zeile enthält den Code 'return redirect("/admin")'.
150. Diese Zeile ist leer und trennt Abschnitte.
151. Diese Zeile ist leer und trennt Abschnitte.
152. Diese Zeile enthält den Code '@router.post("/admin/run-kochwiki-seed")'.
153. Diese Zeile enthält den Code 'def run_kochwiki_seed('.
154. Diese Zeile enthält den Code 'request: Request,'.
155. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
156. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
157. Diese Zeile enthält den Code '):'.
158. Diese Zeile enthält den Code 'if not settings.enable_kochwiki_seed:'.
159. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.not_found"))'.
160. Diese Zeile enthält den Code 'if is_meta_true(db, "kochwiki_seed_done"):'.
161. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
162. Diese Zeile enthält den Code '"admin.html",'.
163. Diese Zeile enthält den Code 'admin_dashboard_context(request, db, current_user, error=t("error.seed_already_done")),'.
164. Diese Zeile enthält den Code 'status_code=status.HTTP_409_CONFLICT,'.
165. Diese Zeile enthält den Code ')'.
166. Diese Zeile enthält den Code 'recipes_count = db.scalar(select(func.count()).select_from(Recipe)) or 0'.
167. Diese Zeile enthält den Code 'if recipes_count > 0:'.
168. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
169. Diese Zeile enthält den Code '"admin.html",'.
170. Diese Zeile enthält den Code 'admin_dashboard_context('.
171. Diese Zeile enthält den Code 'request,'.
172. Diese Zeile enthält den Code 'db,'.
173. Diese Zeile enthält den Code 'current_user,'.
174. Diese Zeile enthält den Code 'error=t("error.seed_not_empty"),'.
175. Diese Zeile enthält den Code '),'.
176. Diese Zeile enthält den Code 'status_code=status.HTTP_409_CONFLICT,'.
177. Diese Zeile enthält den Code ')'.
178. Diese Zeile enthält den Code 'seed_path = Path(settings.kochwiki_csv_path)'.
179. Diese Zeile enthält den Code 'if not seed_path.exists():'.
180. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
181. Diese Zeile enthält den Code '"admin.html",'.
182. Diese Zeile enthält den Code 'admin_dashboard_context('.
183. Diese Zeile enthält den Code 'request,'.
184. Diese Zeile enthält den Code 'db,'.
185. Diese Zeile enthält den Code 'current_user,'.
186. Diese Zeile enthält den Code 'error=f"{t('error.csv_not_found_prefix')}: {seed_path}",'.
187. Diese Zeile enthält den Code '),'.
188. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
189. Diese Zeile enthält den Code ')'.
190. Diese Zeile enthält den Code 'report = import_kochwiki_csv(db, seed_path, current_user.id, mode="insert_only")'.
191. Diese Zeile enthält den Code 'if report.errors:'.
192. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
193. Diese Zeile enthält den Code '"admin.html",'.
194. Diese Zeile enthält den Code 'admin_dashboard_context('.
195. Diese Zeile enthält den Code 'request,'.
196. Diese Zeile enthält den Code 'db,'.
197. Diese Zeile enthält den Code 'current_user,'.
198. Diese Zeile enthält den Code 'report=report,'.
199. Diese Zeile enthält den Code 'error=t("error.seed_finished_errors"),'.
200. Diese Zeile enthält den Code '),'.
201. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
202. Diese Zeile enthält den Code ')'.
203. Diese Zeile enthält den Code 'set_meta_value(db, "kochwiki_seed_done", "1")'.
204. Diese Zeile enthält den Code 'db.commit()'.
205. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
206. Diese Zeile enthält den Code '"admin.html",'.
207. Diese Zeile enthält den Code 'admin_dashboard_context('.
208. Diese Zeile enthält den Code 'request,'.
209. Diese Zeile enthält den Code 'db,'.
210. Diese Zeile enthält den Code 'current_user,'.
211. Diese Zeile enthält den Code 'report=report,'.
212. Diese Zeile enthält den Code 'message=t("error.seed_success"),'.
213. Diese Zeile enthält den Code '),'.
214. Diese Zeile enthält den Code ')'.
215. Diese Zeile ist leer und trennt Abschnitte.
216. Diese Zeile ist leer und trennt Abschnitte.
217. Diese Zeile enthält den Code '@router.post("/admin/import-recipes")'.
218. Diese Zeile enthält den Code '@limiter.limit("2/minute", key_func=key_by_user_or_ip)'.
219. Diese Zeile enthält den Code 'async def import_recipes_admin('.
220. Diese Zeile enthält den Code 'request: Request,'.
221. Diese Zeile enthält den Code 'response: Response,'.
222. Diese Zeile enthält den Code 'file: UploadFile | None = File(None),'.
223. Diese Zeile enthält den Code 'insert_only: str | None = Form("on"),'.
224. Diese Zeile enthält den Code 'update_existing: str | None = Form(None),'.
225. Diese Zeile enthält den Code 'dry_run: str | None = Form(None),'.
226. Diese Zeile enthält den Code 'force_with_warnings: str | None = Form(None),'.
227. Diese Zeile enthält den Code 'action: str = Form("preview"),'.
228. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
229. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
230. Diese Zeile enthält den Code '):'.
231. Diese Zeile enthält den Code '_ = response'.
232. Diese Zeile enthält den Code 'max_bytes = settings.max_csv_upload_mb * 1024 * 1024'.
233. Diese Zeile enthält den Code 'mode = "update_existing" if update_existing else "insert_only"'.
234. Diese Zeile enthält den Code 'dry_run_flag = bool(dry_run)'.
235. Diese Zeile enthält den Code 'force_warnings_flag = bool(force_with_warnings)'.
236. Diese Zeile enthält den Code 'if insert_only and mode != "update_existing":'.
237. Diese Zeile enthält den Code 'mode = "insert_only"'.
238. Diese Zeile enthält den Code 'try:'.
239. Diese Zeile enthält den Code 'if not file or not file.filename:'.
240. Diese Zeile enthält den Code 'raise ValueError(t("error.csv_upload_required"))'.
241. Diese Zeile enthält den Code 'if not file.filename.lower().endswith(".csv"):'.
242. Diese Zeile enthält den Code 'raise ValueError(t("error.csv_only"))'.
243. Diese Zeile enthält den Code 'raw_bytes = await file.read(max_bytes + 1)'.
244. Diese Zeile enthält den Code 'if len(raw_bytes) > max_bytes:'.
245. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=t("error.csv_too...'.
246. Diese Zeile enthält den Code 'if not raw_bytes:'.
247. Diese Zeile enthält den Code 'raise ValueError(t("error.csv_empty"))'.
248. Diese Zeile enthält den Code 'preview_report = import_admin_csv('.
249. Diese Zeile enthält den Code 'db,'.
250. Diese Zeile enthält den Code 'raw_bytes,'.
251. Diese Zeile enthält den Code 'current_user.id,'.
252. Diese Zeile enthält den Code 'mode=mode,'.
253. Diese Zeile enthält den Code 'dry_run=True,'.
254. Diese Zeile enthält den Code 'autocommit=False,'.
255. Diese Zeile enthält den Code ')'.
256. Diese Zeile enthält den Code 'if action == "preview":'.
257. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
258. Diese Zeile enthält den Code '"admin.html",'.
259. Diese Zeile enthält den Code 'admin_dashboard_context('.
260. Diese Zeile enthält den Code 'request,'.
261. Diese Zeile enthält den Code 'db,'.
262. Diese Zeile enthält den Code 'current_user,'.
263. Diese Zeile enthält den Code 'preview_report=preview_report,'.
264. Diese Zeile enthält den Code 'message=t("admin.preview_done"),'.
265. Diese Zeile enthält den Code 'import_mode=mode,'.
266. Diese Zeile enthält den Code 'import_dry_run=dry_run_flag,'.
267. Diese Zeile enthält den Code 'import_force_with_warnings=force_warnings_flag,'.
268. Diese Zeile enthält den Code '),'.
269. Diese Zeile enthält den Code ')'.
270. Diese Zeile enthält den Code 'if preview_report.fatal_error_rows > 0:'.
271. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
272. Diese Zeile enthält den Code '"admin.html",'.
273. Diese Zeile enthält den Code 'admin_dashboard_context('.
274. Diese Zeile enthält den Code 'request,'.
275. Diese Zeile enthält den Code 'db,'.
276. Diese Zeile enthält den Code 'current_user,'.
277. Diese Zeile enthält den Code 'preview_report=preview_report,'.
278. Diese Zeile enthält den Code 'error=t("admin.import_blocked_errors"),'.
279. Diese Zeile enthält den Code 'import_mode=mode,'.
280. Diese Zeile enthält den Code 'import_dry_run=dry_run_flag,'.
281. Diese Zeile enthält den Code 'import_force_with_warnings=force_warnings_flag,'.
282. Diese Zeile enthält den Code '),'.
283. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
284. Diese Zeile enthält den Code ')'.
285. Diese Zeile enthält den Code 'if dry_run_flag:'.
286. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
287. Diese Zeile enthält den Code '"admin.html",'.
288. Diese Zeile enthält den Code 'admin_dashboard_context('.
289. Diese Zeile enthält den Code 'request,'.
290. Diese Zeile enthält den Code 'db,'.
291. Diese Zeile enthält den Code 'current_user,'.
292. Diese Zeile enthält den Code 'preview_report=preview_report,'.
293. Diese Zeile enthält den Code 'message=t("admin.dry_run_done"),'.
294. Diese Zeile enthält den Code 'import_mode=mode,'.
295. Diese Zeile enthält den Code 'import_dry_run=dry_run_flag,'.
296. Diese Zeile enthält den Code 'import_force_with_warnings=force_warnings_flag,'.
297. Diese Zeile enthält den Code '),'.
298. Diese Zeile enthält den Code ')'.
299. Diese Zeile enthält den Code 'if preview_report.warnings and not force_warnings_flag:'.
300. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
301. Diese Zeile enthält den Code '"admin.html",'.
302. Diese Zeile enthält den Code 'admin_dashboard_context('.
303. Diese Zeile enthält den Code 'request,'.
304. Diese Zeile enthält den Code 'db,'.
305. Diese Zeile enthält den Code 'current_user,'.
306. Diese Zeile enthält den Code 'preview_report=preview_report,'.
307. Diese Zeile enthält den Code 'error=t("admin.confirm_warnings_required"),'.
308. Diese Zeile enthält den Code 'import_mode=mode,'.
309. Diese Zeile enthält den Code 'import_dry_run=dry_run_flag,'.
310. Diese Zeile enthält den Code 'import_force_with_warnings=force_warnings_flag,'.
311. Diese Zeile enthält den Code '),'.
312. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
313. Diese Zeile enthält den Code ')'.
314. Diese Zeile enthält den Code 'report = import_admin_csv('.
315. Diese Zeile enthält den Code 'db,'.
316. Diese Zeile enthält den Code 'raw_bytes,'.
317. Diese Zeile enthält den Code 'current_user.id,'.
318. Diese Zeile enthält den Code 'mode=mode,'.
319. Diese Zeile enthält den Code 'dry_run=False,'.
320. Diese Zeile enthält den Code 'autocommit=False,'.
321. Diese Zeile enthält den Code ')'.
322. Diese Zeile enthält den Code 'db.commit()'.
323. Diese Zeile enthält den Code 'message = t("error.import_finished_insert") if mode == "insert_only" else t("error.import_finishe...'.
324. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
325. Diese Zeile enthält den Code '"admin.html",'.
326. Diese Zeile enthält den Code 'admin_dashboard_context('.
327. Diese Zeile enthält den Code 'request,'.
328. Diese Zeile enthält den Code 'db,'.
329. Diese Zeile enthält den Code 'current_user,'.
330. Diese Zeile enthält den Code 'report=report,'.
331. Diese Zeile enthält den Code 'preview_report=report,'.
332. Diese Zeile enthält den Code 'message=message,'.
333. Diese Zeile enthält den Code 'import_mode=mode,'.
334. Diese Zeile enthält den Code 'import_dry_run=dry_run_flag,'.
335. Diese Zeile enthält den Code 'import_force_with_warnings=force_warnings_flag,'.
336. Diese Zeile enthält den Code '),'.
337. Diese Zeile enthält den Code ')'.
338. Diese Zeile enthält den Code 'except (FileNotFoundError, ValueError) as exc:'.
339. Diese Zeile enthält den Code 'db.rollback()'.
340. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
341. Diese Zeile enthält den Code '"admin.html",'.
342. Diese Zeile enthält den Code 'admin_dashboard_context('.
343. Diese Zeile enthält den Code 'request,'.
344. Diese Zeile enthält den Code 'db,'.
345. Diese Zeile enthält den Code 'current_user,'.
346. Diese Zeile enthält den Code 'error=str(exc),'.
347. Diese Zeile enthält den Code 'import_mode=mode,'.
348. Diese Zeile enthält den Code 'import_dry_run=dry_run_flag,'.
349. Diese Zeile enthält den Code 'import_force_with_warnings=force_warnings_flag,'.
350. Diese Zeile enthält den Code '),'.
351. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
352. Diese Zeile enthält den Code ')'.
353. Diese Zeile enthält den Code 'except Exception:'.
354. Diese Zeile enthält den Code 'db.rollback()'.
355. Diese Zeile enthält den Code 'raise'.
356. Diese Zeile ist leer und trennt Abschnitte.
357. Diese Zeile ist leer und trennt Abschnitte.
358. Diese Zeile enthält den Code '@router.get("/admin/import-template.csv")'.
359. Diese Zeile enthält den Code 'def admin_import_template_csv(current_user: User = Depends(get_admin_user)):'.
360. Diese Zeile enthält den Code '_ = current_user'.
361. Diese Zeile enthält den Code 'content = build_csv_template_bytes()'.
362. Diese Zeile enthält den Code 'headers = {"Content-Disposition": 'attachment; filename="mealmate_import_template.csv"'}'.
363. Diese Zeile enthält den Code 'return RawResponse(content=content, media_type="text/csv; charset=utf-8", headers=headers)'.
364. Diese Zeile ist leer und trennt Abschnitte.
365. Diese Zeile ist leer und trennt Abschnitte.
366. Diese Zeile enthält den Code '@router.get("/admin/import-example.csv")'.
367. Diese Zeile enthält den Code 'def admin_import_example_csv(current_user: User = Depends(get_admin_user)):'.
368. Diese Zeile enthält den Code '_ = current_user'.
369. Diese Zeile enthält den Code 'content = build_csv_example_bytes()'.
370. Diese Zeile enthält den Code 'headers = {"Content-Disposition": 'attachment; filename="mealmate_import_beispiel.csv"'}'.
371. Diese Zeile enthält den Code 'return RawResponse(content=content, media_type="text/csv; charset=utf-8", headers=headers)'.
372. Diese Zeile ist leer und trennt Abschnitte.
373. Diese Zeile ist leer und trennt Abschnitte.
374. Diese Zeile enthält den Code '@router.get("/admin/image-change-requests")'.
375. Diese Zeile enthält den Code 'def admin_image_change_requests('.
376. Diese Zeile enthält den Code 'request: Request,'.
377. Diese Zeile enthält den Code 'status_filter: str = "pending",'.
378. Diese Zeile enthält den Code 'page: int = 1,'.
379. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
380. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
381. Diese Zeile enthält den Code '):'.
382. Diese Zeile enthält den Code 'page = max(page, 1)'.
383. Diese Zeile enthält den Code 'valid_statuses = {"pending", "approved", "rejected", "all"}'.
384. Diese Zeile enthält den Code 'if status_filter not in valid_statuses:'.
385. Diese Zeile enthält den Code 'status_filter = "pending"'.
386. Diese Zeile enthält den Code 'stmt = ('.
387. Diese Zeile enthält den Code 'select(RecipeImageChangeRequest)'.
388. Diese Zeile enthält den Code '.order_by(RecipeImageChangeRequest.created_at.desc())'.
389. Diese Zeile enthält den Code '.options('.
390. Diese Zeile enthält den Code 'joinedload(RecipeImageChangeRequest.recipe),'.
391. Diese Zeile enthält den Code 'joinedload(RecipeImageChangeRequest.requester_user),'.
392. Diese Zeile enthält den Code 'joinedload(RecipeImageChangeRequest.reviewed_by_admin),'.
393. Diese Zeile enthält den Code 'selectinload(RecipeImageChangeRequest.files),'.
394. Diese Zeile enthält den Code ')'.
395. Diese Zeile enthält den Code ')'.
396. Diese Zeile enthält den Code 'count_stmt = select(func.count()).select_from(RecipeImageChangeRequest)'.
397. Diese Zeile enthält den Code 'if status_filter != "all":'.
398. Diese Zeile enthält den Code 'stmt = stmt.where(RecipeImageChangeRequest.status == status_filter)'.
399. Diese Zeile enthält den Code 'count_stmt = count_stmt.where(RecipeImageChangeRequest.status == status_filter)'.
400. Diese Zeile enthält den Code 'total_count = int(db.scalar(count_stmt) or 0)'.
401. Diese Zeile enthält den Code 'total_pages = max((total_count + IMAGE_CHANGE_PAGE_SIZE - 1) // IMAGE_CHANGE_PAGE_SIZE, 1)'.
402. Diese Zeile enthält den Code 'page = min(page, total_pages)'.
403. Diese Zeile enthält den Code 'requests = db.scalars(stmt.offset((page - 1) * IMAGE_CHANGE_PAGE_SIZE).limit(IMAGE_CHANGE_PAGE_SI...'.
404. Diese Zeile enthält den Code 'status_rows = db.execute('.
405. Diese Zeile enthält den Code 'select(RecipeImageChangeRequest.status, func.count(RecipeImageChangeRequest.id)).group_by('.
406. Diese Zeile enthält den Code 'RecipeImageChangeRequest.status'.
407. Diese Zeile enthält den Code ')'.
408. Diese Zeile enthält den Code ').all()'.
409. Diese Zeile enthält den Code 'status_stats = {"pending": 0, "approved": 0, "rejected": 0}'.
410. Diese Zeile enthält den Code 'for row_status, count in status_rows:'.
411. Diese Zeile enthält den Code 'status_stats[str(row_status)] = int(count)'.
412. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
413. Diese Zeile enthält den Code '"admin_image_change_requests.html",'.
414. Diese Zeile enthält den Code 'template_context('.
415. Diese Zeile enthält den Code 'request,'.
416. Diese Zeile enthält den Code 'current_user,'.
417. Diese Zeile enthält den Code 'image_change_requests=requests,'.
418. Diese Zeile enthält den Code 'status_filter=status_filter,'.
419. Diese Zeile enthält den Code 'page=page,'.
420. Diese Zeile enthält den Code 'total_pages=total_pages,'.
421. Diese Zeile enthält den Code 'total_count=total_count,'.
422. Diese Zeile enthält den Code 'status_stats=status_stats,'.
423. Diese Zeile enthält den Code '),'.
424. Diese Zeile enthält den Code ')'.
425. Diese Zeile ist leer und trennt Abschnitte.
426. Diese Zeile ist leer und trennt Abschnitte.
427. Diese Zeile enthält den Code '@router.get("/admin/image-change-requests/{request_id}")'.
428. Diese Zeile enthält den Code 'def admin_image_change_request_detail('.
429. Diese Zeile enthält den Code 'request: Request,'.
430. Diese Zeile enthält den Code 'request_id: int,'.
431. Diese Zeile enthält den Code 'message: str = "",'.
432. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
433. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
434. Diese Zeile enthält den Code '):'.
435. Diese Zeile enthält den Code 'image_change_request = fetch_image_change_request_or_404(db, request_id)'.
436. Diese Zeile enthält den Code 'recipe = image_change_request.recipe'.
437. Diese Zeile enthält den Code 'recipe_primary_image = get_recipe_primary_image(recipe)'.
438. Diese Zeile enthält den Code 'current_image_url = f"/images/{recipe_primary_image.id}" if recipe_primary_image else get_recipe_...'.
439. Diese Zeile enthält den Code 'current_image_kind = "db" if recipe_primary_image else ("external" if current_image_url else "pla...'.
440. Diese Zeile enthält den Code 'proposed_file = image_change_request.files[0] if image_change_request.files else None'.
441. Diese Zeile enthält den Code 'message_map = {'.
442. Diese Zeile enthält den Code '"approved": t("image_change.approved", request=request),'.
443. Diese Zeile enthält den Code '"rejected": t("image_change.rejected", request=request),'.
444. Diese Zeile enthält den Code '}'.
445. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
446. Diese Zeile enthält den Code '"admin_image_change_request_detail.html",'.
447. Diese Zeile enthält den Code 'template_context('.
448. Diese Zeile enthält den Code 'request,'.
449. Diese Zeile enthält den Code 'current_user,'.
450. Diese Zeile enthält den Code 'image_change_request=image_change_request,'.
451. Diese Zeile enthält den Code 'recipe=recipe,'.
452. Diese Zeile enthält den Code 'current_image_url=current_image_url,'.
453. Diese Zeile enthält den Code 'current_image_kind=current_image_kind,'.
454. Diese Zeile enthält den Code 'proposed_file=proposed_file,'.
455. Diese Zeile enthält den Code 'message=message_map.get(message, ""),'.
456. Diese Zeile enthält den Code '),'.
457. Diese Zeile enthält den Code ')'.
458. Diese Zeile ist leer und trennt Abschnitte.
459. Diese Zeile ist leer und trennt Abschnitte.
460. Diese Zeile enthält den Code '@router.post("/admin/image-change-requests/{request_id}/approve")'.
461. Diese Zeile enthält den Code '@limiter.limit("30/minute", key_func=key_by_user_or_ip)'.
462. Diese Zeile enthält den Code 'def admin_image_change_request_approve('.
463. Diese Zeile enthält den Code 'request: Request,'.
464. Diese Zeile enthält den Code 'request_id: int,'.
465. Diese Zeile enthält den Code 'admin_note: str = Form(""),'.
466. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
467. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
468. Diese Zeile enthält den Code '):'.
469. Diese Zeile enthält den Code 'image_change_request = fetch_image_change_request_or_404(db, request_id)'.
470. Diese Zeile enthält den Code 'if image_change_request.status != "pending":'.
471. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t("error.image_change_request_no...'.
472. Diese Zeile enthält den Code 'proposed_file = image_change_request.files[0] if image_change_request.files else None'.
473. Diese Zeile enthält den Code 'if not proposed_file:'.
474. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.image_change_file_mi...'.
475. Diese Zeile enthält den Code 'recipe = image_change_request.recipe'.
476. Diese Zeile enthält den Code 'for image in recipe.images:'.
477. Diese Zeile enthält den Code 'image.is_primary = False'.
478. Diese Zeile enthält den Code 'db.add('.
479. Diese Zeile enthält den Code 'RecipeImage('.
480. Diese Zeile enthält den Code 'recipe_id=recipe.id,'.
481. Diese Zeile enthält den Code 'filename=proposed_file.filename,'.
482. Diese Zeile enthält den Code 'content_type=proposed_file.content_type,'.
483. Diese Zeile enthält den Code 'data=proposed_file.data,'.
484. Diese Zeile enthält den Code 'is_primary=True,'.
485. Diese Zeile enthält den Code ')'.
486. Diese Zeile enthält den Code ')'.
487. Diese Zeile enthält den Code 'image_change_request.status = "approved"'.
488. Diese Zeile enthält den Code 'image_change_request.admin_note = admin_note.strip() or None'.
489. Diese Zeile enthält den Code 'image_change_request.reviewed_by_admin_id = current_user.id'.
490. Diese Zeile enthält den Code 'image_change_request.reviewed_at = datetime.now(timezone.utc)'.
491. Diese Zeile enthält den Code 'db.commit()'.
492. Diese Zeile enthält den Code '_ = request'.
493. Diese Zeile enthält den Code 'return redirect(f"/admin/image-change-requests/{request_id}?message=approved")'.
494. Diese Zeile ist leer und trennt Abschnitte.
495. Diese Zeile ist leer und trennt Abschnitte.
496. Diese Zeile enthält den Code '@router.post("/admin/image-change-requests/{request_id}/reject")'.
497. Diese Zeile enthält den Code '@limiter.limit("30/minute", key_func=key_by_user_or_ip)'.
498. Diese Zeile enthält den Code 'def admin_image_change_request_reject('.
499. Diese Zeile enthält den Code 'request: Request,'.
500. Diese Zeile enthält den Code 'request_id: int,'.
501. Diese Zeile enthält den Code 'admin_note: str = Form(...),'.
502. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
503. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
504. Diese Zeile enthält den Code '):'.
505. Diese Zeile enthält den Code 'image_change_request = fetch_image_change_request_or_404(db, request_id)'.
506. Diese Zeile enthält den Code 'if image_change_request.status != "pending":'.
507. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=t("error.image_change_request_no...'.
508. Diese Zeile enthält den Code 'if not admin_note.strip():'.
509. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=t("error.submission_reject_re...'.
510. Diese Zeile enthält den Code 'image_change_request.status = "rejected"'.
511. Diese Zeile enthält den Code 'image_change_request.admin_note = admin_note.strip()'.
512. Diese Zeile enthält den Code 'image_change_request.reviewed_by_admin_id = current_user.id'.
513. Diese Zeile enthält den Code 'image_change_request.reviewed_at = datetime.now(timezone.utc)'.
514. Diese Zeile enthält den Code 'db.commit()'.
515. Diese Zeile enthält den Code '_ = request'.
516. Diese Zeile enthält den Code 'return redirect(f"/admin/image-change-requests/{request_id}?message=rejected")'.
517. Diese Zeile ist leer und trennt Abschnitte.
518. Diese Zeile ist leer und trennt Abschnitte.
519. Diese Zeile enthält den Code '@router.get("/admin/image-change-files/{file_id}")'.
520. Diese Zeile enthält den Code 'def admin_image_change_file_get('.
521. Diese Zeile enthält den Code 'file_id: int,'.
522. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
523. Diese Zeile enthält den Code 'current_user: User = Depends(get_admin_user),'.
524. Diese Zeile enthält den Code '):'.
525. Diese Zeile enthält den Code '_ = current_user'.
526. Diese Zeile enthält den Code 'image_change_file = db.scalar('.
527. Diese Zeile enthält den Code 'select(RecipeImageChangeFile)'.
528. Diese Zeile enthält den Code '.where(RecipeImageChangeFile.id == file_id)'.
529. Diese Zeile enthält den Code '.options(joinedload(RecipeImageChangeFile.request))'.
530. Diese Zeile enthält den Code ')'.
531. Diese Zeile enthält den Code 'if not image_change_file:'.
532. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=t("error.image_not_found"))'.
533. Diese Zeile enthält den Code 'return RawResponse(content=image_change_file.data, media_type=image_change_file.content_type)'.

## app/templates/admin.html

```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("admin.title") }}</h1>
  {% if message %}
  <p class="meta">{{ message }}</p>
  {% endif %}
  {% if error %}
  <p class="error">{{ error }}</p>
  {% endif %}
  <p><a href="/admin/submissions">{{ t("submission.admin_queue_link") }}</a></p>
</section>
<section class="panel">
  <h2>{{ t("image_change.admin_title") }}</h2>
  <p class="meta">{{ t("image_change.pending_count", count=pending_image_change_count) }}</p>
  <p><a href="/admin/image-change-requests">{{ t("image_change.open_queue") }}</a></p>
  {% if pending_image_change_requests %}
  <table>
    <thead>
      <tr>
        <th>{{ t("submission.table_date") }}</th>
        <th>{{ t("submission.table_title") }}</th>
        <th>{{ t("submission.table_submitter") }}</th>
        <th>{{ t("submission.table_action") }}</th>
      </tr>
    </thead>
    <tbody>
      {% for item in pending_image_change_requests %}
      <tr>
        <td>{{ item.created_at|datetime_de }}</td>
        <td><a href="/recipes/{{ item.recipe.id }}">{{ item.recipe.title }}</a></td>
        <td>{{ item.requester_user.email if item.requester_user else "-" }}</td>
        <td><a href="/admin/image-change-requests/{{ item.id }}">{{ t("submission.open_detail") }}</a></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% else %}
  <p>{{ t("image_change.admin_empty") }}</p>
  {% endif %}
</section>
<section class="panel">
  <h2>{{ t("admin.import_title") }}</h2>
  <div class="stack">
    <h3>{{ t("admin.import_help_title") }}</h3>
    <p class="meta">{{ t("admin.import_help_intro") }}</p>
    <ul>
      <li>{{ t("admin.import_required_columns") }}</li>
      <li>{{ t("admin.import_optional_columns") }}</li>
      <li>{{ t("admin.import_difficulty_values") }}</li>
      <li>{{ t("admin.import_ingredients_example") }}</li>
      <li>{{ t("admin.import_encoding_delimiter") }}</li>
    </ul>
    <div class="actions">
      <a href="/admin/import-template.csv">{{ t("admin.download_template") }}</a>
      <a href="/admin/import-example.csv">{{ t("admin.download_example") }}</a>
    </div>
  </div>
  <form method="post" action="/admin/import-recipes" enctype="multipart/form-data" class="stack">
    <label>{{ t("admin.upload_label") }}
      <input type="file" name="file" accept=".csv" required>
    </label>
    <label class="inline">
      <input type="checkbox" name="insert_only" {% if import_mode == "insert_only" %}checked{% endif %}>
      {{ t("admin.insert_only") }}
    </label>
    <label class="inline">
      <input type="checkbox" name="update_existing" {% if import_mode == "update_existing" %}checked{% endif %}>
      {{ t("admin.update_existing") }}
    </label>
    <label class="inline">
      <input type="checkbox" name="dry_run" {% if import_dry_run %}checked{% endif %}>
      {{ t("admin.dry_run") }}
    </label>
    <label class="inline">
      <input type="checkbox" name="force_with_warnings" {% if import_force_with_warnings %}checked{% endif %}>
      {{ t("admin.force_with_warnings") }}
    </label>
    <p class="meta">{{ t("admin.import_warning_text") }}</p>
    <div class="actions">
      <button type="submit" name="action" value="preview">{{ t("admin.preview_button") }}</button>
      <button type="submit" name="action" value="import">{{ t("admin.start_import") }}</button>
    </div>
  </form>
  {% if preview_report %}
  <h3>{{ t("admin.preview_title") }}</h3>
  <p class="meta">
    {{ t("admin.preview_total_rows") }}: {{ preview_report.total_rows }},
    {{ t("admin.preview_delimiter") }}: {{ preview_report.delimiter }},
    {{ t("admin.preview_fatal_rows") }}: {{ preview_report.fatal_error_rows }}
  </p>
  <p class="meta">
    {{ t("admin.report_inserted") }}: {{ preview_report.inserted }},
    {{ t("admin.report_updated") }}: {{ preview_report.updated }},
    {{ t("admin.report_skipped") }}: {{ preview_report.skipped }},
    {{ t("admin.report_errors") }}: {{ preview_report.errors|length }},
    {{ t("admin.report_warnings") }}: {{ preview_report.warnings|length }}
  </p>
  <table>
    <thead>
      <tr>
        <th>{{ t("admin.preview_row") }}</th>
        <th>{{ t("admin.title_column") }}</th>
        <th>{{ t("home.category") }}</th>
        <th>{{ t("home.difficulty") }}</th>
        <th>{{ t("recipe_form.prep_time") }}</th>
        <th>{{ t("admin.preview_status") }}</th>
        <th>{{ t("admin.preview_notes") }}</th>
      </tr>
    </thead>
    <tbody>
      {% for row in preview_report.preview_rows %}
      <tr>
        <td>{{ row.row_number }}</td>
        <td>{{ row.title }}</td>
        <td>{{ row.category }}</td>
        <td>{{ difficulty_label(row.difficulty) }}</td>
        <td>{{ row.prep_time_minutes }}</td>
        <td>{{ row.status }}</td>
        <td>
          {% if row.errors %}
          {{ row.errors|join("; ") }}
          {% elif row.warnings %}
          {{ row.warnings|join("; ") }}
          {% else %}
          -
          {% endif %}
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% if preview_report.errors %}
  <h4>{{ t("admin.preview_errors_title") }}</h4>
  <ul>
    {% for item in preview_report.errors %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
  {% endif %}
  {% if preview_report.warnings %}
  <h4>{{ t("admin.preview_warnings_title") }}</h4>
  <ul>
    {% for item in preview_report.warnings %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
  {% endif %}
  {% endif %}
  {% if report %}
  <h3>{{ t("admin.import_result_title") }}</h3>
  <p class="meta">
    {{ t("admin.report_inserted") }}: {{ report.inserted }},
    {{ t("admin.report_updated") }}: {{ report.updated }},
    {{ t("admin.report_skipped") }}: {{ report.skipped }},
    {{ t("admin.report_errors") }}: {{ report.errors|length }},
    {{ t("admin.report_warnings") }}: {{ report.warnings|length }}
  </p>
  {% endif %}
</section>
<section class="panel">
  <h2>{{ t("admin.category_stats_title") }}</h2>
  <p class="meta">{{ t("admin.category_distinct_count") }}: {{ distinct_category_count }}</p>
  <h3>{{ t("admin.category_top") }}</h3>
  <ul>
    {% for category_name, category_count in top_categories %}
    <li>{{ category_name }} ({{ category_count }})</li>
    {% endfor %}
  </ul>
</section>
<section class="panel">
  <h2>{{ t("admin.users") }}</h2>
  <table>
    <thead>
      <tr><th>{{ t("admin.id") }}</th><th>{{ t("admin.email") }}</th><th>{{ t("admin.role") }}</th><th>{{ t("admin.action") }}</th></tr>
    </thead>
    <tbody>
      {% for user in users %}
      <tr>
        <td>{{ user.id }}</td>
        <td>{{ user.email }}</td>
        <td>{{ role_label(user.role) }}</td>
        <td>
          <form method="post" action="/admin/users/{{ user.id }}/role" class="inline">
            <select name="role">
              <option value="user" {% if user.role == "user" %}selected{% endif %}>{{ t("role.user") }}</option>
              <option value="admin" {% if user.role == "admin" %}selected{% endif %}>{{ t("role.admin") }}</option>
            </select>
            <button type="submit">{{ t("admin.save") }}</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
<section class="panel">
  <h2>{{ t("admin.recipes") }}</h2>
  <table>
    <thead>
      <tr><th>{{ t("admin.id") }}</th><th>{{ t("admin.title_column") }}</th><th>{{ t("admin.creator") }}</th><th>{{ t("admin.source") }}</th><th>{{ t("admin.action") }}</th></tr>
    </thead>
    <tbody>
      {% for recipe in recipes %}
      <tr>
        <td>{{ recipe.id }}</td>
        <td><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></td>
        <td>{{ recipe.creator.email }}</td>
        <td>{{ recipe.source }}</td>
        <td>
          <form method="post" action="/admin/recipes/{{ recipe.id }}/delete">
            <button type="submit">{{ t("recipe.delete") }}</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
{% endblock %}

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '{% extends "base.html" %}'.
2. Diese Zeile enthält den Code '{% block content %}'.
3. Diese Zeile enthält den Code '<section class="panel">'.
4. Diese Zeile enthält den Code '<h1>{{ t("admin.title") }}</h1>'.
5. Diese Zeile enthält den Code '{% if message %}'.
6. Diese Zeile enthält den Code '<p class="meta">{{ message }}</p>'.
7. Diese Zeile enthält den Code '{% endif %}'.
8. Diese Zeile enthält den Code '{% if error %}'.
9. Diese Zeile enthält den Code '<p class="error">{{ error }}</p>'.
10. Diese Zeile enthält den Code '{% endif %}'.
11. Diese Zeile enthält den Code '<p><a href="/admin/submissions">{{ t("submission.admin_queue_link") }}</a></p>'.
12. Diese Zeile enthält den Code '</section>'.
13. Diese Zeile enthält den Code '<section class="panel">'.
14. Diese Zeile enthält den Code '<h2>{{ t("image_change.admin_title") }}</h2>'.
15. Diese Zeile enthält den Code '<p class="meta">{{ t("image_change.pending_count", count=pending_image_change_count) }}</p>'.
16. Diese Zeile enthält den Code '<p><a href="/admin/image-change-requests">{{ t("image_change.open_queue") }}</a></p>'.
17. Diese Zeile enthält den Code '{% if pending_image_change_requests %}'.
18. Diese Zeile enthält den Code '<table>'.
19. Diese Zeile enthält den Code '<thead>'.
20. Diese Zeile enthält den Code '<tr>'.
21. Diese Zeile enthält den Code '<th>{{ t("submission.table_date") }}</th>'.
22. Diese Zeile enthält den Code '<th>{{ t("submission.table_title") }}</th>'.
23. Diese Zeile enthält den Code '<th>{{ t("submission.table_submitter") }}</th>'.
24. Diese Zeile enthält den Code '<th>{{ t("submission.table_action") }}</th>'.
25. Diese Zeile enthält den Code '</tr>'.
26. Diese Zeile enthält den Code '</thead>'.
27. Diese Zeile enthält den Code '<tbody>'.
28. Diese Zeile enthält den Code '{% for item in pending_image_change_requests %}'.
29. Diese Zeile enthält den Code '<tr>'.
30. Diese Zeile enthält den Code '<td>{{ item.created_at|datetime_de }}</td>'.
31. Diese Zeile enthält den Code '<td><a href="/recipes/{{ item.recipe.id }}">{{ item.recipe.title }}</a></td>'.
32. Diese Zeile enthält den Code '<td>{{ item.requester_user.email if item.requester_user else "-" }}</td>'.
33. Diese Zeile enthält den Code '<td><a href="/admin/image-change-requests/{{ item.id }}">{{ t("submission.open_detail") }}</a></td>'.
34. Diese Zeile enthält den Code '</tr>'.
35. Diese Zeile enthält den Code '{% endfor %}'.
36. Diese Zeile enthält den Code '</tbody>'.
37. Diese Zeile enthält den Code '</table>'.
38. Diese Zeile enthält den Code '{% else %}'.
39. Diese Zeile enthält den Code '<p>{{ t("image_change.admin_empty") }}</p>'.
40. Diese Zeile enthält den Code '{% endif %}'.
41. Diese Zeile enthält den Code '</section>'.
42. Diese Zeile enthält den Code '<section class="panel">'.
43. Diese Zeile enthält den Code '<h2>{{ t("admin.import_title") }}</h2>'.
44. Diese Zeile enthält den Code '<div class="stack">'.
45. Diese Zeile enthält den Code '<h3>{{ t("admin.import_help_title") }}</h3>'.
46. Diese Zeile enthält den Code '<p class="meta">{{ t("admin.import_help_intro") }}</p>'.
47. Diese Zeile enthält den Code '<ul>'.
48. Diese Zeile enthält den Code '<li>{{ t("admin.import_required_columns") }}</li>'.
49. Diese Zeile enthält den Code '<li>{{ t("admin.import_optional_columns") }}</li>'.
50. Diese Zeile enthält den Code '<li>{{ t("admin.import_difficulty_values") }}</li>'.
51. Diese Zeile enthält den Code '<li>{{ t("admin.import_ingredients_example") }}</li>'.
52. Diese Zeile enthält den Code '<li>{{ t("admin.import_encoding_delimiter") }}</li>'.
53. Diese Zeile enthält den Code '</ul>'.
54. Diese Zeile enthält den Code '<div class="actions">'.
55. Diese Zeile enthält den Code '<a href="/admin/import-template.csv">{{ t("admin.download_template") }}</a>'.
56. Diese Zeile enthält den Code '<a href="/admin/import-example.csv">{{ t("admin.download_example") }}</a>'.
57. Diese Zeile enthält den Code '</div>'.
58. Diese Zeile enthält den Code '</div>'.
59. Diese Zeile enthält den Code '<form method="post" action="/admin/import-recipes" enctype="multipart/form-data" class="stack">'.
60. Diese Zeile enthält den Code '<label>{{ t("admin.upload_label") }}'.
61. Diese Zeile enthält den Code '<input type="file" name="file" accept=".csv" required>'.
62. Diese Zeile enthält den Code '</label>'.
63. Diese Zeile enthält den Code '<label class="inline">'.
64. Diese Zeile enthält den Code '<input type="checkbox" name="insert_only" {% if import_mode == "insert_only" %}checked{% endif %}>'.
65. Diese Zeile enthält den Code '{{ t("admin.insert_only") }}'.
66. Diese Zeile enthält den Code '</label>'.
67. Diese Zeile enthält den Code '<label class="inline">'.
68. Diese Zeile enthält den Code '<input type="checkbox" name="update_existing" {% if import_mode == "update_existing" %}checked{% ...'.
69. Diese Zeile enthält den Code '{{ t("admin.update_existing") }}'.
70. Diese Zeile enthält den Code '</label>'.
71. Diese Zeile enthält den Code '<label class="inline">'.
72. Diese Zeile enthält den Code '<input type="checkbox" name="dry_run" {% if import_dry_run %}checked{% endif %}>'.
73. Diese Zeile enthält den Code '{{ t("admin.dry_run") }}'.
74. Diese Zeile enthält den Code '</label>'.
75. Diese Zeile enthält den Code '<label class="inline">'.
76. Diese Zeile enthält den Code '<input type="checkbox" name="force_with_warnings" {% if import_force_with_warnings %}checked{% en...'.
77. Diese Zeile enthält den Code '{{ t("admin.force_with_warnings") }}'.
78. Diese Zeile enthält den Code '</label>'.
79. Diese Zeile enthält den Code '<p class="meta">{{ t("admin.import_warning_text") }}</p>'.
80. Diese Zeile enthält den Code '<div class="actions">'.
81. Diese Zeile enthält den Code '<button type="submit" name="action" value="preview">{{ t("admin.preview_button") }}</button>'.
82. Diese Zeile enthält den Code '<button type="submit" name="action" value="import">{{ t("admin.start_import") }}</button>'.
83. Diese Zeile enthält den Code '</div>'.
84. Diese Zeile enthält den Code '</form>'.
85. Diese Zeile enthält den Code '{% if preview_report %}'.
86. Diese Zeile enthält den Code '<h3>{{ t("admin.preview_title") }}</h3>'.
87. Diese Zeile enthält den Code '<p class="meta">'.
88. Diese Zeile enthält den Code '{{ t("admin.preview_total_rows") }}: {{ preview_report.total_rows }},'.
89. Diese Zeile enthält den Code '{{ t("admin.preview_delimiter") }}: {{ preview_report.delimiter }},'.
90. Diese Zeile enthält den Code '{{ t("admin.preview_fatal_rows") }}: {{ preview_report.fatal_error_rows }}'.
91. Diese Zeile enthält den Code '</p>'.
92. Diese Zeile enthält den Code '<p class="meta">'.
93. Diese Zeile enthält den Code '{{ t("admin.report_inserted") }}: {{ preview_report.inserted }},'.
94. Diese Zeile enthält den Code '{{ t("admin.report_updated") }}: {{ preview_report.updated }},'.
95. Diese Zeile enthält den Code '{{ t("admin.report_skipped") }}: {{ preview_report.skipped }},'.
96. Diese Zeile enthält den Code '{{ t("admin.report_errors") }}: {{ preview_report.errors|length }},'.
97. Diese Zeile enthält den Code '{{ t("admin.report_warnings") }}: {{ preview_report.warnings|length }}'.
98. Diese Zeile enthält den Code '</p>'.
99. Diese Zeile enthält den Code '<table>'.
100. Diese Zeile enthält den Code '<thead>'.
101. Diese Zeile enthält den Code '<tr>'.
102. Diese Zeile enthält den Code '<th>{{ t("admin.preview_row") }}</th>'.
103. Diese Zeile enthält den Code '<th>{{ t("admin.title_column") }}</th>'.
104. Diese Zeile enthält den Code '<th>{{ t("home.category") }}</th>'.
105. Diese Zeile enthält den Code '<th>{{ t("home.difficulty") }}</th>'.
106. Diese Zeile enthält den Code '<th>{{ t("recipe_form.prep_time") }}</th>'.
107. Diese Zeile enthält den Code '<th>{{ t("admin.preview_status") }}</th>'.
108. Diese Zeile enthält den Code '<th>{{ t("admin.preview_notes") }}</th>'.
109. Diese Zeile enthält den Code '</tr>'.
110. Diese Zeile enthält den Code '</thead>'.
111. Diese Zeile enthält den Code '<tbody>'.
112. Diese Zeile enthält den Code '{% for row in preview_report.preview_rows %}'.
113. Diese Zeile enthält den Code '<tr>'.
114. Diese Zeile enthält den Code '<td>{{ row.row_number }}</td>'.
115. Diese Zeile enthält den Code '<td>{{ row.title }}</td>'.
116. Diese Zeile enthält den Code '<td>{{ row.category }}</td>'.
117. Diese Zeile enthält den Code '<td>{{ difficulty_label(row.difficulty) }}</td>'.
118. Diese Zeile enthält den Code '<td>{{ row.prep_time_minutes }}</td>'.
119. Diese Zeile enthält den Code '<td>{{ row.status }}</td>'.
120. Diese Zeile enthält den Code '<td>'.
121. Diese Zeile enthält den Code '{% if row.errors %}'.
122. Diese Zeile enthält den Code '{{ row.errors|join("; ") }}'.
123. Diese Zeile enthält den Code '{% elif row.warnings %}'.
124. Diese Zeile enthält den Code '{{ row.warnings|join("; ") }}'.
125. Diese Zeile enthält den Code '{% else %}'.
126. Diese Zeile enthält den Code '-'.
127. Diese Zeile enthält den Code '{% endif %}'.
128. Diese Zeile enthält den Code '</td>'.
129. Diese Zeile enthält den Code '</tr>'.
130. Diese Zeile enthält den Code '{% endfor %}'.
131. Diese Zeile enthält den Code '</tbody>'.
132. Diese Zeile enthält den Code '</table>'.
133. Diese Zeile enthält den Code '{% if preview_report.errors %}'.
134. Diese Zeile enthält den Code '<h4>{{ t("admin.preview_errors_title") }}</h4>'.
135. Diese Zeile enthält den Code '<ul>'.
136. Diese Zeile enthält den Code '{% for item in preview_report.errors %}'.
137. Diese Zeile enthält den Code '<li>{{ item }}</li>'.
138. Diese Zeile enthält den Code '{% endfor %}'.
139. Diese Zeile enthält den Code '</ul>'.
140. Diese Zeile enthält den Code '{% endif %}'.
141. Diese Zeile enthält den Code '{% if preview_report.warnings %}'.
142. Diese Zeile enthält den Code '<h4>{{ t("admin.preview_warnings_title") }}</h4>'.
143. Diese Zeile enthält den Code '<ul>'.
144. Diese Zeile enthält den Code '{% for item in preview_report.warnings %}'.
145. Diese Zeile enthält den Code '<li>{{ item }}</li>'.
146. Diese Zeile enthält den Code '{% endfor %}'.
147. Diese Zeile enthält den Code '</ul>'.
148. Diese Zeile enthält den Code '{% endif %}'.
149. Diese Zeile enthält den Code '{% endif %}'.
150. Diese Zeile enthält den Code '{% if report %}'.
151. Diese Zeile enthält den Code '<h3>{{ t("admin.import_result_title") }}</h3>'.
152. Diese Zeile enthält den Code '<p class="meta">'.
153. Diese Zeile enthält den Code '{{ t("admin.report_inserted") }}: {{ report.inserted }},'.
154. Diese Zeile enthält den Code '{{ t("admin.report_updated") }}: {{ report.updated }},'.
155. Diese Zeile enthält den Code '{{ t("admin.report_skipped") }}: {{ report.skipped }},'.
156. Diese Zeile enthält den Code '{{ t("admin.report_errors") }}: {{ report.errors|length }},'.
157. Diese Zeile enthält den Code '{{ t("admin.report_warnings") }}: {{ report.warnings|length }}'.
158. Diese Zeile enthält den Code '</p>'.
159. Diese Zeile enthält den Code '{% endif %}'.
160. Diese Zeile enthält den Code '</section>'.
161. Diese Zeile enthält den Code '<section class="panel">'.
162. Diese Zeile enthält den Code '<h2>{{ t("admin.category_stats_title") }}</h2>'.
163. Diese Zeile enthält den Code '<p class="meta">{{ t("admin.category_distinct_count") }}: {{ distinct_category_count }}</p>'.
164. Diese Zeile enthält den Code '<h3>{{ t("admin.category_top") }}</h3>'.
165. Diese Zeile enthält den Code '<ul>'.
166. Diese Zeile enthält den Code '{% for category_name, category_count in top_categories %}'.
167. Diese Zeile enthält den Code '<li>{{ category_name }} ({{ category_count }})</li>'.
168. Diese Zeile enthält den Code '{% endfor %}'.
169. Diese Zeile enthält den Code '</ul>'.
170. Diese Zeile enthält den Code '</section>'.
171. Diese Zeile enthält den Code '<section class="panel">'.
172. Diese Zeile enthält den Code '<h2>{{ t("admin.users") }}</h2>'.
173. Diese Zeile enthält den Code '<table>'.
174. Diese Zeile enthält den Code '<thead>'.
175. Diese Zeile enthält den Code '<tr><th>{{ t("admin.id") }}</th><th>{{ t("admin.email") }}</th><th>{{ t("admin.role") }}</th><th>...'.
176. Diese Zeile enthält den Code '</thead>'.
177. Diese Zeile enthält den Code '<tbody>'.
178. Diese Zeile enthält den Code '{% for user in users %}'.
179. Diese Zeile enthält den Code '<tr>'.
180. Diese Zeile enthält den Code '<td>{{ user.id }}</td>'.
181. Diese Zeile enthält den Code '<td>{{ user.email }}</td>'.
182. Diese Zeile enthält den Code '<td>{{ role_label(user.role) }}</td>'.
183. Diese Zeile enthält den Code '<td>'.
184. Diese Zeile enthält den Code '<form method="post" action="/admin/users/{{ user.id }}/role" class="inline">'.
185. Diese Zeile enthält den Code '<select name="role">'.
186. Diese Zeile enthält den Code '<option value="user" {% if user.role == "user" %}selected{% endif %}>{{ t("role.user") }}</option>'.
187. Diese Zeile enthält den Code '<option value="admin" {% if user.role == "admin" %}selected{% endif %}>{{ t("role.admin") }}</opt...'.
188. Diese Zeile enthält den Code '</select>'.
189. Diese Zeile enthält den Code '<button type="submit">{{ t("admin.save") }}</button>'.
190. Diese Zeile enthält den Code '</form>'.
191. Diese Zeile enthält den Code '</td>'.
192. Diese Zeile enthält den Code '</tr>'.
193. Diese Zeile enthält den Code '{% endfor %}'.
194. Diese Zeile enthält den Code '</tbody>'.
195. Diese Zeile enthält den Code '</table>'.
196. Diese Zeile enthält den Code '</section>'.
197. Diese Zeile enthält den Code '<section class="panel">'.
198. Diese Zeile enthält den Code '<h2>{{ t("admin.recipes") }}</h2>'.
199. Diese Zeile enthält den Code '<table>'.
200. Diese Zeile enthält den Code '<thead>'.
201. Diese Zeile enthält den Code '<tr><th>{{ t("admin.id") }}</th><th>{{ t("admin.title_column") }}</th><th>{{ t("admin.creator") }...'.
202. Diese Zeile enthält den Code '</thead>'.
203. Diese Zeile enthält den Code '<tbody>'.
204. Diese Zeile enthält den Code '{% for recipe in recipes %}'.
205. Diese Zeile enthält den Code '<tr>'.
206. Diese Zeile enthält den Code '<td>{{ recipe.id }}</td>'.
207. Diese Zeile enthält den Code '<td><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></td>'.
208. Diese Zeile enthält den Code '<td>{{ recipe.creator.email }}</td>'.
209. Diese Zeile enthält den Code '<td>{{ recipe.source }}</td>'.
210. Diese Zeile enthält den Code '<td>'.
211. Diese Zeile enthält den Code '<form method="post" action="/admin/recipes/{{ recipe.id }}/delete">'.
212. Diese Zeile enthält den Code '<button type="submit">{{ t("recipe.delete") }}</button>'.
213. Diese Zeile enthält den Code '</form>'.
214. Diese Zeile enthält den Code '</td>'.
215. Diese Zeile enthält den Code '</tr>'.
216. Diese Zeile enthält den Code '{% endfor %}'.
217. Diese Zeile enthält den Code '</tbody>'.
218. Diese Zeile enthält den Code '</table>'.
219. Diese Zeile enthält den Code '</section>'.
220. Diese Zeile enthält den Code '{% endblock %}'.

## app/templates/partials/recipe_list.html

```html
<p class="list-summary">
  {% if total > 0 %}
  {{ t("pagination.results_range", start=start_item, end=end_item, total=total) }}
  {% else %}
  {{ t("recipe.no_results") }}
  {% endif %}
</p>
<div class="cards">
  {% for entry in recipes_data %}
  {% set recipe = entry.recipe %}
  <article class="card">
    {% set primary_image = entry.primary_image %}
    {% set display_image_url = entry.display_image_url %}
    {% set display_image_kind = entry.display_image_kind %}
    {% set has_pending_change_request = entry.has_pending_change_request %}
    {% set can_upload_direct = current_user and current_user.role == "admin" %}
    {% set can_request_change = current_user and current_user.role != "admin" %}
    {% set image_feedback_message = "" %}
    {% set image_feedback_error = "" %}
    {% include "partials/recipe_card_image.html" %}
    <h3><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></h3>
    <p class="summary">{{ recipe.description }}</p>
    <p class="meta">{{ recipe.category }} | {{ difficulty_label(recipe.difficulty) }} | {{ recipe.prep_time_minutes }} min</p>
    <p class="meta">{{ t("recipe.rating_short") }} {{ "%.2f"|format(entry.avg_rating) }} ({{ entry.review_count }})</p>
  </article>
  {% endfor %}
</div>
{% if pages > 1 %}
{% set filter_query = "per_page=" ~ per_page ~ "&sort=" ~ (sort|urlencode) ~ "&title=" ~ (title|urlencode) ~ "&category=" ~ (category|urlencode) ~ "&difficulty=" ~ (difficulty|urlencode) ~ "&ingredient=" ~ (ingredient|urlencode) %}
<div class="pagination">
  <div class="pagination-links">
    {% if page > 1 %}
    <a href="/?page={{ page - 1 }}&{{ filter_query }}" hx-get="/?page={{ page - 1 }}&{{ filter_query }}" hx-target="#recipe-list" hx-push-url="true">{{ t("pagination.previous") }}</a>
    {% else %}
    <span class="disabled">{{ t("pagination.previous") }}</span>
    {% endif %}
    {% for item in pagination_items %}
    {% if item is none %}
    <span class="ellipsis">...</span>
    {% elif item == page %}
    <span class="active">{{ item }}</span>
    {% else %}
    <a href="/?page={{ item }}&{{ filter_query }}" hx-get="/?page={{ item }}&{{ filter_query }}" hx-target="#recipe-list" hx-push-url="true">{{ item }}</a>
    {% endif %}
    {% endfor %}
    {% if page < pages %}
    <a href="/?page={{ page + 1 }}&{{ filter_query }}" hx-get="/?page={{ page + 1 }}&{{ filter_query }}" hx-target="#recipe-list" hx-push-url="true">{{ t("pagination.next") }}</a>
    {% else %}
    <span class="disabled">{{ t("pagination.next") }}</span>
    {% endif %}
  </div>
  <span class="pagination-info">{{ t("pagination.page") }} {{ page }} / {{ total_pages }}</span>
</div>
{% endif %}

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '<p class="list-summary">'.
2. Diese Zeile enthält den Code '{% if total > 0 %}'.
3. Diese Zeile enthält den Code '{{ t("pagination.results_range", start=start_item, end=end_item, total=total) }}'.
4. Diese Zeile enthält den Code '{% else %}'.
5. Diese Zeile enthält den Code '{{ t("recipe.no_results") }}'.
6. Diese Zeile enthält den Code '{% endif %}'.
7. Diese Zeile enthält den Code '</p>'.
8. Diese Zeile enthält den Code '<div class="cards">'.
9. Diese Zeile enthält den Code '{% for entry in recipes_data %}'.
10. Diese Zeile enthält den Code '{% set recipe = entry.recipe %}'.
11. Diese Zeile enthält den Code '<article class="card">'.
12. Diese Zeile enthält den Code '{% set primary_image = entry.primary_image %}'.
13. Diese Zeile enthält den Code '{% set display_image_url = entry.display_image_url %}'.
14. Diese Zeile enthält den Code '{% set display_image_kind = entry.display_image_kind %}'.
15. Diese Zeile enthält den Code '{% set has_pending_change_request = entry.has_pending_change_request %}'.
16. Diese Zeile enthält den Code '{% set can_upload_direct = current_user and current_user.role == "admin" %}'.
17. Diese Zeile enthält den Code '{% set can_request_change = current_user and current_user.role != "admin" %}'.
18. Diese Zeile enthält den Code '{% set image_feedback_message = "" %}'.
19. Diese Zeile enthält den Code '{% set image_feedback_error = "" %}'.
20. Diese Zeile enthält den Code '{% include "partials/recipe_card_image.html" %}'.
21. Diese Zeile enthält den Code '<h3><a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a></h3>'.
22. Diese Zeile enthält den Code '<p class="summary">{{ recipe.description }}</p>'.
23. Diese Zeile enthält den Code '<p class="meta">{{ recipe.category }} | {{ difficulty_label(recipe.difficulty) }} | {{ recipe.pre...'.
24. Diese Zeile enthält den Code '<p class="meta">{{ t("recipe.rating_short") }} {{ "%.2f"|format(entry.avg_rating) }} ({{ entry.re...'.
25. Diese Zeile enthält den Code '</article>'.
26. Diese Zeile enthält den Code '{% endfor %}'.
27. Diese Zeile enthält den Code '</div>'.
28. Diese Zeile enthält den Code '{% if pages > 1 %}'.
29. Diese Zeile enthält den Code '{% set filter_query = "per_page=" ~ per_page ~ "&sort=" ~ (sort|urlencode) ~ "&title=" ~ (title|u...'.
30. Diese Zeile enthält den Code '<div class="pagination">'.
31. Diese Zeile enthält den Code '<div class="pagination-links">'.
32. Diese Zeile enthält den Code '{% if page > 1 %}'.
33. Diese Zeile enthält den Code '<a href="/?page={{ page - 1 }}&{{ filter_query }}" hx-get="/?page={{ page - 1 }}&{{ filter_query ...'.
34. Diese Zeile enthält den Code '{% else %}'.
35. Diese Zeile enthält den Code '<span class="disabled">{{ t("pagination.previous") }}</span>'.
36. Diese Zeile enthält den Code '{% endif %}'.
37. Diese Zeile enthält den Code '{% for item in pagination_items %}'.
38. Diese Zeile enthält den Code '{% if item is none %}'.
39. Diese Zeile enthält den Code '<span class="ellipsis">...</span>'.
40. Diese Zeile enthält den Code '{% elif item == page %}'.
41. Diese Zeile enthält den Code '<span class="active">{{ item }}</span>'.
42. Diese Zeile enthält den Code '{% else %}'.
43. Diese Zeile enthält den Code '<a href="/?page={{ item }}&{{ filter_query }}" hx-get="/?page={{ item }}&{{ filter_query }}" hx-t...'.
44. Diese Zeile enthält den Code '{% endif %}'.
45. Diese Zeile enthält den Code '{% endfor %}'.
46. Diese Zeile enthält den Code '{% if page < pages %}'.
47. Diese Zeile enthält den Code '<a href="/?page={{ page + 1 }}&{{ filter_query }}" hx-get="/?page={{ page + 1 }}&{{ filter_query ...'.
48. Diese Zeile enthält den Code '{% else %}'.
49. Diese Zeile enthält den Code '<span class="disabled">{{ t("pagination.next") }}</span>'.
50. Diese Zeile enthält den Code '{% endif %}'.
51. Diese Zeile enthält den Code '</div>'.
52. Diese Zeile enthält den Code '<span class="pagination-info">{{ t("pagination.page") }} {{ page }} / {{ total_pages }}</span>'.
53. Diese Zeile enthält den Code '</div>'.
54. Diese Zeile enthält den Code '{% endif %}'.

## app/templates/partials/recipe_images.html

```html
<section class="panel" id="recipe-images-section">
  <h2>{{ t("images.title") }}</h2>

  {% if display_image_url %}
  <img
    src="{{ display_image_url }}"
    alt="{{ recipe.title }}"
    class="hero-image"
    {% if display_image_kind == "external" %}referrerpolicy="no-referrer" loading="lazy"{% endif %}
  >
  {% else %}
  <div class="hero-placeholder">
    <span>{{ t("images.placeholder") }}</span>
    {% if can_upload_direct or can_request_change %}
    <details class="plus-uploader">
      <summary title="{{ t('images.plus_title') }}">+</summary>
      {% if can_upload_direct %}
      <form
        method="post"
        action="/recipes/{{ recipe.id }}/images"
        enctype="multipart/form-data"
        hx-post="/recipes/{{ recipe.id }}/images"
        hx-encoding="multipart/form-data"
        hx-target="#recipe-images-section"
        hx-swap="outerHTML"
        class="stack"
      >
        <input type="hidden" name="response_mode" value="detail">
        <input type="hidden" name="set_primary" value="true">
        <input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>
        <button type="submit">{{ t("images.upload") }}</button>
      </form>
      {% elif can_request_change %}
      <form
        method="post"
        action="/recipes/{{ recipe.id }}/image-change-request"
        enctype="multipart/form-data"
        hx-post="/recipes/{{ recipe.id }}/image-change-request"
        hx-encoding="multipart/form-data"
        hx-target="#recipe-images-section"
        hx-swap="outerHTML"
        class="stack"
      >
        <input type="hidden" name="response_mode" value="detail">
        <input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>
        <button type="submit">{{ t("images.propose_change") }}</button>
      </form>
      {% endif %}
    </details>
    {% else %}
    <a href="/login">{{ t("images.login_to_propose") }}</a>
    {% endif %}
  </div>
  {% endif %}

  {% if image_feedback_message %}
  <p class="meta">{{ image_feedback_message }}</p>
  {% endif %}
  {% if image_feedback_error %}
  <p class="error">{{ image_feedback_error }}</p>
  {% endif %}
  {% if has_pending_change_request %}
  <p class="meta pending-badge">{{ t("images.pending_badge") }}</p>
  {% endif %}

  {% if can_upload_direct %}
  <form
    method="post"
    action="/recipes/{{ recipe.id }}/images"
    enctype="multipart/form-data"
    hx-post="/recipes/{{ recipe.id }}/images"
    hx-encoding="multipart/form-data"
    hx-target="#recipe-images-section"
    hx-swap="outerHTML"
    class="stack"
  >
    <input type="hidden" name="response_mode" value="detail">
    <label>{{ t("images.new_file") }}
      <input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>
    </label>
    <label class="inline">
      <input type="checkbox" name="set_primary" value="true" checked>
      {{ t("images.set_primary") }}
    </label>
    <button type="submit">{{ t("images.upload") }}</button>
  </form>
  {% elif can_request_change %}
  <p class="meta">{{ t("images.user_change_note") }}</p>
  <form
    method="post"
    action="/recipes/{{ recipe.id }}/image-change-request"
    enctype="multipart/form-data"
    hx-post="/recipes/{{ recipe.id }}/image-change-request"
    hx-encoding="multipart/form-data"
    hx-target="#recipe-images-section"
    hx-swap="outerHTML"
    class="stack"
  >
    <input type="hidden" name="response_mode" value="detail">
    <label>{{ t("images.new_file") }}
      <input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>
    </label>
    <button type="submit">{{ t("images.propose_change") }}</button>
  </form>
  {% endif %}

  <div class="cards">
    {% for image in recipe.images %}
    <article class="card">
      <img src="/images/{{ image.id }}" alt="{{ image.filename }}" class="thumb">
      <p>{{ image.filename }}</p>
      {% if image.is_primary %}
      <p class="meta">{{ t("images.primary") }}</p>
      {% endif %}
      {% if can_upload_direct %}
      <div class="actions">
        {% if not image.is_primary %}
        <form
          method="post"
          action="/images/{{ image.id }}/set-primary"
          hx-post="/images/{{ image.id }}/set-primary"
          hx-target="#recipe-images-section"
          hx-swap="outerHTML"
        >
          <button type="submit">{{ t("images.set_primary") }}</button>
        </form>
        {% endif %}
        <form
          method="post"
          action="/images/{{ image.id }}/delete"
          hx-post="/images/{{ image.id }}/delete"
          hx-target="#recipe-images-section"
          hx-swap="outerHTML"
        >
          <button type="submit">{{ t("images.delete") }}</button>
        </form>
      </div>
      {% endif %}
    </article>
    {% else %}
    <p>{{ t("images.empty") }}</p>
    {% endfor %}
  </div>
</section>

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '<section class="panel" id="recipe-images-section">'.
2. Diese Zeile enthält den Code '<h2>{{ t("images.title") }}</h2>'.
3. Diese Zeile ist leer und trennt Abschnitte.
4. Diese Zeile enthält den Code '{% if display_image_url %}'.
5. Diese Zeile enthält den Code '<img'.
6. Diese Zeile enthält den Code 'src="{{ display_image_url }}"'.
7. Diese Zeile enthält den Code 'alt="{{ recipe.title }}"'.
8. Diese Zeile enthält den Code 'class="hero-image"'.
9. Diese Zeile enthält den Code '{% if display_image_kind == "external" %}referrerpolicy="no-referrer" loading="lazy"{% endif %}'.
10. Diese Zeile enthält den Code '>'.
11. Diese Zeile enthält den Code '{% else %}'.
12. Diese Zeile enthält den Code '<div class="hero-placeholder">'.
13. Diese Zeile enthält den Code '<span>{{ t("images.placeholder") }}</span>'.
14. Diese Zeile enthält den Code '{% if can_upload_direct or can_request_change %}'.
15. Diese Zeile enthält den Code '<details class="plus-uploader">'.
16. Diese Zeile enthält den Code '<summary title="{{ t('images.plus_title') }}">+</summary>'.
17. Diese Zeile enthält den Code '{% if can_upload_direct %}'.
18. Diese Zeile enthält den Code '<form'.
19. Diese Zeile enthält den Code 'method="post"'.
20. Diese Zeile enthält den Code 'action="/recipes/{{ recipe.id }}/images"'.
21. Diese Zeile enthält den Code 'enctype="multipart/form-data"'.
22. Diese Zeile enthält den Code 'hx-post="/recipes/{{ recipe.id }}/images"'.
23. Diese Zeile enthält den Code 'hx-encoding="multipart/form-data"'.
24. Diese Zeile enthält den Code 'hx-target="#recipe-images-section"'.
25. Diese Zeile enthält den Code 'hx-swap="outerHTML"'.
26. Diese Zeile enthält den Code 'class="stack"'.
27. Diese Zeile enthält den Code '>'.
28. Diese Zeile enthält den Code '<input type="hidden" name="response_mode" value="detail">'.
29. Diese Zeile enthält den Code '<input type="hidden" name="set_primary" value="true">'.
30. Diese Zeile enthält den Code '<input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>'.
31. Diese Zeile enthält den Code '<button type="submit">{{ t("images.upload") }}</button>'.
32. Diese Zeile enthält den Code '</form>'.
33. Diese Zeile enthält den Code '{% elif can_request_change %}'.
34. Diese Zeile enthält den Code '<form'.
35. Diese Zeile enthält den Code 'method="post"'.
36. Diese Zeile enthält den Code 'action="/recipes/{{ recipe.id }}/image-change-request"'.
37. Diese Zeile enthält den Code 'enctype="multipart/form-data"'.
38. Diese Zeile enthält den Code 'hx-post="/recipes/{{ recipe.id }}/image-change-request"'.
39. Diese Zeile enthält den Code 'hx-encoding="multipart/form-data"'.
40. Diese Zeile enthält den Code 'hx-target="#recipe-images-section"'.
41. Diese Zeile enthält den Code 'hx-swap="outerHTML"'.
42. Diese Zeile enthält den Code 'class="stack"'.
43. Diese Zeile enthält den Code '>'.
44. Diese Zeile enthält den Code '<input type="hidden" name="response_mode" value="detail">'.
45. Diese Zeile enthält den Code '<input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>'.
46. Diese Zeile enthält den Code '<button type="submit">{{ t("images.propose_change") }}</button>'.
47. Diese Zeile enthält den Code '</form>'.
48. Diese Zeile enthält den Code '{% endif %}'.
49. Diese Zeile enthält den Code '</details>'.
50. Diese Zeile enthält den Code '{% else %}'.
51. Diese Zeile enthält den Code '<a href="/login">{{ t("images.login_to_propose") }}</a>'.
52. Diese Zeile enthält den Code '{% endif %}'.
53. Diese Zeile enthält den Code '</div>'.
54. Diese Zeile enthält den Code '{% endif %}'.
55. Diese Zeile ist leer und trennt Abschnitte.
56. Diese Zeile enthält den Code '{% if image_feedback_message %}'.
57. Diese Zeile enthält den Code '<p class="meta">{{ image_feedback_message }}</p>'.
58. Diese Zeile enthält den Code '{% endif %}'.
59. Diese Zeile enthält den Code '{% if image_feedback_error %}'.
60. Diese Zeile enthält den Code '<p class="error">{{ image_feedback_error }}</p>'.
61. Diese Zeile enthält den Code '{% endif %}'.
62. Diese Zeile enthält den Code '{% if has_pending_change_request %}'.
63. Diese Zeile enthält den Code '<p class="meta pending-badge">{{ t("images.pending_badge") }}</p>'.
64. Diese Zeile enthält den Code '{% endif %}'.
65. Diese Zeile ist leer und trennt Abschnitte.
66. Diese Zeile enthält den Code '{% if can_upload_direct %}'.
67. Diese Zeile enthält den Code '<form'.
68. Diese Zeile enthält den Code 'method="post"'.
69. Diese Zeile enthält den Code 'action="/recipes/{{ recipe.id }}/images"'.
70. Diese Zeile enthält den Code 'enctype="multipart/form-data"'.
71. Diese Zeile enthält den Code 'hx-post="/recipes/{{ recipe.id }}/images"'.
72. Diese Zeile enthält den Code 'hx-encoding="multipart/form-data"'.
73. Diese Zeile enthält den Code 'hx-target="#recipe-images-section"'.
74. Diese Zeile enthält den Code 'hx-swap="outerHTML"'.
75. Diese Zeile enthält den Code 'class="stack"'.
76. Diese Zeile enthält den Code '>'.
77. Diese Zeile enthält den Code '<input type="hidden" name="response_mode" value="detail">'.
78. Diese Zeile enthält den Code '<label>{{ t("images.new_file") }}'.
79. Diese Zeile enthält den Code '<input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>'.
80. Diese Zeile enthält den Code '</label>'.
81. Diese Zeile enthält den Code '<label class="inline">'.
82. Diese Zeile enthält den Code '<input type="checkbox" name="set_primary" value="true" checked>'.
83. Diese Zeile enthält den Code '{{ t("images.set_primary") }}'.
84. Diese Zeile enthält den Code '</label>'.
85. Diese Zeile enthält den Code '<button type="submit">{{ t("images.upload") }}</button>'.
86. Diese Zeile enthält den Code '</form>'.
87. Diese Zeile enthält den Code '{% elif can_request_change %}'.
88. Diese Zeile enthält den Code '<p class="meta">{{ t("images.user_change_note") }}</p>'.
89. Diese Zeile enthält den Code '<form'.
90. Diese Zeile enthält den Code 'method="post"'.
91. Diese Zeile enthält den Code 'action="/recipes/{{ recipe.id }}/image-change-request"'.
92. Diese Zeile enthält den Code 'enctype="multipart/form-data"'.
93. Diese Zeile enthält den Code 'hx-post="/recipes/{{ recipe.id }}/image-change-request"'.
94. Diese Zeile enthält den Code 'hx-encoding="multipart/form-data"'.
95. Diese Zeile enthält den Code 'hx-target="#recipe-images-section"'.
96. Diese Zeile enthält den Code 'hx-swap="outerHTML"'.
97. Diese Zeile enthält den Code 'class="stack"'.
98. Diese Zeile enthält den Code '>'.
99. Diese Zeile enthält den Code '<input type="hidden" name="response_mode" value="detail">'.
100. Diese Zeile enthält den Code '<label>{{ t("images.new_file") }}'.
101. Diese Zeile enthält den Code '<input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>'.
102. Diese Zeile enthält den Code '</label>'.
103. Diese Zeile enthält den Code '<button type="submit">{{ t("images.propose_change") }}</button>'.
104. Diese Zeile enthält den Code '</form>'.
105. Diese Zeile enthält den Code '{% endif %}'.
106. Diese Zeile ist leer und trennt Abschnitte.
107. Diese Zeile enthält den Code '<div class="cards">'.
108. Diese Zeile enthält den Code '{% for image in recipe.images %}'.
109. Diese Zeile enthält den Code '<article class="card">'.
110. Diese Zeile enthält den Code '<img src="/images/{{ image.id }}" alt="{{ image.filename }}" class="thumb">'.
111. Diese Zeile enthält den Code '<p>{{ image.filename }}</p>'.
112. Diese Zeile enthält den Code '{% if image.is_primary %}'.
113. Diese Zeile enthält den Code '<p class="meta">{{ t("images.primary") }}</p>'.
114. Diese Zeile enthält den Code '{% endif %}'.
115. Diese Zeile enthält den Code '{% if can_upload_direct %}'.
116. Diese Zeile enthält den Code '<div class="actions">'.
117. Diese Zeile enthält den Code '{% if not image.is_primary %}'.
118. Diese Zeile enthält den Code '<form'.
119. Diese Zeile enthält den Code 'method="post"'.
120. Diese Zeile enthält den Code 'action="/images/{{ image.id }}/set-primary"'.
121. Diese Zeile enthält den Code 'hx-post="/images/{{ image.id }}/set-primary"'.
122. Diese Zeile enthält den Code 'hx-target="#recipe-images-section"'.
123. Diese Zeile enthält den Code 'hx-swap="outerHTML"'.
124. Diese Zeile enthält den Code '>'.
125. Diese Zeile enthält den Code '<button type="submit">{{ t("images.set_primary") }}</button>'.
126. Diese Zeile enthält den Code '</form>'.
127. Diese Zeile enthält den Code '{% endif %}'.
128. Diese Zeile enthält den Code '<form'.
129. Diese Zeile enthält den Code 'method="post"'.
130. Diese Zeile enthält den Code 'action="/images/{{ image.id }}/delete"'.
131. Diese Zeile enthält den Code 'hx-post="/images/{{ image.id }}/delete"'.
132. Diese Zeile enthält den Code 'hx-target="#recipe-images-section"'.
133. Diese Zeile enthält den Code 'hx-swap="outerHTML"'.
134. Diese Zeile enthält den Code '>'.
135. Diese Zeile enthält den Code '<button type="submit">{{ t("images.delete") }}</button>'.
136. Diese Zeile enthält den Code '</form>'.
137. Diese Zeile enthält den Code '</div>'.
138. Diese Zeile enthält den Code '{% endif %}'.
139. Diese Zeile enthält den Code '</article>'.
140. Diese Zeile enthält den Code '{% else %}'.
141. Diese Zeile enthält den Code '<p>{{ t("images.empty") }}</p>'.
142. Diese Zeile enthält den Code '{% endfor %}'.
143. Diese Zeile enthält den Code '</div>'.
144. Diese Zeile enthält den Code '</section>'.

## app/templates/partials/recipe_card_image.html

```html
<div id="card-image-{{ recipe.id }}" class="card-image-wrap">
  {% if display_image_url %}
  <img
    src="{{ display_image_url }}"
    alt="{{ recipe.title }}"
    class="thumb"
    {% if display_image_kind == "external" %}referrerpolicy="no-referrer" loading="lazy"{% endif %}
  >
  {% else %}
  <div class="thumb placeholder-thumb">
    <span>{{ t("images.placeholder") }}</span>
    {% if can_upload_direct or can_request_change %}
    <details class="plus-uploader">
      <summary title="{{ t('images.plus_title') }}">+</summary>
      {% if can_upload_direct %}
      <form
        method="post"
        action="/recipes/{{ recipe.id }}/images"
        enctype="multipart/form-data"
        hx-post="/recipes/{{ recipe.id }}/images"
        hx-encoding="multipart/form-data"
        hx-target="#card-image-{{ recipe.id }}"
        hx-swap="outerHTML"
        class="stack"
      >
        <input type="hidden" name="response_mode" value="card">
        <input type="hidden" name="set_primary" value="true">
        <input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>
        <button type="submit">{{ t("images.upload") }}</button>
      </form>
      {% elif can_request_change %}
      <form
        method="post"
        action="/recipes/{{ recipe.id }}/image-change-request"
        enctype="multipart/form-data"
        hx-post="/recipes/{{ recipe.id }}/image-change-request"
        hx-encoding="multipart/form-data"
        hx-target="#card-image-{{ recipe.id }}"
        hx-swap="outerHTML"
        class="stack"
      >
        <input type="hidden" name="response_mode" value="card">
        <input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>
        <button type="submit">{{ t("images.propose_change") }}</button>
      </form>
      {% endif %}
    </details>
    {% else %}
    <a class="placeholder-login" href="/login">{{ t("images.login_to_propose") }}</a>
    {% endif %}
  </div>
  {% endif %}
  {% if has_pending_change_request %}
  <p class="meta pending-badge">{{ t("images.pending_badge") }}</p>
  {% endif %}
  {% if image_feedback_message %}
  <p class="meta">{{ image_feedback_message }}</p>
  {% endif %}
  {% if image_feedback_error %}
  <p class="error">{{ image_feedback_error }}</p>
  {% endif %}
</div>

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '<div id="card-image-{{ recipe.id }}" class="card-image-wrap">'.
2. Diese Zeile enthält den Code '{% if display_image_url %}'.
3. Diese Zeile enthält den Code '<img'.
4. Diese Zeile enthält den Code 'src="{{ display_image_url }}"'.
5. Diese Zeile enthält den Code 'alt="{{ recipe.title }}"'.
6. Diese Zeile enthält den Code 'class="thumb"'.
7. Diese Zeile enthält den Code '{% if display_image_kind == "external" %}referrerpolicy="no-referrer" loading="lazy"{% endif %}'.
8. Diese Zeile enthält den Code '>'.
9. Diese Zeile enthält den Code '{% else %}'.
10. Diese Zeile enthält den Code '<div class="thumb placeholder-thumb">'.
11. Diese Zeile enthält den Code '<span>{{ t("images.placeholder") }}</span>'.
12. Diese Zeile enthält den Code '{% if can_upload_direct or can_request_change %}'.
13. Diese Zeile enthält den Code '<details class="plus-uploader">'.
14. Diese Zeile enthält den Code '<summary title="{{ t('images.plus_title') }}">+</summary>'.
15. Diese Zeile enthält den Code '{% if can_upload_direct %}'.
16. Diese Zeile enthält den Code '<form'.
17. Diese Zeile enthält den Code 'method="post"'.
18. Diese Zeile enthält den Code 'action="/recipes/{{ recipe.id }}/images"'.
19. Diese Zeile enthält den Code 'enctype="multipart/form-data"'.
20. Diese Zeile enthält den Code 'hx-post="/recipes/{{ recipe.id }}/images"'.
21. Diese Zeile enthält den Code 'hx-encoding="multipart/form-data"'.
22. Diese Zeile enthält den Code 'hx-target="#card-image-{{ recipe.id }}"'.
23. Diese Zeile enthält den Code 'hx-swap="outerHTML"'.
24. Diese Zeile enthält den Code 'class="stack"'.
25. Diese Zeile enthält den Code '>'.
26. Diese Zeile enthält den Code '<input type="hidden" name="response_mode" value="card">'.
27. Diese Zeile enthält den Code '<input type="hidden" name="set_primary" value="true">'.
28. Diese Zeile enthält den Code '<input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>'.
29. Diese Zeile enthält den Code '<button type="submit">{{ t("images.upload") }}</button>'.
30. Diese Zeile enthält den Code '</form>'.
31. Diese Zeile enthält den Code '{% elif can_request_change %}'.
32. Diese Zeile enthält den Code '<form'.
33. Diese Zeile enthält den Code 'method="post"'.
34. Diese Zeile enthält den Code 'action="/recipes/{{ recipe.id }}/image-change-request"'.
35. Diese Zeile enthält den Code 'enctype="multipart/form-data"'.
36. Diese Zeile enthält den Code 'hx-post="/recipes/{{ recipe.id }}/image-change-request"'.
37. Diese Zeile enthält den Code 'hx-encoding="multipart/form-data"'.
38. Diese Zeile enthält den Code 'hx-target="#card-image-{{ recipe.id }}"'.
39. Diese Zeile enthält den Code 'hx-swap="outerHTML"'.
40. Diese Zeile enthält den Code 'class="stack"'.
41. Diese Zeile enthält den Code '>'.
42. Diese Zeile enthält den Code '<input type="hidden" name="response_mode" value="card">'.
43. Diese Zeile enthält den Code '<input type="file" name="file" accept="image/png,image/jpeg,image/webp" required>'.
44. Diese Zeile enthält den Code '<button type="submit">{{ t("images.propose_change") }}</button>'.
45. Diese Zeile enthält den Code '</form>'.
46. Diese Zeile enthält den Code '{% endif %}'.
47. Diese Zeile enthält den Code '</details>'.
48. Diese Zeile enthält den Code '{% else %}'.
49. Diese Zeile enthält den Code '<a class="placeholder-login" href="/login">{{ t("images.login_to_propose") }}</a>'.
50. Diese Zeile enthält den Code '{% endif %}'.
51. Diese Zeile enthält den Code '</div>'.
52. Diese Zeile enthält den Code '{% endif %}'.
53. Diese Zeile enthält den Code '{% if has_pending_change_request %}'.
54. Diese Zeile enthält den Code '<p class="meta pending-badge">{{ t("images.pending_badge") }}</p>'.
55. Diese Zeile enthält den Code '{% endif %}'.
56. Diese Zeile enthält den Code '{% if image_feedback_message %}'.
57. Diese Zeile enthält den Code '<p class="meta">{{ image_feedback_message }}</p>'.
58. Diese Zeile enthält den Code '{% endif %}'.
59. Diese Zeile enthält den Code '{% if image_feedback_error %}'.
60. Diese Zeile enthält den Code '<p class="error">{{ image_feedback_error }}</p>'.
61. Diese Zeile enthält den Code '{% endif %}'.
62. Diese Zeile enthält den Code '</div>'.

## app/templates/admin_image_change_requests.html

```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("image_change.admin_title") }}</h1>
  <form method="get" action="/admin/image-change-requests" class="inline">
    <label>{{ t("submission.status_filter") }}
      <select name="status_filter">
        <option value="pending" {% if status_filter == "pending" %}selected{% endif %}>{{ t("submission.status_pending") }}</option>
        <option value="approved" {% if status_filter == "approved" %}selected{% endif %}>{{ t("submission.status_approved") }}</option>
        <option value="rejected" {% if status_filter == "rejected" %}selected{% endif %}>{{ t("submission.status_rejected") }}</option>
        <option value="all" {% if status_filter == "all" %}selected{% endif %}>{{ t("submission.status_all") }}</option>
      </select>
    </label>
    <button type="submit">{{ t("home.apply") }}</button>
  </form>
  <p class="meta">
    {{ t("submission.stats_pending") }}: {{ status_stats.pending }},
    {{ t("submission.stats_approved") }}: {{ status_stats.approved }},
    {{ t("submission.stats_rejected") }}: {{ status_stats.rejected }}
  </p>
</section>

<section class="panel">
  {% if image_change_requests %}
  <table>
    <thead>
      <tr>
        <th>{{ t("submission.table_date") }}</th>
        <th>{{ t("submission.table_title") }}</th>
        <th>{{ t("submission.table_submitter") }}</th>
        <th>{{ t("submission.table_status") }}</th>
        <th>{{ t("submission.table_action") }}</th>
      </tr>
    </thead>
    <tbody>
      {% for item in image_change_requests %}
      <tr>
        <td>{{ item.created_at|datetime_de }}</td>
        <td><a href="/recipes/{{ item.recipe.id }}">{{ item.recipe.title }}</a></td>
        <td>{{ item.requester_user.email if item.requester_user else "-" }}</td>
        <td>{{ submission_status_label(item.status) }}</td>
        <td><a href="/admin/image-change-requests/{{ item.id }}">{{ t("submission.open_detail") }}</a></td>
      </tr>
      {% endfor %}
    </tbody>
  </table>

  {% if total_pages > 1 %}
  <div class="pagination">
    <div class="pagination-links">
      {% if page > 1 %}
      <a href="/admin/image-change-requests?status_filter={{ status_filter }}&page={{ page - 1 }}">{{ t("pagination.previous") }}</a>
      {% else %}
      <span class="disabled">{{ t("pagination.previous") }}</span>
      {% endif %}

      {% for item_page in range(1, total_pages + 1) %}
      {% if item_page == page %}
      <span class="active">{{ item_page }}</span>
      {% else %}
      <a href="/admin/image-change-requests?status_filter={{ status_filter }}&page={{ item_page }}">{{ item_page }}</a>
      {% endif %}
      {% endfor %}

      {% if page < total_pages %}
      <a href="/admin/image-change-requests?status_filter={{ status_filter }}&page={{ page + 1 }}">{{ t("pagination.next") }}</a>
      {% else %}
      <span class="disabled">{{ t("pagination.next") }}</span>
      {% endif %}
    </div>
    <span class="pagination-info">{{ t("pagination.page") }} {{ page }} / {{ total_pages }}</span>
  </div>
  {% endif %}

  {% else %}
  <p>{{ t("image_change.admin_empty") }}</p>
  {% endif %}
</section>
{% endblock %}

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '{% extends "base.html" %}'.
2. Diese Zeile enthält den Code '{% block content %}'.
3. Diese Zeile enthält den Code '<section class="panel">'.
4. Diese Zeile enthält den Code '<h1>{{ t("image_change.admin_title") }}</h1>'.
5. Diese Zeile enthält den Code '<form method="get" action="/admin/image-change-requests" class="inline">'.
6. Diese Zeile enthält den Code '<label>{{ t("submission.status_filter") }}'.
7. Diese Zeile enthält den Code '<select name="status_filter">'.
8. Diese Zeile enthält den Code '<option value="pending" {% if status_filter == "pending" %}selected{% endif %}>{{ t("submission.s...'.
9. Diese Zeile enthält den Code '<option value="approved" {% if status_filter == "approved" %}selected{% endif %}>{{ t("submission...'.
10. Diese Zeile enthält den Code '<option value="rejected" {% if status_filter == "rejected" %}selected{% endif %}>{{ t("submission...'.
11. Diese Zeile enthält den Code '<option value="all" {% if status_filter == "all" %}selected{% endif %}>{{ t("submission.status_al...'.
12. Diese Zeile enthält den Code '</select>'.
13. Diese Zeile enthält den Code '</label>'.
14. Diese Zeile enthält den Code '<button type="submit">{{ t("home.apply") }}</button>'.
15. Diese Zeile enthält den Code '</form>'.
16. Diese Zeile enthält den Code '<p class="meta">'.
17. Diese Zeile enthält den Code '{{ t("submission.stats_pending") }}: {{ status_stats.pending }},'.
18. Diese Zeile enthält den Code '{{ t("submission.stats_approved") }}: {{ status_stats.approved }},'.
19. Diese Zeile enthält den Code '{{ t("submission.stats_rejected") }}: {{ status_stats.rejected }}'.
20. Diese Zeile enthält den Code '</p>'.
21. Diese Zeile enthält den Code '</section>'.
22. Diese Zeile ist leer und trennt Abschnitte.
23. Diese Zeile enthält den Code '<section class="panel">'.
24. Diese Zeile enthält den Code '{% if image_change_requests %}'.
25. Diese Zeile enthält den Code '<table>'.
26. Diese Zeile enthält den Code '<thead>'.
27. Diese Zeile enthält den Code '<tr>'.
28. Diese Zeile enthält den Code '<th>{{ t("submission.table_date") }}</th>'.
29. Diese Zeile enthält den Code '<th>{{ t("submission.table_title") }}</th>'.
30. Diese Zeile enthält den Code '<th>{{ t("submission.table_submitter") }}</th>'.
31. Diese Zeile enthält den Code '<th>{{ t("submission.table_status") }}</th>'.
32. Diese Zeile enthält den Code '<th>{{ t("submission.table_action") }}</th>'.
33. Diese Zeile enthält den Code '</tr>'.
34. Diese Zeile enthält den Code '</thead>'.
35. Diese Zeile enthält den Code '<tbody>'.
36. Diese Zeile enthält den Code '{% for item in image_change_requests %}'.
37. Diese Zeile enthält den Code '<tr>'.
38. Diese Zeile enthält den Code '<td>{{ item.created_at|datetime_de }}</td>'.
39. Diese Zeile enthält den Code '<td><a href="/recipes/{{ item.recipe.id }}">{{ item.recipe.title }}</a></td>'.
40. Diese Zeile enthält den Code '<td>{{ item.requester_user.email if item.requester_user else "-" }}</td>'.
41. Diese Zeile enthält den Code '<td>{{ submission_status_label(item.status) }}</td>'.
42. Diese Zeile enthält den Code '<td><a href="/admin/image-change-requests/{{ item.id }}">{{ t("submission.open_detail") }}</a></td>'.
43. Diese Zeile enthält den Code '</tr>'.
44. Diese Zeile enthält den Code '{% endfor %}'.
45. Diese Zeile enthält den Code '</tbody>'.
46. Diese Zeile enthält den Code '</table>'.
47. Diese Zeile ist leer und trennt Abschnitte.
48. Diese Zeile enthält den Code '{% if total_pages > 1 %}'.
49. Diese Zeile enthält den Code '<div class="pagination">'.
50. Diese Zeile enthält den Code '<div class="pagination-links">'.
51. Diese Zeile enthält den Code '{% if page > 1 %}'.
52. Diese Zeile enthält den Code '<a href="/admin/image-change-requests?status_filter={{ status_filter }}&page={{ page - 1 }}">{{ t...'.
53. Diese Zeile enthält den Code '{% else %}'.
54. Diese Zeile enthält den Code '<span class="disabled">{{ t("pagination.previous") }}</span>'.
55. Diese Zeile enthält den Code '{% endif %}'.
56. Diese Zeile ist leer und trennt Abschnitte.
57. Diese Zeile enthält den Code '{% for item_page in range(1, total_pages + 1) %}'.
58. Diese Zeile enthält den Code '{% if item_page == page %}'.
59. Diese Zeile enthält den Code '<span class="active">{{ item_page }}</span>'.
60. Diese Zeile enthält den Code '{% else %}'.
61. Diese Zeile enthält den Code '<a href="/admin/image-change-requests?status_filter={{ status_filter }}&page={{ item_page }}">{{ ...'.
62. Diese Zeile enthält den Code '{% endif %}'.
63. Diese Zeile enthält den Code '{% endfor %}'.
64. Diese Zeile ist leer und trennt Abschnitte.
65. Diese Zeile enthält den Code '{% if page < total_pages %}'.
66. Diese Zeile enthält den Code '<a href="/admin/image-change-requests?status_filter={{ status_filter }}&page={{ page + 1 }}">{{ t...'.
67. Diese Zeile enthält den Code '{% else %}'.
68. Diese Zeile enthält den Code '<span class="disabled">{{ t("pagination.next") }}</span>'.
69. Diese Zeile enthält den Code '{% endif %}'.
70. Diese Zeile enthält den Code '</div>'.
71. Diese Zeile enthält den Code '<span class="pagination-info">{{ t("pagination.page") }} {{ page }} / {{ total_pages }}</span>'.
72. Diese Zeile enthält den Code '</div>'.
73. Diese Zeile enthält den Code '{% endif %}'.
74. Diese Zeile ist leer und trennt Abschnitte.
75. Diese Zeile enthält den Code '{% else %}'.
76. Diese Zeile enthält den Code '<p>{{ t("image_change.admin_empty") }}</p>'.
77. Diese Zeile enthält den Code '{% endif %}'.
78. Diese Zeile enthält den Code '</section>'.
79. Diese Zeile enthält den Code '{% endblock %}'.

## app/templates/admin_image_change_request_detail.html

```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("image_change.detail_title") }} #{{ image_change_request.id }}</h1>
  <p class="meta">
    {{ submission_status_label(image_change_request.status) }} |
    {{ image_change_request.created_at|datetime_de }} |
    {{ image_change_request.requester_user.email if image_change_request.requester_user else "-" }}
  </p>
  {% if message %}
  <p class="meta">{{ message }}</p>
  {% endif %}
  {% if image_change_request.admin_note %}
  <p class="meta">{{ t("submission.admin_note") }}: {{ image_change_request.admin_note }}</p>
  {% endif %}
  <div class="actions">
    <a href="/admin/image-change-requests">{{ t("submission.back_to_queue") }}</a>
    <a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a>
  </div>
</section>

<section class="panel">
  <h2>{{ t("image_change.compare_title") }}</h2>
  <div class="cards">
    <article class="card">
      <h3>{{ t("image_change.current_image") }}</h3>
      {% if current_image_url %}
      <img
        src="{{ current_image_url }}"
        alt="{{ recipe.title }}"
        class="thumb"
        {% if current_image_kind == "external" %}referrerpolicy="no-referrer" loading="lazy"{% endif %}
      >
      {% else %}
      <div class="thumb placeholder-thumb"><span>{{ t("images.placeholder") }}</span></div>
      {% endif %}
    </article>

    <article class="card">
      <h3>{{ t("image_change.proposed_image") }}</h3>
      {% if proposed_file %}
      <img src="/admin/image-change-files/{{ proposed_file.id }}" alt="{{ recipe.title }}" class="thumb">
      <p class="meta">{{ proposed_file.filename }}</p>
      {% else %}
      <div class="thumb placeholder-thumb"><span>{{ t("images.empty") }}</span></div>
      {% endif %}
    </article>
  </div>
</section>

<section class="panel">
  <h2>{{ t("submission.moderation_actions") }}</h2>
  {% if image_change_request.status == "pending" %}
  <form method="post" action="/admin/image-change-requests/{{ image_change_request.id }}/approve" class="stack">
    <label>{{ t("submission.optional_admin_note") }} <textarea name="admin_note" rows="3">{{ image_change_request.admin_note or "" }}</textarea></label>
    <button type="submit">{{ t("moderation.approve") }}</button>
  </form>

  <form method="post" action="/admin/image-change-requests/{{ image_change_request.id }}/reject" class="stack">
    <label>{{ t("submission.reject_reason") }} <textarea name="admin_note" rows="3" required></textarea></label>
    <button type="submit">{{ t("moderation.reject") }}</button>
  </form>
  {% else %}
  <p class="meta">{{ t("image_change.review_done") }}</p>
  {% endif %}
</section>
{% endblock %}

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '{% extends "base.html" %}'.
2. Diese Zeile enthält den Code '{% block content %}'.
3. Diese Zeile enthält den Code '<section class="panel">'.
4. Diese Zeile enthält den Code '<h1>{{ t("image_change.detail_title") }} #{{ image_change_request.id }}</h1>'.
5. Diese Zeile enthält den Code '<p class="meta">'.
6. Diese Zeile enthält den Code '{{ submission_status_label(image_change_request.status) }} |'.
7. Diese Zeile enthält den Code '{{ image_change_request.created_at|datetime_de }} |'.
8. Diese Zeile enthält den Code '{{ image_change_request.requester_user.email if image_change_request.requester_user else "-" }}'.
9. Diese Zeile enthält den Code '</p>'.
10. Diese Zeile enthält den Code '{% if message %}'.
11. Diese Zeile enthält den Code '<p class="meta">{{ message }}</p>'.
12. Diese Zeile enthält den Code '{% endif %}'.
13. Diese Zeile enthält den Code '{% if image_change_request.admin_note %}'.
14. Diese Zeile enthält den Code '<p class="meta">{{ t("submission.admin_note") }}: {{ image_change_request.admin_note }}</p>'.
15. Diese Zeile enthält den Code '{% endif %}'.
16. Diese Zeile enthält den Code '<div class="actions">'.
17. Diese Zeile enthält den Code '<a href="/admin/image-change-requests">{{ t("submission.back_to_queue") }}</a>'.
18. Diese Zeile enthält den Code '<a href="/recipes/{{ recipe.id }}">{{ recipe.title }}</a>'.
19. Diese Zeile enthält den Code '</div>'.
20. Diese Zeile enthält den Code '</section>'.
21. Diese Zeile ist leer und trennt Abschnitte.
22. Diese Zeile enthält den Code '<section class="panel">'.
23. Diese Zeile enthält den Code '<h2>{{ t("image_change.compare_title") }}</h2>'.
24. Diese Zeile enthält den Code '<div class="cards">'.
25. Diese Zeile enthält den Code '<article class="card">'.
26. Diese Zeile enthält den Code '<h3>{{ t("image_change.current_image") }}</h3>'.
27. Diese Zeile enthält den Code '{% if current_image_url %}'.
28. Diese Zeile enthält den Code '<img'.
29. Diese Zeile enthält den Code 'src="{{ current_image_url }}"'.
30. Diese Zeile enthält den Code 'alt="{{ recipe.title }}"'.
31. Diese Zeile enthält den Code 'class="thumb"'.
32. Diese Zeile enthält den Code '{% if current_image_kind == "external" %}referrerpolicy="no-referrer" loading="lazy"{% endif %}'.
33. Diese Zeile enthält den Code '>'.
34. Diese Zeile enthält den Code '{% else %}'.
35. Diese Zeile enthält den Code '<div class="thumb placeholder-thumb"><span>{{ t("images.placeholder") }}</span></div>'.
36. Diese Zeile enthält den Code '{% endif %}'.
37. Diese Zeile enthält den Code '</article>'.
38. Diese Zeile ist leer und trennt Abschnitte.
39. Diese Zeile enthält den Code '<article class="card">'.
40. Diese Zeile enthält den Code '<h3>{{ t("image_change.proposed_image") }}</h3>'.
41. Diese Zeile enthält den Code '{% if proposed_file %}'.
42. Diese Zeile enthält den Code '<img src="/admin/image-change-files/{{ proposed_file.id }}" alt="{{ recipe.title }}" class="thumb">'.
43. Diese Zeile enthält den Code '<p class="meta">{{ proposed_file.filename }}</p>'.
44. Diese Zeile enthält den Code '{% else %}'.
45. Diese Zeile enthält den Code '<div class="thumb placeholder-thumb"><span>{{ t("images.empty") }}</span></div>'.
46. Diese Zeile enthält den Code '{% endif %}'.
47. Diese Zeile enthält den Code '</article>'.
48. Diese Zeile enthält den Code '</div>'.
49. Diese Zeile enthält den Code '</section>'.
50. Diese Zeile ist leer und trennt Abschnitte.
51. Diese Zeile enthält den Code '<section class="panel">'.
52. Diese Zeile enthält den Code '<h2>{{ t("submission.moderation_actions") }}</h2>'.
53. Diese Zeile enthält den Code '{% if image_change_request.status == "pending" %}'.
54. Diese Zeile enthält den Code '<form method="post" action="/admin/image-change-requests/{{ image_change_request.id }}/approve" c...'.
55. Diese Zeile enthält den Code '<label>{{ t("submission.optional_admin_note") }} <textarea name="admin_note" rows="3">{{ image_ch...'.
56. Diese Zeile enthält den Code '<button type="submit">{{ t("moderation.approve") }}</button>'.
57. Diese Zeile enthält den Code '</form>'.
58. Diese Zeile ist leer und trennt Abschnitte.
59. Diese Zeile enthält den Code '<form method="post" action="/admin/image-change-requests/{{ image_change_request.id }}/reject" cl...'.
60. Diese Zeile enthält den Code '<label>{{ t("submission.reject_reason") }} <textarea name="admin_note" rows="3" required></textar...'.
61. Diese Zeile enthält den Code '<button type="submit">{{ t("moderation.reject") }}</button>'.
62. Diese Zeile enthält den Code '</form>'.
63. Diese Zeile enthält den Code '{% else %}'.
64. Diese Zeile enthält den Code '<p class="meta">{{ t("image_change.review_done") }}</p>'.
65. Diese Zeile enthält den Code '{% endif %}'.
66. Diese Zeile enthält den Code '</section>'.
67. Diese Zeile enthält den Code '{% endblock %}'.

## app/static/style.css

```text
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

.card-image-wrap {
  display: grid;
  gap: 0.35rem;
}

.hero-image {
  width: 100%;
  max-height: 380px;
  object-fit: cover;
  border-radius: 10px;
  margin-bottom: 0.8rem;
}

.placeholder-thumb,
.hero-placeholder {
  position: relative;
  display: grid;
  place-items: center;
  color: #4b5563;
  border-radius: 8px;
  border: 1px dashed #9ca3af;
  background: linear-gradient(135deg, #f3f4f6, #e5e7eb);
  text-align: center;
  padding: 0.75rem;
}

.placeholder-thumb {
  height: 160px;
  margin-bottom: 0.5rem;
}

.hero-placeholder {
  height: 320px;
  margin-bottom: 0.8rem;
}

.plus-uploader {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  max-width: min(240px, 85%);
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 0.3rem;
}

.plus-uploader summary {
  cursor: pointer;
  list-style: none;
  display: grid;
  place-items: center;
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  color: #fff;
  background: var(--accent);
  font-size: 1.35rem;
  font-weight: 700;
}

.plus-uploader summary::-webkit-details-marker {
  display: none;
}

.plus-uploader[open] summary {
  margin-bottom: 0.5rem;
}

.plus-uploader form {
  width: min(220px, 100%);
}

.placeholder-login {
  display: inline-block;
  margin-top: 0.4rem;
  font-weight: 600;
}

.pending-badge {
  display: inline-block;
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  border: 1px solid #f59e0b;
  color: #92400e;
  background: #fef3c7;
  font-size: 0.82rem;
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

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code ':root {'.
2. Diese Zeile enthält den Code '--bg: #f8f7f3;'.
3. Diese Zeile enthält den Code '--panel: #ffffff;'.
4. Diese Zeile enthält den Code '--ink: #1d2433;'.
5. Diese Zeile enthält den Code '--accent: #0f766e;'.
6. Diese Zeile enthält den Code '--danger: #b91c1c;'.
7. Diese Zeile enthält den Code '--border: #d1d5db;'.
8. Diese Zeile enthält den Code '--font: "Segoe UI", "Trebuchet MS", sans-serif;'.
9. Diese Zeile enthält den Code '}'.
10. Diese Zeile ist leer und trennt Abschnitte.
11. Diese Zeile enthält den Code '* {'.
12. Diese Zeile enthält den Code 'box-sizing: border-box;'.
13. Diese Zeile enthält den Code '}'.
14. Diese Zeile ist leer und trennt Abschnitte.
15. Diese Zeile enthält den Code 'body {'.
16. Diese Zeile enthält den Code 'margin: 0;'.
17. Diese Zeile enthält den Code 'color: var(--ink);'.
18. Diese Zeile enthält den Code 'background: radial-gradient(circle at top right, #e8f5f1, var(--bg));'.
19. Diese Zeile enthält den Code 'font-family: var(--font);'.
20. Diese Zeile enthält den Code '}'.
21. Diese Zeile ist leer und trennt Abschnitte.
22. Diese Zeile enthält den Code '.topbar {'.
23. Diese Zeile enthält den Code 'position: sticky;'.
24. Diese Zeile enthält den Code 'top: 0;'.
25. Diese Zeile enthält den Code 'z-index: 9;'.
26. Diese Zeile enthält den Code 'display: flex;'.
27. Diese Zeile enthält den Code 'justify-content: space-between;'.
28. Diese Zeile enthält den Code 'gap: 1rem;'.
29. Diese Zeile enthält den Code 'align-items: center;'.
30. Diese Zeile enthält den Code 'padding: 1rem;'.
31. Diese Zeile enthält den Code 'background: #fff;'.
32. Diese Zeile enthält den Code 'border-bottom: 1px solid var(--border);'.
33. Diese Zeile enthält den Code '}'.
34. Diese Zeile ist leer und trennt Abschnitte.
35. Diese Zeile enthält den Code '.brand {'.
36. Diese Zeile enthält den Code 'text-decoration: none;'.
37. Diese Zeile enthält den Code 'color: var(--accent);'.
38. Diese Zeile enthält den Code 'font-weight: 700;'.
39. Diese Zeile enthält den Code 'font-size: 1.25rem;'.
40. Diese Zeile enthält den Code '}'.
41. Diese Zeile ist leer und trennt Abschnitte.
42. Diese Zeile enthält den Code 'nav {'.
43. Diese Zeile enthält den Code 'display: flex;'.
44. Diese Zeile enthält den Code 'flex-wrap: wrap;'.
45. Diese Zeile enthält den Code 'gap: 0.6rem;'.
46. Diese Zeile enthält den Code 'align-items: center;'.
47. Diese Zeile enthält den Code '}'.
48. Diese Zeile ist leer und trennt Abschnitte.
49. Diese Zeile enthält den Code 'a {'.
50. Diese Zeile enthält den Code 'color: var(--accent);'.
51. Diese Zeile enthält den Code '}'.
52. Diese Zeile ist leer und trennt Abschnitte.
53. Diese Zeile enthält den Code '.container {'.
54. Diese Zeile enthält den Code 'max-width: 1080px;'.
55. Diese Zeile enthält den Code 'margin: 1.2rem auto;'.
56. Diese Zeile enthält den Code 'padding: 0 1rem 2rem;'.
57. Diese Zeile enthält den Code '}'.
58. Diese Zeile ist leer und trennt Abschnitte.
59. Diese Zeile enthält den Code '.panel {'.
60. Diese Zeile enthält den Code 'background: var(--panel);'.
61. Diese Zeile enthält den Code 'border: 1px solid var(--border);'.
62. Diese Zeile enthält den Code 'border-radius: 12px;'.
63. Diese Zeile enthält den Code 'padding: 1rem;'.
64. Diese Zeile enthält den Code 'margin-bottom: 1rem;'.
65. Diese Zeile enthält den Code 'box-shadow: 0 5px 14px rgba(0, 0, 0, 0.05);'.
66. Diese Zeile enthält den Code '}'.
67. Diese Zeile ist leer und trennt Abschnitte.
68. Diese Zeile enthält den Code '.narrow {'.
69. Diese Zeile enthält den Code 'max-width: 480px;'.
70. Diese Zeile enthält den Code '}'.
71. Diese Zeile ist leer und trennt Abschnitte.
72. Diese Zeile enthält den Code '.grid {'.
73. Diese Zeile enthält den Code 'display: grid;'.
74. Diese Zeile enthält den Code 'grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));'.
75. Diese Zeile enthält den Code 'gap: 0.5rem;'.
76. Diese Zeile enthält den Code '}'.
77. Diese Zeile ist leer und trennt Abschnitte.
78. Diese Zeile enthält den Code '.stack {'.
79. Diese Zeile enthält den Code 'display: grid;'.
80. Diese Zeile enthält den Code 'gap: 0.7rem;'.
81. Diese Zeile enthält den Code '}'.
82. Diese Zeile ist leer und trennt Abschnitte.
83. Diese Zeile enthält den Code '.cards {'.
84. Diese Zeile enthält den Code 'display: grid;'.
85. Diese Zeile enthält den Code 'grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));'.
86. Diese Zeile enthält den Code 'gap: 0.8rem;'.
87. Diese Zeile enthält den Code '}'.
88. Diese Zeile ist leer und trennt Abschnitte.
89. Diese Zeile enthält den Code '.card {'.
90. Diese Zeile enthält den Code 'border: 1px solid var(--border);'.
91. Diese Zeile enthält den Code 'border-radius: 10px;'.
92. Diese Zeile enthält den Code 'padding: 0.8rem;'.
93. Diese Zeile enthält den Code 'background: #fff;'.
94. Diese Zeile enthält den Code '}'.
95. Diese Zeile ist leer und trennt Abschnitte.
96. Diese Zeile enthält den Code '.card h3 {'.
97. Diese Zeile enthält den Code 'margin: 0.2rem 0 0.4rem;'.
98. Diese Zeile enthält den Code 'font-size: 1rem;'.
99. Diese Zeile enthält den Code 'line-height: 1.3;'.
100. Diese Zeile enthält den Code 'display: -webkit-box;'.
101. Diese Zeile enthält den Code '-webkit-line-clamp: 2;'.
102. Diese Zeile enthält den Code '-webkit-box-orient: vertical;'.
103. Diese Zeile enthält den Code 'overflow: hidden;'.
104. Diese Zeile enthält den Code '}'.
105. Diese Zeile ist leer und trennt Abschnitte.
106. Diese Zeile enthält den Code '.meta {'.
107. Diese Zeile enthält den Code 'color: #4b5563;'.
108. Diese Zeile enthält den Code 'font-size: 0.95rem;'.
109. Diese Zeile enthält den Code '}'.
110. Diese Zeile ist leer und trennt Abschnitte.
111. Diese Zeile enthält den Code '.summary {'.
112. Diese Zeile enthält den Code 'margin: 0.2rem 0 0.45rem;'.
113. Diese Zeile enthält den Code 'color: #24303f;'.
114. Diese Zeile enthält den Code 'display: -webkit-box;'.
115. Diese Zeile enthält den Code '-webkit-line-clamp: 3;'.
116. Diese Zeile enthält den Code '-webkit-box-orient: vertical;'.
117. Diese Zeile enthält den Code 'overflow: hidden;'.
118. Diese Zeile enthält den Code '}'.
119. Diese Zeile ist leer und trennt Abschnitte.
120. Diese Zeile enthält den Code '.thumb {'.
121. Diese Zeile enthält den Code 'width: 100%;'.
122. Diese Zeile enthält den Code 'height: 160px;'.
123. Diese Zeile enthält den Code 'object-fit: cover;'.
124. Diese Zeile enthält den Code 'border-radius: 8px;'.
125. Diese Zeile enthält den Code 'margin-bottom: 0.5rem;'.
126. Diese Zeile enthält den Code '}'.
127. Diese Zeile ist leer und trennt Abschnitte.
128. Diese Zeile enthält den Code '.card-image-wrap {'.
129. Diese Zeile enthält den Code 'display: grid;'.
130. Diese Zeile enthält den Code 'gap: 0.35rem;'.
131. Diese Zeile enthält den Code '}'.
132. Diese Zeile ist leer und trennt Abschnitte.
133. Diese Zeile enthält den Code '.hero-image {'.
134. Diese Zeile enthält den Code 'width: 100%;'.
135. Diese Zeile enthält den Code 'max-height: 380px;'.
136. Diese Zeile enthält den Code 'object-fit: cover;'.
137. Diese Zeile enthält den Code 'border-radius: 10px;'.
138. Diese Zeile enthält den Code 'margin-bottom: 0.8rem;'.
139. Diese Zeile enthält den Code '}'.
140. Diese Zeile ist leer und trennt Abschnitte.
141. Diese Zeile enthält den Code '.placeholder-thumb,'.
142. Diese Zeile enthält den Code '.hero-placeholder {'.
143. Diese Zeile enthält den Code 'position: relative;'.
144. Diese Zeile enthält den Code 'display: grid;'.
145. Diese Zeile enthält den Code 'place-items: center;'.
146. Diese Zeile enthält den Code 'color: #4b5563;'.
147. Diese Zeile enthält den Code 'border-radius: 8px;'.
148. Diese Zeile enthält den Code 'border: 1px dashed #9ca3af;'.
149. Diese Zeile enthält den Code 'background: linear-gradient(135deg, #f3f4f6, #e5e7eb);'.
150. Diese Zeile enthält den Code 'text-align: center;'.
151. Diese Zeile enthält den Code 'padding: 0.75rem;'.
152. Diese Zeile enthält den Code '}'.
153. Diese Zeile ist leer und trennt Abschnitte.
154. Diese Zeile enthält den Code '.placeholder-thumb {'.
155. Diese Zeile enthält den Code 'height: 160px;'.
156. Diese Zeile enthält den Code 'margin-bottom: 0.5rem;'.
157. Diese Zeile enthält den Code '}'.
158. Diese Zeile ist leer und trennt Abschnitte.
159. Diese Zeile enthält den Code '.hero-placeholder {'.
160. Diese Zeile enthält den Code 'height: 320px;'.
161. Diese Zeile enthält den Code 'margin-bottom: 0.8rem;'.
162. Diese Zeile enthält den Code '}'.
163. Diese Zeile ist leer und trennt Abschnitte.
164. Diese Zeile enthält den Code '.plus-uploader {'.
165. Diese Zeile enthält den Code 'position: absolute;'.
166. Diese Zeile enthält den Code 'top: 0.5rem;'.
167. Diese Zeile enthält den Code 'right: 0.5rem;'.
168. Diese Zeile enthält den Code 'max-width: min(240px, 85%);'.
169. Diese Zeile enthält den Code 'background: rgba(255, 255, 255, 0.95);'.
170. Diese Zeile enthält den Code 'border: 1px solid var(--border);'.
171. Diese Zeile enthält den Code 'border-radius: 10px;'.
172. Diese Zeile enthält den Code 'padding: 0.3rem;'.
173. Diese Zeile enthält den Code '}'.
174. Diese Zeile ist leer und trennt Abschnitte.
175. Diese Zeile enthält den Code '.plus-uploader summary {'.
176. Diese Zeile enthält den Code 'cursor: pointer;'.
177. Diese Zeile enthält den Code 'list-style: none;'.
178. Diese Zeile enthält den Code 'display: grid;'.
179. Diese Zeile enthält den Code 'place-items: center;'.
180. Diese Zeile enthält den Code 'width: 2rem;'.
181. Diese Zeile enthält den Code 'height: 2rem;'.
182. Diese Zeile enthält den Code 'border-radius: 999px;'.
183. Diese Zeile enthält den Code 'color: #fff;'.
184. Diese Zeile enthält den Code 'background: var(--accent);'.
185. Diese Zeile enthält den Code 'font-size: 1.35rem;'.
186. Diese Zeile enthält den Code 'font-weight: 700;'.
187. Diese Zeile enthält den Code '}'.
188. Diese Zeile ist leer und trennt Abschnitte.
189. Diese Zeile enthält den Code '.plus-uploader summary::-webkit-details-marker {'.
190. Diese Zeile enthält den Code 'display: none;'.
191. Diese Zeile enthält den Code '}'.
192. Diese Zeile ist leer und trennt Abschnitte.
193. Diese Zeile enthält den Code '.plus-uploader[open] summary {'.
194. Diese Zeile enthält den Code 'margin-bottom: 0.5rem;'.
195. Diese Zeile enthält den Code '}'.
196. Diese Zeile ist leer und trennt Abschnitte.
197. Diese Zeile enthält den Code '.plus-uploader form {'.
198. Diese Zeile enthält den Code 'width: min(220px, 100%);'.
199. Diese Zeile enthält den Code '}'.
200. Diese Zeile ist leer und trennt Abschnitte.
201. Diese Zeile enthält den Code '.placeholder-login {'.
202. Diese Zeile enthält den Code 'display: inline-block;'.
203. Diese Zeile enthält den Code 'margin-top: 0.4rem;'.
204. Diese Zeile enthält den Code 'font-weight: 600;'.
205. Diese Zeile enthält den Code '}'.
206. Diese Zeile ist leer und trennt Abschnitte.
207. Diese Zeile enthält den Code '.pending-badge {'.
208. Diese Zeile enthält den Code 'display: inline-block;'.
209. Diese Zeile enthält den Code 'padding: 0.2rem 0.55rem;'.
210. Diese Zeile enthält den Code 'border-radius: 999px;'.
211. Diese Zeile enthält den Code 'border: 1px solid #f59e0b;'.
212. Diese Zeile enthält den Code 'color: #92400e;'.
213. Diese Zeile enthält den Code 'background: #fef3c7;'.
214. Diese Zeile enthält den Code 'font-size: 0.82rem;'.
215. Diese Zeile enthält den Code '}'.
216. Diese Zeile ist leer und trennt Abschnitte.
217. Diese Zeile enthält den Code 'input,'.
218. Diese Zeile enthält den Code 'select,'.
219. Diese Zeile enthält den Code 'textarea,'.
220. Diese Zeile enthält den Code 'button {'.
221. Diese Zeile enthält den Code 'width: 100%;'.
222. Diese Zeile enthält den Code 'padding: 0.55rem 0.6rem;'.
223. Diese Zeile enthält den Code 'border-radius: 8px;'.
224. Diese Zeile enthält den Code 'border: 1px solid var(--border);'.
225. Diese Zeile enthält den Code 'font: inherit;'.
226. Diese Zeile enthält den Code '}'.
227. Diese Zeile ist leer und trennt Abschnitte.
228. Diese Zeile enthält den Code 'button {'.
229. Diese Zeile enthält den Code 'cursor: pointer;'.
230. Diese Zeile enthält den Code 'background: var(--accent);'.
231. Diese Zeile enthält den Code 'color: #fff;'.
232. Diese Zeile enthält den Code 'border: none;'.
233. Diese Zeile enthält den Code '}'.
234. Diese Zeile ist leer und trennt Abschnitte.
235. Diese Zeile enthält den Code '.inline {'.
236. Diese Zeile enthält den Code 'display: inline-flex;'.
237. Diese Zeile enthält den Code 'gap: 0.4rem;'.
238. Diese Zeile enthält den Code 'align-items: center;'.
239. Diese Zeile enthält den Code '}'.
240. Diese Zeile ist leer und trennt Abschnitte.
241. Diese Zeile enthält den Code '.inline button,'.
242. Diese Zeile enthält den Code '.inline input,'.
243. Diese Zeile enthält den Code '.inline select {'.
244. Diese Zeile enthält den Code 'width: auto;'.
245. Diese Zeile enthält den Code '}'.
246. Diese Zeile ist leer und trennt Abschnitte.
247. Diese Zeile enthält den Code '.actions {'.
248. Diese Zeile enthält den Code 'display: flex;'.
249. Diese Zeile enthält den Code 'flex-wrap: wrap;'.
250. Diese Zeile enthält den Code 'gap: 0.5rem;'.
251. Diese Zeile enthält den Code 'margin-top: 0.7rem;'.
252. Diese Zeile enthält den Code '}'.
253. Diese Zeile ist leer und trennt Abschnitte.
254. Diese Zeile enthält den Code '.hidden {'.
255. Diese Zeile enthält den Code 'display: none !important;'.
256. Diese Zeile enthält den Code '}'.
257. Diese Zeile ist leer und trennt Abschnitte.
258. Diese Zeile enthält den Code '.error {'.
259. Diese Zeile enthält den Code 'color: var(--danger);'.
260. Diese Zeile enthält den Code 'font-weight: 700;'.
261. Diese Zeile enthält den Code '}'.
262. Diese Zeile ist leer und trennt Abschnitte.
263. Diese Zeile enthält den Code '.pagination {'.
264. Diese Zeile enthält den Code 'display: grid;'.
265. Diese Zeile enthält den Code 'justify-items: center;'.
266. Diese Zeile enthält den Code 'gap: 0.55rem;'.
267. Diese Zeile enthält den Code 'margin-top: 1rem;'.
268. Diese Zeile enthält den Code '}'.
269. Diese Zeile ist leer und trennt Abschnitte.
270. Diese Zeile enthält den Code '.list-summary {'.
271. Diese Zeile enthält den Code 'margin: 0.3rem 0 0.8rem;'.
272. Diese Zeile enthält den Code 'font-weight: 600;'.
273. Diese Zeile enthält den Code '}'.
274. Diese Zeile ist leer und trennt Abschnitte.
275. Diese Zeile enthält den Code '.pagination-links {'.
276. Diese Zeile enthält den Code 'display: flex;'.
277. Diese Zeile enthält den Code 'justify-content: center;'.
278. Diese Zeile enthält den Code 'flex-wrap: wrap;'.
279. Diese Zeile enthält den Code 'gap: 0.4rem;'.
280. Diese Zeile enthält den Code 'align-items: center;'.
281. Diese Zeile enthält den Code '}'.
282. Diese Zeile ist leer und trennt Abschnitte.
283. Diese Zeile enthält den Code '.pagination-links a {'.
284. Diese Zeile enthält den Code 'min-width: 2rem;'.
285. Diese Zeile enthält den Code 'text-align: center;'.
286. Diese Zeile enthält den Code 'text-decoration: none;'.
287. Diese Zeile enthält den Code 'border: 1px solid var(--border);'.
288. Diese Zeile enthält den Code 'border-radius: 8px;'.
289. Diese Zeile enthält den Code 'padding: 0.35rem 0.55rem;'.
290. Diese Zeile enthält den Code 'background: #fff;'.
291. Diese Zeile enthält den Code '}'.
292. Diese Zeile ist leer und trennt Abschnitte.
293. Diese Zeile enthält den Code '.pagination-links .active {'.
294. Diese Zeile enthält den Code 'min-width: 2rem;'.
295. Diese Zeile enthält den Code 'text-align: center;'.
296. Diese Zeile enthält den Code 'border: 1px solid var(--accent);'.
297. Diese Zeile enthält den Code 'border-radius: 8px;'.
298. Diese Zeile enthält den Code 'padding: 0.35rem 0.55rem;'.
299. Diese Zeile enthält den Code 'background: var(--accent);'.
300. Diese Zeile enthält den Code 'color: #fff;'.
301. Diese Zeile enthält den Code '}'.
302. Diese Zeile ist leer und trennt Abschnitte.
303. Diese Zeile enthält den Code '.pagination-links .disabled {'.
304. Diese Zeile enthält den Code 'min-width: 2rem;'.
305. Diese Zeile enthält den Code 'text-align: center;'.
306. Diese Zeile enthält den Code 'border: 1px solid var(--border);'.
307. Diese Zeile enthält den Code 'border-radius: 8px;'.
308. Diese Zeile enthält den Code 'padding: 0.35rem 0.55rem;'.
309. Diese Zeile enthält den Code 'color: #9ca3af;'.
310. Diese Zeile enthält den Code 'background: #f3f4f6;'.
311. Diese Zeile enthält den Code '}'.
312. Diese Zeile ist leer und trennt Abschnitte.
313. Diese Zeile enthält den Code '.pagination-links .ellipsis {'.
314. Diese Zeile enthält den Code 'min-width: 2rem;'.
315. Diese Zeile enthält den Code 'text-align: center;'.
316. Diese Zeile enthält den Code 'padding: 0.35rem 0.55rem;'.
317. Diese Zeile enthält den Code 'color: #6b7280;'.
318. Diese Zeile enthält den Code '}'.
319. Diese Zeile ist leer und trennt Abschnitte.
320. Diese Zeile enthält den Code '.pagination-info {'.
321. Diese Zeile enthält den Code 'color: #4b5563;'.
322. Diese Zeile enthält den Code 'font-size: 0.95rem;'.
323. Diese Zeile enthält den Code '}'.
324. Diese Zeile ist leer und trennt Abschnitte.
325. Diese Zeile enthält den Code 'pre {'.
326. Diese Zeile enthält den Code 'white-space: pre-wrap;'.
327. Diese Zeile enthält den Code 'word-break: break-word;'.
328. Diese Zeile enthält den Code 'border: 1px solid var(--border);'.
329. Diese Zeile enthält den Code 'border-radius: 8px;'.
330. Diese Zeile enthält den Code 'background: #f8fafc;'.
331. Diese Zeile enthält den Code 'padding: 0.7rem;'.
332. Diese Zeile enthält den Code '}'.
333. Diese Zeile ist leer und trennt Abschnitte.
334. Diese Zeile enthält den Code 'table {'.
335. Diese Zeile enthält den Code 'width: 100%;'.
336. Diese Zeile enthält den Code 'border-collapse: collapse;'.
337. Diese Zeile enthält den Code '}'.
338. Diese Zeile ist leer und trennt Abschnitte.
339. Diese Zeile enthält den Code 'th,'.
340. Diese Zeile enthält den Code 'td {'.
341. Diese Zeile enthält den Code 'border-bottom: 1px solid var(--border);'.
342. Diese Zeile enthält den Code 'padding: 0.6rem 0.4rem;'.
343. Diese Zeile enthält den Code 'text-align: left;'.
344. Diese Zeile enthält den Code '}'.
345. Diese Zeile ist leer und trennt Abschnitte.
346. Diese Zeile enthält den Code '.lang-switch {'.
347. Diese Zeile enthält den Code 'display: inline-flex;'.
348. Diese Zeile enthält den Code 'align-items: center;'.
349. Diese Zeile enthält den Code 'gap: 0.35rem;'.
350. Diese Zeile enthält den Code 'color: #4b5563;'.
351. Diese Zeile enthält den Code 'font-size: 0.92rem;'.
352. Diese Zeile enthält den Code '}'.
353. Diese Zeile ist leer und trennt Abschnitte.
354. Diese Zeile enthält den Code '.lang-switch a {'.
355. Diese Zeile enthält den Code 'text-decoration: none;'.
356. Diese Zeile enthält den Code 'padding: 0.2rem 0.45rem;'.
357. Diese Zeile enthält den Code 'border: 1px solid var(--border);'.
358. Diese Zeile enthält den Code 'border-radius: 999px;'.
359. Diese Zeile enthält den Code 'color: var(--accent);'.
360. Diese Zeile enthält den Code 'background: #fff;'.
361. Diese Zeile enthält den Code '}'.
362. Diese Zeile ist leer und trennt Abschnitte.
363. Diese Zeile enthält den Code '.lang-switch a.active {'.
364. Diese Zeile enthält den Code 'color: #fff;'.
365. Diese Zeile enthält den Code 'background: var(--accent);'.
366. Diese Zeile enthält den Code 'border-color: var(--accent);'.
367. Diese Zeile enthält den Code '}'.

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
  "auth.change_password_button": "Passwort aktualisieren",
  "auth.change_password_title": "Passwort aendern",
  "auth.change_email_confirm_button": "E-Mail jetzt aktualisieren",
  "auth.change_email_confirm_hint": "Du bestaetigst die neue E-Mail-Adresse: {email}",
  "auth.change_email_confirm_title": "E-Mail-Aenderung bestaetigen",
  "auth.change_email_current": "Aktuelle E-Mail: {email}",
  "auth.change_email_open_link": "E-Mail-Adresse aendern",
  "auth.change_email_request_button": "Bestaetigungslink senden",
  "auth.change_email_requested": "Bitte pruefe deine neue E-Mail und bestaetige den Link.",
  "auth.change_email_reissue_hint": "Wenn der Link abgelaufen ist, fordere bitte einen neuen Link an.",
  "auth.change_email_retry_link": "Neue E-Mail-Aenderung anfordern",
  "auth.change_email_title": "E-Mail aendern",
  "auth.confirm_password": "Passwort bestaetigen",
  "auth.email": "E-Mail",
  "auth.email_change_body": "Bitte bestaetige deine neue E-Mail-Adresse mit diesem Link: {confirm_link}",
  "auth.email_change_same_email": "Die neue E-Mail entspricht bereits deiner aktuellen Adresse.",
  "auth.email_change_subject": "MealMate E-Mail-Aenderung bestaetigen",
  "auth.email_change_success": "E-Mail wurde erfolgreich aktualisiert.",
  "auth.forgot_generic_response": "Wenn der Account existiert, wurde eine E-Mail gesendet.",
  "auth.forgot_password_button": "Reset-Link anfordern",
  "auth.forgot_password_hint": "Gib deine E-Mail oder deinen Benutzernamen ein, um einen Reset-Link zu erhalten.",
  "auth.forgot_password_link": "Passwort vergessen?",
  "auth.forgot_password_title": "Passwort vergessen",
  "auth.identifier": "E-Mail oder Benutzername",
  "auth.login": "Anmelden",
  "auth.login_button": "Anmelden",
  "auth.login_title": "Anmelden",
  "auth.new_password": "Neues Passwort",
  "auth.new_email_label": "Neue E-Mail",
  "auth.old_password": "Altes Passwort",
  "auth.password": "Passwort",
  "auth.password_changed_success": "Passwort wurde erfolgreich geaendert.",
  "auth.register": "Konto erstellen",
  "auth.register_button": "Konto erstellen",
  "auth.register_title": "Registrieren",
  "auth.reset_email_body": "Nutze diesen Link zum Zuruecksetzen deines Passworts: {reset_link}",
  "auth.reset_email_subject": "MealMate Passwort-Reset",
  "auth.reset_password_button": "Passwort zuruecksetzen",
  "auth.reset_password_title": "Passwort zuruecksetzen",
  "auth.reset_success": "Passwort wurde zurueckgesetzt, bitte neu anmelden.",
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
  "error.image_change_file_missing": "Zu diesem Antrag wurde keine Bilddatei gefunden.",
  "error.image_change_request_not_found": "Bildaenderungsantrag nicht gefunden.",
  "error.image_change_request_not_pending": "Dieser Bildaenderungsantrag ist nicht mehr ausstehend.",
  "error.email_change_token_invalid": "Link ungueltig oder abgelaufen. Bitte erneut anfordern.",
  "error.email_invalid": "Bitte gib eine gueltige E-Mail-Adresse ein.",
  "error.email_unavailable": "Diese E-Mail ist nicht verfuegbar.",
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
  "error.password_confirm_mismatch": "Passwort und Bestaetigung stimmen nicht ueberein.",
  "error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",
  "error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",
  "error.password_old_invalid": "Das alte Passwort ist ungueltig.",
  "error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",
  "error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",
  "error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",
  "error.recipe_not_found": "Rezept nicht gefunden.",
  "error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",
  "error.reset_token_invalid": "Der Reset-Link ist ungueltig oder abgelaufen.",
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
  "error.username_invalid": "Benutzername muss 3-30 Zeichen haben und darf nur a-z, A-Z, 0-9, Punkt, Unterstrich oder Bindestrich enthalten.",
  "error.username_taken": "Dieser Benutzername ist bereits vergeben.",
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
  "images.admin_use_direct_upload": "Admins nutzen den direkten Bild-Upload fuer Rezepte.",
  "images.delete": "Loeschen",
  "images.empty": "Noch keine Bilder vorhanden.",
  "images.login_to_propose": "Bitte anmelden, um ein Bild vorzuschlagen.",
  "images.new_file": "Neue Bilddatei",
  "images.pending_badge": "Bildvorschlag ausstehend",
  "images.placeholder": "Kein Bild vorhanden",
  "images.plus_title": "Bild hinzufuegen",
  "images.primary": "Hauptbild",
  "images.propose_change": "Bildaenderung vorschlagen",
  "images.request_submitted": "Danke, Bildaenderung wurde zur Pruefung eingereicht.",
  "images.set_primary": "Als Hauptbild setzen",
  "images.title": "Bilder",
  "images.upload": "Bild hochladen",
  "images.uploaded": "Bild wurde hochgeladen.",
  "images.user_change_note": "Als Nutzer wird die Bildaenderung erst nach Admin-Freigabe sichtbar.",
  "image_change.admin_empty": "Keine Bildaenderungen in der Warteschlange.",
  "image_change.admin_title": "Bildaenderungen (Pruefung)",
  "image_change.approved": "Bildaenderung wurde freigegeben.",
  "image_change.compare_title": "Bildvergleich",
  "image_change.current_image": "Aktuelles Bild",
  "image_change.detail_title": "Bildaenderungsantrag",
  "image_change.open_queue": "Bildaenderungen oeffnen",
  "image_change.pending_count": "Ausstehende Antraege: {count}",
  "image_change.proposed_image": "Vorgeschlagenes Bild",
  "image_change.rejected": "Bildaenderung wurde abgelehnt.",
  "image_change.review_done": "Diese Bildaenderung wurde bereits entschieden.",
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
  "profile.user_uid": "Deine Nutzer-ID",
  "profile.username": "Benutzername",
  "profile.username_change_title": "Benutzername aendern",
  "profile.username_save": "Benutzernamen speichern",
  "profile.username_updated": "Benutzername wurde aktualisiert.",
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

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '{'.
2. Diese Zeile enthält den Code '"admin.action": "Aktion",'.
3. Diese Zeile enthält den Code '"admin.category_distinct_count": "Anzahl eindeutiger Kategorien",'.
4. Diese Zeile enthält den Code '"admin.category_stats_title": "Kategorien-Status",'.
5. Diese Zeile enthält den Code '"admin.category_top": "Top 10 Kategorien",'.
6. Diese Zeile enthält den Code '"admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortsetzen', um d...'.
7. Diese Zeile enthält den Code '"admin.creator": "Ersteller",'.
8. Diese Zeile enthält den Code '"admin.csv_path": "CSV-Pfad",'.
9. Diese Zeile enthält den Code '"admin.download_example": "CSV Beispiel herunterladen",'.
10. Diese Zeile enthält den Code '"admin.download_template": "CSV Template herunterladen",'.
11. Diese Zeile enthält den Code '"admin.dry_run": "Nur pruefen (Dry Run)",'.
12. Diese Zeile enthält den Code '"admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",'.
13. Diese Zeile enthält den Code '"admin.email": "E-Mail",'.
14. Diese Zeile enthält den Code '"admin.force_with_warnings": "Trotz Warnungen fortsetzen",'.
15. Diese Zeile enthält den Code '"admin.id": "ID",'.
16. Diese Zeile enthält den Code '"admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften Zeilen.",'.
17. Diese Zeile enthält den Code '"admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",'.
18. Diese Zeile enthält den Code '"admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' (',' als F...'.
19. Diese Zeile enthält den Code '"admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import stabil und ...'.
20. Diese Zeile enthält den Code '"admin.import_help_title": "CSV-Format Hilfe",'.
21. Diese Zeile enthält den Code '"admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise Salz oder...'.
22. Diese Zeile enthält den Code '"admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty, prep_tim...'.
23. Diese Zeile enthält den Code '"admin.import_required_columns": "Pflichtspalten: title, instructions",'.
24. Diese Zeile enthält den Code '"admin.import_result_title": "Import-Ergebnis",'.
25. Diese Zeile enthält den Code '"admin.import_title": "CSV manuell importieren",'.
26. Diese Zeile enthält den Code '"admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren, wenn bewu...'.
27. Diese Zeile enthält den Code '"admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",'.
28. Diese Zeile enthält den Code '"admin.preview_button": "Vorschau erstellen",'.
29. Diese Zeile enthält den Code '"admin.preview_delimiter": "Erkannter Delimiter",'.
30. Diese Zeile enthält den Code '"admin.preview_done": "Vorschau wurde erstellt.",'.
31. Diese Zeile enthält den Code '"admin.preview_errors_title": "Fehlerliste",'.
32. Diese Zeile enthält den Code '"admin.preview_fatal_rows": "Zeilen mit Fehlern",'.
33. Diese Zeile enthält den Code '"admin.preview_notes": "Hinweise",'.
34. Diese Zeile enthält den Code '"admin.preview_row": "Zeile",'.
35. Diese Zeile enthält den Code '"admin.preview_status": "Status",'.
36. Diese Zeile enthält den Code '"admin.preview_title": "Import-Vorschau",'.
37. Diese Zeile enthält den Code '"admin.preview_total_rows": "Gesamtzeilen",'.
38. Diese Zeile enthält den Code '"admin.preview_warnings_title": "Warnungsliste",'.
39. Diese Zeile enthält den Code '"admin.recipes": "Rezepte",'.
40. Diese Zeile enthält den Code '"admin.report_errors": "Fehler",'.
41. Diese Zeile enthält den Code '"admin.report_inserted": "Neu",'.
42. Diese Zeile enthält den Code '"admin.report_skipped": "Uebersprungen",'.
43. Diese Zeile enthält den Code '"admin.report_updated": "Aktualisiert",'.
44. Diese Zeile enthält den Code '"admin.report_warnings": "Warnungen",'.
45. Diese Zeile enthält den Code '"admin.role": "Rolle",'.
46. Diese Zeile enthält den Code '"admin.save": "Speichern",'.
47. Diese Zeile enthält den Code '"admin.seed_done": "Seed-Status: bereits ausgefuehrt.",'.
48. Diese Zeile enthält den Code '"admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",'.
49. Diese Zeile enthält den Code '"admin.seed_title": "KochWiki-Seed (einmalig)",'.
50. Diese Zeile enthält den Code '"admin.source": "Quelle",'.
51. Diese Zeile enthält den Code '"admin.start_import": "Import starten",'.
52. Diese Zeile enthält den Code '"admin.title": "Admin-Bereich",'.
53. Diese Zeile enthält den Code '"admin.title_column": "Titel",'.
54. Diese Zeile enthält den Code '"admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",'.
55. Diese Zeile enthält den Code '"admin.upload_label": "CSV-Upload",'.
56. Diese Zeile enthält den Code '"admin.users": "Nutzer",'.
57. Diese Zeile enthält den Code '"app.name": "MealMate",'.
58. Diese Zeile enthält den Code '"auth.change_password_button": "Passwort aktualisieren",'.
59. Diese Zeile enthält den Code '"auth.change_password_title": "Passwort aendern",'.
60. Diese Zeile enthält den Code '"auth.change_email_confirm_button": "E-Mail jetzt aktualisieren",'.
61. Diese Zeile enthält den Code '"auth.change_email_confirm_hint": "Du bestaetigst die neue E-Mail-Adresse: {email}",'.
62. Diese Zeile enthält den Code '"auth.change_email_confirm_title": "E-Mail-Aenderung bestaetigen",'.
63. Diese Zeile enthält den Code '"auth.change_email_current": "Aktuelle E-Mail: {email}",'.
64. Diese Zeile enthält den Code '"auth.change_email_open_link": "E-Mail-Adresse aendern",'.
65. Diese Zeile enthält den Code '"auth.change_email_request_button": "Bestaetigungslink senden",'.
66. Diese Zeile enthält den Code '"auth.change_email_requested": "Bitte pruefe deine neue E-Mail und bestaetige den Link.",'.
67. Diese Zeile enthält den Code '"auth.change_email_reissue_hint": "Wenn der Link abgelaufen ist, fordere bitte einen neuen Link a...'.
68. Diese Zeile enthält den Code '"auth.change_email_retry_link": "Neue E-Mail-Aenderung anfordern",'.
69. Diese Zeile enthält den Code '"auth.change_email_title": "E-Mail aendern",'.
70. Diese Zeile enthält den Code '"auth.confirm_password": "Passwort bestaetigen",'.
71. Diese Zeile enthält den Code '"auth.email": "E-Mail",'.
72. Diese Zeile enthält den Code '"auth.email_change_body": "Bitte bestaetige deine neue E-Mail-Adresse mit diesem Link: {confirm_l...'.
73. Diese Zeile enthält den Code '"auth.email_change_same_email": "Die neue E-Mail entspricht bereits deiner aktuellen Adresse.",'.
74. Diese Zeile enthält den Code '"auth.email_change_subject": "MealMate E-Mail-Aenderung bestaetigen",'.
75. Diese Zeile enthält den Code '"auth.email_change_success": "E-Mail wurde erfolgreich aktualisiert.",'.
76. Diese Zeile enthält den Code '"auth.forgot_generic_response": "Wenn der Account existiert, wurde eine E-Mail gesendet.",'.
77. Diese Zeile enthält den Code '"auth.forgot_password_button": "Reset-Link anfordern",'.
78. Diese Zeile enthält den Code '"auth.forgot_password_hint": "Gib deine E-Mail oder deinen Benutzernamen ein, um einen Reset-Link...'.
79. Diese Zeile enthält den Code '"auth.forgot_password_link": "Passwort vergessen?",'.
80. Diese Zeile enthält den Code '"auth.forgot_password_title": "Passwort vergessen",'.
81. Diese Zeile enthält den Code '"auth.identifier": "E-Mail oder Benutzername",'.
82. Diese Zeile enthält den Code '"auth.login": "Anmelden",'.
83. Diese Zeile enthält den Code '"auth.login_button": "Anmelden",'.
84. Diese Zeile enthält den Code '"auth.login_title": "Anmelden",'.
85. Diese Zeile enthält den Code '"auth.new_password": "Neues Passwort",'.
86. Diese Zeile enthält den Code '"auth.new_email_label": "Neue E-Mail",'.
87. Diese Zeile enthält den Code '"auth.old_password": "Altes Passwort",'.
88. Diese Zeile enthält den Code '"auth.password": "Passwort",'.
89. Diese Zeile enthält den Code '"auth.password_changed_success": "Passwort wurde erfolgreich geaendert.",'.
90. Diese Zeile enthält den Code '"auth.register": "Konto erstellen",'.
91. Diese Zeile enthält den Code '"auth.register_button": "Konto erstellen",'.
92. Diese Zeile enthält den Code '"auth.register_title": "Registrieren",'.
93. Diese Zeile enthält den Code '"auth.reset_email_body": "Nutze diesen Link zum Zuruecksetzen deines Passworts: {reset_link}",'.
94. Diese Zeile enthält den Code '"auth.reset_email_subject": "MealMate Passwort-Reset",'.
95. Diese Zeile enthält den Code '"auth.reset_password_button": "Passwort zuruecksetzen",'.
96. Diese Zeile enthält den Code '"auth.reset_password_title": "Passwort zuruecksetzen",'.
97. Diese Zeile enthält den Code '"auth.reset_success": "Passwort wurde zurueckgesetzt, bitte neu anmelden.",'.
98. Diese Zeile enthält den Code '"difficulty.easy": "Einfach",'.
99. Diese Zeile enthält den Code '"difficulty.hard": "Schwer",'.
100. Diese Zeile enthält den Code '"difficulty.medium": "Mittel",'.
101. Diese Zeile enthält den Code '"discover.filter.apply": "Anwenden",'.
102. Diese Zeile enthält den Code '"discover.filter.category": "Kategorie",'.
103. Diese Zeile enthält den Code '"discover.filter.difficulty": "Schwierigkeit",'.
104. Diese Zeile enthält den Code '"discover.filter.ingredient": "Zutat",'.
105. Diese Zeile enthält den Code '"discover.filter.title_contains": "Titel enthaelt",'.
106. Diese Zeile enthält den Code '"discover.sort.newest": "Neueste",'.
107. Diese Zeile enthält den Code '"discover.sort.oldest": "Aelteste",'.
108. Diese Zeile enthält den Code '"discover.sort.prep_time": "Zubereitungszeit",'.
109. Diese Zeile enthält den Code '"discover.sort.rating_asc": "Schlechteste Bewertung",'.
110. Diese Zeile enthält den Code '"discover.sort.rating_desc": "Beste Bewertung",'.
111. Diese Zeile enthält den Code '"discover.title": "Rezepte entdecken",'.
112. Diese Zeile enthält den Code '"empty.no_recipes": "Keine Rezepte gefunden.",'.
113. Diese Zeile enthält den Code '"error.404_text": "Die angeforderte Seite existiert nicht oder wurde verschoben.",'.
114. Diese Zeile enthält den Code '"error.404_title": "404 - Seite nicht gefunden",'.
115. Diese Zeile enthält den Code '"error.500_text": "Beim Verarbeiten der Anfrage ist ein unerwarteter Fehler aufgetreten.",'.
116. Diese Zeile enthält den Code '"error.500_title": "500 - Interner Fehler",'.
117. Diese Zeile enthält den Code '"error.admin_required": "Administratorrechte erforderlich.",'.
118. Diese Zeile enthält den Code '"error.auth_required": "Anmeldung erforderlich.",'.
119. Diese Zeile enthält den Code '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
120. Diese Zeile enthält den Code '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
121. Diese Zeile enthält den Code '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
122. Diese Zeile enthält den Code '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
123. Diese Zeile enthält den Code '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
124. Diese Zeile enthält den Code '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
125. Diese Zeile enthält den Code '"error.email_registered": "Diese E-Mail ist bereits registriert.",'.
126. Diese Zeile enthält den Code '"error.image_change_file_missing": "Zu diesem Antrag wurde keine Bilddatei gefunden.",'.
127. Diese Zeile enthält den Code '"error.image_change_request_not_found": "Bildaenderungsantrag nicht gefunden.",'.
128. Diese Zeile enthält den Code '"error.image_change_request_not_pending": "Dieser Bildaenderungsantrag ist nicht mehr ausstehend.",'.
129. Diese Zeile enthält den Code '"error.email_change_token_invalid": "Link ungueltig oder abgelaufen. Bitte erneut anfordern.",'.
130. Diese Zeile enthält den Code '"error.email_invalid": "Bitte gib eine gueltige E-Mail-Adresse ein.",'.
131. Diese Zeile enthält den Code '"error.email_unavailable": "Diese E-Mail ist nicht verfuegbar.",'.
132. Diese Zeile enthält den Code '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
133. Diese Zeile enthält den Code '"error.field_positive": "{field} muss groesser als null sein.",'.
134. Diese Zeile enthält den Code '"error.home_link": "Zur Startseite",'.
135. Diese Zeile enthält den Code '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
136. Diese Zeile enthält den Code '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
137. Diese Zeile enthält den Code '"error.image_not_found": "Bild nicht gefunden.",'.
138. Diese Zeile enthält den Code '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
139. Diese Zeile enthält den Code '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
140. Diese Zeile enthält den Code '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
141. Diese Zeile enthält den Code '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
142. Diese Zeile enthält den Code '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
143. Diese Zeile enthält den Code '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",'.
144. Diese Zeile enthält den Code '"error.internal": "Interner Serverfehler.",'.
145. Diese Zeile enthält den Code '"error.invalid_credentials": "Ungueltige Zugangsdaten.",'.
146. Diese Zeile enthält den Code '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
147. Diese Zeile enthält den Code '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
148. Diese Zeile enthält den Code '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
149. Diese Zeile enthält den Code '"error.not_found": "Ressource nicht gefunden.",'.
150. Diese Zeile enthält den Code '"error.password_confirm_mismatch": "Passwort und Bestaetigung stimmen nicht ueberein.",'.
151. Diese Zeile enthält den Code '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
152. Diese Zeile enthält den Code '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
153. Diese Zeile enthält den Code '"error.password_old_invalid": "Das alte Passwort ist ungueltig.",'.
154. Diese Zeile enthält den Code '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
155. Diese Zeile enthält den Code '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
156. Diese Zeile enthält den Code '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
157. Diese Zeile enthält den Code '"error.recipe_not_found": "Rezept nicht gefunden.",'.
158. Diese Zeile enthält den Code '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
159. Diese Zeile enthält den Code '"error.reset_token_invalid": "Der Reset-Link ist ungueltig oder abgelaufen.",'.
160. Diese Zeile enthält den Code '"error.review_not_found": "Bewertung nicht gefunden.",'.
161. Diese Zeile enthält den Code '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
162. Diese Zeile enthält den Code '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
163. Diese Zeile enthält den Code '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
164. Diese Zeile enthält den Code '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",'.
165. Diese Zeile enthält den Code '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
166. Diese Zeile enthält den Code '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
167. Diese Zeile enthält den Code '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
168. Diese Zeile enthält den Code '"error.submission_not_found": "Einreichung nicht gefunden.",'.
169. Diese Zeile enthält den Code '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
170. Diese Zeile enthält den Code '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
171. Diese Zeile enthält den Code '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
172. Diese Zeile enthält den Code '"error.trace": "Stacktrace (nur Dev)",'.
173. Diese Zeile enthält den Code '"error.user_not_found": "Nutzer nicht gefunden.",'.
174. Diese Zeile enthält den Code '"error.username_invalid": "Benutzername muss 3-30 Zeichen haben und darf nur a-z, A-Z, 0-9, Punkt...'.
175. Diese Zeile enthält den Code '"error.username_taken": "Dieser Benutzername ist bereits vergeben.",'.
176. Diese Zeile enthält den Code '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
177. Diese Zeile enthält den Code '"favorite.add": "Zu Favoriten",'.
178. Diese Zeile enthält den Code '"favorite.remove": "Aus Favoriten entfernen",'.
179. Diese Zeile enthält den Code '"favorites.empty": "Keine Favoriten gespeichert.",'.
180. Diese Zeile enthält den Code '"favorites.remove": "Favorit entfernen",'.
181. Diese Zeile enthält den Code '"favorites.title": "Favoriten",'.
182. Diese Zeile enthält den Code '"home.all_categories": "Alle Kategorien",'.
183. Diese Zeile enthält den Code '"home.apply": "Anwenden",'.
184. Diese Zeile enthält den Code '"home.category": "Kategorie",'.
185. Diese Zeile enthält den Code '"home.difficulty": "Schwierigkeit",'.
186. Diese Zeile enthält den Code '"home.ingredient": "Zutat",'.
187. Diese Zeile enthält den Code '"home.per_page": "Pro Seite",'.
188. Diese Zeile enthält den Code '"home.title": "Rezepte entdecken",'.
189. Diese Zeile enthält den Code '"home.title_contains": "Titel enthaelt",'.
190. Diese Zeile enthält den Code '"images.admin_use_direct_upload": "Admins nutzen den direkten Bild-Upload fuer Rezepte.",'.
191. Diese Zeile enthält den Code '"images.delete": "Loeschen",'.
192. Diese Zeile enthält den Code '"images.empty": "Noch keine Bilder vorhanden.",'.
193. Diese Zeile enthält den Code '"images.login_to_propose": "Bitte anmelden, um ein Bild vorzuschlagen.",'.
194. Diese Zeile enthält den Code '"images.new_file": "Neue Bilddatei",'.
195. Diese Zeile enthält den Code '"images.pending_badge": "Bildvorschlag ausstehend",'.
196. Diese Zeile enthält den Code '"images.placeholder": "Kein Bild vorhanden",'.
197. Diese Zeile enthält den Code '"images.plus_title": "Bild hinzufuegen",'.
198. Diese Zeile enthält den Code '"images.primary": "Hauptbild",'.
199. Diese Zeile enthält den Code '"images.propose_change": "Bildaenderung vorschlagen",'.
200. Diese Zeile enthält den Code '"images.request_submitted": "Danke, Bildaenderung wurde zur Pruefung eingereicht.",'.
201. Diese Zeile enthält den Code '"images.set_primary": "Als Hauptbild setzen",'.
202. Diese Zeile enthält den Code '"images.title": "Bilder",'.
203. Diese Zeile enthält den Code '"images.upload": "Bild hochladen",'.
204. Diese Zeile enthält den Code '"images.uploaded": "Bild wurde hochgeladen.",'.
205. Diese Zeile enthält den Code '"images.user_change_note": "Als Nutzer wird die Bildaenderung erst nach Admin-Freigabe sichtbar.",'.
206. Diese Zeile enthält den Code '"image_change.admin_empty": "Keine Bildaenderungen in der Warteschlange.",'.
207. Diese Zeile enthält den Code '"image_change.admin_title": "Bildaenderungen (Pruefung)",'.
208. Diese Zeile enthält den Code '"image_change.approved": "Bildaenderung wurde freigegeben.",'.
209. Diese Zeile enthält den Code '"image_change.compare_title": "Bildvergleich",'.
210. Diese Zeile enthält den Code '"image_change.current_image": "Aktuelles Bild",'.
211. Diese Zeile enthält den Code '"image_change.detail_title": "Bildaenderungsantrag",'.
212. Diese Zeile enthält den Code '"image_change.open_queue": "Bildaenderungen oeffnen",'.
213. Diese Zeile enthält den Code '"image_change.pending_count": "Ausstehende Antraege: {count}",'.
214. Diese Zeile enthält den Code '"image_change.proposed_image": "Vorgeschlagenes Bild",'.
215. Diese Zeile enthält den Code '"image_change.rejected": "Bildaenderung wurde abgelehnt.",'.
216. Diese Zeile enthält den Code '"image_change.review_done": "Diese Bildaenderung wurde bereits entschieden.",'.
217. Diese Zeile enthält den Code '"moderation.approve": "Freigeben",'.
218. Diese Zeile enthält den Code '"moderation.pending": "Ausstehend",'.
219. Diese Zeile enthält den Code '"moderation.reject": "Ablehnen",'.
220. Diese Zeile enthält den Code '"moderation.title": "Moderations-Warteschlange",'.
221. Diese Zeile enthält den Code '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
222. Diese Zeile enthält den Code '"my_recipes.title": "Meine Rezepte",'.
223. Diese Zeile enthält den Code '"nav.admin": "Admin",'.
224. Diese Zeile enthält den Code '"nav.admin_submissions": "Moderation",'.
225. Diese Zeile enthält den Code '"nav.create_recipe": "Rezept erstellen",'.
226. Diese Zeile enthält den Code '"nav.discover": "Rezepte entdecken",'.
227. Diese Zeile enthält den Code '"nav.favorites": "Favoriten",'.
228. Diese Zeile enthält den Code '"nav.language": "Sprache",'.
229. Diese Zeile enthält den Code '"nav.login": "Anmelden",'.
230. Diese Zeile enthält den Code '"nav.logout": "Abmelden",'.
231. Diese Zeile enthält den Code '"nav.my_recipes": "Meine Rezepte",'.
232. Diese Zeile enthält den Code '"nav.my_submissions": "Meine Einreichungen",'.
233. Diese Zeile enthält den Code '"nav.profile": "Mein Profil",'.
234. Diese Zeile enthält den Code '"nav.publish_recipe": "Rezept veroeffentlichen",'.
235. Diese Zeile enthält den Code '"nav.register": "Registrieren",'.
236. Diese Zeile enthält den Code '"nav.submit": "Rezept einreichen",'.
237. Diese Zeile enthält den Code '"nav.submit_recipe": "Rezept einreichen",'.
238. Diese Zeile enthält den Code '"pagination.first": "Erste",'.
239. Diese Zeile enthält den Code '"pagination.last": "Letzte",'.
240. Diese Zeile enthält den Code '"pagination.next": "Weiter",'.
241. Diese Zeile enthält den Code '"pagination.page": "Seite",'.
242. Diese Zeile enthält den Code '"pagination.prev": "Zurueck",'.
243. Diese Zeile enthält den Code '"pagination.previous": "Zurueck",'.
244. Diese Zeile enthält den Code '"pagination.results_range": "Zeige {start}-{end} von {total} Rezepten",'.
245. Diese Zeile enthält den Code '"profile.email": "E-Mail",'.
246. Diese Zeile enthält den Code '"profile.joined": "Registriert am",'.
247. Diese Zeile enthält den Code '"profile.role": "Rolle",'.
248. Diese Zeile enthält den Code '"profile.title": "Mein Profil",'.
249. Diese Zeile enthält den Code '"profile.user_uid": "Deine Nutzer-ID",'.
250. Diese Zeile enthält den Code '"profile.username": "Benutzername",'.
251. Diese Zeile enthält den Code '"profile.username_change_title": "Benutzername aendern",'.
252. Diese Zeile enthält den Code '"profile.username_save": "Benutzernamen speichern",'.
253. Diese Zeile enthält den Code '"profile.username_updated": "Benutzername wurde aktualisiert.",'.
254. Diese Zeile enthält den Code '"recipe.average_rating": "Durchschnittliche Bewertung",'.
255. Diese Zeile enthält den Code '"recipe.comment": "Kommentar",'.
256. Diese Zeile enthält den Code '"recipe.delete": "Loeschen",'.
257. Diese Zeile enthält den Code '"recipe.edit": "Bearbeiten",'.
258. Diese Zeile enthält den Code '"recipe.ingredients": "Zutaten",'.
259. Diese Zeile enthält den Code '"recipe.instructions": "Anleitung",'.
260. Diese Zeile enthält den Code '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
261. Diese Zeile enthält den Code '"recipe.no_results": "Keine Rezepte gefunden.",'.
262. Diese Zeile enthält den Code '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
263. Diese Zeile enthält den Code '"recipe.pdf_download": "PDF herunterladen",'.
264. Diese Zeile enthält den Code '"recipe.rating": "Bewertung",'.
265. Diese Zeile enthält den Code '"recipe.rating_short": "Bewertung",'.
266. Diese Zeile enthält den Code '"recipe.review_count_label": "Bewertungen",'.
267. Diese Zeile enthält den Code '"recipe.reviews": "Bewertungen",'.
268. Diese Zeile enthält den Code '"recipe.save_review": "Bewertung speichern",'.
269. Diese Zeile enthält den Code '"recipe_form.category": "Kategorie",'.
270. Diese Zeile enthält den Code '"recipe_form.create": "Erstellen",'.
271. Diese Zeile enthält den Code '"recipe_form.create_title": "Rezept veroeffentlichen",'.
272. Diese Zeile enthält den Code '"recipe_form.description": "Beschreibung",'.
273. Diese Zeile enthält den Code '"recipe_form.difficulty": "Schwierigkeit",'.
274. Diese Zeile enthält den Code '"recipe_form.edit_title": "Rezept bearbeiten",'.
275. Diese Zeile enthält den Code '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
276. Diese Zeile enthält den Code '"recipe_form.instructions": "Anleitung",'.
277. Diese Zeile enthält den Code '"recipe_form.new_category_label": "Neue Kategorie",'.
278. Diese Zeile enthält den Code '"recipe_form.new_category_option": "Neue Kategorie...",'.
279. Diese Zeile enthält den Code '"recipe_form.optional_image": "Optionales Bild",'.
280. Diese Zeile enthält den Code '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
281. Diese Zeile enthält den Code '"recipe_form.save": "Speichern",'.
282. Diese Zeile enthält den Code '"recipe_form.title": "Titel",'.
283. Diese Zeile enthält den Code '"recipe_form.title_image_url": "Titelbild-URL",'.
284. Diese Zeile enthält den Code '"role.admin": "Administrator",'.
285. Diese Zeile enthält den Code '"role.user": "Nutzer",'.
286. Diese Zeile enthält den Code '"sort.highest_rated": "Beste Bewertung",'.
287. Diese Zeile enthält den Code '"sort.lowest_rated": "Schlechteste Bewertung",'.
288. Diese Zeile enthält den Code '"sort.newest": "Neueste",'.
289. Diese Zeile enthält den Code '"sort.oldest": "Aelteste",'.
290. Diese Zeile enthält den Code '"sort.prep_time": "Zubereitungszeit",'.
291. Diese Zeile enthält den Code '"submission.admin_detail_title": "Einreichung",'.
292. Diese Zeile enthält den Code '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
293. Diese Zeile enthält den Code '"submission.admin_note": "Admin-Notiz",'.
294. Diese Zeile enthält den Code '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
295. Diese Zeile enthält den Code '"submission.admin_queue_title": "Moderations-Warteschlange",'.
296. Diese Zeile enthält den Code '"submission.approve_button": "Freigeben",'.
297. Diese Zeile enthält den Code '"submission.approved": "Einreichung wurde freigegeben.",'.
298. Diese Zeile enthält den Code '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
299. Diese Zeile enthält den Code '"submission.category": "Kategorie",'.
300. Diese Zeile enthält den Code '"submission.default_description": "Rezept-Einreichung",'.
301. Diese Zeile enthält den Code '"submission.description": "Beschreibung",'.
302. Diese Zeile enthält den Code '"submission.difficulty": "Schwierigkeit",'.
303. Diese Zeile enthält den Code '"submission.edit_submission": "Einreichung bearbeiten",'.
304. Diese Zeile enthält den Code '"submission.guest": "Gast",'.
305. Diese Zeile enthält den Code '"submission.image_deleted": "Bild wurde entfernt.",'.
306. Diese Zeile enthält den Code '"submission.image_optional": "Optionales Bild",'.
307. Diese Zeile enthält den Code '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
308. Diese Zeile enthält den Code '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
309. Diese Zeile enthält den Code '"submission.instructions": "Anleitung",'.
310. Diese Zeile enthält den Code '"submission.moderation_actions": "Moderations-Aktionen",'.
311. Diese Zeile enthält den Code '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
312. Diese Zeile enthält den Code '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",'.
313. Diese Zeile enthält den Code '"submission.my_title": "Meine Einreichungen",'.
314. Diese Zeile enthält den Code '"submission.new_category_label": "Neue Kategorie",'.
315. Diese Zeile enthält den Code '"submission.new_category_option": "Neue Kategorie...",'.
316. Diese Zeile enthält den Code '"submission.open_detail": "Details",'.
317. Diese Zeile enthält den Code '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
318. Diese Zeile enthält den Code '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
319. Diese Zeile enthält den Code '"submission.preview": "Vorschau",'.
320. Diese Zeile enthält den Code '"submission.reject_button": "Ablehnen",'.
321. Diese Zeile enthält den Code '"submission.reject_reason": "Ablehnungsgrund",'.
322. Diese Zeile enthält den Code '"submission.rejected": "Einreichung wurde abgelehnt.",'.
323. Diese Zeile enthält den Code '"submission.save_changes": "Aenderungen speichern",'.
324. Diese Zeile enthält den Code '"submission.servings": "Portionen (optional)",'.
325. Diese Zeile enthält den Code '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
326. Diese Zeile enthält den Code '"submission.stats_approved": "Freigegeben",'.
327. Diese Zeile enthält den Code '"submission.stats_pending": "Ausstehend",'.
328. Diese Zeile enthält den Code '"submission.stats_rejected": "Abgelehnt",'.
329. Diese Zeile enthält den Code '"submission.status_all": "Alle",'.
330. Diese Zeile enthält den Code '"submission.status_approved": "Freigegeben",'.
331. Diese Zeile enthält den Code '"submission.status_filter": "Status",'.
332. Diese Zeile enthält den Code '"submission.status_pending": "Ausstehend",'.
333. Diese Zeile enthält den Code '"submission.status_rejected": "Abgelehnt",'.
334. Diese Zeile enthält den Code '"submission.submit_button": "Zur Pruefung einreichen",'.
335. Diese Zeile enthält den Code '"submission.submit_hint": "Einreichungen werden vor der Veroeffentlichung durch das Admin-Team ge...'.
336. Diese Zeile enthält den Code '"submission.submit_title": "Rezept einreichen",'.
337. Diese Zeile enthält den Code '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
338. Diese Zeile enthält den Code '"submission.table_action": "Aktion",'.
339. Diese Zeile enthält den Code '"submission.table_date": "Datum",'.
340. Diese Zeile enthält den Code '"submission.table_status": "Status",'.
341. Diese Zeile enthält den Code '"submission.table_submitter": "Einreicher",'.
342. Diese Zeile enthält den Code '"submission.table_title": "Titel",'.
343. Diese Zeile enthält den Code '"submission.thank_you": "Vielen Dank! Dein Rezept wurde eingereicht und wird geprueft.",'.
344. Diese Zeile enthält den Code '"submission.title": "Titel",'.
345. Diese Zeile enthält den Code '"submission.updated": "Einreichung wurde aktualisiert."'.
346. Diese Zeile enthält den Code '}'.

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
  "auth.change_password_button": "Update password",
  "auth.change_password_title": "Change Password",
  "auth.change_email_confirm_button": "Update email now",
  "auth.change_email_confirm_hint": "You are confirming this new email address: {email}",
  "auth.change_email_confirm_title": "Confirm Email Change",
  "auth.change_email_current": "Current email: {email}",
  "auth.change_email_open_link": "Change email address",
  "auth.change_email_request_button": "Send confirmation link",
  "auth.change_email_requested": "Please check your new email and confirm the link.",
  "auth.change_email_reissue_hint": "If this link expired, request a new one.",
  "auth.change_email_retry_link": "Request a new email change",
  "auth.change_email_title": "Change Email",
  "auth.confirm_password": "Confirm password",
  "auth.email": "Email",
  "auth.email_change_body": "Please confirm your new email address with this link: {confirm_link}",
  "auth.email_change_same_email": "The new email already matches your current address.",
  "auth.email_change_subject": "Confirm your MealMate email change",
  "auth.email_change_success": "Email was updated successfully.",
  "auth.forgot_generic_response": "If the account exists, an email has been sent.",
  "auth.forgot_password_button": "Request reset link",
  "auth.forgot_password_hint": "Enter your email or username to receive a reset link.",
  "auth.forgot_password_link": "Forgot password?",
  "auth.forgot_password_title": "Forgot Password",
  "auth.identifier": "Email or username",
  "auth.login": "Login",
  "auth.login_button": "Login",
  "auth.login_title": "Login",
  "auth.new_password": "New password",
  "auth.new_email_label": "New email",
  "auth.old_password": "Current password",
  "auth.password": "Password",
  "auth.password_changed_success": "Password was changed successfully.",
  "auth.register": "Register",
  "auth.register_button": "Create account",
  "auth.register_title": "Register",
  "auth.reset_email_body": "Use this link to reset your password: {reset_link}",
  "auth.reset_email_subject": "MealMate Password Reset",
  "auth.reset_password_button": "Reset password",
  "auth.reset_password_title": "Reset Password",
  "auth.reset_success": "Password was reset, please sign in again.",
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
  "error.image_change_file_missing": "No image file was found for this request.",
  "error.image_change_request_not_found": "Image change request not found.",
  "error.image_change_request_not_pending": "This image change request is no longer pending.",
  "error.email_change_token_invalid": "This link is invalid or expired. Please request a new one.",
  "error.email_invalid": "Please enter a valid email address.",
  "error.email_unavailable": "This email is not available.",
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
  "error.password_confirm_mismatch": "Password and confirmation do not match.",
  "error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",
  "error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",
  "error.password_old_invalid": "Current password is invalid.",
  "error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",
  "error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",
  "error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",
  "error.recipe_not_found": "Rezept nicht gefunden.",
  "error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",
  "error.reset_token_invalid": "Reset link is invalid or expired.",
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
  "error.username_invalid": "Username must be 3-30 characters and may only contain letters, numbers, dot, underscore or hyphen.",
  "error.username_taken": "This username is already taken.",
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
  "images.admin_use_direct_upload": "Admins should use direct recipe image upload.",
  "images.delete": "Delete",
  "images.empty": "No images uploaded yet.",
  "images.login_to_propose": "Please sign in to suggest an image.",
  "images.new_file": "New image file",
  "images.pending_badge": "Image suggestion pending",
  "images.placeholder": "No image available",
  "images.plus_title": "Add image",
  "images.primary": "Primary image",
  "images.propose_change": "Suggest image change",
  "images.request_submitted": "Thanks, your image change request was submitted for review.",
  "images.set_primary": "Set as primary",
  "images.title": "Images",
  "images.upload": "Upload image",
  "images.uploaded": "Image uploaded successfully.",
  "images.user_change_note": "As a user, image changes go live only after admin approval.",
  "image_change.admin_empty": "No image change requests found.",
  "image_change.admin_title": "Image Changes (Review)",
  "image_change.approved": "Image change request approved.",
  "image_change.compare_title": "Image comparison",
  "image_change.current_image": "Current image",
  "image_change.detail_title": "Image change request",
  "image_change.open_queue": "Open image change queue",
  "image_change.pending_count": "Pending requests: {count}",
  "image_change.proposed_image": "Proposed image",
  "image_change.rejected": "Image change request rejected.",
  "image_change.review_done": "This image change request has already been reviewed.",
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
  "profile.user_uid": "Your user ID",
  "profile.username": "Username",
  "profile.username_change_title": "Change username",
  "profile.username_save": "Save username",
  "profile.username_updated": "Username was updated.",
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

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '{'.
2. Diese Zeile enthält den Code '"admin.action": "Aktion",'.
3. Diese Zeile enthält den Code '"admin.category_distinct_count": "Anzahl eindeutiger Kategorien",'.
4. Diese Zeile enthält den Code '"admin.category_stats_title": "Kategorien-Status",'.
5. Diese Zeile enthält den Code '"admin.category_top": "Top 10 Kategorien",'.
6. Diese Zeile enthält den Code '"admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortsetzen', um d...'.
7. Diese Zeile enthält den Code '"admin.creator": "Ersteller",'.
8. Diese Zeile enthält den Code '"admin.csv_path": "CSV-Pfad",'.
9. Diese Zeile enthält den Code '"admin.download_example": "CSV Beispiel herunterladen",'.
10. Diese Zeile enthält den Code '"admin.download_template": "CSV Template herunterladen",'.
11. Diese Zeile enthält den Code '"admin.dry_run": "Nur pruefen (Dry Run)",'.
12. Diese Zeile enthält den Code '"admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",'.
13. Diese Zeile enthält den Code '"admin.email": "E-Mail",'.
14. Diese Zeile enthält den Code '"admin.force_with_warnings": "Trotz Warnungen fortsetzen",'.
15. Diese Zeile enthält den Code '"admin.id": "ID",'.
16. Diese Zeile enthält den Code '"admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften Zeilen.",'.
17. Diese Zeile enthält den Code '"admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",'.
18. Diese Zeile enthält den Code '"admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' (',' als F...'.
19. Diese Zeile enthält den Code '"admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import stabil und ...'.
20. Diese Zeile enthält den Code '"admin.import_help_title": "CSV-Format Hilfe",'.
21. Diese Zeile enthält den Code '"admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise Salz oder...'.
22. Diese Zeile enthält den Code '"admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty, prep_tim...'.
23. Diese Zeile enthält den Code '"admin.import_required_columns": "Pflichtspalten: title, instructions",'.
24. Diese Zeile enthält den Code '"admin.import_result_title": "Import-Ergebnis",'.
25. Diese Zeile enthält den Code '"admin.import_title": "Manual CSV Import",'.
26. Diese Zeile enthält den Code '"admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren, wenn bewu...'.
27. Diese Zeile enthält den Code '"admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",'.
28. Diese Zeile enthält den Code '"admin.preview_button": "Vorschau erstellen",'.
29. Diese Zeile enthält den Code '"admin.preview_delimiter": "Erkannter Delimiter",'.
30. Diese Zeile enthält den Code '"admin.preview_done": "Vorschau wurde erstellt.",'.
31. Diese Zeile enthält den Code '"admin.preview_errors_title": "Fehlerliste",'.
32. Diese Zeile enthält den Code '"admin.preview_fatal_rows": "Zeilen mit Fehlern",'.
33. Diese Zeile enthält den Code '"admin.preview_notes": "Hinweise",'.
34. Diese Zeile enthält den Code '"admin.preview_row": "Zeile",'.
35. Diese Zeile enthält den Code '"admin.preview_status": "Status",'.
36. Diese Zeile enthält den Code '"admin.preview_title": "Import-Vorschau",'.
37. Diese Zeile enthält den Code '"admin.preview_total_rows": "Gesamtzeilen",'.
38. Diese Zeile enthält den Code '"admin.preview_warnings_title": "Warnungsliste",'.
39. Diese Zeile enthält den Code '"admin.recipes": "Rezepte",'.
40. Diese Zeile enthält den Code '"admin.report_errors": "Fehler",'.
41. Diese Zeile enthält den Code '"admin.report_inserted": "Neu",'.
42. Diese Zeile enthält den Code '"admin.report_skipped": "Uebersprungen",'.
43. Diese Zeile enthält den Code '"admin.report_updated": "Aktualisiert",'.
44. Diese Zeile enthält den Code '"admin.report_warnings": "Warnungen",'.
45. Diese Zeile enthält den Code '"admin.role": "Rolle",'.
46. Diese Zeile enthält den Code '"admin.save": "Speichern",'.
47. Diese Zeile enthält den Code '"admin.seed_done": "Seed-Status: bereits ausgefuehrt.",'.
48. Diese Zeile enthält den Code '"admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",'.
49. Diese Zeile enthält den Code '"admin.seed_title": "KochWiki-Seed (einmalig)",'.
50. Diese Zeile enthält den Code '"admin.source": "Quelle",'.
51. Diese Zeile enthält den Code '"admin.start_import": "Import starten",'.
52. Diese Zeile enthält den Code '"admin.title": "Admin Area",'.
53. Diese Zeile enthält den Code '"admin.title_column": "Titel",'.
54. Diese Zeile enthält den Code '"admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",'.
55. Diese Zeile enthält den Code '"admin.upload_label": "CSV-Upload",'.
56. Diese Zeile enthält den Code '"admin.users": "Nutzer",'.
57. Diese Zeile enthält den Code '"app.name": "MealMate",'.
58. Diese Zeile enthält den Code '"auth.change_password_button": "Update password",'.
59. Diese Zeile enthält den Code '"auth.change_password_title": "Change Password",'.
60. Diese Zeile enthält den Code '"auth.change_email_confirm_button": "Update email now",'.
61. Diese Zeile enthält den Code '"auth.change_email_confirm_hint": "You are confirming this new email address: {email}",'.
62. Diese Zeile enthält den Code '"auth.change_email_confirm_title": "Confirm Email Change",'.
63. Diese Zeile enthält den Code '"auth.change_email_current": "Current email: {email}",'.
64. Diese Zeile enthält den Code '"auth.change_email_open_link": "Change email address",'.
65. Diese Zeile enthält den Code '"auth.change_email_request_button": "Send confirmation link",'.
66. Diese Zeile enthält den Code '"auth.change_email_requested": "Please check your new email and confirm the link.",'.
67. Diese Zeile enthält den Code '"auth.change_email_reissue_hint": "If this link expired, request a new one.",'.
68. Diese Zeile enthält den Code '"auth.change_email_retry_link": "Request a new email change",'.
69. Diese Zeile enthält den Code '"auth.change_email_title": "Change Email",'.
70. Diese Zeile enthält den Code '"auth.confirm_password": "Confirm password",'.
71. Diese Zeile enthält den Code '"auth.email": "Email",'.
72. Diese Zeile enthält den Code '"auth.email_change_body": "Please confirm your new email address with this link: {confirm_link}",'.
73. Diese Zeile enthält den Code '"auth.email_change_same_email": "The new email already matches your current address.",'.
74. Diese Zeile enthält den Code '"auth.email_change_subject": "Confirm your MealMate email change",'.
75. Diese Zeile enthält den Code '"auth.email_change_success": "Email was updated successfully.",'.
76. Diese Zeile enthält den Code '"auth.forgot_generic_response": "If the account exists, an email has been sent.",'.
77. Diese Zeile enthält den Code '"auth.forgot_password_button": "Request reset link",'.
78. Diese Zeile enthält den Code '"auth.forgot_password_hint": "Enter your email or username to receive a reset link.",'.
79. Diese Zeile enthält den Code '"auth.forgot_password_link": "Forgot password?",'.
80. Diese Zeile enthält den Code '"auth.forgot_password_title": "Forgot Password",'.
81. Diese Zeile enthält den Code '"auth.identifier": "Email or username",'.
82. Diese Zeile enthält den Code '"auth.login": "Login",'.
83. Diese Zeile enthält den Code '"auth.login_button": "Login",'.
84. Diese Zeile enthält den Code '"auth.login_title": "Login",'.
85. Diese Zeile enthält den Code '"auth.new_password": "New password",'.
86. Diese Zeile enthält den Code '"auth.new_email_label": "New email",'.
87. Diese Zeile enthält den Code '"auth.old_password": "Current password",'.
88. Diese Zeile enthält den Code '"auth.password": "Password",'.
89. Diese Zeile enthält den Code '"auth.password_changed_success": "Password was changed successfully.",'.
90. Diese Zeile enthält den Code '"auth.register": "Register",'.
91. Diese Zeile enthält den Code '"auth.register_button": "Create account",'.
92. Diese Zeile enthält den Code '"auth.register_title": "Register",'.
93. Diese Zeile enthält den Code '"auth.reset_email_body": "Use this link to reset your password: {reset_link}",'.
94. Diese Zeile enthält den Code '"auth.reset_email_subject": "MealMate Password Reset",'.
95. Diese Zeile enthält den Code '"auth.reset_password_button": "Reset password",'.
96. Diese Zeile enthält den Code '"auth.reset_password_title": "Reset Password",'.
97. Diese Zeile enthält den Code '"auth.reset_success": "Password was reset, please sign in again.",'.
98. Diese Zeile enthält den Code '"difficulty.easy": "Easy",'.
99. Diese Zeile enthält den Code '"difficulty.hard": "Hard",'.
100. Diese Zeile enthält den Code '"difficulty.medium": "Medium",'.
101. Diese Zeile enthält den Code '"discover.filter.apply": "Apply",'.
102. Diese Zeile enthält den Code '"discover.filter.category": "Category",'.
103. Diese Zeile enthält den Code '"discover.filter.difficulty": "Difficulty",'.
104. Diese Zeile enthält den Code '"discover.filter.ingredient": "Ingredient",'.
105. Diese Zeile enthält den Code '"discover.filter.title_contains": "Title contains",'.
106. Diese Zeile enthält den Code '"discover.sort.newest": "Newest",'.
107. Diese Zeile enthält den Code '"discover.sort.oldest": "Oldest",'.
108. Diese Zeile enthält den Code '"discover.sort.prep_time": "Prep time",'.
109. Diese Zeile enthält den Code '"discover.sort.rating_asc": "Lowest rated",'.
110. Diese Zeile enthält den Code '"discover.sort.rating_desc": "Highest rated",'.
111. Diese Zeile enthält den Code '"discover.title": "Discover Recipes",'.
112. Diese Zeile enthält den Code '"empty.no_recipes": "No recipes found.",'.
113. Diese Zeile enthält den Code '"error.404_text": "The requested page does not exist or has been moved.",'.
114. Diese Zeile enthält den Code '"error.404_title": "404 - Page Not Found",'.
115. Diese Zeile enthält den Code '"error.500_text": "An unexpected error occurred while processing the request.",'.
116. Diese Zeile enthält den Code '"error.500_title": "500 - Internal Error",'.
117. Diese Zeile enthält den Code '"error.admin_required": "Admin role required.",'.
118. Diese Zeile enthält den Code '"error.auth_required": "Authentication required.",'.
119. Diese Zeile enthält den Code '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
120. Diese Zeile enthält den Code '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
121. Diese Zeile enthält den Code '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
122. Diese Zeile enthält den Code '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
123. Diese Zeile enthält den Code '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
124. Diese Zeile enthält den Code '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
125. Diese Zeile enthält den Code '"error.email_registered": "This email is already registered.",'.
126. Diese Zeile enthält den Code '"error.image_change_file_missing": "No image file was found for this request.",'.
127. Diese Zeile enthält den Code '"error.image_change_request_not_found": "Image change request not found.",'.
128. Diese Zeile enthält den Code '"error.image_change_request_not_pending": "This image change request is no longer pending.",'.
129. Diese Zeile enthält den Code '"error.email_change_token_invalid": "This link is invalid or expired. Please request a new one.",'.
130. Diese Zeile enthält den Code '"error.email_invalid": "Please enter a valid email address.",'.
131. Diese Zeile enthält den Code '"error.email_unavailable": "This email is not available.",'.
132. Diese Zeile enthält den Code '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
133. Diese Zeile enthält den Code '"error.field_positive": "{field} muss groesser als null sein.",'.
134. Diese Zeile enthält den Code '"error.home_link": "Back to Home",'.
135. Diese Zeile enthält den Code '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
136. Diese Zeile enthält den Code '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
137. Diese Zeile enthält den Code '"error.image_not_found": "Bild nicht gefunden.",'.
138. Diese Zeile enthält den Code '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
139. Diese Zeile enthält den Code '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
140. Diese Zeile enthält den Code '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
141. Diese Zeile enthält den Code '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
142. Diese Zeile enthält den Code '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
143. Diese Zeile enthält den Code '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",'.
144. Diese Zeile enthält den Code '"error.internal": "Interner Serverfehler.",'.
145. Diese Zeile enthält den Code '"error.invalid_credentials": "Invalid credentials.",'.
146. Diese Zeile enthält den Code '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
147. Diese Zeile enthält den Code '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
148. Diese Zeile enthält den Code '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
149. Diese Zeile enthält den Code '"error.not_found": "Ressource nicht gefunden.",'.
150. Diese Zeile enthält den Code '"error.password_confirm_mismatch": "Password and confirmation do not match.",'.
151. Diese Zeile enthält den Code '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
152. Diese Zeile enthält den Code '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
153. Diese Zeile enthält den Code '"error.password_old_invalid": "Current password is invalid.",'.
154. Diese Zeile enthält den Code '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
155. Diese Zeile enthält den Code '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
156. Diese Zeile enthält den Code '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
157. Diese Zeile enthält den Code '"error.recipe_not_found": "Rezept nicht gefunden.",'.
158. Diese Zeile enthält den Code '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
159. Diese Zeile enthält den Code '"error.reset_token_invalid": "Reset link is invalid or expired.",'.
160. Diese Zeile enthält den Code '"error.review_not_found": "Bewertung nicht gefunden.",'.
161. Diese Zeile enthält den Code '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
162. Diese Zeile enthält den Code '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
163. Diese Zeile enthält den Code '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
164. Diese Zeile enthält den Code '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",'.
165. Diese Zeile enthält den Code '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
166. Diese Zeile enthält den Code '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
167. Diese Zeile enthält den Code '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
168. Diese Zeile enthält den Code '"error.submission_not_found": "Einreichung nicht gefunden.",'.
169. Diese Zeile enthält den Code '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
170. Diese Zeile enthält den Code '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
171. Diese Zeile enthält den Code '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
172. Diese Zeile enthält den Code '"error.trace": "Stacktrace (nur Dev)",'.
173. Diese Zeile enthält den Code '"error.user_not_found": "Nutzer nicht gefunden.",'.
174. Diese Zeile enthält den Code '"error.username_invalid": "Username must be 3-30 characters and may only contain letters, numbers...'.
175. Diese Zeile enthält den Code '"error.username_taken": "This username is already taken.",'.
176. Diese Zeile enthält den Code '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
177. Diese Zeile enthält den Code '"favorite.add": "Zu Favoriten",'.
178. Diese Zeile enthält den Code '"favorite.remove": "Aus Favoriten entfernen",'.
179. Diese Zeile enthält den Code '"favorites.empty": "Keine Favoriten gespeichert.",'.
180. Diese Zeile enthält den Code '"favorites.remove": "Favorit entfernen",'.
181. Diese Zeile enthält den Code '"favorites.title": "Favoriten",'.
182. Diese Zeile enthält den Code '"home.all_categories": "All categories",'.
183. Diese Zeile enthält den Code '"home.apply": "Apply",'.
184. Diese Zeile enthält den Code '"home.category": "Category",'.
185. Diese Zeile enthält den Code '"home.difficulty": "Difficulty",'.
186. Diese Zeile enthält den Code '"home.ingredient": "Ingredient",'.
187. Diese Zeile enthält den Code '"home.per_page": "Per page",'.
188. Diese Zeile enthält den Code '"home.title": "Discover Recipes",'.
189. Diese Zeile enthält den Code '"home.title_contains": "Title contains",'.
190. Diese Zeile enthält den Code '"images.admin_use_direct_upload": "Admins should use direct recipe image upload.",'.
191. Diese Zeile enthält den Code '"images.delete": "Delete",'.
192. Diese Zeile enthält den Code '"images.empty": "No images uploaded yet.",'.
193. Diese Zeile enthält den Code '"images.login_to_propose": "Please sign in to suggest an image.",'.
194. Diese Zeile enthält den Code '"images.new_file": "New image file",'.
195. Diese Zeile enthält den Code '"images.pending_badge": "Image suggestion pending",'.
196. Diese Zeile enthält den Code '"images.placeholder": "No image available",'.
197. Diese Zeile enthält den Code '"images.plus_title": "Add image",'.
198. Diese Zeile enthält den Code '"images.primary": "Primary image",'.
199. Diese Zeile enthält den Code '"images.propose_change": "Suggest image change",'.
200. Diese Zeile enthält den Code '"images.request_submitted": "Thanks, your image change request was submitted for review.",'.
201. Diese Zeile enthält den Code '"images.set_primary": "Set as primary",'.
202. Diese Zeile enthält den Code '"images.title": "Images",'.
203. Diese Zeile enthält den Code '"images.upload": "Upload image",'.
204. Diese Zeile enthält den Code '"images.uploaded": "Image uploaded successfully.",'.
205. Diese Zeile enthält den Code '"images.user_change_note": "As a user, image changes go live only after admin approval.",'.
206. Diese Zeile enthält den Code '"image_change.admin_empty": "No image change requests found.",'.
207. Diese Zeile enthält den Code '"image_change.admin_title": "Image Changes (Review)",'.
208. Diese Zeile enthält den Code '"image_change.approved": "Image change request approved.",'.
209. Diese Zeile enthält den Code '"image_change.compare_title": "Image comparison",'.
210. Diese Zeile enthält den Code '"image_change.current_image": "Current image",'.
211. Diese Zeile enthält den Code '"image_change.detail_title": "Image change request",'.
212. Diese Zeile enthält den Code '"image_change.open_queue": "Open image change queue",'.
213. Diese Zeile enthält den Code '"image_change.pending_count": "Pending requests: {count}",'.
214. Diese Zeile enthält den Code '"image_change.proposed_image": "Proposed image",'.
215. Diese Zeile enthält den Code '"image_change.rejected": "Image change request rejected.",'.
216. Diese Zeile enthält den Code '"image_change.review_done": "This image change request has already been reviewed.",'.
217. Diese Zeile enthält den Code '"moderation.approve": "Approve",'.
218. Diese Zeile enthält den Code '"moderation.pending": "Pending",'.
219. Diese Zeile enthält den Code '"moderation.reject": "Reject",'.
220. Diese Zeile enthält den Code '"moderation.title": "Moderation Queue",'.
221. Diese Zeile enthält den Code '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
222. Diese Zeile enthält den Code '"my_recipes.title": "Meine Rezepte",'.
223. Diese Zeile enthält den Code '"nav.admin": "Admin",'.
224. Diese Zeile enthält den Code '"nav.admin_submissions": "Moderation",'.
225. Diese Zeile enthält den Code '"nav.create_recipe": "Create Recipe",'.
226. Diese Zeile enthält den Code '"nav.discover": "Discover Recipes",'.
227. Diese Zeile enthält den Code '"nav.favorites": "Favorites",'.
228. Diese Zeile enthält den Code '"nav.language": "Language",'.
229. Diese Zeile enthält den Code '"nav.login": "Login",'.
230. Diese Zeile enthält den Code '"nav.logout": "Logout",'.
231. Diese Zeile enthält den Code '"nav.my_recipes": "My Recipes",'.
232. Diese Zeile enthält den Code '"nav.my_submissions": "My Submissions",'.
233. Diese Zeile enthält den Code '"nav.profile": "My Profile",'.
234. Diese Zeile enthält den Code '"nav.publish_recipe": "Publish Recipe",'.
235. Diese Zeile enthält den Code '"nav.register": "Register",'.
236. Diese Zeile enthält den Code '"nav.submit": "Submit Recipe",'.
237. Diese Zeile enthält den Code '"nav.submit_recipe": "Submit Recipe",'.
238. Diese Zeile enthält den Code '"pagination.first": "First",'.
239. Diese Zeile enthält den Code '"pagination.last": "Last",'.
240. Diese Zeile enthält den Code '"pagination.next": "Next",'.
241. Diese Zeile enthält den Code '"pagination.page": "Page",'.
242. Diese Zeile enthält den Code '"pagination.prev": "Previous",'.
243. Diese Zeile enthält den Code '"pagination.previous": "Previous",'.
244. Diese Zeile enthält den Code '"pagination.results_range": "Showing {start}-{end} of {total} recipes",'.
245. Diese Zeile enthält den Code '"profile.email": "E-Mail",'.
246. Diese Zeile enthält den Code '"profile.joined": "Registriert am",'.
247. Diese Zeile enthält den Code '"profile.role": "Rolle",'.
248. Diese Zeile enthält den Code '"profile.title": "Mein Profil",'.
249. Diese Zeile enthält den Code '"profile.user_uid": "Your user ID",'.
250. Diese Zeile enthält den Code '"profile.username": "Username",'.
251. Diese Zeile enthält den Code '"profile.username_change_title": "Change username",'.
252. Diese Zeile enthält den Code '"profile.username_save": "Save username",'.
253. Diese Zeile enthält den Code '"profile.username_updated": "Username was updated.",'.
254. Diese Zeile enthält den Code '"recipe.average_rating": "Durchschnittliche Bewertung",'.
255. Diese Zeile enthält den Code '"recipe.comment": "Kommentar",'.
256. Diese Zeile enthält den Code '"recipe.delete": "Loeschen",'.
257. Diese Zeile enthält den Code '"recipe.edit": "Bearbeiten",'.
258. Diese Zeile enthält den Code '"recipe.ingredients": "Zutaten",'.
259. Diese Zeile enthält den Code '"recipe.instructions": "Anleitung",'.
260. Diese Zeile enthält den Code '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
261. Diese Zeile enthält den Code '"recipe.no_results": "No recipes found.",'.
262. Diese Zeile enthält den Code '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
263. Diese Zeile enthält den Code '"recipe.pdf_download": "PDF herunterladen",'.
264. Diese Zeile enthält den Code '"recipe.rating": "Bewertung",'.
265. Diese Zeile enthält den Code '"recipe.rating_short": "Bewertung",'.
266. Diese Zeile enthält den Code '"recipe.review_count_label": "Bewertungen",'.
267. Diese Zeile enthält den Code '"recipe.reviews": "Bewertungen",'.
268. Diese Zeile enthält den Code '"recipe.save_review": "Bewertung speichern",'.
269. Diese Zeile enthält den Code '"recipe_form.category": "Kategorie",'.
270. Diese Zeile enthält den Code '"recipe_form.create": "Erstellen",'.
271. Diese Zeile enthält den Code '"recipe_form.create_title": "Rezept veroeffentlichen",'.
272. Diese Zeile enthält den Code '"recipe_form.description": "Beschreibung",'.
273. Diese Zeile enthält den Code '"recipe_form.difficulty": "Schwierigkeit",'.
274. Diese Zeile enthält den Code '"recipe_form.edit_title": "Rezept bearbeiten",'.
275. Diese Zeile enthält den Code '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
276. Diese Zeile enthält den Code '"recipe_form.instructions": "Anleitung",'.
277. Diese Zeile enthält den Code '"recipe_form.new_category_label": "Neue Kategorie",'.
278. Diese Zeile enthält den Code '"recipe_form.new_category_option": "Neue Kategorie...",'.
279. Diese Zeile enthält den Code '"recipe_form.optional_image": "Optionales Bild",'.
280. Diese Zeile enthält den Code '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
281. Diese Zeile enthält den Code '"recipe_form.save": "Speichern",'.
282. Diese Zeile enthält den Code '"recipe_form.title": "Titel",'.
283. Diese Zeile enthält den Code '"recipe_form.title_image_url": "Titelbild-URL",'.
284. Diese Zeile enthält den Code '"role.admin": "Administrator",'.
285. Diese Zeile enthält den Code '"role.user": "Nutzer",'.
286. Diese Zeile enthält den Code '"sort.highest_rated": "Highest rated",'.
287. Diese Zeile enthält den Code '"sort.lowest_rated": "Lowest rated",'.
288. Diese Zeile enthält den Code '"sort.newest": "Newest",'.
289. Diese Zeile enthält den Code '"sort.oldest": "Oldest",'.
290. Diese Zeile enthält den Code '"sort.prep_time": "Prep time",'.
291. Diese Zeile enthält den Code '"submission.admin_detail_title": "Einreichung",'.
292. Diese Zeile enthält den Code '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
293. Diese Zeile enthält den Code '"submission.admin_note": "Admin-Notiz",'.
294. Diese Zeile enthält den Code '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
295. Diese Zeile enthält den Code '"submission.admin_queue_title": "Moderation Queue",'.
296. Diese Zeile enthält den Code '"submission.approve_button": "Approve",'.
297. Diese Zeile enthält den Code '"submission.approved": "Einreichung wurde freigegeben.",'.
298. Diese Zeile enthält den Code '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
299. Diese Zeile enthält den Code '"submission.category": "Kategorie",'.
300. Diese Zeile enthält den Code '"submission.default_description": "Rezept-Einreichung",'.
301. Diese Zeile enthält den Code '"submission.description": "Beschreibung",'.
302. Diese Zeile enthält den Code '"submission.difficulty": "Schwierigkeit",'.
303. Diese Zeile enthält den Code '"submission.edit_submission": "Einreichung bearbeiten",'.
304. Diese Zeile enthält den Code '"submission.guest": "Gast",'.
305. Diese Zeile enthält den Code '"submission.image_deleted": "Bild wurde entfernt.",'.
306. Diese Zeile enthält den Code '"submission.image_optional": "Optionales Bild",'.
307. Diese Zeile enthält den Code '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
308. Diese Zeile enthält den Code '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
309. Diese Zeile enthält den Code '"submission.instructions": "Anleitung",'.
310. Diese Zeile enthält den Code '"submission.moderation_actions": "Moderations-Aktionen",'.
311. Diese Zeile enthält den Code '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
312. Diese Zeile enthält den Code '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",'.
313. Diese Zeile enthält den Code '"submission.my_title": "My Submissions",'.
314. Diese Zeile enthält den Code '"submission.new_category_label": "Neue Kategorie",'.
315. Diese Zeile enthält den Code '"submission.new_category_option": "Neue Kategorie...",'.
316. Diese Zeile enthält den Code '"submission.open_detail": "Details",'.
317. Diese Zeile enthält den Code '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
318. Diese Zeile enthält den Code '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
319. Diese Zeile enthält den Code '"submission.preview": "Vorschau",'.
320. Diese Zeile enthält den Code '"submission.reject_button": "Reject",'.
321. Diese Zeile enthält den Code '"submission.reject_reason": "Ablehnungsgrund",'.
322. Diese Zeile enthält den Code '"submission.rejected": "Einreichung wurde abgelehnt.",'.
323. Diese Zeile enthält den Code '"submission.save_changes": "Aenderungen speichern",'.
324. Diese Zeile enthält den Code '"submission.servings": "Portionen (optional)",'.
325. Diese Zeile enthält den Code '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
326. Diese Zeile enthält den Code '"submission.stats_approved": "Freigegeben",'.
327. Diese Zeile enthält den Code '"submission.stats_pending": "Ausstehend",'.
328. Diese Zeile enthält den Code '"submission.stats_rejected": "Abgelehnt",'.
329. Diese Zeile enthält den Code '"submission.status_all": "Alle",'.
330. Diese Zeile enthält den Code '"submission.status_approved": "Approved",'.
331. Diese Zeile enthält den Code '"submission.status_filter": "Status",'.
332. Diese Zeile enthält den Code '"submission.status_pending": "Pending",'.
333. Diese Zeile enthält den Code '"submission.status_rejected": "Rejected",'.
334. Diese Zeile enthält den Code '"submission.submit_button": "Zur Pruefung einreichen",'.
335. Diese Zeile enthält den Code '"submission.submit_hint": "Submissions are reviewed by admins before publication.",'.
336. Diese Zeile enthält den Code '"submission.submit_title": "Submit Recipe",'.
337. Diese Zeile enthält den Code '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
338. Diese Zeile enthält den Code '"submission.table_action": "Aktion",'.
339. Diese Zeile enthält den Code '"submission.table_date": "Datum",'.
340. Diese Zeile enthält den Code '"submission.table_status": "Status",'.
341. Diese Zeile enthält den Code '"submission.table_submitter": "Einreicher",'.
342. Diese Zeile enthält den Code '"submission.table_title": "Titel",'.
343. Diese Zeile enthält den Code '"submission.thank_you": "Thank you! Your recipe has been submitted for review.",'.
344. Diese Zeile enthält den Code '"submission.title": "Titel",'.
345. Diese Zeile enthält den Code '"submission.updated": "Einreichung wurde aktualisiert."'.
346. Diese Zeile enthält den Code '}'.

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
  "auth.change_password_button": "Mettre a jour le mot de passe",
  "auth.change_password_title": "Changer le mot de passe",
  "auth.change_email_confirm_button": "Mettre a jour l'e-mail maintenant",
  "auth.change_email_confirm_hint": "Vous confirmez cette nouvelle adresse e-mail : {email}",
  "auth.change_email_confirm_title": "Confirmer le changement d'e-mail",
  "auth.change_email_current": "E-mail actuel : {email}",
  "auth.change_email_open_link": "Changer l'adresse e-mail",
  "auth.change_email_request_button": "Envoyer le lien de confirmation",
  "auth.change_email_requested": "Veuillez verifier votre nouvel e-mail et confirmer le lien.",
  "auth.change_email_reissue_hint": "Si ce lien a expire, demandez-en un nouveau.",
  "auth.change_email_retry_link": "Demander un nouveau changement d'e-mail",
  "auth.change_email_title": "Changer l'e-mail",
  "auth.confirm_password": "Confirmer le mot de passe",
  "auth.email": "E-mail",
  "auth.email_change_body": "Veuillez confirmer votre nouvelle adresse e-mail avec ce lien : {confirm_link}",
  "auth.email_change_same_email": "Le nouvel e-mail correspond deja a l'adresse actuelle.",
  "auth.email_change_subject": "Confirmer le changement d'e-mail MealMate",
  "auth.email_change_success": "L'e-mail a ete mis a jour avec succes.",
  "auth.forgot_generic_response": "Si le compte existe, un e-mail a ete envoye.",
  "auth.forgot_password_button": "Demander un lien",
  "auth.forgot_password_hint": "Entrez votre e-mail ou nom d'utilisateur pour recevoir un lien de reinitialisation.",
  "auth.forgot_password_link": "Mot de passe oublie ?",
  "auth.forgot_password_title": "Mot de passe oublie",
  "auth.identifier": "E-mail ou nom d'utilisateur",
  "auth.login": "Connexion",
  "auth.login_button": "Connexion",
  "auth.login_title": "Connexion",
  "auth.new_password": "Nouveau mot de passe",
  "auth.new_email_label": "Nouvel e-mail",
  "auth.old_password": "Ancien mot de passe",
  "auth.password": "Mot de passe",
  "auth.password_changed_success": "Le mot de passe a ete modifie avec succes.",
  "auth.register": "Inscription",
  "auth.register_button": "Creer un compte",
  "auth.register_title": "Inscription",
  "auth.reset_email_body": "Utilisez ce lien pour reinitialiser votre mot de passe : {reset_link}",
  "auth.reset_email_subject": "Reinitialisation du mot de passe MealMate",
  "auth.reset_password_button": "Reinitialiser le mot de passe",
  "auth.reset_password_title": "Reinitialiser le mot de passe",
  "auth.reset_success": "Le mot de passe a ete reinitialise, veuillez vous reconnecter.",
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
  "error.image_change_file_missing": "Aucun fichier image n'a ete trouve pour cette demande.",
  "error.image_change_request_not_found": "Demande de changement d'image introuvable.",
  "error.image_change_request_not_pending": "Cette demande de changement d'image n'est plus en attente.",
  "error.email_change_token_invalid": "Ce lien est invalide ou expire. Veuillez en demander un nouveau.",
  "error.email_invalid": "Veuillez saisir une adresse e-mail valide.",
  "error.email_unavailable": "Cette adresse e-mail n'est pas disponible.",
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
  "error.password_confirm_mismatch": "Le mot de passe et la confirmation ne correspondent pas.",
  "error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",
  "error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",
  "error.password_old_invalid": "L'ancien mot de passe est invalide.",
  "error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",
  "error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",
  "error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",
  "error.recipe_not_found": "Rezept nicht gefunden.",
  "error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",
  "error.reset_token_invalid": "Le lien de reinitialisation est invalide ou expire.",
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
  "error.username_invalid": "Le nom d'utilisateur doit contenir 3 a 30 caracteres et uniquement lettres, chiffres, point, underscore ou tiret.",
  "error.username_taken": "Ce nom d'utilisateur est deja utilise.",
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
  "images.admin_use_direct_upload": "Les admins doivent utiliser l'upload direct d'image.",
  "images.delete": "Supprimer",
  "images.empty": "Aucune image importee pour le moment.",
  "images.login_to_propose": "Veuillez vous connecter pour proposer une image.",
  "images.new_file": "Nouveau fichier image",
  "images.pending_badge": "Proposition d'image en attente",
  "images.placeholder": "Aucune image disponible",
  "images.plus_title": "Ajouter une image",
  "images.primary": "Image principale",
  "images.propose_change": "Proposer un changement d'image",
  "images.request_submitted": "Merci, votre proposition d'image a ete envoyee pour validation.",
  "images.set_primary": "Definir comme principale",
  "images.title": "Images",
  "images.upload": "Televerser l'image",
  "images.uploaded": "Image televersee avec succes.",
  "images.user_change_note": "Pour un utilisateur, la modification d'image est publiee apres validation admin.",
  "image_change.admin_empty": "Aucune demande de changement d'image trouvee.",
  "image_change.admin_title": "Changements d'image (Validation)",
  "image_change.approved": "Demande de changement d'image approuvee.",
  "image_change.compare_title": "Comparaison d'images",
  "image_change.current_image": "Image actuelle",
  "image_change.detail_title": "Demande de changement d'image",
  "image_change.open_queue": "Ouvrir la file des changements d'image",
  "image_change.pending_count": "Demandes en attente : {count}",
  "image_change.proposed_image": "Image proposee",
  "image_change.rejected": "Demande de changement d'image rejetee.",
  "image_change.review_done": "Cette demande a deja ete traitee.",
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
  "profile.user_uid": "Votre identifiant utilisateur",
  "profile.username": "Nom d'utilisateur",
  "profile.username_change_title": "Changer le nom d'utilisateur",
  "profile.username_save": "Enregistrer le nom d'utilisateur",
  "profile.username_updated": "Le nom d'utilisateur a ete mis a jour.",
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

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '{'.
2. Diese Zeile enthält den Code '"admin.action": "Aktion",'.
3. Diese Zeile enthält den Code '"admin.category_distinct_count": "Anzahl eindeutiger Kategorien",'.
4. Diese Zeile enthält den Code '"admin.category_stats_title": "Kategorien-Status",'.
5. Diese Zeile enthält den Code '"admin.category_top": "Top 10 Kategorien",'.
6. Diese Zeile enthält den Code '"admin.confirm_warnings_required": "Warnungen vorhanden: Setze 'Trotz Warnungen fortsetzen', um d...'.
7. Diese Zeile enthält den Code '"admin.creator": "Ersteller",'.
8. Diese Zeile enthält den Code '"admin.csv_path": "CSV-Pfad",'.
9. Diese Zeile enthält den Code '"admin.download_example": "CSV Beispiel herunterladen",'.
10. Diese Zeile enthält den Code '"admin.download_template": "CSV Template herunterladen",'.
11. Diese Zeile enthält den Code '"admin.dry_run": "Nur pruefen (Dry Run)",'.
12. Diese Zeile enthält den Code '"admin.dry_run_done": "Dry-Run abgeschlossen, es wurden keine Daten geschrieben.",'.
13. Diese Zeile enthält den Code '"admin.email": "E-Mail",'.
14. Diese Zeile enthält den Code '"admin.force_with_warnings": "Trotz Warnungen fortsetzen",'.
15. Diese Zeile enthält den Code '"admin.id": "ID",'.
16. Diese Zeile enthält den Code '"admin.import_blocked_errors": "Import blockiert: Bitte behebe zuerst die fehlerhaften Zeilen.",'.
17. Diese Zeile enthält den Code '"admin.import_difficulty_values": "Difficulty-Werte: easy, medium, hard",'.
18. Diese Zeile enthält den Code '"admin.import_encoding_delimiter": "Encoding: utf-8-sig, Delimiter standardmaessig ';' (',' als F...'.
19. Diese Zeile enthält den Code '"admin.import_help_intro": "Bitte nutze das kanonische Importformat, damit der Import stabil und ...'.
20. Diese Zeile enthält den Code '"admin.import_help_title": "CSV-Format Hilfe",'.
21. Diese Zeile enthält den Code '"admin.import_ingredients_example": "Ingredients Beispiel: 2 Eier | 200g Mehl | 1 Prise Salz oder...'.
22. Diese Zeile enthält den Code '"admin.import_optional_columns": "Empfohlene Spalten: description, category, difficulty, prep_tim...'.
23. Diese Zeile enthält den Code '"admin.import_required_columns": "Pflichtspalten: title, instructions",'.
24. Diese Zeile enthält den Code '"admin.import_result_title": "Import-Ergebnis",'.
25. Diese Zeile enthält den Code '"admin.import_title": "Import CSV manuel",'.
26. Diese Zeile enthält den Code '"admin.import_warning_text": "Standard ist Insert-Only; Update Existing nur aktivieren, wenn bewu...'.
27. Diese Zeile enthält den Code '"admin.insert_only": "Nur neue hinzufuegen (UPSERT SAFE)",'.
28. Diese Zeile enthält den Code '"admin.preview_button": "Vorschau erstellen",'.
29. Diese Zeile enthält den Code '"admin.preview_delimiter": "Erkannter Delimiter",'.
30. Diese Zeile enthält den Code '"admin.preview_done": "Vorschau wurde erstellt.",'.
31. Diese Zeile enthält den Code '"admin.preview_errors_title": "Fehlerliste",'.
32. Diese Zeile enthält den Code '"admin.preview_fatal_rows": "Zeilen mit Fehlern",'.
33. Diese Zeile enthält den Code '"admin.preview_notes": "Hinweise",'.
34. Diese Zeile enthält den Code '"admin.preview_row": "Zeile",'.
35. Diese Zeile enthält den Code '"admin.preview_status": "Status",'.
36. Diese Zeile enthält den Code '"admin.preview_title": "Import-Vorschau",'.
37. Diese Zeile enthält den Code '"admin.preview_total_rows": "Gesamtzeilen",'.
38. Diese Zeile enthält den Code '"admin.preview_warnings_title": "Warnungsliste",'.
39. Diese Zeile enthält den Code '"admin.recipes": "Rezepte",'.
40. Diese Zeile enthält den Code '"admin.report_errors": "Fehler",'.
41. Diese Zeile enthält den Code '"admin.report_inserted": "Neu",'.
42. Diese Zeile enthält den Code '"admin.report_skipped": "Uebersprungen",'.
43. Diese Zeile enthält den Code '"admin.report_updated": "Aktualisiert",'.
44. Diese Zeile enthält den Code '"admin.report_warnings": "Warnungen",'.
45. Diese Zeile enthält den Code '"admin.role": "Rolle",'.
46. Diese Zeile enthält den Code '"admin.save": "Speichern",'.
47. Diese Zeile enthält den Code '"admin.seed_done": "Seed-Status: bereits ausgefuehrt.",'.
48. Diese Zeile enthält den Code '"admin.seed_run": "Einmaligen KochWiki-Seed ausfuehren",'.
49. Diese Zeile enthält den Code '"admin.seed_title": "KochWiki-Seed (einmalig)",'.
50. Diese Zeile enthält den Code '"admin.source": "Quelle",'.
51. Diese Zeile enthält den Code '"admin.start_import": "Import starten",'.
52. Diese Zeile enthält den Code '"admin.title": "Espace Admin",'.
53. Diese Zeile enthält den Code '"admin.title_column": "Titel",'.
54. Diese Zeile enthält den Code '"admin.update_existing": "Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)",'.
55. Diese Zeile enthält den Code '"admin.upload_label": "CSV-Upload",'.
56. Diese Zeile enthält den Code '"admin.users": "Nutzer",'.
57. Diese Zeile enthält den Code '"app.name": "MealMate",'.
58. Diese Zeile enthält den Code '"auth.change_password_button": "Mettre a jour le mot de passe",'.
59. Diese Zeile enthält den Code '"auth.change_password_title": "Changer le mot de passe",'.
60. Diese Zeile enthält den Code '"auth.change_email_confirm_button": "Mettre a jour l'e-mail maintenant",'.
61. Diese Zeile enthält den Code '"auth.change_email_confirm_hint": "Vous confirmez cette nouvelle adresse e-mail : {email}",'.
62. Diese Zeile enthält den Code '"auth.change_email_confirm_title": "Confirmer le changement d'e-mail",'.
63. Diese Zeile enthält den Code '"auth.change_email_current": "E-mail actuel : {email}",'.
64. Diese Zeile enthält den Code '"auth.change_email_open_link": "Changer l'adresse e-mail",'.
65. Diese Zeile enthält den Code '"auth.change_email_request_button": "Envoyer le lien de confirmation",'.
66. Diese Zeile enthält den Code '"auth.change_email_requested": "Veuillez verifier votre nouvel e-mail et confirmer le lien.",'.
67. Diese Zeile enthält den Code '"auth.change_email_reissue_hint": "Si ce lien a expire, demandez-en un nouveau.",'.
68. Diese Zeile enthält den Code '"auth.change_email_retry_link": "Demander un nouveau changement d'e-mail",'.
69. Diese Zeile enthält den Code '"auth.change_email_title": "Changer l'e-mail",'.
70. Diese Zeile enthält den Code '"auth.confirm_password": "Confirmer le mot de passe",'.
71. Diese Zeile enthält den Code '"auth.email": "E-mail",'.
72. Diese Zeile enthält den Code '"auth.email_change_body": "Veuillez confirmer votre nouvelle adresse e-mail avec ce lien : {confi...'.
73. Diese Zeile enthält den Code '"auth.email_change_same_email": "Le nouvel e-mail correspond deja a l'adresse actuelle.",'.
74. Diese Zeile enthält den Code '"auth.email_change_subject": "Confirmer le changement d'e-mail MealMate",'.
75. Diese Zeile enthält den Code '"auth.email_change_success": "L'e-mail a ete mis a jour avec succes.",'.
76. Diese Zeile enthält den Code '"auth.forgot_generic_response": "Si le compte existe, un e-mail a ete envoye.",'.
77. Diese Zeile enthält den Code '"auth.forgot_password_button": "Demander un lien",'.
78. Diese Zeile enthält den Code '"auth.forgot_password_hint": "Entrez votre e-mail ou nom d'utilisateur pour recevoir un lien de r...'.
79. Diese Zeile enthält den Code '"auth.forgot_password_link": "Mot de passe oublie ?",'.
80. Diese Zeile enthält den Code '"auth.forgot_password_title": "Mot de passe oublie",'.
81. Diese Zeile enthält den Code '"auth.identifier": "E-mail ou nom d'utilisateur",'.
82. Diese Zeile enthält den Code '"auth.login": "Connexion",'.
83. Diese Zeile enthält den Code '"auth.login_button": "Connexion",'.
84. Diese Zeile enthält den Code '"auth.login_title": "Connexion",'.
85. Diese Zeile enthält den Code '"auth.new_password": "Nouveau mot de passe",'.
86. Diese Zeile enthält den Code '"auth.new_email_label": "Nouvel e-mail",'.
87. Diese Zeile enthält den Code '"auth.old_password": "Ancien mot de passe",'.
88. Diese Zeile enthält den Code '"auth.password": "Mot de passe",'.
89. Diese Zeile enthält den Code '"auth.password_changed_success": "Le mot de passe a ete modifie avec succes.",'.
90. Diese Zeile enthält den Code '"auth.register": "Inscription",'.
91. Diese Zeile enthält den Code '"auth.register_button": "Creer un compte",'.
92. Diese Zeile enthält den Code '"auth.register_title": "Inscription",'.
93. Diese Zeile enthält den Code '"auth.reset_email_body": "Utilisez ce lien pour reinitialiser votre mot de passe : {reset_link}",'.
94. Diese Zeile enthält den Code '"auth.reset_email_subject": "Reinitialisation du mot de passe MealMate",'.
95. Diese Zeile enthält den Code '"auth.reset_password_button": "Reinitialiser le mot de passe",'.
96. Diese Zeile enthält den Code '"auth.reset_password_title": "Reinitialiser le mot de passe",'.
97. Diese Zeile enthält den Code '"auth.reset_success": "Le mot de passe a ete reinitialise, veuillez vous reconnecter.",'.
98. Diese Zeile enthält den Code '"difficulty.easy": "Facile",'.
99. Diese Zeile enthält den Code '"difficulty.hard": "Difficile",'.
100. Diese Zeile enthält den Code '"difficulty.medium": "Moyen",'.
101. Diese Zeile enthält den Code '"discover.filter.apply": "Appliquer",'.
102. Diese Zeile enthält den Code '"discover.filter.category": "Categorie",'.
103. Diese Zeile enthält den Code '"discover.filter.difficulty": "Difficulte",'.
104. Diese Zeile enthält den Code '"discover.filter.ingredient": "Ingredient",'.
105. Diese Zeile enthält den Code '"discover.filter.title_contains": "Le titre contient",'.
106. Diese Zeile enthält den Code '"discover.sort.newest": "Plus recentes",'.
107. Diese Zeile enthält den Code '"discover.sort.oldest": "Plus anciennes",'.
108. Diese Zeile enthält den Code '"discover.sort.prep_time": "Temps de preparation",'.
109. Diese Zeile enthält den Code '"discover.sort.rating_asc": "Moins bien notees",'.
110. Diese Zeile enthält den Code '"discover.sort.rating_desc": "Mieux notees",'.
111. Diese Zeile enthält den Code '"discover.title": "Decouvrir des recettes",'.
112. Diese Zeile enthält den Code '"empty.no_recipes": "Aucune recette trouvee.",'.
113. Diese Zeile enthält den Code '"error.404_text": "La page demandee n'existe pas ou a ete deplacee.",'.
114. Diese Zeile enthält den Code '"error.404_title": "404 - Page introuvable",'.
115. Diese Zeile enthält den Code '"error.500_text": "Une erreur inattendue est survenue pendant le traitement.",'.
116. Diese Zeile enthält den Code '"error.500_title": "500 - Erreur interne",'.
117. Diese Zeile enthält den Code '"error.admin_required": "Role admin requis.",'.
118. Diese Zeile enthält den Code '"error.auth_required": "Authentification requise.",'.
119. Diese Zeile enthält den Code '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
120. Diese Zeile enthält den Code '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
121. Diese Zeile enthält den Code '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
122. Diese Zeile enthält den Code '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
123. Diese Zeile enthält den Code '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
124. Diese Zeile enthält den Code '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
125. Diese Zeile enthält den Code '"error.email_registered": "Cet e-mail est deja utilise.",'.
126. Diese Zeile enthält den Code '"error.image_change_file_missing": "Aucun fichier image n'a ete trouve pour cette demande.",'.
127. Diese Zeile enthält den Code '"error.image_change_request_not_found": "Demande de changement d'image introuvable.",'.
128. Diese Zeile enthält den Code '"error.image_change_request_not_pending": "Cette demande de changement d'image n'est plus en atte...'.
129. Diese Zeile enthält den Code '"error.email_change_token_invalid": "Ce lien est invalide ou expire. Veuillez en demander un nouv...'.
130. Diese Zeile enthält den Code '"error.email_invalid": "Veuillez saisir une adresse e-mail valide.",'.
131. Diese Zeile enthält den Code '"error.email_unavailable": "Cette adresse e-mail n'est pas disponible.",'.
132. Diese Zeile enthält den Code '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
133. Diese Zeile enthält den Code '"error.field_positive": "{field} muss groesser als null sein.",'.
134. Diese Zeile enthält den Code '"error.home_link": "Retour a l'accueil",'.
135. Diese Zeile enthält den Code '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
136. Diese Zeile enthält den Code '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
137. Diese Zeile enthält den Code '"error.image_not_found": "Bild nicht gefunden.",'.
138. Diese Zeile enthält den Code '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
139. Diese Zeile enthält den Code '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
140. Diese Zeile enthält den Code '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
141. Diese Zeile enthält den Code '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
142. Diese Zeile enthält den Code '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
143. Diese Zeile enthält den Code '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",'.
144. Diese Zeile enthält den Code '"error.internal": "Interner Serverfehler.",'.
145. Diese Zeile enthält den Code '"error.invalid_credentials": "Identifiants invalides.",'.
146. Diese Zeile enthält den Code '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
147. Diese Zeile enthält den Code '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
148. Diese Zeile enthält den Code '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
149. Diese Zeile enthält den Code '"error.not_found": "Ressource nicht gefunden.",'.
150. Diese Zeile enthält den Code '"error.password_confirm_mismatch": "Le mot de passe et la confirmation ne correspondent pas.",'.
151. Diese Zeile enthält den Code '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
152. Diese Zeile enthält den Code '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
153. Diese Zeile enthält den Code '"error.password_old_invalid": "L'ancien mot de passe est invalide.",'.
154. Diese Zeile enthält den Code '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
155. Diese Zeile enthält den Code '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
156. Diese Zeile enthält den Code '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
157. Diese Zeile enthält den Code '"error.recipe_not_found": "Rezept nicht gefunden.",'.
158. Diese Zeile enthält den Code '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
159. Diese Zeile enthält den Code '"error.reset_token_invalid": "Le lien de reinitialisation est invalide ou expire.",'.
160. Diese Zeile enthält den Code '"error.review_not_found": "Bewertung nicht gefunden.",'.
161. Diese Zeile enthält den Code '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
162. Diese Zeile enthält den Code '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
163. Diese Zeile enthält den Code '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
164. Diese Zeile enthält den Code '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",'.
165. Diese Zeile enthält den Code '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
166. Diese Zeile enthält den Code '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
167. Diese Zeile enthält den Code '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
168. Diese Zeile enthält den Code '"error.submission_not_found": "Einreichung nicht gefunden.",'.
169. Diese Zeile enthält den Code '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
170. Diese Zeile enthält den Code '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
171. Diese Zeile enthält den Code '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
172. Diese Zeile enthält den Code '"error.trace": "Stacktrace (nur Dev)",'.
173. Diese Zeile enthält den Code '"error.user_not_found": "Nutzer nicht gefunden.",'.
174. Diese Zeile enthält den Code '"error.username_invalid": "Le nom d'utilisateur doit contenir 3 a 30 caracteres et uniquement let...'.
175. Diese Zeile enthält den Code '"error.username_taken": "Ce nom d'utilisateur est deja utilise.",'.
176. Diese Zeile enthält den Code '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
177. Diese Zeile enthält den Code '"favorite.add": "Zu Favoriten",'.
178. Diese Zeile enthält den Code '"favorite.remove": "Aus Favoriten entfernen",'.
179. Diese Zeile enthält den Code '"favorites.empty": "Keine Favoriten gespeichert.",'.
180. Diese Zeile enthält den Code '"favorites.remove": "Favorit entfernen",'.
181. Diese Zeile enthält den Code '"favorites.title": "Favoriten",'.
182. Diese Zeile enthält den Code '"home.all_categories": "Toutes les categories",'.
183. Diese Zeile enthält den Code '"home.apply": "Appliquer",'.
184. Diese Zeile enthält den Code '"home.category": "Categorie",'.
185. Diese Zeile enthält den Code '"home.difficulty": "Difficulte",'.
186. Diese Zeile enthält den Code '"home.ingredient": "Ingredient",'.
187. Diese Zeile enthält den Code '"home.per_page": "Par page",'.
188. Diese Zeile enthält den Code '"home.title": "Decouvrir des recettes",'.
189. Diese Zeile enthält den Code '"home.title_contains": "Le titre contient",'.
190. Diese Zeile enthält den Code '"images.admin_use_direct_upload": "Les admins doivent utiliser l'upload direct d'image.",'.
191. Diese Zeile enthält den Code '"images.delete": "Supprimer",'.
192. Diese Zeile enthält den Code '"images.empty": "Aucune image importee pour le moment.",'.
193. Diese Zeile enthält den Code '"images.login_to_propose": "Veuillez vous connecter pour proposer une image.",'.
194. Diese Zeile enthält den Code '"images.new_file": "Nouveau fichier image",'.
195. Diese Zeile enthält den Code '"images.pending_badge": "Proposition d'image en attente",'.
196. Diese Zeile enthält den Code '"images.placeholder": "Aucune image disponible",'.
197. Diese Zeile enthält den Code '"images.plus_title": "Ajouter une image",'.
198. Diese Zeile enthält den Code '"images.primary": "Image principale",'.
199. Diese Zeile enthält den Code '"images.propose_change": "Proposer un changement d'image",'.
200. Diese Zeile enthält den Code '"images.request_submitted": "Merci, votre proposition d'image a ete envoyee pour validation.",'.
201. Diese Zeile enthält den Code '"images.set_primary": "Definir comme principale",'.
202. Diese Zeile enthält den Code '"images.title": "Images",'.
203. Diese Zeile enthält den Code '"images.upload": "Televerser l'image",'.
204. Diese Zeile enthält den Code '"images.uploaded": "Image televersee avec succes.",'.
205. Diese Zeile enthält den Code '"images.user_change_note": "Pour un utilisateur, la modification d'image est publiee apres valida...'.
206. Diese Zeile enthält den Code '"image_change.admin_empty": "Aucune demande de changement d'image trouvee.",'.
207. Diese Zeile enthält den Code '"image_change.admin_title": "Changements d'image (Validation)",'.
208. Diese Zeile enthält den Code '"image_change.approved": "Demande de changement d'image approuvee.",'.
209. Diese Zeile enthält den Code '"image_change.compare_title": "Comparaison d'images",'.
210. Diese Zeile enthält den Code '"image_change.current_image": "Image actuelle",'.
211. Diese Zeile enthält den Code '"image_change.detail_title": "Demande de changement d'image",'.
212. Diese Zeile enthält den Code '"image_change.open_queue": "Ouvrir la file des changements d'image",'.
213. Diese Zeile enthält den Code '"image_change.pending_count": "Demandes en attente : {count}",'.
214. Diese Zeile enthält den Code '"image_change.proposed_image": "Image proposee",'.
215. Diese Zeile enthält den Code '"image_change.rejected": "Demande de changement d'image rejetee.",'.
216. Diese Zeile enthält den Code '"image_change.review_done": "Cette demande a deja ete traitee.",'.
217. Diese Zeile enthält den Code '"moderation.approve": "Approuver",'.
218. Diese Zeile enthält den Code '"moderation.pending": "En attente",'.
219. Diese Zeile enthält den Code '"moderation.reject": "Rejeter",'.
220. Diese Zeile enthält den Code '"moderation.title": "File de moderation",'.
221. Diese Zeile enthält den Code '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
222. Diese Zeile enthält den Code '"my_recipes.title": "Meine Rezepte",'.
223. Diese Zeile enthält den Code '"nav.admin": "Admin",'.
224. Diese Zeile enthält den Code '"nav.admin_submissions": "Moderation",'.
225. Diese Zeile enthält den Code '"nav.create_recipe": "Creer une recette",'.
226. Diese Zeile enthält den Code '"nav.discover": "Decouvrir des recettes",'.
227. Diese Zeile enthält den Code '"nav.favorites": "Favoris",'.
228. Diese Zeile enthält den Code '"nav.language": "Langue",'.
229. Diese Zeile enthält den Code '"nav.login": "Connexion",'.
230. Diese Zeile enthält den Code '"nav.logout": "Deconnexion",'.
231. Diese Zeile enthält den Code '"nav.my_recipes": "Mes recettes",'.
232. Diese Zeile enthält den Code '"nav.my_submissions": "Mes soumissions",'.
233. Diese Zeile enthält den Code '"nav.profile": "Mon profil",'.
234. Diese Zeile enthält den Code '"nav.publish_recipe": "Publier une recette",'.
235. Diese Zeile enthält den Code '"nav.register": "Inscription",'.
236. Diese Zeile enthält den Code '"nav.submit": "Soumettre une recette",'.
237. Diese Zeile enthält den Code '"nav.submit_recipe": "Soumettre une recette",'.
238. Diese Zeile enthält den Code '"pagination.first": "Premier",'.
239. Diese Zeile enthält den Code '"pagination.last": "Dernier",'.
240. Diese Zeile enthält den Code '"pagination.next": "Suivant",'.
241. Diese Zeile enthält den Code '"pagination.page": "Page",'.
242. Diese Zeile enthält den Code '"pagination.prev": "Precedent",'.
243. Diese Zeile enthält den Code '"pagination.previous": "Precedent",'.
244. Diese Zeile enthält den Code '"pagination.results_range": "Affichage {start}-{end} sur {total} recettes",'.
245. Diese Zeile enthält den Code '"profile.email": "E-Mail",'.
246. Diese Zeile enthält den Code '"profile.joined": "Registriert am",'.
247. Diese Zeile enthält den Code '"profile.role": "Rolle",'.
248. Diese Zeile enthält den Code '"profile.title": "Mein Profil",'.
249. Diese Zeile enthält den Code '"profile.user_uid": "Votre identifiant utilisateur",'.
250. Diese Zeile enthält den Code '"profile.username": "Nom d'utilisateur",'.
251. Diese Zeile enthält den Code '"profile.username_change_title": "Changer le nom d'utilisateur",'.
252. Diese Zeile enthält den Code '"profile.username_save": "Enregistrer le nom d'utilisateur",'.
253. Diese Zeile enthält den Code '"profile.username_updated": "Le nom d'utilisateur a ete mis a jour.",'.
254. Diese Zeile enthält den Code '"recipe.average_rating": "Durchschnittliche Bewertung",'.
255. Diese Zeile enthält den Code '"recipe.comment": "Kommentar",'.
256. Diese Zeile enthält den Code '"recipe.delete": "Loeschen",'.
257. Diese Zeile enthält den Code '"recipe.edit": "Bearbeiten",'.
258. Diese Zeile enthält den Code '"recipe.ingredients": "Zutaten",'.
259. Diese Zeile enthält den Code '"recipe.instructions": "Anleitung",'.
260. Diese Zeile enthält den Code '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
261. Diese Zeile enthält den Code '"recipe.no_results": "Aucune recette trouvee.",'.
262. Diese Zeile enthält den Code '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
263. Diese Zeile enthält den Code '"recipe.pdf_download": "PDF herunterladen",'.
264. Diese Zeile enthält den Code '"recipe.rating": "Bewertung",'.
265. Diese Zeile enthält den Code '"recipe.rating_short": "Bewertung",'.
266. Diese Zeile enthält den Code '"recipe.review_count_label": "Bewertungen",'.
267. Diese Zeile enthält den Code '"recipe.reviews": "Bewertungen",'.
268. Diese Zeile enthält den Code '"recipe.save_review": "Bewertung speichern",'.
269. Diese Zeile enthält den Code '"recipe_form.category": "Kategorie",'.
270. Diese Zeile enthält den Code '"recipe_form.create": "Erstellen",'.
271. Diese Zeile enthält den Code '"recipe_form.create_title": "Rezept veroeffentlichen",'.
272. Diese Zeile enthält den Code '"recipe_form.description": "Beschreibung",'.
273. Diese Zeile enthält den Code '"recipe_form.difficulty": "Schwierigkeit",'.
274. Diese Zeile enthält den Code '"recipe_form.edit_title": "Rezept bearbeiten",'.
275. Diese Zeile enthält den Code '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
276. Diese Zeile enthält den Code '"recipe_form.instructions": "Anleitung",'.
277. Diese Zeile enthält den Code '"recipe_form.new_category_label": "Neue Kategorie",'.
278. Diese Zeile enthält den Code '"recipe_form.new_category_option": "Neue Kategorie...",'.
279. Diese Zeile enthält den Code '"recipe_form.optional_image": "Optionales Bild",'.
280. Diese Zeile enthält den Code '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
281. Diese Zeile enthält den Code '"recipe_form.save": "Speichern",'.
282. Diese Zeile enthält den Code '"recipe_form.title": "Titel",'.
283. Diese Zeile enthält den Code '"recipe_form.title_image_url": "Titelbild-URL",'.
284. Diese Zeile enthält den Code '"role.admin": "Administrator",'.
285. Diese Zeile enthält den Code '"role.user": "Nutzer",'.
286. Diese Zeile enthält den Code '"sort.highest_rated": "Mieux notees",'.
287. Diese Zeile enthält den Code '"sort.lowest_rated": "Moins bien notees",'.
288. Diese Zeile enthält den Code '"sort.newest": "Plus recentes",'.
289. Diese Zeile enthält den Code '"sort.oldest": "Plus anciennes",'.
290. Diese Zeile enthält den Code '"sort.prep_time": "Temps de preparation",'.
291. Diese Zeile enthält den Code '"submission.admin_detail_title": "Einreichung",'.
292. Diese Zeile enthält den Code '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
293. Diese Zeile enthält den Code '"submission.admin_note": "Admin-Notiz",'.
294. Diese Zeile enthält den Code '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
295. Diese Zeile enthält den Code '"submission.admin_queue_title": "File de moderation",'.
296. Diese Zeile enthält den Code '"submission.approve_button": "Approuver",'.
297. Diese Zeile enthält den Code '"submission.approved": "Einreichung wurde freigegeben.",'.
298. Diese Zeile enthält den Code '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
299. Diese Zeile enthält den Code '"submission.category": "Kategorie",'.
300. Diese Zeile enthält den Code '"submission.default_description": "Rezept-Einreichung",'.
301. Diese Zeile enthält den Code '"submission.description": "Beschreibung",'.
302. Diese Zeile enthält den Code '"submission.difficulty": "Schwierigkeit",'.
303. Diese Zeile enthält den Code '"submission.edit_submission": "Einreichung bearbeiten",'.
304. Diese Zeile enthält den Code '"submission.guest": "Gast",'.
305. Diese Zeile enthält den Code '"submission.image_deleted": "Bild wurde entfernt.",'.
306. Diese Zeile enthält den Code '"submission.image_optional": "Optionales Bild",'.
307. Diese Zeile enthält den Code '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
308. Diese Zeile enthält den Code '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
309. Diese Zeile enthält den Code '"submission.instructions": "Anleitung",'.
310. Diese Zeile enthält den Code '"submission.moderation_actions": "Moderations-Aktionen",'.
311. Diese Zeile enthält den Code '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
312. Diese Zeile enthält den Code '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",'.
313. Diese Zeile enthält den Code '"submission.my_title": "Mes soumissions",'.
314. Diese Zeile enthält den Code '"submission.new_category_label": "Neue Kategorie",'.
315. Diese Zeile enthält den Code '"submission.new_category_option": "Neue Kategorie...",'.
316. Diese Zeile enthält den Code '"submission.open_detail": "Details",'.
317. Diese Zeile enthält den Code '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
318. Diese Zeile enthält den Code '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
319. Diese Zeile enthält den Code '"submission.preview": "Vorschau",'.
320. Diese Zeile enthält den Code '"submission.reject_button": "Rejeter",'.
321. Diese Zeile enthält den Code '"submission.reject_reason": "Ablehnungsgrund",'.
322. Diese Zeile enthält den Code '"submission.rejected": "Einreichung wurde abgelehnt.",'.
323. Diese Zeile enthält den Code '"submission.save_changes": "Aenderungen speichern",'.
324. Diese Zeile enthält den Code '"submission.servings": "Portionen (optional)",'.
325. Diese Zeile enthält den Code '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
326. Diese Zeile enthält den Code '"submission.stats_approved": "Freigegeben",'.
327. Diese Zeile enthält den Code '"submission.stats_pending": "Ausstehend",'.
328. Diese Zeile enthält den Code '"submission.stats_rejected": "Abgelehnt",'.
329. Diese Zeile enthält den Code '"submission.status_all": "Alle",'.
330. Diese Zeile enthält den Code '"submission.status_approved": "Approuvee",'.
331. Diese Zeile enthält den Code '"submission.status_filter": "Status",'.
332. Diese Zeile enthält den Code '"submission.status_pending": "En attente",'.
333. Diese Zeile enthält den Code '"submission.status_rejected": "Rejetee",'.
334. Diese Zeile enthält den Code '"submission.submit_button": "Zur Pruefung einreichen",'.
335. Diese Zeile enthält den Code '"submission.submit_hint": "Les soumissions sont verifiees par les admins avant publication.",'.
336. Diese Zeile enthält den Code '"submission.submit_title": "Soumettre une recette",'.
337. Diese Zeile enthält den Code '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
338. Diese Zeile enthält den Code '"submission.table_action": "Aktion",'.
339. Diese Zeile enthält den Code '"submission.table_date": "Datum",'.
340. Diese Zeile enthält den Code '"submission.table_status": "Status",'.
341. Diese Zeile enthält den Code '"submission.table_submitter": "Einreicher",'.
342. Diese Zeile enthält den Code '"submission.table_title": "Titel",'.
343. Diese Zeile enthält den Code '"submission.thank_you": "Merci ! Votre recette a ete soumise pour moderation.",'.
344. Diese Zeile enthält den Code '"submission.title": "Titel",'.
345. Diese Zeile enthält den Code '"submission.updated": "Einreichung wurde aktualisiert."'.
346. Diese Zeile enthält den Code '}'.

## alembic/versions/20260303_0009_recipe_image_change_requests.py

```python
"""add moderation tables for recipe image change requests

Revision ID: 20260303_0009
Revises: 20260303_0008
Create Date: 2026-03-03 21:05:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0009"
down_revision: Union[str, None] = "20260303_0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

image_change_status_enum = sa.Enum(
    "pending",
    "approved",
    "rejected",
    name="image_change_status",
    native_enum=False,
)


def upgrade() -> None:
    op.create_table(
        "recipe_image_change_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requester_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("status", image_change_status_enum, nullable=False, server_default="pending"),
        sa.Column("admin_note", sa.Text(), nullable=True),
        sa.Column("reviewed_by_admin_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_recipe_image_change_requests_recipe_id",
        "recipe_image_change_requests",
        ["recipe_id"],
        unique=False,
    )
    op.create_index(
        "ix_recipe_image_change_requests_requester_user_id",
        "recipe_image_change_requests",
        ["requester_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_recipe_image_change_requests_status",
        "recipe_image_change_requests",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_recipe_image_change_requests_reviewed_by_admin_id",
        "recipe_image_change_requests",
        ["reviewed_by_admin_id"],
        unique=False,
    )
    op.create_index(
        "ix_recipe_image_change_requests_created_at",
        "recipe_image_change_requests",
        ["created_at"],
        unique=False,
    )

    op.create_table(
        "recipe_image_change_files",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "request_id",
            sa.Integer(),
            sa.ForeignKey("recipe_image_change_requests.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("data", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("request_id", name="uq_recipe_image_change_files_request"),
    )
    op.create_index("ix_recipe_image_change_files_request_id", "recipe_image_change_files", ["request_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_recipe_image_change_files_request_id", table_name="recipe_image_change_files")
    op.drop_table("recipe_image_change_files")

    op.drop_index("ix_recipe_image_change_requests_created_at", table_name="recipe_image_change_requests")
    op.drop_index("ix_recipe_image_change_requests_reviewed_by_admin_id", table_name="recipe_image_change_requests")
    op.drop_index("ix_recipe_image_change_requests_status", table_name="recipe_image_change_requests")
    op.drop_index("ix_recipe_image_change_requests_requester_user_id", table_name="recipe_image_change_requests")
    op.drop_index("ix_recipe_image_change_requests_recipe_id", table_name="recipe_image_change_requests")
    op.drop_table("recipe_image_change_requests")

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '"""add moderation tables for recipe image change requests'.
2. Diese Zeile ist leer und trennt Abschnitte.
3. Diese Zeile enthält den Code 'Revision ID: 20260303_0009'.
4. Diese Zeile enthält den Code 'Revises: 20260303_0008'.
5. Diese Zeile enthält den Code 'Create Date: 2026-03-03 21:05:00'.
6. Diese Zeile enthält den Code '"""'.
7. Diese Zeile ist leer und trennt Abschnitte.
8. Diese Zeile enthält den Code 'from typing import Sequence, Union'.
9. Diese Zeile ist leer und trennt Abschnitte.
10. Diese Zeile enthält den Code 'from alembic import op'.
11. Diese Zeile enthält den Code 'import sqlalchemy as sa'.
12. Diese Zeile ist leer und trennt Abschnitte.
13. Diese Zeile enthält den Code '# revision identifiers, used by Alembic.'.
14. Diese Zeile enthält den Code 'revision: str = "20260303_0009"'.
15. Diese Zeile enthält den Code 'down_revision: Union[str, None] = "20260303_0008"'.
16. Diese Zeile enthält den Code 'branch_labels: Union[str, Sequence[str], None] = None'.
17. Diese Zeile enthält den Code 'depends_on: Union[str, Sequence[str], None] = None'.
18. Diese Zeile ist leer und trennt Abschnitte.
19. Diese Zeile enthält den Code 'image_change_status_enum = sa.Enum('.
20. Diese Zeile enthält den Code '"pending",'.
21. Diese Zeile enthält den Code '"approved",'.
22. Diese Zeile enthält den Code '"rejected",'.
23. Diese Zeile enthält den Code 'name="image_change_status",'.
24. Diese Zeile enthält den Code 'native_enum=False,'.
25. Diese Zeile enthält den Code ')'.
26. Diese Zeile ist leer und trennt Abschnitte.
27. Diese Zeile ist leer und trennt Abschnitte.
28. Diese Zeile enthält den Code 'def upgrade() -> None:'.
29. Diese Zeile enthält den Code 'op.create_table('.
30. Diese Zeile enthält den Code '"recipe_image_change_requests",'.
31. Diese Zeile enthält den Code 'sa.Column("id", sa.Integer(), primary_key=True),'.
32. Diese Zeile enthält den Code 'sa.Column("recipe_id", sa.Integer(), sa.ForeignKey("recipes.id", ondelete="CASCADE"), nullable=Fa...'.
33. Diese Zeile enthält den Code 'sa.Column("requester_user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), null...'.
34. Diese Zeile enthält den Code 'sa.Column("status", image_change_status_enum, nullable=False, server_default="pending"),'.
35. Diese Zeile enthält den Code 'sa.Column("admin_note", sa.Text(), nullable=True),'.
36. Diese Zeile enthält den Code 'sa.Column("reviewed_by_admin_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), n...'.
37. Diese Zeile enthält den Code 'sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),'.
38. Diese Zeile enthält den Code 'sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),'.
39. Diese Zeile enthält den Code ')'.
40. Diese Zeile enthält den Code 'op.create_index('.
41. Diese Zeile enthält den Code '"ix_recipe_image_change_requests_recipe_id",'.
42. Diese Zeile enthält den Code '"recipe_image_change_requests",'.
43. Diese Zeile enthält den Code '["recipe_id"],'.
44. Diese Zeile enthält den Code 'unique=False,'.
45. Diese Zeile enthält den Code ')'.
46. Diese Zeile enthält den Code 'op.create_index('.
47. Diese Zeile enthält den Code '"ix_recipe_image_change_requests_requester_user_id",'.
48. Diese Zeile enthält den Code '"recipe_image_change_requests",'.
49. Diese Zeile enthält den Code '["requester_user_id"],'.
50. Diese Zeile enthält den Code 'unique=False,'.
51. Diese Zeile enthält den Code ')'.
52. Diese Zeile enthält den Code 'op.create_index('.
53. Diese Zeile enthält den Code '"ix_recipe_image_change_requests_status",'.
54. Diese Zeile enthält den Code '"recipe_image_change_requests",'.
55. Diese Zeile enthält den Code '["status"],'.
56. Diese Zeile enthält den Code 'unique=False,'.
57. Diese Zeile enthält den Code ')'.
58. Diese Zeile enthält den Code 'op.create_index('.
59. Diese Zeile enthält den Code '"ix_recipe_image_change_requests_reviewed_by_admin_id",'.
60. Diese Zeile enthält den Code '"recipe_image_change_requests",'.
61. Diese Zeile enthält den Code '["reviewed_by_admin_id"],'.
62. Diese Zeile enthält den Code 'unique=False,'.
63. Diese Zeile enthält den Code ')'.
64. Diese Zeile enthält den Code 'op.create_index('.
65. Diese Zeile enthält den Code '"ix_recipe_image_change_requests_created_at",'.
66. Diese Zeile enthält den Code '"recipe_image_change_requests",'.
67. Diese Zeile enthält den Code '["created_at"],'.
68. Diese Zeile enthält den Code 'unique=False,'.
69. Diese Zeile enthält den Code ')'.
70. Diese Zeile ist leer und trennt Abschnitte.
71. Diese Zeile enthält den Code 'op.create_table('.
72. Diese Zeile enthält den Code '"recipe_image_change_files",'.
73. Diese Zeile enthält den Code 'sa.Column("id", sa.Integer(), primary_key=True),'.
74. Diese Zeile enthält den Code 'sa.Column('.
75. Diese Zeile enthält den Code '"request_id",'.
76. Diese Zeile enthält den Code 'sa.Integer(),'.
77. Diese Zeile enthält den Code 'sa.ForeignKey("recipe_image_change_requests.id", ondelete="CASCADE"),'.
78. Diese Zeile enthält den Code 'nullable=False,'.
79. Diese Zeile enthält den Code '),'.
80. Diese Zeile enthält den Code 'sa.Column("filename", sa.String(length=255), nullable=False),'.
81. Diese Zeile enthält den Code 'sa.Column("content_type", sa.String(length=50), nullable=False),'.
82. Diese Zeile enthält den Code 'sa.Column("data", sa.LargeBinary(), nullable=False),'.
83. Diese Zeile enthält den Code 'sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),'.
84. Diese Zeile enthält den Code 'sa.UniqueConstraint("request_id", name="uq_recipe_image_change_files_request"),'.
85. Diese Zeile enthält den Code ')'.
86. Diese Zeile enthält den Code 'op.create_index("ix_recipe_image_change_files_request_id", "recipe_image_change_files", ["request...'.
87. Diese Zeile ist leer und trennt Abschnitte.
88. Diese Zeile ist leer und trennt Abschnitte.
89. Diese Zeile enthält den Code 'def downgrade() -> None:'.
90. Diese Zeile enthält den Code 'op.drop_index("ix_recipe_image_change_files_request_id", table_name="recipe_image_change_files")'.
91. Diese Zeile enthält den Code 'op.drop_table("recipe_image_change_files")'.
92. Diese Zeile ist leer und trennt Abschnitte.
93. Diese Zeile enthält den Code 'op.drop_index("ix_recipe_image_change_requests_created_at", table_name="recipe_image_change_reque...'.
94. Diese Zeile enthält den Code 'op.drop_index("ix_recipe_image_change_requests_reviewed_by_admin_id", table_name="recipe_image_ch...'.
95. Diese Zeile enthält den Code 'op.drop_index("ix_recipe_image_change_requests_status", table_name="recipe_image_change_requests")'.
96. Diese Zeile enthält den Code 'op.drop_index("ix_recipe_image_change_requests_requester_user_id", table_name="recipe_image_chang...'.
97. Diese Zeile enthält den Code 'op.drop_index("ix_recipe_image_change_requests_recipe_id", table_name="recipe_image_change_reques...'.
98. Diese Zeile enthält den Code 'op.drop_table("recipe_image_change_requests")'.

## tests/test_image_change_workflow.py

```python
from io import BytesIO

from PIL import Image
from sqlalchemy import select

from app.config import get_settings
from app.models import Recipe, RecipeImage, RecipeImageChangeRequest, User
from app.security import create_access_token, hash_password


def build_png_bytes() -> bytes:
    buffer = BytesIO()
    Image.new("RGB", (2, 2), color=(32, 128, 96)).save(buffer, format="PNG")
    return buffer.getvalue()


PNG_BYTES = build_png_bytes()


def create_user(db, email: str, role: str = "user") -> tuple[int, str, str]:
    user = User(
        email=email.strip().lower(),
        hashed_password=hash_password("StrongPass123!"),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id, user.user_uid, user.role


def create_recipe(db, creator_id: int, *, source_image_url: str | None = None) -> int:
    recipe = Recipe(
        title="Bildtest Rezept",
        description="Beschreibung",
        instructions="Schritt 1",
        category="Test",
        prep_time_minutes=20,
        difficulty="easy",
        creator_id=creator_id,
        source="test",
        source_image_url=source_image_url,
        is_published=True,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe.id


def auth_client(client, user_uid: str, role: str) -> str:
    token = create_access_token(user_uid, role)
    client.cookies.set("access_token", f"Bearer {token}")
    page = client.get("/")
    assert page.status_code == 200
    csrf = client.cookies.get("csrf_token")
    assert csrf
    return str(csrf)


def test_image_fallback_order(client, db_session_factory):
    with db_session_factory() as db:
        admin_id, _, _ = create_user(db, "fallback-admin@example.local", "admin")
        recipe_id = create_recipe(db, admin_id, source_image_url="https://upload.wikimedia.org/source-image.jpg")

    response = client.get("/")
    assert response.status_code == 200
    assert "https://upload.wikimedia.org/source-image.jpg" in response.text

    with db_session_factory() as db:
        db.add(
            RecipeImage(
                recipe_id=recipe_id,
                filename="primary.png",
                content_type="image/png",
                data=PNG_BYTES,
                is_primary=True,
            )
        )
        db.commit()
        primary_image = db.scalar(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id))
        assert primary_image is not None
        image_id = primary_image.id

    response_with_db_image = client.get("/")
    assert response_with_db_image.status_code == 200
    assert f"/images/{image_id}" in response_with_db_image.text


def test_user_cannot_upload_direct_recipe_image(client, db_session_factory):
    with db_session_factory() as db:
        admin_id, _, _ = create_user(db, "img-admin@example.local", "admin")
        recipe_id = create_recipe(db, admin_id)
        _, user_uid, user_role = create_user(db, "img-user@example.local", "user")

    csrf = auth_client(client, user_uid, user_role)
    response = client.post(
        f"/recipes/{recipe_id}/images",
        data={"set_primary": "true", "csrf_token": csrf},
        files={"file": ("test.png", PNG_BYTES, "image/png")},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 403


def test_user_image_change_request_pending(client, db_session_factory):
    with db_session_factory() as db:
        admin_id, _, _ = create_user(db, "request-admin@example.local", "admin")
        recipe_id = create_recipe(db, admin_id)
        _, user_uid, user_role = create_user(db, "request-user@example.local", "user")

    csrf = auth_client(client, user_uid, user_role)
    response = client.post(
        f"/recipes/{recipe_id}/image-change-request",
        data={"csrf_token": csrf},
        files={"file": ("proposal.png", PNG_BYTES, "image/png")},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}

    with db_session_factory() as db:
        request_row = db.scalar(select(RecipeImageChangeRequest).where(RecipeImageChangeRequest.recipe_id == recipe_id))
        assert request_row is not None
        assert request_row.status == "pending"
        recipe_images = db.scalars(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id)).all()
        assert len(recipe_images) == 0


def test_admin_approves_image_change_creates_primary_image(client, db_session_factory):
    with db_session_factory() as db:
        admin_id, admin_uid, admin_role = create_user(db, "approve-admin@example.local", "admin")
        recipe_id = create_recipe(db, admin_id, source_image_url="https://upload.wikimedia.org/old.jpg")
        existing_image = RecipeImage(
            recipe_id=recipe_id,
            filename="existing.png",
            content_type="image/png",
            data=PNG_BYTES,
            is_primary=True,
        )
        db.add(existing_image)
        _, user_uid, user_role = create_user(db, "approve-user@example.local", "user")
        db.commit()

    csrf_user = auth_client(client, user_uid, user_role)
    create_request = client.post(
        f"/recipes/{recipe_id}/image-change-request",
        data={"csrf_token": csrf_user},
        files={"file": ("new-primary.png", PNG_BYTES, "image/png")},
        headers={"X-CSRF-Token": csrf_user},
        follow_redirects=False,
    )
    assert create_request.status_code in {302, 303}

    with db_session_factory() as db:
        pending_request = db.scalar(
            select(RecipeImageChangeRequest).where(
                RecipeImageChangeRequest.recipe_id == recipe_id,
                RecipeImageChangeRequest.status == "pending",
            )
        )
        assert pending_request is not None
        request_id = pending_request.id

    csrf_admin = auth_client(client, admin_uid, admin_role)
    approve_response = client.post(
        f"/admin/image-change-requests/{request_id}/approve",
        data={"admin_note": "Freigegeben", "csrf_token": csrf_admin},
        headers={"X-CSRF-Token": csrf_admin},
        follow_redirects=False,
    )
    assert approve_response.status_code in {302, 303}

    with db_session_factory() as db:
        approved_request = db.scalar(select(RecipeImageChangeRequest).where(RecipeImageChangeRequest.id == request_id))
        assert approved_request is not None
        assert approved_request.status == "approved"
        images = db.scalars(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id).order_by(RecipeImage.id.asc())).all()
        assert len(images) == 2
        primary_images = [item for item in images if item.is_primary]
        assert len(primary_images) == 1
        assert primary_images[0].filename != "existing.png"


def test_csp_allows_external_images_when_configured(client):
    settings = get_settings()
    original_value = settings.csp_img_src
    settings.csp_img_src = "'self' data: https://upload.wikimedia.org https://kochwiki.org"
    try:
        response = client.get("/")
        assert response.status_code == 200
        csp = response.headers.get("content-security-policy", "")
        assert "img-src 'self' data: https://upload.wikimedia.org https://kochwiki.org" in csp
    finally:
        settings.csp_img_src = original_value

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'from io import BytesIO'.
2. Diese Zeile ist leer und trennt Abschnitte.
3. Diese Zeile enthält den Code 'from PIL import Image'.
4. Diese Zeile enthält den Code 'from sqlalchemy import select'.
5. Diese Zeile ist leer und trennt Abschnitte.
6. Diese Zeile enthält den Code 'from app.config import get_settings'.
7. Diese Zeile enthält den Code 'from app.models import Recipe, RecipeImage, RecipeImageChangeRequest, User'.
8. Diese Zeile enthält den Code 'from app.security import create_access_token, hash_password'.
9. Diese Zeile ist leer und trennt Abschnitte.
10. Diese Zeile ist leer und trennt Abschnitte.
11. Diese Zeile enthält den Code 'def build_png_bytes() -> bytes:'.
12. Diese Zeile enthält den Code 'buffer = BytesIO()'.
13. Diese Zeile enthält den Code 'Image.new("RGB", (2, 2), color=(32, 128, 96)).save(buffer, format="PNG")'.
14. Diese Zeile enthält den Code 'return buffer.getvalue()'.
15. Diese Zeile ist leer und trennt Abschnitte.
16. Diese Zeile ist leer und trennt Abschnitte.
17. Diese Zeile enthält den Code 'PNG_BYTES = build_png_bytes()'.
18. Diese Zeile ist leer und trennt Abschnitte.
19. Diese Zeile ist leer und trennt Abschnitte.
20. Diese Zeile enthält den Code 'def create_user(db, email: str, role: str = "user") -> tuple[int, str, str]:'.
21. Diese Zeile enthält den Code 'user = User('.
22. Diese Zeile enthält den Code 'email=email.strip().lower(),'.
23. Diese Zeile enthält den Code 'hashed_password=hash_password("StrongPass123!"),'.
24. Diese Zeile enthält den Code 'role=role,'.
25. Diese Zeile enthält den Code ')'.
26. Diese Zeile enthält den Code 'db.add(user)'.
27. Diese Zeile enthält den Code 'db.commit()'.
28. Diese Zeile enthält den Code 'db.refresh(user)'.
29. Diese Zeile enthält den Code 'return user.id, user.user_uid, user.role'.
30. Diese Zeile ist leer und trennt Abschnitte.
31. Diese Zeile ist leer und trennt Abschnitte.
32. Diese Zeile enthält den Code 'def create_recipe(db, creator_id: int, *, source_image_url: str | None = None) -> int:'.
33. Diese Zeile enthält den Code 'recipe = Recipe('.
34. Diese Zeile enthält den Code 'title="Bildtest Rezept",'.
35. Diese Zeile enthält den Code 'description="Beschreibung",'.
36. Diese Zeile enthält den Code 'instructions="Schritt 1",'.
37. Diese Zeile enthält den Code 'category="Test",'.
38. Diese Zeile enthält den Code 'prep_time_minutes=20,'.
39. Diese Zeile enthält den Code 'difficulty="easy",'.
40. Diese Zeile enthält den Code 'creator_id=creator_id,'.
41. Diese Zeile enthält den Code 'source="test",'.
42. Diese Zeile enthält den Code 'source_image_url=source_image_url,'.
43. Diese Zeile enthält den Code 'is_published=True,'.
44. Diese Zeile enthält den Code ')'.
45. Diese Zeile enthält den Code 'db.add(recipe)'.
46. Diese Zeile enthält den Code 'db.commit()'.
47. Diese Zeile enthält den Code 'db.refresh(recipe)'.
48. Diese Zeile enthält den Code 'return recipe.id'.
49. Diese Zeile ist leer und trennt Abschnitte.
50. Diese Zeile ist leer und trennt Abschnitte.
51. Diese Zeile enthält den Code 'def auth_client(client, user_uid: str, role: str) -> str:'.
52. Diese Zeile enthält den Code 'token = create_access_token(user_uid, role)'.
53. Diese Zeile enthält den Code 'client.cookies.set("access_token", f"Bearer {token}")'.
54. Diese Zeile enthält den Code 'page = client.get("/")'.
55. Diese Zeile enthält den Code 'assert page.status_code == 200'.
56. Diese Zeile enthält den Code 'csrf = client.cookies.get("csrf_token")'.
57. Diese Zeile enthält den Code 'assert csrf'.
58. Diese Zeile enthält den Code 'return str(csrf)'.
59. Diese Zeile ist leer und trennt Abschnitte.
60. Diese Zeile ist leer und trennt Abschnitte.
61. Diese Zeile enthält den Code 'def test_image_fallback_order(client, db_session_factory):'.
62. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
63. Diese Zeile enthält den Code 'admin_id, _, _ = create_user(db, "fallback-admin@example.local", "admin")'.
64. Diese Zeile enthält den Code 'recipe_id = create_recipe(db, admin_id, source_image_url="https://upload.wikimedia.org/source-ima...'.
65. Diese Zeile ist leer und trennt Abschnitte.
66. Diese Zeile enthält den Code 'response = client.get("/")'.
67. Diese Zeile enthält den Code 'assert response.status_code == 200'.
68. Diese Zeile enthält den Code 'assert "https://upload.wikimedia.org/source-image.jpg" in response.text'.
69. Diese Zeile ist leer und trennt Abschnitte.
70. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
71. Diese Zeile enthält den Code 'db.add('.
72. Diese Zeile enthält den Code 'RecipeImage('.
73. Diese Zeile enthält den Code 'recipe_id=recipe_id,'.
74. Diese Zeile enthält den Code 'filename="primary.png",'.
75. Diese Zeile enthält den Code 'content_type="image/png",'.
76. Diese Zeile enthält den Code 'data=PNG_BYTES,'.
77. Diese Zeile enthält den Code 'is_primary=True,'.
78. Diese Zeile enthält den Code ')'.
79. Diese Zeile enthält den Code ')'.
80. Diese Zeile enthält den Code 'db.commit()'.
81. Diese Zeile enthält den Code 'primary_image = db.scalar(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id))'.
82. Diese Zeile enthält den Code 'assert primary_image is not None'.
83. Diese Zeile enthält den Code 'image_id = primary_image.id'.
84. Diese Zeile ist leer und trennt Abschnitte.
85. Diese Zeile enthält den Code 'response_with_db_image = client.get("/")'.
86. Diese Zeile enthält den Code 'assert response_with_db_image.status_code == 200'.
87. Diese Zeile enthält den Code 'assert f"/images/{image_id}" in response_with_db_image.text'.
88. Diese Zeile ist leer und trennt Abschnitte.
89. Diese Zeile ist leer und trennt Abschnitte.
90. Diese Zeile enthält den Code 'def test_user_cannot_upload_direct_recipe_image(client, db_session_factory):'.
91. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
92. Diese Zeile enthält den Code 'admin_id, _, _ = create_user(db, "img-admin@example.local", "admin")'.
93. Diese Zeile enthält den Code 'recipe_id = create_recipe(db, admin_id)'.
94. Diese Zeile enthält den Code '_, user_uid, user_role = create_user(db, "img-user@example.local", "user")'.
95. Diese Zeile ist leer und trennt Abschnitte.
96. Diese Zeile enthält den Code 'csrf = auth_client(client, user_uid, user_role)'.
97. Diese Zeile enthält den Code 'response = client.post('.
98. Diese Zeile enthält den Code 'f"/recipes/{recipe_id}/images",'.
99. Diese Zeile enthält den Code 'data={"set_primary": "true", "csrf_token": csrf},'.
100. Diese Zeile enthält den Code 'files={"file": ("test.png", PNG_BYTES, "image/png")},'.
101. Diese Zeile enthält den Code 'headers={"X-CSRF-Token": csrf},'.
102. Diese Zeile enthält den Code 'follow_redirects=False,'.
103. Diese Zeile enthält den Code ')'.
104. Diese Zeile enthält den Code 'assert response.status_code == 403'.
105. Diese Zeile ist leer und trennt Abschnitte.
106. Diese Zeile ist leer und trennt Abschnitte.
107. Diese Zeile enthält den Code 'def test_user_image_change_request_pending(client, db_session_factory):'.
108. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
109. Diese Zeile enthält den Code 'admin_id, _, _ = create_user(db, "request-admin@example.local", "admin")'.
110. Diese Zeile enthält den Code 'recipe_id = create_recipe(db, admin_id)'.
111. Diese Zeile enthält den Code '_, user_uid, user_role = create_user(db, "request-user@example.local", "user")'.
112. Diese Zeile ist leer und trennt Abschnitte.
113. Diese Zeile enthält den Code 'csrf = auth_client(client, user_uid, user_role)'.
114. Diese Zeile enthält den Code 'response = client.post('.
115. Diese Zeile enthält den Code 'f"/recipes/{recipe_id}/image-change-request",'.
116. Diese Zeile enthält den Code 'data={"csrf_token": csrf},'.
117. Diese Zeile enthält den Code 'files={"file": ("proposal.png", PNG_BYTES, "image/png")},'.
118. Diese Zeile enthält den Code 'headers={"X-CSRF-Token": csrf},'.
119. Diese Zeile enthält den Code 'follow_redirects=False,'.
120. Diese Zeile enthält den Code ')'.
121. Diese Zeile enthält den Code 'assert response.status_code in {302, 303}'.
122. Diese Zeile ist leer und trennt Abschnitte.
123. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
124. Diese Zeile enthält den Code 'request_row = db.scalar(select(RecipeImageChangeRequest).where(RecipeImageChangeRequest.recipe_id...'.
125. Diese Zeile enthält den Code 'assert request_row is not None'.
126. Diese Zeile enthält den Code 'assert request_row.status == "pending"'.
127. Diese Zeile enthält den Code 'recipe_images = db.scalars(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id)).all()'.
128. Diese Zeile enthält den Code 'assert len(recipe_images) == 0'.
129. Diese Zeile ist leer und trennt Abschnitte.
130. Diese Zeile ist leer und trennt Abschnitte.
131. Diese Zeile enthält den Code 'def test_admin_approves_image_change_creates_primary_image(client, db_session_factory):'.
132. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
133. Diese Zeile enthält den Code 'admin_id, admin_uid, admin_role = create_user(db, "approve-admin@example.local", "admin")'.
134. Diese Zeile enthält den Code 'recipe_id = create_recipe(db, admin_id, source_image_url="https://upload.wikimedia.org/old.jpg")'.
135. Diese Zeile enthält den Code 'existing_image = RecipeImage('.
136. Diese Zeile enthält den Code 'recipe_id=recipe_id,'.
137. Diese Zeile enthält den Code 'filename="existing.png",'.
138. Diese Zeile enthält den Code 'content_type="image/png",'.
139. Diese Zeile enthält den Code 'data=PNG_BYTES,'.
140. Diese Zeile enthält den Code 'is_primary=True,'.
141. Diese Zeile enthält den Code ')'.
142. Diese Zeile enthält den Code 'db.add(existing_image)'.
143. Diese Zeile enthält den Code '_, user_uid, user_role = create_user(db, "approve-user@example.local", "user")'.
144. Diese Zeile enthält den Code 'db.commit()'.
145. Diese Zeile ist leer und trennt Abschnitte.
146. Diese Zeile enthält den Code 'csrf_user = auth_client(client, user_uid, user_role)'.
147. Diese Zeile enthält den Code 'create_request = client.post('.
148. Diese Zeile enthält den Code 'f"/recipes/{recipe_id}/image-change-request",'.
149. Diese Zeile enthält den Code 'data={"csrf_token": csrf_user},'.
150. Diese Zeile enthält den Code 'files={"file": ("new-primary.png", PNG_BYTES, "image/png")},'.
151. Diese Zeile enthält den Code 'headers={"X-CSRF-Token": csrf_user},'.
152. Diese Zeile enthält den Code 'follow_redirects=False,'.
153. Diese Zeile enthält den Code ')'.
154. Diese Zeile enthält den Code 'assert create_request.status_code in {302, 303}'.
155. Diese Zeile ist leer und trennt Abschnitte.
156. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
157. Diese Zeile enthält den Code 'pending_request = db.scalar('.
158. Diese Zeile enthält den Code 'select(RecipeImageChangeRequest).where('.
159. Diese Zeile enthält den Code 'RecipeImageChangeRequest.recipe_id == recipe_id,'.
160. Diese Zeile enthält den Code 'RecipeImageChangeRequest.status == "pending",'.
161. Diese Zeile enthält den Code ')'.
162. Diese Zeile enthält den Code ')'.
163. Diese Zeile enthält den Code 'assert pending_request is not None'.
164. Diese Zeile enthält den Code 'request_id = pending_request.id'.
165. Diese Zeile ist leer und trennt Abschnitte.
166. Diese Zeile enthält den Code 'csrf_admin = auth_client(client, admin_uid, admin_role)'.
167. Diese Zeile enthält den Code 'approve_response = client.post('.
168. Diese Zeile enthält den Code 'f"/admin/image-change-requests/{request_id}/approve",'.
169. Diese Zeile enthält den Code 'data={"admin_note": "Freigegeben", "csrf_token": csrf_admin},'.
170. Diese Zeile enthält den Code 'headers={"X-CSRF-Token": csrf_admin},'.
171. Diese Zeile enthält den Code 'follow_redirects=False,'.
172. Diese Zeile enthält den Code ')'.
173. Diese Zeile enthält den Code 'assert approve_response.status_code in {302, 303}'.
174. Diese Zeile ist leer und trennt Abschnitte.
175. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
176. Diese Zeile enthält den Code 'approved_request = db.scalar(select(RecipeImageChangeRequest).where(RecipeImageChangeRequest.id =...'.
177. Diese Zeile enthält den Code 'assert approved_request is not None'.
178. Diese Zeile enthält den Code 'assert approved_request.status == "approved"'.
179. Diese Zeile enthält den Code 'images = db.scalars(select(RecipeImage).where(RecipeImage.recipe_id == recipe_id).order_by(Recipe...'.
180. Diese Zeile enthält den Code 'assert len(images) == 2'.
181. Diese Zeile enthält den Code 'primary_images = [item for item in images if item.is_primary]'.
182. Diese Zeile enthält den Code 'assert len(primary_images) == 1'.
183. Diese Zeile enthält den Code 'assert primary_images[0].filename != "existing.png"'.
184. Diese Zeile ist leer und trennt Abschnitte.
185. Diese Zeile ist leer und trennt Abschnitte.
186. Diese Zeile enthält den Code 'def test_csp_allows_external_images_when_configured(client):'.
187. Diese Zeile enthält den Code 'settings = get_settings()'.
188. Diese Zeile enthält den Code 'original_value = settings.csp_img_src'.
189. Diese Zeile enthält den Code 'settings.csp_img_src = "'self' data: https://upload.wikimedia.org https://kochwiki.org"'.
190. Diese Zeile enthält den Code 'try:'.
191. Diese Zeile enthält den Code 'response = client.get("/")'.
192. Diese Zeile enthält den Code 'assert response.status_code == 200'.
193. Diese Zeile enthält den Code 'csp = response.headers.get("content-security-policy", "")'.
194. Diese Zeile enthält den Code 'assert "img-src 'self' data: https://upload.wikimedia.org https://kochwiki.org" in csp'.
195. Diese Zeile enthält den Code 'finally:'.
196. Diese Zeile enthält den Code 'settings.csp_img_src = original_value'.


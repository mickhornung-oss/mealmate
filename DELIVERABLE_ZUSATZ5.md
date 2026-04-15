# Projektstruktur
```text
.
|-- .env.example
|-- requirements.txt
|-- README_SECURITY.md
`-- app/
    |-- config.py
    |-- dependencies.py
    |-- image_utils.py
    |-- logging_config.py
    |-- main.py
    |-- middleware.py
    |-- rate_limit.py
    |-- security.py
    |-- services.py
    |-- routers/
    |   |-- admin.py
    |   |-- auth.py
    |   `-- recipes.py
    |-- static/
    |   |-- htmx.min.js
    |   `-- security.js
    `-- templates/
        |-- admin.html
        |-- base.html
        |-- error_404.html
        `-- error_500.html
```

## .env.example
```dotenv
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
CSRF_COOKIE_NAME=csrf_token
CSRF_HEADER_NAME=X-CSRF-Token
MAX_UPLOAD_MB=4
MAX_CSV_UPLOAD_MB=10
ALLOWED_IMAGE_TYPES=image/png,image/jpeg,image/webp
AUTO_SEED_KOCHWIKI=0
KOCHWIKI_CSV_PATH=rezepte_kochwiki_clean_3713.csv
IMPORT_DOWNLOAD_IMAGES=0
SEED_ADMIN_EMAIL=admin@mealmate.local
SEED_ADMIN_PASSWORD=AdminPass123!
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt einen Teil der Implementierung um.
2. Diese Zeile setzt einen Teil der Implementierung um.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.

## requirements.txt
```text
fastapi==0.116.1
uvicorn[standard]==0.35.0
gunicorn==23.0.0
jinja2==3.1.6
sqlalchemy==2.0.43
alembic==1.16.5
python-jose[cryptography]==3.5.0
pwdlib==0.2.1
argon2-cffi==25.1.0
python-multipart==0.0.20
pydantic-settings==2.10.1
reportlab==4.4.4
pillow==11.3.0
psycopg[binary]==3.2.13
slowapi==0.1.9
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt einen Teil der Implementierung um.
2. Diese Zeile setzt einen Teil der Implementierung um.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.

## app/config.py
```python
from functools import lru_cache
from typing import Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    app_name: str = "MealMate"
    app_env: Literal["dev", "prod"] = "dev"
    app_url: AnyHttpUrl = "http://localhost:8000"
    secret_key: str = "change-me"
    algorithm: str = "HS256"
    token_expire_minutes: int = 60
    database_url: str = "sqlite:///./mealmate.db"
    allowed_hosts: list[str] = ["*"]
    cookie_secure: bool | None = None
    force_https: bool | None = None
    log_level: str = "INFO"
    csrf_cookie_name: str = "csrf_token"
    csrf_header_name: str = "X-CSRF-Token"
    max_upload_mb: int = 4
    max_csv_upload_mb: int = 10
    allowed_image_types: list[str] = ["image/png", "image/jpeg", "image/webp"]
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
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile ist bewusst leer.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist bewusst leer.
7. Diese Zeile ist bewusst leer.
8. Diese Zeile startet eine Klassendefinition.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile ist bewusst leer.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile ist bewusst leer.
33. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
34. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
35. Diese Zeile startet eine Funktionsdefinition.
36. Diese Zeile steuert einen bedingten Ablauf.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile ist bewusst leer.
40. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
41. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
42. Diese Zeile startet eine Funktionsdefinition.
43. Diese Zeile steuert einen bedingten Ablauf.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile steuert einen bedingten Ablauf.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile ist bewusst leer.
49. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
50. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
51. Diese Zeile startet eine Funktionsdefinition.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile ist bewusst leer.
54. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
55. Diese Zeile startet eine Funktionsdefinition.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile steuert einen bedingten Ablauf.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile steuert einen bedingten Ablauf.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile ist bewusst leer.
63. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
64. Diese Zeile startet eine Funktionsdefinition.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile ist bewusst leer.
67. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
68. Diese Zeile startet eine Funktionsdefinition.
69. Diese Zeile setzt einen Teil der Implementierung um.
70. Diese Zeile ist bewusst leer.
71. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
72. Diese Zeile startet eine Funktionsdefinition.
73. Diese Zeile steuert einen bedingten Ablauf.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile ist bewusst leer.
77. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
78. Diese Zeile startet eine Funktionsdefinition.
79. Diese Zeile steuert einen bedingten Ablauf.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile ist bewusst leer.
83. Diese Zeile ist bewusst leer.
84. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
85. Diese Zeile startet eine Funktionsdefinition.
86. Diese Zeile setzt einen Teil der Implementierung um.

## app/dependencies.py
```python
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required.")
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
    }
    base.update(kwargs)
    return base
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile ist bewusst leer.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist bewusst leer.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile importiert benoetigte Abhaengigkeiten.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile ist bewusst leer.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile ist bewusst leer.
15. Diese Zeile ist bewusst leer.
16. Diese Zeile startet eine Funktionsdefinition.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile steuert einen bedingten Ablauf.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile gehoert zur Fehlerbehandlung.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile gehoert zur Fehlerbehandlung.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile steuert einen bedingten Ablauf.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile steuert einen bedingten Ablauf.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile ist bewusst leer.
36. Diese Zeile ist bewusst leer.
37. Diese Zeile startet eine Funktionsdefinition.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile steuert einen bedingten Ablauf.
40. Diese Zeile setzt einen Teil der Implementierung um.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile ist bewusst leer.
43. Diese Zeile ist bewusst leer.
44. Diese Zeile startet eine Funktionsdefinition.
45. Diese Zeile steuert einen bedingten Ablauf.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile ist bewusst leer.
49. Diese Zeile ist bewusst leer.
50. Diese Zeile startet eine Funktionsdefinition.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.

## app/image_utils.py
```python
import io
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from app.config import get_settings

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
        raise ImageValidationError("Unsupported MIME type.")
    if content_type == "image/webp":
        if not (file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP"):
            raise ImageValidationError("Invalid WEBP file signature.")
        return
    if not any(file_bytes.startswith(sig) for sig in signatures):
        raise ImageValidationError("File signature does not match content type.")


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
    except (UnidentifiedImageError, OSError) as exc:
        raise ImageValidationError("Uploaded file is not a valid image.") from exc
    if expected_format and actual_format != expected_format:
        raise ImageValidationError("Image format does not match content type.")


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
        raise ImageValidationError(f"Unsupported MIME type '{content_type}'.")
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ImageValidationError(f"Image too large. Max size is {settings.max_upload_mb} MB.", status_code=413)
    if len(file_bytes) < 12:
        raise ImageValidationError("Uploaded file is too small to be a valid image.")
    _validate_magic_bytes(content_type, file_bytes)
    _validate_image_decode(content_type, file_bytes)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile ist bewusst leer.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist bewusst leer.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile ist bewusst leer.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile ist bewusst leer.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile ist bewusst leer.
17. Diese Zeile ist bewusst leer.
18. Diese Zeile startet eine Klassendefinition.
19. Diese Zeile startet eine Funktionsdefinition.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile ist bewusst leer.
23. Diese Zeile ist bewusst leer.
24. Diese Zeile startet eine Funktionsdefinition.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile steuert einen bedingten Ablauf.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile steuert einen bedingten Ablauf.
29. Diese Zeile steuert einen bedingten Ablauf.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile steuert einen bedingten Ablauf.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile ist bewusst leer.
35. Diese Zeile ist bewusst leer.
36. Diese Zeile startet eine Funktionsdefinition.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile setzt einen Teil der Implementierung um.
40. Diese Zeile setzt einen Teil der Implementierung um.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile gehoert zur Fehlerbehandlung.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile gehoert zur Fehlerbehandlung.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile steuert einen bedingten Ablauf.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile ist bewusst leer.
51. Diese Zeile ist bewusst leer.
52. Diese Zeile startet eine Funktionsdefinition.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile steuert einen bedingten Ablauf.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile ist bewusst leer.
63. Diese Zeile ist bewusst leer.
64. Diese Zeile startet eine Funktionsdefinition.
65. Diese Zeile steuert einen bedingten Ablauf.
66. Diese Zeile setzt einen Teil der Implementierung um.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile steuert einen bedingten Ablauf.
69. Diese Zeile setzt einen Teil der Implementierung um.
70. Diese Zeile steuert einen bedingten Ablauf.
71. Diese Zeile setzt einen Teil der Implementierung um.
72. Diese Zeile setzt einen Teil der Implementierung um.
73. Diese Zeile setzt einen Teil der Implementierung um.

## app/logging_config.py
```python
import logging

from app.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    level_name = settings.log_level
    level = getattr(logging, level_name, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    logging.getLogger("uvicorn.error").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile ist bewusst leer.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile ist bewusst leer.
5. Diese Zeile ist bewusst leer.
6. Diese Zeile startet eine Funktionsdefinition.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.

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
from app.logging_config import configure_logging
from app.middleware import CSRFMiddleware, HTTPSRedirectMiddleware, RequestContextMiddleware, SecurityHeadersMiddleware
from app.models import Recipe, User
from app.rate_limit import limiter
from app.routers import admin, auth, recipes
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
app.include_router(admin.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    accept = request.headers.get("accept", "")
    if exc.status_code == 404 and "text/html" in accept:
        return templates.TemplateResponse(
            "error_404.html",
            template_context(request, None, title="404 - Not Found"),
            status_code=404,
        )
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", "-")
    logger.exception("unhandled_exception request_id=%s path=%s", request_id, request.url.path)
    accept = request.headers.get("accept", "")
    if settings.prod_mode:
        if "text/html" in accept:
            return templates.TemplateResponse(
                "error_500.html",
                template_context(request, None, title="500 - Internal Server Error", show_trace=False, error_trace=None),
                status_code=500,
            )
        return JSONResponse({"detail": "Internal server error."}, status_code=500)
    trace = traceback.format_exc()
    if "text/html" in accept:
        return templates.TemplateResponse(
            "error_500.html",
            template_context(request, None, title="500 - Internal Server Error", show_trace=True, error_trace=trace),
            status_code=500,
        )
    return JSONResponse({"detail": "Internal server error.", "trace": trace}, status_code=500)


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
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile ist bewusst leer.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile importiert benoetigte Abhaengigkeiten.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile importiert benoetigte Abhaengigkeiten.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile importiert benoetigte Abhaengigkeiten.
13. Diese Zeile importiert benoetigte Abhaengigkeiten.
14. Diese Zeile importiert benoetigte Abhaengigkeiten.
15. Diese Zeile ist bewusst leer.
16. Diese Zeile importiert benoetigte Abhaengigkeiten.
17. Diese Zeile importiert benoetigte Abhaengigkeiten.
18. Diese Zeile importiert benoetigte Abhaengigkeiten.
19. Diese Zeile importiert benoetigte Abhaengigkeiten.
20. Diese Zeile importiert benoetigte Abhaengigkeiten.
21. Diese Zeile importiert benoetigte Abhaengigkeiten.
22. Diese Zeile importiert benoetigte Abhaengigkeiten.
23. Diese Zeile importiert benoetigte Abhaengigkeiten.
24. Diese Zeile importiert benoetigte Abhaengigkeiten.
25. Diese Zeile importiert benoetigte Abhaengigkeiten.
26. Diese Zeile importiert benoetigte Abhaengigkeiten.
27. Diese Zeile ist bewusst leer.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile ist bewusst leer.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile ist bewusst leer.
34. Diese Zeile ist bewusst leer.
35. Diese Zeile startet eine Klassendefinition.
36. Diese Zeile startet eine Funktionsdefinition.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile ist bewusst leer.
40. Diese Zeile startet eine Funktionsdefinition.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile steuert einen bedingten Ablauf.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile ist bewusst leer.
46. Diese Zeile ist bewusst leer.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile steuert einen bedingten Ablauf.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile ist bewusst leer.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile ist bewusst leer.
63. Diese Zeile setzt einen Teil der Implementierung um.
64. Diese Zeile setzt einen Teil der Implementierung um.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile ist bewusst leer.
67. Diese Zeile ist bewusst leer.
68. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
69. Diese Zeile startet eine Funktionsdefinition.
70. Diese Zeile setzt einen Teil der Implementierung um.
71. Diese Zeile steuert einen bedingten Ablauf.
72. Diese Zeile setzt einen Teil der Implementierung um.
73. Diese Zeile setzt einen Teil der Implementierung um.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile ist bewusst leer.
79. Diese Zeile ist bewusst leer.
80. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
81. Diese Zeile startet eine Funktionsdefinition.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile setzt einen Teil der Implementierung um.
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile steuert einen bedingten Ablauf.
86. Diese Zeile steuert einen bedingten Ablauf.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile setzt einen Teil der Implementierung um.
89. Diese Zeile setzt einen Teil der Implementierung um.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile steuert einen bedingten Ablauf.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile ist bewusst leer.
102. Diese Zeile ist bewusst leer.
103. Diese Zeile startet eine Funktionsdefinition.
104. Diese Zeile setzt einen Teil der Implementierung um.
105. Diese Zeile steuert einen bedingten Ablauf.
106. Diese Zeile setzt einen Teil der Implementierung um.
107. Diese Zeile setzt einen Teil der Implementierung um.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile steuert einen bedingten Ablauf.
110. Diese Zeile setzt einen Teil der Implementierung um.
111. Diese Zeile setzt einen Teil der Implementierung um.
112. Diese Zeile setzt einen Teil der Implementierung um.
113. Diese Zeile setzt einen Teil der Implementierung um.
114. Diese Zeile setzt einen Teil der Implementierung um.
115. Diese Zeile setzt einen Teil der Implementierung um.
116. Diese Zeile setzt einen Teil der Implementierung um.
117. Diese Zeile setzt einen Teil der Implementierung um.
118. Diese Zeile setzt einen Teil der Implementierung um.
119. Diese Zeile setzt einen Teil der Implementierung um.
120. Diese Zeile setzt einen Teil der Implementierung um.
121. Diese Zeile setzt einen Teil der Implementierung um.
122. Diese Zeile setzt einen Teil der Implementierung um.
123. Diese Zeile ist bewusst leer.
124. Diese Zeile ist bewusst leer.
125. Diese Zeile startet eine Funktionsdefinition.
126. Diese Zeile steuert einen bedingten Ablauf.
127. Diese Zeile setzt einen Teil der Implementierung um.
128. Diese Zeile setzt einen Teil der Implementierung um.
129. Diese Zeile gehoert zur Fehlerbehandlung.
130. Diese Zeile steuert einen bedingten Ablauf.
131. Diese Zeile setzt einen Teil der Implementierung um.
132. Diese Zeile setzt einen Teil der Implementierung um.
133. Diese Zeile steuert einen bedingten Ablauf.
134. Diese Zeile setzt einen Teil der Implementierung um.
135. Diese Zeile setzt einen Teil der Implementierung um.
136. Diese Zeile steuert einen bedingten Ablauf.
137. Diese Zeile setzt einen Teil der Implementierung um.
138. Diese Zeile setzt einen Teil der Implementierung um.
139. Diese Zeile setzt einen Teil der Implementierung um.
140. Diese Zeile steuert einen bedingten Ablauf.
141. Diese Zeile setzt einen Teil der Implementierung um.
142. Diese Zeile setzt einen Teil der Implementierung um.
143. Diese Zeile setzt einen Teil der Implementierung um.
144. Diese Zeile setzt einen Teil der Implementierung um.
145. Diese Zeile setzt einen Teil der Implementierung um.
146. Diese Zeile setzt einen Teil der Implementierung um.
147. Diese Zeile setzt einen Teil der Implementierung um.
148. Diese Zeile setzt einen Teil der Implementierung um.
149. Diese Zeile setzt einen Teil der Implementierung um.
150. Diese Zeile setzt einen Teil der Implementierung um.
151. Diese Zeile gehoert zur Fehlerbehandlung.
152. Diese Zeile setzt einen Teil der Implementierung um.
153. Diese Zeile ist bewusst leer.
154. Diese Zeile ist bewusst leer.
155. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
156. Diese Zeile startet eine Funktionsdefinition.
157. Diese Zeile setzt einen Teil der Implementierung um.
158. Diese Zeile ist bewusst leer.
159. Diese Zeile ist bewusst leer.
160. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
161. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
162. Diese Zeile startet eine Funktionsdefinition.
163. Diese Zeile setzt einen Teil der Implementierung um.

## app/middleware.py
```python
import logging
import secrets
import time
import uuid

from fastapi import Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger("mealmate.request")

SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}
CSRF_EXEMPT_PREFIXES = ("/health", "/healthz", "/static")


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

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        cookie_name = settings.csrf_cookie_name
        header_name = settings.csrf_header_name
        csrf_cookie = request.cookies.get(cookie_name)
        if request.method in SAFE_METHODS:
            request.state.csrf_token = csrf_cookie or secrets.token_urlsafe(32)
        elif not self._is_exempt(path):
            provided = request.headers.get(header_name)
            if not provided:
                content_type = (request.headers.get("content-type") or "").lower()
                if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
                    try:
                        form = await request.form()
                    except Exception:
                        form = None
                    if form is not None:
                        provided = str(form.get("csrf_token") or "")
            if not csrf_cookie or not provided or not secrets.compare_digest(provided, csrf_cookie):
                return PlainTextResponse("CSRF validation failed.", status_code=403)
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
        csp_parts = [
            "default-src 'self'",
            "img-src 'self' data: https:",
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
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile ist bewusst leer.
6. Diese Zeile importiert benoetigte Abhaengigkeiten.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile ist bewusst leer.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile ist bewusst leer.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile ist bewusst leer.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile ist bewusst leer.
18. Diese Zeile ist bewusst leer.
19. Diese Zeile startet eine Klassendefinition.
20. Diese Zeile startet eine Funktionsdefinition.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile gehoert zur Fehlerbehandlung.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile gehoert zur Fehlerbehandlung.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile setzt einen Teil der Implementierung um.
40. Diese Zeile setzt einen Teil der Implementierung um.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile ist bewusst leer.
46. Diese Zeile ist bewusst leer.
47. Diese Zeile startet eine Klassendefinition.
48. Diese Zeile startet eine Funktionsdefinition.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile ist bewusst leer.
51. Diese Zeile startet eine Funktionsdefinition.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile steuert einen bedingten Ablauf.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile steuert einen bedingten Ablauf.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile steuert einen bedingten Ablauf.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile steuert einen bedingten Ablauf.
63. Diese Zeile gehoert zur Fehlerbehandlung.
64. Diese Zeile setzt einen Teil der Implementierung um.
65. Diese Zeile gehoert zur Fehlerbehandlung.
66. Diese Zeile setzt einen Teil der Implementierung um.
67. Diese Zeile steuert einen bedingten Ablauf.
68. Diese Zeile setzt einen Teil der Implementierung um.
69. Diese Zeile steuert einen bedingten Ablauf.
70. Diese Zeile setzt einen Teil der Implementierung um.
71. Diese Zeile setzt einen Teil der Implementierung um.
72. Diese Zeile setzt einen Teil der Implementierung um.
73. Diese Zeile steuert einen bedingten Ablauf.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile setzt einen Teil der Implementierung um.
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile ist bewusst leer.
86. Diese Zeile ist bewusst leer.
87. Diese Zeile startet eine Klassendefinition.
88. Diese Zeile startet eine Funktionsdefinition.
89. Diese Zeile steuert einen bedingten Ablauf.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile ist bewusst leer.
94. Diese Zeile ist bewusst leer.
95. Diese Zeile startet eine Klassendefinition.
96. Diese Zeile startet eine Funktionsdefinition.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile setzt einen Teil der Implementierung um.
104. Diese Zeile setzt einen Teil der Implementierung um.
105. Diese Zeile setzt einen Teil der Implementierung um.
106. Diese Zeile setzt einen Teil der Implementierung um.
107. Diese Zeile setzt einen Teil der Implementierung um.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile setzt einen Teil der Implementierung um.
110. Diese Zeile setzt einen Teil der Implementierung um.
111. Diese Zeile setzt einen Teil der Implementierung um.
112. Diese Zeile steuert einen bedingten Ablauf.
113. Diese Zeile setzt einen Teil der Implementierung um.
114. Diese Zeile setzt einen Teil der Implementierung um.

## app/rate_limit.py
```python
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.security import decode_access_token
from app.services import extract_token


def key_by_ip(request: Request) -> str:
    return get_remote_address(request)


def key_by_user_or_ip(request: Request) -> str:
    state_user_key = getattr(request.state, "rate_limit_user_key", None)
    if state_user_key:
        return str(state_user_key)
    token = extract_token(request.cookies.get("access_token"))
    if not token:
        token = extract_token(request.headers.get("Authorization"))
    if token:
        try:
            payload = decode_access_token(token)
            subject = str(payload.get("sub", "")).strip().lower()
            if subject:
                return f"user:{subject}"
        except ValueError:
            pass
    return key_by_ip(request)


limiter = Limiter(key_func=key_by_ip, headers_enabled=True)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile ist bewusst leer.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile importiert benoetigte Abhaengigkeiten.
7. Diese Zeile ist bewusst leer.
8. Diese Zeile ist bewusst leer.
9. Diese Zeile startet eine Funktionsdefinition.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile ist bewusst leer.
12. Diese Zeile ist bewusst leer.
13. Diese Zeile startet eine Funktionsdefinition.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile steuert einen bedingten Ablauf.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile steuert einen bedingten Ablauf.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile steuert einen bedingten Ablauf.
21. Diese Zeile gehoert zur Fehlerbehandlung.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile steuert einen bedingten Ablauf.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile gehoert zur Fehlerbehandlung.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile ist bewusst leer.
30. Diese Zeile ist bewusst leer.
31. Diese Zeile setzt einen Teil der Implementierung um.

## app/security.py
```python
from datetime import datetime, timedelta, timezone
import re

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.config import get_settings

password_hash = PasswordHash.recommended()
settings = get_settings()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def validate_password_policy(password: str) -> str | None:
    if len(password) < 10:
        return "Password must contain at least 10 characters."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one number."
    if not re.search(r"[^A-Za-z0-9]", password):
        return "Password must contain at least one special character."
    return None


def create_access_token(subject: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, str]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile ist bewusst leer.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist bewusst leer.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile ist bewusst leer.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile ist bewusst leer.
12. Diese Zeile ist bewusst leer.
13. Diese Zeile startet eine Funktionsdefinition.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile ist bewusst leer.
16. Diese Zeile ist bewusst leer.
17. Diese Zeile startet eine Funktionsdefinition.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile ist bewusst leer.
20. Diese Zeile ist bewusst leer.
21. Diese Zeile startet eine Funktionsdefinition.
22. Diese Zeile steuert einen bedingten Ablauf.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile steuert einen bedingten Ablauf.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile steuert einen bedingten Ablauf.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile steuert einen bedingten Ablauf.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile ist bewusst leer.
32. Diese Zeile ist bewusst leer.
33. Diese Zeile startet eine Funktionsdefinition.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile ist bewusst leer.
38. Diese Zeile ist bewusst leer.
39. Diese Zeile startet eine Funktionsdefinition.
40. Diese Zeile gehoert zur Fehlerbehandlung.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile gehoert zur Fehlerbehandlung.
43. Diese Zeile setzt einen Teil der Implementierung um.

## app/services.py
```python
import csv
import html
import io
import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from PIL import Image, UnidentifiedImageError
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import AppMeta, Ingredient, Recipe, RecipeImage, RecipeIngredient, User

settings = get_settings()

ALLOWED_DIFFICULTIES = {"easy", "medium", "hard"}
IMPORT_MODE = Literal["insert_only", "update_existing"]


@dataclass
class CSVImportReport:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def parse_ingredient_text(raw: str) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for line in raw.splitlines():
        normalized = line.strip()
        if not normalized:
            continue
        parts = [part.strip() for part in normalized.split("|")]
        if len(parts) == 1:
            items.append({"name": parts[0], "quantity_text": "", "grams": None})
            continue
        if len(parts) == 2:
            items.append({"name": parts[0], "quantity_text": parts[1], "grams": None})
            continue
        grams = parse_optional_int(parts[2])
        items.append({"name": parts[0], "quantity_text": parts[1], "grams": grams})
    return items


def parse_optional_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = str(value).strip()
    if not text:
        return None
    match = re.search(r"\d+", text)
    return int(match.group(0)) if match else None


def sanitize_difficulty(value: str) -> str:
    normalized = value.strip().lower()
    german_map = {"leicht": "easy", "mittel": "medium", "schwer": "hard"}
    normalized = german_map.get(normalized, normalized)
    if normalized not in ALLOWED_DIFFICULTIES:
        return "medium"
    return normalized


def normalize_ingredient_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def parse_list_like(raw_value: Any) -> list[str]:
    if isinstance(raw_value, list):
        return [str(item).strip() for item in raw_value if str(item).strip()]
    if raw_value is None:
        return []
    value = str(raw_value).strip()
    if not value:
        return []
    if value.startswith("[") and value.endswith("]"):
        try:
            loaded = json.loads(value)
        except json.JSONDecodeError:
            loaded = None
        if isinstance(loaded, list):
            return [str(item).strip() for item in loaded if str(item).strip()]
    separator = "\n" if "\n" in value else ","
    return [item.strip().strip('"') for item in value.split(separator) if item.strip()]


def parse_text_block(raw_value: Any) -> str:
    parts = parse_list_like(raw_value)
    if parts:
        return "\n".join(parts)
    return str(raw_value or "").strip()


def get_or_create_ingredient(db: Session, name: str) -> Ingredient:
    normalized = normalize_ingredient_name(name)
    ingredient = db.scalar(select(Ingredient).where(Ingredient.name == normalized))
    if ingredient:
        return ingredient
    ingredient = Ingredient(name=normalized)
    db.add(ingredient)
    db.flush()
    return ingredient


def replace_recipe_ingredients(db: Session, recipe: Recipe, ingredient_entries: list[dict[str, Any]]) -> None:
    recipe.recipe_ingredients.clear()
    merged_entries: dict[str, dict[str, Any]] = {}
    for entry in ingredient_entries:
        name = str(entry.get("name") or "").strip()
        if not name:
            continue
        key = normalize_ingredient_name(name)
        quantity_text = str(entry.get("quantity_text") or "").strip()
        grams = parse_optional_int(entry.get("grams"))
        if key not in merged_entries:
            merged_entries[key] = {"name": name, "quantity_text": quantity_text, "grams": grams}
            continue
        current = merged_entries[key]
        if quantity_text:
            if current["quantity_text"]:
                current["quantity_text"] = f"{current['quantity_text']} | {quantity_text}"
            else:
                current["quantity_text"] = quantity_text
        if current["grams"] is None and grams is not None:
            current["grams"] = grams
    for merged in merged_entries.values():
        ingredient = get_or_create_ingredient(db, merged["name"])
        db.add(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient,
                quantity_text=merged["quantity_text"],
                grams=merged["grams"],
            )
        )


def validate_upload(content_type: str, file_size_bytes: int, file_bytes: bytes | None = None) -> None:
    if content_type not in settings.allowed_image_types:
        raise ValueError(f"Unsupported MIME type '{content_type}'.")
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise ValueError(f"Image too large. Max size is {settings.max_upload_mb} MB.")
    if file_bytes is not None:
        try:
            with Image.open(io.BytesIO(file_bytes)) as image:
                image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("Uploaded file is not a valid image.") from exc


@lru_cache(maxsize=4096)
def resolve_title_image_url(image_url: str) -> str | None:
    cleaned = image_url.strip()
    if not cleaned:
        return None
    lower = cleaned.lower()
    if "kein_bild" in lower:
        return None
    if lower.endswith((".jpg", ".jpeg", ".png", ".webp")) and "/wiki/" not in lower:
        return cleaned
    parsed = urlparse(cleaned)
    host = parsed.netloc.lower()
    path = unquote(parsed.path).lower()
    if "kochwiki.org" in host and "/wiki/" in parsed.path and "datei" in path:
        request = Request(cleaned, headers={"User-Agent": "MealMate/1.0"})
        with urlopen(request, timeout=12) as response:
            html_text = response.read(300_000).decode("utf-8", errors="ignore")
        match = re.search(
            r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
            html_text,
            flags=re.IGNORECASE,
        )
        if match:
            return html.unescape(match.group(1))
    return cleaned


def extract_token(raw_header: str | None) -> str | None:
    if not raw_header:
        return None
    prefix = "Bearer "
    if raw_header.startswith(prefix):
        return raw_header[len(prefix) :].strip()
    return raw_header.strip()


def can_manage_recipe(current_user: User, recipe: Recipe) -> bool:
    return current_user.role == "admin" or recipe.creator_id == current_user.id


def get_meta_value(db: Session, key: str) -> str | None:
    meta = db.scalar(select(AppMeta).where(AppMeta.key == key))
    return meta.value if meta else None


def set_meta_value(db: Session, key: str, value: str) -> None:
    meta = db.scalar(select(AppMeta).where(AppMeta.key == key))
    if not meta:
        db.add(AppMeta(key=key, value=value))
        return
    meta.value = value


def is_meta_true(db: Session, key: str) -> bool:
    return get_meta_value(db, key) == "1"


def normalize_columns(row: dict[str, Any]) -> dict[str, Any]:
    return {str(key).strip().lower(): value for key, value in row.items()}


def read_kochwiki_csv(csv_path: str | Path) -> list[dict[str, Any]]:
    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    data = path.read_bytes()
    return read_kochwiki_csv_bytes(data)


def _read_csv_rows(text: str, delimiter: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
    return [normalize_columns(row) for row in reader]


def read_kochwiki_csv_bytes(csv_bytes: bytes) -> list[dict[str, Any]]:
    text = csv_bytes.decode("utf-8-sig", errors="replace")
    sample_lines = [line for line in text.splitlines() if line.strip()][:5]
    sample = "\n".join(sample_lines)
    delimiter = ";" if sample.count(";") >= sample.count(",") else ","
    rows = _read_csv_rows(text, delimiter)
    if delimiter == ";" and rows and len(rows[0]) <= 1:
        fallback_rows = _read_csv_rows(text, ",")
        if fallback_rows and len(fallback_rows[0]) > 1:
            rows = fallback_rows
    return rows


def _pick_value(row: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return value
    return None


def _clean_title(value: Any) -> str:
    title = re.sub(r"\s+", " ", str(value or "").strip())
    return title[:255]


def _normalize_title_for_match(title: str) -> str:
    return re.sub(r"\s+", " ", title.strip().lower())


def _parse_source_image_url(raw_value: Any) -> str | None:
    candidate = str(raw_value or "").strip()
    if not candidate:
        return None
    if "kein_bild" in candidate.lower():
        return None
    return candidate[:1024]


def _parse_kochwiki_ingredients(raw_value: Any) -> list[dict[str, Any]]:
    entries = []
    for item in parse_list_like(raw_value):
        cleaned = re.sub(r"\s+", " ", item.strip())
        if not cleaned:
            continue
        match = re.match(r"^\s*([\d.,/\-]+\s*[A-Za-z%]*)\s+(.+)$", cleaned)
        if match:
            quantity_text = match.group(1).strip()
            name = match.group(2).strip()
        else:
            quantity_text = ""
            name = cleaned
        entries.append({"name": name, "quantity_text": quantity_text, "grams": parse_optional_int(cleaned)})
    return entries


def _build_category(row: dict[str, Any]) -> str:
    categories = parse_list_like(row.get("kategorien"))
    if categories:
        return categories[0][:120]
    for key in ("mahlzeit", "landkuche", "landkueche", "category"):
        value = str(row.get(key) or "").strip()
        if value:
            return value[:120]
    return "General"


def _build_instructions(row: dict[str, Any]) -> str:
    instructions = parse_text_block(row.get("zubereitung") or row.get("instructions") or row.get("steps"))
    return instructions or "No instructions provided."


def _build_description(row: dict[str, Any]) -> str:
    description = str(row.get("beschreibung") or row.get("description") or "").strip()
    return description or "Imported from KochWiki."


def _find_existing_recipe(
    db: Session,
    source_uuid: str | None,
    title_normalized: str,
    source_url: str | None,
) -> Recipe | None:
    if source_uuid:
        recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == source_uuid))
        if recipe:
            return recipe
    if source_url:
        return db.scalar(
            select(Recipe).where(
                func.lower(Recipe.title) == title_normalized,
                Recipe.source_url == source_url,
            )
        )
    return None


def _apply_update_fields(recipe: Recipe, payload: dict[str, Any]) -> None:
    recipe.description = payload["description"]
    recipe.instructions = payload["instructions"]
    recipe.category = payload["category"]
    recipe.total_time_minutes = payload["total_time_minutes"]
    recipe.prep_time_minutes = payload["prep_time_minutes"]
    recipe.difficulty = payload["difficulty"]
    recipe.servings_text = payload["servings_text"]
    if payload["source_url"] and not recipe.source_url:
        recipe.source_url = payload["source_url"]
    if payload["source_uuid"] and not recipe.source_uuid:
        recipe.source_uuid = payload["source_uuid"]
    if payload["source_image_url"]:
        recipe.source_image_url = payload["source_image_url"]
        recipe.title_image_url = payload["source_image_url"]
    recipe.source = recipe.source or "kochwiki"


def _download_image_if_enabled(db: Session, recipe: Recipe, source_image_url: str | None) -> None:
    if not settings.import_download_images or not source_image_url:
        return
    resolved_url = resolve_title_image_url(source_image_url)
    if not resolved_url:
        return
    request = Request(resolved_url, headers={"User-Agent": "MealMate/1.0"})
    with urlopen(request, timeout=12) as response:
        content_type = str(response.headers.get("Content-Type") or "").split(";")[0].strip().lower()
        data = response.read(settings.max_upload_mb * 1024 * 1024 + 1)
    validate_upload(content_type, len(data), data)
    filename = Path(urlparse(resolved_url).path).name or "import-image"
    db.add(
        RecipeImage(
            recipe_id=recipe.id,
            filename=filename[:255],
            content_type=content_type,
            data=data,
        )
    )


def _prepare_kochwiki_payload(row: dict[str, Any]) -> dict[str, Any]:
    title = _clean_title(row.get("titel") or row.get("title") or row.get("name"))
    if not title:
        raise ValueError("missing title")
    source_url = str(row.get("quelle_url") or row.get("source_url") or "").strip()[:1024] or None
    source_uuid = str(row.get("rezept_uuid") or row.get("source_uuid") or "").strip()[:120] or None
    source_image_url = _parse_source_image_url(row.get("titelbild") or row.get("source_image_url"))
    prep_time_minutes = parse_optional_int(row.get("zeit_prep_min"))
    if prep_time_minutes is None:
        prep_time_minutes = parse_optional_int(row.get("arbeitszeit")) or 30
    total_time_minutes = parse_optional_int(row.get("zeit_total_min"))
    if total_time_minutes is None:
        total_time_minutes = parse_optional_int(row.get("arbeitszeit"))
    servings_text = str(row.get("portionen_text") or row.get("portionen") or "").strip()[:120] or None
    payload = {
        "title": title,
        "title_normalized": _normalize_title_for_match(title),
        "source": "kochwiki",
        "source_uuid": source_uuid,
        "source_url": source_url,
        "source_image_url": source_image_url,
        "description": _build_description(row),
        "instructions": _build_instructions(row),
        "category": _build_category(row),
        "prep_time_minutes": prep_time_minutes,
        "difficulty": sanitize_difficulty(str(row.get("schwierigkeit") or row.get("difficulty") or "medium")),
        "servings_text": servings_text,
        "total_time_minutes": total_time_minutes,
        "ingredients": _parse_kochwiki_ingredients(row.get("zutaten")),
    }
    return payload


def import_kochwiki_csv(
    db: Session,
    csv_source: str | Path | bytes,
    creator_id: int,
    mode: IMPORT_MODE = "insert_only",
    batch_size: int = 200,
    autocommit: bool = True,
) -> CSVImportReport:
    if mode not in {"insert_only", "update_existing"}:
        raise ValueError("mode must be 'insert_only' or 'update_existing'")
    rows = read_kochwiki_csv_bytes(csv_source) if isinstance(csv_source, bytes) else read_kochwiki_csv(csv_source)
    report = CSVImportReport()
    pending_writes = 0
    for row_index, row in enumerate(rows, start=2):
        try:
            payload = _prepare_kochwiki_payload(row)
            with db.begin_nested():
                existing = _find_existing_recipe(
                    db,
                    payload["source_uuid"],
                    payload["title_normalized"],
                    payload["source_url"],
                )
                if existing and mode == "insert_only":
                    report.skipped += 1
                    continue
                if existing and mode == "update_existing":
                    _apply_update_fields(existing, payload)
                    replace_recipe_ingredients(db, existing, payload["ingredients"])
                    db.add(existing)
                    report.updated += 1
                    pending_writes += 1
                    continue
                recipe = Recipe(
                    title=payload["title"],
                    title_image_url=payload["source_image_url"],
                    source=payload["source"],
                    source_uuid=payload["source_uuid"],
                    source_url=payload["source_url"],
                    source_image_url=payload["source_image_url"],
                    servings_text=payload["servings_text"],
                    total_time_minutes=payload["total_time_minutes"],
                    description=payload["description"],
                    instructions=payload["instructions"],
                    category=payload["category"],
                    prep_time_minutes=payload["prep_time_minutes"],
                    difficulty=payload["difficulty"],
                    creator_id=creator_id,
                )
                db.add(recipe)
                db.flush()
                replace_recipe_ingredients(db, recipe, payload["ingredients"])
                _download_image_if_enabled(db, recipe, payload["source_image_url"])
                report.inserted += 1
                pending_writes += 1
            if pending_writes >= batch_size:
                if autocommit:
                    db.commit()
                else:
                    db.flush()
                pending_writes = 0
        except Exception as exc:
            report.skipped += 1
            report.errors.append(f"Row {row_index}: {exc}")
    if pending_writes > 0:
        if autocommit:
            db.commit()
        else:
            db.flush()
    return report


def build_recipe_pdf(recipe: Recipe, avg_rating: float, review_count: int) -> bytes:
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    top = height - 50
    if recipe.images:
        image = recipe.images[0]
        image_reader = ImageReader(io.BytesIO(image.data))
        pdf.drawImage(image_reader, 50, top - 120, width=120, height=90, preserveAspectRatio=True, mask="auto")
        top -= 130
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, top, recipe.title)
    top -= 24
    pdf.setFont("Helvetica", 11)
    meta = f"Category: {recipe.category} | Difficulty: {recipe.difficulty} | Prep: {recipe.prep_time_minutes} min"
    pdf.drawString(50, top, meta)
    top -= 18
    rating_line = f"Average rating: {avg_rating:.2f} ({review_count} reviews)"
    pdf.drawString(50, top, rating_line)
    top -= 26
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, top, "Ingredients")
    top -= 18
    pdf.setFont("Helvetica", 11)
    for link in recipe.recipe_ingredients:
        line = f"- {link.ingredient.name} {link.quantity_text}".strip()
        if link.grams:
            line = f"{line} ({link.grams} g)"
        top = draw_wrapped_line(pdf, line, 50, top, width - 100)
        if top < 100:
            pdf.showPage()
            top = height - 50
            pdf.setFont("Helvetica", 11)
    top -= 6
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, top, "Instructions")
    top -= 18
    pdf.setFont("Helvetica", 11)
    for paragraph in [piece.strip() for piece in recipe.instructions.splitlines() if piece.strip()]:
        top = draw_wrapped_line(pdf, paragraph, 50, top, width - 100)
        top -= 4
        if top < 80:
            pdf.showPage()
            top = height - 50
            pdf.setFont("Helvetica", 11)
    pdf.save()
    buffer.seek(0)
    return buffer.getvalue()


def draw_wrapped_line(pdf: canvas.Canvas, text: str, x: int, y: int, max_width: int) -> int:
    words = text.split()
    current = ""
    for word in words:
        trial = f"{current} {word}".strip()
        if pdf.stringWidth(trial, "Helvetica", 11) <= max_width:
            current = trial
            continue
        pdf.drawString(x, y, current)
        y -= 14
        current = word
    if current:
        pdf.drawString(x, y, current)
        y -= 14
    return y


def readable_file_size(size_bytes: int) -> str:
    return f"{size_bytes / (1024 * 1024):.2f} MB"
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile importiert benoetigte Abhaengigkeiten.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile importiert benoetigte Abhaengigkeiten.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile ist bewusst leer.
13. Diese Zeile importiert benoetigte Abhaengigkeiten.
14. Diese Zeile importiert benoetigte Abhaengigkeiten.
15. Diese Zeile importiert benoetigte Abhaengigkeiten.
16. Diese Zeile importiert benoetigte Abhaengigkeiten.
17. Diese Zeile importiert benoetigte Abhaengigkeiten.
18. Diese Zeile importiert benoetigte Abhaengigkeiten.
19. Diese Zeile ist bewusst leer.
20. Diese Zeile importiert benoetigte Abhaengigkeiten.
21. Diese Zeile importiert benoetigte Abhaengigkeiten.
22. Diese Zeile ist bewusst leer.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile ist bewusst leer.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile ist bewusst leer.
28. Diese Zeile ist bewusst leer.
29. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
30. Diese Zeile startet eine Klassendefinition.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile ist bewusst leer.
36. Diese Zeile ist bewusst leer.
37. Diese Zeile startet eine Funktionsdefinition.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile startet eine Schleife.
40. Diese Zeile setzt einen Teil der Implementierung um.
41. Diese Zeile steuert einen bedingten Ablauf.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile steuert einen bedingten Ablauf.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile steuert einen bedingten Ablauf.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile ist bewusst leer.
54. Diese Zeile ist bewusst leer.
55. Diese Zeile startet eine Funktionsdefinition.
56. Diese Zeile steuert einen bedingten Ablauf.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile steuert einen bedingten Ablauf.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile steuert einen bedingten Ablauf.
62. Diese Zeile setzt einen Teil der Implementierung um.
63. Diese Zeile setzt einen Teil der Implementierung um.
64. Diese Zeile setzt einen Teil der Implementierung um.
65. Diese Zeile ist bewusst leer.
66. Diese Zeile ist bewusst leer.
67. Diese Zeile startet eine Funktionsdefinition.
68. Diese Zeile setzt einen Teil der Implementierung um.
69. Diese Zeile setzt einen Teil der Implementierung um.
70. Diese Zeile setzt einen Teil der Implementierung um.
71. Diese Zeile steuert einen bedingten Ablauf.
72. Diese Zeile setzt einen Teil der Implementierung um.
73. Diese Zeile setzt einen Teil der Implementierung um.
74. Diese Zeile ist bewusst leer.
75. Diese Zeile ist bewusst leer.
76. Diese Zeile startet eine Funktionsdefinition.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile ist bewusst leer.
79. Diese Zeile ist bewusst leer.
80. Diese Zeile startet eine Funktionsdefinition.
81. Diese Zeile steuert einen bedingten Ablauf.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile steuert einen bedingten Ablauf.
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile steuert einen bedingten Ablauf.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile steuert einen bedingten Ablauf.
89. Diese Zeile gehoert zur Fehlerbehandlung.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile gehoert zur Fehlerbehandlung.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile steuert einen bedingten Ablauf.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile ist bewusst leer.
98. Diese Zeile ist bewusst leer.
99. Diese Zeile startet eine Funktionsdefinition.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile steuert einen bedingten Ablauf.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile setzt einen Teil der Implementierung um.
104. Diese Zeile ist bewusst leer.
105. Diese Zeile ist bewusst leer.
106. Diese Zeile startet eine Funktionsdefinition.
107. Diese Zeile setzt einen Teil der Implementierung um.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile steuert einen bedingten Ablauf.
110. Diese Zeile setzt einen Teil der Implementierung um.
111. Diese Zeile setzt einen Teil der Implementierung um.
112. Diese Zeile setzt einen Teil der Implementierung um.
113. Diese Zeile setzt einen Teil der Implementierung um.
114. Diese Zeile setzt einen Teil der Implementierung um.
115. Diese Zeile ist bewusst leer.
116. Diese Zeile ist bewusst leer.
117. Diese Zeile startet eine Funktionsdefinition.
118. Diese Zeile setzt einen Teil der Implementierung um.
119. Diese Zeile setzt einen Teil der Implementierung um.
120. Diese Zeile startet eine Schleife.
121. Diese Zeile setzt einen Teil der Implementierung um.
122. Diese Zeile steuert einen bedingten Ablauf.
123. Diese Zeile setzt einen Teil der Implementierung um.
124. Diese Zeile setzt einen Teil der Implementierung um.
125. Diese Zeile setzt einen Teil der Implementierung um.
126. Diese Zeile setzt einen Teil der Implementierung um.
127. Diese Zeile steuert einen bedingten Ablauf.
128. Diese Zeile setzt einen Teil der Implementierung um.
129. Diese Zeile setzt einen Teil der Implementierung um.
130. Diese Zeile setzt einen Teil der Implementierung um.
131. Diese Zeile steuert einen bedingten Ablauf.
132. Diese Zeile steuert einen bedingten Ablauf.
133. Diese Zeile setzt einen Teil der Implementierung um.
134. Diese Zeile steuert einen bedingten Ablauf.
135. Diese Zeile setzt einen Teil der Implementierung um.
136. Diese Zeile steuert einen bedingten Ablauf.
137. Diese Zeile setzt einen Teil der Implementierung um.
138. Diese Zeile startet eine Schleife.
139. Diese Zeile setzt einen Teil der Implementierung um.
140. Diese Zeile setzt einen Teil der Implementierung um.
141. Diese Zeile setzt einen Teil der Implementierung um.
142. Diese Zeile setzt einen Teil der Implementierung um.
143. Diese Zeile setzt einen Teil der Implementierung um.
144. Diese Zeile setzt einen Teil der Implementierung um.
145. Diese Zeile setzt einen Teil der Implementierung um.
146. Diese Zeile setzt einen Teil der Implementierung um.
147. Diese Zeile setzt einen Teil der Implementierung um.
148. Diese Zeile ist bewusst leer.
149. Diese Zeile ist bewusst leer.
150. Diese Zeile startet eine Funktionsdefinition.
151. Diese Zeile steuert einen bedingten Ablauf.
152. Diese Zeile setzt einen Teil der Implementierung um.
153. Diese Zeile setzt einen Teil der Implementierung um.
154. Diese Zeile steuert einen bedingten Ablauf.
155. Diese Zeile setzt einen Teil der Implementierung um.
156. Diese Zeile steuert einen bedingten Ablauf.
157. Diese Zeile gehoert zur Fehlerbehandlung.
158. Diese Zeile setzt einen Teil der Implementierung um.
159. Diese Zeile setzt einen Teil der Implementierung um.
160. Diese Zeile gehoert zur Fehlerbehandlung.
161. Diese Zeile setzt einen Teil der Implementierung um.
162. Diese Zeile ist bewusst leer.
163. Diese Zeile ist bewusst leer.
164. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
165. Diese Zeile startet eine Funktionsdefinition.
166. Diese Zeile setzt einen Teil der Implementierung um.
167. Diese Zeile steuert einen bedingten Ablauf.
168. Diese Zeile setzt einen Teil der Implementierung um.
169. Diese Zeile setzt einen Teil der Implementierung um.
170. Diese Zeile steuert einen bedingten Ablauf.
171. Diese Zeile setzt einen Teil der Implementierung um.
172. Diese Zeile steuert einen bedingten Ablauf.
173. Diese Zeile setzt einen Teil der Implementierung um.
174. Diese Zeile setzt einen Teil der Implementierung um.
175. Diese Zeile setzt einen Teil der Implementierung um.
176. Diese Zeile setzt einen Teil der Implementierung um.
177. Diese Zeile steuert einen bedingten Ablauf.
178. Diese Zeile setzt einen Teil der Implementierung um.
179. Diese Zeile setzt einen Teil der Implementierung um.
180. Diese Zeile setzt einen Teil der Implementierung um.
181. Diese Zeile setzt einen Teil der Implementierung um.
182. Diese Zeile setzt einen Teil der Implementierung um.
183. Diese Zeile setzt einen Teil der Implementierung um.
184. Diese Zeile setzt einen Teil der Implementierung um.
185. Diese Zeile setzt einen Teil der Implementierung um.
186. Diese Zeile steuert einen bedingten Ablauf.
187. Diese Zeile setzt einen Teil der Implementierung um.
188. Diese Zeile setzt einen Teil der Implementierung um.
189. Diese Zeile ist bewusst leer.
190. Diese Zeile ist bewusst leer.
191. Diese Zeile startet eine Funktionsdefinition.
192. Diese Zeile steuert einen bedingten Ablauf.
193. Diese Zeile setzt einen Teil der Implementierung um.
194. Diese Zeile setzt einen Teil der Implementierung um.
195. Diese Zeile steuert einen bedingten Ablauf.
196. Diese Zeile setzt einen Teil der Implementierung um.
197. Diese Zeile setzt einen Teil der Implementierung um.
198. Diese Zeile ist bewusst leer.
199. Diese Zeile ist bewusst leer.
200. Diese Zeile startet eine Funktionsdefinition.
201. Diese Zeile setzt einen Teil der Implementierung um.
202. Diese Zeile ist bewusst leer.
203. Diese Zeile ist bewusst leer.
204. Diese Zeile startet eine Funktionsdefinition.
205. Diese Zeile setzt einen Teil der Implementierung um.
206. Diese Zeile setzt einen Teil der Implementierung um.
207. Diese Zeile ist bewusst leer.
208. Diese Zeile ist bewusst leer.
209. Diese Zeile startet eine Funktionsdefinition.
210. Diese Zeile setzt einen Teil der Implementierung um.
211. Diese Zeile steuert einen bedingten Ablauf.
212. Diese Zeile setzt einen Teil der Implementierung um.
213. Diese Zeile setzt einen Teil der Implementierung um.
214. Diese Zeile setzt einen Teil der Implementierung um.
215. Diese Zeile ist bewusst leer.
216. Diese Zeile ist bewusst leer.
217. Diese Zeile startet eine Funktionsdefinition.
218. Diese Zeile setzt einen Teil der Implementierung um.
219. Diese Zeile ist bewusst leer.
220. Diese Zeile ist bewusst leer.
221. Diese Zeile startet eine Funktionsdefinition.
222. Diese Zeile setzt einen Teil der Implementierung um.
223. Diese Zeile ist bewusst leer.
224. Diese Zeile ist bewusst leer.
225. Diese Zeile startet eine Funktionsdefinition.
226. Diese Zeile setzt einen Teil der Implementierung um.
227. Diese Zeile steuert einen bedingten Ablauf.
228. Diese Zeile setzt einen Teil der Implementierung um.
229. Diese Zeile setzt einen Teil der Implementierung um.
230. Diese Zeile setzt einen Teil der Implementierung um.
231. Diese Zeile ist bewusst leer.
232. Diese Zeile ist bewusst leer.
233. Diese Zeile startet eine Funktionsdefinition.
234. Diese Zeile setzt einen Teil der Implementierung um.
235. Diese Zeile setzt einen Teil der Implementierung um.
236. Diese Zeile ist bewusst leer.
237. Diese Zeile ist bewusst leer.
238. Diese Zeile startet eine Funktionsdefinition.
239. Diese Zeile setzt einen Teil der Implementierung um.
240. Diese Zeile setzt einen Teil der Implementierung um.
241. Diese Zeile setzt einen Teil der Implementierung um.
242. Diese Zeile setzt einen Teil der Implementierung um.
243. Diese Zeile setzt einen Teil der Implementierung um.
244. Diese Zeile steuert einen bedingten Ablauf.
245. Diese Zeile setzt einen Teil der Implementierung um.
246. Diese Zeile steuert einen bedingten Ablauf.
247. Diese Zeile setzt einen Teil der Implementierung um.
248. Diese Zeile setzt einen Teil der Implementierung um.
249. Diese Zeile ist bewusst leer.
250. Diese Zeile ist bewusst leer.
251. Diese Zeile startet eine Funktionsdefinition.
252. Diese Zeile startet eine Schleife.
253. Diese Zeile setzt einen Teil der Implementierung um.
254. Diese Zeile steuert einen bedingten Ablauf.
255. Diese Zeile setzt einen Teil der Implementierung um.
256. Diese Zeile setzt einen Teil der Implementierung um.
257. Diese Zeile ist bewusst leer.
258. Diese Zeile ist bewusst leer.
259. Diese Zeile startet eine Funktionsdefinition.
260. Diese Zeile setzt einen Teil der Implementierung um.
261. Diese Zeile setzt einen Teil der Implementierung um.
262. Diese Zeile ist bewusst leer.
263. Diese Zeile ist bewusst leer.
264. Diese Zeile startet eine Funktionsdefinition.
265. Diese Zeile setzt einen Teil der Implementierung um.
266. Diese Zeile ist bewusst leer.
267. Diese Zeile ist bewusst leer.
268. Diese Zeile startet eine Funktionsdefinition.
269. Diese Zeile setzt einen Teil der Implementierung um.
270. Diese Zeile steuert einen bedingten Ablauf.
271. Diese Zeile setzt einen Teil der Implementierung um.
272. Diese Zeile steuert einen bedingten Ablauf.
273. Diese Zeile setzt einen Teil der Implementierung um.
274. Diese Zeile setzt einen Teil der Implementierung um.
275. Diese Zeile ist bewusst leer.
276. Diese Zeile ist bewusst leer.
277. Diese Zeile startet eine Funktionsdefinition.
278. Diese Zeile setzt einen Teil der Implementierung um.
279. Diese Zeile startet eine Schleife.
280. Diese Zeile setzt einen Teil der Implementierung um.
281. Diese Zeile steuert einen bedingten Ablauf.
282. Diese Zeile setzt einen Teil der Implementierung um.
283. Diese Zeile setzt einen Teil der Implementierung um.
284. Diese Zeile steuert einen bedingten Ablauf.
285. Diese Zeile setzt einen Teil der Implementierung um.
286. Diese Zeile setzt einen Teil der Implementierung um.
287. Diese Zeile steuert einen bedingten Ablauf.
288. Diese Zeile setzt einen Teil der Implementierung um.
289. Diese Zeile setzt einen Teil der Implementierung um.
290. Diese Zeile setzt einen Teil der Implementierung um.
291. Diese Zeile setzt einen Teil der Implementierung um.
292. Diese Zeile ist bewusst leer.
293. Diese Zeile ist bewusst leer.
294. Diese Zeile startet eine Funktionsdefinition.
295. Diese Zeile setzt einen Teil der Implementierung um.
296. Diese Zeile steuert einen bedingten Ablauf.
297. Diese Zeile setzt einen Teil der Implementierung um.
298. Diese Zeile startet eine Schleife.
299. Diese Zeile setzt einen Teil der Implementierung um.
300. Diese Zeile steuert einen bedingten Ablauf.
301. Diese Zeile setzt einen Teil der Implementierung um.
302. Diese Zeile setzt einen Teil der Implementierung um.
303. Diese Zeile ist bewusst leer.
304. Diese Zeile ist bewusst leer.
305. Diese Zeile startet eine Funktionsdefinition.
306. Diese Zeile setzt einen Teil der Implementierung um.
307. Diese Zeile setzt einen Teil der Implementierung um.
308. Diese Zeile ist bewusst leer.
309. Diese Zeile ist bewusst leer.
310. Diese Zeile startet eine Funktionsdefinition.
311. Diese Zeile setzt einen Teil der Implementierung um.
312. Diese Zeile setzt einen Teil der Implementierung um.
313. Diese Zeile ist bewusst leer.
314. Diese Zeile ist bewusst leer.
315. Diese Zeile startet eine Funktionsdefinition.
316. Diese Zeile setzt einen Teil der Implementierung um.
317. Diese Zeile setzt einen Teil der Implementierung um.
318. Diese Zeile setzt einen Teil der Implementierung um.
319. Diese Zeile setzt einen Teil der Implementierung um.
320. Diese Zeile setzt einen Teil der Implementierung um.
321. Diese Zeile steuert einen bedingten Ablauf.
322. Diese Zeile setzt einen Teil der Implementierung um.
323. Diese Zeile steuert einen bedingten Ablauf.
324. Diese Zeile setzt einen Teil der Implementierung um.
325. Diese Zeile steuert einen bedingten Ablauf.
326. Diese Zeile setzt einen Teil der Implementierung um.
327. Diese Zeile setzt einen Teil der Implementierung um.
328. Diese Zeile setzt einen Teil der Implementierung um.
329. Diese Zeile setzt einen Teil der Implementierung um.
330. Diese Zeile setzt einen Teil der Implementierung um.
331. Diese Zeile setzt einen Teil der Implementierung um.
332. Diese Zeile setzt einen Teil der Implementierung um.
333. Diese Zeile ist bewusst leer.
334. Diese Zeile ist bewusst leer.
335. Diese Zeile startet eine Funktionsdefinition.
336. Diese Zeile setzt einen Teil der Implementierung um.
337. Diese Zeile setzt einen Teil der Implementierung um.
338. Diese Zeile setzt einen Teil der Implementierung um.
339. Diese Zeile setzt einen Teil der Implementierung um.
340. Diese Zeile setzt einen Teil der Implementierung um.
341. Diese Zeile setzt einen Teil der Implementierung um.
342. Diese Zeile setzt einen Teil der Implementierung um.
343. Diese Zeile steuert einen bedingten Ablauf.
344. Diese Zeile setzt einen Teil der Implementierung um.
345. Diese Zeile steuert einen bedingten Ablauf.
346. Diese Zeile setzt einen Teil der Implementierung um.
347. Diese Zeile steuert einen bedingten Ablauf.
348. Diese Zeile setzt einen Teil der Implementierung um.
349. Diese Zeile setzt einen Teil der Implementierung um.
350. Diese Zeile setzt einen Teil der Implementierung um.
351. Diese Zeile ist bewusst leer.
352. Diese Zeile ist bewusst leer.
353. Diese Zeile startet eine Funktionsdefinition.
354. Diese Zeile steuert einen bedingten Ablauf.
355. Diese Zeile setzt einen Teil der Implementierung um.
356. Diese Zeile setzt einen Teil der Implementierung um.
357. Diese Zeile steuert einen bedingten Ablauf.
358. Diese Zeile setzt einen Teil der Implementierung um.
359. Diese Zeile setzt einen Teil der Implementierung um.
360. Diese Zeile setzt einen Teil der Implementierung um.
361. Diese Zeile setzt einen Teil der Implementierung um.
362. Diese Zeile setzt einen Teil der Implementierung um.
363. Diese Zeile setzt einen Teil der Implementierung um.
364. Diese Zeile setzt einen Teil der Implementierung um.
365. Diese Zeile setzt einen Teil der Implementierung um.
366. Diese Zeile setzt einen Teil der Implementierung um.
367. Diese Zeile setzt einen Teil der Implementierung um.
368. Diese Zeile setzt einen Teil der Implementierung um.
369. Diese Zeile setzt einen Teil der Implementierung um.
370. Diese Zeile setzt einen Teil der Implementierung um.
371. Diese Zeile setzt einen Teil der Implementierung um.
372. Diese Zeile setzt einen Teil der Implementierung um.
373. Diese Zeile ist bewusst leer.
374. Diese Zeile ist bewusst leer.
375. Diese Zeile startet eine Funktionsdefinition.
376. Diese Zeile setzt einen Teil der Implementierung um.
377. Diese Zeile steuert einen bedingten Ablauf.
378. Diese Zeile setzt einen Teil der Implementierung um.
379. Diese Zeile setzt einen Teil der Implementierung um.
380. Diese Zeile setzt einen Teil der Implementierung um.
381. Diese Zeile setzt einen Teil der Implementierung um.
382. Diese Zeile setzt einen Teil der Implementierung um.
383. Diese Zeile steuert einen bedingten Ablauf.
384. Diese Zeile setzt einen Teil der Implementierung um.
385. Diese Zeile setzt einen Teil der Implementierung um.
386. Diese Zeile steuert einen bedingten Ablauf.
387. Diese Zeile setzt einen Teil der Implementierung um.
388. Diese Zeile setzt einen Teil der Implementierung um.
389. Diese Zeile setzt einen Teil der Implementierung um.
390. Diese Zeile setzt einen Teil der Implementierung um.
391. Diese Zeile setzt einen Teil der Implementierung um.
392. Diese Zeile setzt einen Teil der Implementierung um.
393. Diese Zeile setzt einen Teil der Implementierung um.
394. Diese Zeile setzt einen Teil der Implementierung um.
395. Diese Zeile setzt einen Teil der Implementierung um.
396. Diese Zeile setzt einen Teil der Implementierung um.
397. Diese Zeile setzt einen Teil der Implementierung um.
398. Diese Zeile setzt einen Teil der Implementierung um.
399. Diese Zeile setzt einen Teil der Implementierung um.
400. Diese Zeile setzt einen Teil der Implementierung um.
401. Diese Zeile setzt einen Teil der Implementierung um.
402. Diese Zeile setzt einen Teil der Implementierung um.
403. Diese Zeile setzt einen Teil der Implementierung um.
404. Diese Zeile setzt einen Teil der Implementierung um.
405. Diese Zeile setzt einen Teil der Implementierung um.
406. Diese Zeile ist bewusst leer.
407. Diese Zeile ist bewusst leer.
408. Diese Zeile startet eine Funktionsdefinition.
409. Diese Zeile setzt einen Teil der Implementierung um.
410. Diese Zeile setzt einen Teil der Implementierung um.
411. Diese Zeile setzt einen Teil der Implementierung um.
412. Diese Zeile setzt einen Teil der Implementierung um.
413. Diese Zeile setzt einen Teil der Implementierung um.
414. Diese Zeile setzt einen Teil der Implementierung um.
415. Diese Zeile setzt einen Teil der Implementierung um.
416. Diese Zeile steuert einen bedingten Ablauf.
417. Diese Zeile setzt einen Teil der Implementierung um.
418. Diese Zeile setzt einen Teil der Implementierung um.
419. Diese Zeile setzt einen Teil der Implementierung um.
420. Diese Zeile setzt einen Teil der Implementierung um.
421. Diese Zeile startet eine Schleife.
422. Diese Zeile gehoert zur Fehlerbehandlung.
423. Diese Zeile setzt einen Teil der Implementierung um.
424. Diese Zeile setzt einen Teil der Implementierung um.
425. Diese Zeile setzt einen Teil der Implementierung um.
426. Diese Zeile setzt einen Teil der Implementierung um.
427. Diese Zeile setzt einen Teil der Implementierung um.
428. Diese Zeile setzt einen Teil der Implementierung um.
429. Diese Zeile setzt einen Teil der Implementierung um.
430. Diese Zeile setzt einen Teil der Implementierung um.
431. Diese Zeile steuert einen bedingten Ablauf.
432. Diese Zeile setzt einen Teil der Implementierung um.
433. Diese Zeile setzt einen Teil der Implementierung um.
434. Diese Zeile steuert einen bedingten Ablauf.
435. Diese Zeile setzt einen Teil der Implementierung um.
436. Diese Zeile setzt einen Teil der Implementierung um.
437. Diese Zeile setzt einen Teil der Implementierung um.
438. Diese Zeile setzt einen Teil der Implementierung um.
439. Diese Zeile setzt einen Teil der Implementierung um.
440. Diese Zeile setzt einen Teil der Implementierung um.
441. Diese Zeile setzt einen Teil der Implementierung um.
442. Diese Zeile setzt einen Teil der Implementierung um.
443. Diese Zeile setzt einen Teil der Implementierung um.
444. Diese Zeile setzt einen Teil der Implementierung um.
445. Diese Zeile setzt einen Teil der Implementierung um.
446. Diese Zeile setzt einen Teil der Implementierung um.
447. Diese Zeile setzt einen Teil der Implementierung um.
448. Diese Zeile setzt einen Teil der Implementierung um.
449. Diese Zeile setzt einen Teil der Implementierung um.
450. Diese Zeile setzt einen Teil der Implementierung um.
451. Diese Zeile setzt einen Teil der Implementierung um.
452. Diese Zeile setzt einen Teil der Implementierung um.
453. Diese Zeile setzt einen Teil der Implementierung um.
454. Diese Zeile setzt einen Teil der Implementierung um.
455. Diese Zeile setzt einen Teil der Implementierung um.
456. Diese Zeile setzt einen Teil der Implementierung um.
457. Diese Zeile setzt einen Teil der Implementierung um.
458. Diese Zeile setzt einen Teil der Implementierung um.
459. Diese Zeile setzt einen Teil der Implementierung um.
460. Diese Zeile setzt einen Teil der Implementierung um.
461. Diese Zeile setzt einen Teil der Implementierung um.
462. Diese Zeile setzt einen Teil der Implementierung um.
463. Diese Zeile steuert einen bedingten Ablauf.
464. Diese Zeile steuert einen bedingten Ablauf.
465. Diese Zeile setzt einen Teil der Implementierung um.
466. Diese Zeile steuert einen bedingten Ablauf.
467. Diese Zeile setzt einen Teil der Implementierung um.
468. Diese Zeile setzt einen Teil der Implementierung um.
469. Diese Zeile gehoert zur Fehlerbehandlung.
470. Diese Zeile setzt einen Teil der Implementierung um.
471. Diese Zeile setzt einen Teil der Implementierung um.
472. Diese Zeile steuert einen bedingten Ablauf.
473. Diese Zeile steuert einen bedingten Ablauf.
474. Diese Zeile setzt einen Teil der Implementierung um.
475. Diese Zeile steuert einen bedingten Ablauf.
476. Diese Zeile setzt einen Teil der Implementierung um.
477. Diese Zeile setzt einen Teil der Implementierung um.
478. Diese Zeile ist bewusst leer.
479. Diese Zeile ist bewusst leer.
480. Diese Zeile startet eine Funktionsdefinition.
481. Diese Zeile setzt einen Teil der Implementierung um.
482. Diese Zeile setzt einen Teil der Implementierung um.
483. Diese Zeile setzt einen Teil der Implementierung um.
484. Diese Zeile setzt einen Teil der Implementierung um.
485. Diese Zeile steuert einen bedingten Ablauf.
486. Diese Zeile setzt einen Teil der Implementierung um.
487. Diese Zeile setzt einen Teil der Implementierung um.
488. Diese Zeile setzt einen Teil der Implementierung um.
489. Diese Zeile setzt einen Teil der Implementierung um.
490. Diese Zeile setzt einen Teil der Implementierung um.
491. Diese Zeile setzt einen Teil der Implementierung um.
492. Diese Zeile setzt einen Teil der Implementierung um.
493. Diese Zeile setzt einen Teil der Implementierung um.
494. Diese Zeile setzt einen Teil der Implementierung um.
495. Diese Zeile setzt einen Teil der Implementierung um.
496. Diese Zeile setzt einen Teil der Implementierung um.
497. Diese Zeile setzt einen Teil der Implementierung um.
498. Diese Zeile setzt einen Teil der Implementierung um.
499. Diese Zeile setzt einen Teil der Implementierung um.
500. Diese Zeile setzt einen Teil der Implementierung um.
501. Diese Zeile setzt einen Teil der Implementierung um.
502. Diese Zeile setzt einen Teil der Implementierung um.
503. Diese Zeile setzt einen Teil der Implementierung um.
504. Diese Zeile startet eine Schleife.
505. Diese Zeile setzt einen Teil der Implementierung um.
506. Diese Zeile steuert einen bedingten Ablauf.
507. Diese Zeile setzt einen Teil der Implementierung um.
508. Diese Zeile setzt einen Teil der Implementierung um.
509. Diese Zeile steuert einen bedingten Ablauf.
510. Diese Zeile setzt einen Teil der Implementierung um.
511. Diese Zeile setzt einen Teil der Implementierung um.
512. Diese Zeile setzt einen Teil der Implementierung um.
513. Diese Zeile setzt einen Teil der Implementierung um.
514. Diese Zeile setzt einen Teil der Implementierung um.
515. Diese Zeile setzt einen Teil der Implementierung um.
516. Diese Zeile setzt einen Teil der Implementierung um.
517. Diese Zeile setzt einen Teil der Implementierung um.
518. Diese Zeile startet eine Schleife.
519. Diese Zeile setzt einen Teil der Implementierung um.
520. Diese Zeile setzt einen Teil der Implementierung um.
521. Diese Zeile steuert einen bedingten Ablauf.
522. Diese Zeile setzt einen Teil der Implementierung um.
523. Diese Zeile setzt einen Teil der Implementierung um.
524. Diese Zeile setzt einen Teil der Implementierung um.
525. Diese Zeile setzt einen Teil der Implementierung um.
526. Diese Zeile setzt einen Teil der Implementierung um.
527. Diese Zeile setzt einen Teil der Implementierung um.
528. Diese Zeile ist bewusst leer.
529. Diese Zeile ist bewusst leer.
530. Diese Zeile startet eine Funktionsdefinition.
531. Diese Zeile setzt einen Teil der Implementierung um.
532. Diese Zeile setzt einen Teil der Implementierung um.
533. Diese Zeile startet eine Schleife.
534. Diese Zeile setzt einen Teil der Implementierung um.
535. Diese Zeile steuert einen bedingten Ablauf.
536. Diese Zeile setzt einen Teil der Implementierung um.
537. Diese Zeile setzt einen Teil der Implementierung um.
538. Diese Zeile setzt einen Teil der Implementierung um.
539. Diese Zeile setzt einen Teil der Implementierung um.
540. Diese Zeile setzt einen Teil der Implementierung um.
541. Diese Zeile steuert einen bedingten Ablauf.
542. Diese Zeile setzt einen Teil der Implementierung um.
543. Diese Zeile setzt einen Teil der Implementierung um.
544. Diese Zeile setzt einen Teil der Implementierung um.
545. Diese Zeile ist bewusst leer.
546. Diese Zeile ist bewusst leer.
547. Diese Zeile startet eine Funktionsdefinition.
548. Diese Zeile setzt einen Teil der Implementierung um.

## app/routers/auth.py
```python
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, template_context
from app.models import User
from app.rate_limit import key_by_ip, limiter
from app.security import create_access_token, hash_password, validate_password_policy, verify_password
from app.views import redirect, templates

router = APIRouter(tags=["auth"])
settings = get_settings()


def set_auth_cookie(response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=settings.resolved_cookie_secure,
        samesite="lax",
        max_age=60 * 60 * 24,
        path="/",
    )


@router.get("/login")
@router.get("/auth/login")
def login_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        return redirect("/")
    return templates.TemplateResponse("auth_login.html", template_context(request, current_user, error=None))


@router.post("/login")
@router.post("/auth/login")
@limiter.limit("5/minute", key_func=key_by_ip)
def login_submit(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = response
    user = db.scalar(select(User).where(User.email == email.strip().lower()))
    if not user or not verify_password(password, user.hashed_password):
        response = templates.TemplateResponse(
            "auth_login.html",
            template_context(request, None, error="Invalid credentials."),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
        return response
    token = create_access_token(user.email, user.role)
    response = redirect("/")
    set_auth_cookie(response, token)
    return response


@router.get("/register")
@router.get("/auth/register")
def register_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        return redirect("/")
    return templates.TemplateResponse("auth_register.html", template_context(request, current_user, error=None))


@router.post("/register")
@router.post("/auth/register")
@limiter.limit("3/minute", key_func=key_by_ip)
def register_submit(
    request: Request,
    response: Response,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = response
    normalized_email = email.strip().lower()
    password_error = validate_password_policy(password)
    if password_error:
        return templates.TemplateResponse(
            "auth_register.html",
            template_context(request, None, error=password_error),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    existing = db.scalar(select(User).where(User.email == normalized_email))
    if existing:
        return templates.TemplateResponse(
            "auth_register.html",
            template_context(request, None, error="Email already registered."),
            status_code=status.HTTP_409_CONFLICT,
        )
    user = User(email=normalized_email, hashed_password=hash_password(password), role="user")
    db.add(user)
    db.commit()
    token = create_access_token(user.email, user.role)
    response = redirect("/")
    set_auth_cookie(response, token)
    return response


@router.post("/logout")
def logout():
    response = redirect("/")
    response.delete_cookie("access_token", path="/")
    return response


@router.get("/me")
def me_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("me.html", template_context(request, current_user, user=current_user))


@router.get("/api/me")
def me_api(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat(),
    }


@router.get("/admin-only")
def admin_only(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required.")
    return {"message": "You are admin."}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile importiert benoetigte Abhaengigkeiten.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile ist bewusst leer.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile importiert benoetigte Abhaengigkeiten.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile importiert benoetigte Abhaengigkeiten.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile ist bewusst leer.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile ist bewusst leer.
16. Diese Zeile ist bewusst leer.
17. Diese Zeile startet eine Funktionsdefinition.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile ist bewusst leer.
28. Diese Zeile ist bewusst leer.
29. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
30. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
31. Diese Zeile startet eine Funktionsdefinition.
32. Diese Zeile steuert einen bedingten Ablauf.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile ist bewusst leer.
36. Diese Zeile ist bewusst leer.
37. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
38. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
39. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
40. Diese Zeile startet eine Funktionsdefinition.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile steuert einen bedingten Ablauf.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile ist bewusst leer.
61. Diese Zeile ist bewusst leer.
62. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
63. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
64. Diese Zeile startet eine Funktionsdefinition.
65. Diese Zeile steuert einen bedingten Ablauf.
66. Diese Zeile setzt einen Teil der Implementierung um.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile ist bewusst leer.
69. Diese Zeile ist bewusst leer.
70. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
71. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
72. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
73. Diese Zeile startet eine Funktionsdefinition.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile steuert einen bedingten Ablauf.
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile setzt einen Teil der Implementierung um.
89. Diese Zeile setzt einen Teil der Implementierung um.
90. Diese Zeile steuert einen bedingten Ablauf.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile ist bewusst leer.
104. Diese Zeile ist bewusst leer.
105. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
106. Diese Zeile startet eine Funktionsdefinition.
107. Diese Zeile setzt einen Teil der Implementierung um.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile setzt einen Teil der Implementierung um.
110. Diese Zeile ist bewusst leer.
111. Diese Zeile ist bewusst leer.
112. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
113. Diese Zeile startet eine Funktionsdefinition.
114. Diese Zeile setzt einen Teil der Implementierung um.
115. Diese Zeile ist bewusst leer.
116. Diese Zeile ist bewusst leer.
117. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
118. Diese Zeile startet eine Funktionsdefinition.
119. Diese Zeile setzt einen Teil der Implementierung um.
120. Diese Zeile setzt einen Teil der Implementierung um.
121. Diese Zeile setzt einen Teil der Implementierung um.
122. Diese Zeile setzt einen Teil der Implementierung um.
123. Diese Zeile setzt einen Teil der Implementierung um.
124. Diese Zeile setzt einen Teil der Implementierung um.
125. Diese Zeile ist bewusst leer.
126. Diese Zeile ist bewusst leer.
127. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
128. Diese Zeile startet eine Funktionsdefinition.
129. Diese Zeile steuert einen bedingten Ablauf.
130. Diese Zeile setzt einen Teil der Implementierung um.
131. Diese Zeile setzt einen Teil der Implementierung um.

## app/routers/admin.py
```python
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, Response, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_admin_user, template_context
from app.models import Recipe, User
from app.rate_limit import key_by_user_or_ip, limiter
from app.services import import_kochwiki_csv, is_meta_true, set_meta_value
from app.views import redirect, templates

router = APIRouter(tags=["admin"])
settings = get_settings()


def admin_dashboard_context(
    request: Request,
    db: Session,
    current_user: User,
    report=None,
    error: str | None = None,
    message: str | None = None,
):
    users = db.scalars(select(User).order_by(User.created_at.desc())).all()
    recipes = db.scalars(
        select(Recipe).order_by(Recipe.created_at.desc()).options(selectinload(Recipe.creator))
    ).all()
    return template_context(
        request,
        current_user,
        users=users,
        recipes=recipes,
        report=report,
        error=error,
        message=message,
        seed_done=is_meta_true(db, "kochwiki_seed_done"),
        default_csv_path=settings.kochwiki_csv_path,
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
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be user or admin.")
    user = db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    db.delete(recipe)
    db.commit()
    return redirect("/admin")


@router.post("/admin/run-kochwiki-seed")
def run_kochwiki_seed(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    if is_meta_true(db, "kochwiki_seed_done"):
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, error="KochWiki seed is already marked as done."),
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
                error="Seed can only run on an empty recipes table.",
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
                error=f"CSV file not found: {seed_path}",
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
                error="Seed finished with errors, marker was not set.",
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
            message="KochWiki seed finished successfully and was marked as done.",
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
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    _ = response
    max_bytes = settings.max_csv_upload_mb * 1024 * 1024
    mode = "insert_only"
    if update_existing:
        mode = "update_existing"
    elif not insert_only:
        mode = "insert_only"
    try:
        if not file or not file.filename:
            raise ValueError("Please upload a CSV file.")
        if not file.filename.lower().endswith(".csv"):
            raise ValueError("Only CSV uploads are allowed.")
        raw_bytes = await file.read(max_bytes + 1)
        if len(raw_bytes) > max_bytes:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="CSV upload too large.")
        if not raw_bytes:
            raise ValueError("Uploaded CSV file is empty.")
        report = import_kochwiki_csv(
            db,
            raw_bytes,
            current_user.id,
            mode=mode,
            autocommit=False,
        )
        db.commit()
        message = "Import finished in insert-only mode."
        if mode == "update_existing":
            message = "Import finished in update-existing mode."
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, report=report, message=message),
        )
    except (FileNotFoundError, ValueError) as exc:
        db.rollback()
        return templates.TemplateResponse(
            "admin.html",
            admin_dashboard_context(request, db, current_user, error=str(exc)),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    except Exception:
        db.rollback()
        raise
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile ist bewusst leer.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile ist bewusst leer.
7. Diese Zeile importiert benoetigte Abhaengigkeiten.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile importiert benoetigte Abhaengigkeiten.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile importiert benoetigte Abhaengigkeiten.
13. Diese Zeile importiert benoetigte Abhaengigkeiten.
14. Diese Zeile ist bewusst leer.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile ist bewusst leer.
18. Diese Zeile ist bewusst leer.
19. Diese Zeile startet eine Funktionsdefinition.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile setzt einen Teil der Implementierung um.
40. Diese Zeile setzt einen Teil der Implementierung um.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile ist bewusst leer.
43. Diese Zeile ist bewusst leer.
44. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
45. Diese Zeile startet eine Funktionsdefinition.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile ist bewusst leer.
52. Diese Zeile ist bewusst leer.
53. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
54. Diese Zeile startet eine Funktionsdefinition.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile steuert einen bedingten Ablauf.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile setzt einen Teil der Implementierung um.
63. Diese Zeile steuert einen bedingten Ablauf.
64. Diese Zeile setzt einen Teil der Implementierung um.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile setzt einen Teil der Implementierung um.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile ist bewusst leer.
69. Diese Zeile ist bewusst leer.
70. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
71. Diese Zeile startet eine Funktionsdefinition.
72. Diese Zeile setzt einen Teil der Implementierung um.
73. Diese Zeile setzt einen Teil der Implementierung um.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile steuert einen bedingten Ablauf.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile ist bewusst leer.
83. Diese Zeile ist bewusst leer.
84. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
85. Diese Zeile startet eine Funktionsdefinition.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile setzt einen Teil der Implementierung um.
89. Diese Zeile setzt einen Teil der Implementierung um.
90. Diese Zeile steuert einen bedingten Ablauf.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile steuert einen bedingten Ablauf.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile setzt einen Teil der Implementierung um.
104. Diese Zeile setzt einen Teil der Implementierung um.
105. Diese Zeile setzt einen Teil der Implementierung um.
106. Diese Zeile setzt einen Teil der Implementierung um.
107. Diese Zeile setzt einen Teil der Implementierung um.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile steuert einen bedingten Ablauf.
110. Diese Zeile setzt einen Teil der Implementierung um.
111. Diese Zeile setzt einen Teil der Implementierung um.
112. Diese Zeile setzt einen Teil der Implementierung um.
113. Diese Zeile setzt einen Teil der Implementierung um.
114. Diese Zeile setzt einen Teil der Implementierung um.
115. Diese Zeile setzt einen Teil der Implementierung um.
116. Diese Zeile setzt einen Teil der Implementierung um.
117. Diese Zeile setzt einen Teil der Implementierung um.
118. Diese Zeile setzt einen Teil der Implementierung um.
119. Diese Zeile setzt einen Teil der Implementierung um.
120. Diese Zeile setzt einen Teil der Implementierung um.
121. Diese Zeile steuert einen bedingten Ablauf.
122. Diese Zeile setzt einen Teil der Implementierung um.
123. Diese Zeile setzt einen Teil der Implementierung um.
124. Diese Zeile setzt einen Teil der Implementierung um.
125. Diese Zeile setzt einen Teil der Implementierung um.
126. Diese Zeile setzt einen Teil der Implementierung um.
127. Diese Zeile setzt einen Teil der Implementierung um.
128. Diese Zeile setzt einen Teil der Implementierung um.
129. Diese Zeile setzt einen Teil der Implementierung um.
130. Diese Zeile setzt einen Teil der Implementierung um.
131. Diese Zeile setzt einen Teil der Implementierung um.
132. Diese Zeile setzt einen Teil der Implementierung um.
133. Diese Zeile setzt einen Teil der Implementierung um.
134. Diese Zeile setzt einen Teil der Implementierung um.
135. Diese Zeile setzt einen Teil der Implementierung um.
136. Diese Zeile setzt einen Teil der Implementierung um.
137. Diese Zeile setzt einen Teil der Implementierung um.
138. Diese Zeile setzt einen Teil der Implementierung um.
139. Diese Zeile setzt einen Teil der Implementierung um.
140. Diese Zeile setzt einen Teil der Implementierung um.
141. Diese Zeile setzt einen Teil der Implementierung um.
142. Diese Zeile setzt einen Teil der Implementierung um.
143. Diese Zeile setzt einen Teil der Implementierung um.
144. Diese Zeile setzt einen Teil der Implementierung um.
145. Diese Zeile ist bewusst leer.
146. Diese Zeile ist bewusst leer.
147. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
148. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
149. Diese Zeile startet eine Funktionsdefinition.
150. Diese Zeile setzt einen Teil der Implementierung um.
151. Diese Zeile setzt einen Teil der Implementierung um.
152. Diese Zeile setzt einen Teil der Implementierung um.
153. Diese Zeile setzt einen Teil der Implementierung um.
154. Diese Zeile setzt einen Teil der Implementierung um.
155. Diese Zeile setzt einen Teil der Implementierung um.
156. Diese Zeile setzt einen Teil der Implementierung um.
157. Diese Zeile setzt einen Teil der Implementierung um.
158. Diese Zeile setzt einen Teil der Implementierung um.
159. Diese Zeile setzt einen Teil der Implementierung um.
160. Diese Zeile setzt einen Teil der Implementierung um.
161. Diese Zeile steuert einen bedingten Ablauf.
162. Diese Zeile setzt einen Teil der Implementierung um.
163. Diese Zeile steuert einen bedingten Ablauf.
164. Diese Zeile setzt einen Teil der Implementierung um.
165. Diese Zeile gehoert zur Fehlerbehandlung.
166. Diese Zeile steuert einen bedingten Ablauf.
167. Diese Zeile setzt einen Teil der Implementierung um.
168. Diese Zeile steuert einen bedingten Ablauf.
169. Diese Zeile setzt einen Teil der Implementierung um.
170. Diese Zeile setzt einen Teil der Implementierung um.
171. Diese Zeile steuert einen bedingten Ablauf.
172. Diese Zeile setzt einen Teil der Implementierung um.
173. Diese Zeile steuert einen bedingten Ablauf.
174. Diese Zeile setzt einen Teil der Implementierung um.
175. Diese Zeile setzt einen Teil der Implementierung um.
176. Diese Zeile setzt einen Teil der Implementierung um.
177. Diese Zeile setzt einen Teil der Implementierung um.
178. Diese Zeile setzt einen Teil der Implementierung um.
179. Diese Zeile setzt einen Teil der Implementierung um.
180. Diese Zeile setzt einen Teil der Implementierung um.
181. Diese Zeile setzt einen Teil der Implementierung um.
182. Diese Zeile setzt einen Teil der Implementierung um.
183. Diese Zeile setzt einen Teil der Implementierung um.
184. Diese Zeile steuert einen bedingten Ablauf.
185. Diese Zeile setzt einen Teil der Implementierung um.
186. Diese Zeile setzt einen Teil der Implementierung um.
187. Diese Zeile setzt einen Teil der Implementierung um.
188. Diese Zeile setzt einen Teil der Implementierung um.
189. Diese Zeile setzt einen Teil der Implementierung um.
190. Diese Zeile gehoert zur Fehlerbehandlung.
191. Diese Zeile setzt einen Teil der Implementierung um.
192. Diese Zeile setzt einen Teil der Implementierung um.
193. Diese Zeile setzt einen Teil der Implementierung um.
194. Diese Zeile setzt einen Teil der Implementierung um.
195. Diese Zeile setzt einen Teil der Implementierung um.
196. Diese Zeile setzt einen Teil der Implementierung um.
197. Diese Zeile gehoert zur Fehlerbehandlung.
198. Diese Zeile setzt einen Teil der Implementierung um.
199. Diese Zeile setzt einen Teil der Implementierung um.

## app/routers/recipes.py
```python
from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from sqlalchemy import and_, desc, func, select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, template_context
from app.image_utils import ImageValidationError, safe_image_filename, validate_image_upload
from app.models import Favorite, Ingredient, Recipe, RecipeImage, RecipeIngredient, Review, User
from app.pdf_service import build_recipe_pdf
from app.rate_limit import key_by_user_or_ip, limiter
from app.services import (
    can_manage_recipe,
    parse_ingredient_text,
    replace_recipe_ingredients,
    resolve_title_image_url,
    sanitize_difficulty,
)
from app.views import redirect, templates

router = APIRouter(tags=["recipes"])

PAGE_SIZE = 8


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


def ensure_recipe_access(user: User, recipe: Recipe) -> None:
    if not can_manage_recipe(user, recipe):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions for this recipe.")


def get_primary_image(recipe: Recipe) -> RecipeImage | None:
    for image in recipe.images:
        if image.is_primary:
            return image
    return recipe.images[0] if recipe.images else None


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


def render_image_section(request: Request, db: Session, recipe_id: int, current_user: User | None):
    recipe = fetch_recipe_or_404(db, recipe_id)
    primary_image = get_primary_image(recipe)
    return templates.TemplateResponse(
        "partials/recipe_images.html",
        template_context(
            request,
            current_user,
            recipe=recipe,
            primary_image=primary_image,
        ),
    )


@router.get("/")
def home_page(
    request: Request,
    page: int = 1,
    sort: str = "date",
    title: str = "",
    category: str = "",
    difficulty: str = "",
    ingredient: str = "",
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    page = max(page, 1)
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
        .options(selectinload(Recipe.images))
    )
    if title.strip():
        like = f"%{title.strip()}%"
        stmt = stmt.where(Recipe.title.ilike(like))
    if category.strip():
        stmt = stmt.where(Recipe.category.ilike(category.strip()))
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
    rows = db.execute(stmt.offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)).all()
    recipes_data = [{"recipe": row[0], "avg_rating": float(row[1] or 0), "review_count": int(row[2] or 0)} for row in rows]
    pages = max((total + PAGE_SIZE - 1) // PAGE_SIZE, 1)
    context = template_context(
        request,
        current_user,
        recipes_data=recipes_data,
        page=page,
        pages=pages,
        sort=sort,
        title=title,
        category=category,
        difficulty=difficulty,
        ingredient=ingredient,
    )
    if request.headers.get("HX-Request") == "true":
        return templates.TemplateResponse("partials/recipe_list.html", context)
    return templates.TemplateResponse("home.html", context)


@router.get("/recipes/new")
def create_recipe_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse(
        "recipe_form.html",
        template_context(request, current_user, recipe=None, error=None, form_mode="create"),
    )


@router.post("/recipes/new")
async def create_recipe_submit(
    request: Request,
    title: str = Form(...),
    description: str = Form(...),
    instructions: str = Form(...),
    category: str = Form(...),
    title_image_url: str = Form(""),
    prep_time_minutes: str = Form(...),
    difficulty: str = Form(...),
    ingredients_text: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    prep_time = parse_positive_int(prep_time_minutes, "prep_time_minutes")
    normalized_difficulty = sanitize_difficulty(difficulty)
    if not title.strip() or not instructions.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title and instructions are required.")
    recipe = Recipe(
        title=title.strip(),
        title_image_url=normalize_image_url(title_image_url),
        description=description.strip(),
        instructions=instructions.strip(),
        category=category.strip() or "General",
        prep_time_minutes=prep_time,
        difficulty=normalized_difficulty,
        creator_id=current_user.id,
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
    db: Session = Depends(get_db),
    current_user: User | None = Depends(get_current_user_optional),
):
    recipe = fetch_recipe_or_404(db, recipe_id)
    avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.recipe_id == recipe_id)) or 0
    review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe_id)) or 0
    primary_image = get_primary_image(recipe)
    is_favorite = False
    if current_user:
        is_favorite = db.scalar(
            select(Favorite).where(and_(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id))
        ) is not None
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
        ),
    )


@router.post("/recipes/{recipe_id}/edit")
async def edit_recipe_submit(
    recipe_id: int,
    title: str = Form(...),
    description: str = Form(...),
    instructions: str = Form(...),
    category: str = Form(...),
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
    recipe.category = category.strip() or "General"
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
    if not recipe:
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
        .where(Favorite.user_id == current_user.id)
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
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _ = response
    recipe = fetch_recipe_or_404(db, recipe_id)
    ensure_recipe_access(current_user, recipe)
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
        return render_image_section(request, db, recipe_id, current_user)
    return redirect(f"/recipes/{recipe_id}")


@router.get("/images/{image_id}")
def get_image(image_id: int, db: Session = Depends(get_db)):
    image = db.scalar(select(RecipeImage).where(RecipeImage.id == image_id))
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    return Response(content=image.data, media_type=image.content_type)


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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    ensure_recipe_access(current_user, image.recipe)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    recipe = image.recipe
    recipe_id = image.recipe_id
    ensure_recipe_access(current_user, recipe)
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found.")
    recipe = image.recipe
    ensure_recipe_access(current_user, recipe)
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
    avg_rating = db.scalar(select(func.coalesce(func.avg(Review.rating), 0)).where(Review.recipe_id == recipe_id)) or 0
    review_count = db.scalar(select(func.count(Review.id)).where(Review.recipe_id == recipe_id)) or 0
    pdf_bytes = build_recipe_pdf(recipe, float(avg_rating), int(review_count))
    filename = f"mealmate_recipe_{recipe_id}.pdf"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(BytesIO(pdf_bytes), media_type="application/pdf", headers=headers)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Abhaengigkeiten.
2. Diese Zeile ist bewusst leer.
3. Diese Zeile importiert benoetigte Abhaengigkeiten.
4. Diese Zeile importiert benoetigte Abhaengigkeiten.
5. Diese Zeile importiert benoetigte Abhaengigkeiten.
6. Diese Zeile importiert benoetigte Abhaengigkeiten.
7. Diese Zeile ist bewusst leer.
8. Diese Zeile importiert benoetigte Abhaengigkeiten.
9. Diese Zeile importiert benoetigte Abhaengigkeiten.
10. Diese Zeile importiert benoetigte Abhaengigkeiten.
11. Diese Zeile importiert benoetigte Abhaengigkeiten.
12. Diese Zeile importiert benoetigte Abhaengigkeiten.
13. Diese Zeile importiert benoetigte Abhaengigkeiten.
14. Diese Zeile importiert benoetigte Abhaengigkeiten.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile setzt einen Teil der Implementierung um.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile importiert benoetigte Abhaengigkeiten.
22. Diese Zeile ist bewusst leer.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile ist bewusst leer.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile ist bewusst leer.
27. Diese Zeile ist bewusst leer.
28. Diese Zeile startet eine Funktionsdefinition.
29. Diese Zeile gehoert zur Fehlerbehandlung.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile gehoert zur Fehlerbehandlung.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile steuert einen bedingten Ablauf.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile ist bewusst leer.
37. Diese Zeile ist bewusst leer.
38. Diese Zeile startet eine Funktionsdefinition.
39. Diese Zeile setzt einen Teil der Implementierung um.
40. Diese Zeile steuert einen bedingten Ablauf.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile steuert einen bedingten Ablauf.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile ist bewusst leer.
46. Diese Zeile ist bewusst leer.
47. Diese Zeile startet eine Funktionsdefinition.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile setzt einen Teil der Implementierung um.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile steuert einen bedingten Ablauf.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile ist bewusst leer.
62. Diese Zeile ist bewusst leer.
63. Diese Zeile startet eine Funktionsdefinition.
64. Diese Zeile steuert einen bedingten Ablauf.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile ist bewusst leer.
67. Diese Zeile ist bewusst leer.
68. Diese Zeile startet eine Funktionsdefinition.
69. Diese Zeile startet eine Schleife.
70. Diese Zeile steuert einen bedingten Ablauf.
71. Diese Zeile setzt einen Teil der Implementierung um.
72. Diese Zeile setzt einen Teil der Implementierung um.
73. Diese Zeile ist bewusst leer.
74. Diese Zeile ist bewusst leer.
75. Diese Zeile startet eine Funktionsdefinition.
76. Diese Zeile startet eine Schleife.
77. Diese Zeile setzt einen Teil der Implementierung um.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile ist bewusst leer.
80. Diese Zeile ist bewusst leer.
81. Diese Zeile startet eine Funktionsdefinition.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile steuert einen bedingten Ablauf.
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile steuert einen bedingten Ablauf.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile setzt einen Teil der Implementierung um.
89. Diese Zeile ist bewusst leer.
90. Diese Zeile ist bewusst leer.
91. Diese Zeile startet eine Funktionsdefinition.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile setzt einen Teil der Implementierung um.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile ist bewusst leer.
104. Diese Zeile ist bewusst leer.
105. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
106. Diese Zeile startet eine Funktionsdefinition.
107. Diese Zeile setzt einen Teil der Implementierung um.
108. Diese Zeile setzt einen Teil der Implementierung um.
109. Diese Zeile setzt einen Teil der Implementierung um.
110. Diese Zeile setzt einen Teil der Implementierung um.
111. Diese Zeile setzt einen Teil der Implementierung um.
112. Diese Zeile setzt einen Teil der Implementierung um.
113. Diese Zeile setzt einen Teil der Implementierung um.
114. Diese Zeile setzt einen Teil der Implementierung um.
115. Diese Zeile setzt einen Teil der Implementierung um.
116. Diese Zeile setzt einen Teil der Implementierung um.
117. Diese Zeile setzt einen Teil der Implementierung um.
118. Diese Zeile setzt einen Teil der Implementierung um.
119. Diese Zeile setzt einen Teil der Implementierung um.
120. Diese Zeile setzt einen Teil der Implementierung um.
121. Diese Zeile setzt einen Teil der Implementierung um.
122. Diese Zeile setzt einen Teil der Implementierung um.
123. Diese Zeile setzt einen Teil der Implementierung um.
124. Diese Zeile setzt einen Teil der Implementierung um.
125. Diese Zeile setzt einen Teil der Implementierung um.
126. Diese Zeile setzt einen Teil der Implementierung um.
127. Diese Zeile setzt einen Teil der Implementierung um.
128. Diese Zeile setzt einen Teil der Implementierung um.
129. Diese Zeile setzt einen Teil der Implementierung um.
130. Diese Zeile setzt einen Teil der Implementierung um.
131. Diese Zeile setzt einen Teil der Implementierung um.
132. Diese Zeile setzt einen Teil der Implementierung um.
133. Diese Zeile setzt einen Teil der Implementierung um.
134. Diese Zeile setzt einen Teil der Implementierung um.
135. Diese Zeile setzt einen Teil der Implementierung um.
136. Diese Zeile steuert einen bedingten Ablauf.
137. Diese Zeile setzt einen Teil der Implementierung um.
138. Diese Zeile setzt einen Teil der Implementierung um.
139. Diese Zeile steuert einen bedingten Ablauf.
140. Diese Zeile setzt einen Teil der Implementierung um.
141. Diese Zeile steuert einen bedingten Ablauf.
142. Diese Zeile setzt einen Teil der Implementierung um.
143. Diese Zeile steuert einen bedingten Ablauf.
144. Diese Zeile setzt einen Teil der Implementierung um.
145. Diese Zeile setzt einen Teil der Implementierung um.
146. Diese Zeile setzt einen Teil der Implementierung um.
147. Diese Zeile setzt einen Teil der Implementierung um.
148. Diese Zeile setzt einen Teil der Implementierung um.
149. Diese Zeile setzt einen Teil der Implementierung um.
150. Diese Zeile setzt einen Teil der Implementierung um.
151. Diese Zeile setzt einen Teil der Implementierung um.
152. Diese Zeile steuert einen bedingten Ablauf.
153. Diese Zeile setzt einen Teil der Implementierung um.
154. Diese Zeile steuert einen bedingten Ablauf.
155. Diese Zeile setzt einen Teil der Implementierung um.
156. Diese Zeile steuert einen bedingten Ablauf.
157. Diese Zeile setzt einen Teil der Implementierung um.
158. Diese Zeile setzt einen Teil der Implementierung um.
159. Diese Zeile setzt einen Teil der Implementierung um.
160. Diese Zeile setzt einen Teil der Implementierung um.
161. Diese Zeile setzt einen Teil der Implementierung um.
162. Diese Zeile setzt einen Teil der Implementierung um.
163. Diese Zeile setzt einen Teil der Implementierung um.
164. Diese Zeile setzt einen Teil der Implementierung um.
165. Diese Zeile setzt einen Teil der Implementierung um.
166. Diese Zeile setzt einen Teil der Implementierung um.
167. Diese Zeile setzt einen Teil der Implementierung um.
168. Diese Zeile setzt einen Teil der Implementierung um.
169. Diese Zeile setzt einen Teil der Implementierung um.
170. Diese Zeile setzt einen Teil der Implementierung um.
171. Diese Zeile setzt einen Teil der Implementierung um.
172. Diese Zeile setzt einen Teil der Implementierung um.
173. Diese Zeile setzt einen Teil der Implementierung um.
174. Diese Zeile steuert einen bedingten Ablauf.
175. Diese Zeile setzt einen Teil der Implementierung um.
176. Diese Zeile setzt einen Teil der Implementierung um.
177. Diese Zeile ist bewusst leer.
178. Diese Zeile ist bewusst leer.
179. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
180. Diese Zeile startet eine Funktionsdefinition.
181. Diese Zeile setzt einen Teil der Implementierung um.
182. Diese Zeile setzt einen Teil der Implementierung um.
183. Diese Zeile setzt einen Teil der Implementierung um.
184. Diese Zeile setzt einen Teil der Implementierung um.
185. Diese Zeile ist bewusst leer.
186. Diese Zeile ist bewusst leer.
187. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
188. Diese Zeile startet eine Funktionsdefinition.
189. Diese Zeile setzt einen Teil der Implementierung um.
190. Diese Zeile setzt einen Teil der Implementierung um.
191. Diese Zeile setzt einen Teil der Implementierung um.
192. Diese Zeile setzt einen Teil der Implementierung um.
193. Diese Zeile setzt einen Teil der Implementierung um.
194. Diese Zeile setzt einen Teil der Implementierung um.
195. Diese Zeile setzt einen Teil der Implementierung um.
196. Diese Zeile setzt einen Teil der Implementierung um.
197. Diese Zeile setzt einen Teil der Implementierung um.
198. Diese Zeile setzt einen Teil der Implementierung um.
199. Diese Zeile setzt einen Teil der Implementierung um.
200. Diese Zeile setzt einen Teil der Implementierung um.
201. Diese Zeile setzt einen Teil der Implementierung um.
202. Diese Zeile setzt einen Teil der Implementierung um.
203. Diese Zeile setzt einen Teil der Implementierung um.
204. Diese Zeile steuert einen bedingten Ablauf.
205. Diese Zeile setzt einen Teil der Implementierung um.
206. Diese Zeile setzt einen Teil der Implementierung um.
207. Diese Zeile setzt einen Teil der Implementierung um.
208. Diese Zeile setzt einen Teil der Implementierung um.
209. Diese Zeile setzt einen Teil der Implementierung um.
210. Diese Zeile setzt einen Teil der Implementierung um.
211. Diese Zeile setzt einen Teil der Implementierung um.
212. Diese Zeile setzt einen Teil der Implementierung um.
213. Diese Zeile setzt einen Teil der Implementierung um.
214. Diese Zeile setzt einen Teil der Implementierung um.
215. Diese Zeile setzt einen Teil der Implementierung um.
216. Diese Zeile setzt einen Teil der Implementierung um.
217. Diese Zeile setzt einen Teil der Implementierung um.
218. Diese Zeile setzt einen Teil der Implementierung um.
219. Diese Zeile setzt einen Teil der Implementierung um.
220. Diese Zeile steuert einen bedingten Ablauf.
221. Diese Zeile setzt einen Teil der Implementierung um.
222. Diese Zeile gehoert zur Fehlerbehandlung.
223. Diese Zeile setzt einen Teil der Implementierung um.
224. Diese Zeile gehoert zur Fehlerbehandlung.
225. Diese Zeile setzt einen Teil der Implementierung um.
226. Diese Zeile setzt einen Teil der Implementierung um.
227. Diese Zeile setzt einen Teil der Implementierung um.
228. Diese Zeile setzt einen Teil der Implementierung um.
229. Diese Zeile setzt einen Teil der Implementierung um.
230. Diese Zeile setzt einen Teil der Implementierung um.
231. Diese Zeile setzt einen Teil der Implementierung um.
232. Diese Zeile setzt einen Teil der Implementierung um.
233. Diese Zeile setzt einen Teil der Implementierung um.
234. Diese Zeile setzt einen Teil der Implementierung um.
235. Diese Zeile setzt einen Teil der Implementierung um.
236. Diese Zeile setzt einen Teil der Implementierung um.
237. Diese Zeile setzt einen Teil der Implementierung um.
238. Diese Zeile ist bewusst leer.
239. Diese Zeile ist bewusst leer.
240. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
241. Diese Zeile startet eine Funktionsdefinition.
242. Diese Zeile setzt einen Teil der Implementierung um.
243. Diese Zeile setzt einen Teil der Implementierung um.
244. Diese Zeile setzt einen Teil der Implementierung um.
245. Diese Zeile setzt einen Teil der Implementierung um.
246. Diese Zeile setzt einen Teil der Implementierung um.
247. Diese Zeile setzt einen Teil der Implementierung um.
248. Diese Zeile setzt einen Teil der Implementierung um.
249. Diese Zeile setzt einen Teil der Implementierung um.
250. Diese Zeile setzt einen Teil der Implementierung um.
251. Diese Zeile setzt einen Teil der Implementierung um.
252. Diese Zeile steuert einen bedingten Ablauf.
253. Diese Zeile setzt einen Teil der Implementierung um.
254. Diese Zeile setzt einen Teil der Implementierung um.
255. Diese Zeile setzt einen Teil der Implementierung um.
256. Diese Zeile setzt einen Teil der Implementierung um.
257. Diese Zeile setzt einen Teil der Implementierung um.
258. Diese Zeile setzt einen Teil der Implementierung um.
259. Diese Zeile setzt einen Teil der Implementierung um.
260. Diese Zeile setzt einen Teil der Implementierung um.
261. Diese Zeile setzt einen Teil der Implementierung um.
262. Diese Zeile setzt einen Teil der Implementierung um.
263. Diese Zeile setzt einen Teil der Implementierung um.
264. Diese Zeile setzt einen Teil der Implementierung um.
265. Diese Zeile setzt einen Teil der Implementierung um.
266. Diese Zeile setzt einen Teil der Implementierung um.
267. Diese Zeile setzt einen Teil der Implementierung um.
268. Diese Zeile ist bewusst leer.
269. Diese Zeile ist bewusst leer.
270. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
271. Diese Zeile startet eine Funktionsdefinition.
272. Diese Zeile setzt einen Teil der Implementierung um.
273. Diese Zeile setzt einen Teil der Implementierung um.
274. Diese Zeile setzt einen Teil der Implementierung um.
275. Diese Zeile setzt einen Teil der Implementierung um.
276. Diese Zeile setzt einen Teil der Implementierung um.
277. Diese Zeile setzt einen Teil der Implementierung um.
278. Diese Zeile setzt einen Teil der Implementierung um.
279. Diese Zeile setzt einen Teil der Implementierung um.
280. Diese Zeile setzt einen Teil der Implementierung um.
281. Diese Zeile startet eine Schleife.
282. Diese Zeile setzt einen Teil der Implementierung um.
283. Diese Zeile setzt einen Teil der Implementierung um.
284. Diese Zeile setzt einen Teil der Implementierung um.
285. Diese Zeile setzt einen Teil der Implementierung um.
286. Diese Zeile setzt einen Teil der Implementierung um.
287. Diese Zeile setzt einen Teil der Implementierung um.
288. Diese Zeile setzt einen Teil der Implementierung um.
289. Diese Zeile setzt einen Teil der Implementierung um.
290. Diese Zeile setzt einen Teil der Implementierung um.
291. Diese Zeile setzt einen Teil der Implementierung um.
292. Diese Zeile setzt einen Teil der Implementierung um.
293. Diese Zeile setzt einen Teil der Implementierung um.
294. Diese Zeile ist bewusst leer.
295. Diese Zeile ist bewusst leer.
296. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
297. Diese Zeile startet eine Funktionsdefinition.
298. Diese Zeile setzt einen Teil der Implementierung um.
299. Diese Zeile setzt einen Teil der Implementierung um.
300. Diese Zeile setzt einen Teil der Implementierung um.
301. Diese Zeile setzt einen Teil der Implementierung um.
302. Diese Zeile setzt einen Teil der Implementierung um.
303. Diese Zeile setzt einen Teil der Implementierung um.
304. Diese Zeile setzt einen Teil der Implementierung um.
305. Diese Zeile setzt einen Teil der Implementierung um.
306. Diese Zeile setzt einen Teil der Implementierung um.
307. Diese Zeile setzt einen Teil der Implementierung um.
308. Diese Zeile setzt einen Teil der Implementierung um.
309. Diese Zeile setzt einen Teil der Implementierung um.
310. Diese Zeile setzt einen Teil der Implementierung um.
311. Diese Zeile setzt einen Teil der Implementierung um.
312. Diese Zeile setzt einen Teil der Implementierung um.
313. Diese Zeile setzt einen Teil der Implementierung um.
314. Diese Zeile setzt einen Teil der Implementierung um.
315. Diese Zeile setzt einen Teil der Implementierung um.
316. Diese Zeile setzt einen Teil der Implementierung um.
317. Diese Zeile setzt einen Teil der Implementierung um.
318. Diese Zeile setzt einen Teil der Implementierung um.
319. Diese Zeile setzt einen Teil der Implementierung um.
320. Diese Zeile setzt einen Teil der Implementierung um.
321. Diese Zeile steuert einen bedingten Ablauf.
322. Diese Zeile setzt einen Teil der Implementierung um.
323. Diese Zeile gehoert zur Fehlerbehandlung.
324. Diese Zeile setzt einen Teil der Implementierung um.
325. Diese Zeile gehoert zur Fehlerbehandlung.
326. Diese Zeile setzt einen Teil der Implementierung um.
327. Diese Zeile setzt einen Teil der Implementierung um.
328. Diese Zeile setzt einen Teil der Implementierung um.
329. Diese Zeile setzt einen Teil der Implementierung um.
330. Diese Zeile setzt einen Teil der Implementierung um.
331. Diese Zeile setzt einen Teil der Implementierung um.
332. Diese Zeile setzt einen Teil der Implementierung um.
333. Diese Zeile setzt einen Teil der Implementierung um.
334. Diese Zeile setzt einen Teil der Implementierung um.
335. Diese Zeile setzt einen Teil der Implementierung um.
336. Diese Zeile setzt einen Teil der Implementierung um.
337. Diese Zeile setzt einen Teil der Implementierung um.
338. Diese Zeile setzt einen Teil der Implementierung um.
339. Diese Zeile setzt einen Teil der Implementierung um.
340. Diese Zeile ist bewusst leer.
341. Diese Zeile ist bewusst leer.
342. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
343. Diese Zeile startet eine Funktionsdefinition.
344. Diese Zeile setzt einen Teil der Implementierung um.
345. Diese Zeile setzt einen Teil der Implementierung um.
346. Diese Zeile setzt einen Teil der Implementierung um.
347. Diese Zeile setzt einen Teil der Implementierung um.
348. Diese Zeile setzt einen Teil der Implementierung um.
349. Diese Zeile setzt einen Teil der Implementierung um.
350. Diese Zeile setzt einen Teil der Implementierung um.
351. Diese Zeile setzt einen Teil der Implementierung um.
352. Diese Zeile setzt einen Teil der Implementierung um.
353. Diese Zeile ist bewusst leer.
354. Diese Zeile ist bewusst leer.
355. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
356. Diese Zeile startet eine Funktionsdefinition.
357. Diese Zeile setzt einen Teil der Implementierung um.
358. Diese Zeile setzt einen Teil der Implementierung um.
359. Diese Zeile setzt einen Teil der Implementierung um.
360. Diese Zeile setzt einen Teil der Implementierung um.
361. Diese Zeile setzt einen Teil der Implementierung um.
362. Diese Zeile setzt einen Teil der Implementierung um.
363. Diese Zeile setzt einen Teil der Implementierung um.
364. Diese Zeile steuert einen bedingten Ablauf.
365. Diese Zeile setzt einen Teil der Implementierung um.
366. Diese Zeile steuert einen bedingten Ablauf.
367. Diese Zeile setzt einen Teil der Implementierung um.
368. Diese Zeile setzt einen Teil der Implementierung um.
369. Diese Zeile steuert einen bedingten Ablauf.
370. Diese Zeile setzt einen Teil der Implementierung um.
371. Diese Zeile setzt einen Teil der Implementierung um.
372. Diese Zeile steuert einen bedingten Ablauf.
373. Diese Zeile setzt einen Teil der Implementierung um.
374. Diese Zeile setzt einen Teil der Implementierung um.
375. Diese Zeile setzt einen Teil der Implementierung um.
376. Diese Zeile ist bewusst leer.
377. Diese Zeile ist bewusst leer.
378. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
379. Diese Zeile startet eine Funktionsdefinition.
380. Diese Zeile setzt einen Teil der Implementierung um.
381. Diese Zeile setzt einen Teil der Implementierung um.
382. Diese Zeile setzt einen Teil der Implementierung um.
383. Diese Zeile setzt einen Teil der Implementierung um.
384. Diese Zeile setzt einen Teil der Implementierung um.
385. Diese Zeile steuert einen bedingten Ablauf.
386. Diese Zeile setzt einen Teil der Implementierung um.
387. Diese Zeile steuert einen bedingten Ablauf.
388. Diese Zeile setzt einen Teil der Implementierung um.
389. Diese Zeile setzt einen Teil der Implementierung um.
390. Diese Zeile setzt einen Teil der Implementierung um.
391. Diese Zeile setzt einen Teil der Implementierung um.
392. Diese Zeile setzt einen Teil der Implementierung um.
393. Diese Zeile ist bewusst leer.
394. Diese Zeile ist bewusst leer.
395. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
396. Diese Zeile startet eine Funktionsdefinition.
397. Diese Zeile setzt einen Teil der Implementierung um.
398. Diese Zeile setzt einen Teil der Implementierung um.
399. Diese Zeile setzt einen Teil der Implementierung um.
400. Diese Zeile setzt einen Teil der Implementierung um.
401. Diese Zeile setzt einen Teil der Implementierung um.
402. Diese Zeile setzt einen Teil der Implementierung um.
403. Diese Zeile steuert einen bedingten Ablauf.
404. Diese Zeile setzt einen Teil der Implementierung um.
405. Diese Zeile setzt einen Teil der Implementierung um.
406. Diese Zeile setzt einen Teil der Implementierung um.
407. Diese Zeile setzt einen Teil der Implementierung um.
408. Diese Zeile setzt einen Teil der Implementierung um.
409. Diese Zeile steuert einen bedingten Ablauf.
410. Diese Zeile setzt einen Teil der Implementierung um.
411. Diese Zeile setzt einen Teil der Implementierung um.
412. Diese Zeile steuert einen bedingten Ablauf.
413. Diese Zeile setzt einen Teil der Implementierung um.
414. Diese Zeile setzt einen Teil der Implementierung um.
415. Diese Zeile setzt einen Teil der Implementierung um.
416. Diese Zeile steuert einen bedingten Ablauf.
417. Diese Zeile setzt einen Teil der Implementierung um.
418. Diese Zeile setzt einen Teil der Implementierung um.
419. Diese Zeile setzt einen Teil der Implementierung um.
420. Diese Zeile setzt einen Teil der Implementierung um.
421. Diese Zeile setzt einen Teil der Implementierung um.
422. Diese Zeile ist bewusst leer.
423. Diese Zeile ist bewusst leer.
424. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
425. Diese Zeile startet eine Funktionsdefinition.
426. Diese Zeile setzt einen Teil der Implementierung um.
427. Diese Zeile setzt einen Teil der Implementierung um.
428. Diese Zeile setzt einen Teil der Implementierung um.
429. Diese Zeile setzt einen Teil der Implementierung um.
430. Diese Zeile setzt einen Teil der Implementierung um.
431. Diese Zeile setzt einen Teil der Implementierung um.
432. Diese Zeile setzt einen Teil der Implementierung um.
433. Diese Zeile setzt einen Teil der Implementierung um.
434. Diese Zeile setzt einen Teil der Implementierung um.
435. Diese Zeile setzt einen Teil der Implementierung um.
436. Diese Zeile setzt einen Teil der Implementierung um.
437. Diese Zeile setzt einen Teil der Implementierung um.
438. Diese Zeile setzt einen Teil der Implementierung um.
439. Diese Zeile setzt einen Teil der Implementierung um.
440. Diese Zeile setzt einen Teil der Implementierung um.
441. Diese Zeile ist bewusst leer.
442. Diese Zeile ist bewusst leer.
443. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
444. Diese Zeile startet eine Funktionsdefinition.
445. Diese Zeile setzt einen Teil der Implementierung um.
446. Diese Zeile setzt einen Teil der Implementierung um.
447. Diese Zeile setzt einen Teil der Implementierung um.
448. Diese Zeile setzt einen Teil der Implementierung um.
449. Diese Zeile setzt einen Teil der Implementierung um.
450. Diese Zeile steuert einen bedingten Ablauf.
451. Diese Zeile setzt einen Teil der Implementierung um.
452. Diese Zeile setzt einen Teil der Implementierung um.
453. Diese Zeile setzt einen Teil der Implementierung um.
454. Diese Zeile setzt einen Teil der Implementierung um.
455. Diese Zeile setzt einen Teil der Implementierung um.
456. Diese Zeile setzt einen Teil der Implementierung um.
457. Diese Zeile ist bewusst leer.
458. Diese Zeile ist bewusst leer.
459. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
460. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
461. Diese Zeile startet eine Funktionsdefinition.
462. Diese Zeile setzt einen Teil der Implementierung um.
463. Diese Zeile setzt einen Teil der Implementierung um.
464. Diese Zeile setzt einen Teil der Implementierung um.
465. Diese Zeile setzt einen Teil der Implementierung um.
466. Diese Zeile setzt einen Teil der Implementierung um.
467. Diese Zeile setzt einen Teil der Implementierung um.
468. Diese Zeile setzt einen Teil der Implementierung um.
469. Diese Zeile setzt einen Teil der Implementierung um.
470. Diese Zeile setzt einen Teil der Implementierung um.
471. Diese Zeile setzt einen Teil der Implementierung um.
472. Diese Zeile setzt einen Teil der Implementierung um.
473. Diese Zeile setzt einen Teil der Implementierung um.
474. Diese Zeile setzt einen Teil der Implementierung um.
475. Diese Zeile gehoert zur Fehlerbehandlung.
476. Diese Zeile setzt einen Teil der Implementierung um.
477. Diese Zeile gehoert zur Fehlerbehandlung.
478. Diese Zeile setzt einen Teil der Implementierung um.
479. Diese Zeile setzt einen Teil der Implementierung um.
480. Diese Zeile setzt einen Teil der Implementierung um.
481. Diese Zeile steuert einen bedingten Ablauf.
482. Diese Zeile setzt einen Teil der Implementierung um.
483. Diese Zeile setzt einen Teil der Implementierung um.
484. Diese Zeile setzt einen Teil der Implementierung um.
485. Diese Zeile setzt einen Teil der Implementierung um.
486. Diese Zeile setzt einen Teil der Implementierung um.
487. Diese Zeile setzt einen Teil der Implementierung um.
488. Diese Zeile setzt einen Teil der Implementierung um.
489. Diese Zeile setzt einen Teil der Implementierung um.
490. Diese Zeile setzt einen Teil der Implementierung um.
491. Diese Zeile setzt einen Teil der Implementierung um.
492. Diese Zeile setzt einen Teil der Implementierung um.
493. Diese Zeile steuert einen bedingten Ablauf.
494. Diese Zeile setzt einen Teil der Implementierung um.
495. Diese Zeile setzt einen Teil der Implementierung um.
496. Diese Zeile steuert einen bedingten Ablauf.
497. Diese Zeile setzt einen Teil der Implementierung um.
498. Diese Zeile setzt einen Teil der Implementierung um.
499. Diese Zeile ist bewusst leer.
500. Diese Zeile ist bewusst leer.
501. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
502. Diese Zeile startet eine Funktionsdefinition.
503. Diese Zeile setzt einen Teil der Implementierung um.
504. Diese Zeile steuert einen bedingten Ablauf.
505. Diese Zeile setzt einen Teil der Implementierung um.
506. Diese Zeile setzt einen Teil der Implementierung um.
507. Diese Zeile ist bewusst leer.
508. Diese Zeile ist bewusst leer.
509. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
510. Diese Zeile startet eine Funktionsdefinition.
511. Diese Zeile gehoert zur Fehlerbehandlung.
512. Diese Zeile setzt einen Teil der Implementierung um.
513. Diese Zeile gehoert zur Fehlerbehandlung.
514. Diese Zeile setzt einen Teil der Implementierung um.
515. Diese Zeile steuert einen bedingten Ablauf.
516. Diese Zeile setzt einen Teil der Implementierung um.
517. Diese Zeile setzt einen Teil der Implementierung um.
518. Diese Zeile ist bewusst leer.
519. Diese Zeile ist bewusst leer.
520. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
521. Diese Zeile startet eine Funktionsdefinition.
522. Diese Zeile setzt einen Teil der Implementierung um.
523. Diese Zeile setzt einen Teil der Implementierung um.
524. Diese Zeile setzt einen Teil der Implementierung um.
525. Diese Zeile setzt einen Teil der Implementierung um.
526. Diese Zeile setzt einen Teil der Implementierung um.
527. Diese Zeile steuert einen bedingten Ablauf.
528. Diese Zeile setzt einen Teil der Implementierung um.
529. Diese Zeile setzt einen Teil der Implementierung um.
530. Diese Zeile setzt einen Teil der Implementierung um.
531. Diese Zeile setzt einen Teil der Implementierung um.
532. Diese Zeile setzt einen Teil der Implementierung um.
533. Diese Zeile setzt einen Teil der Implementierung um.
534. Diese Zeile setzt einen Teil der Implementierung um.
535. Diese Zeile setzt einen Teil der Implementierung um.
536. Diese Zeile ist bewusst leer.
537. Diese Zeile ist bewusst leer.
538. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
539. Diese Zeile startet eine Funktionsdefinition.
540. Diese Zeile setzt einen Teil der Implementierung um.
541. Diese Zeile setzt einen Teil der Implementierung um.
542. Diese Zeile setzt einen Teil der Implementierung um.
543. Diese Zeile setzt einen Teil der Implementierung um.
544. Diese Zeile setzt einen Teil der Implementierung um.
545. Diese Zeile setzt einen Teil der Implementierung um.
546. Diese Zeile steuert einen bedingten Ablauf.
547. Diese Zeile setzt einen Teil der Implementierung um.
548. Diese Zeile setzt einen Teil der Implementierung um.
549. Diese Zeile setzt einen Teil der Implementierung um.
550. Diese Zeile setzt einen Teil der Implementierung um.
551. Diese Zeile setzt einen Teil der Implementierung um.
552. Diese Zeile setzt einen Teil der Implementierung um.
553. Diese Zeile setzt einen Teil der Implementierung um.
554. Diese Zeile setzt einen Teil der Implementierung um.
555. Diese Zeile steuert einen bedingten Ablauf.
556. Diese Zeile setzt einen Teil der Implementierung um.
557. Diese Zeile setzt einen Teil der Implementierung um.
558. Diese Zeile ist bewusst leer.
559. Diese Zeile ist bewusst leer.
560. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
561. Diese Zeile startet eine Funktionsdefinition.
562. Diese Zeile setzt einen Teil der Implementierung um.
563. Diese Zeile setzt einen Teil der Implementierung um.
564. Diese Zeile setzt einen Teil der Implementierung um.
565. Diese Zeile setzt einen Teil der Implementierung um.
566. Diese Zeile setzt einen Teil der Implementierung um.
567. Diese Zeile setzt einen Teil der Implementierung um.
568. Diese Zeile steuert einen bedingten Ablauf.
569. Diese Zeile setzt einen Teil der Implementierung um.
570. Diese Zeile setzt einen Teil der Implementierung um.
571. Diese Zeile setzt einen Teil der Implementierung um.
572. Diese Zeile setzt einen Teil der Implementierung um.
573. Diese Zeile setzt einen Teil der Implementierung um.
574. Diese Zeile steuert einen bedingten Ablauf.
575. Diese Zeile setzt einen Teil der Implementierung um.
576. Diese Zeile setzt einen Teil der Implementierung um.
577. Diese Zeile ist bewusst leer.
578. Diese Zeile ist bewusst leer.
579. Diese Zeile definiert einen Dekorator fuer den folgenden Block.
580. Diese Zeile startet eine Funktionsdefinition.
581. Diese Zeile setzt einen Teil der Implementierung um.
582. Diese Zeile setzt einen Teil der Implementierung um.
583. Diese Zeile setzt einen Teil der Implementierung um.
584. Diese Zeile setzt einen Teil der Implementierung um.
585. Diese Zeile setzt einen Teil der Implementierung um.
586. Diese Zeile setzt einen Teil der Implementierung um.
587. Diese Zeile setzt einen Teil der Implementierung um.
588. Diese Zeile setzt einen Teil der Implementierung um.
589. Diese Zeile setzt einen Teil der Implementierung um.
590. Diese Zeile setzt einen Teil der Implementierung um.
591. Diese Zeile setzt einen Teil der Implementierung um.

## app/static/htmx.min.js
```javascript
(function(e,t){if(typeof define==="function"&&define.amd){define([],t)}else if(typeof module==="object"&&module.exports){module.exports=t()}else{e.htmx=e.htmx||t()}})(typeof self!=="undefined"?self:this,function(){return function(){"use strict";var Q={onLoad:F,process:zt,on:de,off:ge,trigger:ce,ajax:Nr,find:C,findAll:f,closest:v,values:function(e,t){var r=dr(e,t||"post");return r.values},remove:_,addClass:z,removeClass:n,toggleClass:$,takeClass:W,defineExtension:Ur,removeExtension:Br,logAll:V,logNone:j,logger:null,config:{historyEnabled:true,historyCacheSize:10,refreshOnHistoryMiss:false,defaultSwapStyle:"innerHTML",defaultSwapDelay:0,defaultSettleDelay:20,includeIndicatorStyles:true,indicatorClass:"htmx-indicator",requestClass:"htmx-request",addedClass:"htmx-added",settlingClass:"htmx-settling",swappingClass:"htmx-swapping",allowEval:true,allowScriptTags:true,inlineScriptNonce:"",attributesToSettle:["class","style","width","height"],withCredentials:false,timeout:0,wsReconnectDelay:"full-jitter",wsBinaryType:"blob",disableSelector:"[hx-disable], [data-hx-disable]",useTemplateFragments:false,scrollBehavior:"smooth",defaultFocusScroll:false,getCacheBusterParam:false,globalViewTransitions:false,methodsThatUseUrlParams:["get"],selfRequestsOnly:false,ignoreTitle:false,scrollIntoViewOnBoost:true,triggerSpecsCache:null},parseInterval:d,_:t,createEventSource:function(e){return new EventSource(e,{withCredentials:true})},createWebSocket:function(e){var t=new WebSocket(e,[]);t.binaryType=Q.config.wsBinaryType;return t},version:"1.9.12"};var r={addTriggerHandler:Lt,bodyContains:se,canAccessLocalStorage:U,findThisElement:xe,filterValues:yr,hasAttribute:o,getAttributeValue:te,getClosestAttributeValue:ne,getClosestMatch:c,getExpressionVars:Hr,getHeaders:xr,getInputValues:dr,getInternalData:ae,getSwapSpecification:wr,getTriggerSpecs:it,getTarget:ye,makeFragment:l,mergeObjects:le,makeSettleInfo:T,oobSwap:Ee,querySelectorExt:ue,selectAndSwap:je,settleImmediately:nr,shouldCancel:ut,triggerEvent:ce,triggerErrorEvent:fe,withExtensions:R};var w=["get","post","put","delete","patch"];var i=w.map(function(e){return"[hx-"+e+"], [data-hx-"+e+"]"}).join(", ");var S=e("head"),q=e("title"),H=e("svg",true);function e(e,t){return new RegExp("<"+e+"(\\s[^>]*>|>)([\\s\\S]*?)<\\/"+e+">",!!t?"gim":"im")}function d(e){if(e==undefined){return undefined}let t=NaN;if(e.slice(-2)=="ms"){t=parseFloat(e.slice(0,-2))}else if(e.slice(-1)=="s"){t=parseFloat(e.slice(0,-1))*1e3}else if(e.slice(-1)=="m"){t=parseFloat(e.slice(0,-1))*1e3*60}else{t=parseFloat(e)}return isNaN(t)?undefined:t}function ee(e,t){return e.getAttribute&&e.getAttribute(t)}function o(e,t){return e.hasAttribute&&(e.hasAttribute(t)||e.hasAttribute("data-"+t))}function te(e,t){return ee(e,t)||ee(e,"data-"+t)}function u(e){return e.parentElement}function re(){return document}function c(e,t){while(e&&!t(e)){e=u(e)}return e?e:null}function L(e,t,r){var n=te(t,r);var i=te(t,"hx-disinherit");if(e!==t&&i&&(i==="*"||i.split(" ").indexOf(r)>=0)){return"unset"}else{return n}}function ne(t,r){var n=null;c(t,function(e){return n=L(t,e,r)});if(n!=="unset"){return n}}function h(e,t){var r=e.matches||e.matchesSelector||e.msMatchesSelector||e.mozMatchesSelector||e.webkitMatchesSelector||e.oMatchesSelector;return r&&r.call(e,t)}function A(e){var t=/<([a-z][^\/\0>\x20\t\r\n\f]*)/i;var r=t.exec(e);if(r){return r[1].toLowerCase()}else{return""}}function s(e,t){var r=new DOMParser;var n=r.parseFromString(e,"text/html");var i=n.body;while(t>0){t--;i=i.firstChild}if(i==null){i=re().createDocumentFragment()}return i}function N(e){return/<body/.test(e)}function l(e){var t=!N(e);var r=A(e);var n=e;if(r==="head"){n=n.replace(S,"")}if(Q.config.useTemplateFragments&&t){var i=s("<body><template>"+n+"</template></body>",0);var a=i.querySelector("template").content;if(Q.config.allowScriptTags){oe(a.querySelectorAll("script"),function(e){if(Q.config.inlineScriptNonce){e.nonce=Q.config.inlineScriptNonce}e.htmxExecuted=navigator.userAgent.indexOf("Firefox")===-1})}else{oe(a.querySelectorAll("script"),function(e){_(e)})}return a}switch(r){case"thead":case"tbody":case"tfoot":case"colgroup":case"caption":return s("<table>"+n+"</table>",1);case"col":return s("<table><colgroup>"+n+"</colgroup></table>",2);case"tr":return s("<table><tbody>"+n+"</tbody></table>",2);case"td":case"th":return s("<table><tbody><tr>"+n+"</tr></tbody></table>",3);case"script":case"style":return s("<div>"+n+"</div>",1);default:return s(n,0)}}function ie(e){if(e){e()}}function I(e,t){return Object.prototype.toString.call(e)==="[object "+t+"]"}function k(e){return I(e,"Function")}function P(e){return I(e,"Object")}function ae(e){var t="htmx-internal-data";var r=e[t];if(!r){r=e[t]={}}return r}function M(e){var t=[];if(e){for(var r=0;r<e.length;r++){t.push(e[r])}}return t}function oe(e,t){if(e){for(var r=0;r<e.length;r++){t(e[r])}}}function X(e){var t=e.getBoundingClientRect();var r=t.top;var n=t.bottom;return r<window.innerHeight&&n>=0}function se(e){if(e.getRootNode&&e.getRootNode()instanceof window.ShadowRoot){return re().body.contains(e.getRootNode().host)}else{return re().body.contains(e)}}function D(e){return e.trim().split(/\s+/)}function le(e,t){for(var r in t){if(t.hasOwnProperty(r)){e[r]=t[r]}}return e}function E(e){try{return JSON.parse(e)}catch(e){b(e);return null}}function U(){var e="htmx:localStorageTest";try{localStorage.setItem(e,e);localStorage.removeItem(e);return true}catch(e){return false}}function B(t){try{var e=new URL(t);if(e){t=e.pathname+e.search}if(!/^\/$/.test(t)){t=t.replace(/\/+$/,"")}return t}catch(e){return t}}function t(e){return Tr(re().body,function(){return eval(e)})}function F(t){var e=Q.on("htmx:load",function(e){t(e.detail.elt)});return e}function V(){Q.logger=function(e,t,r){if(console){console.log(t,e,r)}}}function j(){Q.logger=null}function C(e,t){if(t){return e.querySelector(t)}else{return C(re(),e)}}function f(e,t){if(t){return e.querySelectorAll(t)}else{return f(re(),e)}}function _(e,t){e=p(e);if(t){setTimeout(function(){_(e);e=null},t)}else{e.parentElement.removeChild(e)}}function z(e,t,r){e=p(e);if(r){setTimeout(function(){z(e,t);e=null},r)}else{e.classList&&e.classList.add(t)}}function n(e,t,r){e=p(e);if(r){setTimeout(function(){n(e,t);e=null},r)}else{if(e.classList){e.classList.remove(t);if(e.classList.length===0){e.removeAttribute("class")}}}}function $(e,t){e=p(e);e.classList.toggle(t)}function W(e,t){e=p(e);oe(e.parentElement.children,function(e){n(e,t)});z(e,t)}function v(e,t){e=p(e);if(e.closest){return e.closest(t)}else{do{if(e==null||h(e,t)){return e}}while(e=e&&u(e));return null}}function g(e,t){return e.substring(0,t.length)===t}function G(e,t){return e.substring(e.length-t.length)===t}function J(e){var t=e.trim();if(g(t,"<")&&G(t,"/>")){return t.substring(1,t.length-2)}else{return t}}function Z(e,t){if(t.indexOf("closest ")===0){return[v(e,J(t.substr(8)))]}else if(t.indexOf("find ")===0){return[C(e,J(t.substr(5)))]}else if(t==="next"){return[e.nextElementSibling]}else if(t.indexOf("next ")===0){return[K(e,J(t.substr(5)))]}else if(t==="previous"){return[e.previousElementSibling]}else if(t.indexOf("previous ")===0){return[Y(e,J(t.substr(9)))]}else if(t==="document"){return[document]}else if(t==="window"){return[window]}else if(t==="body"){return[document.body]}else{return re().querySelectorAll(J(t))}}var K=function(e,t){var r=re().querySelectorAll(t);for(var n=0;n<r.length;n++){var i=r[n];if(i.compareDocumentPosition(e)===Node.DOCUMENT_POSITION_PRECEDING){return i}}};var Y=function(e,t){var r=re().querySelectorAll(t);for(var n=r.length-1;n>=0;n--){var i=r[n];if(i.compareDocumentPosition(e)===Node.DOCUMENT_POSITION_FOLLOWING){return i}}};function ue(e,t){if(t){return Z(e,t)[0]}else{return Z(re().body,e)[0]}}function p(e){if(I(e,"String")){return C(e)}else{return e}}function ve(e,t,r){if(k(t)){return{target:re().body,event:e,listener:t}}else{return{target:p(e),event:t,listener:r}}}function de(t,r,n){jr(function(){var e=ve(t,r,n);e.target.addEventListener(e.event,e.listener)});var e=k(r);return e?r:n}function ge(t,r,n){jr(function(){var e=ve(t,r,n);e.target.removeEventListener(e.event,e.listener)});return k(r)?r:n}var pe=re().createElement("output");function me(e,t){var r=ne(e,t);if(r){if(r==="this"){return[xe(e,t)]}else{var n=Z(e,r);if(n.length===0){b('The selector "'+r+'" on '+t+" returned no matches!");return[pe]}else{return n}}}}function xe(e,t){return c(e,function(e){return te(e,t)!=null})}function ye(e){var t=ne(e,"hx-target");if(t){if(t==="this"){return xe(e,"hx-target")}else{return ue(e,t)}}else{var r=ae(e);if(r.boosted){return re().body}else{return e}}}function be(e){var t=Q.config.attributesToSettle;for(var r=0;r<t.length;r++){if(e===t[r]){return true}}return false}function we(t,r){oe(t.attributes,function(e){if(!r.hasAttribute(e.name)&&be(e.name)){t.removeAttribute(e.name)}});oe(r.attributes,function(e){if(be(e.name)){t.setAttribute(e.name,e.value)}})}function Se(e,t){var r=Fr(t);for(var n=0;n<r.length;n++){var i=r[n];try{if(i.isInlineSwap(e)){return true}}catch(e){b(e)}}return e==="outerHTML"}function Ee(e,i,a){var t="#"+ee(i,"id");var o="outerHTML";if(e==="true"){}else if(e.indexOf(":")>0){o=e.substr(0,e.indexOf(":"));t=e.substr(e.indexOf(":")+1,e.length)}else{o=e}var r=re().querySelectorAll(t);if(r){oe(r,function(e){var t;var r=i.cloneNode(true);t=re().createDocumentFragment();t.appendChild(r);if(!Se(o,e)){t=r}var n={shouldSwap:true,target:e,fragment:t};if(!ce(e,"htmx:oobBeforeSwap",n))return;e=n.target;if(n["shouldSwap"]){Fe(o,e,e,t,a)}oe(a.elts,function(e){ce(e,"htmx:oobAfterSwap",n)})});i.parentNode.removeChild(i)}else{i.parentNode.removeChild(i);fe(re().body,"htmx:oobErrorNoTarget",{content:i})}return e}function Ce(e,t,r){var n=ne(e,"hx-select-oob");if(n){var i=n.split(",");for(var a=0;a<i.length;a++){var o=i[a].split(":",2);var s=o[0].trim();if(s.indexOf("#")===0){s=s.substring(1)}var l=o[1]||"true";var u=t.querySelector("#"+s);if(u){Ee(l,u,r)}}}oe(f(t,"[hx-swap-oob], [data-hx-swap-oob]"),function(e){var t=te(e,"hx-swap-oob");if(t!=null){Ee(t,e,r)}})}function Re(e){oe(f(e,"[hx-preserve], [data-hx-preserve]"),function(e){var t=te(e,"id");var r=re().getElementById(t);if(r!=null){e.parentNode.replaceChild(r,e)}})}function Te(o,e,s){oe(e.querySelectorAll("[id]"),function(e){var t=ee(e,"id");if(t&&t.length>0){var r=t.replace("'","\\'");var n=e.tagName.replace(":","\\:");var i=o.querySelector(n+"[id='"+r+"']");if(i&&i!==o){var a=e.cloneNode();we(e,i);s.tasks.push(function(){we(e,a)})}}})}function Oe(e){return function(){n(e,Q.config.addedClass);zt(e);Nt(e);qe(e);ce(e,"htmx:load")}}function qe(e){var t="[autofocus]";var r=h(e,t)?e:e.querySelector(t);if(r!=null){r.focus()}}function a(e,t,r,n){Te(e,r,n);while(r.childNodes.length>0){var i=r.firstChild;z(i,Q.config.addedClass);e.insertBefore(i,t);if(i.nodeType!==Node.TEXT_NODE&&i.nodeType!==Node.COMMENT_NODE){n.tasks.push(Oe(i))}}}function He(e,t){var r=0;while(r<e.length){t=(t<<5)-t+e.charCodeAt(r++)|0}return t}function Le(e){var t=0;if(e.attributes){for(var r=0;r<e.attributes.length;r++){var n=e.attributes[r];if(n.value){t=He(n.name,t);t=He(n.value,t)}}}return t}function Ae(e){var t=ae(e);if(t.onHandlers){for(var r=0;r<t.onHandlers.length;r++){const n=t.onHandlers[r];e.removeEventListener(n.event,n.listener)}delete t.onHandlers}}function Ne(e){var t=ae(e);if(t.timeout){clearTimeout(t.timeout)}if(t.webSocket){t.webSocket.close()}if(t.sseEventSource){t.sseEventSource.close()}if(t.listenerInfos){oe(t.listenerInfos,function(e){if(e.on){e.on.removeEventListener(e.trigger,e.listener)}})}Ae(e);oe(Object.keys(t),function(e){delete t[e]})}function m(e){ce(e,"htmx:beforeCleanupElement");Ne(e);if(e.children){oe(e.children,function(e){m(e)})}}function Ie(t,e,r){if(t.tagName==="BODY"){return Ue(t,e,r)}else{var n;var i=t.previousSibling;a(u(t),t,e,r);if(i==null){n=u(t).firstChild}else{n=i.nextSibling}r.elts=r.elts.filter(function(e){return e!=t});while(n&&n!==t){if(n.nodeType===Node.ELEMENT_NODE){r.elts.push(n)}n=n.nextElementSibling}m(t);u(t).removeChild(t)}}function ke(e,t,r){return a(e,e.firstChild,t,r)}function Pe(e,t,r){return a(u(e),e,t,r)}function Me(e,t,r){return a(e,null,t,r)}function Xe(e,t,r){return a(u(e),e.nextSibling,t,r)}function De(e,t,r){m(e);return u(e).removeChild(e)}function Ue(e,t,r){var n=e.firstChild;a(e,n,t,r);if(n){while(n.nextSibling){m(n.nextSibling);e.removeChild(n.nextSibling)}m(n);e.removeChild(n)}}function Be(e,t,r){var n=r||ne(e,"hx-select");if(n){var i=re().createDocumentFragment();oe(t.querySelectorAll(n),function(e){i.appendChild(e)});t=i}return t}function Fe(e,t,r,n,i){switch(e){case"none":return;case"outerHTML":Ie(r,n,i);return;case"afterbegin":ke(r,n,i);return;case"beforebegin":Pe(r,n,i);return;case"beforeend":Me(r,n,i);return;case"afterend":Xe(r,n,i);return;case"delete":De(r,n,i);return;default:var a=Fr(t);for(var o=0;o<a.length;o++){var s=a[o];try{var l=s.handleSwap(e,r,n,i);if(l){if(typeof l.length!=="undefined"){for(var u=0;u<l.length;u++){var f=l[u];if(f.nodeType!==Node.TEXT_NODE&&f.nodeType!==Node.COMMENT_NODE){i.tasks.push(Oe(f))}}}return}}catch(e){b(e)}}if(e==="innerHTML"){Ue(r,n,i)}else{Fe(Q.config.defaultSwapStyle,t,r,n,i)}}}function Ve(e){if(e.indexOf("<title")>-1){var t=e.replace(H,"");var r=t.match(q);if(r){return r[2]}}}function je(e,t,r,n,i,a){i.title=Ve(n);var o=l(n);if(o){Ce(r,o,i);o=Be(r,o,a);Re(o);return Fe(e,r,t,o,i)}}function _e(e,t,r){var n=e.getResponseHeader(t);if(n.indexOf("{")===0){var i=E(n);for(var a in i){if(i.hasOwnProperty(a)){var o=i[a];if(!P(o)){o={value:o}}ce(r,a,o)}}}else{var s=n.split(",");for(var l=0;l<s.length;l++){ce(r,s[l].trim(),[])}}}var ze=/\s/;var x=/[\s,]/;var $e=/[_$a-zA-Z]/;var We=/[_$a-zA-Z0-9]/;var Ge=['"',"'","/"];var Je=/[^\s]/;var Ze=/[{(]/;var Ke=/[})]/;function Ye(e){var t=[];var r=0;while(r<e.length){if($e.exec(e.charAt(r))){var n=r;while(We.exec(e.charAt(r+1))){r++}t.push(e.substr(n,r-n+1))}else if(Ge.indexOf(e.charAt(r))!==-1){var i=e.charAt(r);var n=r;r++;while(r<e.length&&e.charAt(r)!==i){if(e.charAt(r)==="\\"){r++}r++}t.push(e.substr(n,r-n+1))}else{var a=e.charAt(r);t.push(a)}r++}return t}function Qe(e,t,r){return $e.exec(e.charAt(0))&&e!=="true"&&e!=="false"&&e!=="this"&&e!==r&&t!=="."}function et(e,t,r){if(t[0]==="["){t.shift();var n=1;var i=" return (function("+r+"){ return (";var a=null;while(t.length>0){var o=t[0];if(o==="]"){n--;if(n===0){if(a===null){i=i+"true"}t.shift();i+=")})";try{var s=Tr(e,function(){return Function(i)()},function(){return true});s.source=i;return s}catch(e){fe(re().body,"htmx:syntax:error",{error:e,source:i});return null}}}else if(o==="["){n++}if(Qe(o,a,r)){i+="(("+r+"."+o+") ? ("+r+"."+o+") : (window."+o+"))"}else{i=i+o}a=t.shift()}}}function y(e,t){var r="";while(e.length>0&&!t.test(e[0])){r+=e.shift()}return r}function tt(e){var t;if(e.length>0&&Ze.test(e[0])){e.shift();t=y(e,Ke).trim();e.shift()}else{t=y(e,x)}return t}var rt="input, textarea, select";function nt(e,t,r){var n=[];var i=Ye(t);do{y(i,Je);var a=i.length;var o=y(i,/[,\[\s]/);if(o!==""){if(o==="every"){var s={trigger:"every"};y(i,Je);s.pollInterval=d(y(i,/[,\[\s]/));y(i,Je);var l=et(e,i,"event");if(l){s.eventFilter=l}n.push(s)}else if(o.indexOf("sse:")===0){n.push({trigger:"sse",sseEvent:o.substr(4)})}else{var u={trigger:o};var l=et(e,i,"event");if(l){u.eventFilter=l}while(i.length>0&&i[0]!==","){y(i,Je);var f=i.shift();if(f==="changed"){u.changed=true}else if(f==="once"){u.once=true}else if(f==="consume"){u.consume=true}else if(f==="delay"&&i[0]===":"){i.shift();u.delay=d(y(i,x))}else if(f==="from"&&i[0]===":"){i.shift();if(Ze.test(i[0])){var c=tt(i)}else{var c=y(i,x);if(c==="closest"||c==="find"||c==="next"||c==="previous"){i.shift();var h=tt(i);if(h.length>0){c+=" "+h}}}u.from=c}else if(f==="target"&&i[0]===":"){i.shift();u.target=tt(i)}else if(f==="throttle"&&i[0]===":"){i.shift();u.throttle=d(y(i,x))}else if(f==="queue"&&i[0]===":"){i.shift();u.queue=y(i,x)}else if(f==="root"&&i[0]===":"){i.shift();u[f]=tt(i)}else if(f==="threshold"&&i[0]===":"){i.shift();u[f]=y(i,x)}else{fe(e,"htmx:syntax:error",{token:i.shift()})}}n.push(u)}}if(i.length===a){fe(e,"htmx:syntax:error",{token:i.shift()})}y(i,Je)}while(i[0]===","&&i.shift());if(r){r[t]=n}return n}function it(e){var t=te(e,"hx-trigger");var r=[];if(t){var n=Q.config.triggerSpecsCache;r=n&&n[t]||nt(e,t,n)}if(r.length>0){return r}else if(h(e,"form")){return[{trigger:"submit"}]}else if(h(e,'input[type="button"], input[type="submit"]')){return[{trigger:"click"}]}else if(h(e,rt)){return[{trigger:"change"}]}else{return[{trigger:"click"}]}}function at(e){ae(e).cancelled=true}function ot(e,t,r){var n=ae(e);n.timeout=setTimeout(function(){if(se(e)&&n.cancelled!==true){if(!ct(r,e,Wt("hx:poll:trigger",{triggerSpec:r,target:e}))){t(e)}ot(e,t,r)}},r.pollInterval)}function st(e){return location.hostname===e.hostname&&ee(e,"href")&&ee(e,"href").indexOf("#")!==0}function lt(t,r,e){if(t.tagName==="A"&&st(t)&&(t.target===""||t.target==="_self")||t.tagName==="FORM"){r.boosted=true;var n,i;if(t.tagName==="A"){n="get";i=ee(t,"href")}else{var a=ee(t,"method");n=a?a.toLowerCase():"get";if(n==="get"){}i=ee(t,"action")}e.forEach(function(e){ht(t,function(e,t){if(v(e,Q.config.disableSelector)){m(e);return}he(n,i,e,t)},r,e,true)})}}function ut(e,t){if(e.type==="submit"||e.type==="click"){if(t.tagName==="FORM"){return true}if(h(t,'input[type="submit"], button')&&v(t,"form")!==null){return true}if(t.tagName==="A"&&t.href&&(t.getAttribute("href")==="#"||t.getAttribute("href").indexOf("#")!==0)){return true}}return false}function ft(e,t){return ae(e).boosted&&e.tagName==="A"&&t.type==="click"&&(t.ctrlKey||t.metaKey)}function ct(e,t,r){var n=e.eventFilter;if(n){try{return n.call(t,r)!==true}catch(e){fe(re().body,"htmx:eventFilter:error",{error:e,source:n.source});return true}}return false}function ht(a,o,e,s,l){var u=ae(a);var t;if(s.from){t=Z(a,s.from)}else{t=[a]}if(s.changed){t.forEach(function(e){var t=ae(e);t.lastValue=e.value})}oe(t,function(n){var i=function(e){if(!se(a)){n.removeEventListener(s.trigger,i);return}if(ft(a,e)){return}if(l||ut(e,a)){e.preventDefault()}if(ct(s,a,e)){return}var t=ae(e);t.triggerSpec=s;if(t.handledFor==null){t.handledFor=[]}if(t.handledFor.indexOf(a)<0){t.handledFor.push(a);if(s.consume){e.stopPropagation()}if(s.target&&e.target){if(!h(e.target,s.target)){return}}if(s.once){if(u.triggeredOnce){return}else{u.triggeredOnce=true}}if(s.changed){var r=ae(n);if(r.lastValue===n.value){return}r.lastValue=n.value}if(u.delayed){clearTimeout(u.delayed)}if(u.throttle){return}if(s.throttle>0){if(!u.throttle){o(a,e);u.throttle=setTimeout(function(){u.throttle=null},s.throttle)}}else if(s.delay>0){u.delayed=setTimeout(function(){o(a,e)},s.delay)}else{ce(a,"htmx:trigger");o(a,e)}}};if(e.listenerInfos==null){e.listenerInfos=[]}e.listenerInfos.push({trigger:s.trigger,listener:i,on:n});n.addEventListener(s.trigger,i)})}var vt=false;var dt=null;function gt(){if(!dt){dt=function(){vt=true};window.addEventListener("scroll",dt);setInterval(function(){if(vt){vt=false;oe(re().querySelectorAll("[hx-trigger='revealed'],[data-hx-trigger='revealed']"),function(e){pt(e)})}},200)}}function pt(t){if(!o(t,"data-hx-revealed")&&X(t)){t.setAttribute("data-hx-revealed","true");var e=ae(t);if(e.initHash){ce(t,"revealed")}else{t.addEventListener("htmx:afterProcessNode",function(e){ce(t,"revealed")},{once:true})}}}function mt(e,t,r){var n=D(r);for(var i=0;i<n.length;i++){var a=n[i].split(/:(.+)/);if(a[0]==="connect"){xt(e,a[1],0)}if(a[0]==="send"){bt(e)}}}function xt(s,r,n){if(!se(s)){return}if(r.indexOf("/")==0){var e=location.hostname+(location.port?":"+location.port:"");if(location.protocol=="https:"){r="wss://"+e+r}else if(location.protocol=="http:"){r="ws://"+e+r}}var t=Q.createWebSocket(r);t.onerror=function(e){fe(s,"htmx:wsError",{error:e,socket:t});yt(s)};t.onclose=function(e){if([1006,1012,1013].indexOf(e.code)>=0){var t=wt(n);setTimeout(function(){xt(s,r,n+1)},t)}};t.onopen=function(e){n=0};ae(s).webSocket=t;t.addEventListener("message",function(e){if(yt(s)){return}var t=e.data;R(s,function(e){t=e.transformResponse(t,null,s)});var r=T(s);var n=l(t);var i=M(n.children);for(var a=0;a<i.length;a++){var o=i[a];Ee(te(o,"hx-swap-oob")||"true",o,r)}nr(r.tasks)})}function yt(e){if(!se(e)){ae(e).webSocket.close();return true}}function bt(u){var f=c(u,function(e){return ae(e).webSocket!=null});if(f){u.addEventListener(it(u)[0].trigger,function(e){var t=ae(f).webSocket;var r=xr(u,f);var n=dr(u,"post");var i=n.errors;var a=n.values;var o=Hr(u);var s=le(a,o);var l=yr(s,u);l["HEADERS"]=r;if(i&&i.length>0){ce(u,"htmx:validation:halted",i);return}t.send(JSON.stringify(l));if(ut(e,u)){e.preventDefault()}})}else{fe(u,"htmx:noWebSocketSourceError")}}function wt(e){var t=Q.config.wsReconnectDelay;if(typeof t==="function"){return t(e)}if(t==="full-jitter"){var r=Math.min(e,6);var n=1e3*Math.pow(2,r);return n*Math.random()}b('htmx.config.wsReconnectDelay must either be a function or the string "full-jitter"')}function St(e,t,r){var n=D(r);for(var i=0;i<n.length;i++){var a=n[i].split(/:(.+)/);if(a[0]==="connect"){Et(e,a[1])}if(a[0]==="swap"){Ct(e,a[1])}}}function Et(t,e){var r=Q.createEventSource(e);r.onerror=function(e){fe(t,"htmx:sseError",{error:e,source:r});Tt(t)};ae(t).sseEventSource=r}function Ct(a,o){var s=c(a,Ot);if(s){var l=ae(s).sseEventSource;var u=function(e){if(Tt(s)){return}if(!se(a)){l.removeEventListener(o,u);return}var t=e.data;R(a,function(e){t=e.transformResponse(t,null,a)});var r=wr(a);var n=ye(a);var i=T(a);je(r.swapStyle,n,a,t,i);nr(i.tasks);ce(a,"htmx:sseMessage",e)};ae(a).sseListener=u;l.addEventListener(o,u)}else{fe(a,"htmx:noSSESourceError")}}function Rt(e,t,r){var n=c(e,Ot);if(n){var i=ae(n).sseEventSource;var a=function(){if(!Tt(n)){if(se(e)){t(e)}else{i.removeEventListener(r,a)}}};ae(e).sseListener=a;i.addEventListener(r,a)}else{fe(e,"htmx:noSSESourceError")}}function Tt(e){if(!se(e)){ae(e).sseEventSource.close();return true}}function Ot(e){return ae(e).sseEventSource!=null}function qt(e,t,r,n){var i=function(){if(!r.loaded){r.loaded=true;t(e)}};if(n>0){setTimeout(i,n)}else{i()}}function Ht(t,i,e){var a=false;oe(w,function(r){if(o(t,"hx-"+r)){var n=te(t,"hx-"+r);a=true;i.path=n;i.verb=r;e.forEach(function(e){Lt(t,e,i,function(e,t){if(v(e,Q.config.disableSelector)){m(e);return}he(r,n,e,t)})})}});return a}function Lt(n,e,t,r){if(e.sseEvent){Rt(n,r,e.sseEvent)}else if(e.trigger==="revealed"){gt();ht(n,r,t,e);pt(n)}else if(e.trigger==="intersect"){var i={};if(e.root){i.root=ue(n,e.root)}if(e.threshold){i.threshold=parseFloat(e.threshold)}var a=new IntersectionObserver(function(e){for(var t=0;t<e.length;t++){var r=e[t];if(r.isIntersecting){ce(n,"intersect");break}}},i);a.observe(n);ht(n,r,t,e)}else if(e.trigger==="load"){if(!ct(e,n,Wt("load",{elt:n}))){qt(n,r,t,e.delay)}}else if(e.pollInterval>0){t.polling=true;ot(n,r,e)}else{ht(n,r,t,e)}}function At(e){if(!e.htmxExecuted&&Q.config.allowScriptTags&&(e.type==="text/javascript"||e.type==="module"||e.type==="")){var t=re().createElement("script");oe(e.attributes,function(e){t.setAttribute(e.name,e.value)});t.textContent=e.textContent;t.async=false;if(Q.config.inlineScriptNonce){t.nonce=Q.config.inlineScriptNonce}var r=e.parentElement;try{r.insertBefore(t,e)}catch(e){b(e)}finally{if(e.parentElement){e.parentElement.removeChild(e)}}}}function Nt(e){if(h(e,"script")){At(e)}oe(f(e,"script"),function(e){At(e)})}function It(e){var t=e.attributes;if(!t){return false}for(var r=0;r<t.length;r++){var n=t[r].name;if(g(n,"hx-on:")||g(n,"data-hx-on:")||g(n,"hx-on-")||g(n,"data-hx-on-")){return true}}return false}function kt(e){var t=null;var r=[];if(It(e)){r.push(e)}if(document.evaluate){var n=document.evaluate('.//*[@*[ starts-with(name(), "hx-on:") or starts-with(name(), "data-hx-on:") or'+' starts-with(name(), "hx-on-") or starts-with(name(), "data-hx-on-") ]]',e);while(t=n.iterateNext())r.push(t)}else if(typeof e.getElementsByTagName==="function"){var i=e.getElementsByTagName("*");for(var a=0;a<i.length;a++){if(It(i[a])){r.push(i[a])}}}return r}function Pt(e){if(e.querySelectorAll){var t=", [hx-boost] a, [data-hx-boost] a, a[hx-boost], a[data-hx-boost]";var r=e.querySelectorAll(i+t+", form, [type='submit'], [hx-sse], [data-hx-sse], [hx-ws],"+" [data-hx-ws], [hx-ext], [data-hx-ext], [hx-trigger], [data-hx-trigger], [hx-on], [data-hx-on]");return r}else{return[]}}function Mt(e){var t=v(e.target,"button, input[type='submit']");var r=Dt(e);if(r){r.lastButtonClicked=t}}function Xt(e){var t=Dt(e);if(t){t.lastButtonClicked=null}}function Dt(e){var t=v(e.target,"button, input[type='submit']");if(!t){return}var r=p("#"+ee(t,"form"))||v(t,"form");if(!r){return}return ae(r)}function Ut(e){e.addEventListener("click",Mt);e.addEventListener("focusin",Mt);e.addEventListener("focusout",Xt)}function Bt(e){var t=Ye(e);var r=0;for(var n=0;n<t.length;n++){const i=t[n];if(i==="{"){r++}else if(i==="}"){r--}}return r}function Ft(t,e,r){var n=ae(t);if(!Array.isArray(n.onHandlers)){n.onHandlers=[]}var i;var a=function(e){return Tr(t,function(){if(!i){i=new Function("event",r)}i.call(t,e)})};t.addEventListener(e,a);n.onHandlers.push({event:e,listener:a})}function Vt(e){var t=te(e,"hx-on");if(t){var r={};var n=t.split("\n");var i=null;var a=0;while(n.length>0){var o=n.shift();var s=o.match(/^\s*([a-zA-Z:\-\.]+:)(.*)/);if(a===0&&s){o.split(":");i=s[1].slice(0,-1);r[i]=s[2]}else{r[i]+=o}a+=Bt(o)}for(var l in r){Ft(e,l,r[l])}}}function jt(e){Ae(e);for(var t=0;t<e.attributes.length;t++){var r=e.attributes[t].name;var n=e.attributes[t].value;if(g(r,"hx-on")||g(r,"data-hx-on")){var i=r.indexOf("-on")+3;var a=r.slice(i,i+1);if(a==="-"||a===":"){var o=r.slice(i+1);if(g(o,":")){o="htmx"+o}else if(g(o,"-")){o="htmx:"+o.slice(1)}else if(g(o,"htmx-")){o="htmx:"+o.slice(5)}Ft(e,o,n)}}}}function _t(t){if(v(t,Q.config.disableSelector)){m(t);return}var r=ae(t);if(r.initHash!==Le(t)){Ne(t);r.initHash=Le(t);Vt(t);ce(t,"htmx:beforeProcessNode");if(t.value){r.lastValue=t.value}var e=it(t);var n=Ht(t,r,e);if(!n){if(ne(t,"hx-boost")==="true"){lt(t,r,e)}else if(o(t,"hx-trigger")){e.forEach(function(e){Lt(t,e,r,function(){})})}}if(t.tagName==="FORM"||ee(t,"type")==="submit"&&o(t,"form")){Ut(t)}var i=te(t,"hx-sse");if(i){St(t,r,i)}var a=te(t,"hx-ws");if(a){mt(t,r,a)}ce(t,"htmx:afterProcessNode")}}function zt(e){e=p(e);if(v(e,Q.config.disableSelector)){m(e);return}_t(e);oe(Pt(e),function(e){_t(e)});oe(kt(e),jt)}function $t(e){return e.replace(/([a-z0-9])([A-Z])/g,"$1-$2").toLowerCase()}function Wt(e,t){var r;if(window.CustomEvent&&typeof window.CustomEvent==="function"){r=new CustomEvent(e,{bubbles:true,cancelable:true,detail:t})}else{r=re().createEvent("CustomEvent");r.initCustomEvent(e,true,true,t)}return r}function fe(e,t,r){ce(e,t,le({error:t},r))}function Gt(e){return e==="htmx:afterProcessNode"}function R(e,t){oe(Fr(e),function(e){try{t(e)}catch(e){b(e)}})}function b(e){if(console.error){console.error(e)}else if(console.log){console.log("ERROR: ",e)}}function ce(e,t,r){e=p(e);if(r==null){r={}}r["elt"]=e;var n=Wt(t,r);if(Q.logger&&!Gt(t)){Q.logger(e,t,r)}if(r.error){b(r.error);ce(e,"htmx:error",{errorInfo:r})}var i=e.dispatchEvent(n);var a=$t(t);if(i&&a!==t){var o=Wt(a,n.detail);i=i&&e.dispatchEvent(o)}R(e,function(e){i=i&&(e.onEvent(t,n)!==false&&!n.defaultPrevented)});return i}var Jt=location.pathname+location.search;function Zt(){var e=re().querySelector("[hx-history-elt],[data-hx-history-elt]");return e||re().body}function Kt(e,t,r,n){if(!U()){return}if(Q.config.historyCacheSize<=0){localStorage.removeItem("htmx-history-cache");return}e=B(e);var i=E(localStorage.getItem("htmx-history-cache"))||[];for(var a=0;a<i.length;a++){if(i[a].url===e){i.splice(a,1);break}}var o={url:e,content:t,title:r,scroll:n};ce(re().body,"htmx:historyItemCreated",{item:o,cache:i});i.push(o);while(i.length>Q.config.historyCacheSize){i.shift()}while(i.length>0){try{localStorage.setItem("htmx-history-cache",JSON.stringify(i));break}catch(e){fe(re().body,"htmx:historyCacheError",{cause:e,cache:i});i.shift()}}}function Yt(e){if(!U()){return null}e=B(e);var t=E(localStorage.getItem("htmx-history-cache"))||[];for(var r=0;r<t.length;r++){if(t[r].url===e){return t[r]}}return null}function Qt(e){var t=Q.config.requestClass;var r=e.cloneNode(true);oe(f(r,"."+t),function(e){n(e,t)});return r.innerHTML}function er(){var e=Zt();var t=Jt||location.pathname+location.search;var r;try{r=re().querySelector('[hx-history="false" i],[data-hx-history="false" i]')}catch(e){r=re().querySelector('[hx-history="false"],[data-hx-history="false"]')}if(!r){ce(re().body,"htmx:beforeHistorySave",{path:t,historyElt:e});Kt(t,Qt(e),re().title,window.scrollY)}if(Q.config.historyEnabled)history.replaceState({htmx:true},re().title,window.location.href)}function tr(e){if(Q.config.getCacheBusterParam){e=e.replace(/org\.htmx\.cache-buster=[^&]*&?/,"");if(G(e,"&")||G(e,"?")){e=e.slice(0,-1)}}if(Q.config.historyEnabled){history.pushState({htmx:true},"",e)}Jt=e}function rr(e){if(Q.config.historyEnabled)history.replaceState({htmx:true},"",e);Jt=e}function nr(e){oe(e,function(e){e.call()})}function ir(a){var e=new XMLHttpRequest;var o={path:a,xhr:e};ce(re().body,"htmx:historyCacheMiss",o);e.open("GET",a,true);e.setRequestHeader("HX-Request","true");e.setRequestHeader("HX-History-Restore-Request","true");e.setRequestHeader("HX-Current-URL",re().location.href);e.onload=function(){if(this.status>=200&&this.status<400){ce(re().body,"htmx:historyCacheMissLoad",o);var e=l(this.response);e=e.querySelector("[hx-history-elt],[data-hx-history-elt]")||e;var t=Zt();var r=T(t);var n=Ve(this.response);if(n){var i=C("title");if(i){i.innerHTML=n}else{window.document.title=n}}Ue(t,e,r);nr(r.tasks);Jt=a;ce(re().body,"htmx:historyRestore",{path:a,cacheMiss:true,serverResponse:this.response})}else{fe(re().body,"htmx:historyCacheMissLoadError",o)}};e.send()}function ar(e){er();e=e||location.pathname+location.search;var t=Yt(e);if(t){var r=l(t.content);var n=Zt();var i=T(n);Ue(n,r,i);nr(i.tasks);document.title=t.title;setTimeout(function(){window.scrollTo(0,t.scroll)},0);Jt=e;ce(re().body,"htmx:historyRestore",{path:e,item:t})}else{if(Q.config.refreshOnHistoryMiss){window.location.reload(true)}else{ir(e)}}}function or(e){var t=me(e,"hx-indicator");if(t==null){t=[e]}oe(t,function(e){var t=ae(e);t.requestCount=(t.requestCount||0)+1;e.classList["add"].call(e.classList,Q.config.requestClass)});return t}function sr(e){var t=me(e,"hx-disabled-elt");if(t==null){t=[]}oe(t,function(e){var t=ae(e);t.requestCount=(t.requestCount||0)+1;e.setAttribute("disabled","")});return t}function lr(e,t){oe(e,function(e){var t=ae(e);t.requestCount=(t.requestCount||0)-1;if(t.requestCount===0){e.classList["remove"].call(e.classList,Q.config.requestClass)}});oe(t,function(e){var t=ae(e);t.requestCount=(t.requestCount||0)-1;if(t.requestCount===0){e.removeAttribute("disabled")}})}function ur(e,t){for(var r=0;r<e.length;r++){var n=e[r];if(n.isSameNode(t)){return true}}return false}function fr(e){if(e.name===""||e.name==null||e.disabled||v(e,"fieldset[disabled]")){return false}if(e.type==="button"||e.type==="submit"||e.tagName==="image"||e.tagName==="reset"||e.tagName==="file"){return false}if(e.type==="checkbox"||e.type==="radio"){return e.checked}return true}function cr(e,t,r){if(e!=null&&t!=null){var n=r[e];if(n===undefined){r[e]=t}else if(Array.isArray(n)){if(Array.isArray(t)){r[e]=n.concat(t)}else{n.push(t)}}else{if(Array.isArray(t)){r[e]=[n].concat(t)}else{r[e]=[n,t]}}}}function hr(t,r,n,e,i){if(e==null||ur(t,e)){return}else{t.push(e)}if(fr(e)){var a=ee(e,"name");var o=e.value;if(e.multiple&&e.tagName==="SELECT"){o=M(e.querySelectorAll("option:checked")).map(function(e){return e.value})}if(e.files){o=M(e.files)}cr(a,o,r);if(i){vr(e,n)}}if(h(e,"form")){var s=e.elements;oe(s,function(e){hr(t,r,n,e,i)})}}function vr(e,t){if(e.willValidate){ce(e,"htmx:validation:validate");if(!e.checkValidity()){t.push({elt:e,message:e.validationMessage,validity:e.validity});ce(e,"htmx:validation:failed",{message:e.validationMessage,validity:e.validity})}}}function dr(e,t){var r=[];var n={};var i={};var a=[];var o=ae(e);if(o.lastButtonClicked&&!se(o.lastButtonClicked)){o.lastButtonClicked=null}var s=h(e,"form")&&e.noValidate!==true||te(e,"hx-validate")==="true";if(o.lastButtonClicked){s=s&&o.lastButtonClicked.formNoValidate!==true}if(t!=="get"){hr(r,i,a,v(e,"form"),s)}hr(r,n,a,e,s);if(o.lastButtonClicked||e.tagName==="BUTTON"||e.tagName==="INPUT"&&ee(e,"type")==="submit"){var l=o.lastButtonClicked||e;var u=ee(l,"name");cr(u,l.value,i)}var f=me(e,"hx-include");oe(f,function(e){hr(r,n,a,e,s);if(!h(e,"form")){oe(e.querySelectorAll(rt),function(e){hr(r,n,a,e,s)})}});n=le(n,i);return{errors:a,values:n}}function gr(e,t,r){if(e!==""){e+="&"}if(String(r)==="[object Object]"){r=JSON.stringify(r)}var n=encodeURIComponent(r);e+=encodeURIComponent(t)+"="+n;return e}function pr(e){var t="";for(var r in e){if(e.hasOwnProperty(r)){var n=e[r];if(Array.isArray(n)){oe(n,function(e){t=gr(t,r,e)})}else{t=gr(t,r,n)}}}return t}function mr(e){var t=new FormData;for(var r in e){if(e.hasOwnProperty(r)){var n=e[r];if(Array.isArray(n)){oe(n,function(e){t.append(r,e)})}else{t.append(r,n)}}}return t}function xr(e,t,r){var n={"HX-Request":"true","HX-Trigger":ee(e,"id"),"HX-Trigger-Name":ee(e,"name"),"HX-Target":te(t,"id"),"HX-Current-URL":re().location.href};Rr(e,"hx-headers",false,n);if(r!==undefined){n["HX-Prompt"]=r}if(ae(e).boosted){n["HX-Boosted"]="true"}return n}function yr(t,e){var r=ne(e,"hx-params");if(r){if(r==="none"){return{}}else if(r==="*"){return t}else if(r.indexOf("not ")===0){oe(r.substr(4).split(","),function(e){e=e.trim();delete t[e]});return t}else{var n={};oe(r.split(","),function(e){e=e.trim();n[e]=t[e]});return n}}else{return t}}function br(e){return ee(e,"href")&&ee(e,"href").indexOf("#")>=0}function wr(e,t){var r=t?t:ne(e,"hx-swap");var n={swapStyle:ae(e).boosted?"innerHTML":Q.config.defaultSwapStyle,swapDelay:Q.config.defaultSwapDelay,settleDelay:Q.config.defaultSettleDelay};if(Q.config.scrollIntoViewOnBoost&&ae(e).boosted&&!br(e)){n["show"]="top"}if(r){var i=D(r);if(i.length>0){for(var a=0;a<i.length;a++){var o=i[a];if(o.indexOf("swap:")===0){n["swapDelay"]=d(o.substr(5))}else if(o.indexOf("settle:")===0){n["settleDelay"]=d(o.substr(7))}else if(o.indexOf("transition:")===0){n["transition"]=o.substr(11)==="true"}else if(o.indexOf("ignoreTitle:")===0){n["ignoreTitle"]=o.substr(12)==="true"}else if(o.indexOf("scroll:")===0){var s=o.substr(7);var l=s.split(":");var u=l.pop();var f=l.length>0?l.join(":"):null;n["scroll"]=u;n["scrollTarget"]=f}else if(o.indexOf("show:")===0){var c=o.substr(5);var l=c.split(":");var h=l.pop();var f=l.length>0?l.join(":"):null;n["show"]=h;n["showTarget"]=f}else if(o.indexOf("focus-scroll:")===0){var v=o.substr("focus-scroll:".length);n["focusScroll"]=v=="true"}else if(a==0){n["swapStyle"]=o}else{b("Unknown modifier in hx-swap: "+o)}}}}return n}function Sr(e){return ne(e,"hx-encoding")==="multipart/form-data"||h(e,"form")&&ee(e,"enctype")==="multipart/form-data"}function Er(t,r,n){var i=null;R(r,function(e){if(i==null){i=e.encodeParameters(t,n,r)}});if(i!=null){return i}else{if(Sr(r)){return mr(n)}else{return pr(n)}}}function T(e){return{tasks:[],elts:[e]}}function Cr(e,t){var r=e[0];var n=e[e.length-1];if(t.scroll){var i=null;if(t.scrollTarget){i=ue(r,t.scrollTarget)}if(t.scroll==="top"&&(r||i)){i=i||r;i.scrollTop=0}if(t.scroll==="bottom"&&(n||i)){i=i||n;i.scrollTop=i.scrollHeight}}if(t.show){var i=null;if(t.showTarget){var a=t.showTarget;if(t.showTarget==="window"){a="body"}i=ue(r,a)}if(t.show==="top"&&(r||i)){i=i||r;i.scrollIntoView({block:"start",behavior:Q.config.scrollBehavior})}if(t.show==="bottom"&&(n||i)){i=i||n;i.scrollIntoView({block:"end",behavior:Q.config.scrollBehavior})}}}function Rr(e,t,r,n){if(n==null){n={}}if(e==null){return n}var i=te(e,t);if(i){var a=i.trim();var o=r;if(a==="unset"){return null}if(a.indexOf("javascript:")===0){a=a.substr(11);o=true}else if(a.indexOf("js:")===0){a=a.substr(3);o=true}if(a.indexOf("{")!==0){a="{"+a+"}"}var s;if(o){s=Tr(e,function(){return Function("return ("+a+")")()},{})}else{s=E(a)}for(var l in s){if(s.hasOwnProperty(l)){if(n[l]==null){n[l]=s[l]}}}}return Rr(u(e),t,r,n)}function Tr(e,t,r){if(Q.config.allowEval){return t()}else{fe(e,"htmx:evalDisallowedError");return r}}function Or(e,t){return Rr(e,"hx-vars",true,t)}function qr(e,t){return Rr(e,"hx-vals",false,t)}function Hr(e){return le(Or(e),qr(e))}function Lr(t,r,n){if(n!==null){try{t.setRequestHeader(r,n)}catch(e){t.setRequestHeader(r,encodeURIComponent(n));t.setRequestHeader(r+"-URI-AutoEncoded","true")}}}function Ar(t){if(t.responseURL&&typeof URL!=="undefined"){try{var e=new URL(t.responseURL);return e.pathname+e.search}catch(e){fe(re().body,"htmx:badResponseUrl",{url:t.responseURL})}}}function O(e,t){return t.test(e.getAllResponseHeaders())}function Nr(e,t,r){e=e.toLowerCase();if(r){if(r instanceof Element||I(r,"String")){return he(e,t,null,null,{targetOverride:p(r),returnPromise:true})}else{return he(e,t,p(r.source),r.event,{handler:r.handler,headers:r.headers,values:r.values,targetOverride:p(r.target),swapOverride:r.swap,select:r.select,returnPromise:true})}}else{return he(e,t,null,null,{returnPromise:true})}}function Ir(e){var t=[];while(e){t.push(e);e=e.parentElement}return t}function kr(e,t,r){var n;var i;if(typeof URL==="function"){i=new URL(t,document.location.href);var a=document.location.origin;n=a===i.origin}else{i=t;n=g(t,document.location.origin)}if(Q.config.selfRequestsOnly){if(!n){return false}}return ce(e,"htmx:validateUrl",le({url:i,sameHost:n},r))}function he(t,r,n,i,a,e){var o=null;var s=null;a=a!=null?a:{};if(a.returnPromise&&typeof Promise!=="undefined"){var l=new Promise(function(e,t){o=e;s=t})}if(n==null){n=re().body}var M=a.handler||Mr;var X=a.select||null;if(!se(n)){ie(o);return l}var u=a.targetOverride||ye(n);if(u==null||u==pe){fe(n,"htmx:targetError",{target:te(n,"hx-target")});ie(s);return l}var f=ae(n);var c=f.lastButtonClicked;if(c){var h=ee(c,"formaction");if(h!=null){r=h}var v=ee(c,"formmethod");if(v!=null){if(v.toLowerCase()!=="dialog"){t=v}}}var d=ne(n,"hx-confirm");if(e===undefined){var D=function(e){return he(t,r,n,i,a,!!e)};var U={target:u,elt:n,path:r,verb:t,triggeringEvent:i,etc:a,issueRequest:D,question:d};if(ce(n,"htmx:confirm",U)===false){ie(o);return l}}var g=n;var p=ne(n,"hx-sync");var m=null;var x=false;if(p){var B=p.split(":");var F=B[0].trim();if(F==="this"){g=xe(n,"hx-sync")}else{g=ue(n,F)}p=(B[1]||"drop").trim();f=ae(g);if(p==="drop"&&f.xhr&&f.abortable!==true){ie(o);return l}else if(p==="abort"){if(f.xhr){ie(o);return l}else{x=true}}else if(p==="replace"){ce(g,"htmx:abort")}else if(p.indexOf("queue")===0){var V=p.split(" ");m=(V[1]||"last").trim()}}if(f.xhr){if(f.abortable){ce(g,"htmx:abort")}else{if(m==null){if(i){var y=ae(i);if(y&&y.triggerSpec&&y.triggerSpec.queue){m=y.triggerSpec.queue}}if(m==null){m="last"}}if(f.queuedRequests==null){f.queuedRequests=[]}if(m==="first"&&f.queuedRequests.length===0){f.queuedRequests.push(function(){he(t,r,n,i,a)})}else if(m==="all"){f.queuedRequests.push(function(){he(t,r,n,i,a)})}else if(m==="last"){f.queuedRequests=[];f.queuedRequests.push(function(){he(t,r,n,i,a)})}ie(o);return l}}var b=new XMLHttpRequest;f.xhr=b;f.abortable=x;var w=function(){f.xhr=null;f.abortable=false;if(f.queuedRequests!=null&&f.queuedRequests.length>0){var e=f.queuedRequests.shift();e()}};var j=ne(n,"hx-prompt");if(j){var S=prompt(j);if(S===null||!ce(n,"htmx:prompt",{prompt:S,target:u})){ie(o);w();return l}}if(d&&!e){if(!confirm(d)){ie(o);w();return l}}var E=xr(n,u,S);if(t!=="get"&&!Sr(n)){E["Content-Type"]="application/x-www-form-urlencoded"}if(a.headers){E=le(E,a.headers)}var _=dr(n,t);var C=_.errors;var R=_.values;if(a.values){R=le(R,a.values)}var z=Hr(n);var $=le(R,z);var T=yr($,n);if(Q.config.getCacheBusterParam&&t==="get"){T["org.htmx.cache-buster"]=ee(u,"id")||"true"}if(r==null||r===""){r=re().location.href}var O=Rr(n,"hx-request");var W=ae(n).boosted;var q=Q.config.methodsThatUseUrlParams.indexOf(t)>=0;var H={boosted:W,useUrlParams:q,parameters:T,unfilteredParameters:$,headers:E,target:u,verb:t,errors:C,withCredentials:a.credentials||O.credentials||Q.config.withCredentials,timeout:a.timeout||O.timeout||Q.config.timeout,path:r,triggeringEvent:i};if(!ce(n,"htmx:configRequest",H)){ie(o);w();return l}r=H.path;t=H.verb;E=H.headers;T=H.parameters;C=H.errors;q=H.useUrlParams;if(C&&C.length>0){ce(n,"htmx:validation:halted",H);ie(o);w();return l}var G=r.split("#");var J=G[0];var L=G[1];var A=r;if(q){A=J;var Z=Object.keys(T).length!==0;if(Z){if(A.indexOf("?")<0){A+="?"}else{A+="&"}A+=pr(T);if(L){A+="#"+L}}}if(!kr(n,A,H)){fe(n,"htmx:invalidPath",H);ie(s);return l}b.open(t.toUpperCase(),A,true);b.overrideMimeType("text/html");b.withCredentials=H.withCredentials;b.timeout=H.timeout;if(O.noHeaders){}else{for(var N in E){if(E.hasOwnProperty(N)){var K=E[N];Lr(b,N,K)}}}var I={xhr:b,target:u,requestConfig:H,etc:a,boosted:W,select:X,pathInfo:{requestPath:r,finalRequestPath:A,anchor:L}};b.onload=function(){try{var e=Ir(n);I.pathInfo.responsePath=Ar(b);M(n,I);lr(k,P);ce(n,"htmx:afterRequest",I);ce(n,"htmx:afterOnLoad",I);if(!se(n)){var t=null;while(e.length>0&&t==null){var r=e.shift();if(se(r)){t=r}}if(t){ce(t,"htmx:afterRequest",I);ce(t,"htmx:afterOnLoad",I)}}ie(o);w()}catch(e){fe(n,"htmx:onLoadError",le({error:e},I));throw e}};b.onerror=function(){lr(k,P);fe(n,"htmx:afterRequest",I);fe(n,"htmx:sendError",I);ie(s);w()};b.onabort=function(){lr(k,P);fe(n,"htmx:afterRequest",I);fe(n,"htmx:sendAbort",I);ie(s);w()};b.ontimeout=function(){lr(k,P);fe(n,"htmx:afterRequest",I);fe(n,"htmx:timeout",I);ie(s);w()};if(!ce(n,"htmx:beforeRequest",I)){ie(o);w();return l}var k=or(n);var P=sr(n);oe(["loadstart","loadend","progress","abort"],function(t){oe([b,b.upload],function(e){e.addEventListener(t,function(e){ce(n,"htmx:xhr:"+t,{lengthComputable:e.lengthComputable,loaded:e.loaded,total:e.total})})})});ce(n,"htmx:beforeSend",I);var Y=q?null:Er(b,n,T);b.send(Y);return l}function Pr(e,t){var r=t.xhr;var n=null;var i=null;if(O(r,/HX-Push:/i)){n=r.getResponseHeader("HX-Push");i="push"}else if(O(r,/HX-Push-Url:/i)){n=r.getResponseHeader("HX-Push-Url");i="push"}else if(O(r,/HX-Replace-Url:/i)){n=r.getResponseHeader("HX-Replace-Url");i="replace"}if(n){if(n==="false"){return{}}else{return{type:i,path:n}}}var a=t.pathInfo.finalRequestPath;var o=t.pathInfo.responsePath;var s=ne(e,"hx-push-url");var l=ne(e,"hx-replace-url");var u=ae(e).boosted;var f=null;var c=null;if(s){f="push";c=s}else if(l){f="replace";c=l}else if(u){f="push";c=o||a}if(c){if(c==="false"){return{}}if(c==="true"){c=o||a}if(t.pathInfo.anchor&&c.indexOf("#")===-1){c=c+"#"+t.pathInfo.anchor}return{type:f,path:c}}else{return{}}}function Mr(l,u){var f=u.xhr;var c=u.target;var e=u.etc;var t=u.requestConfig;var h=u.select;if(!ce(l,"htmx:beforeOnLoad",u))return;if(O(f,/HX-Trigger:/i)){_e(f,"HX-Trigger",l)}if(O(f,/HX-Location:/i)){er();var r=f.getResponseHeader("HX-Location");var v;if(r.indexOf("{")===0){v=E(r);r=v["path"];delete v["path"]}Nr("GET",r,v).then(function(){tr(r)});return}var n=O(f,/HX-Refresh:/i)&&"true"===f.getResponseHeader("HX-Refresh");if(O(f,/HX-Redirect:/i)){location.href=f.getResponseHeader("HX-Redirect");n&&location.reload();return}if(n){location.reload();return}if(O(f,/HX-Retarget:/i)){if(f.getResponseHeader("HX-Retarget")==="this"){u.target=l}else{u.target=ue(l,f.getResponseHeader("HX-Retarget"))}}var d=Pr(l,u);var i=f.status>=200&&f.status<400&&f.status!==204;var g=f.response;var a=f.status>=400;var p=Q.config.ignoreTitle;var o=le({shouldSwap:i,serverResponse:g,isError:a,ignoreTitle:p},u);if(!ce(c,"htmx:beforeSwap",o))return;c=o.target;g=o.serverResponse;a=o.isError;p=o.ignoreTitle;u.target=c;u.failed=a;u.successful=!a;if(o.shouldSwap){if(f.status===286){at(l)}R(l,function(e){g=e.transformResponse(g,f,l)});if(d.type){er()}var s=e.swapOverride;if(O(f,/HX-Reswap:/i)){s=f.getResponseHeader("HX-Reswap")}var v=wr(l,s);if(v.hasOwnProperty("ignoreTitle")){p=v.ignoreTitle}c.classList.add(Q.config.swappingClass);var m=null;var x=null;var y=function(){try{var e=document.activeElement;var t={};try{t={elt:e,start:e?e.selectionStart:null,end:e?e.selectionEnd:null}}catch(e){}var r;if(h){r=h}if(O(f,/HX-Reselect:/i)){r=f.getResponseHeader("HX-Reselect")}if(d.type){ce(re().body,"htmx:beforeHistoryUpdate",le({history:d},u));if(d.type==="push"){tr(d.path);ce(re().body,"htmx:pushedIntoHistory",{path:d.path})}else{rr(d.path);ce(re().body,"htmx:replacedInHistory",{path:d.path})}}var n=T(c);je(v.swapStyle,c,l,g,n,r);if(t.elt&&!se(t.elt)&&ee(t.elt,"id")){var i=document.getElementById(ee(t.elt,"id"));var a={preventScroll:v.focusScroll!==undefined?!v.focusScroll:!Q.config.defaultFocusScroll};if(i){if(t.start&&i.setSelectionRange){try{i.setSelectionRange(t.start,t.end)}catch(e){}}i.focus(a)}}c.classList.remove(Q.config.swappingClass);oe(n.elts,function(e){if(e.classList){e.classList.add(Q.config.settlingClass)}ce(e,"htmx:afterSwap",u)});if(O(f,/HX-Trigger-After-Swap:/i)){var o=l;if(!se(l)){o=re().body}_e(f,"HX-Trigger-After-Swap",o)}var s=function(){oe(n.tasks,function(e){e.call()});oe(n.elts,function(e){if(e.classList){e.classList.remove(Q.config.settlingClass)}ce(e,"htmx:afterSettle",u)});if(u.pathInfo.anchor){var e=re().getElementById(u.pathInfo.anchor);if(e){e.scrollIntoView({block:"start",behavior:"auto"})}}if(n.title&&!p){var t=C("title");if(t){t.innerHTML=n.title}else{window.document.title=n.title}}Cr(n.elts,v);if(O(f,/HX-Trigger-After-Settle:/i)){var r=l;if(!se(l)){r=re().body}_e(f,"HX-Trigger-After-Settle",r)}ie(m)};if(v.settleDelay>0){setTimeout(s,v.settleDelay)}else{s()}}catch(e){fe(l,"htmx:swapError",u);ie(x);throw e}};var b=Q.config.globalViewTransitions;if(v.hasOwnProperty("transition")){b=v.transition}if(b&&ce(l,"htmx:beforeTransition",u)&&typeof Promise!=="undefined"&&document.startViewTransition){var w=new Promise(function(e,t){m=e;x=t});var S=y;y=function(){document.startViewTransition(function(){S();return w})}}if(v.swapDelay>0){setTimeout(y,v.swapDelay)}else{y()}}if(a){fe(l,"htmx:responseError",le({error:"Response Status Error Code "+f.status+" from "+u.pathInfo.requestPath},u))}}var Xr={};function Dr(){return{init:function(e){return null},onEvent:function(e,t){return true},transformResponse:function(e,t,r){return e},isInlineSwap:function(e){return false},handleSwap:function(e,t,r,n){return false},encodeParameters:function(e,t,r){return null}}}function Ur(e,t){if(t.init){t.init(r)}Xr[e]=le(Dr(),t)}function Br(e){delete Xr[e]}function Fr(e,r,n){if(e==undefined){return r}if(r==undefined){r=[]}if(n==undefined){n=[]}var t=te(e,"hx-ext");if(t){oe(t.split(","),function(e){e=e.replace(/ /g,"");if(e.slice(0,7)=="ignore:"){n.push(e.slice(7));return}if(n.indexOf(e)<0){var t=Xr[e];if(t&&r.indexOf(t)<0){r.push(t)}}})}return Fr(u(e),r,n)}var Vr=false;re().addEventListener("DOMContentLoaded",function(){Vr=true});function jr(e){if(Vr||re().readyState==="complete"){e()}else{re().addEventListener("DOMContentLoaded",e)}}function _r(){if(Q.config.includeIndicatorStyles!==false){re().head.insertAdjacentHTML("beforeend","<style>                      ."+Q.config.indicatorClass+"{opacity:0}                      ."+Q.config.requestClass+" ."+Q.config.indicatorClass+"{opacity:1; transition: opacity 200ms ease-in;}                      ."+Q.config.requestClass+"."+Q.config.indicatorClass+"{opacity:1; transition: opacity 200ms ease-in;}                    </style>")}}function zr(){var e=re().querySelector('meta[name="htmx-config"]');if(e){return E(e.content)}else{return null}}function $r(){var e=zr();if(e){Q.config=le(Q.config,e)}}jr(function(){$r();_r();var e=re().body;zt(e);var t=re().querySelectorAll("[hx-trigger='restored'],[data-hx-trigger='restored']");e.addEventListener("htmx:abort",function(e){var t=e.target;var r=ae(t);if(r&&r.xhr){r.xhr.abort()}});const r=window.onpopstate?window.onpopstate.bind(window):null;window.onpopstate=function(e){if(e.state&&e.state.htmx){ar();oe(t,function(e){ce(e,"htmx:restored",{document:re(),triggerEvent:ce})})}else{if(r){r(e)}}};setTimeout(function(){ce(e,"htmx:load",{});e=null},0)});return Q}()});
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt einen Teil der Implementierung um.

## app/static/security.js
```javascript
function getCookie(name) {
  const parts = document.cookie ? document.cookie.split("; ") : [];
  for (const part of parts) {
    const splitIndex = part.indexOf("=");
    if (splitIndex === -1) {
      continue;
    }
    const key = decodeURIComponent(part.slice(0, splitIndex));
    if (key === name) {
      return decodeURIComponent(part.slice(splitIndex + 1));
    }
  }
  return "";
}

function addCsrfInput(form, token) {
  if (!token) {
    return;
  }
  const method = (form.getAttribute("method") || "get").toUpperCase();
  if (!["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    return;
  }
  let csrfInput = form.querySelector('input[name="csrf_token"]');
  if (!csrfInput) {
    csrfInput = document.createElement("input");
    csrfInput.type = "hidden";
    csrfInput.name = "csrf_token";
    form.appendChild(csrfInput);
  }
  csrfInput.value = token;
}

function injectCsrfIntoForms() {
  const token = getCookie("csrf_token");
  document.querySelectorAll("form").forEach((form) => addCsrfInput(form, token));
}

document.addEventListener("DOMContentLoaded", injectCsrfIntoForms);

document.addEventListener(
  "submit",
  (event) => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) {
      return;
    }
    addCsrfInput(form, getCookie("csrf_token"));
  },
  true
);

document.body.addEventListener("htmx:configRequest", (event) => {
  const token = getCookie("csrf_token");
  if (!token) {
    return;
  }
  event.detail.headers["X-CSRF-Token"] = token;
});
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt einen Teil der Implementierung um.
2. Diese Zeile setzt einen Teil der Implementierung um.
3. Diese Zeile startet eine Schleife.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile steuert einen bedingten Ablauf.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile steuert einen bedingten Ablauf.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile ist bewusst leer.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile steuert einen bedingten Ablauf.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile steuert einen bedingten Ablauf.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile steuert einen bedingten Ablauf.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile ist bewusst leer.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile ist bewusst leer.
39. Diese Zeile setzt einen Teil der Implementierung um.
40. Diese Zeile ist bewusst leer.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile steuert einen bedingten Ablauf.
46. Diese Zeile setzt einen Teil der Implementierung um.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile setzt einen Teil der Implementierung um.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile setzt einen Teil der Implementierung um.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile ist bewusst leer.
53. Diese Zeile setzt einen Teil der Implementierung um.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile steuert einen bedingten Ablauf.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.

## app/templates/base.html
```html
<!doctype html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="csrf-token" content="{{ csrf_token or '' }}">
  <title>{{ title or "MealMate" }}</title>
  <link rel="stylesheet" href="/static/style.css">
  <script src="/static/htmx.min.js"></script>
  <script src="/static/security.js" defer></script>
</head>
<body>
  <header class="topbar">
    <a href="/" class="brand">MealMate</a>
    <nav>
      <a href="/">Discover</a>
      {% if current_user %}
      <a href="/recipes/new">Create Recipe</a>
      <a href="/my-recipes">My Recipes</a>
      <a href="/favorites">Favorites</a>
      <a href="/me">Me</a>
      {% if current_user.role == "admin" %}
      <a href="/admin">Admin</a>
      {% endif %}
      <form method="post" action="/logout" class="inline">
        <button type="submit">Logout</button>
      </form>
      {% else %}
      <a href="/login">Login</a>
      <a href="/register">Register</a>
      {% endif %}
    </nav>
  </header>
  <main class="container">
    {% block content %}{% endblock %}
  </main>
</body>
</html>
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt einen Teil der Implementierung um.
2. Diese Zeile setzt einen Teil der Implementierung um.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile setzt einen Teil der Implementierung um.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile setzt einen Teil der Implementierung um.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile enthaelt Jinja-Template-Logik.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile setzt einen Teil der Implementierung um.
22. Diese Zeile enthaelt Jinja-Template-Logik.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile enthaelt Jinja-Template-Logik.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile enthaelt Jinja-Template-Logik.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile enthaelt Jinja-Template-Logik.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile enthaelt Jinja-Template-Logik.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.

## app/templates/admin.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>Admin Panel</h1>
  {% if message %}
  <p class="meta">{{ message }}</p>
  {% endif %}
  {% if error %}
  <p class="error">{{ error }}</p>
  {% endif %}
</section>
<section class="panel">
  <h2>KochWiki Seed (einmalig)</h2>
  <p class="meta">CSV Pfad: {{ default_csv_path }}</p>
  {% if seed_done %}
  <p class="meta">Seed-Status: bereits ausgefuehrt.</p>
  {% else %}
  <form method="post" action="/admin/run-kochwiki-seed">
    <button type="submit">Einmaligen KochWiki-Seed ausfuehren</button>
  </form>
  {% endif %}
</section>
<section class="panel">
  <h2>CSV manuell importieren</h2>
  <form method="post" action="/admin/import-recipes" enctype="multipart/form-data" class="stack">
    <label>CSV Upload
      <input type="file" name="file" accept=".csv" required>
    </label>
    <label class="inline">
      <input type="checkbox" name="insert_only" checked>
      Nur neue hinzufuegen (UPSERT SAFE)
    </label>
    <label class="inline">
      <input type="checkbox" name="update_existing">
      Existierende aktualisieren (Warnung: nur ausgewaehlte Felder!)
    </label>
    <button type="submit">Start Import</button>
  </form>
  {% if report %}
  <p class="meta">
    Inserted: {{ report.inserted }},
    Updated: {{ report.updated }},
    Skipped: {{ report.skipped }},
    Errors: {{ report.errors|length }}
  </p>
  {% if report.errors %}
  <ul>
    {% for item in report.errors %}
    <li>{{ item }}</li>
    {% endfor %}
  </ul>
  {% endif %}
  {% endif %}
</section>
<section class="panel">
  <h2>Users</h2>
  <table>
    <thead>
      <tr><th>ID</th><th>Email</th><th>Role</th><th>Action</th></tr>
    </thead>
    <tbody>
      {% for user in users %}
      <tr>
        <td>{{ user.id }}</td>
        <td>{{ user.email }}</td>
        <td>{{ user.role }}</td>
        <td>
          <form method="post" action="/admin/users/{{ user.id }}/role" class="inline">
            <select name="role">
              <option value="user" {% if user.role == "user" %}selected{% endif %}>user</option>
              <option value="admin" {% if user.role == "admin" %}selected{% endif %}>admin</option>
            </select>
            <button type="submit">Save</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
<section class="panel">
  <h2>Recipes</h2>
  <table>
    <thead>
      <tr><th>ID</th><th>Title</th><th>Creator</th><th>Source</th><th>Action</th></tr>
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
            <button type="submit">Delete</button>
          </form>
        </td>
      </tr>
      {% endfor %}
    </tbody>
  </table>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile enthaelt Jinja-Template-Logik.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile enthaelt Jinja-Template-Logik.
8. Diese Zeile enthaelt Jinja-Template-Logik.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile enthaelt Jinja-Template-Logik.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile setzt einen Teil der Implementierung um.
13. Diese Zeile setzt einen Teil der Implementierung um.
14. Diese Zeile setzt einen Teil der Implementierung um.
15. Diese Zeile enthaelt Jinja-Template-Logik.
16. Diese Zeile setzt einen Teil der Implementierung um.
17. Diese Zeile enthaelt Jinja-Template-Logik.
18. Diese Zeile setzt einen Teil der Implementierung um.
19. Diese Zeile setzt einen Teil der Implementierung um.
20. Diese Zeile setzt einen Teil der Implementierung um.
21. Diese Zeile enthaelt Jinja-Template-Logik.
22. Diese Zeile setzt einen Teil der Implementierung um.
23. Diese Zeile setzt einen Teil der Implementierung um.
24. Diese Zeile setzt einen Teil der Implementierung um.
25. Diese Zeile setzt einen Teil der Implementierung um.
26. Diese Zeile setzt einen Teil der Implementierung um.
27. Diese Zeile setzt einen Teil der Implementierung um.
28. Diese Zeile setzt einen Teil der Implementierung um.
29. Diese Zeile setzt einen Teil der Implementierung um.
30. Diese Zeile setzt einen Teil der Implementierung um.
31. Diese Zeile setzt einen Teil der Implementierung um.
32. Diese Zeile setzt einen Teil der Implementierung um.
33. Diese Zeile setzt einen Teil der Implementierung um.
34. Diese Zeile setzt einen Teil der Implementierung um.
35. Diese Zeile setzt einen Teil der Implementierung um.
36. Diese Zeile setzt einen Teil der Implementierung um.
37. Diese Zeile setzt einen Teil der Implementierung um.
38. Diese Zeile setzt einen Teil der Implementierung um.
39. Diese Zeile enthaelt Jinja-Template-Logik.
40. Diese Zeile setzt einen Teil der Implementierung um.
41. Diese Zeile setzt einen Teil der Implementierung um.
42. Diese Zeile setzt einen Teil der Implementierung um.
43. Diese Zeile setzt einen Teil der Implementierung um.
44. Diese Zeile setzt einen Teil der Implementierung um.
45. Diese Zeile setzt einen Teil der Implementierung um.
46. Diese Zeile enthaelt Jinja-Template-Logik.
47. Diese Zeile setzt einen Teil der Implementierung um.
48. Diese Zeile enthaelt Jinja-Template-Logik.
49. Diese Zeile setzt einen Teil der Implementierung um.
50. Diese Zeile enthaelt Jinja-Template-Logik.
51. Diese Zeile setzt einen Teil der Implementierung um.
52. Diese Zeile enthaelt Jinja-Template-Logik.
53. Diese Zeile enthaelt Jinja-Template-Logik.
54. Diese Zeile setzt einen Teil der Implementierung um.
55. Diese Zeile setzt einen Teil der Implementierung um.
56. Diese Zeile setzt einen Teil der Implementierung um.
57. Diese Zeile setzt einen Teil der Implementierung um.
58. Diese Zeile setzt einen Teil der Implementierung um.
59. Diese Zeile setzt einen Teil der Implementierung um.
60. Diese Zeile setzt einen Teil der Implementierung um.
61. Diese Zeile setzt einen Teil der Implementierung um.
62. Diese Zeile enthaelt Jinja-Template-Logik.
63. Diese Zeile setzt einen Teil der Implementierung um.
64. Diese Zeile setzt einen Teil der Implementierung um.
65. Diese Zeile setzt einen Teil der Implementierung um.
66. Diese Zeile setzt einen Teil der Implementierung um.
67. Diese Zeile setzt einen Teil der Implementierung um.
68. Diese Zeile setzt einen Teil der Implementierung um.
69. Diese Zeile setzt einen Teil der Implementierung um.
70. Diese Zeile setzt einen Teil der Implementierung um.
71. Diese Zeile setzt einen Teil der Implementierung um.
72. Diese Zeile setzt einen Teil der Implementierung um.
73. Diese Zeile setzt einen Teil der Implementierung um.
74. Diese Zeile setzt einen Teil der Implementierung um.
75. Diese Zeile setzt einen Teil der Implementierung um.
76. Diese Zeile setzt einen Teil der Implementierung um.
77. Diese Zeile enthaelt Jinja-Template-Logik.
78. Diese Zeile setzt einen Teil der Implementierung um.
79. Diese Zeile setzt einen Teil der Implementierung um.
80. Diese Zeile setzt einen Teil der Implementierung um.
81. Diese Zeile setzt einen Teil der Implementierung um.
82. Diese Zeile setzt einen Teil der Implementierung um.
83. Diese Zeile setzt einen Teil der Implementierung um.
84. Diese Zeile setzt einen Teil der Implementierung um.
85. Diese Zeile setzt einen Teil der Implementierung um.
86. Diese Zeile setzt einen Teil der Implementierung um.
87. Diese Zeile setzt einen Teil der Implementierung um.
88. Diese Zeile enthaelt Jinja-Template-Logik.
89. Diese Zeile setzt einen Teil der Implementierung um.
90. Diese Zeile setzt einen Teil der Implementierung um.
91. Diese Zeile setzt einen Teil der Implementierung um.
92. Diese Zeile setzt einen Teil der Implementierung um.
93. Diese Zeile setzt einen Teil der Implementierung um.
94. Diese Zeile setzt einen Teil der Implementierung um.
95. Diese Zeile setzt einen Teil der Implementierung um.
96. Diese Zeile setzt einen Teil der Implementierung um.
97. Diese Zeile setzt einen Teil der Implementierung um.
98. Diese Zeile setzt einen Teil der Implementierung um.
99. Diese Zeile setzt einen Teil der Implementierung um.
100. Diese Zeile enthaelt Jinja-Template-Logik.
101. Diese Zeile setzt einen Teil der Implementierung um.
102. Diese Zeile setzt einen Teil der Implementierung um.
103. Diese Zeile setzt einen Teil der Implementierung um.
104. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/error_404.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>404 - Seite nicht gefunden</h1>
  <p>Die angeforderte Seite existiert nicht oder wurde verschoben.</p>
  <p><a href="/">Zur Startseite</a></p>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile setzt einen Teil der Implementierung um.
8. Diese Zeile enthaelt Jinja-Template-Logik.

## app/templates/error_500.html
```html
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>500 - Interner Fehler</h1>
  <p>Beim Verarbeiten der Anfrage ist ein unerwarteter Fehler aufgetreten.</p>
  <p><a href="/">Zur Startseite</a></p>
  {% if show_trace and error_trace %}
  <h2>Stacktrace (nur Dev)</h2>
  <pre>{{ error_trace }}</pre>
  {% endif %}
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile enthaelt Jinja-Template-Logik.
2. Diese Zeile enthaelt Jinja-Template-Logik.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile setzt einen Teil der Implementierung um.
5. Diese Zeile setzt einen Teil der Implementierung um.
6. Diese Zeile setzt einen Teil der Implementierung um.
7. Diese Zeile enthaelt Jinja-Template-Logik.
8. Diese Zeile setzt einen Teil der Implementierung um.
9. Diese Zeile setzt einen Teil der Implementierung um.
10. Diese Zeile enthaelt Jinja-Template-Logik.
11. Diese Zeile setzt einen Teil der Implementierung um.
12. Diese Zeile enthaelt Jinja-Template-Logik.

## README_SECURITY.md
```markdown
# MealMate Security Checklist

Diese Checkliste hilft beim manuellen Test der Production-Sicherheitsfunktionen.

## 1) Login Rate Limit

1. Sende 6 Login-POSTs innerhalb von 1 Minute an `/login`.
2. Erwartung: Die ersten 5 Requests werden normal verarbeitet.
3. Erwartung: Der 6. Request liefert `429 Too Many Requests`.
4. Erwartung: Response enthaelt Rate-Limit Header (z. B. `X-RateLimit-*`).

## 2) Register Rate Limit

1. Sende 4 Register-POSTs innerhalb von 1 Minute an `/register`.
2. Erwartung: Nach 3 Requests greift der Limiter.
3. Erwartung: Der 4. Request liefert `429`.

## 3) CSRF Schutz ohne Token

1. Oeffne eine geschuetzte POST-Route ohne `csrf_token` Feld oder `X-CSRF-Token` Header.
2. Beispiel: `curl -X POST http://localhost:8000/logout`.
3. Erwartung: Response `403` mit Hinweis auf fehlgeschlagene CSRF-Validierung.

## 4) CSRF Schutz mit Token

1. Lade zuerst eine GET-Seite, damit `csrf_token` Cookie gesetzt wird.
2. Sende dann POST mit passendem Header `X-CSRF-Token: <cookie-wert>`.
3. Erwartung: Request wird normal akzeptiert (`200` oder Redirect `303`).

## 5) Security Headers

1. Fuehre `curl -I http://localhost:8000/` aus.
2. Erwartung: Header enthalten mindestens:
3. `Content-Security-Policy`
4. `X-Content-Type-Options: nosniff`
5. `X-Frame-Options: DENY`
6. `Referrer-Policy: strict-origin-when-cross-origin`
7. `Permissions-Policy: geolocation=(), microphone=(), camera=()`
8. In Prod/HTTPS zusaetzlich `Strict-Transport-Security`.

## 6) Bild-Upload Hardening

1. Lade eine Datei mit falschem MIME-Typ hoch.
2. Erwartung: `400 Bad Request`.
3. Lade ein Bild groesser als `MAX_UPLOAD_MB` hoch.
4. Erwartung: `413 Request Entity Too Large` oder klarer Fehler.
5. Lade ein Bild mit passendem MIME aber falschen Magic Bytes hoch.
6. Erwartung: `400 Bad Request`.

## 7) CSV Upload Hardening (Admin)

1. Lade eine CSV groesser als `MAX_CSV_UPLOAD_MB` hoch.
2. Erwartung: `413 Request Entity Too Large`.
3. Lade eine Datei ohne `.csv` Endung hoch.
4. Erwartung: `400 Bad Request`.
5. Pruefe, dass kein freier Dateipfad im Request verarbeitet wird.

## 8) Allowed Hosts

1. Setze in ENV `ALLOWED_HOSTS` auf eine feste Domain.
2. Sende einen Request mit falschem Host Header.
3. Erwartung: `400 Bad Request` durch TrustedHostMiddleware.

## 9) Request ID

1. Fuehre einen normalen Request auf `/` aus.
2. Erwartung: Response enthaelt Header `X-Request-ID`.
3. Pruefe Logs: dieselbe `request_id` ist im Request-Log sichtbar.
```
ZEILEN-ERKL?RUNG
1. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
2. Diese Zeile ist bewusst leer.
3. Diese Zeile setzt einen Teil der Implementierung um.
4. Diese Zeile ist bewusst leer.
5. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
6. Diese Zeile ist bewusst leer.
7. Diese Zeile beschreibt einen Punkt der Anleitung.
8. Diese Zeile beschreibt einen Punkt der Anleitung.
9. Diese Zeile beschreibt einen Punkt der Anleitung.
10. Diese Zeile beschreibt einen Punkt der Anleitung.
11. Diese Zeile ist bewusst leer.
12. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
13. Diese Zeile ist bewusst leer.
14. Diese Zeile beschreibt einen Punkt der Anleitung.
15. Diese Zeile beschreibt einen Punkt der Anleitung.
16. Diese Zeile beschreibt einen Punkt der Anleitung.
17. Diese Zeile ist bewusst leer.
18. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
19. Diese Zeile ist bewusst leer.
20. Diese Zeile beschreibt einen Punkt der Anleitung.
21. Diese Zeile beschreibt einen Punkt der Anleitung.
22. Diese Zeile beschreibt einen Punkt der Anleitung.
23. Diese Zeile ist bewusst leer.
24. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
25. Diese Zeile ist bewusst leer.
26. Diese Zeile beschreibt einen Punkt der Anleitung.
27. Diese Zeile beschreibt einen Punkt der Anleitung.
28. Diese Zeile beschreibt einen Punkt der Anleitung.
29. Diese Zeile ist bewusst leer.
30. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
31. Diese Zeile ist bewusst leer.
32. Diese Zeile beschreibt einen Punkt der Anleitung.
33. Diese Zeile beschreibt einen Punkt der Anleitung.
34. Diese Zeile beschreibt einen Punkt der Anleitung.
35. Diese Zeile beschreibt einen Punkt der Anleitung.
36. Diese Zeile beschreibt einen Punkt der Anleitung.
37. Diese Zeile beschreibt einen Punkt der Anleitung.
38. Diese Zeile beschreibt einen Punkt der Anleitung.
39. Diese Zeile beschreibt einen Punkt der Anleitung.
40. Diese Zeile ist bewusst leer.
41. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
42. Diese Zeile ist bewusst leer.
43. Diese Zeile beschreibt einen Punkt der Anleitung.
44. Diese Zeile beschreibt einen Punkt der Anleitung.
45. Diese Zeile beschreibt einen Punkt der Anleitung.
46. Diese Zeile beschreibt einen Punkt der Anleitung.
47. Diese Zeile beschreibt einen Punkt der Anleitung.
48. Diese Zeile beschreibt einen Punkt der Anleitung.
49. Diese Zeile ist bewusst leer.
50. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
51. Diese Zeile ist bewusst leer.
52. Diese Zeile beschreibt einen Punkt der Anleitung.
53. Diese Zeile beschreibt einen Punkt der Anleitung.
54. Diese Zeile beschreibt einen Punkt der Anleitung.
55. Diese Zeile beschreibt einen Punkt der Anleitung.
56. Diese Zeile beschreibt einen Punkt der Anleitung.
57. Diese Zeile ist bewusst leer.
58. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
59. Diese Zeile ist bewusst leer.
60. Diese Zeile beschreibt einen Punkt der Anleitung.
61. Diese Zeile beschreibt einen Punkt der Anleitung.
62. Diese Zeile beschreibt einen Punkt der Anleitung.
63. Diese Zeile ist bewusst leer.
64. Diese Zeile ist eine Ueberschrift oder ein Kommentar.
65. Diese Zeile ist bewusst leer.
66. Diese Zeile beschreibt einen Punkt der Anleitung.
67. Diese Zeile beschreibt einen Punkt der Anleitung.
68. Diese Zeile beschreibt einen Punkt der Anleitung.

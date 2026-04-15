# Projektstruktur
```text
.
|-- .env.example
|-- .dockerignore
|-- Dockerfile
|-- docker-compose.yml
|-- start.sh
|-- requirements.txt
|-- README_DEPLOY.md
|-- render.yaml
`-- app/
    |-- config.py
    |-- database.py
    |-- main.py
    `-- routers/
        `-- auth.py
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
MAX_UPLOAD_MB=4
ALLOWED_IMAGE_TYPES=image/png,image/jpeg,image/webp
AUTO_SEED_KOCHWIKI=0
KOCHWIKI_CSV_PATH=rezepte_kochwiki_clean_3713.csv
IMPORT_DOWNLOAD_IMAGES=0
SEED_ADMIN_EMAIL=admin@mealmate.local
SEED_ADMIN_PASSWORD=AdminPass123!
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt einen konkreten Teil der Implementierung um.
2. Diese Zeile setzt einen konkreten Teil der Implementierung um.
3. Diese Zeile setzt eine Konfiguration oder Zuordnung.
4. Diese Zeile setzt einen konkreten Teil der Implementierung um.
5. Diese Zeile setzt einen konkreten Teil der Implementierung um.
6. Diese Zeile setzt einen konkreten Teil der Implementierung um.
7. Diese Zeile ist ein Kommentar oder eine Markdown-Ueberschrift.
8. Diese Zeile setzt eine Konfiguration oder Zuordnung.
9. Diese Zeile setzt einen konkreten Teil der Implementierung um.
10. Diese Zeile setzt einen konkreten Teil der Implementierung um.
11. Diese Zeile setzt einen konkreten Teil der Implementierung um.
12. Diese Zeile setzt einen konkreten Teil der Implementierung um.
13. Diese Zeile setzt einen konkreten Teil der Implementierung um.
14. Diese Zeile setzt einen konkreten Teil der Implementierung um.
15. Diese Zeile setzt einen konkreten Teil der Implementierung um.
16. Diese Zeile setzt einen konkreten Teil der Implementierung um.
17. Diese Zeile setzt einen konkreten Teil der Implementierung um.

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
    max_upload_mb: int = 4
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


@lru_cache
def get_settings() -> Settings:
    return Settings()
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Funktionen oder Klassen.
2. Diese Zeile importiert benoetigte Funktionen oder Klassen.
3. Diese Zeile ist absichtlich leer.
4. Diese Zeile importiert benoetigte Funktionen oder Klassen.
5. Diese Zeile importiert benoetigte Funktionen oder Klassen.
6. Diese Zeile ist absichtlich leer.
7. Diese Zeile ist absichtlich leer.
8. Diese Zeile startet eine Klassendefinition.
9. Diese Zeile setzt einen konkreten Teil der Implementierung um.
10. Diese Zeile ist absichtlich leer.
11. Diese Zeile setzt eine Konfiguration oder Zuordnung.
12. Diese Zeile setzt eine Konfiguration oder Zuordnung.
13. Diese Zeile setzt eine Konfiguration oder Zuordnung.
14. Diese Zeile setzt eine Konfiguration oder Zuordnung.
15. Diese Zeile setzt eine Konfiguration oder Zuordnung.
16. Diese Zeile setzt eine Konfiguration oder Zuordnung.
17. Diese Zeile setzt eine Konfiguration oder Zuordnung.
18. Diese Zeile setzt eine Konfiguration oder Zuordnung.
19. Diese Zeile setzt eine Konfiguration oder Zuordnung.
20. Diese Zeile setzt eine Konfiguration oder Zuordnung.
21. Diese Zeile setzt eine Konfiguration oder Zuordnung.
22. Diese Zeile setzt eine Konfiguration oder Zuordnung.
23. Diese Zeile setzt eine Konfiguration oder Zuordnung.
24. Diese Zeile setzt eine Konfiguration oder Zuordnung.
25. Diese Zeile setzt eine Konfiguration oder Zuordnung.
26. Diese Zeile setzt eine Konfiguration oder Zuordnung.
27. Diese Zeile ist absichtlich leer.
28. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
29. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
30. Diese Zeile startet eine Funktionsdefinition.
31. Diese Zeile steuert eine Bedingung im Ablauf.
32. Diese Zeile gibt einen Rueckgabewert zurueck.
33. Diese Zeile gibt einen Rueckgabewert zurueck.
34. Diese Zeile ist absichtlich leer.
35. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
36. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
37. Diese Zeile startet eine Funktionsdefinition.
38. Diese Zeile steuert eine Bedingung im Ablauf.
39. Diese Zeile setzt einen konkreten Teil der Implementierung um.
40. Diese Zeile steuert eine Bedingung im Ablauf.
41. Diese Zeile setzt einen konkreten Teil der Implementierung um.
42. Diese Zeile gibt einen Rueckgabewert zurueck.
43. Diese Zeile ist absichtlich leer.
44. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
45. Diese Zeile startet eine Funktionsdefinition.
46. Diese Zeile setzt einen konkreten Teil der Implementierung um.
47. Diese Zeile steuert eine Bedingung im Ablauf.
48. Diese Zeile gibt einen Rueckgabewert zurueck.
49. Diese Zeile steuert eine Bedingung im Ablauf.
50. Diese Zeile gibt einen Rueckgabewert zurueck.
51. Diese Zeile gibt einen Rueckgabewert zurueck.
52. Diese Zeile ist absichtlich leer.
53. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
54. Diese Zeile startet eine Funktionsdefinition.
55. Diese Zeile gibt einen Rueckgabewert zurueck.
56. Diese Zeile ist absichtlich leer.
57. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
58. Diese Zeile startet eine Funktionsdefinition.
59. Diese Zeile gibt einen Rueckgabewert zurueck.
60. Diese Zeile ist absichtlich leer.
61. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
62. Diese Zeile startet eine Funktionsdefinition.
63. Diese Zeile steuert eine Bedingung im Ablauf.
64. Diese Zeile gibt einen Rueckgabewert zurueck.
65. Diese Zeile gibt einen Rueckgabewert zurueck.
66. Diese Zeile ist absichtlich leer.
67. Diese Zeile ist absichtlich leer.
68. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
69. Diese Zeile startet eine Funktionsdefinition.
70. Diese Zeile gibt einen Rueckgabewert zurueck.

## app/database.py
```python
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

connect_args = {"check_same_thread": False} if settings.is_sqlite else {}
engine = create_engine(
    settings.sqlalchemy_database_url,
    echo=False,
    connect_args=connect_args,
    pool_pre_ping=not settings.is_sqlite,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert benoetigte Funktionen oder Klassen.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile importiert benoetigte Funktionen oder Klassen.
4. Diese Zeile importiert benoetigte Funktionen oder Klassen.
5. Diese Zeile ist absichtlich leer.
6. Diese Zeile importiert benoetigte Funktionen oder Klassen.
7. Diese Zeile ist absichtlich leer.
8. Diese Zeile setzt einen konkreten Teil der Implementierung um.
9. Diese Zeile ist absichtlich leer.
10. Diese Zeile setzt eine Konfiguration oder Zuordnung.
11. Diese Zeile setzt einen konkreten Teil der Implementierung um.
12. Diese Zeile setzt einen konkreten Teil der Implementierung um.
13. Diese Zeile setzt einen konkreten Teil der Implementierung um.
14. Diese Zeile setzt einen konkreten Teil der Implementierung um.
15. Diese Zeile setzt einen konkreten Teil der Implementierung um.
16. Diese Zeile setzt einen konkreten Teil der Implementierung um.
17. Diese Zeile setzt einen konkreten Teil der Implementierung um.
18. Diese Zeile ist absichtlich leer.
19. Diese Zeile ist absichtlich leer.
20. Diese Zeile startet eine Klassendefinition.
21. Diese Zeile setzt einen konkreten Teil der Implementierung um.
22. Diese Zeile ist absichtlich leer.
23. Diese Zeile ist absichtlich leer.
24. Diese Zeile startet eine Funktionsdefinition.
25. Diese Zeile setzt einen konkreten Teil der Implementierung um.
26. Diese Zeile gehoert zur Fehlerbehandlung.
27. Diese Zeile setzt einen konkreten Teil der Implementierung um.
28. Diese Zeile gehoert zur Fehlerbehandlung.
29. Diese Zeile setzt einen konkreten Teil der Implementierung um.

## app/main.py
```python
from pathlib import Path

from fastapi import FastAPI
from starlette.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import func, select
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.config import get_settings
from app.database import SessionLocal
from app.models import Recipe, User
from app.routers import admin, auth, recipes
from app.security import hash_password
from app.services import import_kochwiki_csv, is_meta_true, set_meta_value

settings = get_settings()

app = FastAPI(title=settings.app_name, version="1.0.0")


class CacheControlStaticFiles(StaticFiles):
    def __init__(self, *args, cache_control: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_control = cache_control

    async def get_response(self, path: str, scope):
        response = await super().get_response(path, scope)
        if self.cache_control and response.status_code == 200:
            response.headers.setdefault("Cache-Control", self.cache_control)
        return response


if settings.prod_mode:
    app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")
if settings.allowed_hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)

static_dir = Path("app/static")
static_dir.mkdir(parents=True, exist_ok=True)
static_cache = "public, max-age=3600" if settings.prod_mode else None
app.mount("/static", CacheControlStaticFiles(directory=str(static_dir), cache_control=static_cache), name="static")

app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(admin.router)


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
            print(f"Auto seed finished with {len(report.errors)} errors; marker was not set.")
            return
        set_meta_value(db, "kochwiki_seed_done", "1")
        db.commit()
        print(f"KochWiki auto seed done: inserted={report.inserted}, updated={report.updated}, skipped={report.skipped}")
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
1. Diese Zeile importiert benoetigte Funktionen oder Klassen.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile importiert benoetigte Funktionen oder Klassen.
4. Diese Zeile importiert benoetigte Funktionen oder Klassen.
5. Diese Zeile importiert benoetigte Funktionen oder Klassen.
6. Diese Zeile importiert benoetigte Funktionen oder Klassen.
7. Diese Zeile importiert benoetigte Funktionen oder Klassen.
8. Diese Zeile ist absichtlich leer.
9. Diese Zeile importiert benoetigte Funktionen oder Klassen.
10. Diese Zeile importiert benoetigte Funktionen oder Klassen.
11. Diese Zeile importiert benoetigte Funktionen oder Klassen.
12. Diese Zeile importiert benoetigte Funktionen oder Klassen.
13. Diese Zeile importiert benoetigte Funktionen oder Klassen.
14. Diese Zeile importiert benoetigte Funktionen oder Klassen.
15. Diese Zeile ist absichtlich leer.
16. Diese Zeile setzt einen konkreten Teil der Implementierung um.
17. Diese Zeile ist absichtlich leer.
18. Diese Zeile setzt einen konkreten Teil der Implementierung um.
19. Diese Zeile ist absichtlich leer.
20. Diese Zeile ist absichtlich leer.
21. Diese Zeile startet eine Klassendefinition.
22. Diese Zeile startet eine Funktionsdefinition.
23. Diese Zeile setzt einen konkreten Teil der Implementierung um.
24. Diese Zeile setzt einen konkreten Teil der Implementierung um.
25. Diese Zeile ist absichtlich leer.
26. Diese Zeile startet eine Funktionsdefinition.
27. Diese Zeile setzt einen konkreten Teil der Implementierung um.
28. Diese Zeile steuert eine Bedingung im Ablauf.
29. Diese Zeile setzt einen konkreten Teil der Implementierung um.
30. Diese Zeile gibt einen Rueckgabewert zurueck.
31. Diese Zeile ist absichtlich leer.
32. Diese Zeile ist absichtlich leer.
33. Diese Zeile steuert eine Bedingung im Ablauf.
34. Diese Zeile setzt einen konkreten Teil der Implementierung um.
35. Diese Zeile steuert eine Bedingung im Ablauf.
36. Diese Zeile setzt einen konkreten Teil der Implementierung um.
37. Diese Zeile ist absichtlich leer.
38. Diese Zeile setzt einen konkreten Teil der Implementierung um.
39. Diese Zeile setzt einen konkreten Teil der Implementierung um.
40. Diese Zeile setzt einen konkreten Teil der Implementierung um.
41. Diese Zeile setzt einen konkreten Teil der Implementierung um.
42. Diese Zeile ist absichtlich leer.
43. Diese Zeile setzt einen konkreten Teil der Implementierung um.
44. Diese Zeile setzt einen konkreten Teil der Implementierung um.
45. Diese Zeile setzt einen konkreten Teil der Implementierung um.
46. Diese Zeile ist absichtlich leer.
47. Diese Zeile ist absichtlich leer.
48. Diese Zeile startet eine Funktionsdefinition.
49. Diese Zeile setzt einen konkreten Teil der Implementierung um.
50. Diese Zeile steuert eine Bedingung im Ablauf.
51. Diese Zeile gibt einen Rueckgabewert zurueck.
52. Diese Zeile setzt einen konkreten Teil der Implementierung um.
53. Diese Zeile setzt einen konkreten Teil der Implementierung um.
54. Diese Zeile steuert eine Bedingung im Ablauf.
55. Diese Zeile setzt einen konkreten Teil der Implementierung um.
56. Diese Zeile setzt einen konkreten Teil der Implementierung um.
57. Diese Zeile setzt einen konkreten Teil der Implementierung um.
58. Diese Zeile gibt einen Rueckgabewert zurueck.
59. Diese Zeile setzt einen konkreten Teil der Implementierung um.
60. Diese Zeile setzt einen konkreten Teil der Implementierung um.
61. Diese Zeile setzt einen konkreten Teil der Implementierung um.
62. Diese Zeile setzt einen konkreten Teil der Implementierung um.
63. Diese Zeile setzt einen konkreten Teil der Implementierung um.
64. Diese Zeile setzt einen konkreten Teil der Implementierung um.
65. Diese Zeile setzt einen konkreten Teil der Implementierung um.
66. Diese Zeile setzt einen konkreten Teil der Implementierung um.
67. Diese Zeile gibt einen Rueckgabewert zurueck.
68. Diese Zeile ist absichtlich leer.
69. Diese Zeile ist absichtlich leer.
70. Diese Zeile startet eine Funktionsdefinition.
71. Diese Zeile steuert eine Bedingung im Ablauf.
72. Diese Zeile setzt einen konkreten Teil der Implementierung um.
73. Diese Zeile setzt einen konkreten Teil der Implementierung um.
74. Diese Zeile gehoert zur Fehlerbehandlung.
75. Diese Zeile steuert eine Bedingung im Ablauf.
76. Diese Zeile setzt einen konkreten Teil der Implementierung um.
77. Diese Zeile setzt einen konkreten Teil der Implementierung um.
78. Diese Zeile steuert eine Bedingung im Ablauf.
79. Diese Zeile setzt einen konkreten Teil der Implementierung um.
80. Diese Zeile setzt einen konkreten Teil der Implementierung um.
81. Diese Zeile steuert eine Bedingung im Ablauf.
82. Diese Zeile setzt einen konkreten Teil der Implementierung um.
83. Diese Zeile setzt einen konkreten Teil der Implementierung um.
84. Diese Zeile setzt einen konkreten Teil der Implementierung um.
85. Diese Zeile steuert eine Bedingung im Ablauf.
86. Diese Zeile setzt einen konkreten Teil der Implementierung um.
87. Diese Zeile setzt einen konkreten Teil der Implementierung um.
88. Diese Zeile setzt einen konkreten Teil der Implementierung um.
89. Diese Zeile setzt einen konkreten Teil der Implementierung um.
90. Diese Zeile setzt eine Konfiguration oder Zuordnung.
91. Diese Zeile gehoert zur Fehlerbehandlung.
92. Diese Zeile setzt einen konkreten Teil der Implementierung um.
93. Diese Zeile ist absichtlich leer.
94. Diese Zeile ist absichtlich leer.
95. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
96. Diese Zeile startet eine Funktionsdefinition.
97. Diese Zeile setzt einen konkreten Teil der Implementierung um.
98. Diese Zeile ist absichtlich leer.
99. Diese Zeile ist absichtlich leer.
100. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
101. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
102. Diese Zeile startet eine Funktionsdefinition.
103. Diese Zeile gibt einen Rueckgabewert zurueck.

## app/routers/auth.py
```python
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, template_context
from app.models import User
from app.security import create_access_token, hash_password, verify_password
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
def login_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        return redirect("/")
    return templates.TemplateResponse("auth_login.html", template_context(request, current_user, error=None))


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
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
def register_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        return redirect("/")
    return templates.TemplateResponse("auth_register.html", template_context(request, current_user, error=None))


@router.post("/register")
def register_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    normalized_email = email.strip().lower()
    if len(password) < 8:
        return templates.TemplateResponse(
            "auth_register.html",
            template_context(request, None, error="Password must contain at least 8 characters."),
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
1. Diese Zeile importiert benoetigte Funktionen oder Klassen.
2. Diese Zeile importiert benoetigte Funktionen oder Klassen.
3. Diese Zeile importiert benoetigte Funktionen oder Klassen.
4. Diese Zeile ist absichtlich leer.
5. Diese Zeile importiert benoetigte Funktionen oder Klassen.
6. Diese Zeile importiert benoetigte Funktionen oder Klassen.
7. Diese Zeile importiert benoetigte Funktionen oder Klassen.
8. Diese Zeile importiert benoetigte Funktionen oder Klassen.
9. Diese Zeile importiert benoetigte Funktionen oder Klassen.
10. Diese Zeile importiert benoetigte Funktionen oder Klassen.
11. Diese Zeile ist absichtlich leer.
12. Diese Zeile setzt einen konkreten Teil der Implementierung um.
13. Diese Zeile setzt einen konkreten Teil der Implementierung um.
14. Diese Zeile ist absichtlich leer.
15. Diese Zeile ist absichtlich leer.
16. Diese Zeile startet eine Funktionsdefinition.
17. Diese Zeile setzt einen konkreten Teil der Implementierung um.
18. Diese Zeile setzt einen konkreten Teil der Implementierung um.
19. Diese Zeile setzt einen konkreten Teil der Implementierung um.
20. Diese Zeile setzt einen konkreten Teil der Implementierung um.
21. Diese Zeile setzt einen konkreten Teil der Implementierung um.
22. Diese Zeile setzt einen konkreten Teil der Implementierung um.
23. Diese Zeile setzt einen konkreten Teil der Implementierung um.
24. Diese Zeile setzt einen konkreten Teil der Implementierung um.
25. Diese Zeile setzt einen konkreten Teil der Implementierung um.
26. Diese Zeile ist absichtlich leer.
27. Diese Zeile ist absichtlich leer.
28. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
29. Diese Zeile startet eine Funktionsdefinition.
30. Diese Zeile steuert eine Bedingung im Ablauf.
31. Diese Zeile gibt einen Rueckgabewert zurueck.
32. Diese Zeile gibt einen Rueckgabewert zurueck.
33. Diese Zeile ist absichtlich leer.
34. Diese Zeile ist absichtlich leer.
35. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
36. Diese Zeile startet eine Funktionsdefinition.
37. Diese Zeile setzt eine Konfiguration oder Zuordnung.
38. Diese Zeile setzt eine Konfiguration oder Zuordnung.
39. Diese Zeile setzt eine Konfiguration oder Zuordnung.
40. Diese Zeile setzt eine Konfiguration oder Zuordnung.
41. Diese Zeile setzt eine Konfiguration oder Zuordnung.
42. Diese Zeile setzt einen konkreten Teil der Implementierung um.
43. Diese Zeile steuert eine Bedingung im Ablauf.
44. Diese Zeile setzt einen konkreten Teil der Implementierung um.
45. Diese Zeile setzt einen konkreten Teil der Implementierung um.
46. Diese Zeile setzt einen konkreten Teil der Implementierung um.
47. Diese Zeile setzt einen konkreten Teil der Implementierung um.
48. Diese Zeile setzt einen konkreten Teil der Implementierung um.
49. Diese Zeile gibt einen Rueckgabewert zurueck.
50. Diese Zeile setzt einen konkreten Teil der Implementierung um.
51. Diese Zeile setzt einen konkreten Teil der Implementierung um.
52. Diese Zeile setzt einen konkreten Teil der Implementierung um.
53. Diese Zeile gibt einen Rueckgabewert zurueck.
54. Diese Zeile ist absichtlich leer.
55. Diese Zeile ist absichtlich leer.
56. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
57. Diese Zeile startet eine Funktionsdefinition.
58. Diese Zeile steuert eine Bedingung im Ablauf.
59. Diese Zeile gibt einen Rueckgabewert zurueck.
60. Diese Zeile gibt einen Rueckgabewert zurueck.
61. Diese Zeile ist absichtlich leer.
62. Diese Zeile ist absichtlich leer.
63. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
64. Diese Zeile startet eine Funktionsdefinition.
65. Diese Zeile setzt eine Konfiguration oder Zuordnung.
66. Diese Zeile setzt eine Konfiguration oder Zuordnung.
67. Diese Zeile setzt eine Konfiguration oder Zuordnung.
68. Diese Zeile setzt eine Konfiguration oder Zuordnung.
69. Diese Zeile setzt eine Konfiguration oder Zuordnung.
70. Diese Zeile setzt einen konkreten Teil der Implementierung um.
71. Diese Zeile steuert eine Bedingung im Ablauf.
72. Diese Zeile gibt einen Rueckgabewert zurueck.
73. Diese Zeile setzt einen konkreten Teil der Implementierung um.
74. Diese Zeile setzt einen konkreten Teil der Implementierung um.
75. Diese Zeile setzt einen konkreten Teil der Implementierung um.
76. Diese Zeile setzt einen konkreten Teil der Implementierung um.
77. Diese Zeile setzt einen konkreten Teil der Implementierung um.
78. Diese Zeile steuert eine Bedingung im Ablauf.
79. Diese Zeile gibt einen Rueckgabewert zurueck.
80. Diese Zeile setzt einen konkreten Teil der Implementierung um.
81. Diese Zeile setzt einen konkreten Teil der Implementierung um.
82. Diese Zeile setzt einen konkreten Teil der Implementierung um.
83. Diese Zeile setzt einen konkreten Teil der Implementierung um.
84. Diese Zeile setzt einen konkreten Teil der Implementierung um.
85. Diese Zeile setzt einen konkreten Teil der Implementierung um.
86. Diese Zeile setzt einen konkreten Teil der Implementierung um.
87. Diese Zeile setzt einen konkreten Teil der Implementierung um.
88. Diese Zeile setzt einen konkreten Teil der Implementierung um.
89. Diese Zeile setzt einen konkreten Teil der Implementierung um.
90. Diese Zeile gibt einen Rueckgabewert zurueck.
91. Diese Zeile ist absichtlich leer.
92. Diese Zeile ist absichtlich leer.
93. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
94. Diese Zeile startet eine Funktionsdefinition.
95. Diese Zeile setzt einen konkreten Teil der Implementierung um.
96. Diese Zeile setzt einen konkreten Teil der Implementierung um.
97. Diese Zeile gibt einen Rueckgabewert zurueck.
98. Diese Zeile ist absichtlich leer.
99. Diese Zeile ist absichtlich leer.
100. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
101. Diese Zeile startet eine Funktionsdefinition.
102. Diese Zeile gibt einen Rueckgabewert zurueck.
103. Diese Zeile ist absichtlich leer.
104. Diese Zeile ist absichtlich leer.
105. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
106. Diese Zeile startet eine Funktionsdefinition.
107. Diese Zeile gibt einen Rueckgabewert zurueck.
108. Diese Zeile setzt einen konkreten Teil der Implementierung um.
109. Diese Zeile setzt einen konkreten Teil der Implementierung um.
110. Diese Zeile setzt einen konkreten Teil der Implementierung um.
111. Diese Zeile setzt einen konkreten Teil der Implementierung um.
112. Diese Zeile setzt einen konkreten Teil der Implementierung um.
113. Diese Zeile ist absichtlich leer.
114. Diese Zeile ist absichtlich leer.
115. Diese Zeile setzt einen Dekorator fuer die folgende Definition.
116. Diese Zeile startet eine Funktionsdefinition.
117. Diese Zeile steuert eine Bedingung im Ablauf.
118. Diese Zeile setzt einen konkreten Teil der Implementierung um.
119. Diese Zeile gibt einen Rueckgabewert zurueck.

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
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt einen konkreten Teil der Implementierung um.
2. Diese Zeile setzt einen konkreten Teil der Implementierung um.
3. Diese Zeile setzt einen konkreten Teil der Implementierung um.
4. Diese Zeile setzt einen konkreten Teil der Implementierung um.
5. Diese Zeile setzt einen konkreten Teil der Implementierung um.
6. Diese Zeile setzt einen konkreten Teil der Implementierung um.
7. Diese Zeile setzt einen konkreten Teil der Implementierung um.
8. Diese Zeile setzt einen konkreten Teil der Implementierung um.
9. Diese Zeile setzt einen konkreten Teil der Implementierung um.
10. Diese Zeile setzt einen konkreten Teil der Implementierung um.
11. Diese Zeile setzt einen konkreten Teil der Implementierung um.
12. Diese Zeile setzt einen konkreten Teil der Implementierung um.
13. Diese Zeile setzt einen konkreten Teil der Implementierung um.
14. Diese Zeile setzt einen konkreten Teil der Implementierung um.

## Dockerfile
```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN addgroup --system app && adduser --system --ingroup app app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY alembic ./alembic
COPY app ./app
COPY scripts ./scripts
COPY alembic.ini ./
COPY start.sh ./
COPY .env.example ./.env.example

RUN chmod +x /app/start.sh && chown -R app:app /app

USER app

EXPOSE 8000
ENV PORT=8000

CMD ["./start.sh"]
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt eine Konfiguration oder Zuordnung.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
4. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
5. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
6. Diese Zeile ist absichtlich leer.
7. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
8. Diese Zeile ist absichtlich leer.
9. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
10. Diese Zeile ist absichtlich leer.
11. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
12. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
13. Diese Zeile ist absichtlich leer.
14. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
15. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
16. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
17. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
18. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
19. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
20. Diese Zeile ist absichtlich leer.
21. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
22. Diese Zeile ist absichtlich leer.
23. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
24. Diese Zeile ist absichtlich leer.
25. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
26. Diese Zeile konfiguriert den Docker-Build oder Container-Start.
27. Diese Zeile ist absichtlich leer.
28. Diese Zeile konfiguriert den Docker-Build oder Container-Start.

## .dockerignore
```text
.git
.gitignore
.venv
__pycache__/
*.pyc
*.pyo
*.pyd
*.db
*.sqlite
*.sqlite3
.pytest_cache/
.mypy_cache/
.ruff_cache/
htmlcov/
.coverage
mealmate.db
DELIVERABLE_ZUSATZ3.md
projekt_3_meal_mate.pdf
rezepte_kochwiki_clean_3713.csv
*.log
tmp/
dist/
build/
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt einen konkreten Teil der Implementierung um.
2. Diese Zeile setzt einen konkreten Teil der Implementierung um.
3. Diese Zeile setzt einen konkreten Teil der Implementierung um.
4. Diese Zeile setzt einen konkreten Teil der Implementierung um.
5. Diese Zeile setzt einen konkreten Teil der Implementierung um.
6. Diese Zeile setzt einen konkreten Teil der Implementierung um.
7. Diese Zeile setzt einen konkreten Teil der Implementierung um.
8. Diese Zeile setzt einen konkreten Teil der Implementierung um.
9. Diese Zeile setzt einen konkreten Teil der Implementierung um.
10. Diese Zeile setzt einen konkreten Teil der Implementierung um.
11. Diese Zeile setzt einen konkreten Teil der Implementierung um.
12. Diese Zeile setzt einen konkreten Teil der Implementierung um.
13. Diese Zeile setzt einen konkreten Teil der Implementierung um.
14. Diese Zeile setzt einen konkreten Teil der Implementierung um.
15. Diese Zeile setzt einen konkreten Teil der Implementierung um.
16. Diese Zeile setzt einen konkreten Teil der Implementierung um.
17. Diese Zeile setzt einen konkreten Teil der Implementierung um.
18. Diese Zeile setzt einen konkreten Teil der Implementierung um.
19. Diese Zeile setzt einen konkreten Teil der Implementierung um.
20. Diese Zeile setzt einen konkreten Teil der Implementierung um.
21. Diese Zeile setzt einen konkreten Teil der Implementierung um.
22. Diese Zeile setzt einen konkreten Teil der Implementierung um.
23. Diese Zeile setzt einen konkreten Teil der Implementierung um.

## docker-compose.yml
```yaml
services:
  db:
    image: postgres:16
    restart: unless-stopped
    environment:
      POSTGRES_DB: mealmate
      POSTGRES_USER: mealmate
      POSTGRES_PASSWORD: mealmate
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mealmate -d mealmate"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    restart: unless-stopped
    depends_on:
      db:
        condition: service_healthy
    environment:
      APP_NAME: MealMate
      APP_ENV: dev
      APP_URL: http://localhost:8000
      SECRET_KEY: change-this-in-docker
      ALGORITHM: HS256
      TOKEN_EXPIRE_MINUTES: 60
      DATABASE_URL: postgresql+psycopg://mealmate:mealmate@db:5432/mealmate
      ALLOWED_HOSTS: localhost,127.0.0.1
      COOKIE_SECURE: 0
      MAX_UPLOAD_MB: 4
      ALLOWED_IMAGE_TYPES: image/png,image/jpeg,image/webp
      AUTO_SEED_KOCHWIKI: 0
      PORT: 8000
    ports:
      - "8000:8000"

volumes:
  postgres_data:
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt eine Konfiguration oder Zuordnung.
2. Diese Zeile setzt eine Konfiguration oder Zuordnung.
3. Diese Zeile setzt eine Konfiguration oder Zuordnung.
4. Diese Zeile setzt eine Konfiguration oder Zuordnung.
5. Diese Zeile setzt eine Konfiguration oder Zuordnung.
6. Diese Zeile setzt eine Konfiguration oder Zuordnung.
7. Diese Zeile setzt eine Konfiguration oder Zuordnung.
8. Diese Zeile setzt eine Konfiguration oder Zuordnung.
9. Diese Zeile setzt eine Konfiguration oder Zuordnung.
10. Diese Zeile beschreibt einen Punkt in der Anleitung.
11. Diese Zeile setzt eine Konfiguration oder Zuordnung.
12. Diese Zeile beschreibt einen Punkt in der Anleitung.
13. Diese Zeile setzt eine Konfiguration oder Zuordnung.
14. Diese Zeile setzt eine Konfiguration oder Zuordnung.
15. Diese Zeile setzt eine Konfiguration oder Zuordnung.
16. Diese Zeile setzt eine Konfiguration oder Zuordnung.
17. Diese Zeile setzt eine Konfiguration oder Zuordnung.
18. Diese Zeile ist absichtlich leer.
19. Diese Zeile setzt eine Konfiguration oder Zuordnung.
20. Diese Zeile setzt eine Konfiguration oder Zuordnung.
21. Diese Zeile setzt eine Konfiguration oder Zuordnung.
22. Diese Zeile setzt eine Konfiguration oder Zuordnung.
23. Diese Zeile setzt eine Konfiguration oder Zuordnung.
24. Diese Zeile setzt eine Konfiguration oder Zuordnung.
25. Diese Zeile setzt eine Konfiguration oder Zuordnung.
26. Diese Zeile setzt eine Konfiguration oder Zuordnung.
27. Diese Zeile setzt eine Konfiguration oder Zuordnung.
28. Diese Zeile setzt eine Konfiguration oder Zuordnung.
29. Diese Zeile setzt eine Konfiguration oder Zuordnung.
30. Diese Zeile setzt eine Konfiguration oder Zuordnung.
31. Diese Zeile setzt eine Konfiguration oder Zuordnung.
32. Diese Zeile setzt eine Konfiguration oder Zuordnung.
33. Diese Zeile setzt eine Konfiguration oder Zuordnung.
34. Diese Zeile setzt eine Konfiguration oder Zuordnung.
35. Diese Zeile setzt eine Konfiguration oder Zuordnung.
36. Diese Zeile setzt eine Konfiguration oder Zuordnung.
37. Diese Zeile setzt eine Konfiguration oder Zuordnung.
38. Diese Zeile setzt eine Konfiguration oder Zuordnung.
39. Diese Zeile setzt eine Konfiguration oder Zuordnung.
40. Diese Zeile beschreibt einen Punkt in der Anleitung.
41. Diese Zeile ist absichtlich leer.
42. Diese Zeile setzt eine Konfiguration oder Zuordnung.
43. Diese Zeile setzt eine Konfiguration oder Zuordnung.

## start.sh
```bash
#!/usr/bin/env sh
set -eu

PORT="${PORT:-8000}"
WEB_CONCURRENCY="${WEB_CONCURRENCY:-2}"
WEB_TIMEOUT="${WEB_TIMEOUT:-120}"
APP_MODULE="${APP_MODULE:-app.main:app}"

echo "Applying database migrations..."
alembic upgrade head

echo "Starting MealMate..."
exec gunicorn \
  -k uvicorn.workers.UvicornWorker \
  "${APP_MODULE}" \
  --bind "0.0.0.0:${PORT}" \
  --workers "${WEB_CONCURRENCY}" \
  --timeout "${WEB_TIMEOUT}" \
  --access-logfile "-" \
  --error-logfile "-" \
  --forwarded-allow-ips "*"
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Interpreter fuer das Skript.
2. Diese Zeile setzt einen konkreten Teil der Implementierung um.
3. Diese Zeile ist absichtlich leer.
4. Diese Zeile setzt eine Konfiguration oder Zuordnung.
5. Diese Zeile setzt eine Konfiguration oder Zuordnung.
6. Diese Zeile setzt eine Konfiguration oder Zuordnung.
7. Diese Zeile setzt eine Konfiguration oder Zuordnung.
8. Diese Zeile ist absichtlich leer.
9. Diese Zeile setzt einen konkreten Teil der Implementierung um.
10. Diese Zeile setzt einen konkreten Teil der Implementierung um.
11. Diese Zeile ist absichtlich leer.
12. Diese Zeile setzt einen konkreten Teil der Implementierung um.
13. Diese Zeile setzt einen konkreten Teil der Implementierung um.
14. Diese Zeile setzt einen konkreten Teil der Implementierung um.
15. Diese Zeile setzt einen konkreten Teil der Implementierung um.
16. Diese Zeile setzt eine Konfiguration oder Zuordnung.
17. Diese Zeile setzt einen konkreten Teil der Implementierung um.
18. Diese Zeile setzt einen konkreten Teil der Implementierung um.
19. Diese Zeile setzt einen konkreten Teil der Implementierung um.
20. Diese Zeile setzt einen konkreten Teil der Implementierung um.
21. Diese Zeile setzt einen konkreten Teil der Implementierung um.

## README_DEPLOY.md
```markdown
# MealMate Deployment Guide

Dieses Dokument zeigt zwei einfache Wege, um MealMate als oeffentliche Website zu deployen.

## Voraussetzungen

- Ein GitHub-Repository mit diesem Projekt.
- Eine erzeugte `SECRET_KEY` mit hoher Entropie.
- `AUTO_SEED_KOCHWIKI=0` in Produktion als sicherer Standard.

## Wichtige ENV Variablen

- `APP_ENV=prod`
- `APP_URL=https://deine-domain`
- `SECRET_KEY=<lange-zufaellige-zeichenkette>`
- `DATABASE_URL=<postgres-connection-string>`
- `ALLOWED_HOSTS=deine-domain[,weitere-domain]`
- `COOKIE_SECURE=1`
- `TOKEN_EXPIRE_MINUTES=60`
- `MAX_UPLOAD_MB=4`
- `AUTO_SEED_KOCHWIKI=0`

## Weg A (Empfohlen): Neon + Render

1. Erstelle bei Neon ein neues Projekt und kopiere den Postgres Connection String.
2. Passe den Connection String fuer SQLAlchemy an (`postgresql+psycopg://...`) falls noetig.
3. Pushe dieses Projekt zu GitHub.
4. Erstelle auf Render einen neuen Web Service aus dem GitHub-Repository.
5. Nutze den Docker-Deploy (Render erkennt die `Dockerfile` automatisch).
6. Setze in Render die ENV Variablen aus der Liste oben.
7. Setze `DATABASE_URL` auf den Neon String.
8. Setze `ALLOWED_HOSTS` auf deine Render Domain (z. B. `mealmate.onrender.com`).
9. Deploye den Service.
10. Pruefe `https://deine-domain/healthz` auf `{ "status": "ok" }`.
11. Oeffne danach die Website im Browser und teste Login, Rezeptseite und PDF-Download.

Hinweis:
- Free-Tarife haben oft Cold Starts und schlafen bei Inaktivitaet.

## Weg B (Alternative): Supabase + Render

1. Erstelle ein Supabase Projekt und hole den Postgres Connection String.
2. Konvertiere den String bei Bedarf nach `postgresql+psycopg://...`.
3. Erstelle den Render Web Service aus dem GitHub-Repository.
4. Hinterlege die gleichen ENV Variablen wie bei Weg A.
5. Setze `DATABASE_URL` auf den Supabase String.
6. Deploye und pruefe `.../healthz`.

Hinweis:
- Supabase Free kann bei Quota-Limits gedrosselt werden oder in read-only Situationen laufen.

## Render Blueprint (Optional)

- Dieses Projekt enthaelt bereits eine `render.yaml`.
- Du kannst in Render statt manueller Konfiguration auch den Blueprint verwenden.
- Trage danach noch geheime Werte wie `DATABASE_URL` ein.

## Lokaler prod-naher Test mit Docker Compose

```bash
docker compose up --build
```

Danach:
- App: `http://localhost:8000`
- Healthcheck: `http://localhost:8000/healthz`
- DB: Postgres auf `localhost:5432`

## Migrations und Startverhalten

- Der Container startet ueber `start.sh`.
- `start.sh` fuehrt zuerst `alembic upgrade head` aus.
- Danach startet Gunicorn mit Uvicorn-Worker.
- Seed laeuft nur, wenn `AUTO_SEED_KOCHWIKI=1` gesetzt wurde.

## Sicherheitshinweise fuer Produktion

- Nutze niemals den Default `SECRET_KEY`.
- Setze `COOKIE_SECURE=1`.
- Nutze keine SQLite-Datei in Produktion.
- Begrenze `ALLOWED_HOSTS` auf echte Domains.
```
ZEILEN-ERKL?RUNG
1. Diese Zeile ist ein Kommentar oder eine Markdown-Ueberschrift.
2. Diese Zeile ist absichtlich leer.
3. Diese Zeile setzt einen konkreten Teil der Implementierung um.
4. Diese Zeile ist absichtlich leer.
5. Diese Zeile ist ein Kommentar oder eine Markdown-Ueberschrift.
6. Diese Zeile ist absichtlich leer.
7. Diese Zeile beschreibt einen Punkt in der Anleitung.
8. Diese Zeile beschreibt einen Punkt in der Anleitung.
9. Diese Zeile beschreibt einen Punkt in der Anleitung.
10. Diese Zeile ist absichtlich leer.
11. Diese Zeile ist ein Kommentar oder eine Markdown-Ueberschrift.
12. Diese Zeile ist absichtlich leer.
13. Diese Zeile beschreibt einen Punkt in der Anleitung.
14. Diese Zeile beschreibt einen Punkt in der Anleitung.
15. Diese Zeile beschreibt einen Punkt in der Anleitung.
16. Diese Zeile beschreibt einen Punkt in der Anleitung.
17. Diese Zeile beschreibt einen Punkt in der Anleitung.
18. Diese Zeile beschreibt einen Punkt in der Anleitung.
19. Diese Zeile beschreibt einen Punkt in der Anleitung.
20. Diese Zeile beschreibt einen Punkt in der Anleitung.
21. Diese Zeile beschreibt einen Punkt in der Anleitung.
22. Diese Zeile ist absichtlich leer.
23. Diese Zeile ist ein Kommentar oder eine Markdown-Ueberschrift.
24. Diese Zeile ist absichtlich leer.
25. Diese Zeile beschreibt einen Punkt in der Anleitung.
26. Diese Zeile beschreibt einen Punkt in der Anleitung.
27. Diese Zeile beschreibt einen Punkt in der Anleitung.
28. Diese Zeile beschreibt einen Punkt in der Anleitung.
29. Diese Zeile beschreibt einen Punkt in der Anleitung.
30. Diese Zeile beschreibt einen Punkt in der Anleitung.
31. Diese Zeile beschreibt einen Punkt in der Anleitung.
32. Diese Zeile beschreibt einen Punkt in der Anleitung.
33. Diese Zeile beschreibt einen Punkt in der Anleitung.
34. Diese Zeile beschreibt einen Punkt in der Anleitung.
35. Diese Zeile beschreibt einen Punkt in der Anleitung.
36. Diese Zeile ist absichtlich leer.
37. Diese Zeile setzt eine Konfiguration oder Zuordnung.
38. Diese Zeile beschreibt einen Punkt in der Anleitung.
39. Diese Zeile ist absichtlich leer.
40. Diese Zeile ist ein Kommentar oder eine Markdown-Ueberschrift.
41. Diese Zeile ist absichtlich leer.
42. Diese Zeile beschreibt einen Punkt in der Anleitung.
43. Diese Zeile beschreibt einen Punkt in der Anleitung.
44. Diese Zeile beschreibt einen Punkt in der Anleitung.
45. Diese Zeile beschreibt einen Punkt in der Anleitung.
46. Diese Zeile beschreibt einen Punkt in der Anleitung.
47. Diese Zeile beschreibt einen Punkt in der Anleitung.
48. Diese Zeile ist absichtlich leer.
49. Diese Zeile setzt eine Konfiguration oder Zuordnung.
50. Diese Zeile beschreibt einen Punkt in der Anleitung.
51. Diese Zeile ist absichtlich leer.
52. Diese Zeile ist ein Kommentar oder eine Markdown-Ueberschrift.
53. Diese Zeile ist absichtlich leer.
54. Diese Zeile beschreibt einen Punkt in der Anleitung.
55. Diese Zeile beschreibt einen Punkt in der Anleitung.
56. Diese Zeile beschreibt einen Punkt in der Anleitung.
57. Diese Zeile ist absichtlich leer.
58. Diese Zeile ist ein Kommentar oder eine Markdown-Ueberschrift.
59. Diese Zeile ist absichtlich leer.
60. Diese Zeile setzt einen konkreten Teil der Implementierung um.
61. Diese Zeile setzt einen konkreten Teil der Implementierung um.
62. Diese Zeile setzt einen konkreten Teil der Implementierung um.
63. Diese Zeile ist absichtlich leer.
64. Diese Zeile setzt eine Konfiguration oder Zuordnung.
65. Diese Zeile beschreibt einen Punkt in der Anleitung.
66. Diese Zeile beschreibt einen Punkt in der Anleitung.
67. Diese Zeile beschreibt einen Punkt in der Anleitung.
68. Diese Zeile ist absichtlich leer.
69. Diese Zeile ist ein Kommentar oder eine Markdown-Ueberschrift.
70. Diese Zeile ist absichtlich leer.
71. Diese Zeile beschreibt einen Punkt in der Anleitung.
72. Diese Zeile beschreibt einen Punkt in der Anleitung.
73. Diese Zeile beschreibt einen Punkt in der Anleitung.
74. Diese Zeile beschreibt einen Punkt in der Anleitung.
75. Diese Zeile ist absichtlich leer.
76. Diese Zeile ist ein Kommentar oder eine Markdown-Ueberschrift.
77. Diese Zeile ist absichtlich leer.
78. Diese Zeile beschreibt einen Punkt in der Anleitung.
79. Diese Zeile beschreibt einen Punkt in der Anleitung.
80. Diese Zeile beschreibt einen Punkt in der Anleitung.
81. Diese Zeile beschreibt einen Punkt in der Anleitung.

## render.yaml
```yaml
services:
  - type: web
    name: mealmate
    env: docker
    plan: free
    dockerfilePath: ./Dockerfile
    autoDeploy: true
    envVars:
      - key: APP_NAME
        value: MealMate
      - key: APP_ENV
        value: prod
      - key: APP_URL
        value: https://mealmate.onrender.com
      - key: SECRET_KEY
        generateValue: true
      - key: DATABASE_URL
        sync: false
      - key: ALLOWED_HOSTS
        value: mealmate.onrender.com
      - key: COOKIE_SECURE
        value: "1"
      - key: TOKEN_EXPIRE_MINUTES
        value: "60"
      - key: MAX_UPLOAD_MB
        value: "4"
      - key: ALLOWED_IMAGE_TYPES
        value: image/png,image/jpeg,image/webp
      - key: AUTO_SEED_KOCHWIKI
        value: "0"
      - key: PORT
        value: "10000"
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt eine Konfiguration oder Zuordnung.
2. Diese Zeile beschreibt einen Punkt in der Anleitung.
3. Diese Zeile setzt eine Konfiguration oder Zuordnung.
4. Diese Zeile setzt eine Konfiguration oder Zuordnung.
5. Diese Zeile setzt eine Konfiguration oder Zuordnung.
6. Diese Zeile setzt eine Konfiguration oder Zuordnung.
7. Diese Zeile setzt eine Konfiguration oder Zuordnung.
8. Diese Zeile setzt eine Konfiguration oder Zuordnung.
9. Diese Zeile beschreibt einen Punkt in der Anleitung.
10. Diese Zeile setzt eine Konfiguration oder Zuordnung.
11. Diese Zeile beschreibt einen Punkt in der Anleitung.
12. Diese Zeile setzt eine Konfiguration oder Zuordnung.
13. Diese Zeile beschreibt einen Punkt in der Anleitung.
14. Diese Zeile setzt eine Konfiguration oder Zuordnung.
15. Diese Zeile beschreibt einen Punkt in der Anleitung.
16. Diese Zeile setzt eine Konfiguration oder Zuordnung.
17. Diese Zeile beschreibt einen Punkt in der Anleitung.
18. Diese Zeile setzt eine Konfiguration oder Zuordnung.
19. Diese Zeile beschreibt einen Punkt in der Anleitung.
20. Diese Zeile setzt eine Konfiguration oder Zuordnung.
21. Diese Zeile beschreibt einen Punkt in der Anleitung.
22. Diese Zeile setzt eine Konfiguration oder Zuordnung.
23. Diese Zeile beschreibt einen Punkt in der Anleitung.
24. Diese Zeile setzt eine Konfiguration oder Zuordnung.
25. Diese Zeile beschreibt einen Punkt in der Anleitung.
26. Diese Zeile setzt eine Konfiguration oder Zuordnung.
27. Diese Zeile beschreibt einen Punkt in der Anleitung.
28. Diese Zeile setzt eine Konfiguration oder Zuordnung.
29. Diese Zeile beschreibt einen Punkt in der Anleitung.
30. Diese Zeile setzt eine Konfiguration oder Zuordnung.
31. Diese Zeile beschreibt einen Punkt in der Anleitung.
32. Diese Zeile setzt eine Konfiguration oder Zuordnung.

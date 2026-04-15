# DELIVERABLE_EMAIL_CHANGE

## Geänderte Dateien

- .env.example
- app/config.py
- app/models.py
- app/mailer.py
- app/routers/auth.py
- app/templates/me.html
- app/templates/auth_change_email.html
- app/templates/auth_change_email_confirm.html
- app/i18n/locales/de.json
- app/i18n/locales/en.json
- app/i18n/locales/fr.json
- alembic/versions/20260303_0008_email_change_token_field.py
- tests/test_email_change.py
- README_EMAIL_CHANGE.md

## .env.example

`$lang
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
13. Diese Zeile enthält den Code 'CSRF_COOKIE_NAME=csrf_token'.
14. Diese Zeile enthält den Code 'CSRF_HEADER_NAME=X-CSRF-Token'.
15. Diese Zeile enthält den Code 'PASSWORD_RESET_TOKEN_MINUTES=30'.
16. Diese Zeile enthält den Code 'MAX_UPLOAD_MB=4'.
17. Diese Zeile enthält den Code 'MAX_CSV_UPLOAD_MB=10'.
18. Diese Zeile enthält den Code 'ALLOWED_IMAGE_TYPES=image/png,image/jpeg,image/webp'.
19. Diese Zeile enthält den Code 'MAIL_OUTBOX_PATH=outbox/reset_links.txt'.
20. Diese Zeile enthält den Code 'MAIL_OUTBOX_EMAIL_CHANGE_PATH=outbox/email_change_links.txt'.
21. Diese Zeile enthält den Code 'SMTP_HOST='.
22. Diese Zeile enthält den Code 'SMTP_PORT=587'.
23. Diese Zeile enthält den Code 'SMTP_USER='.
24. Diese Zeile enthält den Code 'SMTP_PASSWORD='.
25. Diese Zeile enthält den Code 'SMTP_FROM=no-reply@mealmate.local'.
26. Diese Zeile enthält den Code 'SECURITY_EVENT_RETENTION_DAYS=30'.
27. Diese Zeile enthält den Code 'SECURITY_EVENT_MAX_ROWS=5000'.
28. Diese Zeile enthält den Code 'ENABLE_KOCHWIKI_SEED=0'.
29. Diese Zeile enthält den Code 'AUTO_SEED_KOCHWIKI=0'.
30. Diese Zeile enthält den Code 'KOCHWIKI_CSV_PATH=rezepte_kochwiki_clean_3713.csv'.
31. Diese Zeile enthält den Code 'IMPORT_DOWNLOAD_IMAGES=0'.
32. Diese Zeile enthält den Code 'SEED_ADMIN_EMAIL=admin@mealmate.local'.
33. Diese Zeile enthält den Code 'SEED_ADMIN_PASSWORD=AdminPass123!'.

## app/config.py

`$lang
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
22. Diese Zeile enthält den Code 'csrf_cookie_name: str = "csrf_token"'.
23. Diese Zeile enthält den Code 'csrf_header_name: str = "X-CSRF-Token"'.
24. Diese Zeile enthält den Code 'password_reset_token_minutes: int = 30'.
25. Diese Zeile enthält den Code 'max_upload_mb: int = 4'.
26. Diese Zeile enthält den Code 'max_csv_upload_mb: int = 10'.
27. Diese Zeile enthält den Code 'allowed_image_types: Annotated[list[str], NoDecode] = ["image/png", "image/jpeg", "image/webp"]'.
28. Diese Zeile enthält den Code 'mail_outbox_path: str = "outbox/reset_links.txt"'.
29. Diese Zeile enthält den Code 'mail_outbox_email_change_path: str = "outbox/email_change_links.txt"'.
30. Diese Zeile enthält den Code 'smtp_host: str | None = None'.
31. Diese Zeile enthält den Code 'smtp_port: int = 587'.
32. Diese Zeile enthält den Code 'smtp_user: str | None = None'.
33. Diese Zeile enthält den Code 'smtp_password: str | None = None'.
34. Diese Zeile enthält den Code 'smtp_from: str = "no-reply@mealmate.local"'.
35. Diese Zeile enthält den Code 'security_event_retention_days: int = 30'.
36. Diese Zeile enthält den Code 'security_event_max_rows: int = 5000'.
37. Diese Zeile enthält den Code 'enable_kochwiki_seed: bool = False'.
38. Diese Zeile enthält den Code 'auto_seed_kochwiki: bool = False'.
39. Diese Zeile enthält den Code 'kochwiki_csv_path: str = "rezepte_kochwiki_clean_3713.csv"'.
40. Diese Zeile enthält den Code 'import_download_images: bool = False'.
41. Diese Zeile enthält den Code 'seed_admin_email: str = "admin@mealmate.local"'.
42. Diese Zeile enthält den Code 'seed_admin_password: str = "AdminPass123!"'.
43. Diese Zeile ist leer und trennt Abschnitte.
44. Diese Zeile enthält den Code '@field_validator("allowed_image_types", mode="before")'.
45. Diese Zeile enthält den Code '@classmethod'.
46. Diese Zeile enthält den Code 'def parse_allowed_image_types(cls, value: str | list[str]) -> list[str]:'.
47. Diese Zeile enthält den Code 'if isinstance(value, list):'.
48. Diese Zeile enthält den Code 'return [item.strip() for item in value if item.strip()]'.
49. Diese Zeile enthält den Code 'return [item.strip() for item in value.split(",") if item.strip()]'.
50. Diese Zeile ist leer und trennt Abschnitte.
51. Diese Zeile enthält den Code '@field_validator("allowed_hosts", mode="before")'.
52. Diese Zeile enthält den Code '@classmethod'.
53. Diese Zeile enthält den Code 'def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:'.
54. Diese Zeile enthält den Code 'if isinstance(value, list):'.
55. Diese Zeile enthält den Code 'hosts = [item.strip() for item in value if item.strip()]'.
56. Diese Zeile enthält den Code 'else:'.
57. Diese Zeile enthält den Code 'hosts = [item.strip() for item in value.split(",") if item.strip()]'.
58. Diese Zeile enthält den Code 'return hosts or ["*"]'.
59. Diese Zeile ist leer und trennt Abschnitte.
60. Diese Zeile enthält den Code '@field_validator("log_level", mode="before")'.
61. Diese Zeile enthält den Code '@classmethod'.
62. Diese Zeile enthält den Code 'def parse_log_level(cls, value: str) -> str:'.
63. Diese Zeile enthält den Code 'return str(value).strip().upper() or "INFO"'.
64. Diese Zeile ist leer und trennt Abschnitte.
65. Diese Zeile enthält den Code '@property'.
66. Diese Zeile enthält den Code 'def sqlalchemy_database_url(self) -> str:'.
67. Diese Zeile enthält den Code 'url = self.database_url.strip()'.
68. Diese Zeile enthält den Code 'if url.startswith("postgres://"):'.
69. Diese Zeile enthält den Code 'return "postgresql+psycopg://" + url[len("postgres://") :]'.
70. Diese Zeile enthält den Code 'if url.startswith("postgresql://"):'.
71. Diese Zeile enthält den Code 'return "postgresql+psycopg://" + url[len("postgresql://") :]'.
72. Diese Zeile enthält den Code 'return url'.
73. Diese Zeile ist leer und trennt Abschnitte.
74. Diese Zeile enthält den Code '@property'.
75. Diese Zeile enthält den Code 'def is_sqlite(self) -> bool:'.
76. Diese Zeile enthält den Code 'return self.sqlalchemy_database_url.startswith("sqlite")'.
77. Diese Zeile ist leer und trennt Abschnitte.
78. Diese Zeile enthält den Code '@property'.
79. Diese Zeile enthält den Code 'def prod_mode(self) -> bool:'.
80. Diese Zeile enthält den Code 'return self.app_env == "prod"'.
81. Diese Zeile ist leer und trennt Abschnitte.
82. Diese Zeile enthält den Code '@property'.
83. Diese Zeile enthält den Code 'def resolved_cookie_secure(self) -> bool:'.
84. Diese Zeile enthält den Code 'if self.cookie_secure is None:'.
85. Diese Zeile enthält den Code 'return self.prod_mode'.
86. Diese Zeile enthält den Code 'return self.cookie_secure'.
87. Diese Zeile ist leer und trennt Abschnitte.
88. Diese Zeile enthält den Code '@property'.
89. Diese Zeile enthält den Code 'def resolved_force_https(self) -> bool:'.
90. Diese Zeile enthält den Code 'if self.force_https is None:'.
91. Diese Zeile enthält den Code 'return self.prod_mode'.
92. Diese Zeile enthält den Code 'return self.force_https'.
93. Diese Zeile ist leer und trennt Abschnitte.
94. Diese Zeile ist leer und trennt Abschnitte.
95. Diese Zeile enthält den Code '@lru_cache'.
96. Diese Zeile enthält den Code 'def get_settings() -> Settings:'.
97. Diese Zeile enthält den Code 'return Settings()'.

## app/models.py

`$lang
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
22. Diese Zeile ist leer und trennt Abschnitte.
23. Diese Zeile enthält den Code 'class User(Base):'.
24. Diese Zeile enthält den Code '__tablename__ = "users"'.
25. Diese Zeile ist leer und trennt Abschnitte.
26. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
27. Diese Zeile enthält den Code 'user_uid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=lambda: st...'.
28. Diese Zeile enthält den Code 'email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)'.
29. Diese Zeile enthält den Code 'username: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, index=True)'.
30. Diese Zeile enthält den Code 'username_normalized: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, i...'.
31. Diese Zeile enthält den Code 'hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)'.
32. Diese Zeile enthält den Code 'role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)'.
33. Diese Zeile enthält den Code 'last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)'.
34. Diese Zeile enthält den Code 'last_login_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)'.
35. Diese Zeile enthält den Code 'last_login_user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)'.
36. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
37. Diese Zeile ist leer und trennt Abschnitte.
38. Diese Zeile enthält den Code 'recipes: Mapped[list["Recipe"]] = relationship(back_populates="creator", cascade="all, delete-orp...'.
39. Diese Zeile enthält den Code 'reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, delete-orphan")'.
40. Diese Zeile enthält den Code 'favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all, delete-or...'.
41. Diese Zeile enthält den Code 'submissions: Mapped[list["RecipeSubmission"]] = relationship('.
42. Diese Zeile enthält den Code 'back_populates="submitter_user",'.
43. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
44. Diese Zeile enthält den Code 'foreign_keys="RecipeSubmission.submitter_user_id",'.
45. Diese Zeile enthält den Code ')'.
46. Diese Zeile enthält den Code 'reviewed_submissions: Mapped[list["RecipeSubmission"]] = relationship('.
47. Diese Zeile enthält den Code 'back_populates="reviewed_by_admin",'.
48. Diese Zeile enthält den Code 'foreign_keys="RecipeSubmission.reviewed_by_admin_id",'.
49. Diese Zeile enthält den Code ')'.
50. Diese Zeile enthält den Code 'password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship('.
51. Diese Zeile enthält den Code 'back_populates="user",'.
52. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
53. Diese Zeile enthält den Code ')'.
54. Diese Zeile enthält den Code 'security_events: Mapped[list["SecurityEvent"]] = relationship('.
55. Diese Zeile enthält den Code 'back_populates="user",'.
56. Diese Zeile enthält den Code ')'.
57. Diese Zeile ist leer und trennt Abschnitte.
58. Diese Zeile ist leer und trennt Abschnitte.
59. Diese Zeile enthält den Code 'class Recipe(Base):'.
60. Diese Zeile enthält den Code '__tablename__ = "recipes"'.
61. Diese Zeile ist leer und trennt Abschnitte.
62. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
63. Diese Zeile enthält den Code 'title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)'.
64. Diese Zeile enthält den Code 'title_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
65. Diese Zeile enthält den Code 'source: Mapped[str] = mapped_column(String(50), nullable=False, default="user", index=True)'.
66. Diese Zeile enthält den Code 'source_uuid: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True, index=True)'.
67. Diese Zeile enthält den Code 'source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
68. Diese Zeile enthält den Code 'source_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
69. Diese Zeile enthält den Code 'servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)'.
70. Diese Zeile enthält den Code 'total_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
71. Diese Zeile enthält den Code 'is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)'.
72. Diese Zeile enthält den Code 'description: Mapped[str] = mapped_column(Text, nullable=False)'.
73. Diese Zeile enthält den Code 'instructions: Mapped[str] = mapped_column(Text, nullable=False)'.
74. Diese Zeile enthält den Code 'category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)'.
75. Diese Zeile enthält den Code 'prep_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, index=True)'.
76. Diese Zeile enthält den Code 'difficulty: Mapped[str] = mapped_column(String(30), nullable=False, index=True)'.
77. Diese Zeile enthält den Code 'creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=Fals...'.
78. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
79. Diese Zeile ist leer und trennt Abschnitte.
80. Diese Zeile enthält den Code 'creator: Mapped["User"] = relationship(back_populates="recipes")'.
81. Diese Zeile enthält den Code 'recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship('.
82. Diese Zeile enthält den Code 'back_populates="recipe",'.
83. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
84. Diese Zeile enthält den Code ')'.
85. Diese Zeile enthält den Code 'reviews: Mapped[list["Review"]] = relationship(back_populates="recipe", cascade="all, delete-orph...'.
86. Diese Zeile enthält den Code 'favorites: Mapped[list["Favorite"]] = relationship(back_populates="recipe", cascade="all, delete-...'.
87. Diese Zeile enthält den Code 'images: Mapped[list["RecipeImage"]] = relationship('.
88. Diese Zeile enthält den Code 'back_populates="recipe",'.
89. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
90. Diese Zeile enthält den Code 'order_by="RecipeImage.created_at",'.
91. Diese Zeile enthält den Code ')'.
92. Diese Zeile ist leer und trennt Abschnitte.
93. Diese Zeile ist leer und trennt Abschnitte.
94. Diese Zeile enthält den Code 'class Ingredient(Base):'.
95. Diese Zeile enthält den Code '__tablename__ = "ingredients"'.
96. Diese Zeile ist leer und trennt Abschnitte.
97. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
98. Diese Zeile enthält den Code 'name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)'.
99. Diese Zeile ist leer und trennt Abschnitte.
100. Diese Zeile enthält den Code 'recipe_links: Mapped[list["RecipeIngredient"]] = relationship('.
101. Diese Zeile enthält den Code 'back_populates="ingredient",'.
102. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
103. Diese Zeile enthält den Code ')'.
104. Diese Zeile ist leer und trennt Abschnitte.
105. Diese Zeile ist leer und trennt Abschnitte.
106. Diese Zeile enthält den Code 'class RecipeIngredient(Base):'.
107. Diese Zeile enthält den Code '__tablename__ = "recipe_ingredients"'.
108. Diese Zeile ist leer und trennt Abschnitte.
109. Diese Zeile enthält den Code 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=...'.
110. Diese Zeile enthält den Code 'ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCADE"), prim...'.
111. Diese Zeile enthält den Code 'quantity_text: Mapped[str] = mapped_column(String(120), default="", nullable=False)'.
112. Diese Zeile enthält den Code 'grams: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
113. Diese Zeile ist leer und trennt Abschnitte.
114. Diese Zeile enthält den Code 'recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")'.
115. Diese Zeile enthält den Code 'ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_links")'.
116. Diese Zeile ist leer und trennt Abschnitte.
117. Diese Zeile ist leer und trennt Abschnitte.
118. Diese Zeile enthält den Code 'class Review(Base):'.
119. Diese Zeile enthält den Code '__tablename__ = "reviews"'.
120. Diese Zeile enthält den Code '__table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_reviews_user_recipe"),)'.
121. Diese Zeile ist leer und trennt Abschnitte.
122. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
123. Diese Zeile enthält den Code 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=Fal...'.
124. Diese Zeile enthält den Code 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, ...'.
125. Diese Zeile enthält den Code 'rating: Mapped[int] = mapped_column(Integer, nullable=False)'.
126. Diese Zeile enthält den Code 'comment: Mapped[str] = mapped_column(Text, default="", nullable=False)'.
127. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
128. Diese Zeile ist leer und trennt Abschnitte.
129. Diese Zeile enthält den Code 'recipe: Mapped["Recipe"] = relationship(back_populates="reviews")'.
130. Diese Zeile enthält den Code 'user: Mapped["User"] = relationship(back_populates="reviews")'.
131. Diese Zeile ist leer und trennt Abschnitte.
132. Diese Zeile ist leer und trennt Abschnitte.
133. Diese Zeile enthält den Code 'class Favorite(Base):'.
134. Diese Zeile enthält den Code '__tablename__ = "favorites"'.
135. Diese Zeile enthält den Code '__table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_recipe"),)'.
136. Diese Zeile ist leer und trennt Abschnitte.
137. Diese Zeile enthält den Code 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)'.
138. Diese Zeile enthält den Code 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), primary_key=...'.
139. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
140. Diese Zeile ist leer und trennt Abschnitte.
141. Diese Zeile enthält den Code 'user: Mapped["User"] = relationship(back_populates="favorites")'.
142. Diese Zeile enthält den Code 'recipe: Mapped["Recipe"] = relationship(back_populates="favorites")'.
143. Diese Zeile ist leer und trennt Abschnitte.
144. Diese Zeile ist leer und trennt Abschnitte.
145. Diese Zeile enthält den Code 'class RecipeImage(Base):'.
146. Diese Zeile enthält den Code '__tablename__ = "recipe_images"'.
147. Diese Zeile ist leer und trennt Abschnitte.
148. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
149. Diese Zeile enthält den Code 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nullable=Fal...'.
150. Diese Zeile enthält den Code 'filename: Mapped[str] = mapped_column(String(255), nullable=False)'.
151. Diese Zeile enthält den Code 'content_type: Mapped[str] = mapped_column(String(50), nullable=False)'.
152. Diese Zeile enthält den Code 'data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)'.
153. Diese Zeile enthält den Code 'is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)'.
154. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
155. Diese Zeile ist leer und trennt Abschnitte.
156. Diese Zeile enthält den Code 'recipe: Mapped["Recipe"] = relationship(back_populates="images")'.
157. Diese Zeile ist leer und trennt Abschnitte.
158. Diese Zeile ist leer und trennt Abschnitte.
159. Diese Zeile enthält den Code 'class RecipeSubmission(Base):'.
160. Diese Zeile enthält den Code '__tablename__ = "recipe_submissions"'.
161. Diese Zeile ist leer und trennt Abschnitte.
162. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
163. Diese Zeile enthält den Code 'submitter_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL")...'.
164. Diese Zeile enthält den Code 'submitter_email: Mapped[str | None] = mapped_column(String(255), nullable=True)'.
165. Diese Zeile enthält den Code 'title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)'.
166. Diese Zeile enthält den Code 'description: Mapped[str] = mapped_column(Text, nullable=False)'.
167. Diese Zeile enthält den Code 'category: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)'.
168. Diese Zeile enthält den Code 'difficulty: Mapped[str] = mapped_column(String(30), nullable=False, default="medium", index=True)'.
169. Diese Zeile enthält den Code 'prep_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
170. Diese Zeile enthält den Code 'servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)'.
171. Diese Zeile enthält den Code 'instructions: Mapped[str] = mapped_column(Text, nullable=False)'.
172. Diese Zeile enthält den Code 'status: Mapped[str] = mapped_column(SUBMISSION_STATUS_ENUM, nullable=False, default="pending", se...'.
173. Diese Zeile enthält den Code 'admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)'.
174. Diese Zeile enthält den Code 'reviewed_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NUL...'.
175. Diese Zeile enthält den Code 'reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)'.
176. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
177. Diese Zeile ist leer und trennt Abschnitte.
178. Diese Zeile enthält den Code 'submitter_user: Mapped["User"] = relationship('.
179. Diese Zeile enthält den Code 'back_populates="submissions",'.
180. Diese Zeile enthält den Code 'foreign_keys=[submitter_user_id],'.
181. Diese Zeile enthält den Code ')'.
182. Diese Zeile enthält den Code 'reviewed_by_admin: Mapped["User"] = relationship('.
183. Diese Zeile enthält den Code 'back_populates="reviewed_submissions",'.
184. Diese Zeile enthält den Code 'foreign_keys=[reviewed_by_admin_id],'.
185. Diese Zeile enthält den Code ')'.
186. Diese Zeile enthält den Code 'ingredients: Mapped[list["SubmissionIngredient"]] = relationship('.
187. Diese Zeile enthält den Code 'back_populates="submission",'.
188. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
189. Diese Zeile enthält den Code 'order_by="SubmissionIngredient.id",'.
190. Diese Zeile enthält den Code ')'.
191. Diese Zeile enthält den Code 'images: Mapped[list["SubmissionImage"]] = relationship('.
192. Diese Zeile enthält den Code 'back_populates="submission",'.
193. Diese Zeile enthält den Code 'cascade="all, delete-orphan",'.
194. Diese Zeile enthält den Code 'order_by="SubmissionImage.created_at",'.
195. Diese Zeile enthält den Code ')'.
196. Diese Zeile ist leer und trennt Abschnitte.
197. Diese Zeile ist leer und trennt Abschnitte.
198. Diese Zeile enthält den Code 'class SubmissionIngredient(Base):'.
199. Diese Zeile enthält den Code '__tablename__ = "submission_ingredients"'.
200. Diese Zeile ist leer und trennt Abschnitte.
201. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
202. Diese Zeile enthält den Code 'submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete="CASCADE"...'.
203. Diese Zeile enthält den Code 'ingredient_name: Mapped[str] = mapped_column(String(200), nullable=False)'.
204. Diese Zeile enthält den Code 'quantity_text: Mapped[str] = mapped_column(String(120), nullable=False, default="")'.
205. Diese Zeile enthält den Code 'grams: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
206. Diese Zeile enthält den Code 'ingredient_name_normalized: Mapped[str | None] = mapped_column(String(200), nullable=True, index=...'.
207. Diese Zeile ist leer und trennt Abschnitte.
208. Diese Zeile enthält den Code 'submission: Mapped["RecipeSubmission"] = relationship(back_populates="ingredients")'.
209. Diese Zeile ist leer und trennt Abschnitte.
210. Diese Zeile ist leer und trennt Abschnitte.
211. Diese Zeile enthält den Code 'class SubmissionImage(Base):'.
212. Diese Zeile enthält den Code '__tablename__ = "submission_images"'.
213. Diese Zeile ist leer und trennt Abschnitte.
214. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
215. Diese Zeile enthält den Code 'submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete="CASCADE"...'.
216. Diese Zeile enthält den Code 'filename: Mapped[str] = mapped_column(String(255), nullable=False)'.
217. Diese Zeile enthält den Code 'content_type: Mapped[str] = mapped_column(String(50), nullable=False)'.
218. Diese Zeile enthält den Code 'data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)'.
219. Diese Zeile enthält den Code 'is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)'.
220. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
221. Diese Zeile ist leer und trennt Abschnitte.
222. Diese Zeile enthält den Code 'submission: Mapped["RecipeSubmission"] = relationship(back_populates="images")'.
223. Diese Zeile ist leer und trennt Abschnitte.
224. Diese Zeile ist leer und trennt Abschnitte.
225. Diese Zeile enthält den Code 'class AppMeta(Base):'.
226. Diese Zeile enthält den Code '__tablename__ = "app_meta"'.
227. Diese Zeile ist leer und trennt Abschnitte.
228. Diese Zeile enthält den Code 'key: Mapped[str] = mapped_column(String(120), primary_key=True)'.
229. Diese Zeile enthält den Code 'value: Mapped[str] = mapped_column(Text, nullable=False)'.
230. Diese Zeile ist leer und trennt Abschnitte.
231. Diese Zeile ist leer und trennt Abschnitte.
232. Diese Zeile enthält den Code 'class PasswordResetToken(Base):'.
233. Diese Zeile enthält den Code '__tablename__ = "password_reset_tokens"'.
234. Diese Zeile ist leer und trennt Abschnitte.
235. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
236. Diese Zeile enthält den Code 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, ...'.
237. Diese Zeile enthält den Code 'new_email_normalized: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)'.
238. Diese Zeile enthält den Code 'token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)'.
239. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
240. Diese Zeile enthält den Code 'expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)'.
241. Diese Zeile enthält den Code 'used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, index=True)'.
242. Diese Zeile enthält den Code 'created_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)'.
243. Diese Zeile enthält den Code 'created_user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)'.
244. Diese Zeile enthält den Code 'purpose: Mapped[str] = mapped_column(String(50), nullable=False, default="password_reset", index=...'.
245. Diese Zeile ist leer und trennt Abschnitte.
246. Diese Zeile enthält den Code 'user: Mapped["User"] = relationship(back_populates="password_reset_tokens")'.
247. Diese Zeile ist leer und trennt Abschnitte.
248. Diese Zeile ist leer und trennt Abschnitte.
249. Diese Zeile enthält den Code 'class SecurityEvent(Base):'.
250. Diese Zeile enthält den Code '__tablename__ = "security_events"'.
251. Diese Zeile ist leer und trennt Abschnitte.
252. Diese Zeile enthält den Code 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
253. Diese Zeile enthält den Code 'user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable...'.
254. Diese Zeile enthält den Code 'event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)'.
255. Diese Zeile enthält den Code 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=F...'.
256. Diese Zeile enthält den Code 'ip: Mapped[str | None] = mapped_column(String(64), nullable=True)'.
257. Diese Zeile enthält den Code 'user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)'.
258. Diese Zeile enthält den Code 'details: Mapped[str | None] = mapped_column(String(300), nullable=True)'.
259. Diese Zeile ist leer und trennt Abschnitte.
260. Diese Zeile enthält den Code 'user: Mapped["User"] = relationship(back_populates="security_events")'.

## app/mailer.py

`$lang
import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path

from app.config import Settings, get_settings

logger = logging.getLogger("mealmate.mailer")


@dataclass
class MailPayload:
    to_email: str
    subject: str
    body: str
    outbox_file: str | None = None


class BaseMailer:
    def send(self, payload: MailPayload) -> None:
        raise NotImplementedError


class OutboxMailer(BaseMailer):
    def __init__(self, settings: Settings):
        self.settings = settings

    def send(self, payload: MailPayload) -> None:
        outbox_file = Path(payload.outbox_file or self.settings.mail_outbox_path)
        outbox_file.parent.mkdir(parents=True, exist_ok=True)
        with outbox_file.open("a", encoding="utf-8") as handle:
            handle.write(f"TO: {payload.to_email}\n")
            handle.write(f"SUBJECT: {payload.subject}\n")
            handle.write(f"BODY: {payload.body}\n")
            handle.write("---\n")
        logger.info("mail_written_to_outbox to=%s path=%s", payload.to_email, outbox_file)


class SMTPMailer(BaseMailer):
    def __init__(self, settings: Settings):
        self.settings = settings

    def send(self, payload: MailPayload) -> None:
        if not self.settings.smtp_host:
            raise RuntimeError("SMTP host is not configured")
        msg = EmailMessage()
        msg["From"] = self.settings.smtp_from
        msg["To"] = payload.to_email
        msg["Subject"] = payload.subject
        msg.set_content(payload.body)
        with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as server:
            server.starttls()
            if self.settings.smtp_user and self.settings.smtp_password:
                server.login(self.settings.smtp_user, self.settings.smtp_password)
            server.send_message(msg)
        logger.info("mail_sent_via_smtp to=%s", payload.to_email)


def get_mailer(settings: Settings | None = None) -> BaseMailer:
    resolved = settings or get_settings()
    if resolved.prod_mode:
        return SMTPMailer(resolved)
    return OutboxMailer(resolved)

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'import logging'.
2. Diese Zeile enthält den Code 'import smtplib'.
3. Diese Zeile enthält den Code 'from dataclasses import dataclass'.
4. Diese Zeile enthält den Code 'from email.message import EmailMessage'.
5. Diese Zeile enthält den Code 'from pathlib import Path'.
6. Diese Zeile ist leer und trennt Abschnitte.
7. Diese Zeile enthält den Code 'from app.config import Settings, get_settings'.
8. Diese Zeile ist leer und trennt Abschnitte.
9. Diese Zeile enthält den Code 'logger = logging.getLogger("mealmate.mailer")'.
10. Diese Zeile ist leer und trennt Abschnitte.
11. Diese Zeile ist leer und trennt Abschnitte.
12. Diese Zeile enthält den Code '@dataclass'.
13. Diese Zeile enthält den Code 'class MailPayload:'.
14. Diese Zeile enthält den Code 'to_email: str'.
15. Diese Zeile enthält den Code 'subject: str'.
16. Diese Zeile enthält den Code 'body: str'.
17. Diese Zeile enthält den Code 'outbox_file: str | None = None'.
18. Diese Zeile ist leer und trennt Abschnitte.
19. Diese Zeile ist leer und trennt Abschnitte.
20. Diese Zeile enthält den Code 'class BaseMailer:'.
21. Diese Zeile enthält den Code 'def send(self, payload: MailPayload) -> None:'.
22. Diese Zeile enthält den Code 'raise NotImplementedError'.
23. Diese Zeile ist leer und trennt Abschnitte.
24. Diese Zeile ist leer und trennt Abschnitte.
25. Diese Zeile enthält den Code 'class OutboxMailer(BaseMailer):'.
26. Diese Zeile enthält den Code 'def __init__(self, settings: Settings):'.
27. Diese Zeile enthält den Code 'self.settings = settings'.
28. Diese Zeile ist leer und trennt Abschnitte.
29. Diese Zeile enthält den Code 'def send(self, payload: MailPayload) -> None:'.
30. Diese Zeile enthält den Code 'outbox_file = Path(payload.outbox_file or self.settings.mail_outbox_path)'.
31. Diese Zeile enthält den Code 'outbox_file.parent.mkdir(parents=True, exist_ok=True)'.
32. Diese Zeile enthält den Code 'with outbox_file.open("a", encoding="utf-8") as handle:'.
33. Diese Zeile enthält den Code 'handle.write(f"TO: {payload.to_email}\n")'.
34. Diese Zeile enthält den Code 'handle.write(f"SUBJECT: {payload.subject}\n")'.
35. Diese Zeile enthält den Code 'handle.write(f"BODY: {payload.body}\n")'.
36. Diese Zeile enthält den Code 'handle.write("---\n")'.
37. Diese Zeile enthält den Code 'logger.info("mail_written_to_outbox to=%s path=%s", payload.to_email, outbox_file)'.
38. Diese Zeile ist leer und trennt Abschnitte.
39. Diese Zeile ist leer und trennt Abschnitte.
40. Diese Zeile enthält den Code 'class SMTPMailer(BaseMailer):'.
41. Diese Zeile enthält den Code 'def __init__(self, settings: Settings):'.
42. Diese Zeile enthält den Code 'self.settings = settings'.
43. Diese Zeile ist leer und trennt Abschnitte.
44. Diese Zeile enthält den Code 'def send(self, payload: MailPayload) -> None:'.
45. Diese Zeile enthält den Code 'if not self.settings.smtp_host:'.
46. Diese Zeile enthält den Code 'raise RuntimeError("SMTP host is not configured")'.
47. Diese Zeile enthält den Code 'msg = EmailMessage()'.
48. Diese Zeile enthält den Code 'msg["From"] = self.settings.smtp_from'.
49. Diese Zeile enthält den Code 'msg["To"] = payload.to_email'.
50. Diese Zeile enthält den Code 'msg["Subject"] = payload.subject'.
51. Diese Zeile enthält den Code 'msg.set_content(payload.body)'.
52. Diese Zeile enthält den Code 'with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as server:'.
53. Diese Zeile enthält den Code 'server.starttls()'.
54. Diese Zeile enthält den Code 'if self.settings.smtp_user and self.settings.smtp_password:'.
55. Diese Zeile enthält den Code 'server.login(self.settings.smtp_user, self.settings.smtp_password)'.
56. Diese Zeile enthält den Code 'server.send_message(msg)'.
57. Diese Zeile enthält den Code 'logger.info("mail_sent_via_smtp to=%s", payload.to_email)'.
58. Diese Zeile ist leer und trennt Abschnitte.
59. Diese Zeile ist leer und trennt Abschnitte.
60. Diese Zeile enthält den Code 'def get_mailer(settings: Settings | None = None) -> BaseMailer:'.
61. Diese Zeile enthält den Code 'resolved = settings or get_settings()'.
62. Diese Zeile enthält den Code 'if resolved.prod_mode:'.
63. Diese Zeile enthält den Code 'return SMTPMailer(resolved)'.
64. Diese Zeile enthält den Code 'return OutboxMailer(resolved)'.

## app/routers/auth.py

`$lang
from datetime import datetime, timedelta, timezone
import logging
import re

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, template_context
from app.i18n import t
from app.mailer import MailPayload, get_mailer
from app.models import PasswordResetToken, User
from app.rate_limit import key_by_ip, key_by_user_or_ip, limiter
from app.security import (
    create_access_token,
    create_raw_reset_token,
    hash_password,
    hash_reset_token,
    normalize_username,
    validate_password_policy,
    validate_username_policy,
    verify_password,
)
from app.security_events import log_security_event
from app.views import redirect, templates

router = APIRouter(tags=["auth"])
settings = get_settings()
logger = logging.getLogger("mealmate.auth")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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


def _identifier_type(identifier: str) -> str:
    return "email" if "@" in identifier else "username"


def _find_user_by_identifier(db: Session, identifier: str) -> User | None:
    cleaned = identifier.strip()
    if not cleaned:
        return None
    if "@" in cleaned:
        return db.scalar(select(User).where(User.email == cleaned.lower()))
    return db.scalar(select(User).where(User.username_normalized == normalize_username(cleaned)))


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(value))


def _find_valid_token(
    db: Session,
    raw_token: str,
    *,
    purpose: str,
) -> PasswordResetToken | None:
    now = datetime.now(timezone.utc)
    return db.scalar(
        select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token_hash == hash_reset_token(raw_token),
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
                PasswordResetToken.purpose == purpose,
            )
        )
    )


def _reset_token_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_token_minutes)


def _render_me(
    request: Request,
    current_user: User,
    message: str | None = None,
    error: str | None = None,
    status_code: int = status.HTTP_200_OK,
):
    return templates.TemplateResponse(
        "me.html",
        template_context(
            request,
            current_user,
            user=current_user,
            message=message,
            error=error,
        ),
        status_code=status_code,
    )


@router.get("/login")
@router.get("/auth/login")
def login_page(
    request: Request,
    message: str = "",
    current_user: User | None = Depends(get_current_user_optional),
):
    if current_user:
        return redirect("/")
    message_map = {
        "reset_done": t("auth.reset_success", request=request),
        "password_changed": t("auth.password_changed_success", request=request),
    }
    return templates.TemplateResponse(
        "auth_login.html",
        template_context(
            request,
            current_user,
            error=None,
            message=message_map.get(message, ""),
            identifier_value="",
        ),
    )


@router.post("/login")
@router.post("/auth/login")
@limiter.limit("5/minute", key_func=key_by_ip)
def login_submit(
    request: Request,
    response: Response,
    identifier: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = response
    user = _find_user_by_identifier(db, identifier)
    id_type = _identifier_type(identifier)
    if not user or not verify_password(password, user.hashed_password):
        log_security_event(
            db,
            request,
            event_type="login_failed",
            user_id=user.id if user else None,
            details=f"identifier={id_type}",
        )
        db.commit()
        return templates.TemplateResponse(
            "auth_login.html",
            template_context(
                request,
                None,
                error=t("error.invalid_credentials", request=request),
                message="",
                identifier_value=identifier,
            ),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    user.last_login_at = datetime.now(timezone.utc)
    user.last_login_ip = request.client.host[:64] if request.client and request.client.host else None
    user.last_login_user_agent = (request.headers.get("user-agent") or "")[:200] or None
    db.add(user)
    log_security_event(db, request, event_type="login_success", user_id=user.id, details=f"identifier={id_type}")
    db.commit()
    token = create_access_token(user.user_uid, user.role)
    response = redirect("/")
    set_auth_cookie(response, token)
    return response


@router.get("/register")
@router.get("/auth/register")
def register_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        return redirect("/")
    return templates.TemplateResponse(
        "auth_register.html",
        template_context(request, current_user, error=None, username_value=""),
    )


@router.post("/register")
@router.post("/auth/register")
@limiter.limit("3/minute", key_func=key_by_ip)
def register_submit(
    request: Request,
    response: Response,
    email: str = Form(...),
    username: str = Form(""),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = response
    normalized_email = email.strip().lower()
    username_value = username.strip()
    normalized_username = normalize_username(username_value) if username_value else None
    password_error = validate_password_policy(password)
    if password_error:
        return templates.TemplateResponse(
            "auth_register.html",
            template_context(request, None, error=password_error, username_value=username_value),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if username_value:
        username_error = validate_username_policy(username_value)
        if username_error:
            return templates.TemplateResponse(
                "auth_register.html",
                template_context(request, None, error=username_error, username_value=username_value),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    existing = db.scalar(select(User).where(User.email == normalized_email))
    if existing:
        return templates.TemplateResponse(
            "auth_register.html",
            template_context(request, None, error=t("error.email_registered", request=request), username_value=username_value),
            status_code=status.HTTP_409_CONFLICT,
        )
    if normalized_username:
        same_username = db.scalar(select(User).where(User.username_normalized == normalized_username))
        if same_username:
            return templates.TemplateResponse(
                "auth_register.html",
                template_context(request, None, error=t("error.username_taken", request=request), username_value=username_value),
                status_code=status.HTTP_409_CONFLICT,
            )
    user = User(
        email=normalized_email,
        username=username_value or None,
        username_normalized=normalized_username,
        hashed_password=hash_password(password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.user_uid, user.role)
    response = redirect("/")
    set_auth_cookie(response, token)
    return response


@router.post("/logout")
def logout():
    response = redirect("/")
    response.delete_cookie("access_token", path="/")
    return response


@router.get("/auth/forgot-password")
@router.get("/forgot-password")
def forgot_password_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "auth_forgot_password.html",
        template_context(request, current_user, error=None, message=None, identifier_value=""),
    )


@router.post("/auth/forgot-password")
@router.post("/forgot-password")
@limiter.limit("5/minute", key_func=key_by_ip)
def forgot_password_submit(
    request: Request,
    response: Response,
    identifier: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = response
    generic_message = t("auth.forgot_generic_response", request=request)
    user = _find_user_by_identifier(db, identifier)
    if user:
        raw_token = create_raw_reset_token()
        token_hash = hash_reset_token(raw_token)
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=_reset_token_expires_at(),
                created_ip=request.client.host[:64] if request.client and request.client.host else None,
                created_user_agent=(request.headers.get("user-agent") or "")[:200] or None,
                purpose="password_reset",
            )
        )
        log_security_event(db, request, event_type="pwd_reset_requested", user_id=user.id, details="identifier=known")
        db.commit()
        reset_link = f"{str(settings.app_url).rstrip('/')}/auth/reset-password?token={raw_token}"
        mailer = get_mailer(settings)
        subject = t("auth.reset_email_subject", request=request)
        body = t("auth.reset_email_body", request=request, reset_link=reset_link)
        try:
            mailer.send(MailPayload(to_email=user.email, subject=subject, body=body))
        except Exception:
            # We keep the response generic and avoid leaking whether delivery worked.
            logger.warning("password_reset_mail_send_failed user_id=%s", user.id)
    else:
        log_security_event(db, request, event_type="pwd_reset_requested", user_id=None, details="identifier=unknown")
        db.commit()
    return templates.TemplateResponse(
        "auth_forgot_password.html",
        template_context(
            request,
            None,
            error=None,
            message=generic_message,
            identifier_value="",
        ),
    )


@router.get("/auth/reset-password")
def reset_password_page(
    request: Request,
    token: str = "",
    current_user: User | None = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "auth_reset_password.html",
        template_context(
            request,
            current_user,
            token_value=token,
            error=None,
            message=None,
        ),
    )


@router.post("/auth/reset-password")
@limiter.limit("5/minute", key_func=key_by_ip)
def reset_password_submit(
    request: Request,
    response: Response,
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = response
    token_value = token.strip()
    if not token_value:
        return templates.TemplateResponse(
            "auth_reset_password.html",
            template_context(request, None, token_value="", error=t("error.reset_token_invalid", request=request), message=None),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "auth_reset_password.html",
            template_context(
                request,
                None,
                token_value=token_value,
                error=t("error.password_confirm_mismatch", request=request),
                message=None,
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    password_error = validate_password_policy(new_password)
    if password_error:
        return templates.TemplateResponse(
            "auth_reset_password.html",
            template_context(request, None, token_value=token_value, error=password_error, message=None),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    now = datetime.now(timezone.utc)
    reset_token = _find_valid_token(db, token_value, purpose="password_reset")
    if not reset_token:
        return templates.TemplateResponse(
            "auth_reset_password.html",
            template_context(request, None, token_value="", error=t("error.reset_token_invalid", request=request), message=None),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    user = db.scalar(select(User).where(User.id == reset_token.user_id))
    if not user:
        return templates.TemplateResponse(
            "auth_reset_password.html",
            template_context(request, None, token_value="", error=t("error.reset_token_invalid", request=request), message=None),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    user.hashed_password = hash_password(new_password)
    reset_token.used_at = now
    other_tokens = db.scalars(
        select(PasswordResetToken).where(
            and_(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.id != reset_token.id,
                PasswordResetToken.purpose == "password_reset",
            )
        )
    ).all()
    for item in other_tokens:
        item.used_at = now
    db.add(user)
    log_security_event(db, request, event_type="pwd_reset_done", user_id=user.id, details="token=single-use")
    db.commit()
    return redirect("/login?message=reset_done")


@router.post("/auth/change-password")
@limiter.limit("3/minute", key_func=key_by_user_or_ip)
def change_password_submit(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(old_password, current_user.hashed_password):
        return _render_me(
            request,
            current_user,
            error=t("error.password_old_invalid", request=request),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if new_password != confirm_password:
        return _render_me(
            request,
            current_user,
            error=t("error.password_confirm_mismatch", request=request),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    password_error = validate_password_policy(new_password)
    if password_error:
        return _render_me(
            request,
            current_user,
            error=password_error,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    current_user.hashed_password = hash_password(new_password)
    db.add(current_user)
    log_security_event(db, request, event_type="pwd_changed", user_id=current_user.id, details="changed_via_profile")
    db.commit()
    response = redirect("/me?message=password_changed")
    set_auth_cookie(response, create_access_token(current_user.user_uid, current_user.role))
    return response


@router.post("/profile/username")
@limiter.limit("5/minute", key_func=key_by_user_or_ip)
def update_username_submit(
    request: Request,
    username: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    username_value = username.strip()
    username_error = validate_username_policy(username_value)
    if username_error:
        return _render_me(request, current_user, error=username_error, status_code=status.HTTP_400_BAD_REQUEST)
    normalized_username = normalize_username(username_value)
    existing = db.scalar(
        select(User).where(
            and_(
                User.username_normalized == normalized_username,
                User.id != current_user.id,
            )
        )
    )
    if existing:
        return _render_me(
            request,
            current_user,
            error=t("error.username_taken", request=request),
            status_code=status.HTTP_409_CONFLICT,
        )
    current_user.username = username_value
    current_user.username_normalized = normalized_username
    db.add(current_user)
    log_security_event(db, request, event_type="username_changed", user_id=current_user.id, details="profile_update")
    db.commit()
    return redirect("/me?message=username_updated")


@router.get("/auth/change-email")
def change_email_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "auth_change_email.html",
        template_context(
            request,
            current_user,
            current_email=current_user.email,
            new_email_value="",
            message=None,
            error=None,
        ),
    )


@router.post("/auth/change-email/request")
@limiter.limit("5/minute", key_func=key_by_ip)
@limiter.limit("3/minute", key_func=key_by_user_or_ip)
def change_email_request_submit(
    request: Request,
    new_email: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    normalized_new_email = _normalize_email(new_email)
    if not _is_valid_email(normalized_new_email):
        return templates.TemplateResponse(
            "auth_change_email.html",
            template_context(
                request,
                current_user,
                current_email=current_user.email,
                new_email_value=new_email,
                message=None,
                error=t("error.email_invalid", request=request),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if normalized_new_email == current_user.email:
        return templates.TemplateResponse(
            "auth_change_email.html",
            template_context(
                request,
                current_user,
                current_email=current_user.email,
                new_email_value="",
                message=t("auth.email_change_same_email", request=request),
                error=None,
            ),
        )
    existing = db.scalar(select(User).where(and_(User.email == normalized_new_email, User.id != current_user.id)))
    if existing:
        return templates.TemplateResponse(
            "auth_change_email.html",
            template_context(
                request,
                current_user,
                current_email=current_user.email,
                new_email_value=new_email,
                message=None,
                error=t("error.email_unavailable", request=request),
            ),
            status_code=status.HTTP_409_CONFLICT,
        )
    now = datetime.now(timezone.utc)
    open_tokens = db.scalars(
        select(PasswordResetToken).where(
            and_(
                PasswordResetToken.user_id == current_user.id,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.purpose == "email_change",
            )
        )
    ).all()
    for open_token in open_tokens:
        open_token.used_at = now
    raw_token = create_raw_reset_token()
    db.add(
        PasswordResetToken(
            user_id=current_user.id,
            token_hash=hash_reset_token(raw_token),
            new_email_normalized=normalized_new_email,
            expires_at=_reset_token_expires_at(),
            created_ip=request.client.host[:64] if request.client and request.client.host else None,
            created_user_agent=(request.headers.get("user-agent") or "")[:200] or None,
            purpose="email_change",
        )
    )
    log_security_event(
        db,
        request,
        event_type="email_change_requested",
        user_id=current_user.id,
        details="delivery=new_email",
    )
    db.commit()
    confirmation_link = f"{str(settings.app_url).rstrip('/')}/auth/change-email/confirm?token={raw_token}"
    try:
        get_mailer(settings).send(
            MailPayload(
                to_email=normalized_new_email,
                subject=t("auth.email_change_subject", request=request),
                body=t("auth.email_change_body", request=request, confirm_link=confirmation_link),
                outbox_file=settings.mail_outbox_email_change_path,
            )
        )
    except Exception:
        logger.warning("email_change_mail_send_failed user_uid=%s", current_user.user_uid)
    return templates.TemplateResponse(
        "auth_change_email.html",
        template_context(
            request,
            current_user,
            current_email=current_user.email,
            new_email_value="",
            message=t("auth.email_change_requested", request=request),
            error=None,
        ),
    )


@router.get("/auth/change-email/confirm")
def change_email_confirm_page(
    request: Request,
    token: str = "",
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    token_value = token.strip()
    record = _find_valid_token(db, token_value, purpose="email_change") if token_value else None
    if not record or not record.new_email_normalized:
        return templates.TemplateResponse(
            "auth_change_email_confirm.html",
            template_context(
                request,
                current_user,
                token_value="",
                is_valid=False,
                new_email_value="",
                message=None,
                error=t("error.email_change_token_invalid", request=request),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return templates.TemplateResponse(
        "auth_change_email_confirm.html",
        template_context(
            request,
            current_user,
            token_value=token_value,
            is_valid=True,
            new_email_value=record.new_email_normalized,
            message=None,
            error=None,
        ),
    )


@router.post("/auth/change-email/confirm")
@limiter.limit("5/minute", key_func=key_by_ip)
def change_email_confirm_submit(
    request: Request,
    token: str = Form(...),
    db: Session = Depends(get_db),
):
    token_value = token.strip()
    record = _find_valid_token(db, token_value, purpose="email_change") if token_value else None
    if not record or not record.new_email_normalized:
        return templates.TemplateResponse(
            "auth_change_email_confirm.html",
            template_context(
                request,
                None,
                token_value="",
                is_valid=False,
                new_email_value="",
                message=None,
                error=t("error.email_change_token_invalid", request=request),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    user = db.scalar(select(User).where(User.id == record.user_id))
    if not user:
        record.used_at = datetime.now(timezone.utc)
        db.add(record)
        db.commit()
        return templates.TemplateResponse(
            "auth_change_email_confirm.html",
            template_context(
                request,
                None,
                token_value="",
                is_valid=False,
                new_email_value="",
                message=None,
                error=t("error.email_change_token_invalid", request=request),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    conflict = db.scalar(select(User).where(and_(User.email == record.new_email_normalized, User.id != user.id)))
    if conflict:
        return templates.TemplateResponse(
            "auth_change_email_confirm.html",
            template_context(
                request,
                None,
                token_value="",
                is_valid=False,
                new_email_value="",
                message=None,
                error=t("error.email_unavailable", request=request),
            ),
            status_code=status.HTTP_409_CONFLICT,
        )
    user.email = record.new_email_normalized
    record.used_at = datetime.now(timezone.utc)
    db.add(user)
    log_security_event(db, request, event_type="email_change_completed", user_id=user.id, details="confirmed")
    db.commit()
    response = redirect("/me?message=email_changed")
    set_auth_cookie(response, create_access_token(user.user_uid, user.role))
    return response


@router.get("/me")
def me_page(
    request: Request,
    message: str = "",
    current_user: User = Depends(get_current_user),
):
    message_map = {
        "username_updated": t("profile.username_updated", request=request),
        "password_changed": t("auth.password_changed_success", request=request),
        "email_changed": t("auth.email_change_success", request=request),
    }
    return _render_me(request, current_user, message=message_map.get(message, ""))


@router.get("/api/me")
def me_api(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "user_uid": current_user.user_uid,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat(),
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
    }


@router.get("/admin-only")
def admin_only(request: Request, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required", request=request))
    return {"message": t("role.admin", request=request)}

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'from datetime import datetime, timedelta, timezone'.
2. Diese Zeile enthält den Code 'import logging'.
3. Diese Zeile enthält den Code 'import re'.
4. Diese Zeile ist leer und trennt Abschnitte.
5. Diese Zeile enthält den Code 'from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status'.
6. Diese Zeile enthält den Code 'from sqlalchemy import and_, select'.
7. Diese Zeile enthält den Code 'from sqlalchemy.orm import Session'.
8. Diese Zeile ist leer und trennt Abschnitte.
9. Diese Zeile enthält den Code 'from app.config import get_settings'.
10. Diese Zeile enthält den Code 'from app.database import get_db'.
11. Diese Zeile enthält den Code 'from app.dependencies import get_current_user, get_current_user_optional, template_context'.
12. Diese Zeile enthält den Code 'from app.i18n import t'.
13. Diese Zeile enthält den Code 'from app.mailer import MailPayload, get_mailer'.
14. Diese Zeile enthält den Code 'from app.models import PasswordResetToken, User'.
15. Diese Zeile enthält den Code 'from app.rate_limit import key_by_ip, key_by_user_or_ip, limiter'.
16. Diese Zeile enthält den Code 'from app.security import ('.
17. Diese Zeile enthält den Code 'create_access_token,'.
18. Diese Zeile enthält den Code 'create_raw_reset_token,'.
19. Diese Zeile enthält den Code 'hash_password,'.
20. Diese Zeile enthält den Code 'hash_reset_token,'.
21. Diese Zeile enthält den Code 'normalize_username,'.
22. Diese Zeile enthält den Code 'validate_password_policy,'.
23. Diese Zeile enthält den Code 'validate_username_policy,'.
24. Diese Zeile enthält den Code 'verify_password,'.
25. Diese Zeile enthält den Code ')'.
26. Diese Zeile enthält den Code 'from app.security_events import log_security_event'.
27. Diese Zeile enthält den Code 'from app.views import redirect, templates'.
28. Diese Zeile ist leer und trennt Abschnitte.
29. Diese Zeile enthält den Code 'router = APIRouter(tags=["auth"])'.
30. Diese Zeile enthält den Code 'settings = get_settings()'.
31. Diese Zeile enthält den Code 'logger = logging.getLogger("mealmate.auth")'.
32. Diese Zeile enthält den Code 'EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")'.
33. Diese Zeile ist leer und trennt Abschnitte.
34. Diese Zeile ist leer und trennt Abschnitte.
35. Diese Zeile enthält den Code 'def set_auth_cookie(response, token: str) -> None:'.
36. Diese Zeile enthält den Code 'response.set_cookie('.
37. Diese Zeile enthält den Code 'key="access_token",'.
38. Diese Zeile enthält den Code 'value=f"Bearer {token}",'.
39. Diese Zeile enthält den Code 'httponly=True,'.
40. Diese Zeile enthält den Code 'secure=settings.resolved_cookie_secure,'.
41. Diese Zeile enthält den Code 'samesite="lax",'.
42. Diese Zeile enthält den Code 'max_age=60 * 60 * 24,'.
43. Diese Zeile enthält den Code 'path="/",'.
44. Diese Zeile enthält den Code ')'.
45. Diese Zeile ist leer und trennt Abschnitte.
46. Diese Zeile ist leer und trennt Abschnitte.
47. Diese Zeile enthält den Code 'def _identifier_type(identifier: str) -> str:'.
48. Diese Zeile enthält den Code 'return "email" if "@" in identifier else "username"'.
49. Diese Zeile ist leer und trennt Abschnitte.
50. Diese Zeile ist leer und trennt Abschnitte.
51. Diese Zeile enthält den Code 'def _find_user_by_identifier(db: Session, identifier: str) -> User | None:'.
52. Diese Zeile enthält den Code 'cleaned = identifier.strip()'.
53. Diese Zeile enthält den Code 'if not cleaned:'.
54. Diese Zeile enthält den Code 'return None'.
55. Diese Zeile enthält den Code 'if "@" in cleaned:'.
56. Diese Zeile enthält den Code 'return db.scalar(select(User).where(User.email == cleaned.lower()))'.
57. Diese Zeile enthält den Code 'return db.scalar(select(User).where(User.username_normalized == normalize_username(cleaned)))'.
58. Diese Zeile ist leer und trennt Abschnitte.
59. Diese Zeile ist leer und trennt Abschnitte.
60. Diese Zeile enthält den Code 'def _normalize_email(value: str) -> str:'.
61. Diese Zeile enthält den Code 'return value.strip().lower()'.
62. Diese Zeile ist leer und trennt Abschnitte.
63. Diese Zeile ist leer und trennt Abschnitte.
64. Diese Zeile enthält den Code 'def _is_valid_email(value: str) -> bool:'.
65. Diese Zeile enthält den Code 'return bool(EMAIL_PATTERN.fullmatch(value))'.
66. Diese Zeile ist leer und trennt Abschnitte.
67. Diese Zeile ist leer und trennt Abschnitte.
68. Diese Zeile enthält den Code 'def _find_valid_token('.
69. Diese Zeile enthält den Code 'db: Session,'.
70. Diese Zeile enthält den Code 'raw_token: str,'.
71. Diese Zeile enthält den Code '*,'.
72. Diese Zeile enthält den Code 'purpose: str,'.
73. Diese Zeile enthält den Code ') -> PasswordResetToken | None:'.
74. Diese Zeile enthält den Code 'now = datetime.now(timezone.utc)'.
75. Diese Zeile enthält den Code 'return db.scalar('.
76. Diese Zeile enthält den Code 'select(PasswordResetToken).where('.
77. Diese Zeile enthält den Code 'and_('.
78. Diese Zeile enthält den Code 'PasswordResetToken.token_hash == hash_reset_token(raw_token),'.
79. Diese Zeile enthält den Code 'PasswordResetToken.used_at.is_(None),'.
80. Diese Zeile enthält den Code 'PasswordResetToken.expires_at > now,'.
81. Diese Zeile enthält den Code 'PasswordResetToken.purpose == purpose,'.
82. Diese Zeile enthält den Code ')'.
83. Diese Zeile enthält den Code ')'.
84. Diese Zeile enthält den Code ')'.
85. Diese Zeile ist leer und trennt Abschnitte.
86. Diese Zeile ist leer und trennt Abschnitte.
87. Diese Zeile enthält den Code 'def _reset_token_expires_at() -> datetime:'.
88. Diese Zeile enthält den Code 'return datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_token_minutes)'.
89. Diese Zeile ist leer und trennt Abschnitte.
90. Diese Zeile ist leer und trennt Abschnitte.
91. Diese Zeile enthält den Code 'def _render_me('.
92. Diese Zeile enthält den Code 'request: Request,'.
93. Diese Zeile enthält den Code 'current_user: User,'.
94. Diese Zeile enthält den Code 'message: str | None = None,'.
95. Diese Zeile enthält den Code 'error: str | None = None,'.
96. Diese Zeile enthält den Code 'status_code: int = status.HTTP_200_OK,'.
97. Diese Zeile enthält den Code '):'.
98. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
99. Diese Zeile enthält den Code '"me.html",'.
100. Diese Zeile enthält den Code 'template_context('.
101. Diese Zeile enthält den Code 'request,'.
102. Diese Zeile enthält den Code 'current_user,'.
103. Diese Zeile enthält den Code 'user=current_user,'.
104. Diese Zeile enthält den Code 'message=message,'.
105. Diese Zeile enthält den Code 'error=error,'.
106. Diese Zeile enthält den Code '),'.
107. Diese Zeile enthält den Code 'status_code=status_code,'.
108. Diese Zeile enthält den Code ')'.
109. Diese Zeile ist leer und trennt Abschnitte.
110. Diese Zeile ist leer und trennt Abschnitte.
111. Diese Zeile enthält den Code '@router.get("/login")'.
112. Diese Zeile enthält den Code '@router.get("/auth/login")'.
113. Diese Zeile enthält den Code 'def login_page('.
114. Diese Zeile enthält den Code 'request: Request,'.
115. Diese Zeile enthält den Code 'message: str = "",'.
116. Diese Zeile enthält den Code 'current_user: User | None = Depends(get_current_user_optional),'.
117. Diese Zeile enthält den Code '):'.
118. Diese Zeile enthält den Code 'if current_user:'.
119. Diese Zeile enthält den Code 'return redirect("/")'.
120. Diese Zeile enthält den Code 'message_map = {'.
121. Diese Zeile enthält den Code '"reset_done": t("auth.reset_success", request=request),'.
122. Diese Zeile enthält den Code '"password_changed": t("auth.password_changed_success", request=request),'.
123. Diese Zeile enthält den Code '}'.
124. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
125. Diese Zeile enthält den Code '"auth_login.html",'.
126. Diese Zeile enthält den Code 'template_context('.
127. Diese Zeile enthält den Code 'request,'.
128. Diese Zeile enthält den Code 'current_user,'.
129. Diese Zeile enthält den Code 'error=None,'.
130. Diese Zeile enthält den Code 'message=message_map.get(message, ""),'.
131. Diese Zeile enthält den Code 'identifier_value="",'.
132. Diese Zeile enthält den Code '),'.
133. Diese Zeile enthält den Code ')'.
134. Diese Zeile ist leer und trennt Abschnitte.
135. Diese Zeile ist leer und trennt Abschnitte.
136. Diese Zeile enthält den Code '@router.post("/login")'.
137. Diese Zeile enthält den Code '@router.post("/auth/login")'.
138. Diese Zeile enthält den Code '@limiter.limit("5/minute", key_func=key_by_ip)'.
139. Diese Zeile enthält den Code 'def login_submit('.
140. Diese Zeile enthält den Code 'request: Request,'.
141. Diese Zeile enthält den Code 'response: Response,'.
142. Diese Zeile enthält den Code 'identifier: str = Form(...),'.
143. Diese Zeile enthält den Code 'password: str = Form(...),'.
144. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
145. Diese Zeile enthält den Code '):'.
146. Diese Zeile enthält den Code '_ = response'.
147. Diese Zeile enthält den Code 'user = _find_user_by_identifier(db, identifier)'.
148. Diese Zeile enthält den Code 'id_type = _identifier_type(identifier)'.
149. Diese Zeile enthält den Code 'if not user or not verify_password(password, user.hashed_password):'.
150. Diese Zeile enthält den Code 'log_security_event('.
151. Diese Zeile enthält den Code 'db,'.
152. Diese Zeile enthält den Code 'request,'.
153. Diese Zeile enthält den Code 'event_type="login_failed",'.
154. Diese Zeile enthält den Code 'user_id=user.id if user else None,'.
155. Diese Zeile enthält den Code 'details=f"identifier={id_type}",'.
156. Diese Zeile enthält den Code ')'.
157. Diese Zeile enthält den Code 'db.commit()'.
158. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
159. Diese Zeile enthält den Code '"auth_login.html",'.
160. Diese Zeile enthält den Code 'template_context('.
161. Diese Zeile enthält den Code 'request,'.
162. Diese Zeile enthält den Code 'None,'.
163. Diese Zeile enthält den Code 'error=t("error.invalid_credentials", request=request),'.
164. Diese Zeile enthält den Code 'message="",'.
165. Diese Zeile enthält den Code 'identifier_value=identifier,'.
166. Diese Zeile enthält den Code '),'.
167. Diese Zeile enthält den Code 'status_code=status.HTTP_401_UNAUTHORIZED,'.
168. Diese Zeile enthält den Code ')'.
169. Diese Zeile enthält den Code 'user.last_login_at = datetime.now(timezone.utc)'.
170. Diese Zeile enthält den Code 'user.last_login_ip = request.client.host[:64] if request.client and request.client.host else None'.
171. Diese Zeile enthält den Code 'user.last_login_user_agent = (request.headers.get("user-agent") or "")[:200] or None'.
172. Diese Zeile enthält den Code 'db.add(user)'.
173. Diese Zeile enthält den Code 'log_security_event(db, request, event_type="login_success", user_id=user.id, details=f"identifier...'.
174. Diese Zeile enthält den Code 'db.commit()'.
175. Diese Zeile enthält den Code 'token = create_access_token(user.user_uid, user.role)'.
176. Diese Zeile enthält den Code 'response = redirect("/")'.
177. Diese Zeile enthält den Code 'set_auth_cookie(response, token)'.
178. Diese Zeile enthält den Code 'return response'.
179. Diese Zeile ist leer und trennt Abschnitte.
180. Diese Zeile ist leer und trennt Abschnitte.
181. Diese Zeile enthält den Code '@router.get("/register")'.
182. Diese Zeile enthält den Code '@router.get("/auth/register")'.
183. Diese Zeile enthält den Code 'def register_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):'.
184. Diese Zeile enthält den Code 'if current_user:'.
185. Diese Zeile enthält den Code 'return redirect("/")'.
186. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
187. Diese Zeile enthält den Code '"auth_register.html",'.
188. Diese Zeile enthält den Code 'template_context(request, current_user, error=None, username_value=""),'.
189. Diese Zeile enthält den Code ')'.
190. Diese Zeile ist leer und trennt Abschnitte.
191. Diese Zeile ist leer und trennt Abschnitte.
192. Diese Zeile enthält den Code '@router.post("/register")'.
193. Diese Zeile enthält den Code '@router.post("/auth/register")'.
194. Diese Zeile enthält den Code '@limiter.limit("3/minute", key_func=key_by_ip)'.
195. Diese Zeile enthält den Code 'def register_submit('.
196. Diese Zeile enthält den Code 'request: Request,'.
197. Diese Zeile enthält den Code 'response: Response,'.
198. Diese Zeile enthält den Code 'email: str = Form(...),'.
199. Diese Zeile enthält den Code 'username: str = Form(""),'.
200. Diese Zeile enthält den Code 'password: str = Form(...),'.
201. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
202. Diese Zeile enthält den Code '):'.
203. Diese Zeile enthält den Code '_ = response'.
204. Diese Zeile enthält den Code 'normalized_email = email.strip().lower()'.
205. Diese Zeile enthält den Code 'username_value = username.strip()'.
206. Diese Zeile enthält den Code 'normalized_username = normalize_username(username_value) if username_value else None'.
207. Diese Zeile enthält den Code 'password_error = validate_password_policy(password)'.
208. Diese Zeile enthält den Code 'if password_error:'.
209. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
210. Diese Zeile enthält den Code '"auth_register.html",'.
211. Diese Zeile enthält den Code 'template_context(request, None, error=password_error, username_value=username_value),'.
212. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
213. Diese Zeile enthält den Code ')'.
214. Diese Zeile enthält den Code 'if username_value:'.
215. Diese Zeile enthält den Code 'username_error = validate_username_policy(username_value)'.
216. Diese Zeile enthält den Code 'if username_error:'.
217. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
218. Diese Zeile enthält den Code '"auth_register.html",'.
219. Diese Zeile enthält den Code 'template_context(request, None, error=username_error, username_value=username_value),'.
220. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
221. Diese Zeile enthält den Code ')'.
222. Diese Zeile enthält den Code 'existing = db.scalar(select(User).where(User.email == normalized_email))'.
223. Diese Zeile enthält den Code 'if existing:'.
224. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
225. Diese Zeile enthält den Code '"auth_register.html",'.
226. Diese Zeile enthält den Code 'template_context(request, None, error=t("error.email_registered", request=request), username_valu...'.
227. Diese Zeile enthält den Code 'status_code=status.HTTP_409_CONFLICT,'.
228. Diese Zeile enthält den Code ')'.
229. Diese Zeile enthält den Code 'if normalized_username:'.
230. Diese Zeile enthält den Code 'same_username = db.scalar(select(User).where(User.username_normalized == normalized_username))'.
231. Diese Zeile enthält den Code 'if same_username:'.
232. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
233. Diese Zeile enthält den Code '"auth_register.html",'.
234. Diese Zeile enthält den Code 'template_context(request, None, error=t("error.username_taken", request=request), username_value=...'.
235. Diese Zeile enthält den Code 'status_code=status.HTTP_409_CONFLICT,'.
236. Diese Zeile enthält den Code ')'.
237. Diese Zeile enthält den Code 'user = User('.
238. Diese Zeile enthält den Code 'email=normalized_email,'.
239. Diese Zeile enthält den Code 'username=username_value or None,'.
240. Diese Zeile enthält den Code 'username_normalized=normalized_username,'.
241. Diese Zeile enthält den Code 'hashed_password=hash_password(password),'.
242. Diese Zeile enthält den Code 'role="user",'.
243. Diese Zeile enthält den Code ')'.
244. Diese Zeile enthält den Code 'db.add(user)'.
245. Diese Zeile enthält den Code 'db.commit()'.
246. Diese Zeile enthält den Code 'db.refresh(user)'.
247. Diese Zeile enthält den Code 'token = create_access_token(user.user_uid, user.role)'.
248. Diese Zeile enthält den Code 'response = redirect("/")'.
249. Diese Zeile enthält den Code 'set_auth_cookie(response, token)'.
250. Diese Zeile enthält den Code 'return response'.
251. Diese Zeile ist leer und trennt Abschnitte.
252. Diese Zeile ist leer und trennt Abschnitte.
253. Diese Zeile enthält den Code '@router.post("/logout")'.
254. Diese Zeile enthält den Code 'def logout():'.
255. Diese Zeile enthält den Code 'response = redirect("/")'.
256. Diese Zeile enthält den Code 'response.delete_cookie("access_token", path="/")'.
257. Diese Zeile enthält den Code 'return response'.
258. Diese Zeile ist leer und trennt Abschnitte.
259. Diese Zeile ist leer und trennt Abschnitte.
260. Diese Zeile enthält den Code '@router.get("/auth/forgot-password")'.
261. Diese Zeile enthält den Code '@router.get("/forgot-password")'.
262. Diese Zeile enthält den Code 'def forgot_password_page('.
263. Diese Zeile enthält den Code 'request: Request,'.
264. Diese Zeile enthält den Code 'current_user: User | None = Depends(get_current_user_optional),'.
265. Diese Zeile enthält den Code '):'.
266. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
267. Diese Zeile enthält den Code '"auth_forgot_password.html",'.
268. Diese Zeile enthält den Code 'template_context(request, current_user, error=None, message=None, identifier_value=""),'.
269. Diese Zeile enthält den Code ')'.
270. Diese Zeile ist leer und trennt Abschnitte.
271. Diese Zeile ist leer und trennt Abschnitte.
272. Diese Zeile enthält den Code '@router.post("/auth/forgot-password")'.
273. Diese Zeile enthält den Code '@router.post("/forgot-password")'.
274. Diese Zeile enthält den Code '@limiter.limit("5/minute", key_func=key_by_ip)'.
275. Diese Zeile enthält den Code 'def forgot_password_submit('.
276. Diese Zeile enthält den Code 'request: Request,'.
277. Diese Zeile enthält den Code 'response: Response,'.
278. Diese Zeile enthält den Code 'identifier: str = Form(...),'.
279. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
280. Diese Zeile enthält den Code '):'.
281. Diese Zeile enthält den Code '_ = response'.
282. Diese Zeile enthält den Code 'generic_message = t("auth.forgot_generic_response", request=request)'.
283. Diese Zeile enthält den Code 'user = _find_user_by_identifier(db, identifier)'.
284. Diese Zeile enthält den Code 'if user:'.
285. Diese Zeile enthält den Code 'raw_token = create_raw_reset_token()'.
286. Diese Zeile enthält den Code 'token_hash = hash_reset_token(raw_token)'.
287. Diese Zeile enthält den Code 'db.add('.
288. Diese Zeile enthält den Code 'PasswordResetToken('.
289. Diese Zeile enthält den Code 'user_id=user.id,'.
290. Diese Zeile enthält den Code 'token_hash=token_hash,'.
291. Diese Zeile enthält den Code 'expires_at=_reset_token_expires_at(),'.
292. Diese Zeile enthält den Code 'created_ip=request.client.host[:64] if request.client and request.client.host else None,'.
293. Diese Zeile enthält den Code 'created_user_agent=(request.headers.get("user-agent") or "")[:200] or None,'.
294. Diese Zeile enthält den Code 'purpose="password_reset",'.
295. Diese Zeile enthält den Code ')'.
296. Diese Zeile enthält den Code ')'.
297. Diese Zeile enthält den Code 'log_security_event(db, request, event_type="pwd_reset_requested", user_id=user.id, details="ident...'.
298. Diese Zeile enthält den Code 'db.commit()'.
299. Diese Zeile enthält den Code 'reset_link = f"{str(settings.app_url).rstrip('/')}/auth/reset-password?token={raw_token}"'.
300. Diese Zeile enthält den Code 'mailer = get_mailer(settings)'.
301. Diese Zeile enthält den Code 'subject = t("auth.reset_email_subject", request=request)'.
302. Diese Zeile enthält den Code 'body = t("auth.reset_email_body", request=request, reset_link=reset_link)'.
303. Diese Zeile enthält den Code 'try:'.
304. Diese Zeile enthält den Code 'mailer.send(MailPayload(to_email=user.email, subject=subject, body=body))'.
305. Diese Zeile enthält den Code 'except Exception:'.
306. Diese Zeile enthält den Code '# We keep the response generic and avoid leaking whether delivery worked.'.
307. Diese Zeile enthält den Code 'logger.warning("password_reset_mail_send_failed user_id=%s", user.id)'.
308. Diese Zeile enthält den Code 'else:'.
309. Diese Zeile enthält den Code 'log_security_event(db, request, event_type="pwd_reset_requested", user_id=None, details="identifi...'.
310. Diese Zeile enthält den Code 'db.commit()'.
311. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
312. Diese Zeile enthält den Code '"auth_forgot_password.html",'.
313. Diese Zeile enthält den Code 'template_context('.
314. Diese Zeile enthält den Code 'request,'.
315. Diese Zeile enthält den Code 'None,'.
316. Diese Zeile enthält den Code 'error=None,'.
317. Diese Zeile enthält den Code 'message=generic_message,'.
318. Diese Zeile enthält den Code 'identifier_value="",'.
319. Diese Zeile enthält den Code '),'.
320. Diese Zeile enthält den Code ')'.
321. Diese Zeile ist leer und trennt Abschnitte.
322. Diese Zeile ist leer und trennt Abschnitte.
323. Diese Zeile enthält den Code '@router.get("/auth/reset-password")'.
324. Diese Zeile enthält den Code 'def reset_password_page('.
325. Diese Zeile enthält den Code 'request: Request,'.
326. Diese Zeile enthält den Code 'token: str = "",'.
327. Diese Zeile enthält den Code 'current_user: User | None = Depends(get_current_user_optional),'.
328. Diese Zeile enthält den Code '):'.
329. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
330. Diese Zeile enthält den Code '"auth_reset_password.html",'.
331. Diese Zeile enthält den Code 'template_context('.
332. Diese Zeile enthält den Code 'request,'.
333. Diese Zeile enthält den Code 'current_user,'.
334. Diese Zeile enthält den Code 'token_value=token,'.
335. Diese Zeile enthält den Code 'error=None,'.
336. Diese Zeile enthält den Code 'message=None,'.
337. Diese Zeile enthält den Code '),'.
338. Diese Zeile enthält den Code ')'.
339. Diese Zeile ist leer und trennt Abschnitte.
340. Diese Zeile ist leer und trennt Abschnitte.
341. Diese Zeile enthält den Code '@router.post("/auth/reset-password")'.
342. Diese Zeile enthält den Code '@limiter.limit("5/minute", key_func=key_by_ip)'.
343. Diese Zeile enthält den Code 'def reset_password_submit('.
344. Diese Zeile enthält den Code 'request: Request,'.
345. Diese Zeile enthält den Code 'response: Response,'.
346. Diese Zeile enthält den Code 'token: str = Form(...),'.
347. Diese Zeile enthält den Code 'new_password: str = Form(...),'.
348. Diese Zeile enthält den Code 'confirm_password: str = Form(...),'.
349. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
350. Diese Zeile enthält den Code '):'.
351. Diese Zeile enthält den Code '_ = response'.
352. Diese Zeile enthält den Code 'token_value = token.strip()'.
353. Diese Zeile enthält den Code 'if not token_value:'.
354. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
355. Diese Zeile enthält den Code '"auth_reset_password.html",'.
356. Diese Zeile enthält den Code 'template_context(request, None, token_value="", error=t("error.reset_token_invalid", request=requ...'.
357. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
358. Diese Zeile enthält den Code ')'.
359. Diese Zeile enthält den Code 'if new_password != confirm_password:'.
360. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
361. Diese Zeile enthält den Code '"auth_reset_password.html",'.
362. Diese Zeile enthält den Code 'template_context('.
363. Diese Zeile enthält den Code 'request,'.
364. Diese Zeile enthält den Code 'None,'.
365. Diese Zeile enthält den Code 'token_value=token_value,'.
366. Diese Zeile enthält den Code 'error=t("error.password_confirm_mismatch", request=request),'.
367. Diese Zeile enthält den Code 'message=None,'.
368. Diese Zeile enthält den Code '),'.
369. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
370. Diese Zeile enthält den Code ')'.
371. Diese Zeile enthält den Code 'password_error = validate_password_policy(new_password)'.
372. Diese Zeile enthält den Code 'if password_error:'.
373. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
374. Diese Zeile enthält den Code '"auth_reset_password.html",'.
375. Diese Zeile enthält den Code 'template_context(request, None, token_value=token_value, error=password_error, message=None),'.
376. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
377. Diese Zeile enthält den Code ')'.
378. Diese Zeile enthält den Code 'now = datetime.now(timezone.utc)'.
379. Diese Zeile enthält den Code 'reset_token = _find_valid_token(db, token_value, purpose="password_reset")'.
380. Diese Zeile enthält den Code 'if not reset_token:'.
381. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
382. Diese Zeile enthält den Code '"auth_reset_password.html",'.
383. Diese Zeile enthält den Code 'template_context(request, None, token_value="", error=t("error.reset_token_invalid", request=requ...'.
384. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
385. Diese Zeile enthält den Code ')'.
386. Diese Zeile enthält den Code 'user = db.scalar(select(User).where(User.id == reset_token.user_id))'.
387. Diese Zeile enthält den Code 'if not user:'.
388. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
389. Diese Zeile enthält den Code '"auth_reset_password.html",'.
390. Diese Zeile enthält den Code 'template_context(request, None, token_value="", error=t("error.reset_token_invalid", request=requ...'.
391. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
392. Diese Zeile enthält den Code ')'.
393. Diese Zeile enthält den Code 'user.hashed_password = hash_password(new_password)'.
394. Diese Zeile enthält den Code 'reset_token.used_at = now'.
395. Diese Zeile enthält den Code 'other_tokens = db.scalars('.
396. Diese Zeile enthält den Code 'select(PasswordResetToken).where('.
397. Diese Zeile enthält den Code 'and_('.
398. Diese Zeile enthält den Code 'PasswordResetToken.user_id == user.id,'.
399. Diese Zeile enthält den Code 'PasswordResetToken.used_at.is_(None),'.
400. Diese Zeile enthält den Code 'PasswordResetToken.id != reset_token.id,'.
401. Diese Zeile enthält den Code 'PasswordResetToken.purpose == "password_reset",'.
402. Diese Zeile enthält den Code ')'.
403. Diese Zeile enthält den Code ')'.
404. Diese Zeile enthält den Code ').all()'.
405. Diese Zeile enthält den Code 'for item in other_tokens:'.
406. Diese Zeile enthält den Code 'item.used_at = now'.
407. Diese Zeile enthält den Code 'db.add(user)'.
408. Diese Zeile enthält den Code 'log_security_event(db, request, event_type="pwd_reset_done", user_id=user.id, details="token=sing...'.
409. Diese Zeile enthält den Code 'db.commit()'.
410. Diese Zeile enthält den Code 'return redirect("/login?message=reset_done")'.
411. Diese Zeile ist leer und trennt Abschnitte.
412. Diese Zeile ist leer und trennt Abschnitte.
413. Diese Zeile enthält den Code '@router.post("/auth/change-password")'.
414. Diese Zeile enthält den Code '@limiter.limit("3/minute", key_func=key_by_user_or_ip)'.
415. Diese Zeile enthält den Code 'def change_password_submit('.
416. Diese Zeile enthält den Code 'request: Request,'.
417. Diese Zeile enthält den Code 'old_password: str = Form(...),'.
418. Diese Zeile enthält den Code 'new_password: str = Form(...),'.
419. Diese Zeile enthält den Code 'confirm_password: str = Form(...),'.
420. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
421. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
422. Diese Zeile enthält den Code '):'.
423. Diese Zeile enthält den Code 'if not verify_password(old_password, current_user.hashed_password):'.
424. Diese Zeile enthält den Code 'return _render_me('.
425. Diese Zeile enthält den Code 'request,'.
426. Diese Zeile enthält den Code 'current_user,'.
427. Diese Zeile enthält den Code 'error=t("error.password_old_invalid", request=request),'.
428. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
429. Diese Zeile enthält den Code ')'.
430. Diese Zeile enthält den Code 'if new_password != confirm_password:'.
431. Diese Zeile enthält den Code 'return _render_me('.
432. Diese Zeile enthält den Code 'request,'.
433. Diese Zeile enthält den Code 'current_user,'.
434. Diese Zeile enthält den Code 'error=t("error.password_confirm_mismatch", request=request),'.
435. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
436. Diese Zeile enthält den Code ')'.
437. Diese Zeile enthält den Code 'password_error = validate_password_policy(new_password)'.
438. Diese Zeile enthält den Code 'if password_error:'.
439. Diese Zeile enthält den Code 'return _render_me('.
440. Diese Zeile enthält den Code 'request,'.
441. Diese Zeile enthält den Code 'current_user,'.
442. Diese Zeile enthält den Code 'error=password_error,'.
443. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
444. Diese Zeile enthält den Code ')'.
445. Diese Zeile enthält den Code 'current_user.hashed_password = hash_password(new_password)'.
446. Diese Zeile enthält den Code 'db.add(current_user)'.
447. Diese Zeile enthält den Code 'log_security_event(db, request, event_type="pwd_changed", user_id=current_user.id, details="chang...'.
448. Diese Zeile enthält den Code 'db.commit()'.
449. Diese Zeile enthält den Code 'response = redirect("/me?message=password_changed")'.
450. Diese Zeile enthält den Code 'set_auth_cookie(response, create_access_token(current_user.user_uid, current_user.role))'.
451. Diese Zeile enthält den Code 'return response'.
452. Diese Zeile ist leer und trennt Abschnitte.
453. Diese Zeile ist leer und trennt Abschnitte.
454. Diese Zeile enthält den Code '@router.post("/profile/username")'.
455. Diese Zeile enthält den Code '@limiter.limit("5/minute", key_func=key_by_user_or_ip)'.
456. Diese Zeile enthält den Code 'def update_username_submit('.
457. Diese Zeile enthält den Code 'request: Request,'.
458. Diese Zeile enthält den Code 'username: str = Form(...),'.
459. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
460. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
461. Diese Zeile enthält den Code '):'.
462. Diese Zeile enthält den Code 'username_value = username.strip()'.
463. Diese Zeile enthält den Code 'username_error = validate_username_policy(username_value)'.
464. Diese Zeile enthält den Code 'if username_error:'.
465. Diese Zeile enthält den Code 'return _render_me(request, current_user, error=username_error, status_code=status.HTTP_400_BAD_RE...'.
466. Diese Zeile enthält den Code 'normalized_username = normalize_username(username_value)'.
467. Diese Zeile enthält den Code 'existing = db.scalar('.
468. Diese Zeile enthält den Code 'select(User).where('.
469. Diese Zeile enthält den Code 'and_('.
470. Diese Zeile enthält den Code 'User.username_normalized == normalized_username,'.
471. Diese Zeile enthält den Code 'User.id != current_user.id,'.
472. Diese Zeile enthält den Code ')'.
473. Diese Zeile enthält den Code ')'.
474. Diese Zeile enthält den Code ')'.
475. Diese Zeile enthält den Code 'if existing:'.
476. Diese Zeile enthält den Code 'return _render_me('.
477. Diese Zeile enthält den Code 'request,'.
478. Diese Zeile enthält den Code 'current_user,'.
479. Diese Zeile enthält den Code 'error=t("error.username_taken", request=request),'.
480. Diese Zeile enthält den Code 'status_code=status.HTTP_409_CONFLICT,'.
481. Diese Zeile enthält den Code ')'.
482. Diese Zeile enthält den Code 'current_user.username = username_value'.
483. Diese Zeile enthält den Code 'current_user.username_normalized = normalized_username'.
484. Diese Zeile enthält den Code 'db.add(current_user)'.
485. Diese Zeile enthält den Code 'log_security_event(db, request, event_type="username_changed", user_id=current_user.id, details="...'.
486. Diese Zeile enthält den Code 'db.commit()'.
487. Diese Zeile enthält den Code 'return redirect("/me?message=username_updated")'.
488. Diese Zeile ist leer und trennt Abschnitte.
489. Diese Zeile ist leer und trennt Abschnitte.
490. Diese Zeile enthält den Code '@router.get("/auth/change-email")'.
491. Diese Zeile enthält den Code 'def change_email_page('.
492. Diese Zeile enthält den Code 'request: Request,'.
493. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
494. Diese Zeile enthält den Code '):'.
495. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
496. Diese Zeile enthält den Code '"auth_change_email.html",'.
497. Diese Zeile enthält den Code 'template_context('.
498. Diese Zeile enthält den Code 'request,'.
499. Diese Zeile enthält den Code 'current_user,'.
500. Diese Zeile enthält den Code 'current_email=current_user.email,'.
501. Diese Zeile enthält den Code 'new_email_value="",'.
502. Diese Zeile enthält den Code 'message=None,'.
503. Diese Zeile enthält den Code 'error=None,'.
504. Diese Zeile enthält den Code '),'.
505. Diese Zeile enthält den Code ')'.
506. Diese Zeile ist leer und trennt Abschnitte.
507. Diese Zeile ist leer und trennt Abschnitte.
508. Diese Zeile enthält den Code '@router.post("/auth/change-email/request")'.
509. Diese Zeile enthält den Code '@limiter.limit("5/minute", key_func=key_by_ip)'.
510. Diese Zeile enthält den Code '@limiter.limit("3/minute", key_func=key_by_user_or_ip)'.
511. Diese Zeile enthält den Code 'def change_email_request_submit('.
512. Diese Zeile enthält den Code 'request: Request,'.
513. Diese Zeile enthält den Code 'new_email: str = Form(...),'.
514. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
515. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
516. Diese Zeile enthält den Code '):'.
517. Diese Zeile enthält den Code 'normalized_new_email = _normalize_email(new_email)'.
518. Diese Zeile enthält den Code 'if not _is_valid_email(normalized_new_email):'.
519. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
520. Diese Zeile enthält den Code '"auth_change_email.html",'.
521. Diese Zeile enthält den Code 'template_context('.
522. Diese Zeile enthält den Code 'request,'.
523. Diese Zeile enthält den Code 'current_user,'.
524. Diese Zeile enthält den Code 'current_email=current_user.email,'.
525. Diese Zeile enthält den Code 'new_email_value=new_email,'.
526. Diese Zeile enthält den Code 'message=None,'.
527. Diese Zeile enthält den Code 'error=t("error.email_invalid", request=request),'.
528. Diese Zeile enthält den Code '),'.
529. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
530. Diese Zeile enthält den Code ')'.
531. Diese Zeile enthält den Code 'if normalized_new_email == current_user.email:'.
532. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
533. Diese Zeile enthält den Code '"auth_change_email.html",'.
534. Diese Zeile enthält den Code 'template_context('.
535. Diese Zeile enthält den Code 'request,'.
536. Diese Zeile enthält den Code 'current_user,'.
537. Diese Zeile enthält den Code 'current_email=current_user.email,'.
538. Diese Zeile enthält den Code 'new_email_value="",'.
539. Diese Zeile enthält den Code 'message=t("auth.email_change_same_email", request=request),'.
540. Diese Zeile enthält den Code 'error=None,'.
541. Diese Zeile enthält den Code '),'.
542. Diese Zeile enthält den Code ')'.
543. Diese Zeile enthält den Code 'existing = db.scalar(select(User).where(and_(User.email == normalized_new_email, User.id != curre...'.
544. Diese Zeile enthält den Code 'if existing:'.
545. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
546. Diese Zeile enthält den Code '"auth_change_email.html",'.
547. Diese Zeile enthält den Code 'template_context('.
548. Diese Zeile enthält den Code 'request,'.
549. Diese Zeile enthält den Code 'current_user,'.
550. Diese Zeile enthält den Code 'current_email=current_user.email,'.
551. Diese Zeile enthält den Code 'new_email_value=new_email,'.
552. Diese Zeile enthält den Code 'message=None,'.
553. Diese Zeile enthält den Code 'error=t("error.email_unavailable", request=request),'.
554. Diese Zeile enthält den Code '),'.
555. Diese Zeile enthält den Code 'status_code=status.HTTP_409_CONFLICT,'.
556. Diese Zeile enthält den Code ')'.
557. Diese Zeile enthält den Code 'now = datetime.now(timezone.utc)'.
558. Diese Zeile enthält den Code 'open_tokens = db.scalars('.
559. Diese Zeile enthält den Code 'select(PasswordResetToken).where('.
560. Diese Zeile enthält den Code 'and_('.
561. Diese Zeile enthält den Code 'PasswordResetToken.user_id == current_user.id,'.
562. Diese Zeile enthält den Code 'PasswordResetToken.used_at.is_(None),'.
563. Diese Zeile enthält den Code 'PasswordResetToken.purpose == "email_change",'.
564. Diese Zeile enthält den Code ')'.
565. Diese Zeile enthält den Code ')'.
566. Diese Zeile enthält den Code ').all()'.
567. Diese Zeile enthält den Code 'for open_token in open_tokens:'.
568. Diese Zeile enthält den Code 'open_token.used_at = now'.
569. Diese Zeile enthält den Code 'raw_token = create_raw_reset_token()'.
570. Diese Zeile enthält den Code 'db.add('.
571. Diese Zeile enthält den Code 'PasswordResetToken('.
572. Diese Zeile enthält den Code 'user_id=current_user.id,'.
573. Diese Zeile enthält den Code 'token_hash=hash_reset_token(raw_token),'.
574. Diese Zeile enthält den Code 'new_email_normalized=normalized_new_email,'.
575. Diese Zeile enthält den Code 'expires_at=_reset_token_expires_at(),'.
576. Diese Zeile enthält den Code 'created_ip=request.client.host[:64] if request.client and request.client.host else None,'.
577. Diese Zeile enthält den Code 'created_user_agent=(request.headers.get("user-agent") or "")[:200] or None,'.
578. Diese Zeile enthält den Code 'purpose="email_change",'.
579. Diese Zeile enthält den Code ')'.
580. Diese Zeile enthält den Code ')'.
581. Diese Zeile enthält den Code 'log_security_event('.
582. Diese Zeile enthält den Code 'db,'.
583. Diese Zeile enthält den Code 'request,'.
584. Diese Zeile enthält den Code 'event_type="email_change_requested",'.
585. Diese Zeile enthält den Code 'user_id=current_user.id,'.
586. Diese Zeile enthält den Code 'details="delivery=new_email",'.
587. Diese Zeile enthält den Code ')'.
588. Diese Zeile enthält den Code 'db.commit()'.
589. Diese Zeile enthält den Code 'confirmation_link = f"{str(settings.app_url).rstrip('/')}/auth/change-email/confirm?token={raw_to...'.
590. Diese Zeile enthält den Code 'try:'.
591. Diese Zeile enthält den Code 'get_mailer(settings).send('.
592. Diese Zeile enthält den Code 'MailPayload('.
593. Diese Zeile enthält den Code 'to_email=normalized_new_email,'.
594. Diese Zeile enthält den Code 'subject=t("auth.email_change_subject", request=request),'.
595. Diese Zeile enthält den Code 'body=t("auth.email_change_body", request=request, confirm_link=confirmation_link),'.
596. Diese Zeile enthält den Code 'outbox_file=settings.mail_outbox_email_change_path,'.
597. Diese Zeile enthält den Code ')'.
598. Diese Zeile enthält den Code ')'.
599. Diese Zeile enthält den Code 'except Exception:'.
600. Diese Zeile enthält den Code 'logger.warning("email_change_mail_send_failed user_uid=%s", current_user.user_uid)'.
601. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
602. Diese Zeile enthält den Code '"auth_change_email.html",'.
603. Diese Zeile enthält den Code 'template_context('.
604. Diese Zeile enthält den Code 'request,'.
605. Diese Zeile enthält den Code 'current_user,'.
606. Diese Zeile enthält den Code 'current_email=current_user.email,'.
607. Diese Zeile enthält den Code 'new_email_value="",'.
608. Diese Zeile enthält den Code 'message=t("auth.email_change_requested", request=request),'.
609. Diese Zeile enthält den Code 'error=None,'.
610. Diese Zeile enthält den Code '),'.
611. Diese Zeile enthält den Code ')'.
612. Diese Zeile ist leer und trennt Abschnitte.
613. Diese Zeile ist leer und trennt Abschnitte.
614. Diese Zeile enthält den Code '@router.get("/auth/change-email/confirm")'.
615. Diese Zeile enthält den Code 'def change_email_confirm_page('.
616. Diese Zeile enthält den Code 'request: Request,'.
617. Diese Zeile enthält den Code 'token: str = "",'.
618. Diese Zeile enthält den Code 'current_user: User | None = Depends(get_current_user_optional),'.
619. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
620. Diese Zeile enthält den Code '):'.
621. Diese Zeile enthält den Code 'token_value = token.strip()'.
622. Diese Zeile enthält den Code 'record = _find_valid_token(db, token_value, purpose="email_change") if token_value else None'.
623. Diese Zeile enthält den Code 'if not record or not record.new_email_normalized:'.
624. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
625. Diese Zeile enthält den Code '"auth_change_email_confirm.html",'.
626. Diese Zeile enthält den Code 'template_context('.
627. Diese Zeile enthält den Code 'request,'.
628. Diese Zeile enthält den Code 'current_user,'.
629. Diese Zeile enthält den Code 'token_value="",'.
630. Diese Zeile enthält den Code 'is_valid=False,'.
631. Diese Zeile enthält den Code 'new_email_value="",'.
632. Diese Zeile enthält den Code 'message=None,'.
633. Diese Zeile enthält den Code 'error=t("error.email_change_token_invalid", request=request),'.
634. Diese Zeile enthält den Code '),'.
635. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
636. Diese Zeile enthält den Code ')'.
637. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
638. Diese Zeile enthält den Code '"auth_change_email_confirm.html",'.
639. Diese Zeile enthält den Code 'template_context('.
640. Diese Zeile enthält den Code 'request,'.
641. Diese Zeile enthält den Code 'current_user,'.
642. Diese Zeile enthält den Code 'token_value=token_value,'.
643. Diese Zeile enthält den Code 'is_valid=True,'.
644. Diese Zeile enthält den Code 'new_email_value=record.new_email_normalized,'.
645. Diese Zeile enthält den Code 'message=None,'.
646. Diese Zeile enthält den Code 'error=None,'.
647. Diese Zeile enthält den Code '),'.
648. Diese Zeile enthält den Code ')'.
649. Diese Zeile ist leer und trennt Abschnitte.
650. Diese Zeile ist leer und trennt Abschnitte.
651. Diese Zeile enthält den Code '@router.post("/auth/change-email/confirm")'.
652. Diese Zeile enthält den Code '@limiter.limit("5/minute", key_func=key_by_ip)'.
653. Diese Zeile enthält den Code 'def change_email_confirm_submit('.
654. Diese Zeile enthält den Code 'request: Request,'.
655. Diese Zeile enthält den Code 'token: str = Form(...),'.
656. Diese Zeile enthält den Code 'db: Session = Depends(get_db),'.
657. Diese Zeile enthält den Code '):'.
658. Diese Zeile enthält den Code 'token_value = token.strip()'.
659. Diese Zeile enthält den Code 'record = _find_valid_token(db, token_value, purpose="email_change") if token_value else None'.
660. Diese Zeile enthält den Code 'if not record or not record.new_email_normalized:'.
661. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
662. Diese Zeile enthält den Code '"auth_change_email_confirm.html",'.
663. Diese Zeile enthält den Code 'template_context('.
664. Diese Zeile enthält den Code 'request,'.
665. Diese Zeile enthält den Code 'None,'.
666. Diese Zeile enthält den Code 'token_value="",'.
667. Diese Zeile enthält den Code 'is_valid=False,'.
668. Diese Zeile enthält den Code 'new_email_value="",'.
669. Diese Zeile enthält den Code 'message=None,'.
670. Diese Zeile enthält den Code 'error=t("error.email_change_token_invalid", request=request),'.
671. Diese Zeile enthält den Code '),'.
672. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
673. Diese Zeile enthält den Code ')'.
674. Diese Zeile enthält den Code 'user = db.scalar(select(User).where(User.id == record.user_id))'.
675. Diese Zeile enthält den Code 'if not user:'.
676. Diese Zeile enthält den Code 'record.used_at = datetime.now(timezone.utc)'.
677. Diese Zeile enthält den Code 'db.add(record)'.
678. Diese Zeile enthält den Code 'db.commit()'.
679. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
680. Diese Zeile enthält den Code '"auth_change_email_confirm.html",'.
681. Diese Zeile enthält den Code 'template_context('.
682. Diese Zeile enthält den Code 'request,'.
683. Diese Zeile enthält den Code 'None,'.
684. Diese Zeile enthält den Code 'token_value="",'.
685. Diese Zeile enthält den Code 'is_valid=False,'.
686. Diese Zeile enthält den Code 'new_email_value="",'.
687. Diese Zeile enthält den Code 'message=None,'.
688. Diese Zeile enthält den Code 'error=t("error.email_change_token_invalid", request=request),'.
689. Diese Zeile enthält den Code '),'.
690. Diese Zeile enthält den Code 'status_code=status.HTTP_400_BAD_REQUEST,'.
691. Diese Zeile enthält den Code ')'.
692. Diese Zeile enthält den Code 'conflict = db.scalar(select(User).where(and_(User.email == record.new_email_normalized, User.id !...'.
693. Diese Zeile enthält den Code 'if conflict:'.
694. Diese Zeile enthält den Code 'return templates.TemplateResponse('.
695. Diese Zeile enthält den Code '"auth_change_email_confirm.html",'.
696. Diese Zeile enthält den Code 'template_context('.
697. Diese Zeile enthält den Code 'request,'.
698. Diese Zeile enthält den Code 'None,'.
699. Diese Zeile enthält den Code 'token_value="",'.
700. Diese Zeile enthält den Code 'is_valid=False,'.
701. Diese Zeile enthält den Code 'new_email_value="",'.
702. Diese Zeile enthält den Code 'message=None,'.
703. Diese Zeile enthält den Code 'error=t("error.email_unavailable", request=request),'.
704. Diese Zeile enthält den Code '),'.
705. Diese Zeile enthält den Code 'status_code=status.HTTP_409_CONFLICT,'.
706. Diese Zeile enthält den Code ')'.
707. Diese Zeile enthält den Code 'user.email = record.new_email_normalized'.
708. Diese Zeile enthält den Code 'record.used_at = datetime.now(timezone.utc)'.
709. Diese Zeile enthält den Code 'db.add(user)'.
710. Diese Zeile enthält den Code 'log_security_event(db, request, event_type="email_change_completed", user_id=user.id, details="co...'.
711. Diese Zeile enthält den Code 'db.commit()'.
712. Diese Zeile enthält den Code 'response = redirect("/me?message=email_changed")'.
713. Diese Zeile enthält den Code 'set_auth_cookie(response, create_access_token(user.user_uid, user.role))'.
714. Diese Zeile enthält den Code 'return response'.
715. Diese Zeile ist leer und trennt Abschnitte.
716. Diese Zeile ist leer und trennt Abschnitte.
717. Diese Zeile enthält den Code '@router.get("/me")'.
718. Diese Zeile enthält den Code 'def me_page('.
719. Diese Zeile enthält den Code 'request: Request,'.
720. Diese Zeile enthält den Code 'message: str = "",'.
721. Diese Zeile enthält den Code 'current_user: User = Depends(get_current_user),'.
722. Diese Zeile enthält den Code '):'.
723. Diese Zeile enthält den Code 'message_map = {'.
724. Diese Zeile enthält den Code '"username_updated": t("profile.username_updated", request=request),'.
725. Diese Zeile enthält den Code '"password_changed": t("auth.password_changed_success", request=request),'.
726. Diese Zeile enthält den Code '"email_changed": t("auth.email_change_success", request=request),'.
727. Diese Zeile enthält den Code '}'.
728. Diese Zeile enthält den Code 'return _render_me(request, current_user, message=message_map.get(message, ""))'.
729. Diese Zeile ist leer und trennt Abschnitte.
730. Diese Zeile ist leer und trennt Abschnitte.
731. Diese Zeile enthält den Code '@router.get("/api/me")'.
732. Diese Zeile enthält den Code 'def me_api(current_user: User = Depends(get_current_user)):'.
733. Diese Zeile enthält den Code 'return {'.
734. Diese Zeile enthält den Code '"id": current_user.id,'.
735. Diese Zeile enthält den Code '"user_uid": current_user.user_uid,'.
736. Diese Zeile enthält den Code '"email": current_user.email,'.
737. Diese Zeile enthält den Code '"username": current_user.username,'.
738. Diese Zeile enthält den Code '"role": current_user.role,'.
739. Diese Zeile enthält den Code '"created_at": current_user.created_at.isoformat(),'.
740. Diese Zeile enthält den Code '"last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,'.
741. Diese Zeile enthält den Code '}'.
742. Diese Zeile ist leer und trennt Abschnitte.
743. Diese Zeile ist leer und trennt Abschnitte.
744. Diese Zeile enthält den Code '@router.get("/admin-only")'.
745. Diese Zeile enthält den Code 'def admin_only(request: Request, current_user: User = Depends(get_current_user)):'.
746. Diese Zeile enthält den Code 'if current_user.role != "admin":'.
747. Diese Zeile enthält den Code 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required", reque...'.
748. Diese Zeile enthält den Code 'return {"message": t("role.admin", request=request)}'.

## app/templates/me.html

`$lang
{% extends "base.html" %}
{% block content %}
<section class="panel">
  <h1>{{ t("profile.title") }}</h1>
  {% if message %}<p class="meta">{{ message }}</p>{% endif %}
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  <p><strong>{{ t("profile.user_uid") }}:</strong> {{ user.user_uid }}</p>
  <p><strong>{{ t("profile.email") }}:</strong> {{ user.email }}</p>
  <p><strong>{{ t("profile.role") }}:</strong> {{ role_label(user.role) }}</p>
  <p><strong>{{ t("profile.username") }}:</strong> {{ user.username or "-" }}</p>
  <p><strong>{{ t("profile.joined") }}:</strong> {{ user.created_at|datetime_de }}</p>
</section>

<section class="panel narrow">
  <h2>{{ t("auth.change_email_title") }}</h2>
  <p><a href="/auth/change-email">{{ t("auth.change_email_open_link") }}</a></p>
</section>

<section class="panel narrow">
  <h2>{{ t("profile.username_change_title") }}</h2>
  <form method="post" action="/profile/username" class="stack">
    <label>{{ t("profile.username") }}
      <input type="text" name="username" value="{{ user.username or '' }}" minlength="3" maxlength="30" required>
    </label>
    <button type="submit">{{ t("profile.username_save") }}</button>
  </form>
</section>

<section class="panel narrow">
  <h2>{{ t("auth.change_password_title") }}</h2>
  <form method="post" action="/auth/change-password" class="stack">
    <label>{{ t("auth.old_password") }} <input type="password" name="old_password" required></label>
    <label>{{ t("auth.new_password") }} <input type="password" name="new_password" minlength="10" required></label>
    <label>{{ t("auth.confirm_password") }} <input type="password" name="confirm_password" minlength="10" required></label>
    <button type="submit">{{ t("auth.change_password_button") }}</button>
  </form>
</section>
{% endblock %}

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '{% extends "base.html" %}'.
2. Diese Zeile enthält den Code '{% block content %}'.
3. Diese Zeile enthält den Code '<section class="panel">'.
4. Diese Zeile enthält den Code '<h1>{{ t("profile.title") }}</h1>'.
5. Diese Zeile enthält den Code '{% if message %}<p class="meta">{{ message }}</p>{% endif %}'.
6. Diese Zeile enthält den Code '{% if error %}<p class="error">{{ error }}</p>{% endif %}'.
7. Diese Zeile enthält den Code '<p><strong>{{ t("profile.user_uid") }}:</strong> {{ user.user_uid }}</p>'.
8. Diese Zeile enthält den Code '<p><strong>{{ t("profile.email") }}:</strong> {{ user.email }}</p>'.
9. Diese Zeile enthält den Code '<p><strong>{{ t("profile.role") }}:</strong> {{ role_label(user.role) }}</p>'.
10. Diese Zeile enthält den Code '<p><strong>{{ t("profile.username") }}:</strong> {{ user.username or "-" }}</p>'.
11. Diese Zeile enthält den Code '<p><strong>{{ t("profile.joined") }}:</strong> {{ user.created_at|datetime_de }}</p>'.
12. Diese Zeile enthält den Code '</section>'.
13. Diese Zeile ist leer und trennt Abschnitte.
14. Diese Zeile enthält den Code '<section class="panel narrow">'.
15. Diese Zeile enthält den Code '<h2>{{ t("auth.change_email_title") }}</h2>'.
16. Diese Zeile enthält den Code '<p><a href="/auth/change-email">{{ t("auth.change_email_open_link") }}</a></p>'.
17. Diese Zeile enthält den Code '</section>'.
18. Diese Zeile ist leer und trennt Abschnitte.
19. Diese Zeile enthält den Code '<section class="panel narrow">'.
20. Diese Zeile enthält den Code '<h2>{{ t("profile.username_change_title") }}</h2>'.
21. Diese Zeile enthält den Code '<form method="post" action="/profile/username" class="stack">'.
22. Diese Zeile enthält den Code '<label>{{ t("profile.username") }}'.
23. Diese Zeile enthält den Code '<input type="text" name="username" value="{{ user.username or '' }}" minlength="3" maxlength="30"...'.
24. Diese Zeile enthält den Code '</label>'.
25. Diese Zeile enthält den Code '<button type="submit">{{ t("profile.username_save") }}</button>'.
26. Diese Zeile enthält den Code '</form>'.
27. Diese Zeile enthält den Code '</section>'.
28. Diese Zeile ist leer und trennt Abschnitte.
29. Diese Zeile enthält den Code '<section class="panel narrow">'.
30. Diese Zeile enthält den Code '<h2>{{ t("auth.change_password_title") }}</h2>'.
31. Diese Zeile enthält den Code '<form method="post" action="/auth/change-password" class="stack">'.
32. Diese Zeile enthält den Code '<label>{{ t("auth.old_password") }} <input type="password" name="old_password" required></label>'.
33. Diese Zeile enthält den Code '<label>{{ t("auth.new_password") }} <input type="password" name="new_password" minlength="10" req...'.
34. Diese Zeile enthält den Code '<label>{{ t("auth.confirm_password") }} <input type="password" name="confirm_password" minlength=...'.
35. Diese Zeile enthält den Code '<button type="submit">{{ t("auth.change_password_button") }}</button>'.
36. Diese Zeile enthält den Code '</form>'.
37. Diese Zeile enthält den Code '</section>'.
38. Diese Zeile enthält den Code '{% endblock %}'.

## app/templates/auth_change_email.html

`$lang
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("auth.change_email_title") }}</h1>
  <p class="meta">{{ t("auth.change_email_current", email=current_email) }}</p>
  {% if message %}<p class="meta">{{ message }}</p>{% endif %}
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  <form method="post" action="/auth/change-email/request" class="stack">
    <label>{{ t("auth.new_email_label") }} <input type="email" name="new_email" value="{{ new_email_value }}" required></label>
    <button type="submit">{{ t("auth.change_email_request_button") }}</button>
  </form>
</section>
{% endblock %}

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '{% extends "base.html" %}'.
2. Diese Zeile enthält den Code '{% block content %}'.
3. Diese Zeile enthält den Code '<section class="panel narrow">'.
4. Diese Zeile enthält den Code '<h1>{{ t("auth.change_email_title") }}</h1>'.
5. Diese Zeile enthält den Code '<p class="meta">{{ t("auth.change_email_current", email=current_email) }}</p>'.
6. Diese Zeile enthält den Code '{% if message %}<p class="meta">{{ message }}</p>{% endif %}'.
7. Diese Zeile enthält den Code '{% if error %}<p class="error">{{ error }}</p>{% endif %}'.
8. Diese Zeile enthält den Code '<form method="post" action="/auth/change-email/request" class="stack">'.
9. Diese Zeile enthält den Code '<label>{{ t("auth.new_email_label") }} <input type="email" name="new_email" value="{{ new_email_v...'.
10. Diese Zeile enthält den Code '<button type="submit">{{ t("auth.change_email_request_button") }}</button>'.
11. Diese Zeile enthält den Code '</form>'.
12. Diese Zeile enthält den Code '</section>'.
13. Diese Zeile enthält den Code '{% endblock %}'.

## app/templates/auth_change_email_confirm.html

`$lang
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("auth.change_email_confirm_title") }}</h1>
  {% if message %}<p class="meta">{{ message }}</p>{% endif %}
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  {% if is_valid %}
  <p class="meta">{{ t("auth.change_email_confirm_hint", email=new_email_value) }}</p>
  <form method="post" action="/auth/change-email/confirm" class="stack">
    <input type="hidden" name="token" value="{{ token_value }}">
    <button type="submit">{{ t("auth.change_email_confirm_button") }}</button>
  </form>
  {% else %}
  <p class="meta">{{ t("auth.change_email_reissue_hint") }}</p>
  <p><a href="/auth/change-email">{{ t("auth.change_email_retry_link") }}</a></p>
  {% endif %}
</section>
{% endblock %}

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '{% extends "base.html" %}'.
2. Diese Zeile enthält den Code '{% block content %}'.
3. Diese Zeile enthält den Code '<section class="panel narrow">'.
4. Diese Zeile enthält den Code '<h1>{{ t("auth.change_email_confirm_title") }}</h1>'.
5. Diese Zeile enthält den Code '{% if message %}<p class="meta">{{ message }}</p>{% endif %}'.
6. Diese Zeile enthält den Code '{% if error %}<p class="error">{{ error }}</p>{% endif %}'.
7. Diese Zeile enthält den Code '{% if is_valid %}'.
8. Diese Zeile enthält den Code '<p class="meta">{{ t("auth.change_email_confirm_hint", email=new_email_value) }}</p>'.
9. Diese Zeile enthält den Code '<form method="post" action="/auth/change-email/confirm" class="stack">'.
10. Diese Zeile enthält den Code '<input type="hidden" name="token" value="{{ token_value }}">'.
11. Diese Zeile enthält den Code '<button type="submit">{{ t("auth.change_email_confirm_button") }}</button>'.
12. Diese Zeile enthält den Code '</form>'.
13. Diese Zeile enthält den Code '{% else %}'.
14. Diese Zeile enthält den Code '<p class="meta">{{ t("auth.change_email_reissue_hint") }}</p>'.
15. Diese Zeile enthält den Code '<p><a href="/auth/change-email">{{ t("auth.change_email_retry_link") }}</a></p>'.
16. Diese Zeile enthält den Code '{% endif %}'.
17. Diese Zeile enthält den Code '</section>'.
18. Diese Zeile enthält den Code '{% endblock %}'.

## app/i18n/locales/de.json

`$lang
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
126. Diese Zeile enthält den Code '"error.email_change_token_invalid": "Link ungueltig oder abgelaufen. Bitte erneut anfordern.",'.
127. Diese Zeile enthält den Code '"error.email_invalid": "Bitte gib eine gueltige E-Mail-Adresse ein.",'.
128. Diese Zeile enthält den Code '"error.email_unavailable": "Diese E-Mail ist nicht verfuegbar.",'.
129. Diese Zeile enthält den Code '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
130. Diese Zeile enthält den Code '"error.field_positive": "{field} muss groesser als null sein.",'.
131. Diese Zeile enthält den Code '"error.home_link": "Zur Startseite",'.
132. Diese Zeile enthält den Code '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
133. Diese Zeile enthält den Code '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
134. Diese Zeile enthält den Code '"error.image_not_found": "Bild nicht gefunden.",'.
135. Diese Zeile enthält den Code '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
136. Diese Zeile enthält den Code '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
137. Diese Zeile enthält den Code '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
138. Diese Zeile enthält den Code '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
139. Diese Zeile enthält den Code '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
140. Diese Zeile enthält den Code '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",'.
141. Diese Zeile enthält den Code '"error.internal": "Interner Serverfehler.",'.
142. Diese Zeile enthält den Code '"error.invalid_credentials": "Ungueltige Zugangsdaten.",'.
143. Diese Zeile enthält den Code '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
144. Diese Zeile enthält den Code '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
145. Diese Zeile enthält den Code '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
146. Diese Zeile enthält den Code '"error.not_found": "Ressource nicht gefunden.",'.
147. Diese Zeile enthält den Code '"error.password_confirm_mismatch": "Passwort und Bestaetigung stimmen nicht ueberein.",'.
148. Diese Zeile enthält den Code '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
149. Diese Zeile enthält den Code '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
150. Diese Zeile enthält den Code '"error.password_old_invalid": "Das alte Passwort ist ungueltig.",'.
151. Diese Zeile enthält den Code '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
152. Diese Zeile enthält den Code '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
153. Diese Zeile enthält den Code '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
154. Diese Zeile enthält den Code '"error.recipe_not_found": "Rezept nicht gefunden.",'.
155. Diese Zeile enthält den Code '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
156. Diese Zeile enthält den Code '"error.reset_token_invalid": "Der Reset-Link ist ungueltig oder abgelaufen.",'.
157. Diese Zeile enthält den Code '"error.review_not_found": "Bewertung nicht gefunden.",'.
158. Diese Zeile enthält den Code '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
159. Diese Zeile enthält den Code '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
160. Diese Zeile enthält den Code '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
161. Diese Zeile enthält den Code '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",'.
162. Diese Zeile enthält den Code '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
163. Diese Zeile enthält den Code '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
164. Diese Zeile enthält den Code '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
165. Diese Zeile enthält den Code '"error.submission_not_found": "Einreichung nicht gefunden.",'.
166. Diese Zeile enthält den Code '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
167. Diese Zeile enthält den Code '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
168. Diese Zeile enthält den Code '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
169. Diese Zeile enthält den Code '"error.trace": "Stacktrace (nur Dev)",'.
170. Diese Zeile enthält den Code '"error.user_not_found": "Nutzer nicht gefunden.",'.
171. Diese Zeile enthält den Code '"error.username_invalid": "Benutzername muss 3-30 Zeichen haben und darf nur a-z, A-Z, 0-9, Punkt...'.
172. Diese Zeile enthält den Code '"error.username_taken": "Dieser Benutzername ist bereits vergeben.",'.
173. Diese Zeile enthält den Code '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
174. Diese Zeile enthält den Code '"favorite.add": "Zu Favoriten",'.
175. Diese Zeile enthält den Code '"favorite.remove": "Aus Favoriten entfernen",'.
176. Diese Zeile enthält den Code '"favorites.empty": "Keine Favoriten gespeichert.",'.
177. Diese Zeile enthält den Code '"favorites.remove": "Favorit entfernen",'.
178. Diese Zeile enthält den Code '"favorites.title": "Favoriten",'.
179. Diese Zeile enthält den Code '"home.all_categories": "Alle Kategorien",'.
180. Diese Zeile enthält den Code '"home.apply": "Anwenden",'.
181. Diese Zeile enthält den Code '"home.category": "Kategorie",'.
182. Diese Zeile enthält den Code '"home.difficulty": "Schwierigkeit",'.
183. Diese Zeile enthält den Code '"home.ingredient": "Zutat",'.
184. Diese Zeile enthält den Code '"home.per_page": "Pro Seite",'.
185. Diese Zeile enthält den Code '"home.title": "Rezepte entdecken",'.
186. Diese Zeile enthält den Code '"home.title_contains": "Titel enthaelt",'.
187. Diese Zeile enthält den Code '"images.delete": "Loeschen",'.
188. Diese Zeile enthält den Code '"images.empty": "Noch keine Bilder vorhanden.",'.
189. Diese Zeile enthält den Code '"images.new_file": "Neue Bilddatei",'.
190. Diese Zeile enthält den Code '"images.primary": "Hauptbild",'.
191. Diese Zeile enthält den Code '"images.set_primary": "Als Hauptbild setzen",'.
192. Diese Zeile enthält den Code '"images.title": "Bilder",'.
193. Diese Zeile enthält den Code '"images.upload": "Bild hochladen",'.
194. Diese Zeile enthält den Code '"moderation.approve": "Freigeben",'.
195. Diese Zeile enthält den Code '"moderation.pending": "Ausstehend",'.
196. Diese Zeile enthält den Code '"moderation.reject": "Ablehnen",'.
197. Diese Zeile enthält den Code '"moderation.title": "Moderations-Warteschlange",'.
198. Diese Zeile enthält den Code '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
199. Diese Zeile enthält den Code '"my_recipes.title": "Meine Rezepte",'.
200. Diese Zeile enthält den Code '"nav.admin": "Admin",'.
201. Diese Zeile enthält den Code '"nav.admin_submissions": "Moderation",'.
202. Diese Zeile enthält den Code '"nav.create_recipe": "Rezept erstellen",'.
203. Diese Zeile enthält den Code '"nav.discover": "Rezepte entdecken",'.
204. Diese Zeile enthält den Code '"nav.favorites": "Favoriten",'.
205. Diese Zeile enthält den Code '"nav.language": "Sprache",'.
206. Diese Zeile enthält den Code '"nav.login": "Anmelden",'.
207. Diese Zeile enthält den Code '"nav.logout": "Abmelden",'.
208. Diese Zeile enthält den Code '"nav.my_recipes": "Meine Rezepte",'.
209. Diese Zeile enthält den Code '"nav.my_submissions": "Meine Einreichungen",'.
210. Diese Zeile enthält den Code '"nav.profile": "Mein Profil",'.
211. Diese Zeile enthält den Code '"nav.publish_recipe": "Rezept veroeffentlichen",'.
212. Diese Zeile enthält den Code '"nav.register": "Registrieren",'.
213. Diese Zeile enthält den Code '"nav.submit": "Rezept einreichen",'.
214. Diese Zeile enthält den Code '"nav.submit_recipe": "Rezept einreichen",'.
215. Diese Zeile enthält den Code '"pagination.first": "Erste",'.
216. Diese Zeile enthält den Code '"pagination.last": "Letzte",'.
217. Diese Zeile enthält den Code '"pagination.next": "Weiter",'.
218. Diese Zeile enthält den Code '"pagination.page": "Seite",'.
219. Diese Zeile enthält den Code '"pagination.prev": "Zurueck",'.
220. Diese Zeile enthält den Code '"pagination.previous": "Zurueck",'.
221. Diese Zeile enthält den Code '"pagination.results_range": "Zeige {start}-{end} von {total} Rezepten",'.
222. Diese Zeile enthält den Code '"profile.email": "E-Mail",'.
223. Diese Zeile enthält den Code '"profile.joined": "Registriert am",'.
224. Diese Zeile enthält den Code '"profile.role": "Rolle",'.
225. Diese Zeile enthält den Code '"profile.title": "Mein Profil",'.
226. Diese Zeile enthält den Code '"profile.user_uid": "Deine Nutzer-ID",'.
227. Diese Zeile enthält den Code '"profile.username": "Benutzername",'.
228. Diese Zeile enthält den Code '"profile.username_change_title": "Benutzername aendern",'.
229. Diese Zeile enthält den Code '"profile.username_save": "Benutzernamen speichern",'.
230. Diese Zeile enthält den Code '"profile.username_updated": "Benutzername wurde aktualisiert.",'.
231. Diese Zeile enthält den Code '"recipe.average_rating": "Durchschnittliche Bewertung",'.
232. Diese Zeile enthält den Code '"recipe.comment": "Kommentar",'.
233. Diese Zeile enthält den Code '"recipe.delete": "Loeschen",'.
234. Diese Zeile enthält den Code '"recipe.edit": "Bearbeiten",'.
235. Diese Zeile enthält den Code '"recipe.ingredients": "Zutaten",'.
236. Diese Zeile enthält den Code '"recipe.instructions": "Anleitung",'.
237. Diese Zeile enthält den Code '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
238. Diese Zeile enthält den Code '"recipe.no_results": "Keine Rezepte gefunden.",'.
239. Diese Zeile enthält den Code '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
240. Diese Zeile enthält den Code '"recipe.pdf_download": "PDF herunterladen",'.
241. Diese Zeile enthält den Code '"recipe.rating": "Bewertung",'.
242. Diese Zeile enthält den Code '"recipe.rating_short": "Bewertung",'.
243. Diese Zeile enthält den Code '"recipe.review_count_label": "Bewertungen",'.
244. Diese Zeile enthält den Code '"recipe.reviews": "Bewertungen",'.
245. Diese Zeile enthält den Code '"recipe.save_review": "Bewertung speichern",'.
246. Diese Zeile enthält den Code '"recipe_form.category": "Kategorie",'.
247. Diese Zeile enthält den Code '"recipe_form.create": "Erstellen",'.
248. Diese Zeile enthält den Code '"recipe_form.create_title": "Rezept veroeffentlichen",'.
249. Diese Zeile enthält den Code '"recipe_form.description": "Beschreibung",'.
250. Diese Zeile enthält den Code '"recipe_form.difficulty": "Schwierigkeit",'.
251. Diese Zeile enthält den Code '"recipe_form.edit_title": "Rezept bearbeiten",'.
252. Diese Zeile enthält den Code '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
253. Diese Zeile enthält den Code '"recipe_form.instructions": "Anleitung",'.
254. Diese Zeile enthält den Code '"recipe_form.new_category_label": "Neue Kategorie",'.
255. Diese Zeile enthält den Code '"recipe_form.new_category_option": "Neue Kategorie...",'.
256. Diese Zeile enthält den Code '"recipe_form.optional_image": "Optionales Bild",'.
257. Diese Zeile enthält den Code '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
258. Diese Zeile enthält den Code '"recipe_form.save": "Speichern",'.
259. Diese Zeile enthält den Code '"recipe_form.title": "Titel",'.
260. Diese Zeile enthält den Code '"recipe_form.title_image_url": "Titelbild-URL",'.
261. Diese Zeile enthält den Code '"role.admin": "Administrator",'.
262. Diese Zeile enthält den Code '"role.user": "Nutzer",'.
263. Diese Zeile enthält den Code '"sort.highest_rated": "Beste Bewertung",'.
264. Diese Zeile enthält den Code '"sort.lowest_rated": "Schlechteste Bewertung",'.
265. Diese Zeile enthält den Code '"sort.newest": "Neueste",'.
266. Diese Zeile enthält den Code '"sort.oldest": "Aelteste",'.
267. Diese Zeile enthält den Code '"sort.prep_time": "Zubereitungszeit",'.
268. Diese Zeile enthält den Code '"submission.admin_detail_title": "Einreichung",'.
269. Diese Zeile enthält den Code '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
270. Diese Zeile enthält den Code '"submission.admin_note": "Admin-Notiz",'.
271. Diese Zeile enthält den Code '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
272. Diese Zeile enthält den Code '"submission.admin_queue_title": "Moderations-Warteschlange",'.
273. Diese Zeile enthält den Code '"submission.approve_button": "Freigeben",'.
274. Diese Zeile enthält den Code '"submission.approved": "Einreichung wurde freigegeben.",'.
275. Diese Zeile enthält den Code '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
276. Diese Zeile enthält den Code '"submission.category": "Kategorie",'.
277. Diese Zeile enthält den Code '"submission.default_description": "Rezept-Einreichung",'.
278. Diese Zeile enthält den Code '"submission.description": "Beschreibung",'.
279. Diese Zeile enthält den Code '"submission.difficulty": "Schwierigkeit",'.
280. Diese Zeile enthält den Code '"submission.edit_submission": "Einreichung bearbeiten",'.
281. Diese Zeile enthält den Code '"submission.guest": "Gast",'.
282. Diese Zeile enthält den Code '"submission.image_deleted": "Bild wurde entfernt.",'.
283. Diese Zeile enthält den Code '"submission.image_optional": "Optionales Bild",'.
284. Diese Zeile enthält den Code '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
285. Diese Zeile enthält den Code '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
286. Diese Zeile enthält den Code '"submission.instructions": "Anleitung",'.
287. Diese Zeile enthält den Code '"submission.moderation_actions": "Moderations-Aktionen",'.
288. Diese Zeile enthält den Code '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
289. Diese Zeile enthält den Code '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",'.
290. Diese Zeile enthält den Code '"submission.my_title": "Meine Einreichungen",'.
291. Diese Zeile enthält den Code '"submission.new_category_label": "Neue Kategorie",'.
292. Diese Zeile enthält den Code '"submission.new_category_option": "Neue Kategorie...",'.
293. Diese Zeile enthält den Code '"submission.open_detail": "Details",'.
294. Diese Zeile enthält den Code '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
295. Diese Zeile enthält den Code '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
296. Diese Zeile enthält den Code '"submission.preview": "Vorschau",'.
297. Diese Zeile enthält den Code '"submission.reject_button": "Ablehnen",'.
298. Diese Zeile enthält den Code '"submission.reject_reason": "Ablehnungsgrund",'.
299. Diese Zeile enthält den Code '"submission.rejected": "Einreichung wurde abgelehnt.",'.
300. Diese Zeile enthält den Code '"submission.save_changes": "Aenderungen speichern",'.
301. Diese Zeile enthält den Code '"submission.servings": "Portionen (optional)",'.
302. Diese Zeile enthält den Code '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
303. Diese Zeile enthält den Code '"submission.stats_approved": "Freigegeben",'.
304. Diese Zeile enthält den Code '"submission.stats_pending": "Ausstehend",'.
305. Diese Zeile enthält den Code '"submission.stats_rejected": "Abgelehnt",'.
306. Diese Zeile enthält den Code '"submission.status_all": "Alle",'.
307. Diese Zeile enthält den Code '"submission.status_approved": "Freigegeben",'.
308. Diese Zeile enthält den Code '"submission.status_filter": "Status",'.
309. Diese Zeile enthält den Code '"submission.status_pending": "Ausstehend",'.
310. Diese Zeile enthält den Code '"submission.status_rejected": "Abgelehnt",'.
311. Diese Zeile enthält den Code '"submission.submit_button": "Zur Pruefung einreichen",'.
312. Diese Zeile enthält den Code '"submission.submit_hint": "Einreichungen werden vor der Veroeffentlichung durch das Admin-Team ge...'.
313. Diese Zeile enthält den Code '"submission.submit_title": "Rezept einreichen",'.
314. Diese Zeile enthält den Code '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
315. Diese Zeile enthält den Code '"submission.table_action": "Aktion",'.
316. Diese Zeile enthält den Code '"submission.table_date": "Datum",'.
317. Diese Zeile enthält den Code '"submission.table_status": "Status",'.
318. Diese Zeile enthält den Code '"submission.table_submitter": "Einreicher",'.
319. Diese Zeile enthält den Code '"submission.table_title": "Titel",'.
320. Diese Zeile enthält den Code '"submission.thank_you": "Vielen Dank! Dein Rezept wurde eingereicht und wird geprueft.",'.
321. Diese Zeile enthält den Code '"submission.title": "Titel",'.
322. Diese Zeile enthält den Code '"submission.updated": "Einreichung wurde aktualisiert."'.
323. Diese Zeile enthält den Code '}'.

## app/i18n/locales/en.json

`$lang
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
126. Diese Zeile enthält den Code '"error.email_change_token_invalid": "This link is invalid or expired. Please request a new one.",'.
127. Diese Zeile enthält den Code '"error.email_invalid": "Please enter a valid email address.",'.
128. Diese Zeile enthält den Code '"error.email_unavailable": "This email is not available.",'.
129. Diese Zeile enthält den Code '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
130. Diese Zeile enthält den Code '"error.field_positive": "{field} muss groesser als null sein.",'.
131. Diese Zeile enthält den Code '"error.home_link": "Back to Home",'.
132. Diese Zeile enthält den Code '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
133. Diese Zeile enthält den Code '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
134. Diese Zeile enthält den Code '"error.image_not_found": "Bild nicht gefunden.",'.
135. Diese Zeile enthält den Code '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
136. Diese Zeile enthält den Code '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
137. Diese Zeile enthält den Code '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
138. Diese Zeile enthält den Code '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
139. Diese Zeile enthält den Code '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
140. Diese Zeile enthält den Code '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",'.
141. Diese Zeile enthält den Code '"error.internal": "Interner Serverfehler.",'.
142. Diese Zeile enthält den Code '"error.invalid_credentials": "Invalid credentials.",'.
143. Diese Zeile enthält den Code '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
144. Diese Zeile enthält den Code '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
145. Diese Zeile enthält den Code '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
146. Diese Zeile enthält den Code '"error.not_found": "Ressource nicht gefunden.",'.
147. Diese Zeile enthält den Code '"error.password_confirm_mismatch": "Password and confirmation do not match.",'.
148. Diese Zeile enthält den Code '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
149. Diese Zeile enthält den Code '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
150. Diese Zeile enthält den Code '"error.password_old_invalid": "Current password is invalid.",'.
151. Diese Zeile enthält den Code '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
152. Diese Zeile enthält den Code '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
153. Diese Zeile enthält den Code '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
154. Diese Zeile enthält den Code '"error.recipe_not_found": "Rezept nicht gefunden.",'.
155. Diese Zeile enthält den Code '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
156. Diese Zeile enthält den Code '"error.reset_token_invalid": "Reset link is invalid or expired.",'.
157. Diese Zeile enthält den Code '"error.review_not_found": "Bewertung nicht gefunden.",'.
158. Diese Zeile enthält den Code '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
159. Diese Zeile enthält den Code '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
160. Diese Zeile enthält den Code '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
161. Diese Zeile enthält den Code '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",'.
162. Diese Zeile enthält den Code '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
163. Diese Zeile enthält den Code '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
164. Diese Zeile enthält den Code '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
165. Diese Zeile enthält den Code '"error.submission_not_found": "Einreichung nicht gefunden.",'.
166. Diese Zeile enthält den Code '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
167. Diese Zeile enthält den Code '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
168. Diese Zeile enthält den Code '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
169. Diese Zeile enthält den Code '"error.trace": "Stacktrace (nur Dev)",'.
170. Diese Zeile enthält den Code '"error.user_not_found": "Nutzer nicht gefunden.",'.
171. Diese Zeile enthält den Code '"error.username_invalid": "Username must be 3-30 characters and may only contain letters, numbers...'.
172. Diese Zeile enthält den Code '"error.username_taken": "This username is already taken.",'.
173. Diese Zeile enthält den Code '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
174. Diese Zeile enthält den Code '"favorite.add": "Zu Favoriten",'.
175. Diese Zeile enthält den Code '"favorite.remove": "Aus Favoriten entfernen",'.
176. Diese Zeile enthält den Code '"favorites.empty": "Keine Favoriten gespeichert.",'.
177. Diese Zeile enthält den Code '"favorites.remove": "Favorit entfernen",'.
178. Diese Zeile enthält den Code '"favorites.title": "Favoriten",'.
179. Diese Zeile enthält den Code '"home.all_categories": "All categories",'.
180. Diese Zeile enthält den Code '"home.apply": "Apply",'.
181. Diese Zeile enthält den Code '"home.category": "Category",'.
182. Diese Zeile enthält den Code '"home.difficulty": "Difficulty",'.
183. Diese Zeile enthält den Code '"home.ingredient": "Ingredient",'.
184. Diese Zeile enthält den Code '"home.per_page": "Per page",'.
185. Diese Zeile enthält den Code '"home.title": "Discover Recipes",'.
186. Diese Zeile enthält den Code '"home.title_contains": "Title contains",'.
187. Diese Zeile enthält den Code '"images.delete": "Loeschen",'.
188. Diese Zeile enthält den Code '"images.empty": "Noch keine Bilder vorhanden.",'.
189. Diese Zeile enthält den Code '"images.new_file": "Neue Bilddatei",'.
190. Diese Zeile enthält den Code '"images.primary": "Hauptbild",'.
191. Diese Zeile enthält den Code '"images.set_primary": "Als Hauptbild setzen",'.
192. Diese Zeile enthält den Code '"images.title": "Bilder",'.
193. Diese Zeile enthält den Code '"images.upload": "Bild hochladen",'.
194. Diese Zeile enthält den Code '"moderation.approve": "Approve",'.
195. Diese Zeile enthält den Code '"moderation.pending": "Pending",'.
196. Diese Zeile enthält den Code '"moderation.reject": "Reject",'.
197. Diese Zeile enthält den Code '"moderation.title": "Moderation Queue",'.
198. Diese Zeile enthält den Code '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
199. Diese Zeile enthält den Code '"my_recipes.title": "Meine Rezepte",'.
200. Diese Zeile enthält den Code '"nav.admin": "Admin",'.
201. Diese Zeile enthält den Code '"nav.admin_submissions": "Moderation",'.
202. Diese Zeile enthält den Code '"nav.create_recipe": "Create Recipe",'.
203. Diese Zeile enthält den Code '"nav.discover": "Discover Recipes",'.
204. Diese Zeile enthält den Code '"nav.favorites": "Favorites",'.
205. Diese Zeile enthält den Code '"nav.language": "Language",'.
206. Diese Zeile enthält den Code '"nav.login": "Login",'.
207. Diese Zeile enthält den Code '"nav.logout": "Logout",'.
208. Diese Zeile enthält den Code '"nav.my_recipes": "My Recipes",'.
209. Diese Zeile enthält den Code '"nav.my_submissions": "My Submissions",'.
210. Diese Zeile enthält den Code '"nav.profile": "My Profile",'.
211. Diese Zeile enthält den Code '"nav.publish_recipe": "Publish Recipe",'.
212. Diese Zeile enthält den Code '"nav.register": "Register",'.
213. Diese Zeile enthält den Code '"nav.submit": "Submit Recipe",'.
214. Diese Zeile enthält den Code '"nav.submit_recipe": "Submit Recipe",'.
215. Diese Zeile enthält den Code '"pagination.first": "First",'.
216. Diese Zeile enthält den Code '"pagination.last": "Last",'.
217. Diese Zeile enthält den Code '"pagination.next": "Next",'.
218. Diese Zeile enthält den Code '"pagination.page": "Page",'.
219. Diese Zeile enthält den Code '"pagination.prev": "Previous",'.
220. Diese Zeile enthält den Code '"pagination.previous": "Previous",'.
221. Diese Zeile enthält den Code '"pagination.results_range": "Showing {start}-{end} of {total} recipes",'.
222. Diese Zeile enthält den Code '"profile.email": "E-Mail",'.
223. Diese Zeile enthält den Code '"profile.joined": "Registriert am",'.
224. Diese Zeile enthält den Code '"profile.role": "Rolle",'.
225. Diese Zeile enthält den Code '"profile.title": "Mein Profil",'.
226. Diese Zeile enthält den Code '"profile.user_uid": "Your user ID",'.
227. Diese Zeile enthält den Code '"profile.username": "Username",'.
228. Diese Zeile enthält den Code '"profile.username_change_title": "Change username",'.
229. Diese Zeile enthält den Code '"profile.username_save": "Save username",'.
230. Diese Zeile enthält den Code '"profile.username_updated": "Username was updated.",'.
231. Diese Zeile enthält den Code '"recipe.average_rating": "Durchschnittliche Bewertung",'.
232. Diese Zeile enthält den Code '"recipe.comment": "Kommentar",'.
233. Diese Zeile enthält den Code '"recipe.delete": "Loeschen",'.
234. Diese Zeile enthält den Code '"recipe.edit": "Bearbeiten",'.
235. Diese Zeile enthält den Code '"recipe.ingredients": "Zutaten",'.
236. Diese Zeile enthält den Code '"recipe.instructions": "Anleitung",'.
237. Diese Zeile enthält den Code '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
238. Diese Zeile enthält den Code '"recipe.no_results": "No recipes found.",'.
239. Diese Zeile enthält den Code '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
240. Diese Zeile enthält den Code '"recipe.pdf_download": "PDF herunterladen",'.
241. Diese Zeile enthält den Code '"recipe.rating": "Bewertung",'.
242. Diese Zeile enthält den Code '"recipe.rating_short": "Bewertung",'.
243. Diese Zeile enthält den Code '"recipe.review_count_label": "Bewertungen",'.
244. Diese Zeile enthält den Code '"recipe.reviews": "Bewertungen",'.
245. Diese Zeile enthält den Code '"recipe.save_review": "Bewertung speichern",'.
246. Diese Zeile enthält den Code '"recipe_form.category": "Kategorie",'.
247. Diese Zeile enthält den Code '"recipe_form.create": "Erstellen",'.
248. Diese Zeile enthält den Code '"recipe_form.create_title": "Rezept veroeffentlichen",'.
249. Diese Zeile enthält den Code '"recipe_form.description": "Beschreibung",'.
250. Diese Zeile enthält den Code '"recipe_form.difficulty": "Schwierigkeit",'.
251. Diese Zeile enthält den Code '"recipe_form.edit_title": "Rezept bearbeiten",'.
252. Diese Zeile enthält den Code '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
253. Diese Zeile enthält den Code '"recipe_form.instructions": "Anleitung",'.
254. Diese Zeile enthält den Code '"recipe_form.new_category_label": "Neue Kategorie",'.
255. Diese Zeile enthält den Code '"recipe_form.new_category_option": "Neue Kategorie...",'.
256. Diese Zeile enthält den Code '"recipe_form.optional_image": "Optionales Bild",'.
257. Diese Zeile enthält den Code '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
258. Diese Zeile enthält den Code '"recipe_form.save": "Speichern",'.
259. Diese Zeile enthält den Code '"recipe_form.title": "Titel",'.
260. Diese Zeile enthält den Code '"recipe_form.title_image_url": "Titelbild-URL",'.
261. Diese Zeile enthält den Code '"role.admin": "Administrator",'.
262. Diese Zeile enthält den Code '"role.user": "Nutzer",'.
263. Diese Zeile enthält den Code '"sort.highest_rated": "Highest rated",'.
264. Diese Zeile enthält den Code '"sort.lowest_rated": "Lowest rated",'.
265. Diese Zeile enthält den Code '"sort.newest": "Newest",'.
266. Diese Zeile enthält den Code '"sort.oldest": "Oldest",'.
267. Diese Zeile enthält den Code '"sort.prep_time": "Prep time",'.
268. Diese Zeile enthält den Code '"submission.admin_detail_title": "Einreichung",'.
269. Diese Zeile enthält den Code '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
270. Diese Zeile enthält den Code '"submission.admin_note": "Admin-Notiz",'.
271. Diese Zeile enthält den Code '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
272. Diese Zeile enthält den Code '"submission.admin_queue_title": "Moderation Queue",'.
273. Diese Zeile enthält den Code '"submission.approve_button": "Approve",'.
274. Diese Zeile enthält den Code '"submission.approved": "Einreichung wurde freigegeben.",'.
275. Diese Zeile enthält den Code '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
276. Diese Zeile enthält den Code '"submission.category": "Kategorie",'.
277. Diese Zeile enthält den Code '"submission.default_description": "Rezept-Einreichung",'.
278. Diese Zeile enthält den Code '"submission.description": "Beschreibung",'.
279. Diese Zeile enthält den Code '"submission.difficulty": "Schwierigkeit",'.
280. Diese Zeile enthält den Code '"submission.edit_submission": "Einreichung bearbeiten",'.
281. Diese Zeile enthält den Code '"submission.guest": "Gast",'.
282. Diese Zeile enthält den Code '"submission.image_deleted": "Bild wurde entfernt.",'.
283. Diese Zeile enthält den Code '"submission.image_optional": "Optionales Bild",'.
284. Diese Zeile enthält den Code '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
285. Diese Zeile enthält den Code '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
286. Diese Zeile enthält den Code '"submission.instructions": "Anleitung",'.
287. Diese Zeile enthält den Code '"submission.moderation_actions": "Moderations-Aktionen",'.
288. Diese Zeile enthält den Code '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
289. Diese Zeile enthält den Code '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",'.
290. Diese Zeile enthält den Code '"submission.my_title": "My Submissions",'.
291. Diese Zeile enthält den Code '"submission.new_category_label": "Neue Kategorie",'.
292. Diese Zeile enthält den Code '"submission.new_category_option": "Neue Kategorie...",'.
293. Diese Zeile enthält den Code '"submission.open_detail": "Details",'.
294. Diese Zeile enthält den Code '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
295. Diese Zeile enthält den Code '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
296. Diese Zeile enthält den Code '"submission.preview": "Vorschau",'.
297. Diese Zeile enthält den Code '"submission.reject_button": "Reject",'.
298. Diese Zeile enthält den Code '"submission.reject_reason": "Ablehnungsgrund",'.
299. Diese Zeile enthält den Code '"submission.rejected": "Einreichung wurde abgelehnt.",'.
300. Diese Zeile enthält den Code '"submission.save_changes": "Aenderungen speichern",'.
301. Diese Zeile enthält den Code '"submission.servings": "Portionen (optional)",'.
302. Diese Zeile enthält den Code '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
303. Diese Zeile enthält den Code '"submission.stats_approved": "Freigegeben",'.
304. Diese Zeile enthält den Code '"submission.stats_pending": "Ausstehend",'.
305. Diese Zeile enthält den Code '"submission.stats_rejected": "Abgelehnt",'.
306. Diese Zeile enthält den Code '"submission.status_all": "Alle",'.
307. Diese Zeile enthält den Code '"submission.status_approved": "Approved",'.
308. Diese Zeile enthält den Code '"submission.status_filter": "Status",'.
309. Diese Zeile enthält den Code '"submission.status_pending": "Pending",'.
310. Diese Zeile enthält den Code '"submission.status_rejected": "Rejected",'.
311. Diese Zeile enthält den Code '"submission.submit_button": "Zur Pruefung einreichen",'.
312. Diese Zeile enthält den Code '"submission.submit_hint": "Submissions are reviewed by admins before publication.",'.
313. Diese Zeile enthält den Code '"submission.submit_title": "Submit Recipe",'.
314. Diese Zeile enthält den Code '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
315. Diese Zeile enthält den Code '"submission.table_action": "Aktion",'.
316. Diese Zeile enthält den Code '"submission.table_date": "Datum",'.
317. Diese Zeile enthält den Code '"submission.table_status": "Status",'.
318. Diese Zeile enthält den Code '"submission.table_submitter": "Einreicher",'.
319. Diese Zeile enthält den Code '"submission.table_title": "Titel",'.
320. Diese Zeile enthält den Code '"submission.thank_you": "Thank you! Your recipe has been submitted for review.",'.
321. Diese Zeile enthält den Code '"submission.title": "Titel",'.
322. Diese Zeile enthält den Code '"submission.updated": "Einreichung wurde aktualisiert."'.
323. Diese Zeile enthält den Code '}'.

## app/i18n/locales/fr.json

`$lang
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
126. Diese Zeile enthält den Code '"error.email_change_token_invalid": "Ce lien est invalide ou expire. Veuillez en demander un nouv...'.
127. Diese Zeile enthält den Code '"error.email_invalid": "Veuillez saisir une adresse e-mail valide.",'.
128. Diese Zeile enthält den Code '"error.email_unavailable": "Cette adresse e-mail n'est pas disponible.",'.
129. Diese Zeile enthält den Code '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
130. Diese Zeile enthält den Code '"error.field_positive": "{field} muss groesser als null sein.",'.
131. Diese Zeile enthält den Code '"error.home_link": "Retour a l'accueil",'.
132. Diese Zeile enthält den Code '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
133. Diese Zeile enthält den Code '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
134. Diese Zeile enthält den Code '"error.image_not_found": "Bild nicht gefunden.",'.
135. Diese Zeile enthält den Code '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
136. Diese Zeile enthält den Code '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
137. Diese Zeile enthält den Code '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
138. Diese Zeile enthält den Code '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
139. Diese Zeile enthält den Code '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
140. Diese Zeile enthält den Code '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschlossen.",'.
141. Diese Zeile enthält den Code '"error.internal": "Interner Serverfehler.",'.
142. Diese Zeile enthält den Code '"error.invalid_credentials": "Identifiants invalides.",'.
143. Diese Zeile enthält den Code '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
144. Diese Zeile enthält den Code '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
145. Diese Zeile enthält den Code '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
146. Diese Zeile enthält den Code '"error.not_found": "Ressource nicht gefunden.",'.
147. Diese Zeile enthält den Code '"error.password_confirm_mismatch": "Le mot de passe et la confirmation ne correspondent pas.",'.
148. Diese Zeile enthält den Code '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
149. Diese Zeile enthält den Code '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
150. Diese Zeile enthält den Code '"error.password_old_invalid": "L'ancien mot de passe est invalide.",'.
151. Diese Zeile enthält den Code '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
152. Diese Zeile enthält den Code '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
153. Diese Zeile enthält den Code '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
154. Diese Zeile enthält den Code '"error.recipe_not_found": "Rezept nicht gefunden.",'.
155. Diese Zeile enthält den Code '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
156. Diese Zeile enthält den Code '"error.reset_token_invalid": "Le lien de reinitialisation est invalide ou expire.",'.
157. Diese Zeile enthält den Code '"error.review_not_found": "Bewertung nicht gefunden.",'.
158. Diese Zeile enthält den Code '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
159. Diese Zeile enthält den Code '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
160. Diese Zeile enthält den Code '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
161. Diese Zeile enthält den Code '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht gesetzt.",'.
162. Diese Zeile enthält den Code '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
163. Diese Zeile enthält den Code '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
164. Diese Zeile enthält den Code '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
165. Diese Zeile enthält den Code '"error.submission_not_found": "Einreichung nicht gefunden.",'.
166. Diese Zeile enthält den Code '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
167. Diese Zeile enthält den Code '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
168. Diese Zeile enthält den Code '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
169. Diese Zeile enthält den Code '"error.trace": "Stacktrace (nur Dev)",'.
170. Diese Zeile enthält den Code '"error.user_not_found": "Nutzer nicht gefunden.",'.
171. Diese Zeile enthält den Code '"error.username_invalid": "Le nom d'utilisateur doit contenir 3 a 30 caracteres et uniquement let...'.
172. Diese Zeile enthält den Code '"error.username_taken": "Ce nom d'utilisateur est deja utilise.",'.
173. Diese Zeile enthält den Code '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
174. Diese Zeile enthält den Code '"favorite.add": "Zu Favoriten",'.
175. Diese Zeile enthält den Code '"favorite.remove": "Aus Favoriten entfernen",'.
176. Diese Zeile enthält den Code '"favorites.empty": "Keine Favoriten gespeichert.",'.
177. Diese Zeile enthält den Code '"favorites.remove": "Favorit entfernen",'.
178. Diese Zeile enthält den Code '"favorites.title": "Favoriten",'.
179. Diese Zeile enthält den Code '"home.all_categories": "Toutes les categories",'.
180. Diese Zeile enthält den Code '"home.apply": "Appliquer",'.
181. Diese Zeile enthält den Code '"home.category": "Categorie",'.
182. Diese Zeile enthält den Code '"home.difficulty": "Difficulte",'.
183. Diese Zeile enthält den Code '"home.ingredient": "Ingredient",'.
184. Diese Zeile enthält den Code '"home.per_page": "Par page",'.
185. Diese Zeile enthält den Code '"home.title": "Decouvrir des recettes",'.
186. Diese Zeile enthält den Code '"home.title_contains": "Le titre contient",'.
187. Diese Zeile enthält den Code '"images.delete": "Loeschen",'.
188. Diese Zeile enthält den Code '"images.empty": "Noch keine Bilder vorhanden.",'.
189. Diese Zeile enthält den Code '"images.new_file": "Neue Bilddatei",'.
190. Diese Zeile enthält den Code '"images.primary": "Hauptbild",'.
191. Diese Zeile enthält den Code '"images.set_primary": "Als Hauptbild setzen",'.
192. Diese Zeile enthält den Code '"images.title": "Bilder",'.
193. Diese Zeile enthält den Code '"images.upload": "Bild hochladen",'.
194. Diese Zeile enthält den Code '"moderation.approve": "Approuver",'.
195. Diese Zeile enthält den Code '"moderation.pending": "En attente",'.
196. Diese Zeile enthält den Code '"moderation.reject": "Rejeter",'.
197. Diese Zeile enthält den Code '"moderation.title": "File de moderation",'.
198. Diese Zeile enthält den Code '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
199. Diese Zeile enthält den Code '"my_recipes.title": "Meine Rezepte",'.
200. Diese Zeile enthält den Code '"nav.admin": "Admin",'.
201. Diese Zeile enthält den Code '"nav.admin_submissions": "Moderation",'.
202. Diese Zeile enthält den Code '"nav.create_recipe": "Creer une recette",'.
203. Diese Zeile enthält den Code '"nav.discover": "Decouvrir des recettes",'.
204. Diese Zeile enthält den Code '"nav.favorites": "Favoris",'.
205. Diese Zeile enthält den Code '"nav.language": "Langue",'.
206. Diese Zeile enthält den Code '"nav.login": "Connexion",'.
207. Diese Zeile enthält den Code '"nav.logout": "Deconnexion",'.
208. Diese Zeile enthält den Code '"nav.my_recipes": "Mes recettes",'.
209. Diese Zeile enthält den Code '"nav.my_submissions": "Mes soumissions",'.
210. Diese Zeile enthält den Code '"nav.profile": "Mon profil",'.
211. Diese Zeile enthält den Code '"nav.publish_recipe": "Publier une recette",'.
212. Diese Zeile enthält den Code '"nav.register": "Inscription",'.
213. Diese Zeile enthält den Code '"nav.submit": "Soumettre une recette",'.
214. Diese Zeile enthält den Code '"nav.submit_recipe": "Soumettre une recette",'.
215. Diese Zeile enthält den Code '"pagination.first": "Premier",'.
216. Diese Zeile enthält den Code '"pagination.last": "Dernier",'.
217. Diese Zeile enthält den Code '"pagination.next": "Suivant",'.
218. Diese Zeile enthält den Code '"pagination.page": "Page",'.
219. Diese Zeile enthält den Code '"pagination.prev": "Precedent",'.
220. Diese Zeile enthält den Code '"pagination.previous": "Precedent",'.
221. Diese Zeile enthält den Code '"pagination.results_range": "Affichage {start}-{end} sur {total} recettes",'.
222. Diese Zeile enthält den Code '"profile.email": "E-Mail",'.
223. Diese Zeile enthält den Code '"profile.joined": "Registriert am",'.
224. Diese Zeile enthält den Code '"profile.role": "Rolle",'.
225. Diese Zeile enthält den Code '"profile.title": "Mein Profil",'.
226. Diese Zeile enthält den Code '"profile.user_uid": "Votre identifiant utilisateur",'.
227. Diese Zeile enthält den Code '"profile.username": "Nom d'utilisateur",'.
228. Diese Zeile enthält den Code '"profile.username_change_title": "Changer le nom d'utilisateur",'.
229. Diese Zeile enthält den Code '"profile.username_save": "Enregistrer le nom d'utilisateur",'.
230. Diese Zeile enthält den Code '"profile.username_updated": "Le nom d'utilisateur a ete mis a jour.",'.
231. Diese Zeile enthält den Code '"recipe.average_rating": "Durchschnittliche Bewertung",'.
232. Diese Zeile enthält den Code '"recipe.comment": "Kommentar",'.
233. Diese Zeile enthält den Code '"recipe.delete": "Loeschen",'.
234. Diese Zeile enthält den Code '"recipe.edit": "Bearbeiten",'.
235. Diese Zeile enthält den Code '"recipe.ingredients": "Zutaten",'.
236. Diese Zeile enthält den Code '"recipe.instructions": "Anleitung",'.
237. Diese Zeile enthält den Code '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
238. Diese Zeile enthält den Code '"recipe.no_results": "Aucune recette trouvee.",'.
239. Diese Zeile enthält den Code '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
240. Diese Zeile enthält den Code '"recipe.pdf_download": "PDF herunterladen",'.
241. Diese Zeile enthält den Code '"recipe.rating": "Bewertung",'.
242. Diese Zeile enthält den Code '"recipe.rating_short": "Bewertung",'.
243. Diese Zeile enthält den Code '"recipe.review_count_label": "Bewertungen",'.
244. Diese Zeile enthält den Code '"recipe.reviews": "Bewertungen",'.
245. Diese Zeile enthält den Code '"recipe.save_review": "Bewertung speichern",'.
246. Diese Zeile enthält den Code '"recipe_form.category": "Kategorie",'.
247. Diese Zeile enthält den Code '"recipe_form.create": "Erstellen",'.
248. Diese Zeile enthält den Code '"recipe_form.create_title": "Rezept veroeffentlichen",'.
249. Diese Zeile enthält den Code '"recipe_form.description": "Beschreibung",'.
250. Diese Zeile enthält den Code '"recipe_form.difficulty": "Schwierigkeit",'.
251. Diese Zeile enthält den Code '"recipe_form.edit_title": "Rezept bearbeiten",'.
252. Diese Zeile enthält den Code '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
253. Diese Zeile enthält den Code '"recipe_form.instructions": "Anleitung",'.
254. Diese Zeile enthält den Code '"recipe_form.new_category_label": "Neue Kategorie",'.
255. Diese Zeile enthält den Code '"recipe_form.new_category_option": "Neue Kategorie...",'.
256. Diese Zeile enthält den Code '"recipe_form.optional_image": "Optionales Bild",'.
257. Diese Zeile enthält den Code '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
258. Diese Zeile enthält den Code '"recipe_form.save": "Speichern",'.
259. Diese Zeile enthält den Code '"recipe_form.title": "Titel",'.
260. Diese Zeile enthält den Code '"recipe_form.title_image_url": "Titelbild-URL",'.
261. Diese Zeile enthält den Code '"role.admin": "Administrator",'.
262. Diese Zeile enthält den Code '"role.user": "Nutzer",'.
263. Diese Zeile enthält den Code '"sort.highest_rated": "Mieux notees",'.
264. Diese Zeile enthält den Code '"sort.lowest_rated": "Moins bien notees",'.
265. Diese Zeile enthält den Code '"sort.newest": "Plus recentes",'.
266. Diese Zeile enthält den Code '"sort.oldest": "Plus anciennes",'.
267. Diese Zeile enthält den Code '"sort.prep_time": "Temps de preparation",'.
268. Diese Zeile enthält den Code '"submission.admin_detail_title": "Einreichung",'.
269. Diese Zeile enthält den Code '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
270. Diese Zeile enthält den Code '"submission.admin_note": "Admin-Notiz",'.
271. Diese Zeile enthält den Code '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
272. Diese Zeile enthält den Code '"submission.admin_queue_title": "File de moderation",'.
273. Diese Zeile enthält den Code '"submission.approve_button": "Approuver",'.
274. Diese Zeile enthält den Code '"submission.approved": "Einreichung wurde freigegeben.",'.
275. Diese Zeile enthält den Code '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
276. Diese Zeile enthält den Code '"submission.category": "Kategorie",'.
277. Diese Zeile enthält den Code '"submission.default_description": "Rezept-Einreichung",'.
278. Diese Zeile enthält den Code '"submission.description": "Beschreibung",'.
279. Diese Zeile enthält den Code '"submission.difficulty": "Schwierigkeit",'.
280. Diese Zeile enthält den Code '"submission.edit_submission": "Einreichung bearbeiten",'.
281. Diese Zeile enthält den Code '"submission.guest": "Gast",'.
282. Diese Zeile enthält den Code '"submission.image_deleted": "Bild wurde entfernt.",'.
283. Diese Zeile enthält den Code '"submission.image_optional": "Optionales Bild",'.
284. Diese Zeile enthält den Code '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
285. Diese Zeile enthält den Code '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
286. Diese Zeile enthält den Code '"submission.instructions": "Anleitung",'.
287. Diese Zeile enthält den Code '"submission.moderation_actions": "Moderations-Aktionen",'.
288. Diese Zeile enthält den Code '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
289. Diese Zeile enthält den Code '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf Pruefung.",'.
290. Diese Zeile enthält den Code '"submission.my_title": "Mes soumissions",'.
291. Diese Zeile enthält den Code '"submission.new_category_label": "Neue Kategorie",'.
292. Diese Zeile enthält den Code '"submission.new_category_option": "Neue Kategorie...",'.
293. Diese Zeile enthält den Code '"submission.open_detail": "Details",'.
294. Diese Zeile enthält den Code '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
295. Diese Zeile enthält den Code '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
296. Diese Zeile enthält den Code '"submission.preview": "Vorschau",'.
297. Diese Zeile enthält den Code '"submission.reject_button": "Rejeter",'.
298. Diese Zeile enthält den Code '"submission.reject_reason": "Ablehnungsgrund",'.
299. Diese Zeile enthält den Code '"submission.rejected": "Einreichung wurde abgelehnt.",'.
300. Diese Zeile enthält den Code '"submission.save_changes": "Aenderungen speichern",'.
301. Diese Zeile enthält den Code '"submission.servings": "Portionen (optional)",'.
302. Diese Zeile enthält den Code '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
303. Diese Zeile enthält den Code '"submission.stats_approved": "Freigegeben",'.
304. Diese Zeile enthält den Code '"submission.stats_pending": "Ausstehend",'.
305. Diese Zeile enthält den Code '"submission.stats_rejected": "Abgelehnt",'.
306. Diese Zeile enthält den Code '"submission.status_all": "Alle",'.
307. Diese Zeile enthält den Code '"submission.status_approved": "Approuvee",'.
308. Diese Zeile enthält den Code '"submission.status_filter": "Status",'.
309. Diese Zeile enthält den Code '"submission.status_pending": "En attente",'.
310. Diese Zeile enthält den Code '"submission.status_rejected": "Rejetee",'.
311. Diese Zeile enthält den Code '"submission.submit_button": "Zur Pruefung einreichen",'.
312. Diese Zeile enthält den Code '"submission.submit_hint": "Les soumissions sont verifiees par les admins avant publication.",'.
313. Diese Zeile enthält den Code '"submission.submit_title": "Soumettre une recette",'.
314. Diese Zeile enthält den Code '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
315. Diese Zeile enthält den Code '"submission.table_action": "Aktion",'.
316. Diese Zeile enthält den Code '"submission.table_date": "Datum",'.
317. Diese Zeile enthält den Code '"submission.table_status": "Status",'.
318. Diese Zeile enthält den Code '"submission.table_submitter": "Einreicher",'.
319. Diese Zeile enthält den Code '"submission.table_title": "Titel",'.
320. Diese Zeile enthält den Code '"submission.thank_you": "Merci ! Votre recette a ete soumise pour moderation.",'.
321. Diese Zeile enthält den Code '"submission.title": "Titel",'.
322. Diese Zeile enthält den Code '"submission.updated": "Einreichung wurde aktualisiert."'.
323. Diese Zeile enthält den Code '}'.

## alembic/versions/20260303_0008_email_change_token_field.py

`$lang
"""add email change data to password reset tokens

Revision ID: 20260303_0008
Revises: 20260303_0007
Create Date: 2026-03-03 21:20:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0008"
down_revision: Union[str, None] = "20260303_0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("password_reset_tokens") as batch:
        batch.add_column(sa.Column("new_email_normalized", sa.String(length=255), nullable=True))
        batch.create_index("ix_password_reset_tokens_new_email_normalized", ["new_email_normalized"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("password_reset_tokens") as batch:
        batch.drop_index("ix_password_reset_tokens_new_email_normalized")
        batch.drop_column("new_email_normalized")

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '"""add email change data to password reset tokens'.
2. Diese Zeile ist leer und trennt Abschnitte.
3. Diese Zeile enthält den Code 'Revision ID: 20260303_0008'.
4. Diese Zeile enthält den Code 'Revises: 20260303_0007'.
5. Diese Zeile enthält den Code 'Create Date: 2026-03-03 21:20:00'.
6. Diese Zeile enthält den Code '"""'.
7. Diese Zeile ist leer und trennt Abschnitte.
8. Diese Zeile enthält den Code 'from typing import Sequence, Union'.
9. Diese Zeile ist leer und trennt Abschnitte.
10. Diese Zeile enthält den Code 'from alembic import op'.
11. Diese Zeile enthält den Code 'import sqlalchemy as sa'.
12. Diese Zeile ist leer und trennt Abschnitte.
13. Diese Zeile enthält den Code '# revision identifiers, used by Alembic.'.
14. Diese Zeile enthält den Code 'revision: str = "20260303_0008"'.
15. Diese Zeile enthält den Code 'down_revision: Union[str, None] = "20260303_0007"'.
16. Diese Zeile enthält den Code 'branch_labels: Union[str, Sequence[str], None] = None'.
17. Diese Zeile enthält den Code 'depends_on: Union[str, Sequence[str], None] = None'.
18. Diese Zeile ist leer und trennt Abschnitte.
19. Diese Zeile ist leer und trennt Abschnitte.
20. Diese Zeile enthält den Code 'def upgrade() -> None:'.
21. Diese Zeile enthält den Code 'with op.batch_alter_table("password_reset_tokens") as batch:'.
22. Diese Zeile enthält den Code 'batch.add_column(sa.Column("new_email_normalized", sa.String(length=255), nullable=True))'.
23. Diese Zeile enthält den Code 'batch.create_index("ix_password_reset_tokens_new_email_normalized", ["new_email_normalized"], uni...'.
24. Diese Zeile ist leer und trennt Abschnitte.
25. Diese Zeile ist leer und trennt Abschnitte.
26. Diese Zeile enthält den Code 'def downgrade() -> None:'.
27. Diese Zeile enthält den Code 'with op.batch_alter_table("password_reset_tokens") as batch:'.
28. Diese Zeile enthält den Code 'batch.drop_index("ix_password_reset_tokens_new_email_normalized")'.
29. Diese Zeile enthält den Code 'batch.drop_column("new_email_normalized")'.

## tests/test_email_change.py

`$lang
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select

from app.config import get_settings
from app.models import PasswordResetToken, User
from app.security import create_access_token, create_raw_reset_token, hash_password, hash_reset_token, normalize_username


def create_user(
    db,
    *,
    email: str,
    password: str,
    role: str = "user",
    username: str | None = None,
) -> User:
    user = User(
        email=email.strip().lower(),
        username=username,
        username_normalized=normalize_username(username) if username else None,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_client(client, user_uid: str, role: str = "user") -> None:
    token = create_access_token(user_uid, role)
    client.cookies.set("access_token", f"Bearer {token}")


def csrf_token(client, path: str = "/login") -> str:
    response = client.get(path)
    assert response.status_code == 200
    token = client.cookies.get("csrf_token")
    assert token
    return str(token)


def parse_email_change_token_from_outbox(outbox_path: Path) -> str:
    content = outbox_path.read_text(encoding="utf-8")
    marker = "/auth/change-email/confirm?token="
    index = content.rfind(marker)
    assert index >= 0
    token_start = index + len(marker)
    token_chars: list[str] = []
    for char in content[token_start:]:
        if char in "\n\r ":
            break
        token_chars.append(char)
    token = "".join(token_chars).strip()
    assert token
    return token


def test_request_email_change_creates_token_and_sends_mail(client, db_session_factory, tmp_path):
    settings = get_settings()
    outbox_file = tmp_path / "email_change_links.txt"
    settings.mail_outbox_email_change_path = str(outbox_file)

    with db_session_factory() as db:
        user = create_user(db, email="request-change@example.local", password="RequestPass123!", username="request.change")
        user_uid = user.user_uid

    authenticate_client(client, user_uid)
    csrf = csrf_token(client, "/auth/change-email")
    response = client.post(
        "/auth/change-email/request",
        data={"new_email": "new-address@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 200
    assert outbox_file.exists()

    raw_token = parse_email_change_token_from_outbox(outbox_file)

    with db_session_factory() as db:
        db_user = db.scalar(select(User).where(User.email == "request-change@example.local"))
        assert db_user is not None
        token_row = db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == db_user.id,
                PasswordResetToken.purpose == "email_change",
            )
        )
        assert token_row is not None
        assert token_row.token_hash == hash_reset_token(raw_token)
        assert token_row.new_email_normalized == "new-address@example.local"
        assert token_row.used_at is None


def test_confirm_email_change_updates_email_and_invalidates_token(client, db_session_factory, tmp_path):
    settings = get_settings()
    outbox_file = tmp_path / "email_change_links.txt"
    settings.mail_outbox_email_change_path = str(outbox_file)

    with db_session_factory() as db:
        user = create_user(db, email="confirm-change@example.local", password="ConfirmPass123!", username="confirm.change")
        user_uid = user.user_uid

    authenticate_client(client, user_uid)
    csrf = csrf_token(client, "/auth/change-email")
    request_response = client.post(
        "/auth/change-email/request",
        data={"new_email": "confirmed-address@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert request_response.status_code == 200

    raw_token = parse_email_change_token_from_outbox(outbox_file)

    csrf = csrf_token(client, f"/auth/change-email/confirm?token={raw_token}")
    confirm_response = client.post(
        "/auth/change-email/confirm",
        data={"token": raw_token, "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert confirm_response.status_code in {302, 303}

    with db_session_factory() as db:
        updated_user = db.scalar(select(User).where(User.user_uid == user_uid))
        assert updated_user is not None
        assert updated_user.email == "confirmed-address@example.local"
        token_row = db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.token_hash == hash_reset_token(raw_token),
                PasswordResetToken.purpose == "email_change",
            )
        )
        assert token_row is not None
        assert token_row.used_at is not None

    csrf = csrf_token(client, "/login")
    second_try = client.post(
        "/auth/change-email/confirm",
        data={"token": raw_token, "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert second_try.status_code == 400


def test_email_change_conflict_fails(client, db_session_factory):
    with db_session_factory() as db:
        requester = create_user(db, email="owner@example.local", password="OwnerPass123!", username="owner.user")
        create_user(db, email="already-used@example.local", password="TakenPass123!", username="taken.user")
        requester_uid = requester.user_uid

    authenticate_client(client, requester_uid)
    csrf = csrf_token(client, "/auth/change-email")
    response = client.post(
        "/auth/change-email/request",
        data={"new_email": "already-used@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert response.status_code == 409

    with db_session_factory() as db:
        db_requester = db.scalar(select(User).where(User.user_uid == requester.user_uid))
        assert db_requester is not None
        token_rows = db.scalars(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == db_requester.id,
                PasswordResetToken.purpose == "email_change",
            )
        ).all()
        assert token_rows == []


def test_email_change_expired_token_fails(client, db_session_factory):
    raw_token = create_raw_reset_token()
    with db_session_factory() as db:
        user = create_user(db, email="expired-change@example.local", password="ExpiredPass123!", username="expired.user")
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hash_reset_token(raw_token),
                new_email_normalized="after-expire@example.local",
                expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),
                purpose="email_change",
            )
        )
        db.commit()

    invalid_page = client.get(f"/auth/change-email/confirm?token={raw_token}")
    assert invalid_page.status_code == 400

    csrf = csrf_token(client, "/login")
    invalid_post = client.post(
        "/auth/change-email/confirm",
        data={"token": raw_token, "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert invalid_post.status_code == 400

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code 'from datetime import datetime, timedelta, timezone'.
2. Diese Zeile enthält den Code 'from pathlib import Path'.
3. Diese Zeile ist leer und trennt Abschnitte.
4. Diese Zeile enthält den Code 'from sqlalchemy import select'.
5. Diese Zeile ist leer und trennt Abschnitte.
6. Diese Zeile enthält den Code 'from app.config import get_settings'.
7. Diese Zeile enthält den Code 'from app.models import PasswordResetToken, User'.
8. Diese Zeile enthält den Code 'from app.security import create_access_token, create_raw_reset_token, hash_password, hash_reset_t...'.
9. Diese Zeile ist leer und trennt Abschnitte.
10. Diese Zeile ist leer und trennt Abschnitte.
11. Diese Zeile enthält den Code 'def create_user('.
12. Diese Zeile enthält den Code 'db,'.
13. Diese Zeile enthält den Code '*,'.
14. Diese Zeile enthält den Code 'email: str,'.
15. Diese Zeile enthält den Code 'password: str,'.
16. Diese Zeile enthält den Code 'role: str = "user",'.
17. Diese Zeile enthält den Code 'username: str | None = None,'.
18. Diese Zeile enthält den Code ') -> User:'.
19. Diese Zeile enthält den Code 'user = User('.
20. Diese Zeile enthält den Code 'email=email.strip().lower(),'.
21. Diese Zeile enthält den Code 'username=username,'.
22. Diese Zeile enthält den Code 'username_normalized=normalize_username(username) if username else None,'.
23. Diese Zeile enthält den Code 'hashed_password=hash_password(password),'.
24. Diese Zeile enthält den Code 'role=role,'.
25. Diese Zeile enthält den Code ')'.
26. Diese Zeile enthält den Code 'db.add(user)'.
27. Diese Zeile enthält den Code 'db.commit()'.
28. Diese Zeile enthält den Code 'db.refresh(user)'.
29. Diese Zeile enthält den Code 'return user'.
30. Diese Zeile ist leer und trennt Abschnitte.
31. Diese Zeile ist leer und trennt Abschnitte.
32. Diese Zeile enthält den Code 'def authenticate_client(client, user_uid: str, role: str = "user") -> None:'.
33. Diese Zeile enthält den Code 'token = create_access_token(user_uid, role)'.
34. Diese Zeile enthält den Code 'client.cookies.set("access_token", f"Bearer {token}")'.
35. Diese Zeile ist leer und trennt Abschnitte.
36. Diese Zeile ist leer und trennt Abschnitte.
37. Diese Zeile enthält den Code 'def csrf_token(client, path: str = "/login") -> str:'.
38. Diese Zeile enthält den Code 'response = client.get(path)'.
39. Diese Zeile enthält den Code 'assert response.status_code == 200'.
40. Diese Zeile enthält den Code 'token = client.cookies.get("csrf_token")'.
41. Diese Zeile enthält den Code 'assert token'.
42. Diese Zeile enthält den Code 'return str(token)'.
43. Diese Zeile ist leer und trennt Abschnitte.
44. Diese Zeile ist leer und trennt Abschnitte.
45. Diese Zeile enthält den Code 'def parse_email_change_token_from_outbox(outbox_path: Path) -> str:'.
46. Diese Zeile enthält den Code 'content = outbox_path.read_text(encoding="utf-8")'.
47. Diese Zeile enthält den Code 'marker = "/auth/change-email/confirm?token="'.
48. Diese Zeile enthält den Code 'index = content.rfind(marker)'.
49. Diese Zeile enthält den Code 'assert index >= 0'.
50. Diese Zeile enthält den Code 'token_start = index + len(marker)'.
51. Diese Zeile enthält den Code 'token_chars: list[str] = []'.
52. Diese Zeile enthält den Code 'for char in content[token_start:]:'.
53. Diese Zeile enthält den Code 'if char in "\n\r ":'.
54. Diese Zeile enthält den Code 'break'.
55. Diese Zeile enthält den Code 'token_chars.append(char)'.
56. Diese Zeile enthält den Code 'token = "".join(token_chars).strip()'.
57. Diese Zeile enthält den Code 'assert token'.
58. Diese Zeile enthält den Code 'return token'.
59. Diese Zeile ist leer und trennt Abschnitte.
60. Diese Zeile ist leer und trennt Abschnitte.
61. Diese Zeile enthält den Code 'def test_request_email_change_creates_token_and_sends_mail(client, db_session_factory, tmp_path):'.
62. Diese Zeile enthält den Code 'settings = get_settings()'.
63. Diese Zeile enthält den Code 'outbox_file = tmp_path / "email_change_links.txt"'.
64. Diese Zeile enthält den Code 'settings.mail_outbox_email_change_path = str(outbox_file)'.
65. Diese Zeile ist leer und trennt Abschnitte.
66. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
67. Diese Zeile enthält den Code 'user = create_user(db, email="request-change@example.local", password="RequestPass123!", username...'.
68. Diese Zeile enthält den Code 'user_uid = user.user_uid'.
69. Diese Zeile ist leer und trennt Abschnitte.
70. Diese Zeile enthält den Code 'authenticate_client(client, user_uid)'.
71. Diese Zeile enthält den Code 'csrf = csrf_token(client, "/auth/change-email")'.
72. Diese Zeile enthält den Code 'response = client.post('.
73. Diese Zeile enthält den Code '"/auth/change-email/request",'.
74. Diese Zeile enthält den Code 'data={"new_email": "new-address@example.local", "csrf_token": csrf},'.
75. Diese Zeile enthält den Code 'headers={"X-CSRF-Token": csrf},'.
76. Diese Zeile enthält den Code ')'.
77. Diese Zeile enthält den Code 'assert response.status_code == 200'.
78. Diese Zeile enthält den Code 'assert outbox_file.exists()'.
79. Diese Zeile ist leer und trennt Abschnitte.
80. Diese Zeile enthält den Code 'raw_token = parse_email_change_token_from_outbox(outbox_file)'.
81. Diese Zeile ist leer und trennt Abschnitte.
82. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
83. Diese Zeile enthält den Code 'db_user = db.scalar(select(User).where(User.email == "request-change@example.local"))'.
84. Diese Zeile enthält den Code 'assert db_user is not None'.
85. Diese Zeile enthält den Code 'token_row = db.scalar('.
86. Diese Zeile enthält den Code 'select(PasswordResetToken).where('.
87. Diese Zeile enthält den Code 'PasswordResetToken.user_id == db_user.id,'.
88. Diese Zeile enthält den Code 'PasswordResetToken.purpose == "email_change",'.
89. Diese Zeile enthält den Code ')'.
90. Diese Zeile enthält den Code ')'.
91. Diese Zeile enthält den Code 'assert token_row is not None'.
92. Diese Zeile enthält den Code 'assert token_row.token_hash == hash_reset_token(raw_token)'.
93. Diese Zeile enthält den Code 'assert token_row.new_email_normalized == "new-address@example.local"'.
94. Diese Zeile enthält den Code 'assert token_row.used_at is None'.
95. Diese Zeile ist leer und trennt Abschnitte.
96. Diese Zeile ist leer und trennt Abschnitte.
97. Diese Zeile enthält den Code 'def test_confirm_email_change_updates_email_and_invalidates_token(client, db_session_factory, tmp...'.
98. Diese Zeile enthält den Code 'settings = get_settings()'.
99. Diese Zeile enthält den Code 'outbox_file = tmp_path / "email_change_links.txt"'.
100. Diese Zeile enthält den Code 'settings.mail_outbox_email_change_path = str(outbox_file)'.
101. Diese Zeile ist leer und trennt Abschnitte.
102. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
103. Diese Zeile enthält den Code 'user = create_user(db, email="confirm-change@example.local", password="ConfirmPass123!", username...'.
104. Diese Zeile enthält den Code 'user_uid = user.user_uid'.
105. Diese Zeile ist leer und trennt Abschnitte.
106. Diese Zeile enthält den Code 'authenticate_client(client, user_uid)'.
107. Diese Zeile enthält den Code 'csrf = csrf_token(client, "/auth/change-email")'.
108. Diese Zeile enthält den Code 'request_response = client.post('.
109. Diese Zeile enthält den Code '"/auth/change-email/request",'.
110. Diese Zeile enthält den Code 'data={"new_email": "confirmed-address@example.local", "csrf_token": csrf},'.
111. Diese Zeile enthält den Code 'headers={"X-CSRF-Token": csrf},'.
112. Diese Zeile enthält den Code ')'.
113. Diese Zeile enthält den Code 'assert request_response.status_code == 200'.
114. Diese Zeile ist leer und trennt Abschnitte.
115. Diese Zeile enthält den Code 'raw_token = parse_email_change_token_from_outbox(outbox_file)'.
116. Diese Zeile ist leer und trennt Abschnitte.
117. Diese Zeile enthält den Code 'csrf = csrf_token(client, f"/auth/change-email/confirm?token={raw_token}")'.
118. Diese Zeile enthält den Code 'confirm_response = client.post('.
119. Diese Zeile enthält den Code '"/auth/change-email/confirm",'.
120. Diese Zeile enthält den Code 'data={"token": raw_token, "csrf_token": csrf},'.
121. Diese Zeile enthält den Code 'headers={"X-CSRF-Token": csrf},'.
122. Diese Zeile enthält den Code 'follow_redirects=False,'.
123. Diese Zeile enthält den Code ')'.
124. Diese Zeile enthält den Code 'assert confirm_response.status_code in {302, 303}'.
125. Diese Zeile ist leer und trennt Abschnitte.
126. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
127. Diese Zeile enthält den Code 'updated_user = db.scalar(select(User).where(User.user_uid == user_uid))'.
128. Diese Zeile enthält den Code 'assert updated_user is not None'.
129. Diese Zeile enthält den Code 'assert updated_user.email == "confirmed-address@example.local"'.
130. Diese Zeile enthält den Code 'token_row = db.scalar('.
131. Diese Zeile enthält den Code 'select(PasswordResetToken).where('.
132. Diese Zeile enthält den Code 'PasswordResetToken.token_hash == hash_reset_token(raw_token),'.
133. Diese Zeile enthält den Code 'PasswordResetToken.purpose == "email_change",'.
134. Diese Zeile enthält den Code ')'.
135. Diese Zeile enthält den Code ')'.
136. Diese Zeile enthält den Code 'assert token_row is not None'.
137. Diese Zeile enthält den Code 'assert token_row.used_at is not None'.
138. Diese Zeile ist leer und trennt Abschnitte.
139. Diese Zeile enthält den Code 'csrf = csrf_token(client, "/login")'.
140. Diese Zeile enthält den Code 'second_try = client.post('.
141. Diese Zeile enthält den Code '"/auth/change-email/confirm",'.
142. Diese Zeile enthält den Code 'data={"token": raw_token, "csrf_token": csrf},'.
143. Diese Zeile enthält den Code 'headers={"X-CSRF-Token": csrf},'.
144. Diese Zeile enthält den Code ')'.
145. Diese Zeile enthält den Code 'assert second_try.status_code == 400'.
146. Diese Zeile ist leer und trennt Abschnitte.
147. Diese Zeile ist leer und trennt Abschnitte.
148. Diese Zeile enthält den Code 'def test_email_change_conflict_fails(client, db_session_factory):'.
149. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
150. Diese Zeile enthält den Code 'requester = create_user(db, email="owner@example.local", password="OwnerPass123!", username="owne...'.
151. Diese Zeile enthält den Code 'create_user(db, email="already-used@example.local", password="TakenPass123!", username="taken.user")'.
152. Diese Zeile enthält den Code 'requester_uid = requester.user_uid'.
153. Diese Zeile ist leer und trennt Abschnitte.
154. Diese Zeile enthält den Code 'authenticate_client(client, requester_uid)'.
155. Diese Zeile enthält den Code 'csrf = csrf_token(client, "/auth/change-email")'.
156. Diese Zeile enthält den Code 'response = client.post('.
157. Diese Zeile enthält den Code '"/auth/change-email/request",'.
158. Diese Zeile enthält den Code 'data={"new_email": "already-used@example.local", "csrf_token": csrf},'.
159. Diese Zeile enthält den Code 'headers={"X-CSRF-Token": csrf},'.
160. Diese Zeile enthält den Code ')'.
161. Diese Zeile enthält den Code 'assert response.status_code == 409'.
162. Diese Zeile ist leer und trennt Abschnitte.
163. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
164. Diese Zeile enthält den Code 'db_requester = db.scalar(select(User).where(User.user_uid == requester.user_uid))'.
165. Diese Zeile enthält den Code 'assert db_requester is not None'.
166. Diese Zeile enthält den Code 'token_rows = db.scalars('.
167. Diese Zeile enthält den Code 'select(PasswordResetToken).where('.
168. Diese Zeile enthält den Code 'PasswordResetToken.user_id == db_requester.id,'.
169. Diese Zeile enthält den Code 'PasswordResetToken.purpose == "email_change",'.
170. Diese Zeile enthält den Code ')'.
171. Diese Zeile enthält den Code ').all()'.
172. Diese Zeile enthält den Code 'assert token_rows == []'.
173. Diese Zeile ist leer und trennt Abschnitte.
174. Diese Zeile ist leer und trennt Abschnitte.
175. Diese Zeile enthält den Code 'def test_email_change_expired_token_fails(client, db_session_factory):'.
176. Diese Zeile enthält den Code 'raw_token = create_raw_reset_token()'.
177. Diese Zeile enthält den Code 'with db_session_factory() as db:'.
178. Diese Zeile enthält den Code 'user = create_user(db, email="expired-change@example.local", password="ExpiredPass123!", username...'.
179. Diese Zeile enthält den Code 'db.add('.
180. Diese Zeile enthält den Code 'PasswordResetToken('.
181. Diese Zeile enthält den Code 'user_id=user.id,'.
182. Diese Zeile enthält den Code 'token_hash=hash_reset_token(raw_token),'.
183. Diese Zeile enthält den Code 'new_email_normalized="after-expire@example.local",'.
184. Diese Zeile enthält den Code 'expires_at=datetime.now(timezone.utc) - timedelta(minutes=1),'.
185. Diese Zeile enthält den Code 'purpose="email_change",'.
186. Diese Zeile enthält den Code ')'.
187. Diese Zeile enthält den Code ')'.
188. Diese Zeile enthält den Code 'db.commit()'.
189. Diese Zeile ist leer und trennt Abschnitte.
190. Diese Zeile enthält den Code 'invalid_page = client.get(f"/auth/change-email/confirm?token={raw_token}")'.
191. Diese Zeile enthält den Code 'assert invalid_page.status_code == 400'.
192. Diese Zeile ist leer und trennt Abschnitte.
193. Diese Zeile enthält den Code 'csrf = csrf_token(client, "/login")'.
194. Diese Zeile enthält den Code 'invalid_post = client.post('.
195. Diese Zeile enthält den Code '"/auth/change-email/confirm",'.
196. Diese Zeile enthält den Code 'data={"token": raw_token, "csrf_token": csrf},'.
197. Diese Zeile enthält den Code 'headers={"X-CSRF-Token": csrf},'.
198. Diese Zeile enthält den Code ')'.
199. Diese Zeile enthält den Code 'assert invalid_post.status_code == 400'.

## README_EMAIL_CHANGE.md

`$lang
# README_EMAIL_CHANGE.md

## Zweck

Dieses Modul fuegt eine sichere E-Mail-Aenderung mit Bestaetigungslink hinzu.
Die E-Mail wird erst aktualisiert, nachdem der Link auf der neuen Adresse bestaetigt wurde.

## Ablauf

1. Eingeloggter User oeffnet `GET /auth/change-email`.
2. `POST /auth/change-email/request` prueft die neue E-Mail und erstellt ein Single-Use-Token.
3. Der Link `{APP_URL}/auth/change-email/confirm?token=<raw_token>` wird an die neue E-Mail gesendet.
4. `GET /auth/change-email/confirm` validiert das Token und zeigt die Bestaetigungsseite.
5. `POST /auth/change-email/confirm` aktualisiert `users.email` und markiert das Token als verwendet.

## Sicherheit

- Raw-Token wird nie in der Datenbank gespeichert, nur `token_hash`.
- Token sind single-use (`used_at`) und laufen ab (`expires_at`).
- Alle POST-Routen sind CSRF-geschuetzt.
- Rate-Limits:
  - `POST /auth/change-email/request`: `3/min` pro User und `5/min` pro IP
  - `POST /auth/change-email/confirm`: `5/min` pro IP
- Konflikte werden als "E-Mail nicht verfuegbar" behandelt.

## Datenmodell

Es wird die bestehende Tabelle `password_reset_tokens` wiederverwendet:

- `purpose = "email_change"`
- `new_email_normalized` speichert die angeforderte Zieladresse

Migration: `20260303_0008_email_change_token_field.py`

## ENV-Variablen

- `APP_URL` (z. B. `http://127.0.0.1:8010`)
- `PASSWORD_RESET_TOKEN_MINUTES` (gilt auch fuer E-Mail-Aenderungstoken)
- `MAIL_OUTBOX_EMAIL_CHANGE_PATH` (DEV-Outbox-Datei)
- SMTP in PROD:
  - `SMTP_HOST`
  - `SMTP_PORT`
  - `SMTP_USER`
  - `SMTP_PASSWORD`
  - `SMTP_FROM`

## DEV-Mailer

In `APP_ENV=dev` wird der Link in `MAIL_OUTBOX_EMAIL_CHANGE_PATH` geschrieben.
In `APP_ENV=prod` wird ueber SMTP gesendet.

## Tests

`tests/test_email_change.py` deckt ab:

- Token-Erstellung + Outbox-Versand
- Erfolgreiche Bestaetigung mit Single-Use-Verhalten
- Konfliktfall bei bereits vergebener E-Mail
- Ablauf eines abgelaufenen Tokens

```

ZEILEN-ERKLÄRUNG

1. Diese Zeile enthält den Code '# README_EMAIL_CHANGE.md'.
2. Diese Zeile ist leer und trennt Abschnitte.
3. Diese Zeile enthält den Code '## Zweck'.
4. Diese Zeile ist leer und trennt Abschnitte.
5. Diese Zeile enthält den Code 'Dieses Modul fuegt eine sichere E-Mail-Aenderung mit Bestaetigungslink hinzu.'.
6. Diese Zeile enthält den Code 'Die E-Mail wird erst aktualisiert, nachdem der Link auf der neuen Adresse bestaetigt wurde.'.
7. Diese Zeile ist leer und trennt Abschnitte.
8. Diese Zeile enthält den Code '## Ablauf'.
9. Diese Zeile ist leer und trennt Abschnitte.
10. Diese Zeile enthält den Code '1. Eingeloggter User oeffnet 'GET /auth/change-email'.'.
11. Diese Zeile enthält den Code '2. 'POST /auth/change-email/request' prueft die neue E-Mail und erstellt ein Single-Use-Token.'.
12. Diese Zeile enthält den Code '3. Der Link '{APP_URL}/auth/change-email/confirm?token=<raw_token>' wird an die neue E-Mail gesen...'.
13. Diese Zeile enthält den Code '4. 'GET /auth/change-email/confirm' validiert das Token und zeigt die Bestaetigungsseite.'.
14. Diese Zeile enthält den Code '5. 'POST /auth/change-email/confirm' aktualisiert 'users.email' und markiert das Token als verwen...'.
15. Diese Zeile ist leer und trennt Abschnitte.
16. Diese Zeile enthält den Code '## Sicherheit'.
17. Diese Zeile ist leer und trennt Abschnitte.
18. Diese Zeile enthält den Code '- Raw-Token wird nie in der Datenbank gespeichert, nur 'token_hash'.'.
19. Diese Zeile enthält den Code '- Token sind single-use ('used_at') und laufen ab ('expires_at').'.
20. Diese Zeile enthält den Code '- Alle POST-Routen sind CSRF-geschuetzt.'.
21. Diese Zeile enthält den Code '- Rate-Limits:'.
22. Diese Zeile enthält den Code '- 'POST /auth/change-email/request': '3/min' pro User und '5/min' pro IP'.
23. Diese Zeile enthält den Code '- 'POST /auth/change-email/confirm': '5/min' pro IP'.
24. Diese Zeile enthält den Code '- Konflikte werden als "E-Mail nicht verfuegbar" behandelt.'.
25. Diese Zeile ist leer und trennt Abschnitte.
26. Diese Zeile enthält den Code '## Datenmodell'.
27. Diese Zeile ist leer und trennt Abschnitte.
28. Diese Zeile enthält den Code 'Es wird die bestehende Tabelle 'password_reset_tokens' wiederverwendet:'.
29. Diese Zeile ist leer und trennt Abschnitte.
30. Diese Zeile enthält den Code '- 'purpose = "email_change"''.
31. Diese Zeile enthält den Code '- 'new_email_normalized' speichert die angeforderte Zieladresse'.
32. Diese Zeile ist leer und trennt Abschnitte.
33. Diese Zeile enthält den Code 'Migration: '20260303_0008_email_change_token_field.py''.
34. Diese Zeile ist leer und trennt Abschnitte.
35. Diese Zeile enthält den Code '## ENV-Variablen'.
36. Diese Zeile ist leer und trennt Abschnitte.
37. Diese Zeile enthält den Code '- 'APP_URL' (z. B. 'http://127.0.0.1:8010')'.
38. Diese Zeile enthält den Code '- 'PASSWORD_RESET_TOKEN_MINUTES' (gilt auch fuer E-Mail-Aenderungstoken)'.
39. Diese Zeile enthält den Code '- 'MAIL_OUTBOX_EMAIL_CHANGE_PATH' (DEV-Outbox-Datei)'.
40. Diese Zeile enthält den Code '- SMTP in PROD:'.
41. Diese Zeile enthält den Code '- 'SMTP_HOST''.
42. Diese Zeile enthält den Code '- 'SMTP_PORT''.
43. Diese Zeile enthält den Code '- 'SMTP_USER''.
44. Diese Zeile enthält den Code '- 'SMTP_PASSWORD''.
45. Diese Zeile enthält den Code '- 'SMTP_FROM''.
46. Diese Zeile ist leer und trennt Abschnitte.
47. Diese Zeile enthält den Code '## DEV-Mailer'.
48. Diese Zeile ist leer und trennt Abschnitte.
49. Diese Zeile enthält den Code 'In 'APP_ENV=dev' wird der Link in 'MAIL_OUTBOX_EMAIL_CHANGE_PATH' geschrieben.'.
50. Diese Zeile enthält den Code 'In 'APP_ENV=prod' wird ueber SMTP gesendet.'.
51. Diese Zeile ist leer und trennt Abschnitte.
52. Diese Zeile enthält den Code '## Tests'.
53. Diese Zeile ist leer und trennt Abschnitte.
54. Diese Zeile enthält den Code ''tests/test_email_change.py' deckt ab:'.
55. Diese Zeile ist leer und trennt Abschnitte.
56. Diese Zeile enthält den Code '- Token-Erstellung + Outbox-Versand'.
57. Diese Zeile enthält den Code '- Erfolgreiche Bestaetigung mit Single-Use-Verhalten'.
58. Diese Zeile enthält den Code '- Konfliktfall bei bereits vergebener E-Mail'.
59. Diese Zeile enthält den Code '- Ablauf eines abgelaufenen Tokens'.


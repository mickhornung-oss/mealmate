# Deliverable: Auth & Account Recovery

## Betroffene Dateien
- `app/config.py`
- `app/models.py`
- `alembic/versions/20260303_0007_auth_recovery_fields.py`
- `app/mailer.py`
- `app/security_events.py`
- `app/security.py`
- `app/dependencies.py`
- `app/routers/auth.py`
- `app/templates/auth_login.html`
- `app/templates/auth_register.html`
- `app/templates/me.html`
- `app/templates/auth_forgot_password.html`
- `app/templates/auth_reset_password.html`
- `.env.example`
- `app/i18n/locales/de.json`
- `app/i18n/locales/en.json`
- `app/i18n/locales/fr.json`
- `tests/test_auth_recovery.py`
- `README_AUTH_RECOVERY.md`

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
    csrf_cookie_name: str = "csrf_token"
    csrf_header_name: str = "X-CSRF-Token"
    password_reset_token_minutes: int = 30
    max_upload_mb: int = 4
    max_csv_upload_mb: int = 10
    allowed_image_types: Annotated[list[str], NoDecode] = ["image/png", "image/jpeg", "image/webp"]
    mail_outbox_path: str = "outbox/reset_links.txt"
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
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'from functools import lru_cache'.
2. Diese Zeile definiert den Abschnitt 'from typing import Annotated, Literal'.
3. Diese Zeile ist leer und trennt den Inhalt lesbar.
4. Diese Zeile definiert den Abschnitt 'from pydantic import AnyHttpUrl, field_validator'.
5. Diese Zeile definiert den Abschnitt 'from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict'.
6. Diese Zeile ist leer und trennt den Inhalt lesbar.
7. Diese Zeile ist leer und trennt den Inhalt lesbar.
8. Diese Zeile definiert den Abschnitt 'class Settings(BaseSettings):'.
9. Diese Zeile definiert den Abschnitt 'model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ig...'.
10. Diese Zeile ist leer und trennt den Inhalt lesbar.
11. Diese Zeile definiert den Abschnitt 'app_name: str = "MealMate"'.
12. Diese Zeile definiert den Abschnitt 'app_env: Literal["dev", "prod"] = "dev"'.
13. Diese Zeile definiert den Abschnitt 'app_url: AnyHttpUrl = "http://localhost:8000"'.
14. Diese Zeile definiert den Abschnitt 'secret_key: str = "change-me"'.
15. Diese Zeile definiert den Abschnitt 'algorithm: str = "HS256"'.
16. Diese Zeile definiert den Abschnitt 'token_expire_minutes: int = 60'.
17. Diese Zeile definiert den Abschnitt 'database_url: str = "sqlite:///./mealmate.db"'.
18. Diese Zeile definiert den Abschnitt 'allowed_hosts: Annotated[list[str], NoDecode] = ["*"]'.
19. Diese Zeile definiert den Abschnitt 'cookie_secure: bool | None = None'.
20. Diese Zeile definiert den Abschnitt 'force_https: bool | None = None'.
21. Diese Zeile definiert den Abschnitt 'log_level: str = "INFO"'.
22. Diese Zeile definiert den Abschnitt 'csrf_cookie_name: str = "csrf_token"'.
23. Diese Zeile definiert den Abschnitt 'csrf_header_name: str = "X-CSRF-Token"'.
24. Diese Zeile definiert den Abschnitt 'password_reset_token_minutes: int = 30'.
25. Diese Zeile definiert den Abschnitt 'max_upload_mb: int = 4'.
26. Diese Zeile definiert den Abschnitt 'max_csv_upload_mb: int = 10'.
27. Diese Zeile definiert den Abschnitt 'allowed_image_types: Annotated[list[str], NoDecode] = ["image/png", "image/jpeg", "imag...'.
28. Diese Zeile definiert den Abschnitt 'mail_outbox_path: str = "outbox/reset_links.txt"'.
29. Diese Zeile definiert den Abschnitt 'smtp_host: str | None = None'.
30. Diese Zeile definiert den Abschnitt 'smtp_port: int = 587'.
31. Diese Zeile definiert den Abschnitt 'smtp_user: str | None = None'.
32. Diese Zeile definiert den Abschnitt 'smtp_password: str | None = None'.
33. Diese Zeile definiert den Abschnitt 'smtp_from: str = "no-reply@mealmate.local"'.
34. Diese Zeile definiert den Abschnitt 'security_event_retention_days: int = 30'.
35. Diese Zeile definiert den Abschnitt 'security_event_max_rows: int = 5000'.
36. Diese Zeile definiert den Abschnitt 'enable_kochwiki_seed: bool = False'.
37. Diese Zeile definiert den Abschnitt 'auto_seed_kochwiki: bool = False'.
38. Diese Zeile definiert den Abschnitt 'kochwiki_csv_path: str = "rezepte_kochwiki_clean_3713.csv"'.
39. Diese Zeile definiert den Abschnitt 'import_download_images: bool = False'.
40. Diese Zeile definiert den Abschnitt 'seed_admin_email: str = "admin@mealmate.local"'.
41. Diese Zeile definiert den Abschnitt 'seed_admin_password: str = "AdminPass123!"'.
42. Diese Zeile ist leer und trennt den Inhalt lesbar.
43. Diese Zeile definiert den Abschnitt '@field_validator("allowed_image_types", mode="before")'.
44. Diese Zeile definiert den Abschnitt '@classmethod'.
45. Diese Zeile definiert den Abschnitt 'def parse_allowed_image_types(cls, value: str | list[str]) -> list[str]:'.
46. Diese Zeile definiert den Abschnitt 'if isinstance(value, list):'.
47. Diese Zeile definiert den Abschnitt 'return [item.strip() for item in value if item.strip()]'.
48. Diese Zeile definiert den Abschnitt 'return [item.strip() for item in value.split(",") if item.strip()]'.
49. Diese Zeile ist leer und trennt den Inhalt lesbar.
50. Diese Zeile definiert den Abschnitt '@field_validator("allowed_hosts", mode="before")'.
51. Diese Zeile definiert den Abschnitt '@classmethod'.
52. Diese Zeile definiert den Abschnitt 'def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:'.
53. Diese Zeile definiert den Abschnitt 'if isinstance(value, list):'.
54. Diese Zeile definiert den Abschnitt 'hosts = [item.strip() for item in value if item.strip()]'.
55. Diese Zeile definiert den Abschnitt 'else:'.
56. Diese Zeile definiert den Abschnitt 'hosts = [item.strip() for item in value.split(",") if item.strip()]'.
57. Diese Zeile definiert den Abschnitt 'return hosts or ["*"]'.
58. Diese Zeile ist leer und trennt den Inhalt lesbar.
59. Diese Zeile definiert den Abschnitt '@field_validator("log_level", mode="before")'.
60. Diese Zeile definiert den Abschnitt '@classmethod'.
61. Diese Zeile definiert den Abschnitt 'def parse_log_level(cls, value: str) -> str:'.
62. Diese Zeile definiert den Abschnitt 'return str(value).strip().upper() or "INFO"'.
63. Diese Zeile ist leer und trennt den Inhalt lesbar.
64. Diese Zeile definiert den Abschnitt '@property'.
65. Diese Zeile definiert den Abschnitt 'def sqlalchemy_database_url(self) -> str:'.
66. Diese Zeile definiert den Abschnitt 'url = self.database_url.strip()'.
67. Diese Zeile definiert den Abschnitt 'if url.startswith("postgres://"):'.
68. Diese Zeile definiert den Abschnitt 'return "postgresql+psycopg://" + url[len("postgres://") :]'.
69. Diese Zeile definiert den Abschnitt 'if url.startswith("postgresql://"):'.
70. Diese Zeile definiert den Abschnitt 'return "postgresql+psycopg://" + url[len("postgresql://") :]'.
71. Diese Zeile definiert den Abschnitt 'return url'.
72. Diese Zeile ist leer und trennt den Inhalt lesbar.
73. Diese Zeile definiert den Abschnitt '@property'.
74. Diese Zeile definiert den Abschnitt 'def is_sqlite(self) -> bool:'.
75. Diese Zeile definiert den Abschnitt 'return self.sqlalchemy_database_url.startswith("sqlite")'.
76. Diese Zeile ist leer und trennt den Inhalt lesbar.
77. Diese Zeile definiert den Abschnitt '@property'.
78. Diese Zeile definiert den Abschnitt 'def prod_mode(self) -> bool:'.
79. Diese Zeile definiert den Abschnitt 'return self.app_env == "prod"'.
80. Diese Zeile ist leer und trennt den Inhalt lesbar.
81. Diese Zeile definiert den Abschnitt '@property'.
82. Diese Zeile definiert den Abschnitt 'def resolved_cookie_secure(self) -> bool:'.
83. Diese Zeile definiert den Abschnitt 'if self.cookie_secure is None:'.
84. Diese Zeile definiert den Abschnitt 'return self.prod_mode'.
85. Diese Zeile definiert den Abschnitt 'return self.cookie_secure'.
86. Diese Zeile ist leer und trennt den Inhalt lesbar.
87. Diese Zeile definiert den Abschnitt '@property'.
88. Diese Zeile definiert den Abschnitt 'def resolved_force_https(self) -> bool:'.
89. Diese Zeile definiert den Abschnitt 'if self.force_https is None:'.
90. Diese Zeile definiert den Abschnitt 'return self.prod_mode'.
91. Diese Zeile definiert den Abschnitt 'return self.force_https'.
92. Diese Zeile ist leer und trennt den Inhalt lesbar.
93. Diese Zeile ist leer und trennt den Inhalt lesbar.
94. Diese Zeile definiert den Abschnitt '@lru_cache'.
95. Diese Zeile definiert den Abschnitt 'def get_settings() -> Settings:'.
96. Diese Zeile definiert den Abschnitt 'return Settings()'.

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
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'from datetime import datetime, timezone'.
2. Diese Zeile definiert den Abschnitt 'from uuid import uuid4'.
3. Diese Zeile ist leer und trennt den Inhalt lesbar.
4. Diese Zeile definiert den Abschnitt 'from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, LargeBinary, Strin...'.
5. Diese Zeile definiert den Abschnitt 'from sqlalchemy.orm import Mapped, mapped_column, relationship'.
6. Diese Zeile ist leer und trennt den Inhalt lesbar.
7. Diese Zeile definiert den Abschnitt 'from app.database import Base'.
8. Diese Zeile ist leer und trennt den Inhalt lesbar.
9. Diese Zeile ist leer und trennt den Inhalt lesbar.
10. Diese Zeile definiert den Abschnitt 'def utc_now() -> datetime:'.
11. Diese Zeile definiert den Abschnitt 'return datetime.now(timezone.utc)'.
12. Diese Zeile ist leer und trennt den Inhalt lesbar.
13. Diese Zeile ist leer und trennt den Inhalt lesbar.
14. Diese Zeile definiert den Abschnitt 'SUBMISSION_STATUS_ENUM = Enum('.
15. Diese Zeile definiert den Abschnitt '"pending",'.
16. Diese Zeile definiert den Abschnitt '"approved",'.
17. Diese Zeile definiert den Abschnitt '"rejected",'.
18. Diese Zeile definiert den Abschnitt 'name="submission_status",'.
19. Diese Zeile definiert den Abschnitt 'native_enum=False,'.
20. Diese Zeile definiert den Abschnitt ')'.
21. Diese Zeile ist leer und trennt den Inhalt lesbar.
22. Diese Zeile ist leer und trennt den Inhalt lesbar.
23. Diese Zeile definiert den Abschnitt 'class User(Base):'.
24. Diese Zeile definiert den Abschnitt '__tablename__ = "users"'.
25. Diese Zeile ist leer und trennt den Inhalt lesbar.
26. Diese Zeile definiert den Abschnitt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
27. Diese Zeile definiert den Abschnitt 'user_uid: Mapped[str] = mapped_column(String(36), unique=True, nullable=False, default=...'.
28. Diese Zeile definiert den Abschnitt 'email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)'.
29. Diese Zeile definiert den Abschnitt 'username: Mapped[str | None] = mapped_column(String(30), unique=True, nullable=True, in...'.
30. Diese Zeile definiert den Abschnitt 'username_normalized: Mapped[str | None] = mapped_column(String(30), unique=True, nullab...'.
31. Diese Zeile definiert den Abschnitt 'hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)'.
32. Diese Zeile definiert den Abschnitt 'role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)'.
33. Diese Zeile definiert den Abschnitt 'last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullabl...'.
34. Diese Zeile definiert den Abschnitt 'last_login_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)'.
35. Diese Zeile definiert den Abschnitt 'last_login_user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)'.
36. Diese Zeile definiert den Abschnitt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
37. Diese Zeile ist leer und trennt den Inhalt lesbar.
38. Diese Zeile definiert den Abschnitt 'recipes: Mapped[list["Recipe"]] = relationship(back_populates="creator", cascade="all, ...'.
39. Diese Zeile definiert den Abschnitt 'reviews: Mapped[list["Review"]] = relationship(back_populates="user", cascade="all, del...'.
40. Diese Zeile definiert den Abschnitt 'favorites: Mapped[list["Favorite"]] = relationship(back_populates="user", cascade="all,...'.
41. Diese Zeile definiert den Abschnitt 'submissions: Mapped[list["RecipeSubmission"]] = relationship('.
42. Diese Zeile definiert den Abschnitt 'back_populates="submitter_user",'.
43. Diese Zeile definiert den Abschnitt 'cascade="all, delete-orphan",'.
44. Diese Zeile definiert den Abschnitt 'foreign_keys="RecipeSubmission.submitter_user_id",'.
45. Diese Zeile definiert den Abschnitt ')'.
46. Diese Zeile definiert den Abschnitt 'reviewed_submissions: Mapped[list["RecipeSubmission"]] = relationship('.
47. Diese Zeile definiert den Abschnitt 'back_populates="reviewed_by_admin",'.
48. Diese Zeile definiert den Abschnitt 'foreign_keys="RecipeSubmission.reviewed_by_admin_id",'.
49. Diese Zeile definiert den Abschnitt ')'.
50. Diese Zeile definiert den Abschnitt 'password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship('.
51. Diese Zeile definiert den Abschnitt 'back_populates="user",'.
52. Diese Zeile definiert den Abschnitt 'cascade="all, delete-orphan",'.
53. Diese Zeile definiert den Abschnitt ')'.
54. Diese Zeile definiert den Abschnitt 'security_events: Mapped[list["SecurityEvent"]] = relationship('.
55. Diese Zeile definiert den Abschnitt 'back_populates="user",'.
56. Diese Zeile definiert den Abschnitt ')'.
57. Diese Zeile ist leer und trennt den Inhalt lesbar.
58. Diese Zeile ist leer und trennt den Inhalt lesbar.
59. Diese Zeile definiert den Abschnitt 'class Recipe(Base):'.
60. Diese Zeile definiert den Abschnitt '__tablename__ = "recipes"'.
61. Diese Zeile ist leer und trennt den Inhalt lesbar.
62. Diese Zeile definiert den Abschnitt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
63. Diese Zeile definiert den Abschnitt 'title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)'.
64. Diese Zeile definiert den Abschnitt 'title_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
65. Diese Zeile definiert den Abschnitt 'source: Mapped[str] = mapped_column(String(50), nullable=False, default="user", index=T...'.
66. Diese Zeile definiert den Abschnitt 'source_uuid: Mapped[str | None] = mapped_column(String(120), nullable=True, unique=True...'.
67. Diese Zeile definiert den Abschnitt 'source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
68. Diese Zeile definiert den Abschnitt 'source_image_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)'.
69. Diese Zeile definiert den Abschnitt 'servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)'.
70. Diese Zeile definiert den Abschnitt 'total_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
71. Diese Zeile definiert den Abschnitt 'is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index...'.
72. Diese Zeile definiert den Abschnitt 'description: Mapped[str] = mapped_column(Text, nullable=False)'.
73. Diese Zeile definiert den Abschnitt 'instructions: Mapped[str] = mapped_column(Text, nullable=False)'.
74. Diese Zeile definiert den Abschnitt 'category: Mapped[str] = mapped_column(String(120), nullable=False, index=True)'.
75. Diese Zeile definiert den Abschnitt 'prep_time_minutes: Mapped[int] = mapped_column(Integer, nullable=False, index=True)'.
76. Diese Zeile definiert den Abschnitt 'difficulty: Mapped[str] = mapped_column(String(30), nullable=False, index=True)'.
77. Diese Zeile definiert den Abschnitt 'creator_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nul...'.
78. Diese Zeile definiert den Abschnitt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
79. Diese Zeile ist leer und trennt den Inhalt lesbar.
80. Diese Zeile definiert den Abschnitt 'creator: Mapped["User"] = relationship(back_populates="recipes")'.
81. Diese Zeile definiert den Abschnitt 'recipe_ingredients: Mapped[list["RecipeIngredient"]] = relationship('.
82. Diese Zeile definiert den Abschnitt 'back_populates="recipe",'.
83. Diese Zeile definiert den Abschnitt 'cascade="all, delete-orphan",'.
84. Diese Zeile definiert den Abschnitt ')'.
85. Diese Zeile definiert den Abschnitt 'reviews: Mapped[list["Review"]] = relationship(back_populates="recipe", cascade="all, d...'.
86. Diese Zeile definiert den Abschnitt 'favorites: Mapped[list["Favorite"]] = relationship(back_populates="recipe", cascade="al...'.
87. Diese Zeile definiert den Abschnitt 'images: Mapped[list["RecipeImage"]] = relationship('.
88. Diese Zeile definiert den Abschnitt 'back_populates="recipe",'.
89. Diese Zeile definiert den Abschnitt 'cascade="all, delete-orphan",'.
90. Diese Zeile definiert den Abschnitt 'order_by="RecipeImage.created_at",'.
91. Diese Zeile definiert den Abschnitt ')'.
92. Diese Zeile ist leer und trennt den Inhalt lesbar.
93. Diese Zeile ist leer und trennt den Inhalt lesbar.
94. Diese Zeile definiert den Abschnitt 'class Ingredient(Base):'.
95. Diese Zeile definiert den Abschnitt '__tablename__ = "ingredients"'.
96. Diese Zeile ist leer und trennt den Inhalt lesbar.
97. Diese Zeile definiert den Abschnitt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
98. Diese Zeile definiert den Abschnitt 'name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)'.
99. Diese Zeile ist leer und trennt den Inhalt lesbar.
100. Diese Zeile definiert den Abschnitt 'recipe_links: Mapped[list["RecipeIngredient"]] = relationship('.
101. Diese Zeile definiert den Abschnitt 'back_populates="ingredient",'.
102. Diese Zeile definiert den Abschnitt 'cascade="all, delete-orphan",'.
103. Diese Zeile definiert den Abschnitt ')'.
104. Diese Zeile ist leer und trennt den Inhalt lesbar.
105. Diese Zeile ist leer und trennt den Inhalt lesbar.
106. Diese Zeile definiert den Abschnitt 'class RecipeIngredient(Base):'.
107. Diese Zeile definiert den Abschnitt '__tablename__ = "recipe_ingredients"'.
108. Diese Zeile ist leer und trennt den Inhalt lesbar.
109. Diese Zeile definiert den Abschnitt 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), pr...'.
110. Diese Zeile definiert den Abschnitt 'ingredient_id: Mapped[int] = mapped_column(ForeignKey("ingredients.id", ondelete="CASCA...'.
111. Diese Zeile definiert den Abschnitt 'quantity_text: Mapped[str] = mapped_column(String(120), default="", nullable=False)'.
112. Diese Zeile definiert den Abschnitt 'grams: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
113. Diese Zeile ist leer und trennt den Inhalt lesbar.
114. Diese Zeile definiert den Abschnitt 'recipe: Mapped["Recipe"] = relationship(back_populates="recipe_ingredients")'.
115. Diese Zeile definiert den Abschnitt 'ingredient: Mapped["Ingredient"] = relationship(back_populates="recipe_links")'.
116. Diese Zeile ist leer und trennt den Inhalt lesbar.
117. Diese Zeile ist leer und trennt den Inhalt lesbar.
118. Diese Zeile definiert den Abschnitt 'class Review(Base):'.
119. Diese Zeile definiert den Abschnitt '__tablename__ = "reviews"'.
120. Diese Zeile definiert den Abschnitt '__table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_reviews_user_recipe...'.
121. Diese Zeile ist leer und trennt den Inhalt lesbar.
122. Diese Zeile definiert den Abschnitt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
123. Diese Zeile definiert den Abschnitt 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nu...'.
124. Diese Zeile definiert den Abschnitt 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullab...'.
125. Diese Zeile definiert den Abschnitt 'rating: Mapped[int] = mapped_column(Integer, nullable=False)'.
126. Diese Zeile definiert den Abschnitt 'comment: Mapped[str] = mapped_column(Text, default="", nullable=False)'.
127. Diese Zeile definiert den Abschnitt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
128. Diese Zeile ist leer und trennt den Inhalt lesbar.
129. Diese Zeile definiert den Abschnitt 'recipe: Mapped["Recipe"] = relationship(back_populates="reviews")'.
130. Diese Zeile definiert den Abschnitt 'user: Mapped["User"] = relationship(back_populates="reviews")'.
131. Diese Zeile ist leer und trennt den Inhalt lesbar.
132. Diese Zeile ist leer und trennt den Inhalt lesbar.
133. Diese Zeile definiert den Abschnitt 'class Favorite(Base):'.
134. Diese Zeile definiert den Abschnitt '__tablename__ = "favorites"'.
135. Diese Zeile definiert den Abschnitt '__table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_favorites_user_reci...'.
136. Diese Zeile ist leer und trennt den Inhalt lesbar.
137. Diese Zeile definiert den Abschnitt 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primar...'.
138. Diese Zeile definiert den Abschnitt 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), pr...'.
139. Diese Zeile definiert den Abschnitt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
140. Diese Zeile ist leer und trennt den Inhalt lesbar.
141. Diese Zeile definiert den Abschnitt 'user: Mapped["User"] = relationship(back_populates="favorites")'.
142. Diese Zeile definiert den Abschnitt 'recipe: Mapped["Recipe"] = relationship(back_populates="favorites")'.
143. Diese Zeile ist leer und trennt den Inhalt lesbar.
144. Diese Zeile ist leer und trennt den Inhalt lesbar.
145. Diese Zeile definiert den Abschnitt 'class RecipeImage(Base):'.
146. Diese Zeile definiert den Abschnitt '__tablename__ = "recipe_images"'.
147. Diese Zeile ist leer und trennt den Inhalt lesbar.
148. Diese Zeile definiert den Abschnitt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
149. Diese Zeile definiert den Abschnitt 'recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id", ondelete="CASCADE"), nu...'.
150. Diese Zeile definiert den Abschnitt 'filename: Mapped[str] = mapped_column(String(255), nullable=False)'.
151. Diese Zeile definiert den Abschnitt 'content_type: Mapped[str] = mapped_column(String(50), nullable=False)'.
152. Diese Zeile definiert den Abschnitt 'data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)'.
153. Diese Zeile definiert den Abschnitt 'is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)'.
154. Diese Zeile definiert den Abschnitt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
155. Diese Zeile ist leer und trennt den Inhalt lesbar.
156. Diese Zeile definiert den Abschnitt 'recipe: Mapped["Recipe"] = relationship(back_populates="images")'.
157. Diese Zeile ist leer und trennt den Inhalt lesbar.
158. Diese Zeile ist leer und trennt den Inhalt lesbar.
159. Diese Zeile definiert den Abschnitt 'class RecipeSubmission(Base):'.
160. Diese Zeile definiert den Abschnitt '__tablename__ = "recipe_submissions"'.
161. Diese Zeile ist leer und trennt den Inhalt lesbar.
162. Diese Zeile definiert den Abschnitt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
163. Diese Zeile definiert den Abschnitt 'submitter_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="...'.
164. Diese Zeile definiert den Abschnitt 'submitter_email: Mapped[str | None] = mapped_column(String(255), nullable=True)'.
165. Diese Zeile definiert den Abschnitt 'title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)'.
166. Diese Zeile definiert den Abschnitt 'description: Mapped[str] = mapped_column(Text, nullable=False)'.
167. Diese Zeile definiert den Abschnitt 'category: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)'.
168. Diese Zeile definiert den Abschnitt 'difficulty: Mapped[str] = mapped_column(String(30), nullable=False, default="medium", i...'.
169. Diese Zeile definiert den Abschnitt 'prep_time_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
170. Diese Zeile definiert den Abschnitt 'servings_text: Mapped[str | None] = mapped_column(String(120), nullable=True)'.
171. Diese Zeile definiert den Abschnitt 'instructions: Mapped[str] = mapped_column(Text, nullable=False)'.
172. Diese Zeile definiert den Abschnitt 'status: Mapped[str] = mapped_column(SUBMISSION_STATUS_ENUM, nullable=False, default="pe...'.
173. Diese Zeile definiert den Abschnitt 'admin_note: Mapped[str | None] = mapped_column(Text, nullable=True)'.
174. Diese Zeile definiert den Abschnitt 'reviewed_by_admin_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelet...'.
175. Diese Zeile definiert den Abschnitt 'reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=...'.
176. Diese Zeile definiert den Abschnitt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
177. Diese Zeile ist leer und trennt den Inhalt lesbar.
178. Diese Zeile definiert den Abschnitt 'submitter_user: Mapped["User"] = relationship('.
179. Diese Zeile definiert den Abschnitt 'back_populates="submissions",'.
180. Diese Zeile definiert den Abschnitt 'foreign_keys=[submitter_user_id],'.
181. Diese Zeile definiert den Abschnitt ')'.
182. Diese Zeile definiert den Abschnitt 'reviewed_by_admin: Mapped["User"] = relationship('.
183. Diese Zeile definiert den Abschnitt 'back_populates="reviewed_submissions",'.
184. Diese Zeile definiert den Abschnitt 'foreign_keys=[reviewed_by_admin_id],'.
185. Diese Zeile definiert den Abschnitt ')'.
186. Diese Zeile definiert den Abschnitt 'ingredients: Mapped[list["SubmissionIngredient"]] = relationship('.
187. Diese Zeile definiert den Abschnitt 'back_populates="submission",'.
188. Diese Zeile definiert den Abschnitt 'cascade="all, delete-orphan",'.
189. Diese Zeile definiert den Abschnitt 'order_by="SubmissionIngredient.id",'.
190. Diese Zeile definiert den Abschnitt ')'.
191. Diese Zeile definiert den Abschnitt 'images: Mapped[list["SubmissionImage"]] = relationship('.
192. Diese Zeile definiert den Abschnitt 'back_populates="submission",'.
193. Diese Zeile definiert den Abschnitt 'cascade="all, delete-orphan",'.
194. Diese Zeile definiert den Abschnitt 'order_by="SubmissionImage.created_at",'.
195. Diese Zeile definiert den Abschnitt ')'.
196. Diese Zeile ist leer und trennt den Inhalt lesbar.
197. Diese Zeile ist leer und trennt den Inhalt lesbar.
198. Diese Zeile definiert den Abschnitt 'class SubmissionIngredient(Base):'.
199. Diese Zeile definiert den Abschnitt '__tablename__ = "submission_ingredients"'.
200. Diese Zeile ist leer und trennt den Inhalt lesbar.
201. Diese Zeile definiert den Abschnitt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
202. Diese Zeile definiert den Abschnitt 'submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete...'.
203. Diese Zeile definiert den Abschnitt 'ingredient_name: Mapped[str] = mapped_column(String(200), nullable=False)'.
204. Diese Zeile definiert den Abschnitt 'quantity_text: Mapped[str] = mapped_column(String(120), nullable=False, default="")'.
205. Diese Zeile definiert den Abschnitt 'grams: Mapped[int | None] = mapped_column(Integer, nullable=True)'.
206. Diese Zeile definiert den Abschnitt 'ingredient_name_normalized: Mapped[str | None] = mapped_column(String(200), nullable=Tr...'.
207. Diese Zeile ist leer und trennt den Inhalt lesbar.
208. Diese Zeile definiert den Abschnitt 'submission: Mapped["RecipeSubmission"] = relationship(back_populates="ingredients")'.
209. Diese Zeile ist leer und trennt den Inhalt lesbar.
210. Diese Zeile ist leer und trennt den Inhalt lesbar.
211. Diese Zeile definiert den Abschnitt 'class SubmissionImage(Base):'.
212. Diese Zeile definiert den Abschnitt '__tablename__ = "submission_images"'.
213. Diese Zeile ist leer und trennt den Inhalt lesbar.
214. Diese Zeile definiert den Abschnitt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
215. Diese Zeile definiert den Abschnitt 'submission_id: Mapped[int] = mapped_column(ForeignKey("recipe_submissions.id", ondelete...'.
216. Diese Zeile definiert den Abschnitt 'filename: Mapped[str] = mapped_column(String(255), nullable=False)'.
217. Diese Zeile definiert den Abschnitt 'content_type: Mapped[str] = mapped_column(String(50), nullable=False)'.
218. Diese Zeile definiert den Abschnitt 'data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)'.
219. Diese Zeile definiert den Abschnitt 'is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)'.
220. Diese Zeile definiert den Abschnitt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
221. Diese Zeile ist leer und trennt den Inhalt lesbar.
222. Diese Zeile definiert den Abschnitt 'submission: Mapped["RecipeSubmission"] = relationship(back_populates="images")'.
223. Diese Zeile ist leer und trennt den Inhalt lesbar.
224. Diese Zeile ist leer und trennt den Inhalt lesbar.
225. Diese Zeile definiert den Abschnitt 'class AppMeta(Base):'.
226. Diese Zeile definiert den Abschnitt '__tablename__ = "app_meta"'.
227. Diese Zeile ist leer und trennt den Inhalt lesbar.
228. Diese Zeile definiert den Abschnitt 'key: Mapped[str] = mapped_column(String(120), primary_key=True)'.
229. Diese Zeile definiert den Abschnitt 'value: Mapped[str] = mapped_column(Text, nullable=False)'.
230. Diese Zeile ist leer und trennt den Inhalt lesbar.
231. Diese Zeile ist leer und trennt den Inhalt lesbar.
232. Diese Zeile definiert den Abschnitt 'class PasswordResetToken(Base):'.
233. Diese Zeile definiert den Abschnitt '__tablename__ = "password_reset_tokens"'.
234. Diese Zeile ist leer und trennt den Inhalt lesbar.
235. Diese Zeile definiert den Abschnitt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
236. Diese Zeile definiert den Abschnitt 'user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullab...'.
237. Diese Zeile definiert den Abschnitt 'token_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)'.
238. Diese Zeile definiert den Abschnitt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
239. Diese Zeile definiert den Abschnitt 'expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, i...'.
240. Diese Zeile definiert den Abschnitt 'used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True...'.
241. Diese Zeile definiert den Abschnitt 'created_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)'.
242. Diese Zeile definiert den Abschnitt 'created_user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)'.
243. Diese Zeile definiert den Abschnitt 'purpose: Mapped[str] = mapped_column(String(50), nullable=False, default="password_rese...'.
244. Diese Zeile ist leer und trennt den Inhalt lesbar.
245. Diese Zeile definiert den Abschnitt 'user: Mapped["User"] = relationship(back_populates="password_reset_tokens")'.
246. Diese Zeile ist leer und trennt den Inhalt lesbar.
247. Diese Zeile ist leer und trennt den Inhalt lesbar.
248. Diese Zeile definiert den Abschnitt 'class SecurityEvent(Base):'.
249. Diese Zeile definiert den Abschnitt '__tablename__ = "security_events"'.
250. Diese Zeile ist leer und trennt den Inhalt lesbar.
251. Diese Zeile definiert den Abschnitt 'id: Mapped[int] = mapped_column(Integer, primary_key=True)'.
252. Diese Zeile definiert den Abschnitt 'user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL")...'.
253. Diese Zeile definiert den Abschnitt 'event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)'.
254. Diese Zeile definiert den Abschnitt 'created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, ...'.
255. Diese Zeile definiert den Abschnitt 'ip: Mapped[str | None] = mapped_column(String(64), nullable=True)'.
256. Diese Zeile definiert den Abschnitt 'user_agent: Mapped[str | None] = mapped_column(String(200), nullable=True)'.
257. Diese Zeile definiert den Abschnitt 'details: Mapped[str | None] = mapped_column(String(300), nullable=True)'.
258. Diese Zeile ist leer und trennt den Inhalt lesbar.
259. Diese Zeile definiert den Abschnitt 'user: Mapped["User"] = relationship(back_populates="security_events")'.

## alembic/versions/20260303_0007_auth_recovery_fields.py
```python
"""add auth recovery and user uid fields

Revision ID: 20260303_0007
Revises: 20260303_0006
Create Date: 2026-03-03 20:35:00
"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260303_0007"
down_revision: Union[str, None] = "20260303_0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _backfill_user_uid() -> None:
    bind = op.get_bind()
    users_table = sa.table(
        "users",
        sa.column("id", sa.Integer()),
        sa.column("user_uid", sa.String(length=36)),
    )
    rows = bind.execute(sa.select(users_table.c.id).where(users_table.c.user_uid.is_(None))).fetchall()
    for row in rows:
        bind.execute(
            users_table.update().where(users_table.c.id == row.id).values(user_uid=str(uuid4())),
        )


def upgrade() -> None:
    with op.batch_alter_table("users") as batch:
        batch.add_column(sa.Column("user_uid", sa.String(length=36), nullable=True))
        batch.add_column(sa.Column("username", sa.String(length=30), nullable=True))
        batch.add_column(sa.Column("username_normalized", sa.String(length=30), nullable=True))
        batch.add_column(sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))
        batch.add_column(sa.Column("last_login_ip", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("last_login_user_agent", sa.String(length=200), nullable=True))

    _backfill_user_uid()

    with op.batch_alter_table("users") as batch:
        batch.alter_column("user_uid", existing_type=sa.String(length=36), nullable=False)
        batch.create_index("ix_users_user_uid", ["user_uid"], unique=True)
        batch.create_index("ix_users_username", ["username"], unique=True)
        batch.create_index("ix_users_username_normalized", ["username_normalized"], unique=True)

    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_ip", sa.String(length=64), nullable=True),
        sa.Column("created_user_agent", sa.String(length=200), nullable=True),
        sa.Column("purpose", sa.String(length=50), nullable=False, server_default="password_reset"),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"], unique=False)
    op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"], unique=False)
    op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expires_at"], unique=False)
    op.create_index("ix_password_reset_tokens_used_at", "password_reset_tokens", ["used_at"], unique=False)
    op.create_index("ix_password_reset_tokens_purpose", "password_reset_tokens", ["purpose"], unique=False)

    op.create_table(
        "security_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(length=80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=200), nullable=True),
        sa.Column("details", sa.String(length=300), nullable=True),
    )
    op.create_index("ix_security_events_user_id", "security_events", ["user_id"], unique=False)
    op.create_index("ix_security_events_event_type", "security_events", ["event_type"], unique=False)
    op.create_index("ix_security_events_created_at", "security_events", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_security_events_created_at", table_name="security_events")
    op.drop_index("ix_security_events_event_type", table_name="security_events")
    op.drop_index("ix_security_events_user_id", table_name="security_events")
    op.drop_table("security_events")

    op.drop_index("ix_password_reset_tokens_purpose", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_used_at", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_expires_at", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_token_hash", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_user_id", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")

    with op.batch_alter_table("users") as batch:
        batch.drop_index("ix_users_username_normalized")
        batch.drop_index("ix_users_username")
        batch.drop_index("ix_users_user_uid")
        batch.drop_column("last_login_user_agent")
        batch.drop_column("last_login_ip")
        batch.drop_column("last_login_at")
        batch.drop_column("username_normalized")
        batch.drop_column("username")
        batch.drop_column("user_uid")
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '"""add auth recovery and user uid fields'.
2. Diese Zeile ist leer und trennt den Inhalt lesbar.
3. Diese Zeile definiert den Abschnitt 'Revision ID: 20260303_0007'.
4. Diese Zeile definiert den Abschnitt 'Revises: 20260303_0006'.
5. Diese Zeile definiert den Abschnitt 'Create Date: 2026-03-03 20:35:00'.
6. Diese Zeile definiert den Abschnitt '"""'.
7. Diese Zeile ist leer und trennt den Inhalt lesbar.
8. Diese Zeile definiert den Abschnitt 'from typing import Sequence, Union'.
9. Diese Zeile definiert den Abschnitt 'from uuid import uuid4'.
10. Diese Zeile ist leer und trennt den Inhalt lesbar.
11. Diese Zeile definiert den Abschnitt 'from alembic import op'.
12. Diese Zeile definiert den Abschnitt 'import sqlalchemy as sa'.
13. Diese Zeile ist leer und trennt den Inhalt lesbar.
14. Diese Zeile definiert den Abschnitt '# revision identifiers, used by Alembic.'.
15. Diese Zeile definiert den Abschnitt 'revision: str = "20260303_0007"'.
16. Diese Zeile definiert den Abschnitt 'down_revision: Union[str, None] = "20260303_0006"'.
17. Diese Zeile definiert den Abschnitt 'branch_labels: Union[str, Sequence[str], None] = None'.
18. Diese Zeile definiert den Abschnitt 'depends_on: Union[str, Sequence[str], None] = None'.
19. Diese Zeile ist leer und trennt den Inhalt lesbar.
20. Diese Zeile ist leer und trennt den Inhalt lesbar.
21. Diese Zeile definiert den Abschnitt 'def _backfill_user_uid() -> None:'.
22. Diese Zeile definiert den Abschnitt 'bind = op.get_bind()'.
23. Diese Zeile definiert den Abschnitt 'users_table = sa.table('.
24. Diese Zeile definiert den Abschnitt '"users",'.
25. Diese Zeile definiert den Abschnitt 'sa.column("id", sa.Integer()),'.
26. Diese Zeile definiert den Abschnitt 'sa.column("user_uid", sa.String(length=36)),'.
27. Diese Zeile definiert den Abschnitt ')'.
28. Diese Zeile definiert den Abschnitt 'rows = bind.execute(sa.select(users_table.c.id).where(users_table.c.user_uid.is_(None))...'.
29. Diese Zeile definiert den Abschnitt 'for row in rows:'.
30. Diese Zeile definiert den Abschnitt 'bind.execute('.
31. Diese Zeile definiert den Abschnitt 'users_table.update().where(users_table.c.id == row.id).values(user_uid=str(uuid4())),'.
32. Diese Zeile definiert den Abschnitt ')'.
33. Diese Zeile ist leer und trennt den Inhalt lesbar.
34. Diese Zeile ist leer und trennt den Inhalt lesbar.
35. Diese Zeile definiert den Abschnitt 'def upgrade() -> None:'.
36. Diese Zeile definiert den Abschnitt 'with op.batch_alter_table("users") as batch:'.
37. Diese Zeile definiert den Abschnitt 'batch.add_column(sa.Column("user_uid", sa.String(length=36), nullable=True))'.
38. Diese Zeile definiert den Abschnitt 'batch.add_column(sa.Column("username", sa.String(length=30), nullable=True))'.
39. Diese Zeile definiert den Abschnitt 'batch.add_column(sa.Column("username_normalized", sa.String(length=30), nullable=True))'.
40. Diese Zeile definiert den Abschnitt 'batch.add_column(sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True))'.
41. Diese Zeile definiert den Abschnitt 'batch.add_column(sa.Column("last_login_ip", sa.String(length=64), nullable=True))'.
42. Diese Zeile definiert den Abschnitt 'batch.add_column(sa.Column("last_login_user_agent", sa.String(length=200), nullable=True))'.
43. Diese Zeile ist leer und trennt den Inhalt lesbar.
44. Diese Zeile definiert den Abschnitt '_backfill_user_uid()'.
45. Diese Zeile ist leer und trennt den Inhalt lesbar.
46. Diese Zeile definiert den Abschnitt 'with op.batch_alter_table("users") as batch:'.
47. Diese Zeile definiert den Abschnitt 'batch.alter_column("user_uid", existing_type=sa.String(length=36), nullable=False)'.
48. Diese Zeile definiert den Abschnitt 'batch.create_index("ix_users_user_uid", ["user_uid"], unique=True)'.
49. Diese Zeile definiert den Abschnitt 'batch.create_index("ix_users_username", ["username"], unique=True)'.
50. Diese Zeile definiert den Abschnitt 'batch.create_index("ix_users_username_normalized", ["username_normalized"], unique=True)'.
51. Diese Zeile ist leer und trennt den Inhalt lesbar.
52. Diese Zeile definiert den Abschnitt 'op.create_table('.
53. Diese Zeile definiert den Abschnitt '"password_reset_tokens",'.
54. Diese Zeile definiert den Abschnitt 'sa.Column("id", sa.Integer(), primary_key=True),'.
55. Diese Zeile definiert den Abschnitt 'sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nulla...'.
56. Diese Zeile definiert den Abschnitt 'sa.Column("token_hash", sa.String(length=64), nullable=False),'.
57. Diese Zeile definiert den Abschnitt 'sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),'.
58. Diese Zeile definiert den Abschnitt 'sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),'.
59. Diese Zeile definiert den Abschnitt 'sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),'.
60. Diese Zeile definiert den Abschnitt 'sa.Column("created_ip", sa.String(length=64), nullable=True),'.
61. Diese Zeile definiert den Abschnitt 'sa.Column("created_user_agent", sa.String(length=200), nullable=True),'.
62. Diese Zeile definiert den Abschnitt 'sa.Column("purpose", sa.String(length=50), nullable=False, server_default="password_res...'.
63. Diese Zeile definiert den Abschnitt ')'.
64. Diese Zeile definiert den Abschnitt 'op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"...'.
65. Diese Zeile definiert den Abschnitt 'op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token...'.
66. Diese Zeile definiert den Abschnitt 'op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expir...'.
67. Diese Zeile definiert den Abschnitt 'op.create_index("ix_password_reset_tokens_used_at", "password_reset_tokens", ["used_at"...'.
68. Diese Zeile definiert den Abschnitt 'op.create_index("ix_password_reset_tokens_purpose", "password_reset_tokens", ["purpose"...'.
69. Diese Zeile ist leer und trennt den Inhalt lesbar.
70. Diese Zeile definiert den Abschnitt 'op.create_table('.
71. Diese Zeile definiert den Abschnitt '"security_events",'.
72. Diese Zeile definiert den Abschnitt 'sa.Column("id", sa.Integer(), primary_key=True),'.
73. Diese Zeile definiert den Abschnitt 'sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), null...'.
74. Diese Zeile definiert den Abschnitt 'sa.Column("event_type", sa.String(length=80), nullable=False),'.
75. Diese Zeile definiert den Abschnitt 'sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),'.
76. Diese Zeile definiert den Abschnitt 'sa.Column("ip", sa.String(length=64), nullable=True),'.
77. Diese Zeile definiert den Abschnitt 'sa.Column("user_agent", sa.String(length=200), nullable=True),'.
78. Diese Zeile definiert den Abschnitt 'sa.Column("details", sa.String(length=300), nullable=True),'.
79. Diese Zeile definiert den Abschnitt ')'.
80. Diese Zeile definiert den Abschnitt 'op.create_index("ix_security_events_user_id", "security_events", ["user_id"], unique=Fa...'.
81. Diese Zeile definiert den Abschnitt 'op.create_index("ix_security_events_event_type", "security_events", ["event_type"], uni...'.
82. Diese Zeile definiert den Abschnitt 'op.create_index("ix_security_events_created_at", "security_events", ["created_at"], uni...'.
83. Diese Zeile ist leer und trennt den Inhalt lesbar.
84. Diese Zeile ist leer und trennt den Inhalt lesbar.
85. Diese Zeile definiert den Abschnitt 'def downgrade() -> None:'.
86. Diese Zeile definiert den Abschnitt 'op.drop_index("ix_security_events_created_at", table_name="security_events")'.
87. Diese Zeile definiert den Abschnitt 'op.drop_index("ix_security_events_event_type", table_name="security_events")'.
88. Diese Zeile definiert den Abschnitt 'op.drop_index("ix_security_events_user_id", table_name="security_events")'.
89. Diese Zeile definiert den Abschnitt 'op.drop_table("security_events")'.
90. Diese Zeile ist leer und trennt den Inhalt lesbar.
91. Diese Zeile definiert den Abschnitt 'op.drop_index("ix_password_reset_tokens_purpose", table_name="password_reset_tokens")'.
92. Diese Zeile definiert den Abschnitt 'op.drop_index("ix_password_reset_tokens_used_at", table_name="password_reset_tokens")'.
93. Diese Zeile definiert den Abschnitt 'op.drop_index("ix_password_reset_tokens_expires_at", table_name="password_reset_tokens")'.
94. Diese Zeile definiert den Abschnitt 'op.drop_index("ix_password_reset_tokens_token_hash", table_name="password_reset_tokens")'.
95. Diese Zeile definiert den Abschnitt 'op.drop_index("ix_password_reset_tokens_user_id", table_name="password_reset_tokens")'.
96. Diese Zeile definiert den Abschnitt 'op.drop_table("password_reset_tokens")'.
97. Diese Zeile ist leer und trennt den Inhalt lesbar.
98. Diese Zeile definiert den Abschnitt 'with op.batch_alter_table("users") as batch:'.
99. Diese Zeile definiert den Abschnitt 'batch.drop_index("ix_users_username_normalized")'.
100. Diese Zeile definiert den Abschnitt 'batch.drop_index("ix_users_username")'.
101. Diese Zeile definiert den Abschnitt 'batch.drop_index("ix_users_user_uid")'.
102. Diese Zeile definiert den Abschnitt 'batch.drop_column("last_login_user_agent")'.
103. Diese Zeile definiert den Abschnitt 'batch.drop_column("last_login_ip")'.
104. Diese Zeile definiert den Abschnitt 'batch.drop_column("last_login_at")'.
105. Diese Zeile definiert den Abschnitt 'batch.drop_column("username_normalized")'.
106. Diese Zeile definiert den Abschnitt 'batch.drop_column("username")'.
107. Diese Zeile definiert den Abschnitt 'batch.drop_column("user_uid")'.

## app/mailer.py
```python
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


class BaseMailer:
    def send(self, payload: MailPayload) -> None:
        raise NotImplementedError


class OutboxMailer(BaseMailer):
    def __init__(self, settings: Settings):
        self.settings = settings

    def send(self, payload: MailPayload) -> None:
        outbox_file = Path(self.settings.mail_outbox_path)
        outbox_file.parent.mkdir(parents=True, exist_ok=True)
        with outbox_file.open("a", encoding="utf-8") as handle:
            handle.write(f"TO: {payload.to_email}\n")
            handle.write(f"SUBJECT: {payload.subject}\n")
            handle.write(f"BODY: {payload.body}\n")
            handle.write("---\n")
        logger.info("reset_mail_written_to_outbox to=%s path=%s", payload.to_email, outbox_file)


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
        logger.info("password_reset_mail_sent to=%s", payload.to_email)


def get_mailer(settings: Settings | None = None) -> BaseMailer:
    resolved = settings or get_settings()
    if resolved.prod_mode:
        return SMTPMailer(resolved)
    return OutboxMailer(resolved)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'import logging'.
2. Diese Zeile definiert den Abschnitt 'import smtplib'.
3. Diese Zeile definiert den Abschnitt 'from dataclasses import dataclass'.
4. Diese Zeile definiert den Abschnitt 'from email.message import EmailMessage'.
5. Diese Zeile definiert den Abschnitt 'from pathlib import Path'.
6. Diese Zeile ist leer und trennt den Inhalt lesbar.
7. Diese Zeile definiert den Abschnitt 'from app.config import Settings, get_settings'.
8. Diese Zeile ist leer und trennt den Inhalt lesbar.
9. Diese Zeile definiert den Abschnitt 'logger = logging.getLogger("mealmate.mailer")'.
10. Diese Zeile ist leer und trennt den Inhalt lesbar.
11. Diese Zeile ist leer und trennt den Inhalt lesbar.
12. Diese Zeile definiert den Abschnitt '@dataclass'.
13. Diese Zeile definiert den Abschnitt 'class MailPayload:'.
14. Diese Zeile definiert den Abschnitt 'to_email: str'.
15. Diese Zeile definiert den Abschnitt 'subject: str'.
16. Diese Zeile definiert den Abschnitt 'body: str'.
17. Diese Zeile ist leer und trennt den Inhalt lesbar.
18. Diese Zeile ist leer und trennt den Inhalt lesbar.
19. Diese Zeile definiert den Abschnitt 'class BaseMailer:'.
20. Diese Zeile definiert den Abschnitt 'def send(self, payload: MailPayload) -> None:'.
21. Diese Zeile definiert den Abschnitt 'raise NotImplementedError'.
22. Diese Zeile ist leer und trennt den Inhalt lesbar.
23. Diese Zeile ist leer und trennt den Inhalt lesbar.
24. Diese Zeile definiert den Abschnitt 'class OutboxMailer(BaseMailer):'.
25. Diese Zeile definiert den Abschnitt 'def __init__(self, settings: Settings):'.
26. Diese Zeile definiert den Abschnitt 'self.settings = settings'.
27. Diese Zeile ist leer und trennt den Inhalt lesbar.
28. Diese Zeile definiert den Abschnitt 'def send(self, payload: MailPayload) -> None:'.
29. Diese Zeile definiert den Abschnitt 'outbox_file = Path(self.settings.mail_outbox_path)'.
30. Diese Zeile definiert den Abschnitt 'outbox_file.parent.mkdir(parents=True, exist_ok=True)'.
31. Diese Zeile definiert den Abschnitt 'with outbox_file.open("a", encoding="utf-8") as handle:'.
32. Diese Zeile definiert den Abschnitt 'handle.write(f"TO: {payload.to_email}\n")'.
33. Diese Zeile definiert den Abschnitt 'handle.write(f"SUBJECT: {payload.subject}\n")'.
34. Diese Zeile definiert den Abschnitt 'handle.write(f"BODY: {payload.body}\n")'.
35. Diese Zeile definiert den Abschnitt 'handle.write("---\n")'.
36. Diese Zeile definiert den Abschnitt 'logger.info("reset_mail_written_to_outbox to=%s path=%s", payload.to_email, outbox_file)'.
37. Diese Zeile ist leer und trennt den Inhalt lesbar.
38. Diese Zeile ist leer und trennt den Inhalt lesbar.
39. Diese Zeile definiert den Abschnitt 'class SMTPMailer(BaseMailer):'.
40. Diese Zeile definiert den Abschnitt 'def __init__(self, settings: Settings):'.
41. Diese Zeile definiert den Abschnitt 'self.settings = settings'.
42. Diese Zeile ist leer und trennt den Inhalt lesbar.
43. Diese Zeile definiert den Abschnitt 'def send(self, payload: MailPayload) -> None:'.
44. Diese Zeile definiert den Abschnitt 'if not self.settings.smtp_host:'.
45. Diese Zeile definiert den Abschnitt 'raise RuntimeError("SMTP host is not configured")'.
46. Diese Zeile definiert den Abschnitt 'msg = EmailMessage()'.
47. Diese Zeile definiert den Abschnitt 'msg["From"] = self.settings.smtp_from'.
48. Diese Zeile definiert den Abschnitt 'msg["To"] = payload.to_email'.
49. Diese Zeile definiert den Abschnitt 'msg["Subject"] = payload.subject'.
50. Diese Zeile definiert den Abschnitt 'msg.set_content(payload.body)'.
51. Diese Zeile definiert den Abschnitt 'with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=20) as server:'.
52. Diese Zeile definiert den Abschnitt 'server.starttls()'.
53. Diese Zeile definiert den Abschnitt 'if self.settings.smtp_user and self.settings.smtp_password:'.
54. Diese Zeile definiert den Abschnitt 'server.login(self.settings.smtp_user, self.settings.smtp_password)'.
55. Diese Zeile definiert den Abschnitt 'server.send_message(msg)'.
56. Diese Zeile definiert den Abschnitt 'logger.info("password_reset_mail_sent to=%s", payload.to_email)'.
57. Diese Zeile ist leer und trennt den Inhalt lesbar.
58. Diese Zeile ist leer und trennt den Inhalt lesbar.
59. Diese Zeile definiert den Abschnitt 'def get_mailer(settings: Settings | None = None) -> BaseMailer:'.
60. Diese Zeile definiert den Abschnitt 'resolved = settings or get_settings()'.
61. Diese Zeile definiert den Abschnitt 'if resolved.prod_mode:'.
62. Diese Zeile definiert den Abschnitt 'return SMTPMailer(resolved)'.
63. Diese Zeile definiert den Abschnitt 'return OutboxMailer(resolved)'.

## app/security_events.py
```python
from datetime import datetime, timedelta, timezone

from fastapi import Request
from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models import SecurityEvent

settings = get_settings()


def _extract_ip(request: Request) -> str | None:
    if request.client and request.client.host:
        return request.client.host[:64]
    return None


def _extract_user_agent(request: Request) -> str | None:
    user_agent = (request.headers.get("user-agent") or "").strip()
    return user_agent[:200] if user_agent else None


def _prune_security_events(db: Session) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.security_event_retention_days)
    db.execute(delete(SecurityEvent).where(SecurityEvent.created_at < cutoff))
    total = db.scalar(select(func.count()).select_from(SecurityEvent)) or 0
    overflow = int(total) - int(settings.security_event_max_rows)
    if overflow <= 0:
        return
    oldest_ids = db.scalars(select(SecurityEvent.id).order_by(SecurityEvent.created_at.asc()).limit(overflow)).all()
    if oldest_ids:
        db.execute(delete(SecurityEvent).where(SecurityEvent.id.in_(oldest_ids)))


def log_security_event(
    db: Session,
    request: Request,
    event_type: str,
    user_id: int | None = None,
    details: str | None = None,
) -> None:
    db.add(
        SecurityEvent(
            user_id=user_id,
            event_type=event_type[:80],
            ip=_extract_ip(request),
            user_agent=_extract_user_agent(request),
            details=(details or "")[:300] or None,
        )
    )
    _prune_security_events(db)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'from datetime import datetime, timedelta, timezone'.
2. Diese Zeile ist leer und trennt den Inhalt lesbar.
3. Diese Zeile definiert den Abschnitt 'from fastapi import Request'.
4. Diese Zeile definiert den Abschnitt 'from sqlalchemy import delete, func, select'.
5. Diese Zeile definiert den Abschnitt 'from sqlalchemy.orm import Session'.
6. Diese Zeile ist leer und trennt den Inhalt lesbar.
7. Diese Zeile definiert den Abschnitt 'from app.config import get_settings'.
8. Diese Zeile definiert den Abschnitt 'from app.models import SecurityEvent'.
9. Diese Zeile ist leer und trennt den Inhalt lesbar.
10. Diese Zeile definiert den Abschnitt 'settings = get_settings()'.
11. Diese Zeile ist leer und trennt den Inhalt lesbar.
12. Diese Zeile ist leer und trennt den Inhalt lesbar.
13. Diese Zeile definiert den Abschnitt 'def _extract_ip(request: Request) -> str | None:'.
14. Diese Zeile definiert den Abschnitt 'if request.client and request.client.host:'.
15. Diese Zeile definiert den Abschnitt 'return request.client.host[:64]'.
16. Diese Zeile definiert den Abschnitt 'return None'.
17. Diese Zeile ist leer und trennt den Inhalt lesbar.
18. Diese Zeile ist leer und trennt den Inhalt lesbar.
19. Diese Zeile definiert den Abschnitt 'def _extract_user_agent(request: Request) -> str | None:'.
20. Diese Zeile definiert den Abschnitt 'user_agent = (request.headers.get("user-agent") or "").strip()'.
21. Diese Zeile definiert den Abschnitt 'return user_agent[:200] if user_agent else None'.
22. Diese Zeile ist leer und trennt den Inhalt lesbar.
23. Diese Zeile ist leer und trennt den Inhalt lesbar.
24. Diese Zeile definiert den Abschnitt 'def _prune_security_events(db: Session) -> None:'.
25. Diese Zeile definiert den Abschnitt 'cutoff = datetime.now(timezone.utc) - timedelta(days=settings.security_event_retention_...'.
26. Diese Zeile definiert den Abschnitt 'db.execute(delete(SecurityEvent).where(SecurityEvent.created_at < cutoff))'.
27. Diese Zeile definiert den Abschnitt 'total = db.scalar(select(func.count()).select_from(SecurityEvent)) or 0'.
28. Diese Zeile definiert den Abschnitt 'overflow = int(total) - int(settings.security_event_max_rows)'.
29. Diese Zeile definiert den Abschnitt 'if overflow <= 0:'.
30. Diese Zeile definiert den Abschnitt 'return'.
31. Diese Zeile definiert den Abschnitt 'oldest_ids = db.scalars(select(SecurityEvent.id).order_by(SecurityEvent.created_at.asc(...'.
32. Diese Zeile definiert den Abschnitt 'if oldest_ids:'.
33. Diese Zeile definiert den Abschnitt 'db.execute(delete(SecurityEvent).where(SecurityEvent.id.in_(oldest_ids)))'.
34. Diese Zeile ist leer und trennt den Inhalt lesbar.
35. Diese Zeile ist leer und trennt den Inhalt lesbar.
36. Diese Zeile definiert den Abschnitt 'def log_security_event('.
37. Diese Zeile definiert den Abschnitt 'db: Session,'.
38. Diese Zeile definiert den Abschnitt 'request: Request,'.
39. Diese Zeile definiert den Abschnitt 'event_type: str,'.
40. Diese Zeile definiert den Abschnitt 'user_id: int | None = None,'.
41. Diese Zeile definiert den Abschnitt 'details: str | None = None,'.
42. Diese Zeile definiert den Abschnitt ') -> None:'.
43. Diese Zeile definiert den Abschnitt 'db.add('.
44. Diese Zeile definiert den Abschnitt 'SecurityEvent('.
45. Diese Zeile definiert den Abschnitt 'user_id=user_id,'.
46. Diese Zeile definiert den Abschnitt 'event_type=event_type[:80],'.
47. Diese Zeile definiert den Abschnitt 'ip=_extract_ip(request),'.
48. Diese Zeile definiert den Abschnitt 'user_agent=_extract_user_agent(request),'.
49. Diese Zeile definiert den Abschnitt 'details=(details or "")[:300] or None,'.
50. Diese Zeile definiert den Abschnitt ')'.
51. Diese Zeile definiert den Abschnitt ')'.
52. Diese Zeile definiert den Abschnitt '_prune_security_events(db)'.

## app/security.py
```python
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import re
import secrets

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.config import get_settings
from app.i18n import t

password_hash = PasswordHash.recommended()
settings = get_settings()
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{3,30}$")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def validate_password_policy(password: str) -> str | None:
    if len(password) < 10:
        return t("error.password_min_length")
    if not re.search(r"[A-Z]", password):
        return t("error.password_upper")
    if not re.search(r"\d", password):
        return t("error.password_number")
    if not re.search(r"[^A-Za-z0-9]", password):
        return t("error.password_special")
    return None


def normalize_username(username: str) -> str:
    return username.strip().lower()


def validate_username_policy(username: str) -> str | None:
    trimmed = username.strip()
    if not USERNAME_PATTERN.fullmatch(trimmed):
        return t("error.username_invalid")
    return None


def create_raw_reset_token() -> str:
    return secrets.token_urlsafe(48)


def hash_reset_token(raw_token: str) -> str:
    secret = settings.secret_key.encode("utf-8")
    payload = raw_token.encode("utf-8")
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


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
1. Diese Zeile definiert den Abschnitt 'from datetime import datetime, timedelta, timezone'.
2. Diese Zeile definiert den Abschnitt 'import hashlib'.
3. Diese Zeile definiert den Abschnitt 'import hmac'.
4. Diese Zeile definiert den Abschnitt 'import re'.
5. Diese Zeile definiert den Abschnitt 'import secrets'.
6. Diese Zeile ist leer und trennt den Inhalt lesbar.
7. Diese Zeile definiert den Abschnitt 'from jose import JWTError, jwt'.
8. Diese Zeile definiert den Abschnitt 'from pwdlib import PasswordHash'.
9. Diese Zeile ist leer und trennt den Inhalt lesbar.
10. Diese Zeile definiert den Abschnitt 'from app.config import get_settings'.
11. Diese Zeile definiert den Abschnitt 'from app.i18n import t'.
12. Diese Zeile ist leer und trennt den Inhalt lesbar.
13. Diese Zeile definiert den Abschnitt 'password_hash = PasswordHash.recommended()'.
14. Diese Zeile definiert den Abschnitt 'settings = get_settings()'.
15. Diese Zeile definiert den Abschnitt 'USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{3,30}$")'.
16. Diese Zeile ist leer und trennt den Inhalt lesbar.
17. Diese Zeile ist leer und trennt den Inhalt lesbar.
18. Diese Zeile definiert den Abschnitt 'def hash_password(password: str) -> str:'.
19. Diese Zeile definiert den Abschnitt 'return password_hash.hash(password)'.
20. Diese Zeile ist leer und trennt den Inhalt lesbar.
21. Diese Zeile ist leer und trennt den Inhalt lesbar.
22. Diese Zeile definiert den Abschnitt 'def verify_password(plain_password: str, hashed_password: str) -> bool:'.
23. Diese Zeile definiert den Abschnitt 'return password_hash.verify(plain_password, hashed_password)'.
24. Diese Zeile ist leer und trennt den Inhalt lesbar.
25. Diese Zeile ist leer und trennt den Inhalt lesbar.
26. Diese Zeile definiert den Abschnitt 'def validate_password_policy(password: str) -> str | None:'.
27. Diese Zeile definiert den Abschnitt 'if len(password) < 10:'.
28. Diese Zeile definiert den Abschnitt 'return t("error.password_min_length")'.
29. Diese Zeile definiert den Abschnitt 'if not re.search(r"[A-Z]", password):'.
30. Diese Zeile definiert den Abschnitt 'return t("error.password_upper")'.
31. Diese Zeile definiert den Abschnitt 'if not re.search(r"\d", password):'.
32. Diese Zeile definiert den Abschnitt 'return t("error.password_number")'.
33. Diese Zeile definiert den Abschnitt 'if not re.search(r"[^A-Za-z0-9]", password):'.
34. Diese Zeile definiert den Abschnitt 'return t("error.password_special")'.
35. Diese Zeile definiert den Abschnitt 'return None'.
36. Diese Zeile ist leer und trennt den Inhalt lesbar.
37. Diese Zeile ist leer und trennt den Inhalt lesbar.
38. Diese Zeile definiert den Abschnitt 'def normalize_username(username: str) -> str:'.
39. Diese Zeile definiert den Abschnitt 'return username.strip().lower()'.
40. Diese Zeile ist leer und trennt den Inhalt lesbar.
41. Diese Zeile ist leer und trennt den Inhalt lesbar.
42. Diese Zeile definiert den Abschnitt 'def validate_username_policy(username: str) -> str | None:'.
43. Diese Zeile definiert den Abschnitt 'trimmed = username.strip()'.
44. Diese Zeile definiert den Abschnitt 'if not USERNAME_PATTERN.fullmatch(trimmed):'.
45. Diese Zeile definiert den Abschnitt 'return t("error.username_invalid")'.
46. Diese Zeile definiert den Abschnitt 'return None'.
47. Diese Zeile ist leer und trennt den Inhalt lesbar.
48. Diese Zeile ist leer und trennt den Inhalt lesbar.
49. Diese Zeile definiert den Abschnitt 'def create_raw_reset_token() -> str:'.
50. Diese Zeile definiert den Abschnitt 'return secrets.token_urlsafe(48)'.
51. Diese Zeile ist leer und trennt den Inhalt lesbar.
52. Diese Zeile ist leer und trennt den Inhalt lesbar.
53. Diese Zeile definiert den Abschnitt 'def hash_reset_token(raw_token: str) -> str:'.
54. Diese Zeile definiert den Abschnitt 'secret = settings.secret_key.encode("utf-8")'.
55. Diese Zeile definiert den Abschnitt 'payload = raw_token.encode("utf-8")'.
56. Diese Zeile definiert den Abschnitt 'return hmac.new(secret, payload, hashlib.sha256).hexdigest()'.
57. Diese Zeile ist leer und trennt den Inhalt lesbar.
58. Diese Zeile ist leer und trennt den Inhalt lesbar.
59. Diese Zeile definiert den Abschnitt 'def create_access_token(subject: str, role: str) -> str:'.
60. Diese Zeile definiert den Abschnitt 'expire = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)'.
61. Diese Zeile definiert den Abschnitt 'payload = {"sub": subject, "role": role, "exp": expire}'.
62. Diese Zeile definiert den Abschnitt 'return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)'.
63. Diese Zeile ist leer und trennt den Inhalt lesbar.
64. Diese Zeile ist leer und trennt den Inhalt lesbar.
65. Diese Zeile definiert den Abschnitt 'def decode_access_token(token: str) -> dict[str, str]:'.
66. Diese Zeile definiert den Abschnitt 'try:'.
67. Diese Zeile definiert den Abschnitt 'return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])'.
68. Diese Zeile definiert den Abschnitt 'except JWTError as exc:'.
69. Diese Zeile definiert den Abschnitt 'raise ValueError("Invalid token") from exc'.

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
    normalized_subject = subject.strip().lower()
    user = db.scalar(select(User).where(User.user_uid == subject.strip()))
    if not user:
        user = db.scalar(select(User).where(User.email == normalized_subject))
    if user:
        request.state.current_user = user
        request.state.rate_limit_user_key = f"user:{user.user_uid}"
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
2. Diese Zeile ist leer und trennt den Inhalt lesbar.
3. Diese Zeile definiert den Abschnitt 'from fastapi import Depends, HTTPException, Request, status'.
4. Diese Zeile definiert den Abschnitt 'from sqlalchemy import select'.
5. Diese Zeile definiert den Abschnitt 'from sqlalchemy.orm import Session'.
6. Diese Zeile ist leer und trennt den Inhalt lesbar.
7. Diese Zeile definiert den Abschnitt 'from app.config import get_settings'.
8. Diese Zeile definiert den Abschnitt 'from app.database import get_db'.
9. Diese Zeile definiert den Abschnitt 'from app.i18n import t'.
10. Diese Zeile definiert den Abschnitt 'from app.i18n.service import available_langs'.
11. Diese Zeile definiert den Abschnitt 'from app.models import User'.
12. Diese Zeile definiert den Abschnitt 'from app.security import decode_access_token'.
13. Diese Zeile definiert den Abschnitt 'from app.services import extract_token'.
14. Diese Zeile ist leer und trennt den Inhalt lesbar.
15. Diese Zeile definiert den Abschnitt 'settings = get_settings()'.
16. Diese Zeile ist leer und trennt den Inhalt lesbar.
17. Diese Zeile ist leer und trennt den Inhalt lesbar.
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
32. Diese Zeile definiert den Abschnitt 'normalized_subject = subject.strip().lower()'.
33. Diese Zeile definiert den Abschnitt 'user = db.scalar(select(User).where(User.user_uid == subject.strip()))'.
34. Diese Zeile definiert den Abschnitt 'if not user:'.
35. Diese Zeile definiert den Abschnitt 'user = db.scalar(select(User).where(User.email == normalized_subject))'.
36. Diese Zeile definiert den Abschnitt 'if user:'.
37. Diese Zeile definiert den Abschnitt 'request.state.current_user = user'.
38. Diese Zeile definiert den Abschnitt 'request.state.rate_limit_user_key = f"user:{user.user_uid}"'.
39. Diese Zeile definiert den Abschnitt 'return user'.
40. Diese Zeile ist leer und trennt den Inhalt lesbar.
41. Diese Zeile ist leer und trennt den Inhalt lesbar.
42. Diese Zeile definiert den Abschnitt 'def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:'.
43. Diese Zeile definiert den Abschnitt 'user = get_current_user_optional(request, db)'.
44. Diese Zeile definiert den Abschnitt 'if not user:'.
45. Diese Zeile definiert den Abschnitt 'raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=t("error.auth_requ...'.
46. Diese Zeile definiert den Abschnitt 'return user'.
47. Diese Zeile ist leer und trennt den Inhalt lesbar.
48. Diese Zeile ist leer und trennt den Inhalt lesbar.
49. Diese Zeile definiert den Abschnitt 'def get_admin_user(current_user: User = Depends(get_current_user)) -> User:'.
50. Diese Zeile definiert den Abschnitt 'if current_user.role != "admin":'.
51. Diese Zeile definiert den Abschnitt 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_requir...'.
52. Diese Zeile definiert den Abschnitt 'return current_user'.
53. Diese Zeile ist leer und trennt den Inhalt lesbar.
54. Diese Zeile ist leer und trennt den Inhalt lesbar.
55. Diese Zeile definiert den Abschnitt 'def template_context(request: Request, current_user: User | None, **kwargs: Any) -> dic...'.
56. Diese Zeile definiert den Abschnitt 'csrf_token = getattr(request.state, "csrf_token", None) or request.cookies.get("csrf_to...'.
57. Diese Zeile definiert den Abschnitt 'request_id = getattr(request.state, "request_id", None)'.
58. Diese Zeile definiert den Abschnitt 'base = {'.
59. Diese Zeile definiert den Abschnitt '"request": request,'.
60. Diese Zeile definiert den Abschnitt '"current_user": current_user,'.
61. Diese Zeile definiert den Abschnitt '"csrf_token": csrf_token,'.
62. Diese Zeile definiert den Abschnitt '"csrf_header_name": settings.csrf_header_name,'.
63. Diese Zeile definiert den Abschnitt '"request_id": request_id,'.
64. Diese Zeile definiert den Abschnitt '"current_lang": getattr(getattr(request, "state", None), "lang", "de"),'.
65. Diese Zeile definiert den Abschnitt '"available_langs": available_langs(),'.
66. Diese Zeile definiert den Abschnitt '}'.
67. Diese Zeile definiert den Abschnitt 'base.update(kwargs)'.
68. Diese Zeile definiert den Abschnitt 'return base'.

## app/routers/auth.py
```python
from datetime import datetime, timedelta, timezone
import logging

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
    token_hash = hash_reset_token(token_value)
    now = datetime.now(timezone.utc)
    reset_token = db.scalar(
        select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token_hash == token_hash,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
                PasswordResetToken.purpose == "password_reset",
            )
        )
    )
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


@router.get("/me")
def me_page(
    request: Request,
    message: str = "",
    current_user: User = Depends(get_current_user),
):
    message_map = {
        "username_updated": t("profile.username_updated", request=request),
        "password_changed": t("auth.password_changed_success", request=request),
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
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'from datetime import datetime, timedelta, timezone'.
2. Diese Zeile definiert den Abschnitt 'import logging'.
3. Diese Zeile ist leer und trennt den Inhalt lesbar.
4. Diese Zeile definiert den Abschnitt 'from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status'.
5. Diese Zeile definiert den Abschnitt 'from sqlalchemy import and_, select'.
6. Diese Zeile definiert den Abschnitt 'from sqlalchemy.orm import Session'.
7. Diese Zeile ist leer und trennt den Inhalt lesbar.
8. Diese Zeile definiert den Abschnitt 'from app.config import get_settings'.
9. Diese Zeile definiert den Abschnitt 'from app.database import get_db'.
10. Diese Zeile definiert den Abschnitt 'from app.dependencies import get_current_user, get_current_user_optional, template_context'.
11. Diese Zeile definiert den Abschnitt 'from app.i18n import t'.
12. Diese Zeile definiert den Abschnitt 'from app.mailer import MailPayload, get_mailer'.
13. Diese Zeile definiert den Abschnitt 'from app.models import PasswordResetToken, User'.
14. Diese Zeile definiert den Abschnitt 'from app.rate_limit import key_by_ip, key_by_user_or_ip, limiter'.
15. Diese Zeile definiert den Abschnitt 'from app.security import ('.
16. Diese Zeile definiert den Abschnitt 'create_access_token,'.
17. Diese Zeile definiert den Abschnitt 'create_raw_reset_token,'.
18. Diese Zeile definiert den Abschnitt 'hash_password,'.
19. Diese Zeile definiert den Abschnitt 'hash_reset_token,'.
20. Diese Zeile definiert den Abschnitt 'normalize_username,'.
21. Diese Zeile definiert den Abschnitt 'validate_password_policy,'.
22. Diese Zeile definiert den Abschnitt 'validate_username_policy,'.
23. Diese Zeile definiert den Abschnitt 'verify_password,'.
24. Diese Zeile definiert den Abschnitt ')'.
25. Diese Zeile definiert den Abschnitt 'from app.security_events import log_security_event'.
26. Diese Zeile definiert den Abschnitt 'from app.views import redirect, templates'.
27. Diese Zeile ist leer und trennt den Inhalt lesbar.
28. Diese Zeile definiert den Abschnitt 'router = APIRouter(tags=["auth"])'.
29. Diese Zeile definiert den Abschnitt 'settings = get_settings()'.
30. Diese Zeile definiert den Abschnitt 'logger = logging.getLogger("mealmate.auth")'.
31. Diese Zeile ist leer und trennt den Inhalt lesbar.
32. Diese Zeile ist leer und trennt den Inhalt lesbar.
33. Diese Zeile definiert den Abschnitt 'def set_auth_cookie(response, token: str) -> None:'.
34. Diese Zeile definiert den Abschnitt 'response.set_cookie('.
35. Diese Zeile definiert den Abschnitt 'key="access_token",'.
36. Diese Zeile definiert den Abschnitt 'value=f"Bearer {token}",'.
37. Diese Zeile definiert den Abschnitt 'httponly=True,'.
38. Diese Zeile definiert den Abschnitt 'secure=settings.resolved_cookie_secure,'.
39. Diese Zeile definiert den Abschnitt 'samesite="lax",'.
40. Diese Zeile definiert den Abschnitt 'max_age=60 * 60 * 24,'.
41. Diese Zeile definiert den Abschnitt 'path="/",'.
42. Diese Zeile definiert den Abschnitt ')'.
43. Diese Zeile ist leer und trennt den Inhalt lesbar.
44. Diese Zeile ist leer und trennt den Inhalt lesbar.
45. Diese Zeile definiert den Abschnitt 'def _identifier_type(identifier: str) -> str:'.
46. Diese Zeile definiert den Abschnitt 'return "email" if "@" in identifier else "username"'.
47. Diese Zeile ist leer und trennt den Inhalt lesbar.
48. Diese Zeile ist leer und trennt den Inhalt lesbar.
49. Diese Zeile definiert den Abschnitt 'def _find_user_by_identifier(db: Session, identifier: str) -> User | None:'.
50. Diese Zeile definiert den Abschnitt 'cleaned = identifier.strip()'.
51. Diese Zeile definiert den Abschnitt 'if not cleaned:'.
52. Diese Zeile definiert den Abschnitt 'return None'.
53. Diese Zeile definiert den Abschnitt 'if "@" in cleaned:'.
54. Diese Zeile definiert den Abschnitt 'return db.scalar(select(User).where(User.email == cleaned.lower()))'.
55. Diese Zeile definiert den Abschnitt 'return db.scalar(select(User).where(User.username_normalized == normalize_username(clea...'.
56. Diese Zeile ist leer und trennt den Inhalt lesbar.
57. Diese Zeile ist leer und trennt den Inhalt lesbar.
58. Diese Zeile definiert den Abschnitt 'def _reset_token_expires_at() -> datetime:'.
59. Diese Zeile definiert den Abschnitt 'return datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_token_min...'.
60. Diese Zeile ist leer und trennt den Inhalt lesbar.
61. Diese Zeile ist leer und trennt den Inhalt lesbar.
62. Diese Zeile definiert den Abschnitt 'def _render_me('.
63. Diese Zeile definiert den Abschnitt 'request: Request,'.
64. Diese Zeile definiert den Abschnitt 'current_user: User,'.
65. Diese Zeile definiert den Abschnitt 'message: str | None = None,'.
66. Diese Zeile definiert den Abschnitt 'error: str | None = None,'.
67. Diese Zeile definiert den Abschnitt 'status_code: int = status.HTTP_200_OK,'.
68. Diese Zeile definiert den Abschnitt '):'.
69. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
70. Diese Zeile definiert den Abschnitt '"me.html",'.
71. Diese Zeile definiert den Abschnitt 'template_context('.
72. Diese Zeile definiert den Abschnitt 'request,'.
73. Diese Zeile definiert den Abschnitt 'current_user,'.
74. Diese Zeile definiert den Abschnitt 'user=current_user,'.
75. Diese Zeile definiert den Abschnitt 'message=message,'.
76. Diese Zeile definiert den Abschnitt 'error=error,'.
77. Diese Zeile definiert den Abschnitt '),'.
78. Diese Zeile definiert den Abschnitt 'status_code=status_code,'.
79. Diese Zeile definiert den Abschnitt ')'.
80. Diese Zeile ist leer und trennt den Inhalt lesbar.
81. Diese Zeile ist leer und trennt den Inhalt lesbar.
82. Diese Zeile definiert den Abschnitt '@router.get("/login")'.
83. Diese Zeile definiert den Abschnitt '@router.get("/auth/login")'.
84. Diese Zeile definiert den Abschnitt 'def login_page('.
85. Diese Zeile definiert den Abschnitt 'request: Request,'.
86. Diese Zeile definiert den Abschnitt 'message: str = "",'.
87. Diese Zeile definiert den Abschnitt 'current_user: User | None = Depends(get_current_user_optional),'.
88. Diese Zeile definiert den Abschnitt '):'.
89. Diese Zeile definiert den Abschnitt 'if current_user:'.
90. Diese Zeile definiert den Abschnitt 'return redirect("/")'.
91. Diese Zeile definiert den Abschnitt 'message_map = {'.
92. Diese Zeile definiert den Abschnitt '"reset_done": t("auth.reset_success", request=request),'.
93. Diese Zeile definiert den Abschnitt '"password_changed": t("auth.password_changed_success", request=request),'.
94. Diese Zeile definiert den Abschnitt '}'.
95. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
96. Diese Zeile definiert den Abschnitt '"auth_login.html",'.
97. Diese Zeile definiert den Abschnitt 'template_context('.
98. Diese Zeile definiert den Abschnitt 'request,'.
99. Diese Zeile definiert den Abschnitt 'current_user,'.
100. Diese Zeile definiert den Abschnitt 'error=None,'.
101. Diese Zeile definiert den Abschnitt 'message=message_map.get(message, ""),'.
102. Diese Zeile definiert den Abschnitt 'identifier_value="",'.
103. Diese Zeile definiert den Abschnitt '),'.
104. Diese Zeile definiert den Abschnitt ')'.
105. Diese Zeile ist leer und trennt den Inhalt lesbar.
106. Diese Zeile ist leer und trennt den Inhalt lesbar.
107. Diese Zeile definiert den Abschnitt '@router.post("/login")'.
108. Diese Zeile definiert den Abschnitt '@router.post("/auth/login")'.
109. Diese Zeile definiert den Abschnitt '@limiter.limit("5/minute", key_func=key_by_ip)'.
110. Diese Zeile definiert den Abschnitt 'def login_submit('.
111. Diese Zeile definiert den Abschnitt 'request: Request,'.
112. Diese Zeile definiert den Abschnitt 'response: Response,'.
113. Diese Zeile definiert den Abschnitt 'identifier: str = Form(...),'.
114. Diese Zeile definiert den Abschnitt 'password: str = Form(...),'.
115. Diese Zeile definiert den Abschnitt 'db: Session = Depends(get_db),'.
116. Diese Zeile definiert den Abschnitt '):'.
117. Diese Zeile definiert den Abschnitt '_ = response'.
118. Diese Zeile definiert den Abschnitt 'user = _find_user_by_identifier(db, identifier)'.
119. Diese Zeile definiert den Abschnitt 'id_type = _identifier_type(identifier)'.
120. Diese Zeile definiert den Abschnitt 'if not user or not verify_password(password, user.hashed_password):'.
121. Diese Zeile definiert den Abschnitt 'log_security_event('.
122. Diese Zeile definiert den Abschnitt 'db,'.
123. Diese Zeile definiert den Abschnitt 'request,'.
124. Diese Zeile definiert den Abschnitt 'event_type="login_failed",'.
125. Diese Zeile definiert den Abschnitt 'user_id=user.id if user else None,'.
126. Diese Zeile definiert den Abschnitt 'details=f"identifier={id_type}",'.
127. Diese Zeile definiert den Abschnitt ')'.
128. Diese Zeile definiert den Abschnitt 'db.commit()'.
129. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
130. Diese Zeile definiert den Abschnitt '"auth_login.html",'.
131. Diese Zeile definiert den Abschnitt 'template_context('.
132. Diese Zeile definiert den Abschnitt 'request,'.
133. Diese Zeile definiert den Abschnitt 'None,'.
134. Diese Zeile definiert den Abschnitt 'error=t("error.invalid_credentials", request=request),'.
135. Diese Zeile definiert den Abschnitt 'message="",'.
136. Diese Zeile definiert den Abschnitt 'identifier_value=identifier,'.
137. Diese Zeile definiert den Abschnitt '),'.
138. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_401_UNAUTHORIZED,'.
139. Diese Zeile definiert den Abschnitt ')'.
140. Diese Zeile definiert den Abschnitt 'user.last_login_at = datetime.now(timezone.utc)'.
141. Diese Zeile definiert den Abschnitt 'user.last_login_ip = request.client.host[:64] if request.client and request.client.host...'.
142. Diese Zeile definiert den Abschnitt 'user.last_login_user_agent = (request.headers.get("user-agent") or "")[:200] or None'.
143. Diese Zeile definiert den Abschnitt 'db.add(user)'.
144. Diese Zeile definiert den Abschnitt 'log_security_event(db, request, event_type="login_success", user_id=user.id, details=f"...'.
145. Diese Zeile definiert den Abschnitt 'db.commit()'.
146. Diese Zeile definiert den Abschnitt 'token = create_access_token(user.user_uid, user.role)'.
147. Diese Zeile definiert den Abschnitt 'response = redirect("/")'.
148. Diese Zeile definiert den Abschnitt 'set_auth_cookie(response, token)'.
149. Diese Zeile definiert den Abschnitt 'return response'.
150. Diese Zeile ist leer und trennt den Inhalt lesbar.
151. Diese Zeile ist leer und trennt den Inhalt lesbar.
152. Diese Zeile definiert den Abschnitt '@router.get("/register")'.
153. Diese Zeile definiert den Abschnitt '@router.get("/auth/register")'.
154. Diese Zeile definiert den Abschnitt 'def register_page(request: Request, current_user: User | None = Depends(get_current_use...'.
155. Diese Zeile definiert den Abschnitt 'if current_user:'.
156. Diese Zeile definiert den Abschnitt 'return redirect("/")'.
157. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
158. Diese Zeile definiert den Abschnitt '"auth_register.html",'.
159. Diese Zeile definiert den Abschnitt 'template_context(request, current_user, error=None, username_value=""),'.
160. Diese Zeile definiert den Abschnitt ')'.
161. Diese Zeile ist leer und trennt den Inhalt lesbar.
162. Diese Zeile ist leer und trennt den Inhalt lesbar.
163. Diese Zeile definiert den Abschnitt '@router.post("/register")'.
164. Diese Zeile definiert den Abschnitt '@router.post("/auth/register")'.
165. Diese Zeile definiert den Abschnitt '@limiter.limit("3/minute", key_func=key_by_ip)'.
166. Diese Zeile definiert den Abschnitt 'def register_submit('.
167. Diese Zeile definiert den Abschnitt 'request: Request,'.
168. Diese Zeile definiert den Abschnitt 'response: Response,'.
169. Diese Zeile definiert den Abschnitt 'email: str = Form(...),'.
170. Diese Zeile definiert den Abschnitt 'username: str = Form(""),'.
171. Diese Zeile definiert den Abschnitt 'password: str = Form(...),'.
172. Diese Zeile definiert den Abschnitt 'db: Session = Depends(get_db),'.
173. Diese Zeile definiert den Abschnitt '):'.
174. Diese Zeile definiert den Abschnitt '_ = response'.
175. Diese Zeile definiert den Abschnitt 'normalized_email = email.strip().lower()'.
176. Diese Zeile definiert den Abschnitt 'username_value = username.strip()'.
177. Diese Zeile definiert den Abschnitt 'normalized_username = normalize_username(username_value) if username_value else None'.
178. Diese Zeile definiert den Abschnitt 'password_error = validate_password_policy(password)'.
179. Diese Zeile definiert den Abschnitt 'if password_error:'.
180. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
181. Diese Zeile definiert den Abschnitt '"auth_register.html",'.
182. Diese Zeile definiert den Abschnitt 'template_context(request, None, error=password_error, username_value=username_value),'.
183. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
184. Diese Zeile definiert den Abschnitt ')'.
185. Diese Zeile definiert den Abschnitt 'if username_value:'.
186. Diese Zeile definiert den Abschnitt 'username_error = validate_username_policy(username_value)'.
187. Diese Zeile definiert den Abschnitt 'if username_error:'.
188. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
189. Diese Zeile definiert den Abschnitt '"auth_register.html",'.
190. Diese Zeile definiert den Abschnitt 'template_context(request, None, error=username_error, username_value=username_value),'.
191. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
192. Diese Zeile definiert den Abschnitt ')'.
193. Diese Zeile definiert den Abschnitt 'existing = db.scalar(select(User).where(User.email == normalized_email))'.
194. Diese Zeile definiert den Abschnitt 'if existing:'.
195. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
196. Diese Zeile definiert den Abschnitt '"auth_register.html",'.
197. Diese Zeile definiert den Abschnitt 'template_context(request, None, error=t("error.email_registered", request=request), use...'.
198. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_409_CONFLICT,'.
199. Diese Zeile definiert den Abschnitt ')'.
200. Diese Zeile definiert den Abschnitt 'if normalized_username:'.
201. Diese Zeile definiert den Abschnitt 'same_username = db.scalar(select(User).where(User.username_normalized == normalized_use...'.
202. Diese Zeile definiert den Abschnitt 'if same_username:'.
203. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
204. Diese Zeile definiert den Abschnitt '"auth_register.html",'.
205. Diese Zeile definiert den Abschnitt 'template_context(request, None, error=t("error.username_taken", request=request), usern...'.
206. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_409_CONFLICT,'.
207. Diese Zeile definiert den Abschnitt ')'.
208. Diese Zeile definiert den Abschnitt 'user = User('.
209. Diese Zeile definiert den Abschnitt 'email=normalized_email,'.
210. Diese Zeile definiert den Abschnitt 'username=username_value or None,'.
211. Diese Zeile definiert den Abschnitt 'username_normalized=normalized_username,'.
212. Diese Zeile definiert den Abschnitt 'hashed_password=hash_password(password),'.
213. Diese Zeile definiert den Abschnitt 'role="user",'.
214. Diese Zeile definiert den Abschnitt ')'.
215. Diese Zeile definiert den Abschnitt 'db.add(user)'.
216. Diese Zeile definiert den Abschnitt 'db.commit()'.
217. Diese Zeile definiert den Abschnitt 'db.refresh(user)'.
218. Diese Zeile definiert den Abschnitt 'token = create_access_token(user.user_uid, user.role)'.
219. Diese Zeile definiert den Abschnitt 'response = redirect("/")'.
220. Diese Zeile definiert den Abschnitt 'set_auth_cookie(response, token)'.
221. Diese Zeile definiert den Abschnitt 'return response'.
222. Diese Zeile ist leer und trennt den Inhalt lesbar.
223. Diese Zeile ist leer und trennt den Inhalt lesbar.
224. Diese Zeile definiert den Abschnitt '@router.post("/logout")'.
225. Diese Zeile definiert den Abschnitt 'def logout():'.
226. Diese Zeile definiert den Abschnitt 'response = redirect("/")'.
227. Diese Zeile definiert den Abschnitt 'response.delete_cookie("access_token", path="/")'.
228. Diese Zeile definiert den Abschnitt 'return response'.
229. Diese Zeile ist leer und trennt den Inhalt lesbar.
230. Diese Zeile ist leer und trennt den Inhalt lesbar.
231. Diese Zeile definiert den Abschnitt '@router.get("/auth/forgot-password")'.
232. Diese Zeile definiert den Abschnitt '@router.get("/forgot-password")'.
233. Diese Zeile definiert den Abschnitt 'def forgot_password_page('.
234. Diese Zeile definiert den Abschnitt 'request: Request,'.
235. Diese Zeile definiert den Abschnitt 'current_user: User | None = Depends(get_current_user_optional),'.
236. Diese Zeile definiert den Abschnitt '):'.
237. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
238. Diese Zeile definiert den Abschnitt '"auth_forgot_password.html",'.
239. Diese Zeile definiert den Abschnitt 'template_context(request, current_user, error=None, message=None, identifier_value=""),'.
240. Diese Zeile definiert den Abschnitt ')'.
241. Diese Zeile ist leer und trennt den Inhalt lesbar.
242. Diese Zeile ist leer und trennt den Inhalt lesbar.
243. Diese Zeile definiert den Abschnitt '@router.post("/auth/forgot-password")'.
244. Diese Zeile definiert den Abschnitt '@router.post("/forgot-password")'.
245. Diese Zeile definiert den Abschnitt '@limiter.limit("5/minute", key_func=key_by_ip)'.
246. Diese Zeile definiert den Abschnitt 'def forgot_password_submit('.
247. Diese Zeile definiert den Abschnitt 'request: Request,'.
248. Diese Zeile definiert den Abschnitt 'response: Response,'.
249. Diese Zeile definiert den Abschnitt 'identifier: str = Form(...),'.
250. Diese Zeile definiert den Abschnitt 'db: Session = Depends(get_db),'.
251. Diese Zeile definiert den Abschnitt '):'.
252. Diese Zeile definiert den Abschnitt '_ = response'.
253. Diese Zeile definiert den Abschnitt 'generic_message = t("auth.forgot_generic_response", request=request)'.
254. Diese Zeile definiert den Abschnitt 'user = _find_user_by_identifier(db, identifier)'.
255. Diese Zeile definiert den Abschnitt 'if user:'.
256. Diese Zeile definiert den Abschnitt 'raw_token = create_raw_reset_token()'.
257. Diese Zeile definiert den Abschnitt 'token_hash = hash_reset_token(raw_token)'.
258. Diese Zeile definiert den Abschnitt 'db.add('.
259. Diese Zeile definiert den Abschnitt 'PasswordResetToken('.
260. Diese Zeile definiert den Abschnitt 'user_id=user.id,'.
261. Diese Zeile definiert den Abschnitt 'token_hash=token_hash,'.
262. Diese Zeile definiert den Abschnitt 'expires_at=_reset_token_expires_at(),'.
263. Diese Zeile definiert den Abschnitt 'created_ip=request.client.host[:64] if request.client and request.client.host else None,'.
264. Diese Zeile definiert den Abschnitt 'created_user_agent=(request.headers.get("user-agent") or "")[:200] or None,'.
265. Diese Zeile definiert den Abschnitt 'purpose="password_reset",'.
266. Diese Zeile definiert den Abschnitt ')'.
267. Diese Zeile definiert den Abschnitt ')'.
268. Diese Zeile definiert den Abschnitt 'log_security_event(db, request, event_type="pwd_reset_requested", user_id=user.id, deta...'.
269. Diese Zeile definiert den Abschnitt 'db.commit()'.
270. Diese Zeile definiert den Abschnitt 'reset_link = f"{str(settings.app_url).rstrip('/')}/auth/reset-password?token={raw_token}"'.
271. Diese Zeile definiert den Abschnitt 'mailer = get_mailer(settings)'.
272. Diese Zeile definiert den Abschnitt 'subject = t("auth.reset_email_subject", request=request)'.
273. Diese Zeile definiert den Abschnitt 'body = t("auth.reset_email_body", request=request, reset_link=reset_link)'.
274. Diese Zeile definiert den Abschnitt 'try:'.
275. Diese Zeile definiert den Abschnitt 'mailer.send(MailPayload(to_email=user.email, subject=subject, body=body))'.
276. Diese Zeile definiert den Abschnitt 'except Exception:'.
277. Diese Zeile definiert den Abschnitt '# We keep the response generic and avoid leaking whether delivery worked.'.
278. Diese Zeile definiert den Abschnitt 'logger.warning("password_reset_mail_send_failed user_id=%s", user.id)'.
279. Diese Zeile definiert den Abschnitt 'else:'.
280. Diese Zeile definiert den Abschnitt 'log_security_event(db, request, event_type="pwd_reset_requested", user_id=None, details...'.
281. Diese Zeile definiert den Abschnitt 'db.commit()'.
282. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
283. Diese Zeile definiert den Abschnitt '"auth_forgot_password.html",'.
284. Diese Zeile definiert den Abschnitt 'template_context('.
285. Diese Zeile definiert den Abschnitt 'request,'.
286. Diese Zeile definiert den Abschnitt 'None,'.
287. Diese Zeile definiert den Abschnitt 'error=None,'.
288. Diese Zeile definiert den Abschnitt 'message=generic_message,'.
289. Diese Zeile definiert den Abschnitt 'identifier_value="",'.
290. Diese Zeile definiert den Abschnitt '),'.
291. Diese Zeile definiert den Abschnitt ')'.
292. Diese Zeile ist leer und trennt den Inhalt lesbar.
293. Diese Zeile ist leer und trennt den Inhalt lesbar.
294. Diese Zeile definiert den Abschnitt '@router.get("/auth/reset-password")'.
295. Diese Zeile definiert den Abschnitt 'def reset_password_page('.
296. Diese Zeile definiert den Abschnitt 'request: Request,'.
297. Diese Zeile definiert den Abschnitt 'token: str = "",'.
298. Diese Zeile definiert den Abschnitt 'current_user: User | None = Depends(get_current_user_optional),'.
299. Diese Zeile definiert den Abschnitt '):'.
300. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
301. Diese Zeile definiert den Abschnitt '"auth_reset_password.html",'.
302. Diese Zeile definiert den Abschnitt 'template_context('.
303. Diese Zeile definiert den Abschnitt 'request,'.
304. Diese Zeile definiert den Abschnitt 'current_user,'.
305. Diese Zeile definiert den Abschnitt 'token_value=token,'.
306. Diese Zeile definiert den Abschnitt 'error=None,'.
307. Diese Zeile definiert den Abschnitt 'message=None,'.
308. Diese Zeile definiert den Abschnitt '),'.
309. Diese Zeile definiert den Abschnitt ')'.
310. Diese Zeile ist leer und trennt den Inhalt lesbar.
311. Diese Zeile ist leer und trennt den Inhalt lesbar.
312. Diese Zeile definiert den Abschnitt '@router.post("/auth/reset-password")'.
313. Diese Zeile definiert den Abschnitt '@limiter.limit("5/minute", key_func=key_by_ip)'.
314. Diese Zeile definiert den Abschnitt 'def reset_password_submit('.
315. Diese Zeile definiert den Abschnitt 'request: Request,'.
316. Diese Zeile definiert den Abschnitt 'response: Response,'.
317. Diese Zeile definiert den Abschnitt 'token: str = Form(...),'.
318. Diese Zeile definiert den Abschnitt 'new_password: str = Form(...),'.
319. Diese Zeile definiert den Abschnitt 'confirm_password: str = Form(...),'.
320. Diese Zeile definiert den Abschnitt 'db: Session = Depends(get_db),'.
321. Diese Zeile definiert den Abschnitt '):'.
322. Diese Zeile definiert den Abschnitt '_ = response'.
323. Diese Zeile definiert den Abschnitt 'token_value = token.strip()'.
324. Diese Zeile definiert den Abschnitt 'if not token_value:'.
325. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
326. Diese Zeile definiert den Abschnitt '"auth_reset_password.html",'.
327. Diese Zeile definiert den Abschnitt 'template_context(request, None, token_value="", error=t("error.reset_token_invalid", re...'.
328. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
329. Diese Zeile definiert den Abschnitt ')'.
330. Diese Zeile definiert den Abschnitt 'if new_password != confirm_password:'.
331. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
332. Diese Zeile definiert den Abschnitt '"auth_reset_password.html",'.
333. Diese Zeile definiert den Abschnitt 'template_context('.
334. Diese Zeile definiert den Abschnitt 'request,'.
335. Diese Zeile definiert den Abschnitt 'None,'.
336. Diese Zeile definiert den Abschnitt 'token_value=token_value,'.
337. Diese Zeile definiert den Abschnitt 'error=t("error.password_confirm_mismatch", request=request),'.
338. Diese Zeile definiert den Abschnitt 'message=None,'.
339. Diese Zeile definiert den Abschnitt '),'.
340. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
341. Diese Zeile definiert den Abschnitt ')'.
342. Diese Zeile definiert den Abschnitt 'password_error = validate_password_policy(new_password)'.
343. Diese Zeile definiert den Abschnitt 'if password_error:'.
344. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
345. Diese Zeile definiert den Abschnitt '"auth_reset_password.html",'.
346. Diese Zeile definiert den Abschnitt 'template_context(request, None, token_value=token_value, error=password_error, message=...'.
347. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
348. Diese Zeile definiert den Abschnitt ')'.
349. Diese Zeile definiert den Abschnitt 'token_hash = hash_reset_token(token_value)'.
350. Diese Zeile definiert den Abschnitt 'now = datetime.now(timezone.utc)'.
351. Diese Zeile definiert den Abschnitt 'reset_token = db.scalar('.
352. Diese Zeile definiert den Abschnitt 'select(PasswordResetToken).where('.
353. Diese Zeile definiert den Abschnitt 'and_('.
354. Diese Zeile definiert den Abschnitt 'PasswordResetToken.token_hash == token_hash,'.
355. Diese Zeile definiert den Abschnitt 'PasswordResetToken.used_at.is_(None),'.
356. Diese Zeile definiert den Abschnitt 'PasswordResetToken.expires_at > now,'.
357. Diese Zeile definiert den Abschnitt 'PasswordResetToken.purpose == "password_reset",'.
358. Diese Zeile definiert den Abschnitt ')'.
359. Diese Zeile definiert den Abschnitt ')'.
360. Diese Zeile definiert den Abschnitt ')'.
361. Diese Zeile definiert den Abschnitt 'if not reset_token:'.
362. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
363. Diese Zeile definiert den Abschnitt '"auth_reset_password.html",'.
364. Diese Zeile definiert den Abschnitt 'template_context(request, None, token_value="", error=t("error.reset_token_invalid", re...'.
365. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
366. Diese Zeile definiert den Abschnitt ')'.
367. Diese Zeile definiert den Abschnitt 'user = db.scalar(select(User).where(User.id == reset_token.user_id))'.
368. Diese Zeile definiert den Abschnitt 'if not user:'.
369. Diese Zeile definiert den Abschnitt 'return templates.TemplateResponse('.
370. Diese Zeile definiert den Abschnitt '"auth_reset_password.html",'.
371. Diese Zeile definiert den Abschnitt 'template_context(request, None, token_value="", error=t("error.reset_token_invalid", re...'.
372. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
373. Diese Zeile definiert den Abschnitt ')'.
374. Diese Zeile definiert den Abschnitt 'user.hashed_password = hash_password(new_password)'.
375. Diese Zeile definiert den Abschnitt 'reset_token.used_at = now'.
376. Diese Zeile definiert den Abschnitt 'other_tokens = db.scalars('.
377. Diese Zeile definiert den Abschnitt 'select(PasswordResetToken).where('.
378. Diese Zeile definiert den Abschnitt 'and_('.
379. Diese Zeile definiert den Abschnitt 'PasswordResetToken.user_id == user.id,'.
380. Diese Zeile definiert den Abschnitt 'PasswordResetToken.used_at.is_(None),'.
381. Diese Zeile definiert den Abschnitt 'PasswordResetToken.id != reset_token.id,'.
382. Diese Zeile definiert den Abschnitt 'PasswordResetToken.purpose == "password_reset",'.
383. Diese Zeile definiert den Abschnitt ')'.
384. Diese Zeile definiert den Abschnitt ')'.
385. Diese Zeile definiert den Abschnitt ').all()'.
386. Diese Zeile definiert den Abschnitt 'for item in other_tokens:'.
387. Diese Zeile definiert den Abschnitt 'item.used_at = now'.
388. Diese Zeile definiert den Abschnitt 'db.add(user)'.
389. Diese Zeile definiert den Abschnitt 'log_security_event(db, request, event_type="pwd_reset_done", user_id=user.id, details="...'.
390. Diese Zeile definiert den Abschnitt 'db.commit()'.
391. Diese Zeile definiert den Abschnitt 'return redirect("/login?message=reset_done")'.
392. Diese Zeile ist leer und trennt den Inhalt lesbar.
393. Diese Zeile ist leer und trennt den Inhalt lesbar.
394. Diese Zeile definiert den Abschnitt '@router.post("/auth/change-password")'.
395. Diese Zeile definiert den Abschnitt '@limiter.limit("3/minute", key_func=key_by_user_or_ip)'.
396. Diese Zeile definiert den Abschnitt 'def change_password_submit('.
397. Diese Zeile definiert den Abschnitt 'request: Request,'.
398. Diese Zeile definiert den Abschnitt 'old_password: str = Form(...),'.
399. Diese Zeile definiert den Abschnitt 'new_password: str = Form(...),'.
400. Diese Zeile definiert den Abschnitt 'confirm_password: str = Form(...),'.
401. Diese Zeile definiert den Abschnitt 'db: Session = Depends(get_db),'.
402. Diese Zeile definiert den Abschnitt 'current_user: User = Depends(get_current_user),'.
403. Diese Zeile definiert den Abschnitt '):'.
404. Diese Zeile definiert den Abschnitt 'if not verify_password(old_password, current_user.hashed_password):'.
405. Diese Zeile definiert den Abschnitt 'return _render_me('.
406. Diese Zeile definiert den Abschnitt 'request,'.
407. Diese Zeile definiert den Abschnitt 'current_user,'.
408. Diese Zeile definiert den Abschnitt 'error=t("error.password_old_invalid", request=request),'.
409. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
410. Diese Zeile definiert den Abschnitt ')'.
411. Diese Zeile definiert den Abschnitt 'if new_password != confirm_password:'.
412. Diese Zeile definiert den Abschnitt 'return _render_me('.
413. Diese Zeile definiert den Abschnitt 'request,'.
414. Diese Zeile definiert den Abschnitt 'current_user,'.
415. Diese Zeile definiert den Abschnitt 'error=t("error.password_confirm_mismatch", request=request),'.
416. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
417. Diese Zeile definiert den Abschnitt ')'.
418. Diese Zeile definiert den Abschnitt 'password_error = validate_password_policy(new_password)'.
419. Diese Zeile definiert den Abschnitt 'if password_error:'.
420. Diese Zeile definiert den Abschnitt 'return _render_me('.
421. Diese Zeile definiert den Abschnitt 'request,'.
422. Diese Zeile definiert den Abschnitt 'current_user,'.
423. Diese Zeile definiert den Abschnitt 'error=password_error,'.
424. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_400_BAD_REQUEST,'.
425. Diese Zeile definiert den Abschnitt ')'.
426. Diese Zeile definiert den Abschnitt 'current_user.hashed_password = hash_password(new_password)'.
427. Diese Zeile definiert den Abschnitt 'db.add(current_user)'.
428. Diese Zeile definiert den Abschnitt 'log_security_event(db, request, event_type="pwd_changed", user_id=current_user.id, deta...'.
429. Diese Zeile definiert den Abschnitt 'db.commit()'.
430. Diese Zeile definiert den Abschnitt 'response = redirect("/me?message=password_changed")'.
431. Diese Zeile definiert den Abschnitt 'set_auth_cookie(response, create_access_token(current_user.user_uid, current_user.role))'.
432. Diese Zeile definiert den Abschnitt 'return response'.
433. Diese Zeile ist leer und trennt den Inhalt lesbar.
434. Diese Zeile ist leer und trennt den Inhalt lesbar.
435. Diese Zeile definiert den Abschnitt '@router.post("/profile/username")'.
436. Diese Zeile definiert den Abschnitt '@limiter.limit("5/minute", key_func=key_by_user_or_ip)'.
437. Diese Zeile definiert den Abschnitt 'def update_username_submit('.
438. Diese Zeile definiert den Abschnitt 'request: Request,'.
439. Diese Zeile definiert den Abschnitt 'username: str = Form(...),'.
440. Diese Zeile definiert den Abschnitt 'db: Session = Depends(get_db),'.
441. Diese Zeile definiert den Abschnitt 'current_user: User = Depends(get_current_user),'.
442. Diese Zeile definiert den Abschnitt '):'.
443. Diese Zeile definiert den Abschnitt 'username_value = username.strip()'.
444. Diese Zeile definiert den Abschnitt 'username_error = validate_username_policy(username_value)'.
445. Diese Zeile definiert den Abschnitt 'if username_error:'.
446. Diese Zeile definiert den Abschnitt 'return _render_me(request, current_user, error=username_error, status_code=status.HTTP_...'.
447. Diese Zeile definiert den Abschnitt 'normalized_username = normalize_username(username_value)'.
448. Diese Zeile definiert den Abschnitt 'existing = db.scalar('.
449. Diese Zeile definiert den Abschnitt 'select(User).where('.
450. Diese Zeile definiert den Abschnitt 'and_('.
451. Diese Zeile definiert den Abschnitt 'User.username_normalized == normalized_username,'.
452. Diese Zeile definiert den Abschnitt 'User.id != current_user.id,'.
453. Diese Zeile definiert den Abschnitt ')'.
454. Diese Zeile definiert den Abschnitt ')'.
455. Diese Zeile definiert den Abschnitt ')'.
456. Diese Zeile definiert den Abschnitt 'if existing:'.
457. Diese Zeile definiert den Abschnitt 'return _render_me('.
458. Diese Zeile definiert den Abschnitt 'request,'.
459. Diese Zeile definiert den Abschnitt 'current_user,'.
460. Diese Zeile definiert den Abschnitt 'error=t("error.username_taken", request=request),'.
461. Diese Zeile definiert den Abschnitt 'status_code=status.HTTP_409_CONFLICT,'.
462. Diese Zeile definiert den Abschnitt ')'.
463. Diese Zeile definiert den Abschnitt 'current_user.username = username_value'.
464. Diese Zeile definiert den Abschnitt 'current_user.username_normalized = normalized_username'.
465. Diese Zeile definiert den Abschnitt 'db.add(current_user)'.
466. Diese Zeile definiert den Abschnitt 'log_security_event(db, request, event_type="username_changed", user_id=current_user.id,...'.
467. Diese Zeile definiert den Abschnitt 'db.commit()'.
468. Diese Zeile definiert den Abschnitt 'return redirect("/me?message=username_updated")'.
469. Diese Zeile ist leer und trennt den Inhalt lesbar.
470. Diese Zeile ist leer und trennt den Inhalt lesbar.
471. Diese Zeile definiert den Abschnitt '@router.get("/me")'.
472. Diese Zeile definiert den Abschnitt 'def me_page('.
473. Diese Zeile definiert den Abschnitt 'request: Request,'.
474. Diese Zeile definiert den Abschnitt 'message: str = "",'.
475. Diese Zeile definiert den Abschnitt 'current_user: User = Depends(get_current_user),'.
476. Diese Zeile definiert den Abschnitt '):'.
477. Diese Zeile definiert den Abschnitt 'message_map = {'.
478. Diese Zeile definiert den Abschnitt '"username_updated": t("profile.username_updated", request=request),'.
479. Diese Zeile definiert den Abschnitt '"password_changed": t("auth.password_changed_success", request=request),'.
480. Diese Zeile definiert den Abschnitt '}'.
481. Diese Zeile definiert den Abschnitt 'return _render_me(request, current_user, message=message_map.get(message, ""))'.
482. Diese Zeile ist leer und trennt den Inhalt lesbar.
483. Diese Zeile ist leer und trennt den Inhalt lesbar.
484. Diese Zeile definiert den Abschnitt '@router.get("/api/me")'.
485. Diese Zeile definiert den Abschnitt 'def me_api(current_user: User = Depends(get_current_user)):'.
486. Diese Zeile definiert den Abschnitt 'return {'.
487. Diese Zeile definiert den Abschnitt '"id": current_user.id,'.
488. Diese Zeile definiert den Abschnitt '"user_uid": current_user.user_uid,'.
489. Diese Zeile definiert den Abschnitt '"email": current_user.email,'.
490. Diese Zeile definiert den Abschnitt '"username": current_user.username,'.
491. Diese Zeile definiert den Abschnitt '"role": current_user.role,'.
492. Diese Zeile definiert den Abschnitt '"created_at": current_user.created_at.isoformat(),'.
493. Diese Zeile definiert den Abschnitt '"last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at e...'.
494. Diese Zeile definiert den Abschnitt '}'.
495. Diese Zeile ist leer und trennt den Inhalt lesbar.
496. Diese Zeile ist leer und trennt den Inhalt lesbar.
497. Diese Zeile definiert den Abschnitt '@router.get("/admin-only")'.
498. Diese Zeile definiert den Abschnitt 'def admin_only(request: Request, current_user: User = Depends(get_current_user)):'.
499. Diese Zeile definiert den Abschnitt 'if current_user.role != "admin":'.
500. Diese Zeile definiert den Abschnitt 'raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_requir...'.
501. Diese Zeile definiert den Abschnitt 'return {"message": t("role.admin", request=request)}'.

## app/templates/auth_login.html
```jinja2
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("auth.login_title") }}</h1>
  {% if message %}<p class="meta">{{ message }}</p>{% endif %}
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  <form method="post" action="/login" class="stack">
    <label>{{ t("auth.identifier") }} <input type="text" name="identifier" value="{{ identifier_value }}" required></label>
    <label>{{ t("auth.password") }} <input type="password" name="password" required></label>
    <button type="submit">{{ t("auth.login_button") }}</button>
  </form>
  <p><a href="/auth/forgot-password">{{ t("auth.forgot_password_link") }}</a></p>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '{% extends "base.html" %}'.
2. Diese Zeile definiert den Abschnitt '{% block content %}'.
3. Diese Zeile definiert den Abschnitt '<section class="panel narrow">'.
4. Diese Zeile definiert den Abschnitt '<h1>{{ t("auth.login_title") }}</h1>'.
5. Diese Zeile definiert den Abschnitt '{% if message %}<p class="meta">{{ message }}</p>{% endif %}'.
6. Diese Zeile definiert den Abschnitt '{% if error %}<p class="error">{{ error }}</p>{% endif %}'.
7. Diese Zeile definiert den Abschnitt '<form method="post" action="/login" class="stack">'.
8. Diese Zeile definiert den Abschnitt '<label>{{ t("auth.identifier") }} <input type="text" name="identifier" value="{{ identi...'.
9. Diese Zeile definiert den Abschnitt '<label>{{ t("auth.password") }} <input type="password" name="password" required></label>'.
10. Diese Zeile definiert den Abschnitt '<button type="submit">{{ t("auth.login_button") }}</button>'.
11. Diese Zeile definiert den Abschnitt '</form>'.
12. Diese Zeile definiert den Abschnitt '<p><a href="/auth/forgot-password">{{ t("auth.forgot_password_link") }}</a></p>'.
13. Diese Zeile definiert den Abschnitt '</section>'.
14. Diese Zeile definiert den Abschnitt '{% endblock %}'.

## app/templates/auth_register.html
```jinja2
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("auth.register_title") }}</h1>
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  <form method="post" action="/register" class="stack">
    <label>{{ t("auth.email") }} <input type="email" name="email" required></label>
    <label>{{ t("profile.username") }} <input type="text" name="username" value="{{ username_value }}" minlength="3" maxlength="30"></label>
    <label>{{ t("auth.password") }} <input type="password" name="password" minlength="10" required></label>
    <button type="submit">{{ t("auth.register_button") }}</button>
  </form>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '{% extends "base.html" %}'.
2. Diese Zeile definiert den Abschnitt '{% block content %}'.
3. Diese Zeile definiert den Abschnitt '<section class="panel narrow">'.
4. Diese Zeile definiert den Abschnitt '<h1>{{ t("auth.register_title") }}</h1>'.
5. Diese Zeile definiert den Abschnitt '{% if error %}<p class="error">{{ error }}</p>{% endif %}'.
6. Diese Zeile definiert den Abschnitt '<form method="post" action="/register" class="stack">'.
7. Diese Zeile definiert den Abschnitt '<label>{{ t("auth.email") }} <input type="email" name="email" required></label>'.
8. Diese Zeile definiert den Abschnitt '<label>{{ t("profile.username") }} <input type="text" name="username" value="{{ usernam...'.
9. Diese Zeile definiert den Abschnitt '<label>{{ t("auth.password") }} <input type="password" name="password" minlength="10" r...'.
10. Diese Zeile definiert den Abschnitt '<button type="submit">{{ t("auth.register_button") }}</button>'.
11. Diese Zeile definiert den Abschnitt '</form>'.
12. Diese Zeile definiert den Abschnitt '</section>'.
13. Diese Zeile definiert den Abschnitt '{% endblock %}'.

## app/templates/me.html
```jinja2
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
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '{% extends "base.html" %}'.
2. Diese Zeile definiert den Abschnitt '{% block content %}'.
3. Diese Zeile definiert den Abschnitt '<section class="panel">'.
4. Diese Zeile definiert den Abschnitt '<h1>{{ t("profile.title") }}</h1>'.
5. Diese Zeile definiert den Abschnitt '{% if message %}<p class="meta">{{ message }}</p>{% endif %}'.
6. Diese Zeile definiert den Abschnitt '{% if error %}<p class="error">{{ error }}</p>{% endif %}'.
7. Diese Zeile definiert den Abschnitt '<p><strong>{{ t("profile.user_uid") }}:</strong> {{ user.user_uid }}</p>'.
8. Diese Zeile definiert den Abschnitt '<p><strong>{{ t("profile.email") }}:</strong> {{ user.email }}</p>'.
9. Diese Zeile definiert den Abschnitt '<p><strong>{{ t("profile.role") }}:</strong> {{ role_label(user.role) }}</p>'.
10. Diese Zeile definiert den Abschnitt '<p><strong>{{ t("profile.username") }}:</strong> {{ user.username or "-" }}</p>'.
11. Diese Zeile definiert den Abschnitt '<p><strong>{{ t("profile.joined") }}:</strong> {{ user.created_at|datetime_de }}</p>'.
12. Diese Zeile definiert den Abschnitt '</section>'.
13. Diese Zeile ist leer und trennt den Inhalt lesbar.
14. Diese Zeile definiert den Abschnitt '<section class="panel narrow">'.
15. Diese Zeile definiert den Abschnitt '<h2>{{ t("profile.username_change_title") }}</h2>'.
16. Diese Zeile definiert den Abschnitt '<form method="post" action="/profile/username" class="stack">'.
17. Diese Zeile definiert den Abschnitt '<label>{{ t("profile.username") }}'.
18. Diese Zeile definiert den Abschnitt '<input type="text" name="username" value="{{ user.username or '' }}" minlength="3" maxl...'.
19. Diese Zeile definiert den Abschnitt '</label>'.
20. Diese Zeile definiert den Abschnitt '<button type="submit">{{ t("profile.username_save") }}</button>'.
21. Diese Zeile definiert den Abschnitt '</form>'.
22. Diese Zeile definiert den Abschnitt '</section>'.
23. Diese Zeile ist leer und trennt den Inhalt lesbar.
24. Diese Zeile definiert den Abschnitt '<section class="panel narrow">'.
25. Diese Zeile definiert den Abschnitt '<h2>{{ t("auth.change_password_title") }}</h2>'.
26. Diese Zeile definiert den Abschnitt '<form method="post" action="/auth/change-password" class="stack">'.
27. Diese Zeile definiert den Abschnitt '<label>{{ t("auth.old_password") }} <input type="password" name="old_password" required...'.
28. Diese Zeile definiert den Abschnitt '<label>{{ t("auth.new_password") }} <input type="password" name="new_password" minlengt...'.
29. Diese Zeile definiert den Abschnitt '<label>{{ t("auth.confirm_password") }} <input type="password" name="confirm_password" ...'.
30. Diese Zeile definiert den Abschnitt '<button type="submit">{{ t("auth.change_password_button") }}</button>'.
31. Diese Zeile definiert den Abschnitt '</form>'.
32. Diese Zeile definiert den Abschnitt '</section>'.
33. Diese Zeile definiert den Abschnitt '{% endblock %}'.

## app/templates/auth_forgot_password.html
```jinja2
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("auth.forgot_password_title") }}</h1>
  <p class="meta">{{ t("auth.forgot_password_hint") }}</p>
  {% if message %}<p class="meta">{{ message }}</p>{% endif %}
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  <form method="post" action="/auth/forgot-password" class="stack">
    <label>{{ t("auth.identifier") }} <input type="text" name="identifier" value="{{ identifier_value }}" required></label>
    <button type="submit">{{ t("auth.forgot_password_button") }}</button>
  </form>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '{% extends "base.html" %}'.
2. Diese Zeile definiert den Abschnitt '{% block content %}'.
3. Diese Zeile definiert den Abschnitt '<section class="panel narrow">'.
4. Diese Zeile definiert den Abschnitt '<h1>{{ t("auth.forgot_password_title") }}</h1>'.
5. Diese Zeile definiert den Abschnitt '<p class="meta">{{ t("auth.forgot_password_hint") }}</p>'.
6. Diese Zeile definiert den Abschnitt '{% if message %}<p class="meta">{{ message }}</p>{% endif %}'.
7. Diese Zeile definiert den Abschnitt '{% if error %}<p class="error">{{ error }}</p>{% endif %}'.
8. Diese Zeile definiert den Abschnitt '<form method="post" action="/auth/forgot-password" class="stack">'.
9. Diese Zeile definiert den Abschnitt '<label>{{ t("auth.identifier") }} <input type="text" name="identifier" value="{{ identi...'.
10. Diese Zeile definiert den Abschnitt '<button type="submit">{{ t("auth.forgot_password_button") }}</button>'.
11. Diese Zeile definiert den Abschnitt '</form>'.
12. Diese Zeile definiert den Abschnitt '</section>'.
13. Diese Zeile definiert den Abschnitt '{% endblock %}'.

## app/templates/auth_reset_password.html
```jinja2
{% extends "base.html" %}
{% block content %}
<section class="panel narrow">
  <h1>{{ t("auth.reset_password_title") }}</h1>
  {% if message %}<p class="meta">{{ message }}</p>{% endif %}
  {% if error %}<p class="error">{{ error }}</p>{% endif %}
  <form method="post" action="/auth/reset-password" class="stack">
    <input type="hidden" name="token" value="{{ token_value }}">
    <label>{{ t("auth.new_password") }} <input type="password" name="new_password" minlength="10" required></label>
    <label>{{ t("auth.confirm_password") }} <input type="password" name="confirm_password" minlength="10" required></label>
    <button type="submit">{{ t("auth.reset_password_button") }}</button>
  </form>
</section>
{% endblock %}
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '{% extends "base.html" %}'.
2. Diese Zeile definiert den Abschnitt '{% block content %}'.
3. Diese Zeile definiert den Abschnitt '<section class="panel narrow">'.
4. Diese Zeile definiert den Abschnitt '<h1>{{ t("auth.reset_password_title") }}</h1>'.
5. Diese Zeile definiert den Abschnitt '{% if message %}<p class="meta">{{ message }}</p>{% endif %}'.
6. Diese Zeile definiert den Abschnitt '{% if error %}<p class="error">{{ error }}</p>{% endif %}'.
7. Diese Zeile definiert den Abschnitt '<form method="post" action="/auth/reset-password" class="stack">'.
8. Diese Zeile definiert den Abschnitt '<input type="hidden" name="token" value="{{ token_value }}">'.
9. Diese Zeile definiert den Abschnitt '<label>{{ t("auth.new_password") }} <input type="password" name="new_password" minlengt...'.
10. Diese Zeile definiert den Abschnitt '<label>{{ t("auth.confirm_password") }} <input type="password" name="confirm_password" ...'.
11. Diese Zeile definiert den Abschnitt '<button type="submit">{{ t("auth.reset_password_button") }}</button>'.
12. Diese Zeile definiert den Abschnitt '</form>'.
13. Diese Zeile definiert den Abschnitt '</section>'.
14. Diese Zeile definiert den Abschnitt '{% endblock %}'.

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
PASSWORD_RESET_TOKEN_MINUTES=30
MAX_UPLOAD_MB=4
MAX_CSV_UPLOAD_MB=10
ALLOWED_IMAGE_TYPES=image/png,image/jpeg,image/webp
MAIL_OUTBOX_PATH=outbox/reset_links.txt
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
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'APP_NAME=MealMate'.
2. Diese Zeile definiert den Abschnitt 'APP_ENV=dev'.
3. Diese Zeile definiert den Abschnitt 'APP_URL=http://localhost:8000'.
4. Diese Zeile definiert den Abschnitt 'SECRET_KEY=change-this-in-production'.
5. Diese Zeile definiert den Abschnitt 'ALGORITHM=HS256'.
6. Diese Zeile definiert den Abschnitt 'TOKEN_EXPIRE_MINUTES=60'.
7. Diese Zeile definiert den Abschnitt '# DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/mealmate'.
8. Diese Zeile definiert den Abschnitt 'DATABASE_URL=sqlite:///./mealmate.db'.
9. Diese Zeile definiert den Abschnitt 'ALLOWED_HOSTS=*'.
10. Diese Zeile definiert den Abschnitt 'COOKIE_SECURE=0'.
11. Diese Zeile definiert den Abschnitt 'FORCE_HTTPS=0'.
12. Diese Zeile definiert den Abschnitt 'LOG_LEVEL=INFO'.
13. Diese Zeile definiert den Abschnitt 'CSRF_COOKIE_NAME=csrf_token'.
14. Diese Zeile definiert den Abschnitt 'CSRF_HEADER_NAME=X-CSRF-Token'.
15. Diese Zeile definiert den Abschnitt 'PASSWORD_RESET_TOKEN_MINUTES=30'.
16. Diese Zeile definiert den Abschnitt 'MAX_UPLOAD_MB=4'.
17. Diese Zeile definiert den Abschnitt 'MAX_CSV_UPLOAD_MB=10'.
18. Diese Zeile definiert den Abschnitt 'ALLOWED_IMAGE_TYPES=image/png,image/jpeg,image/webp'.
19. Diese Zeile definiert den Abschnitt 'MAIL_OUTBOX_PATH=outbox/reset_links.txt'.
20. Diese Zeile definiert den Abschnitt 'SMTP_HOST='.
21. Diese Zeile definiert den Abschnitt 'SMTP_PORT=587'.
22. Diese Zeile definiert den Abschnitt 'SMTP_USER='.
23. Diese Zeile definiert den Abschnitt 'SMTP_PASSWORD='.
24. Diese Zeile definiert den Abschnitt 'SMTP_FROM=no-reply@mealmate.local'.
25. Diese Zeile definiert den Abschnitt 'SECURITY_EVENT_RETENTION_DAYS=30'.
26. Diese Zeile definiert den Abschnitt 'SECURITY_EVENT_MAX_ROWS=5000'.
27. Diese Zeile definiert den Abschnitt 'ENABLE_KOCHWIKI_SEED=0'.
28. Diese Zeile definiert den Abschnitt 'AUTO_SEED_KOCHWIKI=0'.
29. Diese Zeile definiert den Abschnitt 'KOCHWIKI_CSV_PATH=rezepte_kochwiki_clean_3713.csv'.
30. Diese Zeile definiert den Abschnitt 'IMPORT_DOWNLOAD_IMAGES=0'.
31. Diese Zeile definiert den Abschnitt 'SEED_ADMIN_EMAIL=admin@mealmate.local'.
32. Diese Zeile definiert den Abschnitt 'SEED_ADMIN_PASSWORD=AdminPass123!'.

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
  "auth.confirm_password": "Passwort bestaetigen",
  "auth.email": "E-Mail",
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
58. Diese Zeile definiert den Abschnitt '"auth.change_password_button": "Passwort aktualisieren",'.
59. Diese Zeile definiert den Abschnitt '"auth.change_password_title": "Passwort aendern",'.
60. Diese Zeile definiert den Abschnitt '"auth.confirm_password": "Passwort bestaetigen",'.
61. Diese Zeile definiert den Abschnitt '"auth.email": "E-Mail",'.
62. Diese Zeile definiert den Abschnitt '"auth.forgot_generic_response": "Wenn der Account existiert, wurde eine E-Mail gesendet.",'.
63. Diese Zeile definiert den Abschnitt '"auth.forgot_password_button": "Reset-Link anfordern",'.
64. Diese Zeile definiert den Abschnitt '"auth.forgot_password_hint": "Gib deine E-Mail oder deinen Benutzernamen ein, um einen ...'.
65. Diese Zeile definiert den Abschnitt '"auth.forgot_password_link": "Passwort vergessen?",'.
66. Diese Zeile definiert den Abschnitt '"auth.forgot_password_title": "Passwort vergessen",'.
67. Diese Zeile definiert den Abschnitt '"auth.identifier": "E-Mail oder Benutzername",'.
68. Diese Zeile definiert den Abschnitt '"auth.login": "Anmelden",'.
69. Diese Zeile definiert den Abschnitt '"auth.login_button": "Anmelden",'.
70. Diese Zeile definiert den Abschnitt '"auth.login_title": "Anmelden",'.
71. Diese Zeile definiert den Abschnitt '"auth.new_password": "Neues Passwort",'.
72. Diese Zeile definiert den Abschnitt '"auth.old_password": "Altes Passwort",'.
73. Diese Zeile definiert den Abschnitt '"auth.password": "Passwort",'.
74. Diese Zeile definiert den Abschnitt '"auth.password_changed_success": "Passwort wurde erfolgreich geaendert.",'.
75. Diese Zeile definiert den Abschnitt '"auth.register": "Konto erstellen",'.
76. Diese Zeile definiert den Abschnitt '"auth.register_button": "Konto erstellen",'.
77. Diese Zeile definiert den Abschnitt '"auth.register_title": "Registrieren",'.
78. Diese Zeile definiert den Abschnitt '"auth.reset_email_body": "Nutze diesen Link zum Zuruecksetzen deines Passworts: {reset_...'.
79. Diese Zeile definiert den Abschnitt '"auth.reset_email_subject": "MealMate Passwort-Reset",'.
80. Diese Zeile definiert den Abschnitt '"auth.reset_password_button": "Passwort zuruecksetzen",'.
81. Diese Zeile definiert den Abschnitt '"auth.reset_password_title": "Passwort zuruecksetzen",'.
82. Diese Zeile definiert den Abschnitt '"auth.reset_success": "Passwort wurde zurueckgesetzt, bitte neu anmelden.",'.
83. Diese Zeile definiert den Abschnitt '"difficulty.easy": "Einfach",'.
84. Diese Zeile definiert den Abschnitt '"difficulty.hard": "Schwer",'.
85. Diese Zeile definiert den Abschnitt '"difficulty.medium": "Mittel",'.
86. Diese Zeile definiert den Abschnitt '"discover.filter.apply": "Anwenden",'.
87. Diese Zeile definiert den Abschnitt '"discover.filter.category": "Kategorie",'.
88. Diese Zeile definiert den Abschnitt '"discover.filter.difficulty": "Schwierigkeit",'.
89. Diese Zeile definiert den Abschnitt '"discover.filter.ingredient": "Zutat",'.
90. Diese Zeile definiert den Abschnitt '"discover.filter.title_contains": "Titel enthaelt",'.
91. Diese Zeile definiert den Abschnitt '"discover.sort.newest": "Neueste",'.
92. Diese Zeile definiert den Abschnitt '"discover.sort.oldest": "Aelteste",'.
93. Diese Zeile definiert den Abschnitt '"discover.sort.prep_time": "Zubereitungszeit",'.
94. Diese Zeile definiert den Abschnitt '"discover.sort.rating_asc": "Schlechteste Bewertung",'.
95. Diese Zeile definiert den Abschnitt '"discover.sort.rating_desc": "Beste Bewertung",'.
96. Diese Zeile definiert den Abschnitt '"discover.title": "Rezepte entdecken",'.
97. Diese Zeile definiert den Abschnitt '"empty.no_recipes": "Keine Rezepte gefunden.",'.
98. Diese Zeile definiert den Abschnitt '"error.404_text": "Die angeforderte Seite existiert nicht oder wurde verschoben.",'.
99. Diese Zeile definiert den Abschnitt '"error.404_title": "404 - Seite nicht gefunden",'.
100. Diese Zeile definiert den Abschnitt '"error.500_text": "Beim Verarbeiten der Anfrage ist ein unerwarteter Fehler aufgetreten.",'.
101. Diese Zeile definiert den Abschnitt '"error.500_title": "500 - Interner Fehler",'.
102. Diese Zeile definiert den Abschnitt '"error.admin_required": "Administratorrechte erforderlich.",'.
103. Diese Zeile definiert den Abschnitt '"error.auth_required": "Anmeldung erforderlich.",'.
104. Diese Zeile definiert den Abschnitt '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
105. Diese Zeile definiert den Abschnitt '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
106. Diese Zeile definiert den Abschnitt '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
107. Diese Zeile definiert den Abschnitt '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
108. Diese Zeile definiert den Abschnitt '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
109. Diese Zeile definiert den Abschnitt '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
110. Diese Zeile definiert den Abschnitt '"error.email_registered": "Diese E-Mail ist bereits registriert.",'.
111. Diese Zeile definiert den Abschnitt '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
112. Diese Zeile definiert den Abschnitt '"error.field_positive": "{field} muss groesser als null sein.",'.
113. Diese Zeile definiert den Abschnitt '"error.home_link": "Zur Startseite",'.
114. Diese Zeile definiert den Abschnitt '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
115. Diese Zeile definiert den Abschnitt '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
116. Diese Zeile definiert den Abschnitt '"error.image_not_found": "Bild nicht gefunden.",'.
117. Diese Zeile definiert den Abschnitt '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
118. Diese Zeile definiert den Abschnitt '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
119. Diese Zeile definiert den Abschnitt '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
120. Diese Zeile definiert den Abschnitt '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
121. Diese Zeile definiert den Abschnitt '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
122. Diese Zeile definiert den Abschnitt '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschloss...'.
123. Diese Zeile definiert den Abschnitt '"error.internal": "Interner Serverfehler.",'.
124. Diese Zeile definiert den Abschnitt '"error.invalid_credentials": "Ungueltige Zugangsdaten.",'.
125. Diese Zeile definiert den Abschnitt '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
126. Diese Zeile definiert den Abschnitt '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
127. Diese Zeile definiert den Abschnitt '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
128. Diese Zeile definiert den Abschnitt '"error.not_found": "Ressource nicht gefunden.",'.
129. Diese Zeile definiert den Abschnitt '"error.password_confirm_mismatch": "Passwort und Bestaetigung stimmen nicht ueberein.",'.
130. Diese Zeile definiert den Abschnitt '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
131. Diese Zeile definiert den Abschnitt '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
132. Diese Zeile definiert den Abschnitt '"error.password_old_invalid": "Das alte Passwort ist ungueltig.",'.
133. Diese Zeile definiert den Abschnitt '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
134. Diese Zeile definiert den Abschnitt '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
135. Diese Zeile definiert den Abschnitt '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
136. Diese Zeile definiert den Abschnitt '"error.recipe_not_found": "Rezept nicht gefunden.",'.
137. Diese Zeile definiert den Abschnitt '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
138. Diese Zeile definiert den Abschnitt '"error.reset_token_invalid": "Der Reset-Link ist ungueltig oder abgelaufen.",'.
139. Diese Zeile definiert den Abschnitt '"error.review_not_found": "Bewertung nicht gefunden.",'.
140. Diese Zeile definiert den Abschnitt '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
141. Diese Zeile definiert den Abschnitt '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
142. Diese Zeile definiert den Abschnitt '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
143. Diese Zeile definiert den Abschnitt '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht g...'.
144. Diese Zeile definiert den Abschnitt '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
145. Diese Zeile definiert den Abschnitt '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
146. Diese Zeile definiert den Abschnitt '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
147. Diese Zeile definiert den Abschnitt '"error.submission_not_found": "Einreichung nicht gefunden.",'.
148. Diese Zeile definiert den Abschnitt '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
149. Diese Zeile definiert den Abschnitt '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
150. Diese Zeile definiert den Abschnitt '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
151. Diese Zeile definiert den Abschnitt '"error.trace": "Stacktrace (nur Dev)",'.
152. Diese Zeile definiert den Abschnitt '"error.user_not_found": "Nutzer nicht gefunden.",'.
153. Diese Zeile definiert den Abschnitt '"error.username_invalid": "Benutzername muss 3-30 Zeichen haben und darf nur a-z, A-Z, ...'.
154. Diese Zeile definiert den Abschnitt '"error.username_taken": "Dieser Benutzername ist bereits vergeben.",'.
155. Diese Zeile definiert den Abschnitt '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
156. Diese Zeile definiert den Abschnitt '"favorite.add": "Zu Favoriten",'.
157. Diese Zeile definiert den Abschnitt '"favorite.remove": "Aus Favoriten entfernen",'.
158. Diese Zeile definiert den Abschnitt '"favorites.empty": "Keine Favoriten gespeichert.",'.
159. Diese Zeile definiert den Abschnitt '"favorites.remove": "Favorit entfernen",'.
160. Diese Zeile definiert den Abschnitt '"favorites.title": "Favoriten",'.
161. Diese Zeile definiert den Abschnitt '"home.all_categories": "Alle Kategorien",'.
162. Diese Zeile definiert den Abschnitt '"home.apply": "Anwenden",'.
163. Diese Zeile definiert den Abschnitt '"home.category": "Kategorie",'.
164. Diese Zeile definiert den Abschnitt '"home.difficulty": "Schwierigkeit",'.
165. Diese Zeile definiert den Abschnitt '"home.ingredient": "Zutat",'.
166. Diese Zeile definiert den Abschnitt '"home.per_page": "Pro Seite",'.
167. Diese Zeile definiert den Abschnitt '"home.title": "Rezepte entdecken",'.
168. Diese Zeile definiert den Abschnitt '"home.title_contains": "Titel enthaelt",'.
169. Diese Zeile definiert den Abschnitt '"images.delete": "Loeschen",'.
170. Diese Zeile definiert den Abschnitt '"images.empty": "Noch keine Bilder vorhanden.",'.
171. Diese Zeile definiert den Abschnitt '"images.new_file": "Neue Bilddatei",'.
172. Diese Zeile definiert den Abschnitt '"images.primary": "Hauptbild",'.
173. Diese Zeile definiert den Abschnitt '"images.set_primary": "Als Hauptbild setzen",'.
174. Diese Zeile definiert den Abschnitt '"images.title": "Bilder",'.
175. Diese Zeile definiert den Abschnitt '"images.upload": "Bild hochladen",'.
176. Diese Zeile definiert den Abschnitt '"moderation.approve": "Freigeben",'.
177. Diese Zeile definiert den Abschnitt '"moderation.pending": "Ausstehend",'.
178. Diese Zeile definiert den Abschnitt '"moderation.reject": "Ablehnen",'.
179. Diese Zeile definiert den Abschnitt '"moderation.title": "Moderations-Warteschlange",'.
180. Diese Zeile definiert den Abschnitt '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
181. Diese Zeile definiert den Abschnitt '"my_recipes.title": "Meine Rezepte",'.
182. Diese Zeile definiert den Abschnitt '"nav.admin": "Admin",'.
183. Diese Zeile definiert den Abschnitt '"nav.admin_submissions": "Moderation",'.
184. Diese Zeile definiert den Abschnitt '"nav.create_recipe": "Rezept erstellen",'.
185. Diese Zeile definiert den Abschnitt '"nav.discover": "Rezepte entdecken",'.
186. Diese Zeile definiert den Abschnitt '"nav.favorites": "Favoriten",'.
187. Diese Zeile definiert den Abschnitt '"nav.language": "Sprache",'.
188. Diese Zeile definiert den Abschnitt '"nav.login": "Anmelden",'.
189. Diese Zeile definiert den Abschnitt '"nav.logout": "Abmelden",'.
190. Diese Zeile definiert den Abschnitt '"nav.my_recipes": "Meine Rezepte",'.
191. Diese Zeile definiert den Abschnitt '"nav.my_submissions": "Meine Einreichungen",'.
192. Diese Zeile definiert den Abschnitt '"nav.profile": "Mein Profil",'.
193. Diese Zeile definiert den Abschnitt '"nav.publish_recipe": "Rezept veroeffentlichen",'.
194. Diese Zeile definiert den Abschnitt '"nav.register": "Registrieren",'.
195. Diese Zeile definiert den Abschnitt '"nav.submit": "Rezept einreichen",'.
196. Diese Zeile definiert den Abschnitt '"nav.submit_recipe": "Rezept einreichen",'.
197. Diese Zeile definiert den Abschnitt '"pagination.first": "Erste",'.
198. Diese Zeile definiert den Abschnitt '"pagination.last": "Letzte",'.
199. Diese Zeile definiert den Abschnitt '"pagination.next": "Weiter",'.
200. Diese Zeile definiert den Abschnitt '"pagination.page": "Seite",'.
201. Diese Zeile definiert den Abschnitt '"pagination.prev": "Zurueck",'.
202. Diese Zeile definiert den Abschnitt '"pagination.previous": "Zurueck",'.
203. Diese Zeile definiert den Abschnitt '"pagination.results_range": "Zeige {start}-{end} von {total} Rezepten",'.
204. Diese Zeile definiert den Abschnitt '"profile.email": "E-Mail",'.
205. Diese Zeile definiert den Abschnitt '"profile.joined": "Registriert am",'.
206. Diese Zeile definiert den Abschnitt '"profile.role": "Rolle",'.
207. Diese Zeile definiert den Abschnitt '"profile.title": "Mein Profil",'.
208. Diese Zeile definiert den Abschnitt '"profile.user_uid": "Deine Nutzer-ID",'.
209. Diese Zeile definiert den Abschnitt '"profile.username": "Benutzername",'.
210. Diese Zeile definiert den Abschnitt '"profile.username_change_title": "Benutzername aendern",'.
211. Diese Zeile definiert den Abschnitt '"profile.username_save": "Benutzernamen speichern",'.
212. Diese Zeile definiert den Abschnitt '"profile.username_updated": "Benutzername wurde aktualisiert.",'.
213. Diese Zeile definiert den Abschnitt '"recipe.average_rating": "Durchschnittliche Bewertung",'.
214. Diese Zeile definiert den Abschnitt '"recipe.comment": "Kommentar",'.
215. Diese Zeile definiert den Abschnitt '"recipe.delete": "Loeschen",'.
216. Diese Zeile definiert den Abschnitt '"recipe.edit": "Bearbeiten",'.
217. Diese Zeile definiert den Abschnitt '"recipe.ingredients": "Zutaten",'.
218. Diese Zeile definiert den Abschnitt '"recipe.instructions": "Anleitung",'.
219. Diese Zeile definiert den Abschnitt '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
220. Diese Zeile definiert den Abschnitt '"recipe.no_results": "Keine Rezepte gefunden.",'.
221. Diese Zeile definiert den Abschnitt '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
222. Diese Zeile definiert den Abschnitt '"recipe.pdf_download": "PDF herunterladen",'.
223. Diese Zeile definiert den Abschnitt '"recipe.rating": "Bewertung",'.
224. Diese Zeile definiert den Abschnitt '"recipe.rating_short": "Bewertung",'.
225. Diese Zeile definiert den Abschnitt '"recipe.review_count_label": "Bewertungen",'.
226. Diese Zeile definiert den Abschnitt '"recipe.reviews": "Bewertungen",'.
227. Diese Zeile definiert den Abschnitt '"recipe.save_review": "Bewertung speichern",'.
228. Diese Zeile definiert den Abschnitt '"recipe_form.category": "Kategorie",'.
229. Diese Zeile definiert den Abschnitt '"recipe_form.create": "Erstellen",'.
230. Diese Zeile definiert den Abschnitt '"recipe_form.create_title": "Rezept veroeffentlichen",'.
231. Diese Zeile definiert den Abschnitt '"recipe_form.description": "Beschreibung",'.
232. Diese Zeile definiert den Abschnitt '"recipe_form.difficulty": "Schwierigkeit",'.
233. Diese Zeile definiert den Abschnitt '"recipe_form.edit_title": "Rezept bearbeiten",'.
234. Diese Zeile definiert den Abschnitt '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
235. Diese Zeile definiert den Abschnitt '"recipe_form.instructions": "Anleitung",'.
236. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_label": "Neue Kategorie",'.
237. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_option": "Neue Kategorie...",'.
238. Diese Zeile definiert den Abschnitt '"recipe_form.optional_image": "Optionales Bild",'.
239. Diese Zeile definiert den Abschnitt '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
240. Diese Zeile definiert den Abschnitt '"recipe_form.save": "Speichern",'.
241. Diese Zeile definiert den Abschnitt '"recipe_form.title": "Titel",'.
242. Diese Zeile definiert den Abschnitt '"recipe_form.title_image_url": "Titelbild-URL",'.
243. Diese Zeile definiert den Abschnitt '"role.admin": "Administrator",'.
244. Diese Zeile definiert den Abschnitt '"role.user": "Nutzer",'.
245. Diese Zeile definiert den Abschnitt '"sort.highest_rated": "Beste Bewertung",'.
246. Diese Zeile definiert den Abschnitt '"sort.lowest_rated": "Schlechteste Bewertung",'.
247. Diese Zeile definiert den Abschnitt '"sort.newest": "Neueste",'.
248. Diese Zeile definiert den Abschnitt '"sort.oldest": "Aelteste",'.
249. Diese Zeile definiert den Abschnitt '"sort.prep_time": "Zubereitungszeit",'.
250. Diese Zeile definiert den Abschnitt '"submission.admin_detail_title": "Einreichung",'.
251. Diese Zeile definiert den Abschnitt '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
252. Diese Zeile definiert den Abschnitt '"submission.admin_note": "Admin-Notiz",'.
253. Diese Zeile definiert den Abschnitt '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
254. Diese Zeile definiert den Abschnitt '"submission.admin_queue_title": "Moderations-Warteschlange",'.
255. Diese Zeile definiert den Abschnitt '"submission.approve_button": "Freigeben",'.
256. Diese Zeile definiert den Abschnitt '"submission.approved": "Einreichung wurde freigegeben.",'.
257. Diese Zeile definiert den Abschnitt '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
258. Diese Zeile definiert den Abschnitt '"submission.category": "Kategorie",'.
259. Diese Zeile definiert den Abschnitt '"submission.default_description": "Rezept-Einreichung",'.
260. Diese Zeile definiert den Abschnitt '"submission.description": "Beschreibung",'.
261. Diese Zeile definiert den Abschnitt '"submission.difficulty": "Schwierigkeit",'.
262. Diese Zeile definiert den Abschnitt '"submission.edit_submission": "Einreichung bearbeiten",'.
263. Diese Zeile definiert den Abschnitt '"submission.guest": "Gast",'.
264. Diese Zeile definiert den Abschnitt '"submission.image_deleted": "Bild wurde entfernt.",'.
265. Diese Zeile definiert den Abschnitt '"submission.image_optional": "Optionales Bild",'.
266. Diese Zeile definiert den Abschnitt '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
267. Diese Zeile definiert den Abschnitt '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
268. Diese Zeile definiert den Abschnitt '"submission.instructions": "Anleitung",'.
269. Diese Zeile definiert den Abschnitt '"submission.moderation_actions": "Moderations-Aktionen",'.
270. Diese Zeile definiert den Abschnitt '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
271. Diese Zeile definiert den Abschnitt '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf ...'.
272. Diese Zeile definiert den Abschnitt '"submission.my_title": "Meine Einreichungen",'.
273. Diese Zeile definiert den Abschnitt '"submission.new_category_label": "Neue Kategorie",'.
274. Diese Zeile definiert den Abschnitt '"submission.new_category_option": "Neue Kategorie...",'.
275. Diese Zeile definiert den Abschnitt '"submission.open_detail": "Details",'.
276. Diese Zeile definiert den Abschnitt '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
277. Diese Zeile definiert den Abschnitt '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
278. Diese Zeile definiert den Abschnitt '"submission.preview": "Vorschau",'.
279. Diese Zeile definiert den Abschnitt '"submission.reject_button": "Ablehnen",'.
280. Diese Zeile definiert den Abschnitt '"submission.reject_reason": "Ablehnungsgrund",'.
281. Diese Zeile definiert den Abschnitt '"submission.rejected": "Einreichung wurde abgelehnt.",'.
282. Diese Zeile definiert den Abschnitt '"submission.save_changes": "Aenderungen speichern",'.
283. Diese Zeile definiert den Abschnitt '"submission.servings": "Portionen (optional)",'.
284. Diese Zeile definiert den Abschnitt '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
285. Diese Zeile definiert den Abschnitt '"submission.stats_approved": "Freigegeben",'.
286. Diese Zeile definiert den Abschnitt '"submission.stats_pending": "Ausstehend",'.
287. Diese Zeile definiert den Abschnitt '"submission.stats_rejected": "Abgelehnt",'.
288. Diese Zeile definiert den Abschnitt '"submission.status_all": "Alle",'.
289. Diese Zeile definiert den Abschnitt '"submission.status_approved": "Freigegeben",'.
290. Diese Zeile definiert den Abschnitt '"submission.status_filter": "Status",'.
291. Diese Zeile definiert den Abschnitt '"submission.status_pending": "Ausstehend",'.
292. Diese Zeile definiert den Abschnitt '"submission.status_rejected": "Abgelehnt",'.
293. Diese Zeile definiert den Abschnitt '"submission.submit_button": "Zur Pruefung einreichen",'.
294. Diese Zeile definiert den Abschnitt '"submission.submit_hint": "Einreichungen werden vor der Veroeffentlichung durch das Adm...'.
295. Diese Zeile definiert den Abschnitt '"submission.submit_title": "Rezept einreichen",'.
296. Diese Zeile definiert den Abschnitt '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
297. Diese Zeile definiert den Abschnitt '"submission.table_action": "Aktion",'.
298. Diese Zeile definiert den Abschnitt '"submission.table_date": "Datum",'.
299. Diese Zeile definiert den Abschnitt '"submission.table_status": "Status",'.
300. Diese Zeile definiert den Abschnitt '"submission.table_submitter": "Einreicher",'.
301. Diese Zeile definiert den Abschnitt '"submission.table_title": "Titel",'.
302. Diese Zeile definiert den Abschnitt '"submission.thank_you": "Vielen Dank! Dein Rezept wurde eingereicht und wird geprueft.",'.
303. Diese Zeile definiert den Abschnitt '"submission.title": "Titel",'.
304. Diese Zeile definiert den Abschnitt '"submission.updated": "Einreichung wurde aktualisiert."'.
305. Diese Zeile definiert den Abschnitt '}'.

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
  "auth.confirm_password": "Confirm password",
  "auth.email": "Email",
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
58. Diese Zeile definiert den Abschnitt '"auth.change_password_button": "Update password",'.
59. Diese Zeile definiert den Abschnitt '"auth.change_password_title": "Change Password",'.
60. Diese Zeile definiert den Abschnitt '"auth.confirm_password": "Confirm password",'.
61. Diese Zeile definiert den Abschnitt '"auth.email": "Email",'.
62. Diese Zeile definiert den Abschnitt '"auth.forgot_generic_response": "If the account exists, an email has been sent.",'.
63. Diese Zeile definiert den Abschnitt '"auth.forgot_password_button": "Request reset link",'.
64. Diese Zeile definiert den Abschnitt '"auth.forgot_password_hint": "Enter your email or username to receive a reset link.",'.
65. Diese Zeile definiert den Abschnitt '"auth.forgot_password_link": "Forgot password?",'.
66. Diese Zeile definiert den Abschnitt '"auth.forgot_password_title": "Forgot Password",'.
67. Diese Zeile definiert den Abschnitt '"auth.identifier": "Email or username",'.
68. Diese Zeile definiert den Abschnitt '"auth.login": "Login",'.
69. Diese Zeile definiert den Abschnitt '"auth.login_button": "Login",'.
70. Diese Zeile definiert den Abschnitt '"auth.login_title": "Login",'.
71. Diese Zeile definiert den Abschnitt '"auth.new_password": "New password",'.
72. Diese Zeile definiert den Abschnitt '"auth.old_password": "Current password",'.
73. Diese Zeile definiert den Abschnitt '"auth.password": "Password",'.
74. Diese Zeile definiert den Abschnitt '"auth.password_changed_success": "Password was changed successfully.",'.
75. Diese Zeile definiert den Abschnitt '"auth.register": "Register",'.
76. Diese Zeile definiert den Abschnitt '"auth.register_button": "Create account",'.
77. Diese Zeile definiert den Abschnitt '"auth.register_title": "Register",'.
78. Diese Zeile definiert den Abschnitt '"auth.reset_email_body": "Use this link to reset your password: {reset_link}",'.
79. Diese Zeile definiert den Abschnitt '"auth.reset_email_subject": "MealMate Password Reset",'.
80. Diese Zeile definiert den Abschnitt '"auth.reset_password_button": "Reset password",'.
81. Diese Zeile definiert den Abschnitt '"auth.reset_password_title": "Reset Password",'.
82. Diese Zeile definiert den Abschnitt '"auth.reset_success": "Password was reset, please sign in again.",'.
83. Diese Zeile definiert den Abschnitt '"difficulty.easy": "Easy",'.
84. Diese Zeile definiert den Abschnitt '"difficulty.hard": "Hard",'.
85. Diese Zeile definiert den Abschnitt '"difficulty.medium": "Medium",'.
86. Diese Zeile definiert den Abschnitt '"discover.filter.apply": "Apply",'.
87. Diese Zeile definiert den Abschnitt '"discover.filter.category": "Category",'.
88. Diese Zeile definiert den Abschnitt '"discover.filter.difficulty": "Difficulty",'.
89. Diese Zeile definiert den Abschnitt '"discover.filter.ingredient": "Ingredient",'.
90. Diese Zeile definiert den Abschnitt '"discover.filter.title_contains": "Title contains",'.
91. Diese Zeile definiert den Abschnitt '"discover.sort.newest": "Newest",'.
92. Diese Zeile definiert den Abschnitt '"discover.sort.oldest": "Oldest",'.
93. Diese Zeile definiert den Abschnitt '"discover.sort.prep_time": "Prep time",'.
94. Diese Zeile definiert den Abschnitt '"discover.sort.rating_asc": "Lowest rated",'.
95. Diese Zeile definiert den Abschnitt '"discover.sort.rating_desc": "Highest rated",'.
96. Diese Zeile definiert den Abschnitt '"discover.title": "Discover Recipes",'.
97. Diese Zeile definiert den Abschnitt '"empty.no_recipes": "No recipes found.",'.
98. Diese Zeile definiert den Abschnitt '"error.404_text": "The requested page does not exist or has been moved.",'.
99. Diese Zeile definiert den Abschnitt '"error.404_title": "404 - Page Not Found",'.
100. Diese Zeile definiert den Abschnitt '"error.500_text": "An unexpected error occurred while processing the request.",'.
101. Diese Zeile definiert den Abschnitt '"error.500_title": "500 - Internal Error",'.
102. Diese Zeile definiert den Abschnitt '"error.admin_required": "Admin role required.",'.
103. Diese Zeile definiert den Abschnitt '"error.auth_required": "Authentication required.",'.
104. Diese Zeile definiert den Abschnitt '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
105. Diese Zeile definiert den Abschnitt '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
106. Diese Zeile definiert den Abschnitt '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
107. Diese Zeile definiert den Abschnitt '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
108. Diese Zeile definiert den Abschnitt '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
109. Diese Zeile definiert den Abschnitt '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
110. Diese Zeile definiert den Abschnitt '"error.email_registered": "This email is already registered.",'.
111. Diese Zeile definiert den Abschnitt '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
112. Diese Zeile definiert den Abschnitt '"error.field_positive": "{field} muss groesser als null sein.",'.
113. Diese Zeile definiert den Abschnitt '"error.home_link": "Back to Home",'.
114. Diese Zeile definiert den Abschnitt '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
115. Diese Zeile definiert den Abschnitt '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
116. Diese Zeile definiert den Abschnitt '"error.image_not_found": "Bild nicht gefunden.",'.
117. Diese Zeile definiert den Abschnitt '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
118. Diese Zeile definiert den Abschnitt '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
119. Diese Zeile definiert den Abschnitt '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
120. Diese Zeile definiert den Abschnitt '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
121. Diese Zeile definiert den Abschnitt '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
122. Diese Zeile definiert den Abschnitt '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschloss...'.
123. Diese Zeile definiert den Abschnitt '"error.internal": "Interner Serverfehler.",'.
124. Diese Zeile definiert den Abschnitt '"error.invalid_credentials": "Invalid credentials.",'.
125. Diese Zeile definiert den Abschnitt '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
126. Diese Zeile definiert den Abschnitt '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
127. Diese Zeile definiert den Abschnitt '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
128. Diese Zeile definiert den Abschnitt '"error.not_found": "Ressource nicht gefunden.",'.
129. Diese Zeile definiert den Abschnitt '"error.password_confirm_mismatch": "Password and confirmation do not match.",'.
130. Diese Zeile definiert den Abschnitt '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
131. Diese Zeile definiert den Abschnitt '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
132. Diese Zeile definiert den Abschnitt '"error.password_old_invalid": "Current password is invalid.",'.
133. Diese Zeile definiert den Abschnitt '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
134. Diese Zeile definiert den Abschnitt '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
135. Diese Zeile definiert den Abschnitt '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
136. Diese Zeile definiert den Abschnitt '"error.recipe_not_found": "Rezept nicht gefunden.",'.
137. Diese Zeile definiert den Abschnitt '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
138. Diese Zeile definiert den Abschnitt '"error.reset_token_invalid": "Reset link is invalid or expired.",'.
139. Diese Zeile definiert den Abschnitt '"error.review_not_found": "Bewertung nicht gefunden.",'.
140. Diese Zeile definiert den Abschnitt '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
141. Diese Zeile definiert den Abschnitt '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
142. Diese Zeile definiert den Abschnitt '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
143. Diese Zeile definiert den Abschnitt '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht g...'.
144. Diese Zeile definiert den Abschnitt '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
145. Diese Zeile definiert den Abschnitt '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
146. Diese Zeile definiert den Abschnitt '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
147. Diese Zeile definiert den Abschnitt '"error.submission_not_found": "Einreichung nicht gefunden.",'.
148. Diese Zeile definiert den Abschnitt '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
149. Diese Zeile definiert den Abschnitt '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
150. Diese Zeile definiert den Abschnitt '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
151. Diese Zeile definiert den Abschnitt '"error.trace": "Stacktrace (nur Dev)",'.
152. Diese Zeile definiert den Abschnitt '"error.user_not_found": "Nutzer nicht gefunden.",'.
153. Diese Zeile definiert den Abschnitt '"error.username_invalid": "Username must be 3-30 characters and may only contain letter...'.
154. Diese Zeile definiert den Abschnitt '"error.username_taken": "This username is already taken.",'.
155. Diese Zeile definiert den Abschnitt '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
156. Diese Zeile definiert den Abschnitt '"favorite.add": "Zu Favoriten",'.
157. Diese Zeile definiert den Abschnitt '"favorite.remove": "Aus Favoriten entfernen",'.
158. Diese Zeile definiert den Abschnitt '"favorites.empty": "Keine Favoriten gespeichert.",'.
159. Diese Zeile definiert den Abschnitt '"favorites.remove": "Favorit entfernen",'.
160. Diese Zeile definiert den Abschnitt '"favorites.title": "Favoriten",'.
161. Diese Zeile definiert den Abschnitt '"home.all_categories": "All categories",'.
162. Diese Zeile definiert den Abschnitt '"home.apply": "Apply",'.
163. Diese Zeile definiert den Abschnitt '"home.category": "Category",'.
164. Diese Zeile definiert den Abschnitt '"home.difficulty": "Difficulty",'.
165. Diese Zeile definiert den Abschnitt '"home.ingredient": "Ingredient",'.
166. Diese Zeile definiert den Abschnitt '"home.per_page": "Per page",'.
167. Diese Zeile definiert den Abschnitt '"home.title": "Discover Recipes",'.
168. Diese Zeile definiert den Abschnitt '"home.title_contains": "Title contains",'.
169. Diese Zeile definiert den Abschnitt '"images.delete": "Loeschen",'.
170. Diese Zeile definiert den Abschnitt '"images.empty": "Noch keine Bilder vorhanden.",'.
171. Diese Zeile definiert den Abschnitt '"images.new_file": "Neue Bilddatei",'.
172. Diese Zeile definiert den Abschnitt '"images.primary": "Hauptbild",'.
173. Diese Zeile definiert den Abschnitt '"images.set_primary": "Als Hauptbild setzen",'.
174. Diese Zeile definiert den Abschnitt '"images.title": "Bilder",'.
175. Diese Zeile definiert den Abschnitt '"images.upload": "Bild hochladen",'.
176. Diese Zeile definiert den Abschnitt '"moderation.approve": "Approve",'.
177. Diese Zeile definiert den Abschnitt '"moderation.pending": "Pending",'.
178. Diese Zeile definiert den Abschnitt '"moderation.reject": "Reject",'.
179. Diese Zeile definiert den Abschnitt '"moderation.title": "Moderation Queue",'.
180. Diese Zeile definiert den Abschnitt '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
181. Diese Zeile definiert den Abschnitt '"my_recipes.title": "Meine Rezepte",'.
182. Diese Zeile definiert den Abschnitt '"nav.admin": "Admin",'.
183. Diese Zeile definiert den Abschnitt '"nav.admin_submissions": "Moderation",'.
184. Diese Zeile definiert den Abschnitt '"nav.create_recipe": "Create Recipe",'.
185. Diese Zeile definiert den Abschnitt '"nav.discover": "Discover Recipes",'.
186. Diese Zeile definiert den Abschnitt '"nav.favorites": "Favorites",'.
187. Diese Zeile definiert den Abschnitt '"nav.language": "Language",'.
188. Diese Zeile definiert den Abschnitt '"nav.login": "Login",'.
189. Diese Zeile definiert den Abschnitt '"nav.logout": "Logout",'.
190. Diese Zeile definiert den Abschnitt '"nav.my_recipes": "My Recipes",'.
191. Diese Zeile definiert den Abschnitt '"nav.my_submissions": "My Submissions",'.
192. Diese Zeile definiert den Abschnitt '"nav.profile": "My Profile",'.
193. Diese Zeile definiert den Abschnitt '"nav.publish_recipe": "Publish Recipe",'.
194. Diese Zeile definiert den Abschnitt '"nav.register": "Register",'.
195. Diese Zeile definiert den Abschnitt '"nav.submit": "Submit Recipe",'.
196. Diese Zeile definiert den Abschnitt '"nav.submit_recipe": "Submit Recipe",'.
197. Diese Zeile definiert den Abschnitt '"pagination.first": "First",'.
198. Diese Zeile definiert den Abschnitt '"pagination.last": "Last",'.
199. Diese Zeile definiert den Abschnitt '"pagination.next": "Next",'.
200. Diese Zeile definiert den Abschnitt '"pagination.page": "Page",'.
201. Diese Zeile definiert den Abschnitt '"pagination.prev": "Previous",'.
202. Diese Zeile definiert den Abschnitt '"pagination.previous": "Previous",'.
203. Diese Zeile definiert den Abschnitt '"pagination.results_range": "Showing {start}-{end} of {total} recipes",'.
204. Diese Zeile definiert den Abschnitt '"profile.email": "E-Mail",'.
205. Diese Zeile definiert den Abschnitt '"profile.joined": "Registriert am",'.
206. Diese Zeile definiert den Abschnitt '"profile.role": "Rolle",'.
207. Diese Zeile definiert den Abschnitt '"profile.title": "Mein Profil",'.
208. Diese Zeile definiert den Abschnitt '"profile.user_uid": "Your user ID",'.
209. Diese Zeile definiert den Abschnitt '"profile.username": "Username",'.
210. Diese Zeile definiert den Abschnitt '"profile.username_change_title": "Change username",'.
211. Diese Zeile definiert den Abschnitt '"profile.username_save": "Save username",'.
212. Diese Zeile definiert den Abschnitt '"profile.username_updated": "Username was updated.",'.
213. Diese Zeile definiert den Abschnitt '"recipe.average_rating": "Durchschnittliche Bewertung",'.
214. Diese Zeile definiert den Abschnitt '"recipe.comment": "Kommentar",'.
215. Diese Zeile definiert den Abschnitt '"recipe.delete": "Loeschen",'.
216. Diese Zeile definiert den Abschnitt '"recipe.edit": "Bearbeiten",'.
217. Diese Zeile definiert den Abschnitt '"recipe.ingredients": "Zutaten",'.
218. Diese Zeile definiert den Abschnitt '"recipe.instructions": "Anleitung",'.
219. Diese Zeile definiert den Abschnitt '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
220. Diese Zeile definiert den Abschnitt '"recipe.no_results": "No recipes found.",'.
221. Diese Zeile definiert den Abschnitt '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
222. Diese Zeile definiert den Abschnitt '"recipe.pdf_download": "PDF herunterladen",'.
223. Diese Zeile definiert den Abschnitt '"recipe.rating": "Bewertung",'.
224. Diese Zeile definiert den Abschnitt '"recipe.rating_short": "Bewertung",'.
225. Diese Zeile definiert den Abschnitt '"recipe.review_count_label": "Bewertungen",'.
226. Diese Zeile definiert den Abschnitt '"recipe.reviews": "Bewertungen",'.
227. Diese Zeile definiert den Abschnitt '"recipe.save_review": "Bewertung speichern",'.
228. Diese Zeile definiert den Abschnitt '"recipe_form.category": "Kategorie",'.
229. Diese Zeile definiert den Abschnitt '"recipe_form.create": "Erstellen",'.
230. Diese Zeile definiert den Abschnitt '"recipe_form.create_title": "Rezept veroeffentlichen",'.
231. Diese Zeile definiert den Abschnitt '"recipe_form.description": "Beschreibung",'.
232. Diese Zeile definiert den Abschnitt '"recipe_form.difficulty": "Schwierigkeit",'.
233. Diese Zeile definiert den Abschnitt '"recipe_form.edit_title": "Rezept bearbeiten",'.
234. Diese Zeile definiert den Abschnitt '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
235. Diese Zeile definiert den Abschnitt '"recipe_form.instructions": "Anleitung",'.
236. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_label": "Neue Kategorie",'.
237. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_option": "Neue Kategorie...",'.
238. Diese Zeile definiert den Abschnitt '"recipe_form.optional_image": "Optionales Bild",'.
239. Diese Zeile definiert den Abschnitt '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
240. Diese Zeile definiert den Abschnitt '"recipe_form.save": "Speichern",'.
241. Diese Zeile definiert den Abschnitt '"recipe_form.title": "Titel",'.
242. Diese Zeile definiert den Abschnitt '"recipe_form.title_image_url": "Titelbild-URL",'.
243. Diese Zeile definiert den Abschnitt '"role.admin": "Administrator",'.
244. Diese Zeile definiert den Abschnitt '"role.user": "Nutzer",'.
245. Diese Zeile definiert den Abschnitt '"sort.highest_rated": "Highest rated",'.
246. Diese Zeile definiert den Abschnitt '"sort.lowest_rated": "Lowest rated",'.
247. Diese Zeile definiert den Abschnitt '"sort.newest": "Newest",'.
248. Diese Zeile definiert den Abschnitt '"sort.oldest": "Oldest",'.
249. Diese Zeile definiert den Abschnitt '"sort.prep_time": "Prep time",'.
250. Diese Zeile definiert den Abschnitt '"submission.admin_detail_title": "Einreichung",'.
251. Diese Zeile definiert den Abschnitt '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
252. Diese Zeile definiert den Abschnitt '"submission.admin_note": "Admin-Notiz",'.
253. Diese Zeile definiert den Abschnitt '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
254. Diese Zeile definiert den Abschnitt '"submission.admin_queue_title": "Moderation Queue",'.
255. Diese Zeile definiert den Abschnitt '"submission.approve_button": "Approve",'.
256. Diese Zeile definiert den Abschnitt '"submission.approved": "Einreichung wurde freigegeben.",'.
257. Diese Zeile definiert den Abschnitt '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
258. Diese Zeile definiert den Abschnitt '"submission.category": "Kategorie",'.
259. Diese Zeile definiert den Abschnitt '"submission.default_description": "Rezept-Einreichung",'.
260. Diese Zeile definiert den Abschnitt '"submission.description": "Beschreibung",'.
261. Diese Zeile definiert den Abschnitt '"submission.difficulty": "Schwierigkeit",'.
262. Diese Zeile definiert den Abschnitt '"submission.edit_submission": "Einreichung bearbeiten",'.
263. Diese Zeile definiert den Abschnitt '"submission.guest": "Gast",'.
264. Diese Zeile definiert den Abschnitt '"submission.image_deleted": "Bild wurde entfernt.",'.
265. Diese Zeile definiert den Abschnitt '"submission.image_optional": "Optionales Bild",'.
266. Diese Zeile definiert den Abschnitt '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
267. Diese Zeile definiert den Abschnitt '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
268. Diese Zeile definiert den Abschnitt '"submission.instructions": "Anleitung",'.
269. Diese Zeile definiert den Abschnitt '"submission.moderation_actions": "Moderations-Aktionen",'.
270. Diese Zeile definiert den Abschnitt '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
271. Diese Zeile definiert den Abschnitt '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf ...'.
272. Diese Zeile definiert den Abschnitt '"submission.my_title": "My Submissions",'.
273. Diese Zeile definiert den Abschnitt '"submission.new_category_label": "Neue Kategorie",'.
274. Diese Zeile definiert den Abschnitt '"submission.new_category_option": "Neue Kategorie...",'.
275. Diese Zeile definiert den Abschnitt '"submission.open_detail": "Details",'.
276. Diese Zeile definiert den Abschnitt '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
277. Diese Zeile definiert den Abschnitt '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
278. Diese Zeile definiert den Abschnitt '"submission.preview": "Vorschau",'.
279. Diese Zeile definiert den Abschnitt '"submission.reject_button": "Reject",'.
280. Diese Zeile definiert den Abschnitt '"submission.reject_reason": "Ablehnungsgrund",'.
281. Diese Zeile definiert den Abschnitt '"submission.rejected": "Einreichung wurde abgelehnt.",'.
282. Diese Zeile definiert den Abschnitt '"submission.save_changes": "Aenderungen speichern",'.
283. Diese Zeile definiert den Abschnitt '"submission.servings": "Portionen (optional)",'.
284. Diese Zeile definiert den Abschnitt '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
285. Diese Zeile definiert den Abschnitt '"submission.stats_approved": "Freigegeben",'.
286. Diese Zeile definiert den Abschnitt '"submission.stats_pending": "Ausstehend",'.
287. Diese Zeile definiert den Abschnitt '"submission.stats_rejected": "Abgelehnt",'.
288. Diese Zeile definiert den Abschnitt '"submission.status_all": "Alle",'.
289. Diese Zeile definiert den Abschnitt '"submission.status_approved": "Approved",'.
290. Diese Zeile definiert den Abschnitt '"submission.status_filter": "Status",'.
291. Diese Zeile definiert den Abschnitt '"submission.status_pending": "Pending",'.
292. Diese Zeile definiert den Abschnitt '"submission.status_rejected": "Rejected",'.
293. Diese Zeile definiert den Abschnitt '"submission.submit_button": "Zur Pruefung einreichen",'.
294. Diese Zeile definiert den Abschnitt '"submission.submit_hint": "Submissions are reviewed by admins before publication.",'.
295. Diese Zeile definiert den Abschnitt '"submission.submit_title": "Submit Recipe",'.
296. Diese Zeile definiert den Abschnitt '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
297. Diese Zeile definiert den Abschnitt '"submission.table_action": "Aktion",'.
298. Diese Zeile definiert den Abschnitt '"submission.table_date": "Datum",'.
299. Diese Zeile definiert den Abschnitt '"submission.table_status": "Status",'.
300. Diese Zeile definiert den Abschnitt '"submission.table_submitter": "Einreicher",'.
301. Diese Zeile definiert den Abschnitt '"submission.table_title": "Titel",'.
302. Diese Zeile definiert den Abschnitt '"submission.thank_you": "Thank you! Your recipe has been submitted for review.",'.
303. Diese Zeile definiert den Abschnitt '"submission.title": "Titel",'.
304. Diese Zeile definiert den Abschnitt '"submission.updated": "Einreichung wurde aktualisiert."'.
305. Diese Zeile definiert den Abschnitt '}'.

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
  "auth.confirm_password": "Confirmer le mot de passe",
  "auth.email": "E-mail",
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
58. Diese Zeile definiert den Abschnitt '"auth.change_password_button": "Mettre a jour le mot de passe",'.
59. Diese Zeile definiert den Abschnitt '"auth.change_password_title": "Changer le mot de passe",'.
60. Diese Zeile definiert den Abschnitt '"auth.confirm_password": "Confirmer le mot de passe",'.
61. Diese Zeile definiert den Abschnitt '"auth.email": "E-mail",'.
62. Diese Zeile definiert den Abschnitt '"auth.forgot_generic_response": "Si le compte existe, un e-mail a ete envoye.",'.
63. Diese Zeile definiert den Abschnitt '"auth.forgot_password_button": "Demander un lien",'.
64. Diese Zeile definiert den Abschnitt '"auth.forgot_password_hint": "Entrez votre e-mail ou nom d'utilisateur pour recevoir un...'.
65. Diese Zeile definiert den Abschnitt '"auth.forgot_password_link": "Mot de passe oublie ?",'.
66. Diese Zeile definiert den Abschnitt '"auth.forgot_password_title": "Mot de passe oublie",'.
67. Diese Zeile definiert den Abschnitt '"auth.identifier": "E-mail ou nom d'utilisateur",'.
68. Diese Zeile definiert den Abschnitt '"auth.login": "Connexion",'.
69. Diese Zeile definiert den Abschnitt '"auth.login_button": "Connexion",'.
70. Diese Zeile definiert den Abschnitt '"auth.login_title": "Connexion",'.
71. Diese Zeile definiert den Abschnitt '"auth.new_password": "Nouveau mot de passe",'.
72. Diese Zeile definiert den Abschnitt '"auth.old_password": "Ancien mot de passe",'.
73. Diese Zeile definiert den Abschnitt '"auth.password": "Mot de passe",'.
74. Diese Zeile definiert den Abschnitt '"auth.password_changed_success": "Le mot de passe a ete modifie avec succes.",'.
75. Diese Zeile definiert den Abschnitt '"auth.register": "Inscription",'.
76. Diese Zeile definiert den Abschnitt '"auth.register_button": "Creer un compte",'.
77. Diese Zeile definiert den Abschnitt '"auth.register_title": "Inscription",'.
78. Diese Zeile definiert den Abschnitt '"auth.reset_email_body": "Utilisez ce lien pour reinitialiser votre mot de passe : {res...'.
79. Diese Zeile definiert den Abschnitt '"auth.reset_email_subject": "Reinitialisation du mot de passe MealMate",'.
80. Diese Zeile definiert den Abschnitt '"auth.reset_password_button": "Reinitialiser le mot de passe",'.
81. Diese Zeile definiert den Abschnitt '"auth.reset_password_title": "Reinitialiser le mot de passe",'.
82. Diese Zeile definiert den Abschnitt '"auth.reset_success": "Le mot de passe a ete reinitialise, veuillez vous reconnecter.",'.
83. Diese Zeile definiert den Abschnitt '"difficulty.easy": "Facile",'.
84. Diese Zeile definiert den Abschnitt '"difficulty.hard": "Difficile",'.
85. Diese Zeile definiert den Abschnitt '"difficulty.medium": "Moyen",'.
86. Diese Zeile definiert den Abschnitt '"discover.filter.apply": "Appliquer",'.
87. Diese Zeile definiert den Abschnitt '"discover.filter.category": "Categorie",'.
88. Diese Zeile definiert den Abschnitt '"discover.filter.difficulty": "Difficulte",'.
89. Diese Zeile definiert den Abschnitt '"discover.filter.ingredient": "Ingredient",'.
90. Diese Zeile definiert den Abschnitt '"discover.filter.title_contains": "Le titre contient",'.
91. Diese Zeile definiert den Abschnitt '"discover.sort.newest": "Plus recentes",'.
92. Diese Zeile definiert den Abschnitt '"discover.sort.oldest": "Plus anciennes",'.
93. Diese Zeile definiert den Abschnitt '"discover.sort.prep_time": "Temps de preparation",'.
94. Diese Zeile definiert den Abschnitt '"discover.sort.rating_asc": "Moins bien notees",'.
95. Diese Zeile definiert den Abschnitt '"discover.sort.rating_desc": "Mieux notees",'.
96. Diese Zeile definiert den Abschnitt '"discover.title": "Decouvrir des recettes",'.
97. Diese Zeile definiert den Abschnitt '"empty.no_recipes": "Aucune recette trouvee.",'.
98. Diese Zeile definiert den Abschnitt '"error.404_text": "La page demandee n'existe pas ou a ete deplacee.",'.
99. Diese Zeile definiert den Abschnitt '"error.404_title": "404 - Page introuvable",'.
100. Diese Zeile definiert den Abschnitt '"error.500_text": "Une erreur inattendue est survenue pendant le traitement.",'.
101. Diese Zeile definiert den Abschnitt '"error.500_title": "500 - Erreur interne",'.
102. Diese Zeile definiert den Abschnitt '"error.admin_required": "Role admin requis.",'.
103. Diese Zeile definiert den Abschnitt '"error.auth_required": "Authentification requise.",'.
104. Diese Zeile definiert den Abschnitt '"error.csrf_failed": "CSRF-Pruefung fehlgeschlagen.",'.
105. Diese Zeile definiert den Abschnitt '"error.csv_empty": "Die hochgeladene CSV-Datei ist leer.",'.
106. Diese Zeile definiert den Abschnitt '"error.csv_not_found_prefix": "CSV-Datei nicht gefunden",'.
107. Diese Zeile definiert den Abschnitt '"error.csv_only": "Es sind nur CSV-Uploads erlaubt.",'.
108. Diese Zeile definiert den Abschnitt '"error.csv_too_large": "CSV-Upload ist zu gross.",'.
109. Diese Zeile definiert den Abschnitt '"error.csv_upload_required": "Bitte eine CSV-Datei hochladen.",'.
110. Diese Zeile definiert den Abschnitt '"error.email_registered": "Cet e-mail est deja utilise.",'.
111. Diese Zeile definiert den Abschnitt '"error.field_int": "{field} muss eine ganze Zahl sein.",'.
112. Diese Zeile definiert den Abschnitt '"error.field_positive": "{field} muss groesser als null sein.",'.
113. Diese Zeile definiert den Abschnitt '"error.home_link": "Retour a l'accueil",'.
114. Diese Zeile definiert den Abschnitt '"error.image_format_mismatch": "Das Bildformat passt nicht zum Content-Type.",'.
115. Diese Zeile definiert den Abschnitt '"error.image_invalid": "Die hochgeladene Datei ist kein gueltiges Bild.",'.
116. Diese Zeile definiert den Abschnitt '"error.image_not_found": "Bild nicht gefunden.",'.
117. Diese Zeile definiert den Abschnitt '"error.image_resolve_prefix": "Die Bild-URL konnte nicht aufgeloest werden",'.
118. Diese Zeile definiert den Abschnitt '"error.image_too_large": "Bild ist zu gross. Maximal {max_mb} MB.",'.
119. Diese Zeile definiert den Abschnitt '"error.image_too_small": "Die hochgeladene Datei ist zu klein fuer ein gueltiges Bild.",'.
120. Diese Zeile definiert den Abschnitt '"error.image_url_scheme": "Die title_image_url muss mit http:// oder https:// beginnen.",'.
121. Diese Zeile definiert den Abschnitt '"error.import_finished_insert": "Import im Modus 'nur neu' abgeschlossen.",'.
122. Diese Zeile definiert den Abschnitt '"error.import_finished_update": "Import im Modus 'bestehende aktualisieren' abgeschloss...'.
123. Diese Zeile definiert den Abschnitt '"error.internal": "Interner Serverfehler.",'.
124. Diese Zeile definiert den Abschnitt '"error.invalid_credentials": "Identifiants invalides.",'.
125. Diese Zeile definiert den Abschnitt '"error.magic_mismatch": "Dateisignatur passt nicht zum Content-Type.",'.
126. Diese Zeile definiert den Abschnitt '"error.mime_unsupported": "Nicht unterstuetzter MIME-Typ '{content_type}'.",'.
127. Diese Zeile definiert den Abschnitt '"error.no_image_url": "Keine Bild-URL verfuegbar.",'.
128. Diese Zeile definiert den Abschnitt '"error.not_found": "Ressource nicht gefunden.",'.
129. Diese Zeile definiert den Abschnitt '"error.password_confirm_mismatch": "Le mot de passe et la confirmation ne correspondent...'.
130. Diese Zeile definiert den Abschnitt '"error.password_min_length": "Das Passwort muss mindestens 10 Zeichen enthalten.",'.
131. Diese Zeile definiert den Abschnitt '"error.password_number": "Das Passwort muss mindestens eine Zahl enthalten.",'.
132. Diese Zeile definiert den Abschnitt '"error.password_old_invalid": "L'ancien mot de passe est invalide.",'.
133. Diese Zeile definiert den Abschnitt '"error.password_special": "Das Passwort muss mindestens ein Sonderzeichen enthalten.",'.
134. Diese Zeile definiert den Abschnitt '"error.password_upper": "Das Passwort muss mindestens einen Grossbuchstaben enthalten.",'.
135. Diese Zeile definiert den Abschnitt '"error.rating_range": "Die Bewertung muss zwischen 1 und 5 liegen.",'.
136. Diese Zeile definiert den Abschnitt '"error.recipe_not_found": "Rezept nicht gefunden.",'.
137. Diese Zeile definiert den Abschnitt '"error.recipe_permission": "Keine ausreichenden Rechte fuer dieses Rezept.",'.
138. Diese Zeile definiert den Abschnitt '"error.reset_token_invalid": "Le lien de reinitialisation est invalide ou expire.",'.
139. Diese Zeile definiert den Abschnitt '"error.review_not_found": "Bewertung nicht gefunden.",'.
140. Diese Zeile definiert den Abschnitt '"error.review_permission": "Keine ausreichenden Rechte fuer diese Bewertung.",'.
141. Diese Zeile definiert den Abschnitt '"error.role_invalid": "Die Rolle muss 'user' oder 'admin' sein.",'.
142. Diese Zeile definiert den Abschnitt '"error.seed_already_done": "Der KochWiki-Seed ist bereits als abgeschlossen markiert.",'.
143. Diese Zeile definiert den Abschnitt '"error.seed_finished_errors": "Der Seed wurde mit Fehlern beendet; Marker wurde nicht g...'.
144. Diese Zeile definiert den Abschnitt '"error.seed_not_empty": "Der Seed darf nur bei leerer Rezepttabelle laufen.",'.
145. Diese Zeile definiert den Abschnitt '"error.seed_success": "Der KochWiki-Seed wurde erfolgreich abgeschlossen und markiert.",'.
146. Diese Zeile definiert den Abschnitt '"error.submission_already_published": "Diese Einreichung wurde bereits veroeffentlicht.",'.
147. Diese Zeile definiert den Abschnitt '"error.submission_not_found": "Einreichung nicht gefunden.",'.
148. Diese Zeile definiert den Abschnitt '"error.submission_permission": "Keine ausreichenden Rechte fuer diese Einreichung.",'.
149. Diese Zeile definiert den Abschnitt '"error.submission_reject_reason_required": "Bitte einen Ablehnungsgrund angeben.",'.
150. Diese Zeile definiert den Abschnitt '"error.title_instructions_required": "Titel und Anleitung sind erforderlich.",'.
151. Diese Zeile definiert den Abschnitt '"error.trace": "Stacktrace (nur Dev)",'.
152. Diese Zeile definiert den Abschnitt '"error.user_not_found": "Nutzer nicht gefunden.",'.
153. Diese Zeile definiert den Abschnitt '"error.username_invalid": "Le nom d'utilisateur doit contenir 3 a 30 caracteres et uniq...'.
154. Diese Zeile definiert den Abschnitt '"error.username_taken": "Ce nom d'utilisateur est deja utilise.",'.
155. Diese Zeile definiert den Abschnitt '"error.webp_signature": "Ungueltige WEBP-Dateisignatur.",'.
156. Diese Zeile definiert den Abschnitt '"favorite.add": "Zu Favoriten",'.
157. Diese Zeile definiert den Abschnitt '"favorite.remove": "Aus Favoriten entfernen",'.
158. Diese Zeile definiert den Abschnitt '"favorites.empty": "Keine Favoriten gespeichert.",'.
159. Diese Zeile definiert den Abschnitt '"favorites.remove": "Favorit entfernen",'.
160. Diese Zeile definiert den Abschnitt '"favorites.title": "Favoriten",'.
161. Diese Zeile definiert den Abschnitt '"home.all_categories": "Toutes les categories",'.
162. Diese Zeile definiert den Abschnitt '"home.apply": "Appliquer",'.
163. Diese Zeile definiert den Abschnitt '"home.category": "Categorie",'.
164. Diese Zeile definiert den Abschnitt '"home.difficulty": "Difficulte",'.
165. Diese Zeile definiert den Abschnitt '"home.ingredient": "Ingredient",'.
166. Diese Zeile definiert den Abschnitt '"home.per_page": "Par page",'.
167. Diese Zeile definiert den Abschnitt '"home.title": "Decouvrir des recettes",'.
168. Diese Zeile definiert den Abschnitt '"home.title_contains": "Le titre contient",'.
169. Diese Zeile definiert den Abschnitt '"images.delete": "Loeschen",'.
170. Diese Zeile definiert den Abschnitt '"images.empty": "Noch keine Bilder vorhanden.",'.
171. Diese Zeile definiert den Abschnitt '"images.new_file": "Neue Bilddatei",'.
172. Diese Zeile definiert den Abschnitt '"images.primary": "Hauptbild",'.
173. Diese Zeile definiert den Abschnitt '"images.set_primary": "Als Hauptbild setzen",'.
174. Diese Zeile definiert den Abschnitt '"images.title": "Bilder",'.
175. Diese Zeile definiert den Abschnitt '"images.upload": "Bild hochladen",'.
176. Diese Zeile definiert den Abschnitt '"moderation.approve": "Approuver",'.
177. Diese Zeile definiert den Abschnitt '"moderation.pending": "En attente",'.
178. Diese Zeile definiert den Abschnitt '"moderation.reject": "Rejeter",'.
179. Diese Zeile definiert den Abschnitt '"moderation.title": "File de moderation",'.
180. Diese Zeile definiert den Abschnitt '"my_recipes.empty": "Noch keine Rezepte vorhanden.",'.
181. Diese Zeile definiert den Abschnitt '"my_recipes.title": "Meine Rezepte",'.
182. Diese Zeile definiert den Abschnitt '"nav.admin": "Admin",'.
183. Diese Zeile definiert den Abschnitt '"nav.admin_submissions": "Moderation",'.
184. Diese Zeile definiert den Abschnitt '"nav.create_recipe": "Creer une recette",'.
185. Diese Zeile definiert den Abschnitt '"nav.discover": "Decouvrir des recettes",'.
186. Diese Zeile definiert den Abschnitt '"nav.favorites": "Favoris",'.
187. Diese Zeile definiert den Abschnitt '"nav.language": "Langue",'.
188. Diese Zeile definiert den Abschnitt '"nav.login": "Connexion",'.
189. Diese Zeile definiert den Abschnitt '"nav.logout": "Deconnexion",'.
190. Diese Zeile definiert den Abschnitt '"nav.my_recipes": "Mes recettes",'.
191. Diese Zeile definiert den Abschnitt '"nav.my_submissions": "Mes soumissions",'.
192. Diese Zeile definiert den Abschnitt '"nav.profile": "Mon profil",'.
193. Diese Zeile definiert den Abschnitt '"nav.publish_recipe": "Publier une recette",'.
194. Diese Zeile definiert den Abschnitt '"nav.register": "Inscription",'.
195. Diese Zeile definiert den Abschnitt '"nav.submit": "Soumettre une recette",'.
196. Diese Zeile definiert den Abschnitt '"nav.submit_recipe": "Soumettre une recette",'.
197. Diese Zeile definiert den Abschnitt '"pagination.first": "Premier",'.
198. Diese Zeile definiert den Abschnitt '"pagination.last": "Dernier",'.
199. Diese Zeile definiert den Abschnitt '"pagination.next": "Suivant",'.
200. Diese Zeile definiert den Abschnitt '"pagination.page": "Page",'.
201. Diese Zeile definiert den Abschnitt '"pagination.prev": "Precedent",'.
202. Diese Zeile definiert den Abschnitt '"pagination.previous": "Precedent",'.
203. Diese Zeile definiert den Abschnitt '"pagination.results_range": "Affichage {start}-{end} sur {total} recettes",'.
204. Diese Zeile definiert den Abschnitt '"profile.email": "E-Mail",'.
205. Diese Zeile definiert den Abschnitt '"profile.joined": "Registriert am",'.
206. Diese Zeile definiert den Abschnitt '"profile.role": "Rolle",'.
207. Diese Zeile definiert den Abschnitt '"profile.title": "Mein Profil",'.
208. Diese Zeile definiert den Abschnitt '"profile.user_uid": "Votre identifiant utilisateur",'.
209. Diese Zeile definiert den Abschnitt '"profile.username": "Nom d'utilisateur",'.
210. Diese Zeile definiert den Abschnitt '"profile.username_change_title": "Changer le nom d'utilisateur",'.
211. Diese Zeile definiert den Abschnitt '"profile.username_save": "Enregistrer le nom d'utilisateur",'.
212. Diese Zeile definiert den Abschnitt '"profile.username_updated": "Le nom d'utilisateur a ete mis a jour.",'.
213. Diese Zeile definiert den Abschnitt '"recipe.average_rating": "Durchschnittliche Bewertung",'.
214. Diese Zeile definiert den Abschnitt '"recipe.comment": "Kommentar",'.
215. Diese Zeile definiert den Abschnitt '"recipe.delete": "Loeschen",'.
216. Diese Zeile definiert den Abschnitt '"recipe.edit": "Bearbeiten",'.
217. Diese Zeile definiert den Abschnitt '"recipe.ingredients": "Zutaten",'.
218. Diese Zeile definiert den Abschnitt '"recipe.instructions": "Anleitung",'.
219. Diese Zeile definiert den Abschnitt '"recipe.no_ingredients": "Keine Zutaten gespeichert.",'.
220. Diese Zeile definiert den Abschnitt '"recipe.no_results": "Aucune recette trouvee.",'.
221. Diese Zeile definiert den Abschnitt '"recipe.no_reviews": "Noch keine Bewertungen vorhanden.",'.
222. Diese Zeile definiert den Abschnitt '"recipe.pdf_download": "PDF herunterladen",'.
223. Diese Zeile definiert den Abschnitt '"recipe.rating": "Bewertung",'.
224. Diese Zeile definiert den Abschnitt '"recipe.rating_short": "Bewertung",'.
225. Diese Zeile definiert den Abschnitt '"recipe.review_count_label": "Bewertungen",'.
226. Diese Zeile definiert den Abschnitt '"recipe.reviews": "Bewertungen",'.
227. Diese Zeile definiert den Abschnitt '"recipe.save_review": "Bewertung speichern",'.
228. Diese Zeile definiert den Abschnitt '"recipe_form.category": "Kategorie",'.
229. Diese Zeile definiert den Abschnitt '"recipe_form.create": "Erstellen",'.
230. Diese Zeile definiert den Abschnitt '"recipe_form.create_title": "Rezept veroeffentlichen",'.
231. Diese Zeile definiert den Abschnitt '"recipe_form.description": "Beschreibung",'.
232. Diese Zeile definiert den Abschnitt '"recipe_form.difficulty": "Schwierigkeit",'.
233. Diese Zeile definiert den Abschnitt '"recipe_form.edit_title": "Rezept bearbeiten",'.
234. Diese Zeile definiert den Abschnitt '"recipe_form.ingredients": "Zutaten (Format: name|menge|gramm)",'.
235. Diese Zeile definiert den Abschnitt '"recipe_form.instructions": "Anleitung",'.
236. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_label": "Neue Kategorie",'.
237. Diese Zeile definiert den Abschnitt '"recipe_form.new_category_option": "Neue Kategorie...",'.
238. Diese Zeile definiert den Abschnitt '"recipe_form.optional_image": "Optionales Bild",'.
239. Diese Zeile definiert den Abschnitt '"recipe_form.prep_time": "Zubereitungszeit (Minuten)",'.
240. Diese Zeile definiert den Abschnitt '"recipe_form.save": "Speichern",'.
241. Diese Zeile definiert den Abschnitt '"recipe_form.title": "Titel",'.
242. Diese Zeile definiert den Abschnitt '"recipe_form.title_image_url": "Titelbild-URL",'.
243. Diese Zeile definiert den Abschnitt '"role.admin": "Administrator",'.
244. Diese Zeile definiert den Abschnitt '"role.user": "Nutzer",'.
245. Diese Zeile definiert den Abschnitt '"sort.highest_rated": "Mieux notees",'.
246. Diese Zeile definiert den Abschnitt '"sort.lowest_rated": "Moins bien notees",'.
247. Diese Zeile definiert den Abschnitt '"sort.newest": "Plus recentes",'.
248. Diese Zeile definiert den Abschnitt '"sort.oldest": "Plus anciennes",'.
249. Diese Zeile definiert den Abschnitt '"sort.prep_time": "Temps de preparation",'.
250. Diese Zeile definiert den Abschnitt '"submission.admin_detail_title": "Einreichung",'.
251. Diese Zeile definiert den Abschnitt '"submission.admin_empty": "Keine Einreichungen gefunden.",'.
252. Diese Zeile definiert den Abschnitt '"submission.admin_note": "Admin-Notiz",'.
253. Diese Zeile definiert den Abschnitt '"submission.admin_queue_link": "Zur Moderations-Warteschlange",'.
254. Diese Zeile definiert den Abschnitt '"submission.admin_queue_title": "File de moderation",'.
255. Diese Zeile definiert den Abschnitt '"submission.approve_button": "Approuver",'.
256. Diese Zeile definiert den Abschnitt '"submission.approved": "Einreichung wurde freigegeben.",'.
257. Diese Zeile definiert den Abschnitt '"submission.back_to_queue": "Zurueck zur Warteschlange",'.
258. Diese Zeile definiert den Abschnitt '"submission.category": "Kategorie",'.
259. Diese Zeile definiert den Abschnitt '"submission.default_description": "Rezept-Einreichung",'.
260. Diese Zeile definiert den Abschnitt '"submission.description": "Beschreibung",'.
261. Diese Zeile definiert den Abschnitt '"submission.difficulty": "Schwierigkeit",'.
262. Diese Zeile definiert den Abschnitt '"submission.edit_submission": "Einreichung bearbeiten",'.
263. Diese Zeile definiert den Abschnitt '"submission.guest": "Gast",'.
264. Diese Zeile definiert den Abschnitt '"submission.image_deleted": "Bild wurde entfernt.",'.
265. Diese Zeile definiert den Abschnitt '"submission.image_optional": "Optionales Bild",'.
266. Diese Zeile definiert den Abschnitt '"submission.image_primary": "Hauptbild wurde gesetzt.",'.
267. Diese Zeile definiert den Abschnitt '"submission.ingredients": "Zutaten (Format: name|menge|gramm)",'.
268. Diese Zeile definiert den Abschnitt '"submission.instructions": "Anleitung",'.
269. Diese Zeile definiert den Abschnitt '"submission.moderation_actions": "Moderations-Aktionen",'.
270. Diese Zeile definiert den Abschnitt '"submission.my_empty": "Du hast noch keine Einreichungen.",'.
271. Diese Zeile definiert den Abschnitt '"submission.my_submitted_message": "Deine Einreichung wurde gespeichert und wartet auf ...'.
272. Diese Zeile definiert den Abschnitt '"submission.my_title": "Mes soumissions",'.
273. Diese Zeile definiert den Abschnitt '"submission.new_category_label": "Neue Kategorie",'.
274. Diese Zeile definiert den Abschnitt '"submission.new_category_option": "Neue Kategorie...",'.
275. Diese Zeile definiert den Abschnitt '"submission.open_detail": "Details",'.
276. Diese Zeile definiert den Abschnitt '"submission.optional_admin_note": "Admin-Notiz (optional)",'.
277. Diese Zeile definiert den Abschnitt '"submission.prep_time": "Zubereitungszeit (Minuten, optional)",'.
278. Diese Zeile definiert den Abschnitt '"submission.preview": "Vorschau",'.
279. Diese Zeile definiert den Abschnitt '"submission.reject_button": "Rejeter",'.
280. Diese Zeile definiert den Abschnitt '"submission.reject_reason": "Ablehnungsgrund",'.
281. Diese Zeile definiert den Abschnitt '"submission.rejected": "Einreichung wurde abgelehnt.",'.
282. Diese Zeile definiert den Abschnitt '"submission.save_changes": "Aenderungen speichern",'.
283. Diese Zeile definiert den Abschnitt '"submission.servings": "Portionen (optional)",'.
284. Diese Zeile definiert den Abschnitt '"submission.set_primary_new_image": "Neues Bild als Hauptbild setzen",'.
285. Diese Zeile definiert den Abschnitt '"submission.stats_approved": "Freigegeben",'.
286. Diese Zeile definiert den Abschnitt '"submission.stats_pending": "Ausstehend",'.
287. Diese Zeile definiert den Abschnitt '"submission.stats_rejected": "Abgelehnt",'.
288. Diese Zeile definiert den Abschnitt '"submission.status_all": "Alle",'.
289. Diese Zeile definiert den Abschnitt '"submission.status_approved": "Approuvee",'.
290. Diese Zeile definiert den Abschnitt '"submission.status_filter": "Status",'.
291. Diese Zeile definiert den Abschnitt '"submission.status_pending": "En attente",'.
292. Diese Zeile definiert den Abschnitt '"submission.status_rejected": "Rejetee",'.
293. Diese Zeile definiert den Abschnitt '"submission.submit_button": "Zur Pruefung einreichen",'.
294. Diese Zeile definiert den Abschnitt '"submission.submit_hint": "Les soumissions sont verifiees par les admins avant publicat...'.
295. Diese Zeile definiert den Abschnitt '"submission.submit_title": "Soumettre une recette",'.
296. Diese Zeile definiert den Abschnitt '"submission.submitter_email": "Kontakt-E-Mail (optional)",'.
297. Diese Zeile definiert den Abschnitt '"submission.table_action": "Aktion",'.
298. Diese Zeile definiert den Abschnitt '"submission.table_date": "Datum",'.
299. Diese Zeile definiert den Abschnitt '"submission.table_status": "Status",'.
300. Diese Zeile definiert den Abschnitt '"submission.table_submitter": "Einreicher",'.
301. Diese Zeile definiert den Abschnitt '"submission.table_title": "Titel",'.
302. Diese Zeile definiert den Abschnitt '"submission.thank_you": "Merci ! Votre recette a ete soumise pour moderation.",'.
303. Diese Zeile definiert den Abschnitt '"submission.title": "Titel",'.
304. Diese Zeile definiert den Abschnitt '"submission.updated": "Einreichung wurde aktualisiert."'.
305. Diese Zeile definiert den Abschnitt '}'.

## tests/test_auth_recovery.py
```python
from pathlib import Path
from uuid import UUID

from sqlalchemy import select

from app.config import get_settings
from app.models import PasswordResetToken, User
from app.security import hash_password, normalize_username


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


def csrf_token(client, path: str = "/login") -> str:
    response = client.get(path)
    assert response.status_code == 200
    token = client.cookies.get("csrf_token")
    assert token
    return str(token)


def parse_reset_token_from_outbox(outbox_path: Path) -> str:
    content = outbox_path.read_text(encoding="utf-8")
    marker = "/auth/reset-password?token="
    index = content.rfind(marker)
    assert index >= 0
    token_start = index + len(marker)
    token = []
    for char in content[token_start:]:
        if char in "\n\r ":
            break
        token.append(char)
    result = "".join(token).strip()
    assert result
    return result


def test_login_with_email_and_username(client, db_session_factory):
    raw_password = "LoginPass123!"
    with db_session_factory() as db:
        create_user(db, email="dual-login@example.local", password=raw_password, username="Dual.Login")

    csrf = csrf_token(client, "/login")
    login_email = client.post(
        "/login",
        data={"identifier": "dual-login@example.local", "password": raw_password, "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert login_email.status_code in {302, 303}

    csrf = csrf_token(client, "/login")
    login_username = client.post(
        "/login",
        data={"identifier": "Dual.Login", "password": raw_password, "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert login_username.status_code in {302, 303}


def test_forgot_password_leaks_no_account_existence(client, db_session_factory, tmp_path):
    settings = get_settings()
    settings.mail_outbox_path = str(tmp_path / "reset_links.txt")

    with db_session_factory() as db:
        create_user(db, email="exists@example.local", password="ForgotPass123!", username="exists.user")

    csrf = csrf_token(client, "/auth/forgot-password")
    known = client.post(
        "/auth/forgot-password",
        data={"identifier": "exists@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert known.status_code == 200

    csrf = csrf_token(client, "/auth/forgot-password")
    unknown = client.post(
        "/auth/forgot-password",
        data={"identifier": "missing@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert unknown.status_code == 200
    expected_message = "Wenn der Account existiert, wurde eine E-Mail gesendet."
    assert expected_message in known.text
    assert expected_message in unknown.text


def test_reset_token_single_use(client, db_session_factory, tmp_path):
    settings = get_settings()
    outbox_file = tmp_path / "reset_links.txt"
    settings.mail_outbox_path = str(outbox_file)

    with db_session_factory() as db:
        create_user(db, email="reset-single-use@example.local", password="OldPass123!", username="reset.user")

    csrf = csrf_token(client, "/auth/forgot-password")
    forgot = client.post(
        "/auth/forgot-password",
        data={"identifier": "reset-single-use@example.local", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert forgot.status_code == 200
    token = parse_reset_token_from_outbox(outbox_file)

    csrf = csrf_token(client, f"/auth/reset-password?token={token}")
    reset_once = client.post(
        "/auth/reset-password",
        data={
            "token": token,
            "new_password": "BrandNewPass123!",
            "confirm_password": "BrandNewPass123!",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert reset_once.status_code in {302, 303}

    with db_session_factory() as db:
        db_token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash.is_not(None)))
        assert db_token is not None
        assert db_token.used_at is not None

    csrf = csrf_token(client, f"/auth/reset-password?token={token}")
    reset_twice = client.post(
        "/auth/reset-password",
        data={
            "token": token,
            "new_password": "AnotherPass123!",
            "confirm_password": "AnotherPass123!",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert reset_twice.status_code == 400


def test_change_password_requires_old_password(client, db_session_factory):
    with db_session_factory() as db:
        create_user(db, email="change-pass@example.local", password="OldPass123!", username="change.user")

    csrf = csrf_token(client, "/login")
    login = client.post(
        "/login",
        data={"identifier": "change.user", "password": "OldPass123!", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}

    csrf = csrf_token(client, "/me")
    bad_change = client.post(
        "/auth/change-password",
        data={
            "old_password": "WrongOld123!",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
    )
    assert bad_change.status_code == 400

    good_change = client.post(
        "/auth/change-password",
        data={
            "old_password": "OldPass123!",
            "new_password": "NewPass123!",
            "confirm_password": "NewPass123!",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert good_change.status_code in {302, 303}


def test_username_unique_and_pattern(client, db_session_factory):
    with db_session_factory() as db:
        create_user(db, email="first@example.local", password="UserPass123!", username="first.user")
        create_user(db, email="taken@example.local", password="UserPass123!", username="taken_name")

    csrf = csrf_token(client, "/login")
    login = client.post(
        "/login",
        data={"identifier": "first@example.local", "password": "UserPass123!", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert login.status_code in {302, 303}

    csrf = csrf_token(client, "/me")
    invalid = client.post(
        "/profile/username",
        data={"username": "ab", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert invalid.status_code == 400

    duplicate = client.post(
        "/profile/username",
        data={"username": "taken_name", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
    )
    assert duplicate.status_code == 409

    success = client.post(
        "/profile/username",
        data={"username": "valid.Name-22", "csrf_token": csrf},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert success.status_code in {302, 303}

    with db_session_factory() as db:
        user = db.scalar(select(User).where(User.email == "first@example.local"))
        assert user is not None
        assert user.username == "valid.Name-22"
        assert user.username_normalized == "valid.name-22"


def test_user_uid_is_set_for_new_user(client, db_session_factory):
    csrf = csrf_token(client, "/register")
    register = client.post(
        "/register",
        data={
            "email": "uid-check@example.local",
            "username": "uid.checker",
            "password": "UidCheck123!",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert register.status_code in {302, 303}

    with db_session_factory() as db:
        user = db.scalar(select(User).where(User.email == "uid-check@example.local"))
        assert user is not None
        assert user.user_uid
        UUID(user.user_uid)
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt 'from pathlib import Path'.
2. Diese Zeile definiert den Abschnitt 'from uuid import UUID'.
3. Diese Zeile ist leer und trennt den Inhalt lesbar.
4. Diese Zeile definiert den Abschnitt 'from sqlalchemy import select'.
5. Diese Zeile ist leer und trennt den Inhalt lesbar.
6. Diese Zeile definiert den Abschnitt 'from app.config import get_settings'.
7. Diese Zeile definiert den Abschnitt 'from app.models import PasswordResetToken, User'.
8. Diese Zeile definiert den Abschnitt 'from app.security import hash_password, normalize_username'.
9. Diese Zeile ist leer und trennt den Inhalt lesbar.
10. Diese Zeile ist leer und trennt den Inhalt lesbar.
11. Diese Zeile definiert den Abschnitt 'def create_user('.
12. Diese Zeile definiert den Abschnitt 'db,'.
13. Diese Zeile definiert den Abschnitt '*,'.
14. Diese Zeile definiert den Abschnitt 'email: str,'.
15. Diese Zeile definiert den Abschnitt 'password: str,'.
16. Diese Zeile definiert den Abschnitt 'role: str = "user",'.
17. Diese Zeile definiert den Abschnitt 'username: str | None = None,'.
18. Diese Zeile definiert den Abschnitt ') -> User:'.
19. Diese Zeile definiert den Abschnitt 'user = User('.
20. Diese Zeile definiert den Abschnitt 'email=email.strip().lower(),'.
21. Diese Zeile definiert den Abschnitt 'username=username,'.
22. Diese Zeile definiert den Abschnitt 'username_normalized=normalize_username(username) if username else None,'.
23. Diese Zeile definiert den Abschnitt 'hashed_password=hash_password(password),'.
24. Diese Zeile definiert den Abschnitt 'role=role,'.
25. Diese Zeile definiert den Abschnitt ')'.
26. Diese Zeile definiert den Abschnitt 'db.add(user)'.
27. Diese Zeile definiert den Abschnitt 'db.commit()'.
28. Diese Zeile definiert den Abschnitt 'db.refresh(user)'.
29. Diese Zeile definiert den Abschnitt 'return user'.
30. Diese Zeile ist leer und trennt den Inhalt lesbar.
31. Diese Zeile ist leer und trennt den Inhalt lesbar.
32. Diese Zeile definiert den Abschnitt 'def csrf_token(client, path: str = "/login") -> str:'.
33. Diese Zeile definiert den Abschnitt 'response = client.get(path)'.
34. Diese Zeile definiert den Abschnitt 'assert response.status_code == 200'.
35. Diese Zeile definiert den Abschnitt 'token = client.cookies.get("csrf_token")'.
36. Diese Zeile definiert den Abschnitt 'assert token'.
37. Diese Zeile definiert den Abschnitt 'return str(token)'.
38. Diese Zeile ist leer und trennt den Inhalt lesbar.
39. Diese Zeile ist leer und trennt den Inhalt lesbar.
40. Diese Zeile definiert den Abschnitt 'def parse_reset_token_from_outbox(outbox_path: Path) -> str:'.
41. Diese Zeile definiert den Abschnitt 'content = outbox_path.read_text(encoding="utf-8")'.
42. Diese Zeile definiert den Abschnitt 'marker = "/auth/reset-password?token="'.
43. Diese Zeile definiert den Abschnitt 'index = content.rfind(marker)'.
44. Diese Zeile definiert den Abschnitt 'assert index >= 0'.
45. Diese Zeile definiert den Abschnitt 'token_start = index + len(marker)'.
46. Diese Zeile definiert den Abschnitt 'token = []'.
47. Diese Zeile definiert den Abschnitt 'for char in content[token_start:]:'.
48. Diese Zeile definiert den Abschnitt 'if char in "\n\r ":'.
49. Diese Zeile definiert den Abschnitt 'break'.
50. Diese Zeile definiert den Abschnitt 'token.append(char)'.
51. Diese Zeile definiert den Abschnitt 'result = "".join(token).strip()'.
52. Diese Zeile definiert den Abschnitt 'assert result'.
53. Diese Zeile definiert den Abschnitt 'return result'.
54. Diese Zeile ist leer und trennt den Inhalt lesbar.
55. Diese Zeile ist leer und trennt den Inhalt lesbar.
56. Diese Zeile definiert den Abschnitt 'def test_login_with_email_and_username(client, db_session_factory):'.
57. Diese Zeile definiert den Abschnitt 'raw_password = "LoginPass123!"'.
58. Diese Zeile definiert den Abschnitt 'with db_session_factory() as db:'.
59. Diese Zeile definiert den Abschnitt 'create_user(db, email="dual-login@example.local", password=raw_password, username="Dual...'.
60. Diese Zeile ist leer und trennt den Inhalt lesbar.
61. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, "/login")'.
62. Diese Zeile definiert den Abschnitt 'login_email = client.post('.
63. Diese Zeile definiert den Abschnitt '"/login",'.
64. Diese Zeile definiert den Abschnitt 'data={"identifier": "dual-login@example.local", "password": raw_password, "csrf_token":...'.
65. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
66. Diese Zeile definiert den Abschnitt 'follow_redirects=False,'.
67. Diese Zeile definiert den Abschnitt ')'.
68. Diese Zeile definiert den Abschnitt 'assert login_email.status_code in {302, 303}'.
69. Diese Zeile ist leer und trennt den Inhalt lesbar.
70. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, "/login")'.
71. Diese Zeile definiert den Abschnitt 'login_username = client.post('.
72. Diese Zeile definiert den Abschnitt '"/login",'.
73. Diese Zeile definiert den Abschnitt 'data={"identifier": "Dual.Login", "password": raw_password, "csrf_token": csrf},'.
74. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
75. Diese Zeile definiert den Abschnitt 'follow_redirects=False,'.
76. Diese Zeile definiert den Abschnitt ')'.
77. Diese Zeile definiert den Abschnitt 'assert login_username.status_code in {302, 303}'.
78. Diese Zeile ist leer und trennt den Inhalt lesbar.
79. Diese Zeile ist leer und trennt den Inhalt lesbar.
80. Diese Zeile definiert den Abschnitt 'def test_forgot_password_leaks_no_account_existence(client, db_session_factory, tmp_path):'.
81. Diese Zeile definiert den Abschnitt 'settings = get_settings()'.
82. Diese Zeile definiert den Abschnitt 'settings.mail_outbox_path = str(tmp_path / "reset_links.txt")'.
83. Diese Zeile ist leer und trennt den Inhalt lesbar.
84. Diese Zeile definiert den Abschnitt 'with db_session_factory() as db:'.
85. Diese Zeile definiert den Abschnitt 'create_user(db, email="exists@example.local", password="ForgotPass123!", username="exis...'.
86. Diese Zeile ist leer und trennt den Inhalt lesbar.
87. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, "/auth/forgot-password")'.
88. Diese Zeile definiert den Abschnitt 'known = client.post('.
89. Diese Zeile definiert den Abschnitt '"/auth/forgot-password",'.
90. Diese Zeile definiert den Abschnitt 'data={"identifier": "exists@example.local", "csrf_token": csrf},'.
91. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
92. Diese Zeile definiert den Abschnitt ')'.
93. Diese Zeile definiert den Abschnitt 'assert known.status_code == 200'.
94. Diese Zeile ist leer und trennt den Inhalt lesbar.
95. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, "/auth/forgot-password")'.
96. Diese Zeile definiert den Abschnitt 'unknown = client.post('.
97. Diese Zeile definiert den Abschnitt '"/auth/forgot-password",'.
98. Diese Zeile definiert den Abschnitt 'data={"identifier": "missing@example.local", "csrf_token": csrf},'.
99. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
100. Diese Zeile definiert den Abschnitt ')'.
101. Diese Zeile definiert den Abschnitt 'assert unknown.status_code == 200'.
102. Diese Zeile definiert den Abschnitt 'expected_message = "Wenn der Account existiert, wurde eine E-Mail gesendet."'.
103. Diese Zeile definiert den Abschnitt 'assert expected_message in known.text'.
104. Diese Zeile definiert den Abschnitt 'assert expected_message in unknown.text'.
105. Diese Zeile ist leer und trennt den Inhalt lesbar.
106. Diese Zeile ist leer und trennt den Inhalt lesbar.
107. Diese Zeile definiert den Abschnitt 'def test_reset_token_single_use(client, db_session_factory, tmp_path):'.
108. Diese Zeile definiert den Abschnitt 'settings = get_settings()'.
109. Diese Zeile definiert den Abschnitt 'outbox_file = tmp_path / "reset_links.txt"'.
110. Diese Zeile definiert den Abschnitt 'settings.mail_outbox_path = str(outbox_file)'.
111. Diese Zeile ist leer und trennt den Inhalt lesbar.
112. Diese Zeile definiert den Abschnitt 'with db_session_factory() as db:'.
113. Diese Zeile definiert den Abschnitt 'create_user(db, email="reset-single-use@example.local", password="OldPass123!", usernam...'.
114. Diese Zeile ist leer und trennt den Inhalt lesbar.
115. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, "/auth/forgot-password")'.
116. Diese Zeile definiert den Abschnitt 'forgot = client.post('.
117. Diese Zeile definiert den Abschnitt '"/auth/forgot-password",'.
118. Diese Zeile definiert den Abschnitt 'data={"identifier": "reset-single-use@example.local", "csrf_token": csrf},'.
119. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
120. Diese Zeile definiert den Abschnitt ')'.
121. Diese Zeile definiert den Abschnitt 'assert forgot.status_code == 200'.
122. Diese Zeile definiert den Abschnitt 'token = parse_reset_token_from_outbox(outbox_file)'.
123. Diese Zeile ist leer und trennt den Inhalt lesbar.
124. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, f"/auth/reset-password?token={token}")'.
125. Diese Zeile definiert den Abschnitt 'reset_once = client.post('.
126. Diese Zeile definiert den Abschnitt '"/auth/reset-password",'.
127. Diese Zeile definiert den Abschnitt 'data={'.
128. Diese Zeile definiert den Abschnitt '"token": token,'.
129. Diese Zeile definiert den Abschnitt '"new_password": "BrandNewPass123!",'.
130. Diese Zeile definiert den Abschnitt '"confirm_password": "BrandNewPass123!",'.
131. Diese Zeile definiert den Abschnitt '"csrf_token": csrf,'.
132. Diese Zeile definiert den Abschnitt '},'.
133. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
134. Diese Zeile definiert den Abschnitt 'follow_redirects=False,'.
135. Diese Zeile definiert den Abschnitt ')'.
136. Diese Zeile definiert den Abschnitt 'assert reset_once.status_code in {302, 303}'.
137. Diese Zeile ist leer und trennt den Inhalt lesbar.
138. Diese Zeile definiert den Abschnitt 'with db_session_factory() as db:'.
139. Diese Zeile definiert den Abschnitt 'db_token = db.scalar(select(PasswordResetToken).where(PasswordResetToken.token_hash.is_...'.
140. Diese Zeile definiert den Abschnitt 'assert db_token is not None'.
141. Diese Zeile definiert den Abschnitt 'assert db_token.used_at is not None'.
142. Diese Zeile ist leer und trennt den Inhalt lesbar.
143. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, f"/auth/reset-password?token={token}")'.
144. Diese Zeile definiert den Abschnitt 'reset_twice = client.post('.
145. Diese Zeile definiert den Abschnitt '"/auth/reset-password",'.
146. Diese Zeile definiert den Abschnitt 'data={'.
147. Diese Zeile definiert den Abschnitt '"token": token,'.
148. Diese Zeile definiert den Abschnitt '"new_password": "AnotherPass123!",'.
149. Diese Zeile definiert den Abschnitt '"confirm_password": "AnotherPass123!",'.
150. Diese Zeile definiert den Abschnitt '"csrf_token": csrf,'.
151. Diese Zeile definiert den Abschnitt '},'.
152. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
153. Diese Zeile definiert den Abschnitt ')'.
154. Diese Zeile definiert den Abschnitt 'assert reset_twice.status_code == 400'.
155. Diese Zeile ist leer und trennt den Inhalt lesbar.
156. Diese Zeile ist leer und trennt den Inhalt lesbar.
157. Diese Zeile definiert den Abschnitt 'def test_change_password_requires_old_password(client, db_session_factory):'.
158. Diese Zeile definiert den Abschnitt 'with db_session_factory() as db:'.
159. Diese Zeile definiert den Abschnitt 'create_user(db, email="change-pass@example.local", password="OldPass123!", username="ch...'.
160. Diese Zeile ist leer und trennt den Inhalt lesbar.
161. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, "/login")'.
162. Diese Zeile definiert den Abschnitt 'login = client.post('.
163. Diese Zeile definiert den Abschnitt '"/login",'.
164. Diese Zeile definiert den Abschnitt 'data={"identifier": "change.user", "password": "OldPass123!", "csrf_token": csrf},'.
165. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
166. Diese Zeile definiert den Abschnitt 'follow_redirects=False,'.
167. Diese Zeile definiert den Abschnitt ')'.
168. Diese Zeile definiert den Abschnitt 'assert login.status_code in {302, 303}'.
169. Diese Zeile ist leer und trennt den Inhalt lesbar.
170. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, "/me")'.
171. Diese Zeile definiert den Abschnitt 'bad_change = client.post('.
172. Diese Zeile definiert den Abschnitt '"/auth/change-password",'.
173. Diese Zeile definiert den Abschnitt 'data={'.
174. Diese Zeile definiert den Abschnitt '"old_password": "WrongOld123!",'.
175. Diese Zeile definiert den Abschnitt '"new_password": "NewPass123!",'.
176. Diese Zeile definiert den Abschnitt '"confirm_password": "NewPass123!",'.
177. Diese Zeile definiert den Abschnitt '"csrf_token": csrf,'.
178. Diese Zeile definiert den Abschnitt '},'.
179. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
180. Diese Zeile definiert den Abschnitt ')'.
181. Diese Zeile definiert den Abschnitt 'assert bad_change.status_code == 400'.
182. Diese Zeile ist leer und trennt den Inhalt lesbar.
183. Diese Zeile definiert den Abschnitt 'good_change = client.post('.
184. Diese Zeile definiert den Abschnitt '"/auth/change-password",'.
185. Diese Zeile definiert den Abschnitt 'data={'.
186. Diese Zeile definiert den Abschnitt '"old_password": "OldPass123!",'.
187. Diese Zeile definiert den Abschnitt '"new_password": "NewPass123!",'.
188. Diese Zeile definiert den Abschnitt '"confirm_password": "NewPass123!",'.
189. Diese Zeile definiert den Abschnitt '"csrf_token": csrf,'.
190. Diese Zeile definiert den Abschnitt '},'.
191. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
192. Diese Zeile definiert den Abschnitt 'follow_redirects=False,'.
193. Diese Zeile definiert den Abschnitt ')'.
194. Diese Zeile definiert den Abschnitt 'assert good_change.status_code in {302, 303}'.
195. Diese Zeile ist leer und trennt den Inhalt lesbar.
196. Diese Zeile ist leer und trennt den Inhalt lesbar.
197. Diese Zeile definiert den Abschnitt 'def test_username_unique_and_pattern(client, db_session_factory):'.
198. Diese Zeile definiert den Abschnitt 'with db_session_factory() as db:'.
199. Diese Zeile definiert den Abschnitt 'create_user(db, email="first@example.local", password="UserPass123!", username="first.u...'.
200. Diese Zeile definiert den Abschnitt 'create_user(db, email="taken@example.local", password="UserPass123!", username="taken_n...'.
201. Diese Zeile ist leer und trennt den Inhalt lesbar.
202. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, "/login")'.
203. Diese Zeile definiert den Abschnitt 'login = client.post('.
204. Diese Zeile definiert den Abschnitt '"/login",'.
205. Diese Zeile definiert den Abschnitt 'data={"identifier": "first@example.local", "password": "UserPass123!", "csrf_token": cs...'.
206. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
207. Diese Zeile definiert den Abschnitt 'follow_redirects=False,'.
208. Diese Zeile definiert den Abschnitt ')'.
209. Diese Zeile definiert den Abschnitt 'assert login.status_code in {302, 303}'.
210. Diese Zeile ist leer und trennt den Inhalt lesbar.
211. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, "/me")'.
212. Diese Zeile definiert den Abschnitt 'invalid = client.post('.
213. Diese Zeile definiert den Abschnitt '"/profile/username",'.
214. Diese Zeile definiert den Abschnitt 'data={"username": "ab", "csrf_token": csrf},'.
215. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
216. Diese Zeile definiert den Abschnitt ')'.
217. Diese Zeile definiert den Abschnitt 'assert invalid.status_code == 400'.
218. Diese Zeile ist leer und trennt den Inhalt lesbar.
219. Diese Zeile definiert den Abschnitt 'duplicate = client.post('.
220. Diese Zeile definiert den Abschnitt '"/profile/username",'.
221. Diese Zeile definiert den Abschnitt 'data={"username": "taken_name", "csrf_token": csrf},'.
222. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
223. Diese Zeile definiert den Abschnitt ')'.
224. Diese Zeile definiert den Abschnitt 'assert duplicate.status_code == 409'.
225. Diese Zeile ist leer und trennt den Inhalt lesbar.
226. Diese Zeile definiert den Abschnitt 'success = client.post('.
227. Diese Zeile definiert den Abschnitt '"/profile/username",'.
228. Diese Zeile definiert den Abschnitt 'data={"username": "valid.Name-22", "csrf_token": csrf},'.
229. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
230. Diese Zeile definiert den Abschnitt 'follow_redirects=False,'.
231. Diese Zeile definiert den Abschnitt ')'.
232. Diese Zeile definiert den Abschnitt 'assert success.status_code in {302, 303}'.
233. Diese Zeile ist leer und trennt den Inhalt lesbar.
234. Diese Zeile definiert den Abschnitt 'with db_session_factory() as db:'.
235. Diese Zeile definiert den Abschnitt 'user = db.scalar(select(User).where(User.email == "first@example.local"))'.
236. Diese Zeile definiert den Abschnitt 'assert user is not None'.
237. Diese Zeile definiert den Abschnitt 'assert user.username == "valid.Name-22"'.
238. Diese Zeile definiert den Abschnitt 'assert user.username_normalized == "valid.name-22"'.
239. Diese Zeile ist leer und trennt den Inhalt lesbar.
240. Diese Zeile ist leer und trennt den Inhalt lesbar.
241. Diese Zeile definiert den Abschnitt 'def test_user_uid_is_set_for_new_user(client, db_session_factory):'.
242. Diese Zeile definiert den Abschnitt 'csrf = csrf_token(client, "/register")'.
243. Diese Zeile definiert den Abschnitt 'register = client.post('.
244. Diese Zeile definiert den Abschnitt '"/register",'.
245. Diese Zeile definiert den Abschnitt 'data={'.
246. Diese Zeile definiert den Abschnitt '"email": "uid-check@example.local",'.
247. Diese Zeile definiert den Abschnitt '"username": "uid.checker",'.
248. Diese Zeile definiert den Abschnitt '"password": "UidCheck123!",'.
249. Diese Zeile definiert den Abschnitt '"csrf_token": csrf,'.
250. Diese Zeile definiert den Abschnitt '},'.
251. Diese Zeile definiert den Abschnitt 'headers={"X-CSRF-Token": csrf},'.
252. Diese Zeile definiert den Abschnitt 'follow_redirects=False,'.
253. Diese Zeile definiert den Abschnitt ')'.
254. Diese Zeile definiert den Abschnitt 'assert register.status_code in {302, 303}'.
255. Diese Zeile ist leer und trennt den Inhalt lesbar.
256. Diese Zeile definiert den Abschnitt 'with db_session_factory() as db:'.
257. Diese Zeile definiert den Abschnitt 'user = db.scalar(select(User).where(User.email == "uid-check@example.local"))'.
258. Diese Zeile definiert den Abschnitt 'assert user is not None'.
259. Diese Zeile definiert den Abschnitt 'assert user.user_uid'.
260. Diese Zeile definiert den Abschnitt 'UUID(user.user_uid)'.

## README_AUTH_RECOVERY.md
```markdown
# MealMate Auth & Account Recovery

## Features

- Login per E-Mail oder Benutzername.
- Jeder User besitzt `user_uid` (UUID, nicht erratbar).
- Username setzen/aendern mit Validierung und Eindeutigkeit.
- Passwort aendern im Profil.
- Passwort vergessen + Reset-Link mit Single-Use-Token.
- Schlanke Security-Events fuer Login/Reset/Username/Password.

## Datenmodell

- `users`:
  - `user_uid`, `username`, `username_normalized`
  - `last_login_at`, `last_login_ip`, `last_login_user_agent`
- `password_reset_tokens`:
  - nur `token_hash` gespeichert (nie Raw-Token)
  - `expires_at` (30 Minuten), `used_at` fuer Single-Use
- `security_events`:
  - minimale Audit-Daten, automatisch begrenzt

## Login

- Feld: `E-Mail oder Benutzername`
- Lookup:
  - mit `@` => `email`
  - sonst => `username_normalized`
- Fehler immer generisch.

## Passwort-Reset

1. `GET/POST /auth/forgot-password`
2. Antwort immer gleich (kein Account-Leak)
3. Bei vorhandenem User:
   - Token erzeugen
   - nur Hash speichern
   - Link `{APP_URL}/auth/reset-password?token=<raw>`
4. `GET/POST /auth/reset-password`
5. Token wird nach Nutzung auf `used_at` gesetzt

## Mail-Versand

- DEV: Outbox-Datei (`MAIL_OUTBOX_PATH`)
- PROD: SMTP (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`)
- In PROD wird der Raw-Token nicht geloggt.

## Rate Limits

- `POST /auth/login`: `5/min` pro IP
- `POST /auth/forgot-password`: `5/min` pro IP
- `POST /auth/reset-password`: `5/min` pro IP
- `POST /auth/change-password`: `3/min` pro User
- `POST /profile/username`: `5/min` pro User

## Tests

`tests/test_auth_recovery.py` deckt ab:

- Login mit E-Mail und Username
- Forgot-Password ohne Existence-Leak
- Reset-Token Single-Use
- Passwortwechsel mit Pflicht auf altes Passwort
- Username Pattern + Unique
- `user_uid` fuer neue Nutzer
```
ZEILEN-ERKL?RUNG
1. Diese Zeile definiert den Abschnitt '# MealMate Auth & Account Recovery'.
2. Diese Zeile ist leer und trennt den Inhalt lesbar.
3. Diese Zeile definiert den Abschnitt '## Features'.
4. Diese Zeile ist leer und trennt den Inhalt lesbar.
5. Diese Zeile definiert den Abschnitt '- Login per E-Mail oder Benutzername.'.
6. Diese Zeile definiert den Abschnitt '- Jeder User besitzt 'user_uid' (UUID, nicht erratbar).'.
7. Diese Zeile definiert den Abschnitt '- Username setzen/aendern mit Validierung und Eindeutigkeit.'.
8. Diese Zeile definiert den Abschnitt '- Passwort aendern im Profil.'.
9. Diese Zeile definiert den Abschnitt '- Passwort vergessen + Reset-Link mit Single-Use-Token.'.
10. Diese Zeile definiert den Abschnitt '- Schlanke Security-Events fuer Login/Reset/Username/Password.'.
11. Diese Zeile ist leer und trennt den Inhalt lesbar.
12. Diese Zeile definiert den Abschnitt '## Datenmodell'.
13. Diese Zeile ist leer und trennt den Inhalt lesbar.
14. Diese Zeile definiert den Abschnitt '- 'users':'.
15. Diese Zeile definiert den Abschnitt '- 'user_uid', 'username', 'username_normalized''.
16. Diese Zeile definiert den Abschnitt '- 'last_login_at', 'last_login_ip', 'last_login_user_agent''.
17. Diese Zeile definiert den Abschnitt '- 'password_reset_tokens':'.
18. Diese Zeile definiert den Abschnitt '- nur 'token_hash' gespeichert (nie Raw-Token)'.
19. Diese Zeile definiert den Abschnitt '- 'expires_at' (30 Minuten), 'used_at' fuer Single-Use'.
20. Diese Zeile definiert den Abschnitt '- 'security_events':'.
21. Diese Zeile definiert den Abschnitt '- minimale Audit-Daten, automatisch begrenzt'.
22. Diese Zeile ist leer und trennt den Inhalt lesbar.
23. Diese Zeile definiert den Abschnitt '## Login'.
24. Diese Zeile ist leer und trennt den Inhalt lesbar.
25. Diese Zeile definiert den Abschnitt '- Feld: 'E-Mail oder Benutzername''.
26. Diese Zeile definiert den Abschnitt '- Lookup:'.
27. Diese Zeile definiert den Abschnitt '- mit '@' => 'email''.
28. Diese Zeile definiert den Abschnitt '- sonst => 'username_normalized''.
29. Diese Zeile definiert den Abschnitt '- Fehler immer generisch.'.
30. Diese Zeile ist leer und trennt den Inhalt lesbar.
31. Diese Zeile definiert den Abschnitt '## Passwort-Reset'.
32. Diese Zeile ist leer und trennt den Inhalt lesbar.
33. Diese Zeile definiert den Abschnitt '1. 'GET/POST /auth/forgot-password''.
34. Diese Zeile definiert den Abschnitt '2. Antwort immer gleich (kein Account-Leak)'.
35. Diese Zeile definiert den Abschnitt '3. Bei vorhandenem User:'.
36. Diese Zeile definiert den Abschnitt '- Token erzeugen'.
37. Diese Zeile definiert den Abschnitt '- nur Hash speichern'.
38. Diese Zeile definiert den Abschnitt '- Link '{APP_URL}/auth/reset-password?token=<raw>''.
39. Diese Zeile definiert den Abschnitt '4. 'GET/POST /auth/reset-password''.
40. Diese Zeile definiert den Abschnitt '5. Token wird nach Nutzung auf 'used_at' gesetzt'.
41. Diese Zeile ist leer und trennt den Inhalt lesbar.
42. Diese Zeile definiert den Abschnitt '## Mail-Versand'.
43. Diese Zeile ist leer und trennt den Inhalt lesbar.
44. Diese Zeile definiert den Abschnitt '- DEV: Outbox-Datei ('MAIL_OUTBOX_PATH')'.
45. Diese Zeile definiert den Abschnitt '- PROD: SMTP ('SMTP_HOST', 'SMTP_PORT', 'SMTP_USER', 'SMTP_PASSWORD', 'SMTP_FROM')'.
46. Diese Zeile definiert den Abschnitt '- In PROD wird der Raw-Token nicht geloggt.'.
47. Diese Zeile ist leer und trennt den Inhalt lesbar.
48. Diese Zeile definiert den Abschnitt '## Rate Limits'.
49. Diese Zeile ist leer und trennt den Inhalt lesbar.
50. Diese Zeile definiert den Abschnitt '- 'POST /auth/login': '5/min' pro IP'.
51. Diese Zeile definiert den Abschnitt '- 'POST /auth/forgot-password': '5/min' pro IP'.
52. Diese Zeile definiert den Abschnitt '- 'POST /auth/reset-password': '5/min' pro IP'.
53. Diese Zeile definiert den Abschnitt '- 'POST /auth/change-password': '3/min' pro User'.
54. Diese Zeile definiert den Abschnitt '- 'POST /profile/username': '5/min' pro User'.
55. Diese Zeile ist leer und trennt den Inhalt lesbar.
56. Diese Zeile definiert den Abschnitt '## Tests'.
57. Diese Zeile ist leer und trennt den Inhalt lesbar.
58. Diese Zeile definiert den Abschnitt ''tests/test_auth_recovery.py' deckt ab:'.
59. Diese Zeile ist leer und trennt den Inhalt lesbar.
60. Diese Zeile definiert den Abschnitt '- Login mit E-Mail und Username'.
61. Diese Zeile definiert den Abschnitt '- Forgot-Password ohne Existence-Leak'.
62. Diese Zeile definiert den Abschnitt '- Reset-Token Single-Use'.
63. Diese Zeile definiert den Abschnitt '- Passwortwechsel mit Pflicht auf altes Passwort'.
64. Diese Zeile definiert den Abschnitt '- Username Pattern + Unique'.
65. Diese Zeile definiert den Abschnitt '- 'user_uid' fuer neue Nutzer'.

from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    app_name: str = "Kitchen Hell and Heaven"
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
    translateapi_enabled: bool = False
    translate_auto_on_publish: bool = False
    translate_lazy_on_view: bool = True
    i18n_strict: bool = False
    translation_provider: Literal["translateapi", "google_translators"] = "translateapi"
    translate_source_lang: str = "auto"
    translate_target_langs: Annotated[list[str], NoDecode] = ["de", "en", "fr"]
    translate_max_recipes_per_run: int = 20
    translateapi_base_url: str = "https://api.translateapi.ai/api/v1"
    translateapi_api_key: str | None = None
    translateapi_poll_interval_seconds: int = 3
    translateapi_max_polls: int = 200
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

    @field_validator("app_name", mode="before")
    @classmethod
    def parse_app_name(cls, value: str | None) -> str:
        candidate = str(value or "").strip()
        if not candidate or candidate in {"MealMate", "Hell's Kitchen and Heaven"}:
            return "Kitchen Hell and Heaven"
        return candidate

    @field_validator("allowed_hosts", mode="before")
    @classmethod
    def parse_allowed_hosts(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            hosts = [item.strip() for item in value if item.strip()]
        else:
            hosts = [item.strip() for item in value.split(",") if item.strip()]
        return hosts or ["*"]

    @field_validator("translate_target_langs", mode="before")
    @classmethod
    def parse_translate_target_langs(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            raw_items = [str(item).strip().lower() for item in value if str(item).strip()]
        else:
            raw_items = [item.strip().lower() for item in str(value).split(",") if item.strip()]
        normalized: list[str] = []
        for item in raw_items:
            lang = item.split("-", 1)[0]
            if len(lang) < 2:
                continue
            if lang not in normalized:
                normalized.append(lang)
        return normalized or ["de", "en", "fr"]

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

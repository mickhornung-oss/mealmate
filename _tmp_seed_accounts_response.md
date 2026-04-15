Ge?nderte Dateien:
- app/dev_seed_accounts.py
- tools/seed_accounts.py
- app/config.py
- .env.example
- tests/test_seed_accounts.py

### app/dev_seed_accounts.py
```python
from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User
from app.security import hash_password, normalize_username


@dataclass(frozen=True)
class AccountSeedSpec:
    email: str
    username: str
    role: str
    password: str


@dataclass(frozen=True)
class AccountSeedRow:
    email: str
    username: str
    role: str
    password: str
    status: str


@dataclass
class AccountSeedReport:
    created: int = 0
    updated: int = 0
    unchanged: int = 0
    rows: list[AccountSeedRow] | None = None

    def __post_init__(self) -> None:
        if self.rows is None:
            self.rows = []


DEFAULT_ACCOUNT_SPECS: tuple[AccountSeedSpec, ...] = (
    AccountSeedSpec("admin1@mealmate.local", "admin1", "admin", "AdminPass123!"),
    AccountSeedSpec("admin2@mealmate.local", "admin2", "admin", "AdminPass123!"),
    AccountSeedSpec("admin3@mealmate.local", "admin3", "admin", "AdminPass123!"),
    AccountSeedSpec("user1@mealmate.local", "user1", "user", "UserPass123!"),
    AccountSeedSpec("user2@mealmate.local", "user2", "user", "UserPass123!"),
    AccountSeedSpec("user3@mealmate.local", "user3", "user", "UserPass123!"),
)


def dev_seed_allowed(app_env: str, allow_dev_seed: bool) -> bool:
    return app_env == "dev" or bool(allow_dev_seed)


def ensure_dev_seed_allowed(app_env: str, allow_dev_seed: bool) -> None:
    if dev_seed_allowed(app_env, allow_dev_seed):
        return
    raise RuntimeError(
        "Testaccount-Seed ist nur in APP_ENV=dev oder mit ALLOW_DEV_SEED=1 erlaubt."
    )


def _collect_taken_username_norms(db: Session) -> set[str]:
    rows = db.scalars(select(User.username_normalized).where(User.username_normalized.is_not(None))).all()
    return {value for value in rows if value}


def _find_available_username(preferred_normalized: str, taken: set[str]) -> tuple[str, bool]:
    if preferred_normalized not in taken:
        return preferred_normalized, False
    base = preferred_normalized[:24]
    index = 2
    while True:
        candidate = f"{base}{index}"
        candidate = candidate[:30]
        if candidate not in taken:
            return candidate, True
        index += 1


def seed_test_accounts(
    db: Session,
    specs: tuple[AccountSeedSpec, ...] = DEFAULT_ACCOUNT_SPECS,
) -> AccountSeedReport:
    report = AccountSeedReport()
    taken_usernames = _collect_taken_username_norms(db)
    users_by_email = {
        user.email.lower(): user
        for user in db.scalars(select(User).where(User.email.in_([item.email for item in specs]))).all()
    }

    for spec in specs:
        email_normalized = spec.email.strip().lower()
        desired_username_norm = normalize_username(spec.username)
        existing_user = users_by_email.get(email_normalized)
        if existing_user:
            if existing_user.username_normalized:
                taken_usernames.add(existing_user.username_normalized)
            report.unchanged += 1
            report.rows.append(
                AccountSeedRow(
                    email=existing_user.email,
                    username=existing_user.username or spec.username,
                    role=existing_user.role,
                    password=spec.password,
                    status="skipped-existing-email",
                )
            )
            continue

        username_norm, adjusted = _find_available_username(desired_username_norm, taken_usernames)
        username_text = username_norm
        user = User(
            email=email_normalized,
            username=username_text,
            username_normalized=username_norm,
            hashed_password=hash_password(spec.password),
            role=spec.role,
        )
        db.add(user)
        users_by_email[email_normalized] = user
        taken_usernames.add(username_norm)
        report.created += 1
        status = "created-adjusted-username" if adjusted else "created"
        report.rows.append(
            AccountSeedRow(
                email=email_normalized,
                username=username_text,
                role=spec.role,
                password=spec.password,
                status=status,
            )
        )
    return report
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
2. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
3. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
4. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
5. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
6. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
7. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
8. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
9. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
10. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
11. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
12. Diese Zeile markiert die folgende Klasse als Dataclass.
13. Diese Zeile definiert eine Klasse f?r Daten oder Logik des Seeds.
14. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
15. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
16. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
17. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
18. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
19. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
20. Diese Zeile markiert die folgende Klasse als Dataclass.
21. Diese Zeile definiert eine Klasse f?r Daten oder Logik des Seeds.
22. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
23. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
24. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
25. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
26. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
27. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
28. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
29. Diese Zeile markiert die folgende Klasse als Dataclass.
30. Diese Zeile definiert eine Klasse f?r Daten oder Logik des Seeds.
31. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
32. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
33. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
34. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
35. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
36. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
37. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
38. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
39. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
40. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
41. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
42. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
43. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
44. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
45. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
46. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
47. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
48. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
49. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
50. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
51. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
52. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
53. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
54. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
55. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
56. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
57. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
58. Diese Zeile l?st bewusst eine Exception aus.
59. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
60. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
61. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
62. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
63. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
64. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
65. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
66. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
67. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
68. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
69. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
70. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
71. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
72. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
73. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
74. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
75. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
76. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
77. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
78. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
79. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
80. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
81. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
82. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
83. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
84. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
85. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
86. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
87. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
88. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
89. Diese Zeile startet eine Schleife ?ber mehrere Eintr?ge.
90. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
91. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
92. Diese Zeile startet eine Schleife ?ber mehrere Eintr?ge.
93. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
94. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
95. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
96. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
97. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
98. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
99. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
100. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
101. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
102. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
103. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
104. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
105. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
106. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
107. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
108. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
109. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
110. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
111. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
112. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
113. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
114. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
115. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
116. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
117. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
118. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
119. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
120. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
121. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
122. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
123. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
124. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
125. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
126. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
127. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
128. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
129. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
130. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
131. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
132. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
133. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
134. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.

### tools/seed_accounts.py
```python
from __future__ import annotations

import argparse
from typing import Iterable

from app.config import get_settings
from app.database import SessionLocal
from app.dev_seed_accounts import ensure_dev_seed_allowed, seed_test_accounts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Erzeugt idempotent 3 Admins und 3 User fuer lokale Tests."
    )
    return parser


def _render_table(rows: Iterable[list[str]]) -> str:
    rows_list = list(rows)
    widths = [max(len(row[index]) for row in rows_list) for index in range(len(rows_list[0]))]
    lines: list[str] = []
    for row_index, row in enumerate(rows_list):
        line = " | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row))
        lines.append(line)
        if row_index == 0:
            lines.append("-+-".join("-" * width for width in widths))
    return "\n".join(lines)


def main() -> int:
    _ = build_parser().parse_args()
    settings = get_settings()
    try:
        ensure_dev_seed_allowed(settings.app_env, settings.allow_dev_seed)
    except RuntimeError as exc:
        print(f"ABBRUCH: {exc}")
        return 1

    with SessionLocal() as db:
        report = seed_test_accounts(db)
        db.commit()

    print("Seed abgeschlossen.")
    print(f"Erstellt: {report.created}")
    print(f"Aktualisiert: {report.updated}")
    print(f"Unveraendert: {report.unchanged}")
    print("")
    header = ["Email", "Username", "Role", "Passwort", "Status"]
    table_rows = [header]
    for row in report.rows or []:
        table_rows.append([row.email, row.username, row.role, row.password, row.status])
    print(_render_table(table_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
2. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
3. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
4. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
5. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
6. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
7. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
8. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
9. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
10. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
11. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
12. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
13. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
14. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
15. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
16. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
17. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
18. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
19. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
20. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
21. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
22. Diese Zeile startet eine Schleife ?ber mehrere Eintr?ge.
23. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
24. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
25. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
26. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
27. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
28. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
29. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
30. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
31. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
32. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
33. Diese Zeile startet einen Fehlerbehandlungsblock.
34. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
35. Diese Zeile f?ngt einen erwarteten Fehlerfall ab.
36. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
37. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
38. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
39. Diese Zeile ?ffnet einen Kontextblock f?r sichere Ressourcenverwaltung.
40. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
41. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
42. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
43. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
44. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
45. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
46. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
47. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
48. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
49. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
50. Diese Zeile startet eine Schleife ?ber mehrere Eintr?ge.
51. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
52. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
53. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
54. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
55. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
56. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
57. Diese Zeile l?st bewusst eine Exception aus.

### app/config.py
```python
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore", case_sensitive=False)

    app_name: str = "Hell's Kitchen and Heaven"
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
    translate_source_lang: str = "de"
    translate_target_langs: Annotated[list[str], NoDecode] = ["en", "fr"]
    translate_max_recipes_per_run: int = 20
    translateapi_base_url: str = "https://api.translateapi.ai/api/v1"
    translateapi_api_key: str | None = None
    translateapi_poll_interval_seconds: int = 3
    translateapi_max_polls: int = 200
    security_event_retention_days: int = 30
    security_event_max_rows: int = 5000
    enable_kochwiki_seed: bool = False
    auto_seed_kochwiki: bool = False
    allow_dev_seed: bool = False
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
        return normalized or ["en", "fr"]

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
1. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
2. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
3. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
4. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
5. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
6. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
7. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
8. Diese Zeile definiert eine Klasse f?r Daten oder Logik des Seeds.
9. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
10. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
11. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
12. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
13. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
14. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
15. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
16. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
17. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
18. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
19. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
20. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
21. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
22. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
23. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
24. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
25. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
26. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
27. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
28. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
29. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
30. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
31. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
32. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
33. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
34. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
35. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
36. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
37. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
38. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
39. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
40. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
41. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
42. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
43. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
44. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
45. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
46. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
47. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
48. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
49. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
50. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
51. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
52. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
53. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
54. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
55. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
56. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
57. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
58. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
59. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
60. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
61. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
62. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
63. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
64. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
65. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
66. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
67. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
68. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
69. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
70. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
71. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
72. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
73. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
74. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
75. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
76. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
77. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
78. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
79. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
80. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
81. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
82. Diese Zeile startet eine Schleife ?ber mehrere Eintr?ge.
83. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
84. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
85. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
86. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
87. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
88. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
89. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
90. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
91. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
92. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
93. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
94. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
95. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
96. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
97. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
98. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
99. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
100. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
101. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
102. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
103. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
104. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
105. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
106. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
107. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
108. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
109. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
110. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
111. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
112. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
113. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
114. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
115. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
116. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
117. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
118. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
119. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
120. Diese Zeile pr?ft eine Bedingung f?r den weiteren Ablauf.
121. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
122. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.
123. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
124. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
125. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
126. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
127. Diese Zeile gibt den berechneten Wert an den Aufrufer zur?ck.

### .env.example
```env
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
TRANSLATEAPI_ENABLED=0
TRANSLATE_AUTO_ON_PUBLISH=0
TRANSLATE_LAZY_ON_VIEW=1
I18N_STRICT=0
TRANSLATION_PROVIDER=translateapi
TRANSLATE_SOURCE_LANG=de
TRANSLATE_TARGET_LANGS=en,fr
TRANSLATE_MAX_RECIPES_PER_RUN=20
TRANSLATEAPI_BASE_URL=https://api.translateapi.ai/api/v1
TRANSLATEAPI_API_KEY=
TRANSLATEAPI_POLL_INTERVAL_SECONDS=3
TRANSLATEAPI_MAX_POLLS=200
SECURITY_EVENT_RETENTION_DAYS=30
SECURITY_EVENT_MAX_ROWS=5000
ENABLE_KOCHWIKI_SEED=0
AUTO_SEED_KOCHWIKI=0
ALLOW_DEV_SEED=0
KOCHWIKI_CSV_PATH=rezepte_kochwiki_clean_3713.csv
IMPORT_DOWNLOAD_IMAGES=0
SEED_ADMIN_EMAIL=admin@mealmate.local
SEED_ADMIN_PASSWORD=AdminPass123!
```
ZEILEN-ERKL?RUNG
1. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `APP_NAME`.
2. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `APP_ENV`.
3. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `APP_URL`.
4. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `SECRET_KEY`.
5. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `ALGORITHM`.
6. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TOKEN_EXPIRE_MINUTES`.
7. Diese Zeile ist ein Kommentar mit einem Hinweis zur Konfiguration.
8. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `DATABASE_URL`.
9. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `ALLOWED_HOSTS`.
10. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `COOKIE_SECURE`.
11. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `FORCE_HTTPS`.
12. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `LOG_LEVEL`.
13. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `CSP_IMG_SRC`.
14. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `CSRF_COOKIE_NAME`.
15. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `CSRF_HEADER_NAME`.
16. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `PASSWORD_RESET_TOKEN_MINUTES`.
17. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `MAX_UPLOAD_MB`.
18. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `MAX_CSV_UPLOAD_MB`.
19. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `ALLOWED_IMAGE_TYPES`.
20. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `MAIL_OUTBOX_PATH`.
21. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `MAIL_OUTBOX_EMAIL_CHANGE_PATH`.
22. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `SMTP_HOST`.
23. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `SMTP_PORT`.
24. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `SMTP_USER`.
25. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `SMTP_PASSWORD`.
26. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `SMTP_FROM`.
27. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATEAPI_ENABLED`.
28. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATE_AUTO_ON_PUBLISH`.
29. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATE_LAZY_ON_VIEW`.
30. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `I18N_STRICT`.
31. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATION_PROVIDER`.
32. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATE_SOURCE_LANG`.
33. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATE_TARGET_LANGS`.
34. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATE_MAX_RECIPES_PER_RUN`.
35. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATEAPI_BASE_URL`.
36. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATEAPI_API_KEY`.
37. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATEAPI_POLL_INTERVAL_SECONDS`.
38. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `TRANSLATEAPI_MAX_POLLS`.
39. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `SECURITY_EVENT_RETENTION_DAYS`.
40. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `SECURITY_EVENT_MAX_ROWS`.
41. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `ENABLE_KOCHWIKI_SEED`.
42. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `AUTO_SEED_KOCHWIKI`.
43. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `ALLOW_DEV_SEED`.
44. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `KOCHWIKI_CSV_PATH`.
45. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `IMPORT_DOWNLOAD_IMAGES`.
46. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `SEED_ADMIN_EMAIL`.
47. Diese Zeile setzt den Beispielwert f?r die Umgebungsvariable `SEED_ADMIN_PASSWORD`.

### tests/test_seed_accounts.py
```python
from sqlalchemy import func, select

from app.dev_seed_accounts import seed_test_accounts
from app.models import User


def test_seed_accounts_idempotent(db_session_factory):
    db = db_session_factory()
    try:
        first_report = seed_test_accounts(db)
        db.commit()

        total_after_first = db.scalar(select(func.count()).select_from(User))
        admin_after_first = db.scalar(select(func.count()).select_from(User).where(User.role == "admin"))
        user_after_first = db.scalar(select(func.count()).select_from(User).where(User.role == "user"))

        assert first_report.created == 6
        assert total_after_first == 6
        assert admin_after_first == 3
        assert user_after_first == 3

        second_report = seed_test_accounts(db)
        db.commit()

        total_after_second = db.scalar(select(func.count()).select_from(User))
        admin_after_second = db.scalar(select(func.count()).select_from(User).where(User.role == "admin"))
        user_after_second = db.scalar(select(func.count()).select_from(User).where(User.role == "user"))

        assert second_report.created == 0
        assert second_report.updated + second_report.unchanged == 6
        assert total_after_second == 6
        assert admin_after_second == 3
        assert user_after_second == 3
    finally:
        db.close()
```
ZEILEN-ERKL?RUNG
1. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
2. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
3. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
4. Diese Zeile importiert ein ben?tigtes Modul oder eine Funktion.
5. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
6. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
7. Diese Zeile definiert eine Funktion f?r den Seed-Ablauf.
8. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
9. Diese Zeile startet einen Fehlerbehandlungsblock.
10. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
11. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
12. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
13. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
14. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
15. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
16. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
17. Diese Zeile pr?ft im Test eine erwartete Bedingung.
18. Diese Zeile pr?ft im Test eine erwartete Bedingung.
19. Diese Zeile pr?ft im Test eine erwartete Bedingung.
20. Diese Zeile pr?ft im Test eine erwartete Bedingung.
21. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
22. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
23. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
24. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
25. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
26. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
27. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
28. Diese Zeile ist absichtlich leer, um den Code lesbarer zu machen.
29. Diese Zeile pr?ft im Test eine erwartete Bedingung.
30. Diese Zeile pr?ft im Test eine erwartete Bedingung.
31. Diese Zeile pr?ft im Test eine erwartete Bedingung.
32. Diese Zeile pr?ft im Test eine erwartete Bedingung.
33. Diese Zeile pr?ft im Test eine erwartete Bedingung.
34. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.
35. Diese Zeile enth?lt Programmlogik f?r den Seed-Mechanismus.

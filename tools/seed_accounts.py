from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from sqlalchemy import select

from app.config import get_settings
from app.database import SessionLocal
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
    unchanged: int = 0
    rows: list[AccountSeedRow] | None = None

    def __post_init__(self) -> None:
        if self.rows is None:
            self.rows = []


ACCOUNT_SPECS: tuple[AccountSeedSpec, ...] = (
    AccountSeedSpec("admin1@mealmate.local", "admin1", "admin", "AdminPass123!"),
    AccountSeedSpec("admin2@mealmate.local", "admin2", "admin", "AdminPass123!"),
    AccountSeedSpec("admin3@mealmate.local", "admin3", "admin", "AdminPass123!"),
    AccountSeedSpec("user1@mealmate.local", "user1", "user", "UserPass123!"),
    AccountSeedSpec("user2@mealmate.local", "user2", "user", "UserPass123!"),
    AccountSeedSpec("user3@mealmate.local", "user3", "user", "UserPass123!"),
)


def build_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser(
        description="Erzeugt idempotent 3 Admins und 3 User fuer lokale Tests."
    )


def _render_table(rows: Iterable[list[str]]) -> str:
    rows_list = list(rows)
    widths = [max(len(row[index]) for row in rows_list) for index in range(len(rows_list[0]))]
    lines: list[str] = []
    for row_index, row in enumerate(rows_list):
        lines.append(" | ".join(cell.ljust(widths[idx]) for idx, cell in enumerate(row)))
        if row_index == 0:
            lines.append("-+-".join("-" * width for width in widths))
    return "\n".join(lines)


def _read_env_file_value(key: str, env_file: Path) -> str | None:
    if not env_file.exists():
        return None
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        left, right = line.split("=", 1)
        if left.strip() == key:
            return right.strip()
    return None


def _parse_bool_env(value: str | None) -> bool:
    if value is None:
        return False
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_allow_dev_seed() -> bool:
    from_process = os.getenv("ALLOW_DEV_SEED")
    if from_process is not None:
        return _parse_bool_env(from_process)
    from_file = _read_env_file_value("ALLOW_DEV_SEED", Path(".env"))
    return _parse_bool_env(from_file)


def _ensure_dev_seed_allowed(app_env: str, allow_dev_seed: bool) -> None:
    if app_env == "dev" or allow_dev_seed:
        return
    raise RuntimeError("Testaccount-Seed ist nur in APP_ENV=dev oder mit ALLOW_DEV_SEED=1 erlaubt.")


def _collect_taken_username_norms(db) -> set[str]:
    values = db.scalars(select(User.username_normalized).where(User.username_normalized.is_not(None))).all()
    return {value for value in values if value}


def _find_available_username(preferred_normalized: str, taken: set[str]) -> tuple[str, bool]:
    if preferred_normalized not in taken:
        return preferred_normalized, False
    base = preferred_normalized[:24]
    index = 2
    while True:
        candidate = f"{base}{index}"[:30]
        if candidate not in taken:
            return candidate, True
        index += 1


def seed_accounts(db) -> AccountSeedReport:
    report = AccountSeedReport()
    taken_usernames = _collect_taken_username_norms(db)
    emails = [item.email for item in ACCOUNT_SPECS]
    users_by_email = {user.email.lower(): user for user in db.scalars(select(User).where(User.email.in_(emails))).all()}

    for spec in ACCOUNT_SPECS:
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
        user = User(
            email=email_normalized,
            username=username_norm,
            username_normalized=username_norm,
            hashed_password=hash_password(spec.password),
            role=spec.role,
        )
        db.add(user)
        users_by_email[email_normalized] = user
        taken_usernames.add(username_norm)
        report.created += 1
        report.rows.append(
            AccountSeedRow(
                email=email_normalized,
                username=username_norm,
                role=spec.role,
                password=spec.password,
                status="created-adjusted-username" if adjusted else "created",
            )
        )
    return report


def main() -> int:
    _ = build_parser().parse_args()
    settings = get_settings()
    try:
        _ensure_dev_seed_allowed(settings.app_env, _resolve_allow_dev_seed())
    except RuntimeError as exc:
        print(f"ABBRUCH: {exc}")
        return 1

    with SessionLocal() as db:
        report = seed_accounts(db)
        db.commit()

    print("Seed abgeschlossen.")
    print(f"Erstellt: {report.created}")
    print(f"Unveraendert: {report.unchanged}")
    print("")
    table_rows = [["Email", "Username", "Role", "Passwort", "Status"]]
    for row in report.rows or []:
        table_rows.append([row.email, row.username, row.role, row.password, row.status])
    print(_render_table(table_rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

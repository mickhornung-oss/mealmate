from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine, select, text

from app.config import get_settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safe database reset helper for development environments.")
    parser.add_argument("--yes", action="store_true", help="Execute destructive steps.")
    parser.add_argument("--drop-all", action="store_true", help="Drop all tables/schema (or remove sqlite file).")
    parser.add_argument("--migrate", action="store_true", help="Run alembic upgrade head after reset.")
    parser.add_argument("--seed-admin", action="store_true", help="Create default admin user after migrations.")
    return parser.parse_args()


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sqlite_file_path(database_url: str, root: Path) -> Path | None:
    if not database_url.startswith("sqlite"):
        return None
    if database_url.endswith(":memory:"):
        return None
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return None
    raw_path = database_url[len(prefix) :]
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = (root / raw_path).resolve()
    return candidate


def run_migrations(root: Path) -> None:
    command = [sys.executable, "-m", "alembic", "-c", "alembic.ini", "upgrade", "head"]
    subprocess.run(command, cwd=root, check=True)


def drop_all_sqlite_tables(database_url: str) -> None:
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    try:
        with engine.begin() as connection:
            connection.execute(text("PRAGMA foreign_keys = OFF"))
            table_names = connection.execute(
                text("SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'")
            ).scalars().all()
            for table_name in table_names:
                connection.execute(text(f'DROP TABLE IF EXISTS "{table_name}"'))
            connection.execute(text("PRAGMA foreign_keys = ON"))
    finally:
        engine.dispose()


def seed_admin_user() -> None:
    from app.database import SessionLocal
    from app.models import User
    from app.security import hash_password

    settings = get_settings()
    session = SessionLocal()
    try:
        existing = session.scalar(select(User).where(User.email == settings.seed_admin_email.strip().lower()))
        if existing:
            if existing.role != "admin":
                existing.role = "admin"
                session.commit()
            print(f"[seed-admin] existing admin ensured: {existing.email}")
            return
        admin = User(
            email=settings.seed_admin_email.strip().lower(),
            hashed_password=hash_password(settings.seed_admin_password),
            role="admin",
        )
        session.add(admin)
        session.commit()
        print(f"[seed-admin] created: {admin.email}")
    finally:
        session.close()


def drop_for_postgres(database_url: str, app_env: str) -> None:
    if app_env != "dev":
        raise RuntimeError("Postgres schema drop is blocked outside APP_ENV=dev.")
    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.begin() as connection:
            connection.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            connection.execute(text("CREATE SCHEMA public"))
    finally:
        engine.dispose()


def main() -> int:
    args = parse_args()
    settings = get_settings()
    root = project_root()
    db_url = settings.sqlalchemy_database_url
    sqlite_path = sqlite_file_path(db_url, root)

    planned_actions: list[str] = []
    if args.drop_all:
        if sqlite_path:
            planned_actions.append(f"delete sqlite file: {sqlite_path}")
        else:
            planned_actions.append("drop postgres schema public")
    if args.migrate:
        planned_actions.append("run alembic upgrade head")
    if args.seed_admin:
        planned_actions.append("create/ensure seed admin user")

    if not planned_actions:
        print("No action selected. Use --drop-all and/or --migrate and/or --seed-admin.")
        return 0

    print("[plan] The following actions are configured:")
    for action in planned_actions:
        print(f" - {action}")
    print("[safety] Backup your project and database before running destructive steps.")

    if not args.yes:
        print("[dry-run] Add --yes to execute.")
        return 0

    if args.drop_all:
        if sqlite_path:
            if sqlite_path.exists():
                try:
                    sqlite_path.unlink()
                    print(f"[drop-all] deleted sqlite file: {sqlite_path}")
                except PermissionError:
                    print("[drop-all] sqlite file is locked, using in-file schema drop fallback")
                    drop_all_sqlite_tables(db_url)
                    print("[drop-all] sqlite schema reset completed inside existing file")
            else:
                print(f"[drop-all] sqlite file not found (nothing to delete): {sqlite_path}")
        else:
            drop_for_postgres(db_url, settings.app_env)
            print("[drop-all] postgres schema reset completed")

    if args.migrate:
        run_migrations(root)
        print("[migrate] alembic upgrade head finished")

    if args.seed_admin:
        seed_admin_user()

    print("[done] db_reset finished")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

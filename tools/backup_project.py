from __future__ import annotations

import argparse
import shutil
from datetime import datetime
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from app.config import get_settings

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "htmlcov",
    "node_modules",
    "dist",
    "build",
    "backups",
}

EXCLUDE_FILE_SUFFIXES = {".pyc", ".pyo", ".pyd"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a safe project backup before cleanup actions.")
    parser.add_argument("--yes", action="store_true", help="Execute backup creation.")
    parser.add_argument("--output-dir", default="backups", help="Target directory for backup artifacts.")
    return parser.parse_args()


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def sqlite_file_path(database_url: str, root: Path) -> Path | None:
    if not database_url.startswith("sqlite") or database_url.endswith(":memory:"):
        return None
    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        return None
    raw = database_url[len(prefix) :]
    path = Path(raw)
    if not path.is_absolute():
        path = (root / raw).resolve()
    return path


def iter_project_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in EXCLUDE_FILE_SUFFIXES:
            continue
        yield path


def create_project_zip(root: Path, output_dir: Path, timestamp: str) -> Path:
    zip_path = output_dir / f"project_backup_{timestamp}.zip"
    with ZipFile(zip_path, mode="w", compression=ZIP_DEFLATED) as archive:
        for file_path in iter_project_files(root):
            archive.write(file_path, arcname=file_path.relative_to(root))
    return zip_path


def copy_sqlite_backup(sqlite_path: Path, output_dir: Path, timestamp: str) -> Path | None:
    if not sqlite_path.exists():
        return None
    backup_path = output_dir / f"sqlite_backup_{timestamp}{sqlite_path.suffix or '.db'}"
    shutil.copy2(sqlite_path, backup_path)
    return backup_path


def main() -> int:
    args = parse_args()
    root = project_root()
    settings = get_settings()
    output_dir = Path(args.output_dir)
    if not output_dir.is_absolute():
        output_dir = (root / output_dir).resolve()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    sqlite_path = sqlite_file_path(settings.sqlalchemy_database_url, root)

    print("[backup-plan] This command creates backups only; no cleanup/deletion happens here.")
    print(f"[backup-plan] Project root: {root}")
    print(f"[backup-plan] Output dir: {output_dir}")
    if sqlite_path:
        print(f"[backup-plan] SQLite source: {sqlite_path}")
    else:
        print("[backup-plan] Database is not SQLite.")
        print("[backup-plan] Postgres backup command example:")
        print('  pg_dump "$DATABASE_URL" > backups/postgres_backup.sql')

    if not args.yes:
        print("[dry-run] Add --yes to create the backup artifacts.")
        return 0

    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = create_project_zip(root, output_dir, timestamp)
    print(f"[done] Project ZIP created: {zip_path}")

    if sqlite_path:
        sqlite_backup = copy_sqlite_backup(sqlite_path, output_dir, timestamp)
        if sqlite_backup:
            print(f"[done] SQLite copy created: {sqlite_backup}")
        else:
            print("[done] SQLite file not found; no DB copy created.")

    print("[done] Backup finished.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

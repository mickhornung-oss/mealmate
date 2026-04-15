import argparse
import sys
from pathlib import Path

from sqlalchemy import select

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.models import User
from app.services import import_kochwiki_csv


def run_import(csv_path: Path, admin_email: str, mode: str) -> None:
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    db = SessionLocal()
    try:
        admin = db.scalar(select(User).where(User.email == admin_email))
        if not admin:
            raise RuntimeError(f"Admin user '{admin_email}' not found. Run scripts/seed_admin.py first.")
        report = import_kochwiki_csv(db, csv_path, admin.id, mode=mode)
        print(
            "Import finished.",
            f"Inserted={report.inserted},",
            f"Updated={report.updated},",
            f"Skipped={report.skipped},",
            f"Errors={len(report.errors)}",
        )
        for item in report.errors[:25]:
            print(f"- {item}")
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import KochWiki CSV into MealMate database.")
    parser.add_argument(
        "--file",
        default="rezepte_kochwiki_clean_3713.csv",
        help="Path to source CSV.",
    )
    parser.add_argument(
        "--admin-email",
        default="admin@mealmate.local",
        help="Owner account for imported recipes.",
    )
    parser.add_argument(
        "--mode",
        choices=["insert_only", "update_existing"],
        default="insert_only",
        help="Import strategy.",
    )
    args = parser.parse_args()
    run_import(Path(args.file), args.admin_email, args.mode)


if __name__ == "__main__":
    main()

import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.moderation_repair import run_moderation_repair


def main() -> None:
    parser = argparse.ArgumentParser(description="Repair moderation visibility by moving non-admin published recipes to pending submissions.")
    parser.add_argument("--apply", action="store_true", help="Apply changes. Without this flag, only dry-run is executed.")
    parser.add_argument("--verbose", action="store_true", help="Print per-recipe detail lines.")
    args = parser.parse_args()

    db = SessionLocal()
    try:
        report = run_moderation_repair(db, dry_run=not args.apply)
        if args.apply:
            db.commit()
        else:
            db.rollback()
        print("Moderation repair finished.")
        print(f"dry_run={report.dry_run}")
        print(f"scanned_count={report.scanned_count}")
        print(f"affected_count={report.affected_count}")
        print(f"moved_to_pending_count={report.moved_to_pending_count}")
        print(f"skipped_count={report.skipped_count}")
        if args.verbose:
            for detail in report.details:
                print(f"- {detail}")
    finally:
        db.close()


if __name__ == "__main__":
    main()

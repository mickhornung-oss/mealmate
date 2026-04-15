from __future__ import annotations

import argparse

from app.database import SessionLocal
from app.translation_service import find_translation_batch_job, poll_translation_batch_job


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Poll TranslateAPI batch job and persist results.")
    parser.add_argument("--job-id", required=True, help="Internal DB job id or external TranslateAPI job id.")
    parser.add_argument("--max-polls", type=int, default=None, help="Override max poll iterations.")
    parser.add_argument("--poll-interval", type=float, default=None, help="Override poll interval seconds.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    db = SessionLocal()
    try:
        job = find_translation_batch_job(db, args.job_id)
        if not job:
            print(f"[translation-worker] job not found: {args.job_id}")
            return 1

        poll_translation_batch_job(
            db,
            job,
            max_polls=args.max_polls,
            poll_interval_seconds=args.poll_interval,
        )
        db.commit()
        print("[translation-worker] finished")
        print(f" internal_id: {job.id}")
        print(f" external_job_id: {job.external_job_id}")
        print(f" status: {job.status}")
        print(f" progress: {job.completed_items}/{job.total_items}")
        print(f" created: {job.created_items}")
        print(f" updated: {job.updated_items}")
        print(f" skipped: {job.skipped_items}")
        print(f" errors: {job.error_count}")
        return 0
    except Exception as exc:
        db.rollback()
        print(f"[translation-worker] failed: {exc}")
        return 2
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())

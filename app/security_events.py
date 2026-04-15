import logging
from datetime import datetime, timedelta, timezone

from fastapi import Request
from sqlalchemy import delete, func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import SecurityEvent

settings = get_settings()
logger = logging.getLogger("mealmate.security")


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
    _ = db
    try:
        with SessionLocal() as audit_db:
            audit_db.add(
                SecurityEvent(
                    user_id=user_id,
                    event_type=event_type[:80],
                    ip=_extract_ip(request),
                    user_agent=_extract_user_agent(request),
                    details=(details or "")[:300] or None,
                )
            )
            _prune_security_events(audit_db)
            audit_db.commit()
    except SQLAlchemyError as exc:
        logger.warning("security_event_write_skipped reason=%s", exc)

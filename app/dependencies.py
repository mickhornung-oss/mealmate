from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.i18n import t
from app.i18n.service import available_langs
from app.models import User
from app.security import decode_access_token, password_token_fingerprint
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
    payload_pwdv = str(payload.get("pwdv", "") or "").strip()
    if user and payload_pwdv:
        if payload_pwdv != password_token_fingerprint(user.hashed_password):
            return None
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
        "app_name": settings.app_name,
        "csrf_token": csrf_token,
        "csrf_header_name": settings.csrf_header_name,
        "request_id": request_id,
        "current_lang": getattr(getattr(request, "state", None), "lang", "de"),
        "available_langs": available_langs(),
    }
    base.update(kwargs)
    return base

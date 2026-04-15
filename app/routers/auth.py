from datetime import datetime, timedelta, timezone
import logging
import re

from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, status
from sqlalchemy import and_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import get_current_user, get_current_user_optional, template_context
from app.i18n import t
from app.mailer import MailPayload, get_mailer
from app.models import PasswordResetToken, User
from app.rate_limit import key_by_ip, key_by_user_or_ip, limiter
from app.security import (
    create_access_token,
    create_raw_reset_token,
    hash_password,
    hash_reset_token,
    normalize_username,
    password_token_fingerprint,
    validate_password_policy,
    validate_username_policy,
    verify_password,
)
from app.security_events import log_security_event
from app.views import redirect, safe_redirect_path, templates

router = APIRouter(tags=["auth"])
settings = get_settings()
logger = logging.getLogger("mealmate.auth")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def set_auth_cookie(response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token}",
        httponly=True,
        secure=settings.resolved_cookie_secure,
        samesite="lax",
        max_age=60 * 60 * 24,
        path="/",
    )


def _identifier_type(identifier: str) -> str:
    return "email" if "@" in identifier else "username"


def _find_user_by_identifier(db: Session, identifier: str) -> User | None:
    cleaned = identifier.strip()
    if not cleaned:
        return None
    if "@" in cleaned:
        return db.scalar(select(User).where(User.email == cleaned.lower()))
    return db.scalar(select(User).where(User.username_normalized == normalize_username(cleaned)))


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _is_valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.fullmatch(value))


def _find_valid_token(
    db: Session,
    raw_token: str,
    *,
    purpose: str,
) -> PasswordResetToken | None:
    now = datetime.now(timezone.utc)
    return db.scalar(
        select(PasswordResetToken).where(
            and_(
                PasswordResetToken.token_hash == hash_reset_token(raw_token),
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > now,
                PasswordResetToken.purpose == purpose,
            )
        )
    )


def _reset_token_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=settings.password_reset_token_minutes)


def _render_me(
    request: Request,
    current_user: User,
    message: str | None = None,
    error: str | None = None,
    status_code: int = status.HTTP_200_OK,
):
    return templates.TemplateResponse(
        "me.html",
        template_context(
            request,
            current_user,
            user=current_user,
            message=message,
            error=error,
        ),
        status_code=status_code,
    )


@router.get("/login")
@router.get("/auth/login")
def login_page(
    request: Request,
    message: str = "",
    current_user: User | None = Depends(get_current_user_optional),
):
    if current_user:
        return redirect("/")
    message_map = {
        "reset_done": t("auth.reset_success", request=request),
        "password_changed": t("auth.password_changed_success", request=request),
    }
    return templates.TemplateResponse(
        "auth_login.html",
        template_context(
            request,
            current_user,
            error=None,
            message=message_map.get(message, ""),
            identifier_value="",
        ),
    )


@router.post("/login")
@router.post("/auth/login")
@limiter.limit("5/minute", key_func=key_by_ip)
def login_submit(
    request: Request,
    response: Response,
    identifier: str = Form(...),
    password: str = Form(...),
    next_path: str = Form("", alias="next"),
    db: Session = Depends(get_db),
):
    _ = response
    user = _find_user_by_identifier(db, identifier)
    id_type = _identifier_type(identifier)
    if not user or not verify_password(password, user.hashed_password):
        log_security_event(
            db,
            request,
            event_type="login_failed",
            user_id=user.id if user else None,
            details=f"identifier={id_type}",
        )
        try:
            db.commit()
        except SQLAlchemyError as exc:
            db.rollback()
            logger.warning("login_failed_audit_commit_skipped reason=%s", exc)
        return templates.TemplateResponse(
            "auth_login.html",
            template_context(
                request,
                None,
                error=t("error.invalid_credentials", request=request),
                message="",
                identifier_value=identifier,
            ),
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    user.last_login_at = datetime.now(timezone.utc)
    user.last_login_ip = request.client.host[:64] if request.client and request.client.host else None
    user.last_login_user_agent = (request.headers.get("user-agent") or "")[:200] or None
    db.add(user)
    log_security_event(db, request, event_type="login_success", user_id=user.id, details=f"identifier={id_type}")
    try:
        db.commit()
    except SQLAlchemyError as exc:
        db.rollback()
        logger.warning("login_success_audit_commit_skipped reason=%s", exc)
    token = create_access_token(user.user_uid, user.role, password_token_fingerprint(user.hashed_password))
    response = redirect(safe_redirect_path(next_path, default="/"))
    set_auth_cookie(response, token)
    return response


@router.get("/register")
@router.get("/auth/register")
def register_page(request: Request, current_user: User | None = Depends(get_current_user_optional)):
    if current_user:
        return redirect("/")
    return templates.TemplateResponse(
        "auth_register.html",
        template_context(request, current_user, error=None, username_value=""),
    )


@router.post("/register")
@router.post("/auth/register")
@limiter.limit("3/minute", key_func=key_by_ip)
def register_submit(
    request: Request,
    response: Response,
    email: str = Form(...),
    username: str = Form(""),
    password: str = Form(...),
    next_path: str = Form("", alias="next"),
    db: Session = Depends(get_db),
):
    _ = response
    normalized_email = email.strip().lower()
    username_value = username.strip()
    normalized_username = normalize_username(username_value) if username_value else None
    password_error = validate_password_policy(password)
    if password_error:
        return templates.TemplateResponse(
            "auth_register.html",
            template_context(request, None, error=password_error, username_value=username_value),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if username_value:
        username_error = validate_username_policy(username_value)
        if username_error:
            return templates.TemplateResponse(
                "auth_register.html",
                template_context(request, None, error=username_error, username_value=username_value),
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    existing = db.scalar(select(User).where(User.email == normalized_email))
    if existing:
        return templates.TemplateResponse(
            "auth_register.html",
            template_context(request, None, error=t("error.email_registered", request=request), username_value=username_value),
            status_code=status.HTTP_409_CONFLICT,
        )
    if normalized_username:
        same_username = db.scalar(select(User).where(User.username_normalized == normalized_username))
        if same_username:
            return templates.TemplateResponse(
                "auth_register.html",
                template_context(request, None, error=t("error.username_taken", request=request), username_value=username_value),
                status_code=status.HTTP_409_CONFLICT,
            )
    user = User(
        email=normalized_email,
        username=username_value or None,
        username_normalized=normalized_username,
        hashed_password=hash_password(password),
        role="user",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(user.user_uid, user.role, password_token_fingerprint(user.hashed_password))
    response = redirect(safe_redirect_path(next_path, default="/"))
    set_auth_cookie(response, token)
    return response


@router.post("/logout")
def logout(next_path: str = Form("", alias="next")):
    response = redirect(safe_redirect_path(next_path, default="/"))
    response.delete_cookie("access_token", path="/")
    return response


@router.get("/auth/forgot-password")
@router.get("/forgot-password")
def forgot_password_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "auth_forgot_password.html",
        template_context(request, current_user, error=None, message=None, identifier_value=""),
    )


@router.post("/auth/forgot-password")
@router.post("/forgot-password")
@limiter.limit("5/minute", key_func=key_by_ip)
def forgot_password_submit(
    request: Request,
    response: Response,
    identifier: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = response
    runtime_settings = get_settings()
    generic_message = t("auth.forgot_generic_response", request=request)
    user = _find_user_by_identifier(db, identifier)
    if user:
        raw_token = create_raw_reset_token()
        token_hash = hash_reset_token(raw_token)
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=token_hash,
                expires_at=_reset_token_expires_at(),
                created_ip=request.client.host[:64] if request.client and request.client.host else None,
                created_user_agent=(request.headers.get("user-agent") or "")[:200] or None,
                purpose="password_reset",
            )
        )
        log_security_event(db, request, event_type="pwd_reset_requested", user_id=user.id, details="identifier=known")
        db.commit()
        reset_link = f"{str(runtime_settings.app_url).rstrip('/')}/auth/reset-password?token={raw_token}"
        mailer = get_mailer(runtime_settings)
        subject = t("auth.reset_email_subject", request=request)
        body = t("auth.reset_email_body", request=request, reset_link=reset_link)
        try:
            mailer.send(MailPayload(to_email=user.email, subject=subject, body=body))
        except Exception:
            # We keep the response generic and avoid leaking whether delivery worked.
            logger.warning("password_reset_mail_send_failed user_id=%s", user.id)
    else:
        log_security_event(db, request, event_type="pwd_reset_requested", user_id=None, details="identifier=unknown")
        db.commit()
    return templates.TemplateResponse(
        "auth_forgot_password.html",
        template_context(
            request,
            None,
            error=None,
            message=generic_message,
            identifier_value="",
        ),
    )


@router.get("/auth/reset-password")
def reset_password_page(
    request: Request,
    token: str = "",
    current_user: User | None = Depends(get_current_user_optional),
):
    return templates.TemplateResponse(
        "auth_reset_password.html",
        template_context(
            request,
            current_user,
            token_value=token,
            error=None,
            message=None,
        ),
    )


@router.post("/auth/reset-password")
@limiter.limit("5/minute", key_func=key_by_ip)
def reset_password_submit(
    request: Request,
    response: Response,
    token: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    _ = response
    token_value = token.strip()
    if not token_value:
        return templates.TemplateResponse(
            "auth_reset_password.html",
            template_context(request, None, token_value="", error=t("error.reset_token_invalid", request=request), message=None),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "auth_reset_password.html",
            template_context(
                request,
                None,
                token_value=token_value,
                error=t("error.password_confirm_mismatch", request=request),
                message=None,
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    password_error = validate_password_policy(new_password)
    if password_error:
        return templates.TemplateResponse(
            "auth_reset_password.html",
            template_context(request, None, token_value=token_value, error=password_error, message=None),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    now = datetime.now(timezone.utc)
    reset_token = _find_valid_token(db, token_value, purpose="password_reset")
    if not reset_token:
        return templates.TemplateResponse(
            "auth_reset_password.html",
            template_context(request, None, token_value="", error=t("error.reset_token_invalid", request=request), message=None),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    user = db.scalar(select(User).where(User.id == reset_token.user_id))
    if not user:
        return templates.TemplateResponse(
            "auth_reset_password.html",
            template_context(request, None, token_value="", error=t("error.reset_token_invalid", request=request), message=None),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    user.hashed_password = hash_password(new_password)
    reset_token.used_at = now
    other_tokens = db.scalars(
        select(PasswordResetToken).where(
            and_(
                PasswordResetToken.user_id == user.id,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.id != reset_token.id,
                PasswordResetToken.purpose == "password_reset",
            )
        )
    ).all()
    for item in other_tokens:
        item.used_at = now
    db.add(user)
    log_security_event(db, request, event_type="pwd_reset_done", user_id=user.id, details="token=single-use")
    db.commit()
    return redirect("/login?message=reset_done")


@router.post("/auth/change-password")
@limiter.limit("3/minute", key_func=key_by_user_or_ip)
def change_password_submit(
    request: Request,
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not verify_password(old_password, current_user.hashed_password):
        return _render_me(
            request,
            current_user,
            error=t("error.password_old_invalid", request=request),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if new_password != confirm_password:
        return _render_me(
            request,
            current_user,
            error=t("error.password_confirm_mismatch", request=request),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    password_error = validate_password_policy(new_password)
    if password_error:
        return _render_me(
            request,
            current_user,
            error=password_error,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    current_user.hashed_password = hash_password(new_password)
    db.add(current_user)
    log_security_event(db, request, event_type="pwd_changed", user_id=current_user.id, details="changed_via_profile")
    db.commit()
    response = redirect("/me?message=password_changed")
    set_auth_cookie(
        response,
        create_access_token(
            current_user.user_uid,
            current_user.role,
            password_token_fingerprint(current_user.hashed_password),
        ),
    )
    return response


@router.post("/profile/username")
@limiter.limit("5/minute", key_func=key_by_user_or_ip)
def update_username_submit(
    request: Request,
    username: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    username_value = username.strip()
    username_error = validate_username_policy(username_value)
    if username_error:
        return _render_me(request, current_user, error=username_error, status_code=status.HTTP_400_BAD_REQUEST)
    normalized_username = normalize_username(username_value)
    existing = db.scalar(
        select(User).where(
            and_(
                User.username_normalized == normalized_username,
                User.id != current_user.id,
            )
        )
    )
    if existing:
        return _render_me(
            request,
            current_user,
            error=t("error.username_taken", request=request),
            status_code=status.HTTP_409_CONFLICT,
        )
    current_user.username = username_value
    current_user.username_normalized = normalized_username
    db.add(current_user)
    log_security_event(db, request, event_type="username_changed", user_id=current_user.id, details="profile_update")
    db.commit()
    return redirect("/me?message=username_updated")


@router.get("/auth/change-email")
def change_email_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        "auth_change_email.html",
        template_context(
            request,
            current_user,
            current_email=current_user.email,
            new_email_value="",
            message=None,
            error=None,
        ),
    )


@router.post("/auth/change-email/request")
@limiter.limit("5/minute", key_func=key_by_ip)
@limiter.limit("3/minute", key_func=key_by_user_or_ip)
def change_email_request_submit(
    request: Request,
    new_email: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    runtime_settings = get_settings()
    normalized_new_email = _normalize_email(new_email)
    if not _is_valid_email(normalized_new_email):
        return templates.TemplateResponse(
            "auth_change_email.html",
            template_context(
                request,
                current_user,
                current_email=current_user.email,
                new_email_value=new_email,
                message=None,
                error=t("error.email_invalid", request=request),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if normalized_new_email == current_user.email:
        return templates.TemplateResponse(
            "auth_change_email.html",
            template_context(
                request,
                current_user,
                current_email=current_user.email,
                new_email_value="",
                message=t("auth.email_change_same_email", request=request),
                error=None,
            ),
        )
    existing = db.scalar(select(User).where(and_(User.email == normalized_new_email, User.id != current_user.id)))
    if existing:
        return templates.TemplateResponse(
            "auth_change_email.html",
            template_context(
                request,
                current_user,
                current_email=current_user.email,
                new_email_value=new_email,
                message=None,
                error=t("error.email_unavailable", request=request),
            ),
            status_code=status.HTTP_409_CONFLICT,
        )
    now = datetime.now(timezone.utc)
    open_tokens = db.scalars(
        select(PasswordResetToken).where(
            and_(
                PasswordResetToken.user_id == current_user.id,
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.purpose == "email_change",
            )
        )
    ).all()
    for open_token in open_tokens:
        open_token.used_at = now
    raw_token = create_raw_reset_token()
    db.add(
        PasswordResetToken(
            user_id=current_user.id,
            token_hash=hash_reset_token(raw_token),
            new_email_normalized=normalized_new_email,
            expires_at=_reset_token_expires_at(),
            created_ip=request.client.host[:64] if request.client and request.client.host else None,
            created_user_agent=(request.headers.get("user-agent") or "")[:200] or None,
            purpose="email_change",
        )
    )
    log_security_event(
        db,
        request,
        event_type="email_change_requested",
        user_id=current_user.id,
        details="delivery=new_email",
    )
    db.commit()
    confirmation_link = f"{str(runtime_settings.app_url).rstrip('/')}/auth/change-email/confirm?token={raw_token}"
    try:
        get_mailer(runtime_settings).send(
            MailPayload(
                to_email=normalized_new_email,
                subject=t("auth.email_change_subject", request=request),
                body=t("auth.email_change_body", request=request, confirm_link=confirmation_link),
                outbox_file=runtime_settings.mail_outbox_email_change_path,
            )
        )
    except Exception:
        logger.warning("email_change_mail_send_failed user_uid=%s", current_user.user_uid)
    return templates.TemplateResponse(
        "auth_change_email.html",
        template_context(
            request,
            current_user,
            current_email=current_user.email,
            new_email_value="",
            message=t("auth.email_change_requested", request=request),
            error=None,
        ),
    )


@router.get("/auth/change-email/confirm")
def change_email_confirm_page(
    request: Request,
    token: str = "",
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    token_value = token.strip()
    record = _find_valid_token(db, token_value, purpose="email_change") if token_value else None
    if not record or not record.new_email_normalized:
        return templates.TemplateResponse(
            "auth_change_email_confirm.html",
            template_context(
                request,
                current_user,
                token_value="",
                is_valid=False,
                new_email_value="",
                message=None,
                error=t("error.email_change_token_invalid", request=request),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return templates.TemplateResponse(
        "auth_change_email_confirm.html",
        template_context(
            request,
            current_user,
            token_value=token_value,
            is_valid=True,
            new_email_value=record.new_email_normalized,
            message=None,
            error=None,
        ),
    )


@router.post("/auth/change-email/confirm")
@limiter.limit("5/minute", key_func=key_by_ip)
def change_email_confirm_submit(
    request: Request,
    token: str = Form(...),
    db: Session = Depends(get_db),
):
    token_value = token.strip()
    record = _find_valid_token(db, token_value, purpose="email_change") if token_value else None
    if not record or not record.new_email_normalized:
        return templates.TemplateResponse(
            "auth_change_email_confirm.html",
            template_context(
                request,
                None,
                token_value="",
                is_valid=False,
                new_email_value="",
                message=None,
                error=t("error.email_change_token_invalid", request=request),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    user = db.scalar(select(User).where(User.id == record.user_id))
    if not user:
        record.used_at = datetime.now(timezone.utc)
        db.add(record)
        db.commit()
        return templates.TemplateResponse(
            "auth_change_email_confirm.html",
            template_context(
                request,
                None,
                token_value="",
                is_valid=False,
                new_email_value="",
                message=None,
                error=t("error.email_change_token_invalid", request=request),
            ),
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    conflict = db.scalar(select(User).where(and_(User.email == record.new_email_normalized, User.id != user.id)))
    if conflict:
        return templates.TemplateResponse(
            "auth_change_email_confirm.html",
            template_context(
                request,
                None,
                token_value="",
                is_valid=False,
                new_email_value="",
                message=None,
                error=t("error.email_unavailable", request=request),
            ),
            status_code=status.HTTP_409_CONFLICT,
        )
    user.email = record.new_email_normalized
    record.used_at = datetime.now(timezone.utc)
    db.add(user)
    log_security_event(db, request, event_type="email_change_completed", user_id=user.id, details="confirmed")
    db.commit()
    response = redirect("/me?message=email_changed")
    set_auth_cookie(
        response,
        create_access_token(user.user_uid, user.role, password_token_fingerprint(user.hashed_password)),
    )
    return response


@router.get("/me")
def me_page(
    request: Request,
    message: str = "",
    current_user: User = Depends(get_current_user),
):
    message_map = {
        "username_updated": t("profile.username_updated", request=request),
        "password_changed": t("auth.password_changed_success", request=request),
        "email_changed": t("auth.email_change_success", request=request),
    }
    return _render_me(request, current_user, message=message_map.get(message, ""))


@router.get("/api/me")
def me_api(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "user_uid": current_user.user_uid,
        "email": current_user.email,
        "username": current_user.username,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat(),
        "last_login_at": current_user.last_login_at.isoformat() if current_user.last_login_at else None,
    }


@router.get("/admin-only")
def admin_only(request: Request, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=t("error.admin_required", request=request))
    return {"message": t("role.admin", request=request)}

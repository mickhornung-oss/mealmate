from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import re
import secrets

from jose import JWTError, jwt
from pwdlib import PasswordHash

from app.config import get_settings
from app.i18n import t

password_hash = PasswordHash.recommended()
settings = get_settings()
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]{3,30}$")


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def validate_password_policy(password: str) -> str | None:
    if len(password) < 10:
        return t("error.password_min_length")
    if not re.search(r"[A-Z]", password):
        return t("error.password_upper")
    if not re.search(r"\d", password):
        return t("error.password_number")
    if not re.search(r"[^A-Za-z0-9]", password):
        return t("error.password_special")
    return None


def normalize_username(username: str) -> str:
    return username.strip().lower()


def validate_username_policy(username: str) -> str | None:
    trimmed = username.strip()
    if not USERNAME_PATTERN.fullmatch(trimmed):
        return t("error.username_invalid")
    return None


def create_raw_reset_token() -> str:
    return secrets.token_urlsafe(48)


def hash_reset_token(raw_token: str) -> str:
    secret = settings.secret_key.encode("utf-8")
    payload = raw_token.encode("utf-8")
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def password_token_fingerprint(hashed_password: str) -> str:
    secret = settings.secret_key.encode("utf-8")
    payload = hashed_password.encode("utf-8")
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()[:24]


def create_access_token(subject: str, role: str, password_fingerprint: str | None = None) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.token_expire_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    if password_fingerprint:
        payload["pwdv"] = password_fingerprint
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, str]:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

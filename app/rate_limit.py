from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.requests import Request

from app.security import decode_access_token
from app.services import extract_token


def key_by_ip(request: Request) -> str:
    return get_remote_address(request)


def key_by_user_or_ip(request: Request) -> str:
    state_user_key = getattr(request.state, "rate_limit_user_key", None)
    if state_user_key:
        return str(state_user_key)
    token = extract_token(request.cookies.get("access_token"))
    if not token:
        token = extract_token(request.headers.get("Authorization"))
    if token:
        try:
            payload = decode_access_token(token)
            subject = str(payload.get("sub", "")).strip().lower()
            if subject:
                return f"user:{subject}"
        except ValueError:
            pass
    return key_by_ip(request)


limiter = Limiter(key_func=key_by_ip, headers_enabled=True)

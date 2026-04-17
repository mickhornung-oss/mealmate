from __future__ import annotations

import html
import io
import re
from functools import lru_cache
from urllib.parse import unquote, urlparse
from urllib.request import Request, urlopen

from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import services as legacy_services
from app.models import AppMeta, Recipe, User

settings = legacy_services.settings


def validate_upload(content_type: str, file_size_bytes: int, file_bytes: bytes | None = None) -> None:
    if content_type not in settings.allowed_image_types:
        raise ValueError(f"Unsupported MIME type '{content_type}'.")
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if file_size_bytes > max_bytes:
        raise ValueError(f"Image too large. Max size is {settings.max_upload_mb} MB.")
    if file_bytes is not None:
        try:
            with Image.open(io.BytesIO(file_bytes)) as image:
                image.verify()
        except (UnidentifiedImageError, OSError) as exc:
            raise ValueError("Uploaded file is not a valid image.") from exc


@lru_cache(maxsize=4096)
def resolve_title_image_url(image_url: str) -> str | None:
    cleaned = image_url.strip()
    if not cleaned:
        return None
    lower = cleaned.lower()
    if "kein_bild" in lower:
        return None
    if lower.endswith((".jpg", ".jpeg", ".png", ".webp")) and "/wiki/" not in lower:
        return cleaned
    parsed = urlparse(cleaned)
    host = parsed.netloc.lower()
    path = unquote(parsed.path).lower()
    if "kochwiki.org" in host and "/wiki/" in parsed.path and "datei" in path:
        request = Request(cleaned, headers={"User-Agent": "MealMate/1.0"})
        with urlopen(request, timeout=12) as response:
            html_text = response.read(300_000).decode("utf-8", errors="ignore")
        match = re.search(
            r'<meta\s+property=["\']og:image["\']\s+content=["\']([^"\']+)["\']',
            html_text,
            flags=re.IGNORECASE,
        )
        if match:
            return html.unescape(match.group(1))
    return cleaned


def extract_token(raw_header: str | None) -> str | None:
    if not raw_header:
        return None
    prefix = "Bearer "
    if raw_header.startswith(prefix):
        return raw_header[len(prefix) :].strip()
    return raw_header.strip()


def can_manage_recipe(current_user: User, recipe: Recipe) -> bool:
    return current_user.role == "admin" or recipe.creator_id == current_user.id


def get_meta_value(db: Session, key: str) -> str | None:
    meta = db.scalar(select(AppMeta).where(AppMeta.key == key))
    return meta.value if meta else None


def set_meta_value(db: Session, key: str, value: str) -> None:
    meta = db.scalar(select(AppMeta).where(AppMeta.key == key))
    if not meta:
        db.add(AppMeta(key=key, value=value))
        return
    meta.value = value


def is_meta_true(db: Session, key: str) -> bool:
    return get_meta_value(db, key) == "1"


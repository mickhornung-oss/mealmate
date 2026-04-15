import io
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from app.config import get_settings
from app.i18n import t

settings = get_settings()

MAGIC_SIGNATURES = {
    "image/jpeg": [b"\xff\xd8\xff"],
    "image/png": [b"\x89PNG\r\n\x1a\n"],
    "image/webp": [b"RIFF"],
}


class ImageValidationError(ValueError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.status_code = status_code


def _validate_magic_bytes(content_type: str, file_bytes: bytes) -> None:
    signatures = MAGIC_SIGNATURES.get(content_type, [])
    if not signatures:
        raise ImageValidationError(t("error.mime_unsupported", content_type=content_type))
    if content_type == "image/webp":
        if not (file_bytes.startswith(b"RIFF") and file_bytes[8:12] == b"WEBP"):
            raise ImageValidationError(t("error.webp_signature"))
        return
    if not any(file_bytes.startswith(sig) for sig in signatures):
        raise ImageValidationError(t("error.magic_mismatch"))


def _validate_image_decode(content_type: str, file_bytes: bytes) -> None:
    expected_format = {
        "image/jpeg": "JPEG",
        "image/png": "PNG",
        "image/webp": "WEBP",
    }.get(content_type)
    try:
        with Image.open(io.BytesIO(file_bytes)) as image:
            image.verify()
            actual_format = (image.format or "").upper()
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ImageValidationError(t("error.image_invalid")) from exc
    if expected_format and actual_format != expected_format:
        raise ImageValidationError(t("error.image_format_mismatch"))


def safe_image_filename(original_filename: str, content_type: str) -> str:
    extension = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }.get(content_type, "")
    clean_name = Path(original_filename or "").name
    if not extension:
        extension = Path(clean_name).suffix.lower()
    return f"{uuid4().hex}{extension[:10]}"


def validate_image_upload(content_type: str, file_bytes: bytes) -> None:
    if content_type not in settings.allowed_image_types:
        raise ImageValidationError(t("error.mime_unsupported", content_type=content_type))
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ImageValidationError(t("error.image_too_large", max_mb=settings.max_upload_mb), status_code=413)
    if len(file_bytes) < 12:
        raise ImageValidationError(t("error.image_too_small"))
    _validate_magic_bytes(content_type, file_bytes)
    _validate_image_decode(content_type, file_bytes)

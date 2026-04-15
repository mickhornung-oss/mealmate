from __future__ import annotations

import importlib
import secrets
import time
from typing import Any, Protocol

import httpx

from app.config import Settings


TERMINAL_STATUSES = {"completed", "failed", "cancelled", "timeout"}


class TranslationProviderError(RuntimeError):
    pass


class TranslationProvider(Protocol):
    def translate(self, text: str, targets: list[str], *, source_lang: str) -> dict[str, str]:
        ...


def _normalize_lang(value: str) -> str:
    token = str(value or "").strip().lower().replace("_", "-")
    if not token:
        return ""
    return token.split("-", 1)[0]


def _normalize_targets(targets: list[str], source_lang: str) -> list[str]:
    normalized: list[str] = []
    source = _normalize_lang(source_lang)
    for value in targets:
        lang = _normalize_lang(value)
        if not lang or lang == source:
            continue
        if lang not in normalized:
            normalized.append(lang)
    return normalized


def _unwrap_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    return payload


def _extract_job_id(payload: Any) -> str:
    top = _unwrap_payload(payload)
    candidates = [
        top.get("job_id"),
        top.get("id"),
        payload.get("job_id") if isinstance(payload, dict) else None,
        payload.get("id") if isinstance(payload, dict) else None,
    ]
    job_obj = top.get("job") if isinstance(top, dict) else None
    if isinstance(job_obj, dict):
        candidates.extend([job_obj.get("job_id"), job_obj.get("id")])
    for candidate in candidates:
        token = str(candidate or "").strip()
        if token:
            return token
    raise TranslationProviderError("TranslateAPI batch response did not include a job_id.")


def _normalize_status(value: Any) -> str:
    token = str(value or "").strip().lower()
    if token in {"queued", "pending"}:
        return "queued"
    if token in {"running", "processing", "in_progress", "started"}:
        return "running"
    if token in {"done", "success", "successful", "completed"}:
        return "completed"
    if token in {"cancelled", "canceled"}:
        return "cancelled"
    if token in {"error", "failed"}:
        return "failed"
    if token:
        return token
    return "queued"


def _extract_items(payload: Any) -> list[dict[str, Any]]:
    top = _unwrap_payload(payload)
    if not isinstance(top, dict):
        return []
    for key in ("results", "items", "translations"):
        value = top.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def _extract_target_lang(item: dict[str, Any], fallback: str = "") -> str:
    candidates = [
        item.get("target_lang"),
        item.get("target_language"),
        item.get("language"),
        item.get("lang"),
    ]
    for candidate in candidates:
        lang = _normalize_lang(str(candidate or ""))
        if lang:
            return lang
    return _normalize_lang(fallback)


def _extract_translated_text(item: dict[str, Any]) -> str:
    direct_candidates = [
        item.get("translated_text"),
        item.get("translation"),
        item.get("text"),
        item.get("result"),
        item.get("output"),
    ]
    for candidate in direct_candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    nested_candidates = [
        item.get("translated_payload"),
        item.get("payload"),
        item.get("content"),
    ]
    for candidate in nested_candidates:
        if isinstance(candidate, dict):
            text_value = candidate.get("text")
            if isinstance(text_value, str) and text_value.strip():
                return text_value.strip()
    return ""


class TranslateApiTranslationProvider:
    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        poll_interval_seconds: int = 3,
        max_polls: int = 200,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.base_url = str(base_url).rstrip("/")
        self.api_key = str(api_key or "").strip()
        self.poll_interval_seconds = max(0, int(poll_interval_seconds))
        self.max_polls = max(1, int(max_polls))
        self.timeout_seconds = max(1.0, float(timeout_seconds))
        if not self.api_key:
            raise TranslationProviderError("TRANSLATEAPI_API_KEY is required for TRANSLATION_PROVIDER=translateapi.")

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _submit_batch(self, text: str, source_lang: str, targets: list[str]) -> tuple[str, dict[str, str]]:
        ext_to_lang: dict[str, str] = {}
        items: list[dict[str, Any]] = []
        for target in targets:
            external_id = f"inline-{target}-{secrets.token_hex(8)}"
            ext_to_lang[external_id] = target
            items.append(
                {
                    "external_id": external_id,
                    "source_language": source_lang,
                    "source_lang": source_lang,
                    "target_language": target,
                    "target_lang": target,
                    "text": text,
                    "payload": {"text": text},
                    "content": {"text": text},
                }
            )
        endpoint = f"{self.base_url}/translate/batch/"
        payload = {
            "items": items,
            "source_language": source_lang,
            "target_languages": targets,
        }
        with httpx.Client(timeout=self.timeout_seconds) as client:
            response = client.post(endpoint, headers=self._headers(), json=payload)
        response.raise_for_status()
        data = response.json()
        return _extract_job_id(data), ext_to_lang

    def _poll_job(self, job_id: str) -> dict[str, Any]:
        endpoint = f"{self.base_url}/jobs/{job_id}/"
        with httpx.Client(timeout=self.timeout_seconds) as client:
            for _ in range(self.max_polls):
                response = client.get(endpoint, headers=self._headers())
                response.raise_for_status()
                payload = response.json()
                status = _normalize_status(_unwrap_payload(payload).get("status"))
                if status in TERMINAL_STATUSES:
                    return payload
                if self.poll_interval_seconds > 0:
                    time.sleep(self.poll_interval_seconds)
        return {"status": "timeout", "results": []}

    def translate(self, text: str, targets: list[str], *, source_lang: str) -> dict[str, str]:
        requested_targets = _normalize_targets(targets, source_lang)
        if not requested_targets:
            return {}
        normalized_text = str(text or "").strip()
        if not normalized_text:
            return {lang: "" for lang in requested_targets}

        job_id, ext_to_lang = self._submit_batch(normalized_text, _normalize_lang(source_lang), requested_targets)
        payload = self._poll_job(job_id)
        status = _normalize_status(_unwrap_payload(payload).get("status"))
        if status != "completed":
            raise TranslationProviderError(f"TranslateAPI job failed with status='{status}'.")

        results: dict[str, str] = {lang: normalized_text for lang in requested_targets}
        for item in _extract_items(payload):
            external_id = str(item.get("external_id") or item.get("id") or "").strip()
            mapped_lang = ext_to_lang.get(external_id, "")
            target_lang = _extract_target_lang(item, fallback=mapped_lang)
            if not target_lang:
                continue
            translated = _extract_translated_text(item)
            if translated:
                results[target_lang] = translated
        return results


class GoogleTranslatorsTranslationProvider:
    def __init__(self) -> None:
        self._module = None

    def _load_module(self):
        if self._module is None:
            try:
                self._module = importlib.import_module("translators")
            except Exception as exc:
                raise TranslationProviderError(
                    "Python package 'translators' is required for TRANSLATION_PROVIDER=google_translators."
                ) from exc
        return self._module

    def translate(self, text: str, targets: list[str], *, source_lang: str) -> dict[str, str]:
        requested_targets = _normalize_targets(targets, source_lang)
        if not requested_targets:
            return {}
        normalized_text = str(text or "").strip()
        if not normalized_text:
            return {lang: "" for lang in requested_targets}

        module = self._load_module()
        output: dict[str, str] = {}
        for lang in requested_targets:
            translated = module.translate_text(
                normalized_text,
                translator="google",
                from_language=_normalize_lang(source_lang),
                to_language=lang,
            )
            output[lang] = str(translated or "").strip()
        return output


def resolve_translation_provider(settings: Settings) -> TranslationProvider:
    provider_name = str(settings.translation_provider or "translateapi").strip().lower()
    if provider_name == "google_translators":
        return GoogleTranslatorsTranslationProvider()
    return TranslateApiTranslationProvider(
        base_url=settings.translateapi_base_url,
        api_key=settings.translateapi_api_key or "",
        poll_interval_seconds=settings.translateapi_poll_interval_seconds,
        max_polls=settings.translateapi_max_polls,
    )

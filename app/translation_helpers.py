from __future__ import annotations

import re
from typing import Any

DE_STOPWORDS = {
    "und",
    "der",
    "die",
    "das",
    "mit",
    "fuer",
    "bei",
    "oder",
    "ein",
    "eine",
    "nicht",
    "zum",
    "zur",
    "auf",
    "im",
    "in",
    "aus",
    "als",
    "dann",
    "danach",
    "geben",
    "nehmen",
    "ruehren",
}
EN_STOPWORDS = {
    "the",
    "and",
    "with",
    "for",
    "from",
    "into",
    "in",
    "on",
    "then",
    "add",
    "stir",
    "cook",
    "serve",
    "minutes",
    "heat",
}
EN_MARKERS = ("serve", "heat", "stir", "add", "cook", "minutes")
TOKEN_PATTERN = re.compile(r"[a-zA-Z]+")


def _normalize_word(value: str) -> str:
    return (
        str(value or "")
        .strip()
        .lower()
        .replace("\u00e4", "ae")
        .replace("\u00f6", "oe")
        .replace("\u00fc", "ue")
        .replace("\u00df", "ss")
    )


def _tokenize_text(text: str) -> list[str]:
    return [_normalize_word(token) for token in TOKEN_PATTERN.findall(str(text or "")) if token.strip()]


def _score_stopwords(tokens: list[str], stopwords: set[str]) -> float:
    if not tokens:
        return 0.0
    hits = sum(1 for token in tokens if token in stopwords)
    return hits / max(len(tokens), 1)


def is_probably_english(text: str) -> bool:
    tokens = _tokenize_text(text)
    english_score = _score_stopwords(tokens, EN_STOPWORDS)
    marker_hits = sum(1 for marker in EN_MARKERS if marker in _normalize_word(text))
    return english_score >= 0.06 or marker_hits >= 2


def is_probably_german(text: str) -> bool:
    tokens = _tokenize_text(text)
    german_score = _score_stopwords(tokens, DE_STOPWORDS)
    umlaut_hint = any(char in str(text or "").lower() for char in ("\u00e4", "\u00f6", "\u00fc", "\u00df"))
    return german_score >= 0.02 or umlaut_hint


def _analyze_de_translation_language(title: str, instructions: str) -> tuple[bool, float, float, int, str]:
    combined = f"{title or ''}\n{instructions or ''}".strip()
    normalized_text = _normalize_word(combined)
    tokens = _tokenize_text(combined)
    english_score = _score_stopwords(tokens, EN_STOPWORDS)
    german_score = _score_stopwords(tokens, DE_STOPWORDS)
    marker_hits = sum(1 for marker in EN_MARKERS if marker in normalized_text)
    suspect = (english_score >= 0.06 and german_score <= 0.02) or marker_hits >= 2
    reason_parts: list[str] = []
    if english_score >= 0.06 and german_score <= 0.02:
        reason_parts.append("english_stopword_bias")
    if marker_hits >= 2:
        reason_parts.append("english_markers")
    if not reason_parts:
        reason_parts.append("looks_german" if not suspect else "unclear")
    return suspect, english_score, german_score, marker_hits, ",".join(reason_parts)


def _unwrap_payload(payload: Any) -> dict[str, Any]:
    if not isinstance(payload, dict):
        return {}
    data = payload.get("data")
    if isinstance(data, dict):
        return data
    return payload


def _extract_job_id(payload: Any) -> str | None:
    top = _unwrap_payload(payload)
    candidates = [
        top.get("job_id"),
        top.get("id"),
        payload.get("job_id") if isinstance(payload, dict) else None,
        payload.get("id") if isinstance(payload, dict) else None,
    ]
    job_node = top.get("job") if isinstance(top, dict) else None
    if isinstance(job_node, dict):
        candidates.extend([job_node.get("job_id"), job_node.get("id")])
    for value in candidates:
        token = str(value or "").strip()
        if token:
            return token
    return None


def _normalize_job_status(value: Any) -> str:
    token = str(value or "").strip().lower()
    if token in {"queued", "pending"}:
        return "queued"
    if token in {"running", "processing", "in_progress", "started"}:
        return "running"
    if token in {"done", "success", "successful", "completed"}:
        return "completed"
    if token in {"error", "failed"}:
        return "failed"
    if token in {"cancelled", "canceled"}:
        return "cancelled"
    if token:
        return token
    return "queued"


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _extract_progress(payload: Any, total_default: int = 0, completed_default: int = 0) -> tuple[int, int]:
    top = _unwrap_payload(payload)
    progress = top.get("progress") if isinstance(top, dict) else None
    if isinstance(progress, dict):
        total = _to_int(progress.get("total"), total_default)
        completed = _to_int(progress.get("completed"), completed_default)
        return max(total, 0), max(completed, 0)
    total = _to_int(top.get("total"), total_default) if isinstance(top, dict) else total_default
    completed = _to_int(top.get("completed"), completed_default) if isinstance(top, dict) else completed_default
    return max(total, 0), max(completed, 0)


def _extract_errors(payload: Any) -> list[str]:
    top = _unwrap_payload(payload)
    raw_errors = []
    if isinstance(top, dict):
        if isinstance(top.get("errors"), list):
            raw_errors = top["errors"]
        elif top.get("error"):
            raw_errors = [top.get("error")]
    messages: list[str] = []
    for item in raw_errors:
        if isinstance(item, str) and item.strip():
            messages.append(item.strip())
            continue
        if isinstance(item, dict):
            text = str(item.get("message") or item.get("detail") or "").strip()
            if text:
                messages.append(text)
    return messages


def _extract_result_items(payload: Any) -> list[dict[str, Any]]:
    top = _unwrap_payload(payload)
    if not isinstance(top, dict):
        return []
    for key in ("results", "items", "translations"):
        raw = top.get(key)
        if isinstance(raw, list):
            return [item for item in raw if isinstance(item, dict)]
    return []

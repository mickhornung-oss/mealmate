from __future__ import annotations

from pathlib import Path


def test_env_example_contains_runtime_and_security_baseline_keys():
    env_path = Path(".env.example")
    content = env_path.read_text(encoding="utf-8")
    required_keys = [
        "APP_ENV=",
        "APP_URL=",
        "SECRET_KEY=",
        "DATABASE_URL=",
        "ALLOWED_HOSTS=",
        "COOKIE_SECURE=",
        "FORCE_HTTPS=",
        "PORT=",
        "WEB_CONCURRENCY=",
        "WEB_TIMEOUT=",
        "TRANSLATEAPI_ENABLED=",
        "TRANSLATEAPI_API_KEY=",
    ]
    for key in required_keys:
        assert key in content


def test_operability_doc_references_conflict_event_contracts():
    doc_path = Path("docs/development/OPERABILITY.md")
    content = doc_path.read_text(encoding="utf-8")
    expected_markers = [
        "translation_batch_start_conflict",
        "submission_reject_replay",
        "image_change_transition_conflict",
        "X-Request-ID",
        "409",
    ]
    for marker in expected_markers:
        assert marker in content

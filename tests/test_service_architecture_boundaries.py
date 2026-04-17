from __future__ import annotations

import app.services as services
import app.services_runtime as services_runtime
import app.services_submission as services_submission
import app.translation_batch_service as translation_batch_service
import app.translation_service as translation_service


def test_services_runtime_entrypoint_delegates(monkeypatch):
    monkeypatch.setattr(services_runtime, "extract_token", lambda raw: f"delegated:{raw}")
    assert services.extract_token("Bearer abc") == "delegated:Bearer abc"


def test_services_submission_entrypoint_delegates(monkeypatch):
    monkeypatch.setattr(services_submission, "get_submission_status_stats", lambda db: {"pending": 7})
    assert services.get_submission_status_stats(object()) == {"pending": 7}


def test_translation_batch_entrypoint_delegates(monkeypatch):
    monkeypatch.setattr(translation_batch_service, "_build_batch_external_id", lambda recipe_id, language, source_hash: "x-id")
    assert translation_service._build_batch_external_id(10, "en", "hash-value") == "x-id"


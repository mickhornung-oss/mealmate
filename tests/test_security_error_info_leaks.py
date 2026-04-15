from __future__ import annotations

from fastapi import Response
from fastapi.testclient import TestClient

from app.main import app
from app.main import settings as app_settings


_BOOM_PATH = "/__test/boom-500"


def _ensure_boom_route() -> None:
    existing = {route.path for route in app.routes}
    if _BOOM_PATH in existing:
        return

    @app.get(_BOOM_PATH)
    def _boom() -> Response:
        raise RuntimeError("forced test exception")


def _assert_no_sensitive_leak(payload: str) -> None:
    lowered = payload.lower()
    forbidden_markers = [
        "traceback",
        "sqlalchemy",
        "sqlite",
        "select ",
        "insert into",
        "c:\\",
        "/users/",
        "secret_key",
        "token=",
        "password",
    ]
    for marker in forbidden_markers:
        assert marker not in lowered


def _set_prod_runtime(monkeypatch):
    previous_env = app_settings.app_env
    previous_debug = app.debug
    monkeypatch.setattr(app_settings, "app_env", "prod")
    app.debug = False
    return previous_env, previous_debug


def _restore_runtime(monkeypatch, previous_env: str, previous_debug: bool):
    monkeypatch.setattr(app_settings, "app_env", previous_env)
    app.debug = previous_debug


def test_force_500_json_does_not_leak_sensitive_info_in_prod(monkeypatch):
    _ensure_boom_route()
    previous_env, previous_debug = _set_prod_runtime(monkeypatch)
    try:
        with TestClient(app, raise_server_exceptions=False) as local_client:
            response = local_client.get(_BOOM_PATH, headers={"accept": "application/json"})
        assert response.status_code == 500
        body = response.text
        _assert_no_sensitive_leak(body)
        assert "trace" not in body.lower()
        assert "detail" in body.lower()
    finally:
        _restore_runtime(monkeypatch, previous_env, previous_debug)


def test_force_500_html_does_not_leak_stacktrace_in_prod(monkeypatch):
    _ensure_boom_route()
    previous_env, previous_debug = _set_prod_runtime(monkeypatch)
    try:
        with TestClient(app, raise_server_exceptions=False) as local_client:
            response = local_client.get(_BOOM_PATH, headers={"accept": "text/html"})
        assert response.status_code == 500
        assert "text/html" in (response.headers.get("content-type") or "").lower()
        _assert_no_sensitive_leak(response.text)
    finally:
        _restore_runtime(monkeypatch, previous_env, previous_debug)


def test_prod_mode_flag_is_enabled_when_env_is_prod(monkeypatch):
    previous_env, previous_debug = _set_prod_runtime(monkeypatch)
    try:
        assert app_settings.prod_mode is True
        assert app.debug is False
    finally:
        _restore_runtime(monkeypatch, previous_env, previous_debug)


def test_security_headers_present_on_error_response(monkeypatch):
    _ensure_boom_route()
    previous_env, previous_debug = _set_prod_runtime(monkeypatch)
    try:
        with TestClient(app, raise_server_exceptions=False) as local_client:
            response = local_client.get(_BOOM_PATH, headers={"accept": "application/json"})
        assert response.status_code == 500
        headers = {key.lower(): value for key, value in response.headers.items()}
        assert "content-security-policy" in headers
        assert "x-frame-options" in headers
        assert "x-content-type-options" in headers
        assert "referrer-policy" in headers
        assert "permissions-policy" in headers
    finally:
        _restore_runtime(monkeypatch, previous_env, previous_debug)

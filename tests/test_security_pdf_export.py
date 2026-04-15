from __future__ import annotations

import socket

from tests.helpers import create_admin_user, create_published_recipe, post_form, unique_email


def _login(client, email: str, password: str) -> None:
    response = post_form(
        client,
        "/login",
        data={"identifier": email, "password": password},
        referer_page="/login",
        follow_redirects=False,
    )
    assert response.status_code in {302, 303}


def test_pdf_export_is_rate_limited_under_abuse(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("pdf-rate-admin"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="PDF Rate Test")
        admin_email = admin.email
        recipe_id = recipe.id

    _login(client, admin_email, "AdminPass123!")

    statuses = []
    for _ in range(40):
        response = client.get(f"/recipes/{recipe_id}/pdf")
        statuses.append(response.status_code)

    assert 200 in statuses
    assert 429 in statuses


def test_pdf_export_handles_very_long_recipe_text_without_crash(client, db_session_factory):
    huge_text = " ".join(["Schritt"] * 12000)
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("pdf-long-admin"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="PDF Long Text")
        recipe.description = huge_text
        recipe.instructions = "\n".join([huge_text] * 5)
        db.add(recipe)
        db.commit()
        admin_email = admin.email
        recipe_id = recipe.id

    _login(client, admin_email, "AdminPass123!")

    response = client.get(f"/recipes/{recipe_id}/pdf")
    assert response.status_code == 200
    assert "application/pdf" in (response.headers.get("content-type") or "").lower()
    assert response.content.startswith(b"%PDF")


def test_pdf_export_does_not_fetch_external_or_internal_network_urls(client, db_session_factory, monkeypatch):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("pdf-ssrf-admin"), "AdminPass123!")
        recipe = create_published_recipe(db, admin.id, title="PDF SSRF Test")
        recipe.source_image_url = "http://169.254.169.254/latest/meta-data/"
        recipe.title_image_url = "http://127.0.0.1:80/private"
        db.add(recipe)
        db.commit()
        admin_email = admin.email
        recipe_id = recipe.id

    _login(client, admin_email, "AdminPass123!")

    calls: list[tuple] = []
    original_create_connection = socket.create_connection

    def _guarded_create_connection(address, *args, **kwargs):
        calls.append((address, args, kwargs))
        host = str(address[0]) if isinstance(address, tuple) and address else ""
        if host in {"127.0.0.1", "169.254.169.254", "localhost"}:
            raise AssertionError(f"Unexpected network call during PDF export: {address}")
        return original_create_connection(address, *args, **kwargs)

    monkeypatch.setattr(socket, "create_connection", _guarded_create_connection)

    response = client.get(f"/recipes/{recipe_id}/pdf")
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
    assert calls == []

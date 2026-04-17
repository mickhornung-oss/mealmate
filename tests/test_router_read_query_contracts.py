from __future__ import annotations

from tests.helpers import (
    create_admin_user,
    create_normal_user,
    create_pending_submission,
    create_published_recipe,
    set_auth_cookie,
    unique_email,
)


def test_home_query_contract_normalizes_per_page_and_image_filter(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("read-home-admin"), "AdminPass123!")
        create_published_recipe(db, admin.id, title="Read Contract Recipe", is_published=True)

    response = client.get("/?per_page=13&image_filter=invalid-value")
    assert response.status_code == 200
    assert '<option value="20" selected' in response.text
    assert 'select name="image_filter"' in response.text
    assert '<option value="with_image" selected' not in response.text


def test_home_query_contract_clamps_page_to_last_page(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("read-page-admin"), "AdminPass123!")
        for index in range(21):
            create_published_recipe(
                db,
                admin.id,
                title=f"Read Paging Recipe {index:02d}",
                is_published=True,
            )

    response = client.get("/?per_page=20&page=999")
    assert response.status_code == 200
    assert "2 / 2" in response.text


def test_admin_submissions_invalid_status_filter_defaults_to_pending(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("read-sub-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("read-sub-user"), "UserPass123!")
        pending = create_pending_submission(db, user.id, "Read Pending Submission")
        approved = create_pending_submission(db, user.id, "Read Approved Submission")
        approved.status = "approved"
        db.commit()
        db.refresh(pending)
        db.refresh(approved)
        set_auth_cookie(client, admin.user_uid, admin.role)

    response = client.get("/admin/submissions?status_filter=INVALID")
    assert response.status_code == 200
    assert 'option value="pending" selected' in response.text
    assert "Read Pending Submission" in response.text
    assert "Read Approved Submission" not in response.text


def test_admin_submissions_page_contract_clamps_to_last_page(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("read-sub-page-admin"), "AdminPass123!")
        user = create_normal_user(db, unique_email("read-sub-page-user"), "UserPass123!")
        for index in range(21):
            create_pending_submission(db, user.id, f"Paged Submission {index:02d}")
        set_auth_cookie(client, admin.user_uid, admin.role)

    response = client.get("/admin/submissions?status_filter=pending&page=999")
    assert response.status_code == 200
    assert "2 / 2" in response.text


def test_admin_translations_read_query_contract_builds_report_and_batch_message(client, db_session_factory):
    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("read-trans-admin"), "AdminPass123!")
        set_auth_cookie(client, admin.user_uid, admin.role)

    response = client.get(
        "/admin/translations"
        "?mode=stale"
        "&processed=1"
        "&created=2"
        "&updated=3"
        "&skipped=4"
        "&errors=5"
        "&batch_started=1"
        "&batch_job=job-read-123"
    )
    assert response.status_code == 200
    assert "Batch-Job gestartet (ID: job-read-123)." in response.text
    assert "Modus: stale" in response.text
    assert "Verarbeitete Rezepte: 1" in response.text
    assert "Neu erstellt: 2" in response.text
    assert "Aktualisiert: 3" in response.text
    assert "Übersprungen: 4" in response.text
    assert "Fehler: 5" in response.text

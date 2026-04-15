from __future__ import annotations

import re

from sqlalchemy import select

from app.models import Recipe, RecipeSubmission
from tests.helpers import create_admin_user, create_normal_user, post_form, set_auth_cookie, unique_email


MOJIBAKE_MARKERS = ("Ã", "Â", "â€", "\ufffd")
I18N_KEY_PREFIXES = (
    "nav.",
    "home.",
    "discover.",
    "submission.",
    "auth.",
    "pagination.",
    "error.",
    "recipe.",
    "admin.",
    "moderation.",
    "images.",
    "image_change.",
)
ALLOWED_DOTTED_TOKENS = {"127.0.0.1", "localhost"}
I18N_TOKEN_RE = re.compile(r"\b[a-z_]+\.[a-z_]+(?:\.[a-z_]+)?\b")


def _assert_no_mojibake(text: str) -> None:
    assert not any(marker in text for marker in MOJIBAKE_MARKERS), "Detected mojibake marker in HTML response."


def _assert_no_key_leaks(text: str) -> None:
    for prefix in I18N_KEY_PREFIXES:
        assert prefix not in text, f"Detected i18n key leak prefix '{prefix}' in HTML response."
    leaked_tokens = {
        token
        for token in I18N_TOKEN_RE.findall(text)
        if token not in ALLOWED_DOTTED_TOKENS and any(token.startswith(prefix) for prefix in I18N_KEY_PREFIXES)
    }
    assert not leaked_tokens, f"Detected i18n key leaks: {sorted(leaked_tokens)}"


def test_i18n_umlauts_rendered_and_keys_hidden(client, db_session_factory):
    response_home = client.get("/?lang=de")
    assert response_home.status_code == 200
    assert "charset=utf-8" in response_home.headers.get("content-type", "").lower()
    assert "Rezepte entdecken" in response_home.text
    assert "Zurücksetzen" in response_home.text
    assert "home.hero_title" not in response_home.text
    assert "HOME.HERO_EYEBROW" not in response_home.text
    _assert_no_mojibake(response_home.text)
    _assert_no_key_leaks(response_home.text)

    response_login = client.get("/login?lang=de")
    assert response_login.status_code == 200
    assert "Passwort vergessen?" in response_login.text
    assert "home.hero_title" not in response_login.text
    _assert_no_mojibake(response_login.text)
    _assert_no_key_leaks(response_login.text)

    response_register = client.get("/register?lang=de")
    assert response_register.status_code == 200
    assert "Registrieren" in response_register.text
    assert "home.hero_title" not in response_register.text
    _assert_no_mojibake(response_register.text)
    _assert_no_key_leaks(response_register.text)

    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("umlaut-admin"), "AdminPass123!")
    set_auth_cookie(client, admin.user_uid, admin.role)
    response_admin = client.get("/admin?lang=de")
    assert response_admin.status_code == 200
    assert "Rezept-Übersetzungen" in response_admin.text
    assert "home.hero_title" not in response_admin.text
    _assert_no_mojibake(response_admin.text)
    _assert_no_key_leaks(response_admin.text)

    response_admin_translations = client.get("/admin/translations/run?lang=de")
    assert response_admin_translations.status_code == 200
    assert "Admin: Rezept-Übersetzungen" in response_admin_translations.text
    _assert_no_mojibake(response_admin_translations.text)
    _assert_no_key_leaks(response_admin_translations.text)


def test_full_flow_umlaut_user_submission_and_approval(client, db_session_factory):
    user_email = unique_email("joerg")
    user_password = "UserPass123!"
    recipe_title = "Käsekuchen mit Äpfeln"
    recipe_description = "Öl erhitzen und die Äpfel über Nacht ziehen lassen."
    recipe_instructions = "Öl erhitzen.\nÜber Nacht ziehen lassen.\nZum Schluss süßen."

    with db_session_factory() as db:
        admin = create_admin_user(db, unique_email("approver-admin"), "AdminPass123!")
        user = create_normal_user(db, user_email, user_password)
        user.username = "Jörg_ÄÖÜ"
        user.username_normalized = "jörg_äöü"
        db.add(user)
        db.commit()
        db.refresh(user)
        admin_uid = admin.user_uid
        admin_role = admin.role

    login_response = post_form(
        client,
        "/login",
        {"identifier": user_email, "password": user_password},
        referer_page="/login",
        follow_redirects=False,
    )
    assert login_response.status_code in {302, 303}

    profile_response = client.get("/me?lang=de")
    assert profile_response.status_code == 200
    assert "Jörg_ÄÖÜ" in profile_response.text

    submit_response = post_form(
        client,
        "/submit",
        {
            "title": recipe_title,
            "description": recipe_description,
            "instructions": recipe_instructions,
            "difficulty": "easy",
            "category_select": "Dessert",
            "prep_time_minutes": "35",
            "servings_text": "4",
            "ingredients_text": "200g Mehl\n3 Äpfel\n1 TL Öl",
        },
        referer_page="/submit",
        follow_redirects=False,
    )
    assert submit_response.status_code in {302, 303}

    my_submissions_response = client.get("/my-submissions?lang=de")
    assert my_submissions_response.status_code == 200
    assert recipe_title in my_submissions_response.text
    assert "Ausstehend" in my_submissions_response.text

    discover_before_approve = client.get("/?lang=de")
    assert discover_before_approve.status_code == 200
    assert recipe_title not in discover_before_approve.text

    with db_session_factory() as db:
        submission = db.scalar(select(RecipeSubmission).where(RecipeSubmission.title == recipe_title))
        assert submission is not None
        submission_id = int(submission.id)

    set_auth_cookie(client, admin_uid, admin_role)
    approve_response = post_form(
        client,
        f"/admin/submissions/{submission_id}/approve",
        {"admin_note": "Freigabe mit Umlaut-Prüfung."},
        referer_page=f"/admin/submissions/{submission_id}",
        follow_redirects=False,
    )
    assert approve_response.status_code in {302, 303}

    with db_session_factory() as db:
        published_recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == f"submission:{submission_id}"))
        assert published_recipe is not None
        published_recipe_id = int(published_recipe.id)

    discover_after_approve = client.get("/?lang=de")
    assert discover_after_approve.status_code == 200
    assert recipe_title in discover_after_approve.text
    _assert_no_mojibake(discover_after_approve.text)
    _assert_no_key_leaks(discover_after_approve.text)

    detail_response = client.get(f"/recipes/{published_recipe_id}?lang=de")
    assert detail_response.status_code == 200
    assert recipe_title in detail_response.text
    assert "Öl erhitzen" in detail_response.text
    assert "Über Nacht ziehen lassen" in detail_response.text
    assert "süßen" in detail_response.text
    _assert_no_mojibake(detail_response.text)
    _assert_no_key_leaks(detail_response.text)

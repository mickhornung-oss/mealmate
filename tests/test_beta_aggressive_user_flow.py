from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from sqlalchemy import and_, select

from app.config import get_settings
from app.models import RecipeImageChangeRequest, RecipeSubmission, User
from tests.helpers import (
    SMALL_PNG_BYTES,
    create_admin_user,
    create_published_recipe,
    extract_token_from_link,
    post_form,
    read_last_link,
    unique_email,
)


def test_beta_aggressive_user_flow(client, db_session_factory, tmp_path):
    settings = get_settings()
    old_reset_outbox = settings.mail_outbox_path
    old_email_change_outbox = settings.mail_outbox_email_change_path
    reset_outbox = tmp_path / "reset_links.txt"
    email_change_outbox = tmp_path / "email_change_links.txt"
    settings.mail_outbox_path = str(reset_outbox)
    settings.mail_outbox_email_change_path = str(email_change_outbox)
    reset_outbox.write_text("", encoding="utf-8")
    email_change_outbox.write_text("", encoding="utf-8")

    try:
        with db_session_factory() as db:
            admin = create_admin_user(db, unique_email("beta-admin"), "AdminPass123!")
            published_recipe = create_published_recipe(
                db,
                admin.id,
                title=f"Beta Published Recipe {uuid4().hex[:8]}",
                is_published=True,
            )
            published_recipe_id = published_recipe.id
            published_recipe_title = published_recipe.title

        user_email = unique_email("beta-user")
        start_password = "BetaStart123!"
        register_response = post_form(
            client,
            "/register",
            data={"email": user_email, "username": "beta.user", "password": start_password},
            referer_page="/register",
            follow_redirects=False,
        )
        assert register_response.status_code in {302, 303}

        logout_after_register = post_form(
            client,
            "/logout",
            data={},
            referer_page="/",
            follow_redirects=False,
        )
        assert logout_after_register.status_code in {302, 303}

        login_response = post_form(
            client,
            "/login",
            data={"identifier": user_email, "password": start_password},
            referer_page="/login",
            follow_redirects=False,
        )
        assert login_response.status_code in {302, 303}

        username_value = "beta.user.01"
        username_response = post_form(
            client,
            "/profile/username",
            data={"username": username_value},
            referer_page="/me",
            follow_redirects=False,
        )
        assert username_response.status_code in {302, 303}
        profile_page = client.get("/me")
        assert profile_page.status_code == 200
        assert username_value in profile_page.text

        changed_password = "BetaChanged123!"
        change_password_response = post_form(
            client,
            "/auth/change-password",
            data={
                "old_password": start_password,
                "new_password": changed_password,
                "confirm_password": changed_password,
            },
            referer_page="/me",
            follow_redirects=False,
        )
        assert change_password_response.status_code in {302, 303}

        logout_after_change = post_form(
            client,
            "/logout",
            data={},
            referer_page="/",
            follow_redirects=False,
        )
        assert logout_after_change.status_code in {302, 303}

        relogin_changed = post_form(
            client,
            "/login",
            data={"identifier": user_email, "password": changed_password},
            referer_page="/login",
            follow_redirects=False,
        )
        assert relogin_changed.status_code in {302, 303}

        forgot_response = post_form(
            client,
            "/auth/forgot-password",
            data={"identifier": user_email},
            referer_page="/auth/forgot-password",
        )
        assert forgot_response.status_code == 200
        assert "Wenn der Account existiert" in forgot_response.text

        reset_link = read_last_link(Path(settings.mail_outbox_path))
        reset_token = extract_token_from_link(reset_link)
        reset_password = "BetaReset123!"
        reset_response = post_form(
            client,
            "/auth/reset-password",
            data={
                "token": reset_token,
                "new_password": reset_password,
                "confirm_password": reset_password,
            },
            referer_page=f"/auth/reset-password?token={reset_token}",
            follow_redirects=False,
        )
        assert reset_response.status_code in {302, 303}

        login_reset = post_form(
            client,
            "/login",
            data={"identifier": user_email, "password": reset_password},
            referer_page="/login",
            follow_redirects=False,
        )
        assert login_reset.status_code in {302, 303}

        submission_title = f"Beta User Submission {uuid4().hex[:8]}"
        submit_response = post_form(
            client,
            "/submit",
            data={
                "title": submission_title,
                "description": "Aggressive user flow submission.",
                "instructions": "Step one\nStep two",
                "category_select": "Unkategorisiert",
                "difficulty": "medium",
            },
            referer_page="/submit",
            follow_redirects=False,
        )
        assert submit_response.status_code in {302, 303}
        assert "/my-submissions" in str(submit_response.headers.get("location", ""))

        discover_page = client.get("/")
        assert discover_page.status_code == 200
        assert submission_title not in discover_page.text

        my_submissions_page = client.get("/my-submissions")
        assert my_submissions_page.status_code == 200
        assert submission_title in my_submissions_page.text

        with db_session_factory() as db:
            user = db.scalar(select(User).where(User.email == user_email))
            assert user is not None
            submission = db.scalar(
                select(RecipeSubmission).where(
                    and_(
                        RecipeSubmission.submitter_user_id == user.id,
                        RecipeSubmission.title == submission_title,
                    )
                )
            )
            assert submission is not None
            assert submission.status == "pending"

        favorite_response = post_form(
            client,
            f"/recipes/{published_recipe_id}/favorite",
            data={},
            referer_page=f"/recipes/{published_recipe_id}",
            follow_redirects=False,
        )
        assert favorite_response.status_code in {302, 303}

        favorites_page = client.get("/favorites")
        assert favorites_page.status_code == 200
        assert published_recipe_title in favorites_page.text

        review_comment = "Beta aggressive review comment."
        review_response = post_form(
            client,
            f"/recipes/{published_recipe_id}/reviews",
            data={"rating": "5", "comment": review_comment},
            referer_page=f"/recipes/{published_recipe_id}",
            follow_redirects=False,
        )
        assert review_response.status_code in {302, 303}

        detail_page = client.get(f"/recipes/{published_recipe_id}")
        assert detail_page.status_code == 200
        assert review_comment in detail_page.text

        pdf_response = client.get(f"/recipes/{published_recipe_id}/pdf")
        assert pdf_response.status_code == 200
        assert "application/pdf" in (pdf_response.headers.get("content-type") or "").lower()
        assert pdf_response.content.startswith(b"%PDF")

        image_change_response = post_form(
            client,
            f"/recipes/{published_recipe_id}/image-change-request",
            data={},
            referer_page=f"/recipes/{published_recipe_id}",
            files={"file": ("beta-change.png", SMALL_PNG_BYTES, "image/png")},
            follow_redirects=False,
        )
        assert image_change_response.status_code in {302, 303}

        with db_session_factory() as db:
            user = db.scalar(select(User).where(User.email == user_email))
            assert user is not None
            pending_change = db.scalar(
                select(RecipeImageChangeRequest).where(
                    and_(
                        RecipeImageChangeRequest.recipe_id == published_recipe_id,
                        RecipeImageChangeRequest.requester_user_id == user.id,
                        RecipeImageChangeRequest.status == "pending",
                    )
                )
            )
            assert pending_change is not None
    finally:
        settings.mail_outbox_path = old_reset_outbox
        settings.mail_outbox_email_change_path = old_email_change_outbox

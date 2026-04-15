from __future__ import annotations

from pathlib import Path
import time
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

if TYPE_CHECKING:
    from playwright.sync_api import Page


def _wait_for_csrf(page: Page, form_action: str) -> None:
    page.wait_for_selector(f"form[action='{form_action}']")
    page.wait_for_selector(f"form[action='{form_action}'] input[name='csrf_token']", state="attached")


def _login(page: Page, base_url: str, identifier: str, password: str) -> None:
    page.goto(f"{base_url}/login")
    _wait_for_csrf(page, "/login")
    page.fill("form[action='/login'] input[name='identifier']", identifier)
    page.fill("form[action='/login'] input[name='password']", password)
    page.click("form[action='/login'] button[type='submit']")
    page.wait_for_url(f"{base_url}/")


def _logout(page: Page, base_url: str) -> None:
    _wait_for_csrf(page, "/logout")
    page.click("form[action='/logout'] button[type='submit']")
    page.wait_for_url(f"{base_url}/")


def _extract_latest_link(outbox_path: Path, marker: str) -> str:
    deadline = time.time() + 5.0
    while time.time() < deadline:
        content = outbox_path.read_text(encoding="utf-8")
        index = content.rfind(marker)
        if index >= 0:
            token_chars: list[str] = []
            for char in content[index:]:
                if char in "\n\r ":
                    break
                token_chars.append(char)
            link = "".join(token_chars).strip()
            if link:
                return link
        time.sleep(0.1)
    raise AssertionError(f"No link with marker '{marker}' found in outbox {outbox_path}")


def test_user_full_journey(page: Page, base_url: str, e2e_seed_data: dict[str, object]) -> None:
    user_email = str(e2e_seed_data["user_email"])
    user_password = str(e2e_seed_data["user_password"])
    user_password_changed = str(e2e_seed_data["user_password_changed"])
    user_password_reset = str(e2e_seed_data["user_password_reset"])
    reset_outbox_path = Path(str(e2e_seed_data["reset_outbox_path"]))
    published_recipe_id = int(e2e_seed_data["published_recipe_id"])
    published_recipe_title = str(e2e_seed_data["published_recipe_title"])

    _login(page, base_url, user_email, user_password)

    page.goto(f"{base_url}/me")
    _wait_for_csrf(page, "/profile/username")
    page.fill("form[action='/profile/username'] input[name='username']", "journey.user")
    page.click("form[action='/profile/username'] button[type='submit']")
    page.wait_for_url("**/me?message=username_updated")
    assert "journey.user" in page.content()

    _wait_for_csrf(page, "/auth/change-password")
    page.fill("form[action='/auth/change-password'] input[name='old_password']", user_password)
    page.fill("form[action='/auth/change-password'] input[name='new_password']", user_password_changed)
    page.fill("form[action='/auth/change-password'] input[name='confirm_password']", user_password_changed)
    page.click("form[action='/auth/change-password'] button[type='submit']")
    page.wait_for_url("**/me?message=password_changed")

    _logout(page, base_url)
    _login(page, base_url, user_email, user_password_changed)
    _logout(page, base_url)

    page.goto(f"{base_url}/auth/forgot-password")
    _wait_for_csrf(page, "/auth/forgot-password")
    page.fill("form[action='/auth/forgot-password'] input[name='identifier']", user_email)
    page.click("form[action='/auth/forgot-password'] button[type='submit']")

    reset_link = _extract_latest_link(reset_outbox_path, f"{base_url}/auth/reset-password?token=")
    page.goto(reset_link)
    _wait_for_csrf(page, "/auth/reset-password")
    page.fill("form[action='/auth/reset-password'] input[name='new_password']", user_password_reset)
    page.fill("form[action='/auth/reset-password'] input[name='confirm_password']", user_password_reset)
    page.click("form[action='/auth/reset-password'] button[type='submit']")
    page.wait_for_url("**/login?message=reset_done")

    _login(page, base_url, user_email, user_password_reset)

    user_submission_title = "E2E User Submission Journey"
    page.goto(f"{base_url}/submit")
    _wait_for_csrf(page, "/submit")
    page.fill("form[action='/submit'] input[name='title']", user_submission_title)
    page.fill("form[action='/submit'] textarea[name='description']", "Beschreibung fuer den E2E-Weg.")
    page.fill("form[action='/submit'] textarea[name='instructions']", "Schritt 1\nSchritt 2")
    page.fill("form[action='/submit'] textarea[name='ingredients_text']", "Mehl|200 g\nEi|2")
    page.click("form[action='/submit'] button[type='submit']")
    page.wait_for_url("**/my-submissions?submitted=1")
    assert user_submission_title in page.content()

    page.goto(f"{base_url}/")
    assert user_submission_title not in page.content()

    page.goto(f"{base_url}/my-submissions")
    assert user_submission_title in page.content()

    page.goto(f"{base_url}/recipes/{published_recipe_id}")
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and response.url.endswith(f"/recipes/{published_recipe_id}/favorite")
    ):
        page.click(f"form[action='/recipes/{published_recipe_id}/favorite'] button[type='submit']")
    page.goto(f"{base_url}/favorites")
    assert published_recipe_title in page.content()

    page.goto(f"{base_url}/recipes/{published_recipe_id}")
    _wait_for_csrf(page, f"/recipes/{published_recipe_id}/reviews")
    review_comment = "E2E Bewertung vom User-Flow"
    page.select_option(f"form[action='/recipes/{published_recipe_id}/reviews'] select[name='rating']", "4")
    page.fill(f"form[action='/recipes/{published_recipe_id}/reviews'] textarea[name='comment']", review_comment)
    page.click(f"form[action='/recipes/{published_recipe_id}/reviews'] button[type='submit']")
    page.wait_for_url(f"**/recipes/{published_recipe_id}")
    assert review_comment in page.content()

    pdf_response = page.request.get(f"{base_url}/recipes/{published_recipe_id}/pdf")
    assert pdf_response.status == 200
    assert "application/pdf" in (pdf_response.headers.get("content-type") or "").lower()
    assert pdf_response.body().startswith(b"%PDF")

    page.goto(f"{base_url}/recipes/{published_recipe_id}")
    with page.expect_response(
        lambda response: response.request.method == "POST"
        and response.url.endswith(f"/recipes/{published_recipe_id}/favorite")
    ):
        page.click(f"form[action='/recipes/{published_recipe_id}/favorite'] button[type='submit']")
    page.goto(f"{base_url}/favorites")
    assert published_recipe_title not in page.content()


def test_admin_full_journey(page: Page, base_url: str, e2e_seed_data: dict[str, object]) -> None:
    admin_email = str(e2e_seed_data["admin_email"])
    admin_password = str(e2e_seed_data["admin_password"])
    approve_submission_id = int(e2e_seed_data["pending_submission_approve_id"])
    approve_submission_title = str(e2e_seed_data["pending_submission_approve_title"])
    reject_submission_id = int(e2e_seed_data["pending_submission_reject_id"])
    image_change_request_id = int(e2e_seed_data["pending_image_change_request_id"])
    recipe_id = int(e2e_seed_data["published_recipe_id"])

    _login(page, base_url, admin_email, admin_password)

    page.goto(f"{base_url}/admin/submissions/{approve_submission_id}")
    _wait_for_csrf(page, f"/admin/submissions/{approve_submission_id}/approve")
    page.fill(
        f"form[action='/admin/submissions/{approve_submission_id}/approve'] textarea[name='admin_note']",
        "Freigabe im E2E-Test.",
    )
    page.click(f"form[action='/admin/submissions/{approve_submission_id}/approve'] button[type='submit']")
    page.wait_for_url(f"**/admin/submissions/{approve_submission_id}?message=approved*")
    page.goto(f"{base_url}/?title={quote_plus(approve_submission_title)}")
    assert approve_submission_title in page.content()

    page.goto(f"{base_url}/admin/submissions/{reject_submission_id}")
    _wait_for_csrf(page, f"/admin/submissions/{reject_submission_id}/reject")
    page.fill(
        f"form[action='/admin/submissions/{reject_submission_id}/reject'] textarea[name='admin_note']",
        "Ablehnung im E2E-Test.",
    )
    page.click(f"form[action='/admin/submissions/{reject_submission_id}/reject'] button[type='submit']")
    page.wait_for_url(f"**/admin/submissions/{reject_submission_id}?message=rejected")

    page.goto(f"{base_url}/admin/image-change-requests/{image_change_request_id}")
    approve_selector = f"form[action='/admin/image-change-requests/{image_change_request_id}/approve']"
    if page.locator(approve_selector).count() > 0:
        _wait_for_csrf(page, f"/admin/image-change-requests/{image_change_request_id}/approve")
        page.fill(
            f"{approve_selector} textarea[name='admin_note']",
            "Bildfreigabe im E2E-Test.",
        )
        page.click(f"{approve_selector} button[type='submit']")
        page.wait_for_url(f"**/admin/image-change-requests/{image_change_request_id}?message=approved")

    page.goto(f"{base_url}/recipes/{recipe_id}")
    assert "/images/" in page.content()

    admin_recipe_title = "E2E Admin Direktveroeffentlichung"
    page.goto(f"{base_url}/recipes/new")
    _wait_for_csrf(page, "/recipes/new")
    page.fill("form[action='/recipes/new'] input[name='title']", admin_recipe_title)
    page.fill("form[action='/recipes/new'] textarea[name='description']", "Direkt vom Admin erstellt.")
    page.fill("form[action='/recipes/new'] textarea[name='instructions']", "Schritt 1\nSchritt 2")
    page.fill("form[action='/recipes/new'] input[name='prep_time_minutes']", "18")
    page.fill("form[action='/recipes/new'] textarea[name='ingredients_text']", "Wasser|200 ml")
    page.click("form[action='/recipes/new'] button[type='submit']")
    page.wait_for_url("**/recipes/*")

    page.goto(f"{base_url}/?title={quote_plus(admin_recipe_title)}")
    assert admin_recipe_title in page.content()

from __future__ import annotations

import time
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

if TYPE_CHECKING:
    from playwright.sync_api import Page


def _wait_for_form_csrf(page: Page, action: str) -> None:
    page.wait_for_selector(f"form[action='{action}']")
    page.wait_for_selector(f"form[action='{action}'] input[name='csrf_token']", state="attached")


def _login(page: Page, base_url: str, identifier: str, password: str) -> None:
    page.goto(f"{base_url}/login")
    _wait_for_form_csrf(page, "/login")
    page.fill("form[action='/login'] input[name='identifier']", identifier)
    page.fill("form[action='/login'] input[name='password']", password)
    page.click("form[action='/login'] button[type='submit']")
    page.wait_for_url(f"{base_url}/")


def _logout(page: Page, base_url: str) -> None:
    _wait_for_form_csrf(page, "/logout")
    page.click("form[action='/logout'] button[type='submit']")
    page.wait_for_url(f"{base_url}/")


def test_beta_smoke_user_submit_pending(page: Page, base_url: str) -> None:
    unique_id = int(time.time() * 1000)
    email = f"beta-smoke-user-{unique_id}@example.local"
    password = "SmokeUser123!"
    submission_title = f"Beta Smoke Submission {unique_id}"

    page.goto(f"{base_url}/register")
    _wait_for_form_csrf(page, "/register")
    page.fill("form[action='/register'] input[name='email']", email)
    page.fill("form[action='/register'] input[name='username']", f"smoke.user.{unique_id}")
    page.fill("form[action='/register'] input[name='password']", password)
    page.click("form[action='/register'] button[type='submit']")
    page.wait_for_url(f"{base_url}/")

    page.goto(f"{base_url}/submit")
    _wait_for_form_csrf(page, "/submit")
    page.fill("form[action='/submit'] input[name='title']", submission_title)
    page.fill("form[action='/submit'] textarea[name='description']", "Smoke-Einreichung fuer die Moderation.")
    page.fill("form[action='/submit'] textarea[name='instructions']", "Schritt 1\nSchritt 2")
    page.fill("form[action='/submit'] textarea[name='ingredients_text']", "Mehl|100 g\nWasser|50 ml")
    page.click("form[action='/submit'] button[type='submit']")
    page.wait_for_url("**/my-submissions?submitted=1")
    assert submission_title in page.content()

    page.goto(f"{base_url}/")
    assert submission_title not in page.content()


def test_beta_smoke_admin_approve_submission(page: Page, base_url: str, e2e_seed_data: dict[str, object]) -> None:
    admin_email = str(e2e_seed_data["admin_email"])
    admin_password = str(e2e_seed_data["admin_password"])
    unique_id = int(time.time() * 1000)
    user_email = f"beta-smoke-approve-user-{unique_id}@example.local"
    user_password = "SmokeApprove123!"
    submission_title = f"Beta Smoke Pending {unique_id}"

    page.goto(f"{base_url}/register")
    _wait_for_form_csrf(page, "/register")
    page.fill("form[action='/register'] input[name='email']", user_email)
    page.fill("form[action='/register'] input[name='username']", f"smoke.approve.{unique_id}")
    page.fill("form[action='/register'] input[name='password']", user_password)
    page.click("form[action='/register'] button[type='submit']")
    page.wait_for_url(f"{base_url}/")

    page.goto(f"{base_url}/submit")
    _wait_for_form_csrf(page, "/submit")
    page.fill("form[action='/submit'] input[name='title']", submission_title)
    page.fill("form[action='/submit'] textarea[name='description']", "Wird vom Admin im Smoke-Test freigegeben.")
    page.fill("form[action='/submit'] textarea[name='instructions']", "Schritt A\nSchritt B")
    page.fill("form[action='/submit'] textarea[name='ingredients_text']", "Tomate|2 Stueck")
    page.click("form[action='/submit'] button[type='submit']")
    page.wait_for_url("**/my-submissions?submitted=1")
    _logout(page, base_url)

    _login(page, base_url, admin_email, admin_password)
    page.goto(f"{base_url}/admin/submissions?status_filter=pending")
    assert submission_title in page.content()

    detail_link = page.locator("tbody tr", has_text=submission_title).first.locator("a[href^='/admin/submissions/']").first
    href = detail_link.get_attribute("href")
    assert href
    page.goto(f"{base_url}{href}")

    approve_action = href.rstrip("/") + "/approve"
    _wait_for_form_csrf(page, approve_action)
    page.fill(f"form[action='{approve_action}'] textarea[name='admin_note']", "Freigabe im Beta-Smoke.")
    page.click(f"form[action='{approve_action}'] button[type='submit']")
    page.wait_for_url("**?message=approved*")

    page.goto(f"{base_url}/?title={quote_plus(submission_title)}")
    assert submission_title in page.content()

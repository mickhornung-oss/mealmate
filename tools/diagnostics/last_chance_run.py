from __future__ import annotations

import argparse
import base64
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import func, inspect, select

from app.config import get_settings
from app.database import SessionLocal
from app.main import app
from app.models import Recipe, RecipeImage, RecipeImageChangeRequest, RecipeSubmission, User
from app.security import hash_password
from app.translation_models import RecipeTranslation
from app.translation_service import build_recipe_source_payload, build_source_hash
from tools.diagnostics.image_smoke import run_image_smoke
from tools.diagnostics.translation_smoke import run_translation_smoke

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTICS_DIR = PROJECT_ROOT / "diagnostics"
REPORT_PATH = DIAGNOSTICS_DIR / "LAST_CHANCE_REPORT.md"
URL_RE = re.compile(r"https?://[^\s]+")
SMALL_PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4z8AAAAMBAQDJ/pLvAAAAAElFTkSuQmCC"
)


@dataclass
class StepStatus:
    name: str
    ok: bool
    detail: str


@dataclass
class FlowArtifacts:
    user_email: str = ""
    user_password: str = ""
    user_password_new: str = ""
    user_password_reset: str = ""
    user_id: int | None = None
    user_submission_title: str = ""
    favorite_recipe_id: int | None = None
    favorite_recipe_title: str = ""
    review_comment: str = ""
    pending_submission_id: int | None = None
    approved_recipe_id: int | None = None
    approved_recipe_title: str = ""
    rejected_submission_id: int | None = None
    pending_image_request_id: int | None = None


@dataclass
class LastChanceResult:
    ok: bool
    user_steps: list[StepStatus] = field(default_factory=list)
    admin_steps: list[StepStatus] = field(default_factory=list)
    smoke_steps: list[StepStatus] = field(default_factory=list)
    env_summary: dict[str, str] = field(default_factory=dict)
    counts_before: dict[str, int] = field(default_factory=dict)
    counts_after: dict[str, int] = field(default_factory=dict)
    headers_summary: dict[str, str] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    artifacts: FlowArtifacts = field(default_factory=FlowArtifacts)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run last chance consistency + end-to-end diagnostics.")
    parser.add_argument("--report", default=str(REPORT_PATH), help="Markdown report output path.")
    parser.add_argument("--real-api", action="store_true", help="Allow optional real translation provider preview.")
    parser.add_argument(
        "--mock-translation-write",
        action="store_true",
        help="Write mock translation rows in translation smoke phase.",
    )
    return parser.parse_args()


def _normalize_report_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (PROJECT_ROOT / path).resolve()


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _log_step(target: list[StepStatus], name: str, ok: bool, detail: str) -> None:
    target.append(StepStatus(name=name, ok=ok, detail=detail))


def _collect_env_summary() -> dict[str, str]:
    settings = get_settings()
    db_url = settings.database_url
    db_scheme = db_url.split("://", 1)[0] if "://" in db_url else db_url
    return {
        "APP_ENV": settings.app_env,
        "APP_NAME": settings.app_name,
        "DATABASE_SCHEME": db_scheme,
        "COOKIE_NAME": "access_token",
        "CSRF_COOKIE_NAME": settings.csrf_cookie_name,
        "CSRF_HEADER_NAME": settings.csrf_header_name,
        "TRANSLATION_PROVIDER": settings.translation_provider,
        "TRANSLATEAPI_ENABLED": "1" if settings.translateapi_enabled else "0",
        "TRANSLATE_AUTO_ON_PUBLISH": "1" if settings.translate_auto_on_publish else "0",
        "TRANSLATE_LAZY_ON_VIEW": "1" if settings.translate_lazy_on_view else "0",
        "TRANSLATE_TARGET_LANGS": ",".join(settings.translate_target_langs),
        "CSP_IMG_SRC": settings.csp_img_src,
    }


def _table_count(model) -> int:
    with SessionLocal() as db:
        try:
            return int(db.scalar(select(func.count()).select_from(model)) or 0)
        except Exception:
            return -1


def _collect_counts() -> dict[str, int]:
    return {
        "recipes": _table_count(Recipe),
        "recipe_translations": _table_count(RecipeTranslation),
        "recipe_images": _table_count(RecipeImage),
        "recipe_submissions": _table_count(RecipeSubmission),
        "recipe_image_change_requests": _table_count(RecipeImageChangeRequest),
    }


def _extract_reset_token_from_outbox(outbox_path: Path) -> str:
    if not outbox_path.exists():
        raise RuntimeError(f"Reset outbox file not found: {outbox_path}")
    urls = URL_RE.findall(outbox_path.read_text(encoding="utf-8"))
    reset_links = [url for url in urls if "/auth/reset-password?token=" in url]
    if not reset_links:
        raise RuntimeError("No reset-password link found in outbox.")
    last_link = reset_links[-1]
    query = parse_qs(urlparse(last_link).query)
    token_values = query.get("token", [])
    if not token_values or not token_values[0].strip():
        raise RuntimeError("Reset token missing in outbox link.")
    return token_values[0].strip()


def _get_csrf(client: TestClient, path: str = "/") -> str:
    response = client.get(path)
    if response.status_code >= 500:
        raise RuntimeError(f"GET {path} returned server error {response.status_code}")
    settings = get_settings()
    token = client.cookies.get(settings.csrf_cookie_name) or client.cookies.get("csrf_token")
    if not token:
        raise RuntimeError(f"CSRF cookie missing after GET {path}")
    return str(token)


def _post_form(
    client: TestClient,
    path: str,
    data: dict[str, str],
    *,
    referer: str = "/",
    follow_redirects: bool = False,
):
    csrf = _get_csrf(client, referer)
    payload = dict(data)
    payload.setdefault("csrf_token", csrf)
    return client.post(
        path,
        data=payload,
        headers={"X-CSRF-Token": csrf},
        follow_redirects=follow_redirects,
    )


def _post_multipart(
    client: TestClient,
    path: str,
    *,
    referer: str,
    data: dict[str, str] | None = None,
    file_field: str = "file",
    file_name: str = "diag.png",
    file_type: str = "image/png",
    file_bytes: bytes = SMALL_PNG_BYTES,
):
    csrf = _get_csrf(client, referer)
    payload = dict(data or {})
    payload.setdefault("csrf_token", csrf)
    return client.post(
        path,
        data=payload,
        files={file_field: (file_name, file_bytes, file_type)},
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )


def _ensure_diag_admin() -> tuple[str, str]:
    email = f"diag-admin-{uuid4().hex[:10]}@example.local"
    password = "DiagAdmin123!"
    with SessionLocal() as db:
        db.add(User(email=email, hashed_password=hash_password(password), role="admin"))
        db.commit()
    return email, password


def _lookup_user_id(email: str) -> int | None:
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == email.strip().lower()))
        return int(user.id) if user else None


def _get_published_recipe_for_interactions() -> tuple[int | None, str]:
    with SessionLocal() as db:
        recipe = db.scalar(select(Recipe).where(Recipe.is_published.is_(True)).order_by(Recipe.id.desc()))
        if not recipe:
            return None, ""
        return int(recipe.id), (recipe.title or "")


def _create_manual_pending_submission(user_id: int | None) -> int:
    with SessionLocal() as db:
        submission = RecipeSubmission(
            submitter_user_id=user_id,
            title=f"Diag reject candidate {uuid4().hex[:8]}",
            description="Pending submission for reject path.",
            category="Test",
            difficulty="easy",
            prep_time_minutes=15,
            servings_text="2",
            instructions="Step one\nStep two",
            status="pending",
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return int(submission.id)


def _latest_pending_submission_id() -> int | None:
    with SessionLocal() as db:
        submission = db.scalar(
            select(RecipeSubmission).where(RecipeSubmission.status == "pending").order_by(RecipeSubmission.id.desc())
        )
        return int(submission.id) if submission else None


def _recipe_from_submission(submission_id: int) -> tuple[int | None, str]:
    with SessionLocal() as db:
        recipe = db.scalar(select(Recipe).where(Recipe.source_uuid == f"submission:{submission_id}"))
        if not recipe:
            return None, ""
        return int(recipe.id), (recipe.title or "")


def _latest_pending_image_request_id() -> int | None:
    with SessionLocal() as db:
        request_row = db.scalar(
            select(RecipeImageChangeRequest)
            .where(RecipeImageChangeRequest.status == "pending")
            .order_by(RecipeImageChangeRequest.id.desc())
        )
        return int(request_row.id) if request_row else None


def _is_image_request_approved(request_id: int) -> bool:
    with SessionLocal() as db:
        request_row = db.scalar(select(RecipeImageChangeRequest).where(RecipeImageChangeRequest.id == request_id))
        return bool(request_row and request_row.status == "approved")


def _recipe_has_primary_image(recipe_id: int) -> bool:
    with SessionLocal() as db:
        count = db.scalar(
            select(func.count()).select_from(RecipeImage).where(RecipeImage.recipe_id == recipe_id, RecipeImage.is_primary.is_(True))
        )
        return int(count or 0) > 0


def _translation_sanity_for_recipe(recipe_id: int) -> tuple[bool, list[str]]:
    settings = get_settings()
    errors: list[str] = []
    with SessionLocal() as db:
        inspector = inspect(db.bind)
        if not inspector.has_table("recipe_translations"):
            return False, ["Table 'recipe_translations' missing."]
        rows = db.scalars(select(RecipeTranslation).where(RecipeTranslation.recipe_id == recipe_id)).all()
    by_lang = {row.language for row in rows}
    target_langs = [lang for lang in settings.translate_target_langs if lang != settings.translate_source_lang]
    missing_targets = [lang for lang in target_langs if lang not in by_lang]
    if missing_targets:
        errors.append(f"Missing translation rows for target langs: {', '.join(missing_targets)}")
    missing_core = [lang for lang in ("de", "en", "fr") if lang not in by_lang]
    if missing_core:
        errors.append(f"Missing core language rows (de/en/fr check): {', '.join(missing_core)}")
    return len(errors) == 0, errors


def _write_mock_translations_for_recipe(recipe_id: int) -> bool:
    with SessionLocal() as db:
        recipe = db.scalar(select(Recipe).where(Recipe.id == recipe_id))
        if not recipe:
            return False
        payload = build_recipe_source_payload(recipe)
        source_hash = build_source_hash(payload)
        for language in ("de", "en", "fr"):
            row = db.scalar(
                select(RecipeTranslation).where(
                    RecipeTranslation.recipe_id == recipe_id,
                    RecipeTranslation.language == language,
                )
            )
            title = f"[MOCK {language.upper()}] {recipe.title}"[:255]
            description = f"[MOCK {language.upper()}] {recipe.description}"
            instructions = f"[MOCK {language.upper()}] {recipe.instructions}"
            ingredients_text = f"[MOCK {language.upper()}] {payload['ingredients_text']}"
            if row is None:
                row = RecipeTranslation(
                    recipe_id=recipe_id,
                    language=language,
                    title=title,
                    description=description,
                    instructions=instructions,
                    ingredients_text=ingredients_text,
                    source_hash=source_hash,
                    stale=False,
                )
                db.add(row)
            else:
                row.title = title
                row.description = description
                row.instructions = instructions
                row.ingredients_text = ingredients_text
                row.source_hash = source_hash
                row.stale = False
        db.commit()
    return True


def run_last_chance(*, real_api: bool, mock_translation_write: bool, report_path: Path) -> LastChanceResult:
    result = LastChanceResult(ok=True)
    result.env_summary = _collect_env_summary()
    result.counts_before = _collect_counts()
    artifacts = result.artifacts

    translation_smoke = run_translation_smoke(
        real_api=real_api,
        mock_write=mock_translation_write,
        report_path=DIAGNOSTICS_DIR / "translation_smoke.md",
    )
    _log_step(
        result.smoke_steps,
        "translation_smoke",
        translation_smoke.ok,
        f"report={DIAGNOSTICS_DIR / 'translation_smoke.md'}",
    )
    if not translation_smoke.ok:
        result.ok = False
        result.failures.extend(translation_smoke.failures)

    image_smoke = run_image_smoke(report_path=DIAGNOSTICS_DIR / "image_smoke.md")
    _log_step(result.smoke_steps, "image_smoke", image_smoke.ok, f"report={DIAGNOSTICS_DIR / 'image_smoke.md'}")
    if not image_smoke.ok:
        result.ok = False
        result.failures.extend(image_smoke.failures)

    with TestClient(app) as client:
        home = client.get("/")
        result.headers_summary["home_status"] = str(home.status_code)
        result.headers_summary["home_csp"] = home.headers.get("content-security-policy", "-")

        artifacts.user_email = f"last-chance-user-{uuid4().hex[:10]}@example.local"
        artifacts.user_password = "UserPass123!"
        artifacts.user_password_new = "UserPass123!X"
        artifacts.user_password_reset = "UserPass123!Z"
        username_initial = f"lcuser{uuid4().hex[:6]}"

        register_response = _post_form(
            client,
            "/register",
            {"email": artifacts.user_email, "username": username_initial, "password": artifacts.user_password},
            referer="/register",
        )
        register_ok = register_response.status_code in {302, 303}
        _log_step(result.user_steps, "register", register_ok, f"status={register_response.status_code}")
        if not register_ok:
            result.ok = False
            result.failures.append("User register failed.")

        logout_after_register = _post_form(client, "/logout", {}, referer="/")
        _log_step(
            result.user_steps,
            "logout_after_register",
            logout_after_register.status_code in {302, 303},
            f"status={logout_after_register.status_code}",
        )

        login_response = _post_form(
            client,
            "/login",
            {"identifier": artifacts.user_email, "password": artifacts.user_password},
            referer="/login",
        )
        login_ok = login_response.status_code in {302, 303} and bool(client.cookies.get("access_token"))
        result.headers_summary["login_set_cookie"] = login_response.headers.get("set-cookie", "-")
        _log_step(result.user_steps, "login", login_ok, f"status={login_response.status_code}")
        if not login_ok:
            result.ok = False
            result.failures.append("User login failed.")

        username_updated = f"lcuserupd{uuid4().hex[:6]}"
        username_response = _post_form(
            client,
            "/profile/username",
            {"username": username_updated},
            referer="/me",
        )
        _log_step(
            result.user_steps,
            "set_username",
            username_response.status_code in {302, 303},
            f"status={username_response.status_code}",
        )

        change_password_response = _post_form(
            client,
            "/auth/change-password",
            {
                "old_password": artifacts.user_password,
                "new_password": artifacts.user_password_new,
                "confirm_password": artifacts.user_password_new,
            },
            referer="/me",
        )
        change_password_ok = change_password_response.status_code in {302, 303}
        _log_step(
            result.user_steps,
            "change_password",
            change_password_ok,
            f"status={change_password_response.status_code}",
        )
        if not change_password_ok:
            result.ok = False
            result.failures.append("Change password failed.")

        logout_response = _post_form(client, "/logout", {}, referer="/")
        _log_step(result.user_steps, "logout_after_change_password", logout_response.status_code in {302, 303}, f"status={logout_response.status_code}")

        login_new_response = _post_form(
            client,
            "/login",
            {"identifier": artifacts.user_email, "password": artifacts.user_password_new},
            referer="/login",
        )
        login_new_ok = login_new_response.status_code in {302, 303}
        _log_step(result.user_steps, "login_with_new_password", login_new_ok, f"status={login_new_response.status_code}")
        if not login_new_ok:
            result.ok = False
            result.failures.append("Login with new password failed.")

        forgot_response = _post_form(
            client,
            "/auth/forgot-password",
            {"identifier": artifacts.user_email},
            referer="/auth/forgot-password",
            follow_redirects=True,
        )
        forgot_ok = forgot_response.status_code == 200
        _log_step(result.user_steps, "forgot_password_request", forgot_ok, f"status={forgot_response.status_code}")
        if not forgot_ok:
            result.ok = False
            result.failures.append("Forgot password request failed.")

        reset_token = ""
        try:
            settings = get_settings()
            outbox_path = Path(settings.mail_outbox_path)
            if not outbox_path.is_absolute():
                outbox_path = (PROJECT_ROOT / outbox_path).resolve()
            reset_token = _extract_reset_token_from_outbox(outbox_path)
            _log_step(result.user_steps, "forgot_password_token_read", True, f"outbox={outbox_path}")
        except Exception as exc:
            _log_step(result.user_steps, "forgot_password_token_read", False, str(exc))
            result.ok = False
            result.failures.append(f"Reset token read failed: {exc}")

        if reset_token:
            reset_response = _post_form(
                client,
                "/auth/reset-password",
                {
                    "token": reset_token,
                    "new_password": artifacts.user_password_reset,
                    "confirm_password": artifacts.user_password_reset,
                },
                referer=f"/auth/reset-password?token={reset_token}",
            )
            reset_ok = reset_response.status_code in {302, 303}
            _log_step(result.user_steps, "reset_password_submit", reset_ok, f"status={reset_response.status_code}")
            if not reset_ok:
                result.ok = False
                result.failures.append("Reset password submit failed.")

            _post_form(client, "/logout", {}, referer="/")
            login_reset_response = _post_form(
                client,
                "/login",
                {"identifier": artifacts.user_email, "password": artifacts.user_password_reset},
                referer="/login",
            )
            login_reset_ok = login_reset_response.status_code in {302, 303}
            _log_step(
                result.user_steps,
                "login_after_reset",
                login_reset_ok,
                f"status={login_reset_response.status_code}",
            )
            if not login_reset_ok:
                result.ok = False
                result.failures.append("Login after reset failed.")

        artifacts.user_id = _lookup_user_id(artifacts.user_email)
        artifacts.user_submission_title = f"LC Pending Recipe {uuid4().hex[:8]}"
        submit_response = _post_form(
            client,
            "/submit",
            {
                "title": artifacts.user_submission_title,
                "description": "Diagnostic submission",
                "instructions": "Step one\nStep two",
                "category_select": "Hauptgericht",
                "difficulty": "easy",
                "prep_time_minutes": "15",
                "servings_text": "2",
                "ingredients_text": "Tomate|2 Stueck",
            },
            referer="/submit",
        )
        submit_ok = submit_response.status_code in {201, 302, 303}
        _log_step(result.user_steps, "submit_recipe", submit_ok, f"status={submit_response.status_code}")
        if not submit_ok:
            result.ok = False
            result.failures.append("Recipe submission failed.")

        my_submissions = client.get("/my-submissions")
        pending_visible = my_submissions.status_code == 200 and artifacts.user_submission_title in my_submissions.text
        _log_step(
            result.user_steps,
            "submission_visible_in_my_submissions",
            pending_visible,
            f"status={my_submissions.status_code}",
        )
        if not pending_visible:
            result.ok = False
            result.failures.append("Pending submission not visible in /my-submissions.")

        discover_page = client.get("/")
        discover_hidden = artifacts.user_submission_title not in discover_page.text
        _log_step(
            result.user_steps,
            "submission_not_in_discover",
            discover_hidden,
            f"status={discover_page.status_code}",
        )
        if not discover_hidden:
            result.ok = False
            result.failures.append("Pending submission leaked into discover page.")

        favorite_recipe_id, favorite_recipe_title = _get_published_recipe_for_interactions()
        artifacts.favorite_recipe_id = favorite_recipe_id
        artifacts.favorite_recipe_title = favorite_recipe_title
        if favorite_recipe_id:
            favorite_response = _post_form(
                client,
                f"/recipes/{favorite_recipe_id}/favorite",
                {"favorite_box_id": f"favorite-box-card-{favorite_recipe_id}"},
                referer=f"/recipes/{favorite_recipe_id}",
            )
            favorite_ok = favorite_response.status_code in {200, 302, 303}
            _log_step(result.user_steps, "favorite_toggle", favorite_ok, f"status={favorite_response.status_code}")
            favorites_page = client.get("/favorites")
            favorite_visible = favorites_page.status_code == 200 and favorite_recipe_title in favorites_page.text
            _log_step(
                result.user_steps,
                "favorite_visible_in_favorites_page",
                favorite_visible,
                f"status={favorites_page.status_code}",
            )
            if not favorite_visible:
                result.ok = False
                result.failures.append("Favorited recipe not visible on /favorites.")

            artifacts.review_comment = f"LC review {uuid4().hex[:8]}"
            review_response = _post_form(
                client,
                f"/recipes/{favorite_recipe_id}/reviews",
                {"rating": "5", "comment": artifacts.review_comment},
                referer=f"/recipes/{favorite_recipe_id}",
            )
            review_ok = review_response.status_code in {302, 303}
            _log_step(result.user_steps, "review_submit", review_ok, f"status={review_response.status_code}")
            detail_after_review = client.get(f"/recipes/{favorite_recipe_id}")
            review_visible = detail_after_review.status_code == 200 and artifacts.review_comment in detail_after_review.text
            _log_step(
                result.user_steps,
                "review_visible_in_detail",
                review_visible,
                f"status={detail_after_review.status_code}",
            )
            if not review_visible:
                result.ok = False
                result.failures.append("Review comment not visible on detail page.")

            pdf_response = client.get(f"/recipes/{favorite_recipe_id}/pdf")
            pdf_ok = (
                pdf_response.status_code == 200
                and "application/pdf" in (pdf_response.headers.get("content-type") or "")
                and bytes(pdf_response.content).startswith(b"%PDF")
            )
            _log_step(result.user_steps, "pdf_download", pdf_ok, f"status={pdf_response.status_code}")
            if not pdf_ok:
                result.ok = False
                result.failures.append("PDF endpoint check failed.")

            before_pending_image_requests = _table_count(RecipeImageChangeRequest)
            image_change_response = _post_multipart(
                client,
                f"/recipes/{favorite_recipe_id}/image-change-request",
                referer=f"/recipes/{favorite_recipe_id}",
                data={},
            )
            image_change_ok = image_change_response.status_code in {302, 303}
            after_pending_image_requests = _table_count(RecipeImageChangeRequest)
            increment_ok = after_pending_image_requests == before_pending_image_requests + 1
            _log_step(
                result.user_steps,
                "image_change_request_submit",
                image_change_ok and increment_ok,
                f"status={image_change_response.status_code}, before={before_pending_image_requests}, after={after_pending_image_requests}",
            )
            if not (image_change_ok and increment_ok):
                result.ok = False
                result.failures.append("Image change request submit/count check failed.")

        admin_email, admin_password = _ensure_diag_admin()
        admin_login = _post_form(
            client,
            "/login",
            {"identifier": admin_email, "password": admin_password},
            referer="/login",
        )
        admin_login_ok = admin_login.status_code in {302, 303}
        _log_step(result.admin_steps, "admin_login", admin_login_ok, f"status={admin_login.status_code}")
        if not admin_login_ok:
            result.ok = False
            result.failures.append("Admin login failed.")

        artifacts.pending_submission_id = _latest_pending_submission_id()
        if artifacts.pending_submission_id:
            approve_response = _post_form(
                client,
                f"/admin/submissions/{artifacts.pending_submission_id}/approve",
                {"admin_note": "Approved in last chance run"},
                referer=f"/admin/submissions/{artifacts.pending_submission_id}",
            )
            approve_ok = approve_response.status_code in {302, 303}
            _log_step(
                result.admin_steps,
                "approve_pending_submission",
                approve_ok,
                f"status={approve_response.status_code}",
            )
            artifacts.approved_recipe_id, artifacts.approved_recipe_title = _recipe_from_submission(artifacts.pending_submission_id)
            if artifacts.approved_recipe_id:
                discover_after_approve = client.get("/")
                recipe_visible = artifacts.approved_recipe_title in discover_after_approve.text
                _log_step(
                    result.admin_steps,
                    "approved_recipe_visible_in_discover",
                    recipe_visible,
                    f"recipe_id={artifacts.approved_recipe_id}",
                )
                if not recipe_visible:
                    result.ok = False
                    result.failures.append("Approved submission recipe not visible in discover.")
            else:
                _log_step(
                    result.admin_steps,
                    "approved_recipe_created",
                    False,
                    "No recipe found for approved submission source_uuid.",
                )
                result.ok = False
                result.failures.append("Approve did not produce published recipe row.")

        artifacts.rejected_submission_id = _create_manual_pending_submission(artifacts.user_id)
        reject_response = _post_form(
            client,
            f"/admin/submissions/{artifacts.rejected_submission_id}/reject",
            {"admin_note": "Rejected in last chance run"},
            referer=f"/admin/submissions/{artifacts.rejected_submission_id}",
        )
        reject_ok = reject_response.status_code in {302, 303}
        _log_step(result.admin_steps, "reject_pending_submission", reject_ok, f"status={reject_response.status_code}")
        with SessionLocal() as db:
            rejected = db.scalar(select(RecipeSubmission).where(RecipeSubmission.id == artifacts.rejected_submission_id))
            rejected_state_ok = bool(rejected and rejected.status == "rejected")
        _log_step(
            result.admin_steps,
            "rejected_submission_state",
            rejected_state_ok,
            f"submission_id={artifacts.rejected_submission_id}",
        )
        if not rejected_state_ok:
            result.ok = False
            result.failures.append("Rejected submission state not persisted.")

        artifacts.pending_image_request_id = _latest_pending_image_request_id()
        if artifacts.pending_image_request_id:
            approve_image_response = _post_form(
                client,
                f"/admin/image-change-requests/{artifacts.pending_image_request_id}/approve",
                {"admin_note": "Approved image change"},
                referer=f"/admin/image-change-requests/{artifacts.pending_image_request_id}",
            )
            approve_image_ok = approve_image_response.status_code in {302, 303}
            _log_step(
                result.admin_steps,
                "approve_image_change_request",
                approve_image_ok,
                f"status={approve_image_response.status_code}",
            )
            image_request_done = _is_image_request_approved(artifacts.pending_image_request_id)
            _log_step(
                result.admin_steps,
                "image_change_request_state",
                image_request_done,
                f"request_id={artifacts.pending_image_request_id}",
            )
            if not image_request_done:
                result.ok = False
                result.failures.append("Image change request did not transition to approved.")

            if artifacts.favorite_recipe_id:
                primary_ok = _recipe_has_primary_image(artifacts.favorite_recipe_id)
                _log_step(
                    result.admin_steps,
                    "recipe_has_primary_image_after_approve",
                    primary_ok,
                    f"recipe_id={artifacts.favorite_recipe_id}",
                )
                if not primary_ok:
                    result.ok = False
                    result.failures.append("Approved image request did not result in primary image.")

        if artifacts.approved_recipe_id:
            translation_ok, translation_errors = _translation_sanity_for_recipe(artifacts.approved_recipe_id)
            if not translation_ok and mock_translation_write:
                mock_applied = _write_mock_translations_for_recipe(artifacts.approved_recipe_id)
                _log_step(
                    result.admin_steps,
                    "translation_mock_write_for_approved_recipe",
                    mock_applied,
                    f"recipe_id={artifacts.approved_recipe_id}",
                )
                translation_ok, translation_errors = _translation_sanity_for_recipe(artifacts.approved_recipe_id)
            _log_step(
                result.admin_steps,
                "translation_sanity_for_approved_recipe",
                translation_ok,
                "ok" if translation_ok else "; ".join(translation_errors),
            )
            if not translation_ok:
                result.ok = False
                result.failures.extend(translation_errors)

    result.counts_after = _collect_counts()
    _add_recommendations(result)
    _write_report(result, report_path)
    return result


def _add_recommendations(result: LastChanceResult) -> None:
    combined_failures = " | ".join(result.failures).lower()
    if "translation" in combined_failures or "missing target translation rows" in combined_failures:
        result.recommendations.append(
            "Likely translation root cause: provider/env trigger mismatch; check TRANSLATEAPI_ENABLED, target langs, and auto/batch run paths."
        )
    if "image" in combined_failures or "repeated image source" in combined_failures:
        result.recommendations.append(
            "Likely image root cause: fallback source selection or caching/template reuse; inspect card/detail src generation and Cache-Control."
        )
    if "csrf" in combined_failures:
        result.recommendations.append("Check CSRF cookie/header wiring in diagnostics helper and middleware exemptions.")
    if "pending submission leaked" in combined_failures:
        result.recommendations.append("Re-verify discover query has is_published=true hard filter.")
    if not result.recommendations:
        result.recommendations.append("No blocker detected in this run; keep running smoke tools after each release candidate.")


def _write_report(result: LastChanceResult, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    lines.append("# LAST CHANCE REPORT")
    lines.append("")
    lines.append(f"- Generated at: {_now_iso()}")
    lines.append(f"- Status: {'PASS' if result.ok else 'FAIL'}")
    lines.append("")
    lines.append("## ENV Summary (keys only)")
    lines.append("| Key | Value |")
    lines.append("| --- | --- |")
    for key, value in sorted(result.env_summary.items(), key=lambda item: item[0]):
        safe_value = str(value).replace("|", "\\|")
        lines.append(f"| `{key}` | `{safe_value}` |")
    lines.append("")
    lines.append("## DB Counts (before -> after)")
    lines.append("| Metric | Before | After | Delta |")
    lines.append("| --- | ---: | ---: | ---: |")
    all_keys = sorted(set(result.counts_before) | set(result.counts_after))
    for key in all_keys:
        before = int(result.counts_before.get(key, 0))
        after = int(result.counts_after.get(key, 0))
        lines.append(f"| `{key}` | {before} | {after} | {after - before} |")
    lines.append("")
    lines.append("## Header Checks")
    for key, value in sorted(result.headers_summary.items(), key=lambda item: item[0]):
        safe_value = str(value).replace("|", "\\|")
        lines.append(f"- {key}: `{safe_value}`")
    lines.append("")
    lines.append("## Smoke Tool Status")
    if result.smoke_steps:
        for step in result.smoke_steps:
            marker = "PASS" if step.ok else "FAIL"
            lines.append(f"- [{marker}] {step.name}: {step.detail}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## User Flow Steps")
    if result.user_steps:
        for step in result.user_steps:
            marker = "PASS" if step.ok else "FAIL"
            lines.append(f"- [{marker}] {step.name}: {step.detail}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Admin Flow Steps")
    if result.admin_steps:
        for step in result.admin_steps:
            marker = "PASS" if step.ok else "FAIL"
            lines.append(f"- [{marker}] {step.name}: {step.detail}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Top Suspects")
    if result.failures:
        for failure in result.failures:
            lines.append(f"- {failure}")
    else:
        lines.append("- none")
    lines.append("")
    lines.append("## Recommendations")
    for recommendation in result.recommendations:
        lines.append(f"- {recommendation}")
    lines.append("")
    lines.append("## Artifacts")
    lines.append(f"- user_email: `{result.artifacts.user_email or '-'}`")
    lines.append(f"- user_submission_title: `{result.artifacts.user_submission_title or '-'}`")
    lines.append(f"- approved_recipe_id: `{result.artifacts.approved_recipe_id or '-'}`")
    lines.append(f"- pending_image_request_id: `{result.artifacts.pending_image_request_id or '-'}`")
    lines.append("")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    report_path = _normalize_report_path(args.report)
    result = run_last_chance(
        real_api=bool(args.real_api),
        mock_translation_write=bool(args.mock_translation_write),
        report_path=report_path,
    )
    print(f"Report written: {report_path}")
    print(f"Status: {'PASS' if result.ok else 'FAIL'}")
    if result.failures:
        for item in result.failures:
            print(f"- FAIL: {item}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

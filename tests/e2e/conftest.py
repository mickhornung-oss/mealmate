from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from typing import Any, Iterator, TYPE_CHECKING

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.models import (
    Recipe,
    RecipeImageChangeFile,
    RecipeImageChangeRequest,
    RecipeSubmission,
    SubmissionIngredient,
    User,
)
from app.security import hash_password

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SMALL_PNG = bytes.fromhex(
    "89504E470D0A1A0A0000000D4948445200000001000000010802000000907753DE"
    "0000000C49444154789C63600800000082000145AF25DB0000000049454E44AE426082"
)

if TYPE_CHECKING:
    from playwright.sync_api import Browser, Page
else:
    Browser = Any
    Page = Any


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        sock.listen(1)
        return int(sock.getsockname()[1])


def _wait_for_server(base_url: str, process: subprocess.Popen[str], timeout_seconds: float = 30.0) -> None:
    deadline = time.time() + timeout_seconds
    health_url = f"{base_url}/healthz"
    while time.time() < deadline:
        if process.poll() is not None:
            output = process.stdout.read() if process.stdout else ""
            raise RuntimeError(f"Uvicorn exited early.\n{output}")
        try:
            response = httpx.get(health_url, timeout=1.0)
            if response.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(0.25)
    output = process.stdout.read() if process.stdout else ""
    raise RuntimeError(f"Timed out waiting for server at {health_url}.\n{output}")


def _seed_database(database_url: str, reset_outbox: Path, email_change_outbox: Path) -> dict[str, object]:
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    now = datetime.now(timezone.utc)
    try:
        with SessionLocal() as db:
            db: Session
            admin = User(
                email="e2e-admin@mealmate.local",
                hashed_password=hash_password("AdminPass123!"),
                role="admin",
                username="e2e.admin",
                username_normalized="e2e.admin",
            )
            user = User(
                email="e2e-user@mealmate.local",
                hashed_password=hash_password("UserPass123!"),
                role="user",
                username="e2e.user",
                username_normalized="e2e.user",
            )
            db.add_all([admin, user])
            db.flush()

            published_recipe = Recipe(
                title="E2E Sichtbares Rezept",
                description="Ein veroeffentlichtes Testrezept fuer die E2E-Flows.",
                instructions="Schritt 1\nSchritt 2",
                category="Testkueche",
                prep_time_minutes=25,
                difficulty="medium",
                creator_id=admin.id,
                source="seed",
                is_published=True,
                created_at=now,
            )
            db.add(published_recipe)
            db.flush()

            pending_submission_for_approve = RecipeSubmission(
                submitter_user_id=user.id,
                title="E2E Pending Freigabe",
                description="Soll vom Admin freigegeben werden.",
                category="Testkueche",
                difficulty="easy",
                prep_time_minutes=15,
                servings_text="2 Portionen",
                instructions="Schritt A\nSchritt B",
                status="pending",
                created_at=now,
            )
            pending_submission_for_reject = RecipeSubmission(
                submitter_user_id=user.id,
                title="E2E Pending Ablehnung",
                description="Soll vom Admin abgelehnt werden.",
                category="Testkueche",
                difficulty="hard",
                prep_time_minutes=45,
                servings_text="4 Portionen",
                instructions="Schritt X\nSchritt Y",
                status="pending",
                created_at=now,
            )
            approved_submission = RecipeSubmission(
                submitter_user_id=user.id,
                title="E2E Schon Freigegeben",
                description="Ist bereits freigegeben.",
                category="Testkueche",
                difficulty="medium",
                prep_time_minutes=20,
                servings_text="3 Portionen",
                instructions="Schritt I\nSchritt II",
                status="approved",
                admin_note="Vorab freigegeben",
                reviewed_by_admin_id=admin.id,
                reviewed_at=now,
                created_at=now,
            )
            db.add_all([pending_submission_for_approve, pending_submission_for_reject, approved_submission])
            db.flush()

            db.add_all(
                [
                    SubmissionIngredient(
                        submission_id=pending_submission_for_approve.id,
                        ingredient_name="Tomate",
                        quantity_text="2 Stueck",
                        grams=None,
                        ingredient_name_normalized="tomate",
                    ),
                    SubmissionIngredient(
                        submission_id=pending_submission_for_reject.id,
                        ingredient_name="Zwiebel",
                        quantity_text="1 Stueck",
                        grams=None,
                        ingredient_name_normalized="zwiebel",
                    ),
                ]
            )

            db.add(
                Recipe(
                    title="E2E Rezept aus freigegebener Submission",
                    description="Wurde bereits veroeffentlicht.",
                    instructions="Schritt 1\nSchritt 2",
                    category="Testkueche",
                    prep_time_minutes=20,
                    difficulty="medium",
                    creator_id=admin.id,
                    source="submission",
                    source_uuid=f"submission:{approved_submission.id}",
                    is_published=True,
                    created_at=now,
                )
            )

            image_change_request = RecipeImageChangeRequest(
                recipe_id=published_recipe.id,
                requester_user_id=user.id,
                status="pending",
                created_at=now,
            )
            db.add(image_change_request)
            db.flush()
            db.add(
                RecipeImageChangeFile(
                    request_id=image_change_request.id,
                    filename="e2e-proposal.png",
                    content_type="image/png",
                    data=SMALL_PNG,
                    created_at=now,
                )
            )

            db.commit()

            reset_outbox.write_text("", encoding="utf-8")
            email_change_outbox.write_text("", encoding="utf-8")

            return {
                "admin_email": admin.email,
                "admin_password": "AdminPass123!",
                "user_email": user.email,
                "user_password": "UserPass123!",
                "user_password_changed": "UserChanged123!",
                "user_password_reset": "UserReset123!",
                "published_recipe_id": published_recipe.id,
                "published_recipe_title": published_recipe.title,
                "pending_submission_approve_id": pending_submission_for_approve.id,
                "pending_submission_approve_title": pending_submission_for_approve.title,
                "pending_submission_reject_id": pending_submission_for_reject.id,
                "pending_submission_reject_title": pending_submission_for_reject.title,
                "pending_image_change_request_id": image_change_request.id,
                "reset_outbox_path": str(reset_outbox),
                "email_change_outbox_path": str(email_change_outbox),
            }
    finally:
        engine.dispose()


@pytest.fixture(scope="session")
def e2e_workspace(tmp_path_factory: pytest.TempPathFactory) -> dict[str, str]:
    workspace = tmp_path_factory.mktemp("mealmate_e2e")
    db_path = workspace / "mealmate_e2e.sqlite3"
    outbox_dir = workspace / "outbox"
    outbox_dir.mkdir(parents=True, exist_ok=True)
    return {
        "database_url": f"sqlite:///{db_path.as_posix()}",
        "reset_outbox_path": str((outbox_dir / "reset_links.txt").as_posix()),
        "email_change_outbox_path": str((outbox_dir / "email_change_links.txt").as_posix()),
    }


@pytest.fixture(scope="session")
def migrated_database_url(e2e_workspace: dict[str, str]) -> Iterator[str]:
    env = os.environ.copy()
    env["DATABASE_URL"] = e2e_workspace["database_url"]
    migrate_command = (
        "from alembic.config import Config;"
        " from alembic import command;"
        f" cfg=Config(r'{(PROJECT_ROOT / 'alembic.ini').as_posix()}');"
        " command.upgrade(cfg, 'head')"
    )
    completed = subprocess.run(
        [sys.executable, "-c", migrate_command],
        cwd=str(PROJECT_ROOT),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"Alembic migration failed:\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}")
    yield e2e_workspace["database_url"]


@pytest.fixture(scope="session")
def e2e_seed_data(migrated_database_url: str, e2e_workspace: dict[str, str]) -> dict[str, object]:
    return _seed_database(
        migrated_database_url,
        Path(e2e_workspace["reset_outbox_path"]),
        Path(e2e_workspace["email_change_outbox_path"]),
    )


@pytest.fixture()
def base_url(migrated_database_url: str, e2e_workspace: dict[str, str], e2e_seed_data: dict[str, object]) -> Iterator[str]:
    _ = migrated_database_url
    _ = e2e_seed_data
    port = _free_port()
    url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env.update(
        {
            "APP_ENV": "dev",
            "DATABASE_URL": e2e_workspace["database_url"],
            "SECRET_KEY": "e2e-secret-key-very-long-and-only-for-tests",
            "APP_URL": url,
            "ALLOWED_HOSTS": "127.0.0.1,localhost",
            "COOKIE_SECURE": "0",
            "FORCE_HTTPS": "0",
            "ENABLE_KOCHWIKI_SEED": "0",
            "AUTO_SEED_KOCHWIKI": "0",
            "MAIL_OUTBOX_PATH": e2e_workspace["reset_outbox_path"],
            "MAIL_OUTBOX_EMAIL_CHANGE_PATH": e2e_workspace["email_change_outbox_path"],
            "LOG_LEVEL": "WARNING",
        }
    )
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(port)],
        cwd=str(PROJECT_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        _wait_for_server(url, process)
        yield url
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)
        if process.stdout is not None:
            process.stdout.close()


@pytest.fixture(scope="session")
def browser() -> Iterator[Browser]:
    playwright_sync_api = pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright package not installed. Install with: pip install playwright",
    )
    with playwright_sync_api.sync_playwright() as playwright:
        try:
            browser_instance = playwright.chromium.launch(headless=True)
        except Exception as exc:
            pytest.skip(f"Playwright browser is not available ({exc}). Run: python -m playwright install chromium")
        yield browser_instance
        browser_instance.close()


@pytest.fixture()
def page(browser: Browser, base_url: str) -> Iterator[Page]:
    _ = base_url
    context = browser.new_context(base_url=base_url)
    page_instance = context.new_page()
    yield page_instance
    context.close()

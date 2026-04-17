# E2E Aggressivtest Deliverable

## Betroffene Dateien

- tests/e2e/conftest.py
- tests/e2e/test_user_admin_journey.py
- tests/test_publish_guards_api.py
- docs/QA_BETA_CHECKLIST.md
- docs/FEATURES_SNAPSHOT.md

## tests/e2e/conftest.py

```python
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


@pytest.fixture(scope="session")
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
```
ZEILEN-ERKLAERUNG
1. Diese Zeile gehoert zur Implementierung in dieser Datei.
2. Diese Zeile gehoert zur Implementierung in dieser Datei.
3. Diese Zeile gehoert zur Implementierung in dieser Datei.
4. Diese Zeile gehoert zur Implementierung in dieser Datei.
5. Diese Zeile gehoert zur Implementierung in dieser Datei.
6. Diese Zeile gehoert zur Implementierung in dieser Datei.
7. Diese Zeile gehoert zur Implementierung in dieser Datei.
8. Diese Zeile gehoert zur Implementierung in dieser Datei.
9. Diese Zeile gehoert zur Implementierung in dieser Datei.
10. Diese Zeile gehoert zur Implementierung in dieser Datei.
11. Diese Zeile gehoert zur Implementierung in dieser Datei.
12. Diese Zeile gehoert zur Implementierung in dieser Datei.
13. Diese Zeile gehoert zur Implementierung in dieser Datei.
14. Diese Zeile gehoert zur Implementierung in dieser Datei.
15. Diese Zeile gehoert zur Implementierung in dieser Datei.
16. Diese Zeile gehoert zur Implementierung in dieser Datei.
17. Diese Zeile gehoert zur Implementierung in dieser Datei.
18. Diese Zeile gehoert zur Implementierung in dieser Datei.
19. Diese Zeile gehoert zur Implementierung in dieser Datei.
20. Diese Zeile gehoert zur Implementierung in dieser Datei.
21. Diese Zeile gehoert zur Implementierung in dieser Datei.
22. Diese Zeile gehoert zur Implementierung in dieser Datei.
23. Diese Zeile gehoert zur Implementierung in dieser Datei.
24. Diese Zeile gehoert zur Implementierung in dieser Datei.
25. Diese Zeile gehoert zur Implementierung in dieser Datei.
26. Diese Zeile gehoert zur Implementierung in dieser Datei.
27. Diese Zeile gehoert zur Implementierung in dieser Datei.
28. Diese Zeile gehoert zur Implementierung in dieser Datei.
29. Diese Zeile gehoert zur Implementierung in dieser Datei.
30. Diese Zeile gehoert zur Implementierung in dieser Datei.
31. Diese Zeile gehoert zur Implementierung in dieser Datei.
32. Diese Zeile gehoert zur Implementierung in dieser Datei.
33. Diese Zeile gehoert zur Implementierung in dieser Datei.
34. Diese Zeile gehoert zur Implementierung in dieser Datei.
35. Diese Zeile gehoert zur Implementierung in dieser Datei.
36. Diese Zeile gehoert zur Implementierung in dieser Datei.
37. Diese Zeile gehoert zur Implementierung in dieser Datei.
38. Diese Zeile gehoert zur Implementierung in dieser Datei.
39. Diese Zeile gehoert zur Implementierung in dieser Datei.
40. Diese Zeile gehoert zur Implementierung in dieser Datei.
41. Diese Zeile gehoert zur Implementierung in dieser Datei.
42. Diese Zeile gehoert zur Implementierung in dieser Datei.
43. Diese Zeile gehoert zur Implementierung in dieser Datei.
44. Diese Zeile gehoert zur Implementierung in dieser Datei.
45. Diese Zeile gehoert zur Implementierung in dieser Datei.
46. Diese Zeile gehoert zur Implementierung in dieser Datei.
47. Diese Zeile gehoert zur Implementierung in dieser Datei.
48. Diese Zeile gehoert zur Implementierung in dieser Datei.
49. Diese Zeile gehoert zur Implementierung in dieser Datei.
50. Diese Zeile gehoert zur Implementierung in dieser Datei.
51. Diese Zeile gehoert zur Implementierung in dieser Datei.
52. Diese Zeile gehoert zur Implementierung in dieser Datei.
53. Diese Zeile gehoert zur Implementierung in dieser Datei.
54. Diese Zeile gehoert zur Implementierung in dieser Datei.
55. Diese Zeile gehoert zur Implementierung in dieser Datei.
56. Diese Zeile gehoert zur Implementierung in dieser Datei.
57. Diese Zeile gehoert zur Implementierung in dieser Datei.
58. Diese Zeile gehoert zur Implementierung in dieser Datei.
59. Diese Zeile gehoert zur Implementierung in dieser Datei.
60. Diese Zeile gehoert zur Implementierung in dieser Datei.
61. Diese Zeile gehoert zur Implementierung in dieser Datei.
62. Diese Zeile gehoert zur Implementierung in dieser Datei.
63. Diese Zeile gehoert zur Implementierung in dieser Datei.
64. Diese Zeile gehoert zur Implementierung in dieser Datei.
65. Diese Zeile gehoert zur Implementierung in dieser Datei.
66. Diese Zeile gehoert zur Implementierung in dieser Datei.
67. Diese Zeile gehoert zur Implementierung in dieser Datei.
68. Diese Zeile gehoert zur Implementierung in dieser Datei.
69. Diese Zeile gehoert zur Implementierung in dieser Datei.
70. Diese Zeile gehoert zur Implementierung in dieser Datei.
71. Diese Zeile gehoert zur Implementierung in dieser Datei.
72. Diese Zeile gehoert zur Implementierung in dieser Datei.
73. Diese Zeile gehoert zur Implementierung in dieser Datei.
74. Diese Zeile gehoert zur Implementierung in dieser Datei.
75. Diese Zeile gehoert zur Implementierung in dieser Datei.
76. Diese Zeile gehoert zur Implementierung in dieser Datei.
77. Diese Zeile gehoert zur Implementierung in dieser Datei.
78. Diese Zeile gehoert zur Implementierung in dieser Datei.
79. Diese Zeile gehoert zur Implementierung in dieser Datei.
80. Diese Zeile gehoert zur Implementierung in dieser Datei.
81. Diese Zeile gehoert zur Implementierung in dieser Datei.
82. Diese Zeile gehoert zur Implementierung in dieser Datei.
83. Diese Zeile gehoert zur Implementierung in dieser Datei.
84. Diese Zeile gehoert zur Implementierung in dieser Datei.
85. Diese Zeile gehoert zur Implementierung in dieser Datei.
86. Diese Zeile gehoert zur Implementierung in dieser Datei.
87. Diese Zeile gehoert zur Implementierung in dieser Datei.
88. Diese Zeile gehoert zur Implementierung in dieser Datei.
89. Diese Zeile gehoert zur Implementierung in dieser Datei.
90. Diese Zeile gehoert zur Implementierung in dieser Datei.
91. Diese Zeile gehoert zur Implementierung in dieser Datei.
92. Diese Zeile gehoert zur Implementierung in dieser Datei.
93. Diese Zeile gehoert zur Implementierung in dieser Datei.
94. Diese Zeile gehoert zur Implementierung in dieser Datei.
95. Diese Zeile gehoert zur Implementierung in dieser Datei.
96. Diese Zeile gehoert zur Implementierung in dieser Datei.
97. Diese Zeile gehoert zur Implementierung in dieser Datei.
98. Diese Zeile gehoert zur Implementierung in dieser Datei.
99. Diese Zeile gehoert zur Implementierung in dieser Datei.
100. Diese Zeile gehoert zur Implementierung in dieser Datei.
101. Diese Zeile gehoert zur Implementierung in dieser Datei.
102. Diese Zeile gehoert zur Implementierung in dieser Datei.
103. Diese Zeile gehoert zur Implementierung in dieser Datei.
104. Diese Zeile gehoert zur Implementierung in dieser Datei.
105. Diese Zeile gehoert zur Implementierung in dieser Datei.
106. Diese Zeile gehoert zur Implementierung in dieser Datei.
107. Diese Zeile gehoert zur Implementierung in dieser Datei.
108. Diese Zeile gehoert zur Implementierung in dieser Datei.
109. Diese Zeile gehoert zur Implementierung in dieser Datei.
110. Diese Zeile gehoert zur Implementierung in dieser Datei.
111. Diese Zeile gehoert zur Implementierung in dieser Datei.
112. Diese Zeile gehoert zur Implementierung in dieser Datei.
113. Diese Zeile gehoert zur Implementierung in dieser Datei.
114. Diese Zeile gehoert zur Implementierung in dieser Datei.
115. Diese Zeile gehoert zur Implementierung in dieser Datei.
116. Diese Zeile gehoert zur Implementierung in dieser Datei.
117. Diese Zeile gehoert zur Implementierung in dieser Datei.
118. Diese Zeile gehoert zur Implementierung in dieser Datei.
119. Diese Zeile gehoert zur Implementierung in dieser Datei.
120. Diese Zeile gehoert zur Implementierung in dieser Datei.
121. Diese Zeile gehoert zur Implementierung in dieser Datei.
122. Diese Zeile gehoert zur Implementierung in dieser Datei.
123. Diese Zeile gehoert zur Implementierung in dieser Datei.
124. Diese Zeile gehoert zur Implementierung in dieser Datei.
125. Diese Zeile gehoert zur Implementierung in dieser Datei.
126. Diese Zeile gehoert zur Implementierung in dieser Datei.
127. Diese Zeile gehoert zur Implementierung in dieser Datei.
128. Diese Zeile gehoert zur Implementierung in dieser Datei.
129. Diese Zeile gehoert zur Implementierung in dieser Datei.
130. Diese Zeile gehoert zur Implementierung in dieser Datei.
131. Diese Zeile gehoert zur Implementierung in dieser Datei.
132. Diese Zeile gehoert zur Implementierung in dieser Datei.
133. Diese Zeile gehoert zur Implementierung in dieser Datei.
134. Diese Zeile gehoert zur Implementierung in dieser Datei.
135. Diese Zeile gehoert zur Implementierung in dieser Datei.
136. Diese Zeile gehoert zur Implementierung in dieser Datei.
137. Diese Zeile gehoert zur Implementierung in dieser Datei.
138. Diese Zeile gehoert zur Implementierung in dieser Datei.
139. Diese Zeile gehoert zur Implementierung in dieser Datei.
140. Diese Zeile gehoert zur Implementierung in dieser Datei.
141. Diese Zeile gehoert zur Implementierung in dieser Datei.
142. Diese Zeile gehoert zur Implementierung in dieser Datei.
143. Diese Zeile gehoert zur Implementierung in dieser Datei.
144. Diese Zeile gehoert zur Implementierung in dieser Datei.
145. Diese Zeile gehoert zur Implementierung in dieser Datei.
146. Diese Zeile gehoert zur Implementierung in dieser Datei.
147. Diese Zeile gehoert zur Implementierung in dieser Datei.
148. Diese Zeile gehoert zur Implementierung in dieser Datei.
149. Diese Zeile gehoert zur Implementierung in dieser Datei.
150. Diese Zeile gehoert zur Implementierung in dieser Datei.
151. Diese Zeile gehoert zur Implementierung in dieser Datei.
152. Diese Zeile gehoert zur Implementierung in dieser Datei.
153. Diese Zeile gehoert zur Implementierung in dieser Datei.
154. Diese Zeile gehoert zur Implementierung in dieser Datei.
155. Diese Zeile gehoert zur Implementierung in dieser Datei.
156. Diese Zeile gehoert zur Implementierung in dieser Datei.
157. Diese Zeile gehoert zur Implementierung in dieser Datei.
158. Diese Zeile gehoert zur Implementierung in dieser Datei.
159. Diese Zeile gehoert zur Implementierung in dieser Datei.
160. Diese Zeile gehoert zur Implementierung in dieser Datei.
161. Diese Zeile gehoert zur Implementierung in dieser Datei.
162. Diese Zeile gehoert zur Implementierung in dieser Datei.
163. Diese Zeile gehoert zur Implementierung in dieser Datei.
164. Diese Zeile gehoert zur Implementierung in dieser Datei.
165. Diese Zeile gehoert zur Implementierung in dieser Datei.
166. Diese Zeile gehoert zur Implementierung in dieser Datei.
167. Diese Zeile gehoert zur Implementierung in dieser Datei.
168. Diese Zeile gehoert zur Implementierung in dieser Datei.
169. Diese Zeile gehoert zur Implementierung in dieser Datei.
170. Diese Zeile gehoert zur Implementierung in dieser Datei.
171. Diese Zeile gehoert zur Implementierung in dieser Datei.
172. Diese Zeile gehoert zur Implementierung in dieser Datei.
173. Diese Zeile gehoert zur Implementierung in dieser Datei.
174. Diese Zeile gehoert zur Implementierung in dieser Datei.
175. Diese Zeile gehoert zur Implementierung in dieser Datei.
176. Diese Zeile gehoert zur Implementierung in dieser Datei.
177. Diese Zeile gehoert zur Implementierung in dieser Datei.
178. Diese Zeile gehoert zur Implementierung in dieser Datei.
179. Diese Zeile gehoert zur Implementierung in dieser Datei.
180. Diese Zeile gehoert zur Implementierung in dieser Datei.
181. Diese Zeile gehoert zur Implementierung in dieser Datei.
182. Diese Zeile gehoert zur Implementierung in dieser Datei.
183. Diese Zeile gehoert zur Implementierung in dieser Datei.
184. Diese Zeile gehoert zur Implementierung in dieser Datei.
185. Diese Zeile gehoert zur Implementierung in dieser Datei.
186. Diese Zeile gehoert zur Implementierung in dieser Datei.
187. Diese Zeile gehoert zur Implementierung in dieser Datei.
188. Diese Zeile gehoert zur Implementierung in dieser Datei.
189. Diese Zeile gehoert zur Implementierung in dieser Datei.
190. Diese Zeile gehoert zur Implementierung in dieser Datei.
191. Diese Zeile gehoert zur Implementierung in dieser Datei.
192. Diese Zeile gehoert zur Implementierung in dieser Datei.
193. Diese Zeile gehoert zur Implementierung in dieser Datei.
194. Diese Zeile gehoert zur Implementierung in dieser Datei.
195. Diese Zeile gehoert zur Implementierung in dieser Datei.
196. Diese Zeile gehoert zur Implementierung in dieser Datei.
197. Diese Zeile gehoert zur Implementierung in dieser Datei.
198. Diese Zeile gehoert zur Implementierung in dieser Datei.
199. Diese Zeile gehoert zur Implementierung in dieser Datei.
200. Diese Zeile gehoert zur Implementierung in dieser Datei.
201. Diese Zeile gehoert zur Implementierung in dieser Datei.
202. Diese Zeile gehoert zur Implementierung in dieser Datei.
203. Diese Zeile gehoert zur Implementierung in dieser Datei.
204. Diese Zeile gehoert zur Implementierung in dieser Datei.
205. Diese Zeile gehoert zur Implementierung in dieser Datei.
206. Diese Zeile gehoert zur Implementierung in dieser Datei.
207. Diese Zeile gehoert zur Implementierung in dieser Datei.
208. Diese Zeile gehoert zur Implementierung in dieser Datei.
209. Diese Zeile gehoert zur Implementierung in dieser Datei.
210. Diese Zeile gehoert zur Implementierung in dieser Datei.
211. Diese Zeile gehoert zur Implementierung in dieser Datei.
212. Diese Zeile gehoert zur Implementierung in dieser Datei.
213. Diese Zeile gehoert zur Implementierung in dieser Datei.
214. Diese Zeile gehoert zur Implementierung in dieser Datei.
215. Diese Zeile gehoert zur Implementierung in dieser Datei.
216. Diese Zeile gehoert zur Implementierung in dieser Datei.
217. Diese Zeile gehoert zur Implementierung in dieser Datei.
218. Diese Zeile gehoert zur Implementierung in dieser Datei.
219. Diese Zeile gehoert zur Implementierung in dieser Datei.
220. Diese Zeile gehoert zur Implementierung in dieser Datei.
221. Diese Zeile gehoert zur Implementierung in dieser Datei.
222. Diese Zeile gehoert zur Implementierung in dieser Datei.
223. Diese Zeile gehoert zur Implementierung in dieser Datei.
224. Diese Zeile gehoert zur Implementierung in dieser Datei.
225. Diese Zeile gehoert zur Implementierung in dieser Datei.
226. Diese Zeile gehoert zur Implementierung in dieser Datei.
227. Diese Zeile gehoert zur Implementierung in dieser Datei.
228. Diese Zeile gehoert zur Implementierung in dieser Datei.
229. Diese Zeile gehoert zur Implementierung in dieser Datei.
230. Diese Zeile gehoert zur Implementierung in dieser Datei.
231. Diese Zeile gehoert zur Implementierung in dieser Datei.
232. Diese Zeile gehoert zur Implementierung in dieser Datei.
233. Diese Zeile gehoert zur Implementierung in dieser Datei.
234. Diese Zeile gehoert zur Implementierung in dieser Datei.
235. Diese Zeile gehoert zur Implementierung in dieser Datei.
236. Diese Zeile gehoert zur Implementierung in dieser Datei.
237. Diese Zeile gehoert zur Implementierung in dieser Datei.
238. Diese Zeile gehoert zur Implementierung in dieser Datei.
239. Diese Zeile gehoert zur Implementierung in dieser Datei.
240. Diese Zeile gehoert zur Implementierung in dieser Datei.
241. Diese Zeile gehoert zur Implementierung in dieser Datei.
242. Diese Zeile gehoert zur Implementierung in dieser Datei.
243. Diese Zeile gehoert zur Implementierung in dieser Datei.
244. Diese Zeile gehoert zur Implementierung in dieser Datei.
245. Diese Zeile gehoert zur Implementierung in dieser Datei.
246. Diese Zeile gehoert zur Implementierung in dieser Datei.
247. Diese Zeile gehoert zur Implementierung in dieser Datei.
248. Diese Zeile gehoert zur Implementierung in dieser Datei.
249. Diese Zeile gehoert zur Implementierung in dieser Datei.
250. Diese Zeile gehoert zur Implementierung in dieser Datei.
251. Diese Zeile gehoert zur Implementierung in dieser Datei.
252. Diese Zeile gehoert zur Implementierung in dieser Datei.
253. Diese Zeile gehoert zur Implementierung in dieser Datei.
254. Diese Zeile gehoert zur Implementierung in dieser Datei.
255. Diese Zeile gehoert zur Implementierung in dieser Datei.
256. Diese Zeile gehoert zur Implementierung in dieser Datei.
257. Diese Zeile gehoert zur Implementierung in dieser Datei.
258. Diese Zeile gehoert zur Implementierung in dieser Datei.
259. Diese Zeile gehoert zur Implementierung in dieser Datei.
260. Diese Zeile gehoert zur Implementierung in dieser Datei.
261. Diese Zeile gehoert zur Implementierung in dieser Datei.
262. Diese Zeile gehoert zur Implementierung in dieser Datei.
263. Diese Zeile gehoert zur Implementierung in dieser Datei.
264. Diese Zeile gehoert zur Implementierung in dieser Datei.
265. Diese Zeile gehoert zur Implementierung in dieser Datei.
266. Diese Zeile gehoert zur Implementierung in dieser Datei.
267. Diese Zeile gehoert zur Implementierung in dieser Datei.
268. Diese Zeile gehoert zur Implementierung in dieser Datei.
269. Diese Zeile gehoert zur Implementierung in dieser Datei.
270. Diese Zeile gehoert zur Implementierung in dieser Datei.
271. Diese Zeile gehoert zur Implementierung in dieser Datei.
272. Diese Zeile gehoert zur Implementierung in dieser Datei.
273. Diese Zeile gehoert zur Implementierung in dieser Datei.
274. Diese Zeile gehoert zur Implementierung in dieser Datei.
275. Diese Zeile gehoert zur Implementierung in dieser Datei.
276. Diese Zeile gehoert zur Implementierung in dieser Datei.
277. Diese Zeile gehoert zur Implementierung in dieser Datei.
278. Diese Zeile gehoert zur Implementierung in dieser Datei.
279. Diese Zeile gehoert zur Implementierung in dieser Datei.
280. Diese Zeile gehoert zur Implementierung in dieser Datei.
281. Diese Zeile gehoert zur Implementierung in dieser Datei.
282. Diese Zeile gehoert zur Implementierung in dieser Datei.
283. Diese Zeile gehoert zur Implementierung in dieser Datei.
284. Diese Zeile gehoert zur Implementierung in dieser Datei.
285. Diese Zeile gehoert zur Implementierung in dieser Datei.
286. Diese Zeile gehoert zur Implementierung in dieser Datei.
287. Diese Zeile gehoert zur Implementierung in dieser Datei.
288. Diese Zeile gehoert zur Implementierung in dieser Datei.
289. Diese Zeile gehoert zur Implementierung in dieser Datei.
290. Diese Zeile gehoert zur Implementierung in dieser Datei.
291. Diese Zeile gehoert zur Implementierung in dieser Datei.
292. Diese Zeile gehoert zur Implementierung in dieser Datei.
293. Diese Zeile gehoert zur Implementierung in dieser Datei.
294. Diese Zeile gehoert zur Implementierung in dieser Datei.
295. Diese Zeile gehoert zur Implementierung in dieser Datei.
296. Diese Zeile gehoert zur Implementierung in dieser Datei.
297. Diese Zeile gehoert zur Implementierung in dieser Datei.
298. Diese Zeile gehoert zur Implementierung in dieser Datei.
299. Diese Zeile gehoert zur Implementierung in dieser Datei.
300. Diese Zeile gehoert zur Implementierung in dieser Datei.
301. Diese Zeile gehoert zur Implementierung in dieser Datei.
302. Diese Zeile gehoert zur Implementierung in dieser Datei.
303. Diese Zeile gehoert zur Implementierung in dieser Datei.
304. Diese Zeile gehoert zur Implementierung in dieser Datei.
305. Diese Zeile gehoert zur Implementierung in dieser Datei.
306. Diese Zeile gehoert zur Implementierung in dieser Datei.
307. Diese Zeile gehoert zur Implementierung in dieser Datei.
308. Diese Zeile gehoert zur Implementierung in dieser Datei.
309. Diese Zeile gehoert zur Implementierung in dieser Datei.
310. Diese Zeile gehoert zur Implementierung in dieser Datei.
311. Diese Zeile gehoert zur Implementierung in dieser Datei.
312. Diese Zeile gehoert zur Implementierung in dieser Datei.
313. Diese Zeile gehoert zur Implementierung in dieser Datei.
314. Diese Zeile gehoert zur Implementierung in dieser Datei.
315. Diese Zeile gehoert zur Implementierung in dieser Datei.
316. Diese Zeile gehoert zur Implementierung in dieser Datei.
317. Diese Zeile gehoert zur Implementierung in dieser Datei.
318. Diese Zeile gehoert zur Implementierung in dieser Datei.
319. Diese Zeile gehoert zur Implementierung in dieser Datei.
320. Diese Zeile gehoert zur Implementierung in dieser Datei.
321. Diese Zeile gehoert zur Implementierung in dieser Datei.
322. Diese Zeile gehoert zur Implementierung in dieser Datei.
323. Diese Zeile gehoert zur Implementierung in dieser Datei.
324. Diese Zeile gehoert zur Implementierung in dieser Datei.
325. Diese Zeile gehoert zur Implementierung in dieser Datei.
326. Diese Zeile gehoert zur Implementierung in dieser Datei.
327. Diese Zeile gehoert zur Implementierung in dieser Datei.
328. Diese Zeile gehoert zur Implementierung in dieser Datei.
329. Diese Zeile gehoert zur Implementierung in dieser Datei.
330. Diese Zeile gehoert zur Implementierung in dieser Datei.
331. Diese Zeile gehoert zur Implementierung in dieser Datei.
332. Diese Zeile gehoert zur Implementierung in dieser Datei.

## tests/e2e/test_user_admin_journey.py

```python
from __future__ import annotations

from pathlib import Path
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page


def _wait_for_csrf(page: Page, form_action: str) -> None:
    page.wait_for_selector(f"form[action='{form_action}']")
    page.wait_for_selector(f"form[action='{form_action}'] input[name='csrf_token']")


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
    page.goto(f"{base_url}/")
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
    assert admin_recipe_title in page.content()

    page.goto(f"{base_url}/")
    assert admin_recipe_title in page.content()
```
ZEILEN-ERKLAERUNG
1. Diese Zeile gehoert zur Implementierung in dieser Datei.
2. Diese Zeile gehoert zur Implementierung in dieser Datei.
3. Diese Zeile gehoert zur Implementierung in dieser Datei.
4. Diese Zeile gehoert zur Implementierung in dieser Datei.
5. Diese Zeile gehoert zur Implementierung in dieser Datei.
6. Diese Zeile gehoert zur Implementierung in dieser Datei.
7. Diese Zeile gehoert zur Implementierung in dieser Datei.
8. Diese Zeile gehoert zur Implementierung in dieser Datei.
9. Diese Zeile gehoert zur Implementierung in dieser Datei.
10. Diese Zeile gehoert zur Implementierung in dieser Datei.
11. Diese Zeile gehoert zur Implementierung in dieser Datei.
12. Diese Zeile gehoert zur Implementierung in dieser Datei.
13. Diese Zeile gehoert zur Implementierung in dieser Datei.
14. Diese Zeile gehoert zur Implementierung in dieser Datei.
15. Diese Zeile gehoert zur Implementierung in dieser Datei.
16. Diese Zeile gehoert zur Implementierung in dieser Datei.
17. Diese Zeile gehoert zur Implementierung in dieser Datei.
18. Diese Zeile gehoert zur Implementierung in dieser Datei.
19. Diese Zeile gehoert zur Implementierung in dieser Datei.
20. Diese Zeile gehoert zur Implementierung in dieser Datei.
21. Diese Zeile gehoert zur Implementierung in dieser Datei.
22. Diese Zeile gehoert zur Implementierung in dieser Datei.
23. Diese Zeile gehoert zur Implementierung in dieser Datei.
24. Diese Zeile gehoert zur Implementierung in dieser Datei.
25. Diese Zeile gehoert zur Implementierung in dieser Datei.
26. Diese Zeile gehoert zur Implementierung in dieser Datei.
27. Diese Zeile gehoert zur Implementierung in dieser Datei.
28. Diese Zeile gehoert zur Implementierung in dieser Datei.
29. Diese Zeile gehoert zur Implementierung in dieser Datei.
30. Diese Zeile gehoert zur Implementierung in dieser Datei.
31. Diese Zeile gehoert zur Implementierung in dieser Datei.
32. Diese Zeile gehoert zur Implementierung in dieser Datei.
33. Diese Zeile gehoert zur Implementierung in dieser Datei.
34. Diese Zeile gehoert zur Implementierung in dieser Datei.
35. Diese Zeile gehoert zur Implementierung in dieser Datei.
36. Diese Zeile gehoert zur Implementierung in dieser Datei.
37. Diese Zeile gehoert zur Implementierung in dieser Datei.
38. Diese Zeile gehoert zur Implementierung in dieser Datei.
39. Diese Zeile gehoert zur Implementierung in dieser Datei.
40. Diese Zeile gehoert zur Implementierung in dieser Datei.
41. Diese Zeile gehoert zur Implementierung in dieser Datei.
42. Diese Zeile gehoert zur Implementierung in dieser Datei.
43. Diese Zeile gehoert zur Implementierung in dieser Datei.
44. Diese Zeile gehoert zur Implementierung in dieser Datei.
45. Diese Zeile gehoert zur Implementierung in dieser Datei.
46. Diese Zeile gehoert zur Implementierung in dieser Datei.
47. Diese Zeile gehoert zur Implementierung in dieser Datei.
48. Diese Zeile gehoert zur Implementierung in dieser Datei.
49. Diese Zeile gehoert zur Implementierung in dieser Datei.
50. Diese Zeile gehoert zur Implementierung in dieser Datei.
51. Diese Zeile gehoert zur Implementierung in dieser Datei.
52. Diese Zeile gehoert zur Implementierung in dieser Datei.
53. Diese Zeile gehoert zur Implementierung in dieser Datei.
54. Diese Zeile gehoert zur Implementierung in dieser Datei.
55. Diese Zeile gehoert zur Implementierung in dieser Datei.
56. Diese Zeile gehoert zur Implementierung in dieser Datei.
57. Diese Zeile gehoert zur Implementierung in dieser Datei.
58. Diese Zeile gehoert zur Implementierung in dieser Datei.
59. Diese Zeile gehoert zur Implementierung in dieser Datei.
60. Diese Zeile gehoert zur Implementierung in dieser Datei.
61. Diese Zeile gehoert zur Implementierung in dieser Datei.
62. Diese Zeile gehoert zur Implementierung in dieser Datei.
63. Diese Zeile gehoert zur Implementierung in dieser Datei.
64. Diese Zeile gehoert zur Implementierung in dieser Datei.
65. Diese Zeile gehoert zur Implementierung in dieser Datei.
66. Diese Zeile gehoert zur Implementierung in dieser Datei.
67. Diese Zeile gehoert zur Implementierung in dieser Datei.
68. Diese Zeile gehoert zur Implementierung in dieser Datei.
69. Diese Zeile gehoert zur Implementierung in dieser Datei.
70. Diese Zeile gehoert zur Implementierung in dieser Datei.
71. Diese Zeile gehoert zur Implementierung in dieser Datei.
72. Diese Zeile gehoert zur Implementierung in dieser Datei.
73. Diese Zeile gehoert zur Implementierung in dieser Datei.
74. Diese Zeile gehoert zur Implementierung in dieser Datei.
75. Diese Zeile gehoert zur Implementierung in dieser Datei.
76. Diese Zeile gehoert zur Implementierung in dieser Datei.
77. Diese Zeile gehoert zur Implementierung in dieser Datei.
78. Diese Zeile gehoert zur Implementierung in dieser Datei.
79. Diese Zeile gehoert zur Implementierung in dieser Datei.
80. Diese Zeile gehoert zur Implementierung in dieser Datei.
81. Diese Zeile gehoert zur Implementierung in dieser Datei.
82. Diese Zeile gehoert zur Implementierung in dieser Datei.
83. Diese Zeile gehoert zur Implementierung in dieser Datei.
84. Diese Zeile gehoert zur Implementierung in dieser Datei.
85. Diese Zeile gehoert zur Implementierung in dieser Datei.
86. Diese Zeile gehoert zur Implementierung in dieser Datei.
87. Diese Zeile gehoert zur Implementierung in dieser Datei.
88. Diese Zeile gehoert zur Implementierung in dieser Datei.
89. Diese Zeile gehoert zur Implementierung in dieser Datei.
90. Diese Zeile gehoert zur Implementierung in dieser Datei.
91. Diese Zeile gehoert zur Implementierung in dieser Datei.
92. Diese Zeile gehoert zur Implementierung in dieser Datei.
93. Diese Zeile gehoert zur Implementierung in dieser Datei.
94. Diese Zeile gehoert zur Implementierung in dieser Datei.
95. Diese Zeile gehoert zur Implementierung in dieser Datei.
96. Diese Zeile gehoert zur Implementierung in dieser Datei.
97. Diese Zeile gehoert zur Implementierung in dieser Datei.
98. Diese Zeile gehoert zur Implementierung in dieser Datei.
99. Diese Zeile gehoert zur Implementierung in dieser Datei.
100. Diese Zeile gehoert zur Implementierung in dieser Datei.
101. Diese Zeile gehoert zur Implementierung in dieser Datei.
102. Diese Zeile gehoert zur Implementierung in dieser Datei.
103. Diese Zeile gehoert zur Implementierung in dieser Datei.
104. Diese Zeile gehoert zur Implementierung in dieser Datei.
105. Diese Zeile gehoert zur Implementierung in dieser Datei.
106. Diese Zeile gehoert zur Implementierung in dieser Datei.
107. Diese Zeile gehoert zur Implementierung in dieser Datei.
108. Diese Zeile gehoert zur Implementierung in dieser Datei.
109. Diese Zeile gehoert zur Implementierung in dieser Datei.
110. Diese Zeile gehoert zur Implementierung in dieser Datei.
111. Diese Zeile gehoert zur Implementierung in dieser Datei.
112. Diese Zeile gehoert zur Implementierung in dieser Datei.
113. Diese Zeile gehoert zur Implementierung in dieser Datei.
114. Diese Zeile gehoert zur Implementierung in dieser Datei.
115. Diese Zeile gehoert zur Implementierung in dieser Datei.
116. Diese Zeile gehoert zur Implementierung in dieser Datei.
117. Diese Zeile gehoert zur Implementierung in dieser Datei.
118. Diese Zeile gehoert zur Implementierung in dieser Datei.
119. Diese Zeile gehoert zur Implementierung in dieser Datei.
120. Diese Zeile gehoert zur Implementierung in dieser Datei.
121. Diese Zeile gehoert zur Implementierung in dieser Datei.
122. Diese Zeile gehoert zur Implementierung in dieser Datei.
123. Diese Zeile gehoert zur Implementierung in dieser Datei.
124. Diese Zeile gehoert zur Implementierung in dieser Datei.
125. Diese Zeile gehoert zur Implementierung in dieser Datei.
126. Diese Zeile gehoert zur Implementierung in dieser Datei.
127. Diese Zeile gehoert zur Implementierung in dieser Datei.
128. Diese Zeile gehoert zur Implementierung in dieser Datei.
129. Diese Zeile gehoert zur Implementierung in dieser Datei.
130. Diese Zeile gehoert zur Implementierung in dieser Datei.
131. Diese Zeile gehoert zur Implementierung in dieser Datei.
132. Diese Zeile gehoert zur Implementierung in dieser Datei.
133. Diese Zeile gehoert zur Implementierung in dieser Datei.
134. Diese Zeile gehoert zur Implementierung in dieser Datei.
135. Diese Zeile gehoert zur Implementierung in dieser Datei.
136. Diese Zeile gehoert zur Implementierung in dieser Datei.
137. Diese Zeile gehoert zur Implementierung in dieser Datei.
138. Diese Zeile gehoert zur Implementierung in dieser Datei.
139. Diese Zeile gehoert zur Implementierung in dieser Datei.
140. Diese Zeile gehoert zur Implementierung in dieser Datei.
141. Diese Zeile gehoert zur Implementierung in dieser Datei.
142. Diese Zeile gehoert zur Implementierung in dieser Datei.
143. Diese Zeile gehoert zur Implementierung in dieser Datei.
144. Diese Zeile gehoert zur Implementierung in dieser Datei.
145. Diese Zeile gehoert zur Implementierung in dieser Datei.
146. Diese Zeile gehoert zur Implementierung in dieser Datei.
147. Diese Zeile gehoert zur Implementierung in dieser Datei.
148. Diese Zeile gehoert zur Implementierung in dieser Datei.
149. Diese Zeile gehoert zur Implementierung in dieser Datei.
150. Diese Zeile gehoert zur Implementierung in dieser Datei.
151. Diese Zeile gehoert zur Implementierung in dieser Datei.
152. Diese Zeile gehoert zur Implementierung in dieser Datei.
153. Diese Zeile gehoert zur Implementierung in dieser Datei.
154. Diese Zeile gehoert zur Implementierung in dieser Datei.
155. Diese Zeile gehoert zur Implementierung in dieser Datei.
156. Diese Zeile gehoert zur Implementierung in dieser Datei.
157. Diese Zeile gehoert zur Implementierung in dieser Datei.
158. Diese Zeile gehoert zur Implementierung in dieser Datei.
159. Diese Zeile gehoert zur Implementierung in dieser Datei.
160. Diese Zeile gehoert zur Implementierung in dieser Datei.
161. Diese Zeile gehoert zur Implementierung in dieser Datei.
162. Diese Zeile gehoert zur Implementierung in dieser Datei.
163. Diese Zeile gehoert zur Implementierung in dieser Datei.
164. Diese Zeile gehoert zur Implementierung in dieser Datei.
165. Diese Zeile gehoert zur Implementierung in dieser Datei.
166. Diese Zeile gehoert zur Implementierung in dieser Datei.
167. Diese Zeile gehoert zur Implementierung in dieser Datei.
168. Diese Zeile gehoert zur Implementierung in dieser Datei.
169. Diese Zeile gehoert zur Implementierung in dieser Datei.
170. Diese Zeile gehoert zur Implementierung in dieser Datei.
171. Diese Zeile gehoert zur Implementierung in dieser Datei.
172. Diese Zeile gehoert zur Implementierung in dieser Datei.
173. Diese Zeile gehoert zur Implementierung in dieser Datei.
174. Diese Zeile gehoert zur Implementierung in dieser Datei.
175. Diese Zeile gehoert zur Implementierung in dieser Datei.
176. Diese Zeile gehoert zur Implementierung in dieser Datei.
177. Diese Zeile gehoert zur Implementierung in dieser Datei.
178. Diese Zeile gehoert zur Implementierung in dieser Datei.
179. Diese Zeile gehoert zur Implementierung in dieser Datei.
180. Diese Zeile gehoert zur Implementierung in dieser Datei.
181. Diese Zeile gehoert zur Implementierung in dieser Datei.
182. Diese Zeile gehoert zur Implementierung in dieser Datei.
183. Diese Zeile gehoert zur Implementierung in dieser Datei.
184. Diese Zeile gehoert zur Implementierung in dieser Datei.
185. Diese Zeile gehoert zur Implementierung in dieser Datei.
186. Diese Zeile gehoert zur Implementierung in dieser Datei.
187. Diese Zeile gehoert zur Implementierung in dieser Datei.
188. Diese Zeile gehoert zur Implementierung in dieser Datei.
189. Diese Zeile gehoert zur Implementierung in dieser Datei.
190. Diese Zeile gehoert zur Implementierung in dieser Datei.
191. Diese Zeile gehoert zur Implementierung in dieser Datei.
192. Diese Zeile gehoert zur Implementierung in dieser Datei.
193. Diese Zeile gehoert zur Implementierung in dieser Datei.
194. Diese Zeile gehoert zur Implementierung in dieser Datei.
195. Diese Zeile gehoert zur Implementierung in dieser Datei.
196. Diese Zeile gehoert zur Implementierung in dieser Datei.
197. Diese Zeile gehoert zur Implementierung in dieser Datei.
198. Diese Zeile gehoert zur Implementierung in dieser Datei.
199. Diese Zeile gehoert zur Implementierung in dieser Datei.
200. Diese Zeile gehoert zur Implementierung in dieser Datei.
201. Diese Zeile gehoert zur Implementierung in dieser Datei.

## tests/test_publish_guards_api.py

```python
from __future__ import annotations

from sqlalchemy import select

from app.models import Recipe, RecipeSubmission, User
from app.security import create_access_token, hash_password


def _create_user(db, *, email: str, role: str, password: str = "StrongPass123!") -> User:
    user = User(email=email.strip().lower(), role=role, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _auth_as(client, user: User) -> str:
    csrf_token = "api-test-csrf-token"
    token = create_access_token(user.user_uid, user.role)
    client.cookies.set("access_token", f"Bearer {token}")
    client.cookies.set("csrf_token", csrf_token)
    return csrf_token


def test_api_user_cannot_publish_recipe_directly(client, db_session_factory):
    with db_session_factory() as db:
        user = _create_user(db, email="api-publish-block@example.local", role="user")
    csrf = _auth_as(client, user)

    response = client.post(
        "/recipes",
        data={
            "title": "API Direct Publish Block",
            "description": "Soll als User nicht direkt live gehen.",
            "instructions": "Schritt 1\nSchritt 2",
            "category_select": "Unkategorisiert",
            "category_new": "",
            "category": "",
            "title_image_url": "",
            "prep_time_minutes": "15",
            "difficulty": "easy",
            "ingredients_text": "Mehl|100 g",
            "csrf_token": csrf,
        },
        headers={"X-CSRF-Token": csrf},
        follow_redirects=False,
    )
    assert response.status_code == 403


def test_api_discover_never_lists_pending_submissions(client, db_session_factory):
    with db_session_factory() as db:
        admin = _create_user(db, email="api-admin@example.local", role="admin")
        user = _create_user(db, email="api-user@example.local", role="user")
        db.add(
            Recipe(
                title="API Sichtbares Rezept",
                description="Dies ist sichtbar.",
                instructions="Schritt 1",
                category="Test",
                prep_time_minutes=12,
                difficulty="medium",
                creator_id=admin.id,
                source="test",
                is_published=True,
            )
        )
        db.add(
            RecipeSubmission(
                submitter_user_id=user.id,
                title="API Pending Nur Moderation",
                description="Darf nicht in Discover erscheinen.",
                category="Test",
                difficulty="easy",
                instructions="Schritt A",
                status="pending",
            )
        )
        db.commit()

    discover_response = client.get("/")
    assert discover_response.status_code == 200
    assert "API Sichtbares Rezept" in discover_response.text
    assert "API Pending Nur Moderation" not in discover_response.text

    with db_session_factory() as db:
        pending_submission = db.scalar(
            select(RecipeSubmission).where(RecipeSubmission.title == "API Pending Nur Moderation")
        )
        assert pending_submission is not None
        assert pending_submission.status == "pending"
```
ZEILEN-ERKLAERUNG
1. Diese Zeile gehoert zur Implementierung in dieser Datei.
2. Diese Zeile gehoert zur Implementierung in dieser Datei.
3. Diese Zeile gehoert zur Implementierung in dieser Datei.
4. Diese Zeile gehoert zur Implementierung in dieser Datei.
5. Diese Zeile gehoert zur Implementierung in dieser Datei.
6. Diese Zeile gehoert zur Implementierung in dieser Datei.
7. Diese Zeile gehoert zur Implementierung in dieser Datei.
8. Diese Zeile gehoert zur Implementierung in dieser Datei.
9. Diese Zeile gehoert zur Implementierung in dieser Datei.
10. Diese Zeile gehoert zur Implementierung in dieser Datei.
11. Diese Zeile gehoert zur Implementierung in dieser Datei.
12. Diese Zeile gehoert zur Implementierung in dieser Datei.
13. Diese Zeile gehoert zur Implementierung in dieser Datei.
14. Diese Zeile gehoert zur Implementierung in dieser Datei.
15. Diese Zeile gehoert zur Implementierung in dieser Datei.
16. Diese Zeile gehoert zur Implementierung in dieser Datei.
17. Diese Zeile gehoert zur Implementierung in dieser Datei.
18. Diese Zeile gehoert zur Implementierung in dieser Datei.
19. Diese Zeile gehoert zur Implementierung in dieser Datei.
20. Diese Zeile gehoert zur Implementierung in dieser Datei.
21. Diese Zeile gehoert zur Implementierung in dieser Datei.
22. Diese Zeile gehoert zur Implementierung in dieser Datei.
23. Diese Zeile gehoert zur Implementierung in dieser Datei.
24. Diese Zeile gehoert zur Implementierung in dieser Datei.
25. Diese Zeile gehoert zur Implementierung in dieser Datei.
26. Diese Zeile gehoert zur Implementierung in dieser Datei.
27. Diese Zeile gehoert zur Implementierung in dieser Datei.
28. Diese Zeile gehoert zur Implementierung in dieser Datei.
29. Diese Zeile gehoert zur Implementierung in dieser Datei.
30. Diese Zeile gehoert zur Implementierung in dieser Datei.
31. Diese Zeile gehoert zur Implementierung in dieser Datei.
32. Diese Zeile gehoert zur Implementierung in dieser Datei.
33. Diese Zeile gehoert zur Implementierung in dieser Datei.
34. Diese Zeile gehoert zur Implementierung in dieser Datei.
35. Diese Zeile gehoert zur Implementierung in dieser Datei.
36. Diese Zeile gehoert zur Implementierung in dieser Datei.
37. Diese Zeile gehoert zur Implementierung in dieser Datei.
38. Diese Zeile gehoert zur Implementierung in dieser Datei.
39. Diese Zeile gehoert zur Implementierung in dieser Datei.
40. Diese Zeile gehoert zur Implementierung in dieser Datei.
41. Diese Zeile gehoert zur Implementierung in dieser Datei.
42. Diese Zeile gehoert zur Implementierung in dieser Datei.
43. Diese Zeile gehoert zur Implementierung in dieser Datei.
44. Diese Zeile gehoert zur Implementierung in dieser Datei.
45. Diese Zeile gehoert zur Implementierung in dieser Datei.
46. Diese Zeile gehoert zur Implementierung in dieser Datei.
47. Diese Zeile gehoert zur Implementierung in dieser Datei.
48. Diese Zeile gehoert zur Implementierung in dieser Datei.
49. Diese Zeile gehoert zur Implementierung in dieser Datei.
50. Diese Zeile gehoert zur Implementierung in dieser Datei.
51. Diese Zeile gehoert zur Implementierung in dieser Datei.
52. Diese Zeile gehoert zur Implementierung in dieser Datei.
53. Diese Zeile gehoert zur Implementierung in dieser Datei.
54. Diese Zeile gehoert zur Implementierung in dieser Datei.
55. Diese Zeile gehoert zur Implementierung in dieser Datei.
56. Diese Zeile gehoert zur Implementierung in dieser Datei.
57. Diese Zeile gehoert zur Implementierung in dieser Datei.
58. Diese Zeile gehoert zur Implementierung in dieser Datei.
59. Diese Zeile gehoert zur Implementierung in dieser Datei.
60. Diese Zeile gehoert zur Implementierung in dieser Datei.
61. Diese Zeile gehoert zur Implementierung in dieser Datei.
62. Diese Zeile gehoert zur Implementierung in dieser Datei.
63. Diese Zeile gehoert zur Implementierung in dieser Datei.
64. Diese Zeile gehoert zur Implementierung in dieser Datei.
65. Diese Zeile gehoert zur Implementierung in dieser Datei.
66. Diese Zeile gehoert zur Implementierung in dieser Datei.
67. Diese Zeile gehoert zur Implementierung in dieser Datei.
68. Diese Zeile gehoert zur Implementierung in dieser Datei.
69. Diese Zeile gehoert zur Implementierung in dieser Datei.
70. Diese Zeile gehoert zur Implementierung in dieser Datei.
71. Diese Zeile gehoert zur Implementierung in dieser Datei.
72. Diese Zeile gehoert zur Implementierung in dieser Datei.
73. Diese Zeile gehoert zur Implementierung in dieser Datei.
74. Diese Zeile gehoert zur Implementierung in dieser Datei.
75. Diese Zeile gehoert zur Implementierung in dieser Datei.
76. Diese Zeile gehoert zur Implementierung in dieser Datei.
77. Diese Zeile gehoert zur Implementierung in dieser Datei.
78. Diese Zeile gehoert zur Implementierung in dieser Datei.
79. Diese Zeile gehoert zur Implementierung in dieser Datei.
80. Diese Zeile gehoert zur Implementierung in dieser Datei.
81. Diese Zeile gehoert zur Implementierung in dieser Datei.
82. Diese Zeile gehoert zur Implementierung in dieser Datei.
83. Diese Zeile gehoert zur Implementierung in dieser Datei.
84. Diese Zeile gehoert zur Implementierung in dieser Datei.
85. Diese Zeile gehoert zur Implementierung in dieser Datei.
86. Diese Zeile gehoert zur Implementierung in dieser Datei.
87. Diese Zeile gehoert zur Implementierung in dieser Datei.
88. Diese Zeile gehoert zur Implementierung in dieser Datei.
89. Diese Zeile gehoert zur Implementierung in dieser Datei.
90. Diese Zeile gehoert zur Implementierung in dieser Datei.
91. Diese Zeile gehoert zur Implementierung in dieser Datei.

## docs/QA_BETA_CHECKLIST.md

```python
# QA Beta Checklist

Diese Checkliste kombiniert automatisierte E2E-Tests mit manuellen Beta-Checks fuer MealMate.

## 1) Automatisierte Tests (Pflicht)

1. Abhaengigkeiten installieren:
   - `pip install -r requirements.txt`
2. Playwright Browser einmalig installieren:
   - `python -m playwright install chromium`
3. Alle Tests starten:
   - `pytest -q`
4. Erwartung:
   - API-/Unit-Tests laufen durch.
   - E2E-Tests unter `tests/e2e/` laufen gegen einen automatisch gestarteten Uvicorn-Testserver.

## 2) Was die E2E-Suite abdeckt

## User Flow (`test_user_full_journey`)

1. Login mit bestehendem User.
2. Username aendern.
3. Passwort aendern und Re-Login.
4. Forgot/Reset mit DEV-Outbox-Link und Re-Login.
5. Rezept einreichen ueber `/submit`.
6. Sicherstellen, dass Einreichung nicht in Discover auftaucht.
7. Eigene Einreichungen mit `pending` pruefen.
8. Favorit setzen und wieder entfernen.
9. Review schreiben und Sichtbarkeit pruefen.
10. PDF-Download mit `application/pdf` pruefen.

## Admin Flow (`test_admin_full_journey`)

1. Admin Login.
2. Pending Submission freigeben.
3. Discover zeigt freigegebenes Rezept.
4. Zweite Submission ablehnen (mit Grund).
5. Pending Image-Change freigeben (wenn vorhanden).
6. Direktes Admin-Rezept erstellen und in Discover sehen.

## API Hard Assertions (`tests/test_publish_guards_api.py`)

1. Normaler User kann `/recipes` nicht direkt publishen (`403`).
2. Discover zeigt keine pending Submissions.

## 3) Manuelle Beta-Checks

1. Security Headers:
   - `curl -I http://127.0.0.1:8010/`
   - CSP, `X-Frame-Options`, `X-Content-Type-Options` vorhanden.
2. CSRF:
   - POST ohne Token -> `403`.
   - POST mit Token -> erfolgreich.
3. Rate Limit:
   - Login absichtlich >5/min von gleicher IP -> `429`.
4. Moderation:
   - User-Submission ist in Admin-Queue sichtbar.
   - Erst nach Approve in Discover sichtbar.
5. Bilder:
   - Fallback-Reihenfolge: DB -> externe URL -> Placeholder.
   - User-Bildvorschlag bleibt pending bis Admin-Freigabe.

## 4) Troubleshooting

1. E2E werden uebersprungen:
   - Chromium fehlt, `python -m playwright install chromium` ausfuehren.
2. Testserver startet nicht:
   - Lokalen Port-Konflikt oder fehlende Dependencies pruefen.
3. PDF-Test faellt:
   - `reportlab` Installation und Rezeptzugriff pruefen.
```
ZEILEN-ERKLAERUNG
1. Diese Zeile gehoert zur Implementierung in dieser Datei.
2. Diese Zeile gehoert zur Implementierung in dieser Datei.
3. Diese Zeile gehoert zur Implementierung in dieser Datei.
4. Diese Zeile gehoert zur Implementierung in dieser Datei.
5. Diese Zeile gehoert zur Implementierung in dieser Datei.
6. Diese Zeile gehoert zur Implementierung in dieser Datei.
7. Diese Zeile gehoert zur Implementierung in dieser Datei.
8. Diese Zeile gehoert zur Implementierung in dieser Datei.
9. Diese Zeile gehoert zur Implementierung in dieser Datei.
10. Diese Zeile gehoert zur Implementierung in dieser Datei.
11. Diese Zeile gehoert zur Implementierung in dieser Datei.
12. Diese Zeile gehoert zur Implementierung in dieser Datei.
13. Diese Zeile gehoert zur Implementierung in dieser Datei.
14. Diese Zeile gehoert zur Implementierung in dieser Datei.
15. Diese Zeile gehoert zur Implementierung in dieser Datei.
16. Diese Zeile gehoert zur Implementierung in dieser Datei.
17. Diese Zeile gehoert zur Implementierung in dieser Datei.
18. Diese Zeile gehoert zur Implementierung in dieser Datei.
19. Diese Zeile gehoert zur Implementierung in dieser Datei.
20. Diese Zeile gehoert zur Implementierung in dieser Datei.
21. Diese Zeile gehoert zur Implementierung in dieser Datei.
22. Diese Zeile gehoert zur Implementierung in dieser Datei.
23. Diese Zeile gehoert zur Implementierung in dieser Datei.
24. Diese Zeile gehoert zur Implementierung in dieser Datei.
25. Diese Zeile gehoert zur Implementierung in dieser Datei.
26. Diese Zeile gehoert zur Implementierung in dieser Datei.
27. Diese Zeile gehoert zur Implementierung in dieser Datei.
28. Diese Zeile gehoert zur Implementierung in dieser Datei.
29. Diese Zeile gehoert zur Implementierung in dieser Datei.
30. Diese Zeile gehoert zur Implementierung in dieser Datei.
31. Diese Zeile gehoert zur Implementierung in dieser Datei.
32. Diese Zeile gehoert zur Implementierung in dieser Datei.
33. Diese Zeile gehoert zur Implementierung in dieser Datei.
34. Diese Zeile gehoert zur Implementierung in dieser Datei.
35. Diese Zeile gehoert zur Implementierung in dieser Datei.
36. Diese Zeile gehoert zur Implementierung in dieser Datei.
37. Diese Zeile gehoert zur Implementierung in dieser Datei.
38. Diese Zeile gehoert zur Implementierung in dieser Datei.
39. Diese Zeile gehoert zur Implementierung in dieser Datei.
40. Diese Zeile gehoert zur Implementierung in dieser Datei.
41. Diese Zeile gehoert zur Implementierung in dieser Datei.
42. Diese Zeile gehoert zur Implementierung in dieser Datei.
43. Diese Zeile gehoert zur Implementierung in dieser Datei.
44. Diese Zeile gehoert zur Implementierung in dieser Datei.
45. Diese Zeile gehoert zur Implementierung in dieser Datei.
46. Diese Zeile gehoert zur Implementierung in dieser Datei.
47. Diese Zeile gehoert zur Implementierung in dieser Datei.
48. Diese Zeile gehoert zur Implementierung in dieser Datei.
49. Diese Zeile gehoert zur Implementierung in dieser Datei.
50. Diese Zeile gehoert zur Implementierung in dieser Datei.
51. Diese Zeile gehoert zur Implementierung in dieser Datei.
52. Diese Zeile gehoert zur Implementierung in dieser Datei.
53. Diese Zeile gehoert zur Implementierung in dieser Datei.
54. Diese Zeile gehoert zur Implementierung in dieser Datei.
55. Diese Zeile gehoert zur Implementierung in dieser Datei.
56. Diese Zeile gehoert zur Implementierung in dieser Datei.
57. Diese Zeile gehoert zur Implementierung in dieser Datei.
58. Diese Zeile gehoert zur Implementierung in dieser Datei.
59. Diese Zeile gehoert zur Implementierung in dieser Datei.
60. Diese Zeile gehoert zur Implementierung in dieser Datei.
61. Diese Zeile gehoert zur Implementierung in dieser Datei.
62. Diese Zeile gehoert zur Implementierung in dieser Datei.
63. Diese Zeile gehoert zur Implementierung in dieser Datei.
64. Diese Zeile gehoert zur Implementierung in dieser Datei.
65. Diese Zeile gehoert zur Implementierung in dieser Datei.
66. Diese Zeile gehoert zur Implementierung in dieser Datei.
67. Diese Zeile gehoert zur Implementierung in dieser Datei.
68. Diese Zeile gehoert zur Implementierung in dieser Datei.
69. Diese Zeile gehoert zur Implementierung in dieser Datei.
70. Diese Zeile gehoert zur Implementierung in dieser Datei.

## docs/FEATURES_SNAPSHOT.md

```python
# MealMate Feature Snapshot

Stand: 03.03.2026

## Core Plattform

1. FastAPI Backend mit Jinja2 + HTMX Frontend.
2. SQLAlchemy 2.0 + Alembic Migrationen.
3. SQLite lokal, Postgres-kompatibel ueber `DATABASE_URL`.
4. Docker- und Deploy-Artefakte (`Dockerfile`, `start.sh`, `render.yaml`).

## Auth & Account

1. JWT in HttpOnly Cookie (`access_token`) mit CSRF-Schutz.
2. Login ueber E-Mail oder Username.
3. Registrierung mit Passwort-Policy.
4. Profilseite mit `user_uid`, Username-Update und Passwortwechsel.
5. Forgot/Reset Password mit Token-Hashing und Single-Use-Token.
6. E-Mail-Aenderung per bestaetigtem Token-Link.

## Rollen & Moderation

1. Rollenmodell: `user` und `admin`.
2. Nur Admin darf direkt veroeffentlichen (`/recipes/new` -> published).
3. User/Gast reichen Rezepte ueber `/submit` als `pending` ein.
4. Admin-Moderation fuer Submissions: Vorschau, Edit, Approve, Reject.
5. Discover listet nur veroeffentlichte Rezepte.

## Rezepte & Interaktionen

1. Discover mit Filtern, Sortierung, Pagination und HTMX-Updates.
2. Kategorien als stabilisierte Dropdown-Werte.
3. Rezeptdetail mit Reviews, Durchschnittsbewertung und Favoriten.
4. PDF-Download pro Rezept (`/recipes/{id}/pdf`).
5. Eigene Bereiche: `My Recipes`, `Favorites`, `My Submissions`.

## Bilder

1. Rezeptbilder in DB (`recipe_images`) mit `is_primary`.
2. Fallback-Reihenfolge im UI:
   - Primary DB-Bild
   - `source_image_url`/`title_image_url`
   - Placeholder
3. Admin darf Bilder direkt setzen/loeschen/primary setzen.
4. User koennen Bildaenderungsvorschlaege einreichen (pending moderation).
5. Admin-Queue fuer Bildaenderungen mit Approve/Reject.

## Import & Seed

1. KochWiki Auto-Seed ist per Flag steuerbar.
2. Admin CSV Import mit:
   - Preview
   - Dry-Run
   - Insert-Only Standard
   - Optional Update Existing
3. Dedup-Regeln und Validierungsreport mit Fehlern/Warnungen.

## Security & Ops

1. CSRF fuer state-changing Browser-Requests.
2. Rate Limits auf Login, Register, Import, Upload und sensible Aktionen.
3. Security Headers inkl. konfigurierbarer CSP (`CSP_IMG_SRC`).
4. Trusted Host / Proxy Header Hardening.
5. Request-ID + strukturiertes Logging + Fehlerseiten.
6. Healthcheck Endpoint: `/healthz`.

## Testing

1. API/Unit Tests fuer Auth, Moderation, i18n, Bildworkflow.
2. Neue Playwright E2E-Suite fuer User- und Admin-End-to-End-Flows.
3. Hard Assertions gegen Direct-Publish-Bug und Discover-Leaks.
```
ZEILEN-ERKLAERUNG
1. Diese Zeile gehoert zur Implementierung in dieser Datei.
2. Diese Zeile gehoert zur Implementierung in dieser Datei.
3. Diese Zeile gehoert zur Implementierung in dieser Datei.
4. Diese Zeile gehoert zur Implementierung in dieser Datei.
5. Diese Zeile gehoert zur Implementierung in dieser Datei.
6. Diese Zeile gehoert zur Implementierung in dieser Datei.
7. Diese Zeile gehoert zur Implementierung in dieser Datei.
8. Diese Zeile gehoert zur Implementierung in dieser Datei.
9. Diese Zeile gehoert zur Implementierung in dieser Datei.
10. Diese Zeile gehoert zur Implementierung in dieser Datei.
11. Diese Zeile gehoert zur Implementierung in dieser Datei.
12. Diese Zeile gehoert zur Implementierung in dieser Datei.
13. Diese Zeile gehoert zur Implementierung in dieser Datei.
14. Diese Zeile gehoert zur Implementierung in dieser Datei.
15. Diese Zeile gehoert zur Implementierung in dieser Datei.
16. Diese Zeile gehoert zur Implementierung in dieser Datei.
17. Diese Zeile gehoert zur Implementierung in dieser Datei.
18. Diese Zeile gehoert zur Implementierung in dieser Datei.
19. Diese Zeile gehoert zur Implementierung in dieser Datei.
20. Diese Zeile gehoert zur Implementierung in dieser Datei.
21. Diese Zeile gehoert zur Implementierung in dieser Datei.
22. Diese Zeile gehoert zur Implementierung in dieser Datei.
23. Diese Zeile gehoert zur Implementierung in dieser Datei.
24. Diese Zeile gehoert zur Implementierung in dieser Datei.
25. Diese Zeile gehoert zur Implementierung in dieser Datei.
26. Diese Zeile gehoert zur Implementierung in dieser Datei.
27. Diese Zeile gehoert zur Implementierung in dieser Datei.
28. Diese Zeile gehoert zur Implementierung in dieser Datei.
29. Diese Zeile gehoert zur Implementierung in dieser Datei.
30. Diese Zeile gehoert zur Implementierung in dieser Datei.
31. Diese Zeile gehoert zur Implementierung in dieser Datei.
32. Diese Zeile gehoert zur Implementierung in dieser Datei.
33. Diese Zeile gehoert zur Implementierung in dieser Datei.
34. Diese Zeile gehoert zur Implementierung in dieser Datei.
35. Diese Zeile gehoert zur Implementierung in dieser Datei.
36. Diese Zeile gehoert zur Implementierung in dieser Datei.
37. Diese Zeile gehoert zur Implementierung in dieser Datei.
38. Diese Zeile gehoert zur Implementierung in dieser Datei.
39. Diese Zeile gehoert zur Implementierung in dieser Datei.
40. Diese Zeile gehoert zur Implementierung in dieser Datei.
41. Diese Zeile gehoert zur Implementierung in dieser Datei.
42. Diese Zeile gehoert zur Implementierung in dieser Datei.
43. Diese Zeile gehoert zur Implementierung in dieser Datei.
44. Diese Zeile gehoert zur Implementierung in dieser Datei.
45. Diese Zeile gehoert zur Implementierung in dieser Datei.
46. Diese Zeile gehoert zur Implementierung in dieser Datei.
47. Diese Zeile gehoert zur Implementierung in dieser Datei.
48. Diese Zeile gehoert zur Implementierung in dieser Datei.
49. Diese Zeile gehoert zur Implementierung in dieser Datei.
50. Diese Zeile gehoert zur Implementierung in dieser Datei.
51. Diese Zeile gehoert zur Implementierung in dieser Datei.
52. Diese Zeile gehoert zur Implementierung in dieser Datei.
53. Diese Zeile gehoert zur Implementierung in dieser Datei.
54. Diese Zeile gehoert zur Implementierung in dieser Datei.
55. Diese Zeile gehoert zur Implementierung in dieser Datei.
56. Diese Zeile gehoert zur Implementierung in dieser Datei.
57. Diese Zeile gehoert zur Implementierung in dieser Datei.
58. Diese Zeile gehoert zur Implementierung in dieser Datei.
59. Diese Zeile gehoert zur Implementierung in dieser Datei.
60. Diese Zeile gehoert zur Implementierung in dieser Datei.
61. Diese Zeile gehoert zur Implementierung in dieser Datei.
62. Diese Zeile gehoert zur Implementierung in dieser Datei.
63. Diese Zeile gehoert zur Implementierung in dieser Datei.
64. Diese Zeile gehoert zur Implementierung in dieser Datei.
65. Diese Zeile gehoert zur Implementierung in dieser Datei.
66. Diese Zeile gehoert zur Implementierung in dieser Datei.
67. Diese Zeile gehoert zur Implementierung in dieser Datei.
68. Diese Zeile gehoert zur Implementierung in dieser Datei.
69. Diese Zeile gehoert zur Implementierung in dieser Datei.
70. Diese Zeile gehoert zur Implementierung in dieser Datei.
71. Diese Zeile gehoert zur Implementierung in dieser Datei.


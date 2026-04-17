# Kitchen Hell and Heaven - Technical Documentation

## 0) Meta

- **Project name:** Kitchen Hell and Heaven
- **Documentation date:** 2026-03-05
- **Repository root:** `Schnittstellen und APIs/Abschluss Projekt`
- **Target audience:** Dozent:innen, Entwickler:innen, QA/Security Engineers
- **Document type:** Single-file technical system documentation derived from code and local test runs

**Scope of this document**

- This document covers architecture, runtime configuration, routes, auth/authz, moderation, translation, security controls, persistence/migrations, and test strategy.
- This document does not describe product marketing, UX copywriting, or future feature ideation.
- Statements are based on the current codebase (`app/`, `alembic/`, `tests/`) and local verification commands.

---

## 1) Executive Technical Summary (max 12 lines)

Kitchen Hell and Heaven is a server-rendered FastAPI web application with Jinja2 + HTMX, SQLAlchemy ORM, and Alembic migrations.
Core modules are split into authentication/account recovery, recipe CRUD/discovery, moderation queues, translation queue/batch orchestration, i18n, upload validation, and PDF export.
Auth uses JWT in HttpOnly cookie + CSRF token middleware; authorization is dependency-driven with role gates (`guest/user/admin`).
Recipe publication is admin-controlled; user/guest recipe flow goes through submission moderation before publication.
Image flow supports DB image, external fallback URL proxy, and moderated image-change requests.
Translation flow supports sync translation runs, queue-based runs, async batch jobs, and DE language audit/repair.
Security hardening includes CSP, XFO, XCTO, Referrer/Permissions policy, TrustedHost (conditional), rate limiting, safe redirect validation, and generic 500 responses in production mode.
Alembic state is consistent: `current == head == 20260304_0016`.
Local regression status (verified): `133 passed, 0 failed, 5 warnings`.
Warning-cleanup history (latest hardening cycle): `11 -> 5 warnings`, `6 ResourceWarnings fixed`, `5 DeprecationWarnings remain`.

**Key security-hardening points**

- Global unhandled exception handler returns generic 500 payload in production mode.
- Security headers are applied in middleware and explicitly in exception handlers.
- Upload validation checks MIME allowlist + magic bytes + PIL decode verification.
- Open redirect protection uses strict relative-path validation (`safe_redirect_path`).
- CSRF is enforced for state-changing methods including HTMX requests.

---

## 2) Technology Stack

| Layer | Technology |
|---|---|
| Backend framework | FastAPI 0.116.1 |
| ASGI server | Uvicorn 0.35.0 (`uvicorn[standard]`) |
| Template engine | Jinja2 3.1.6 |
| HTMX | `app/static/htmx.min.js` |
| Database | SQLite (dev) / PostgreSQL via psycopg (prod-capable) |
| ORM | SQLAlchemy 2.0.43 |
| Migrations | Alembic 1.16.5 |
| Auth/JWT | `python-jose` 3.5.0 |
| Password hashing | `pwdlib` + `argon2-cffi` |
| Rate limiting | SlowAPI 0.1.9 |
| HTTP client | httpx 0.28.1 |
| PDF generation | ReportLab 4.4.4 |
| Image handling | Pillow 11.3.0 |
| Tests | pytest 8.4.2, pytest-asyncio 1.2.0 |
| Browser E2E | Playwright 1.54.0 (optional runtime dependency for E2E) |

**Version source:** `requirements.txt`.

---

## 3) Repository Layout

```text
app/
  main.py
  config.py
  middleware.py
  database.py
  dependencies.py
  models.py
  translation_models.py
  security.py
  security_events.py
  services.py
  translation_provider.py
  translation_service.py
  routers/
    auth.py
    recipes.py
    submissions.py
    admin.py
    translations.py
    legal.py
  i18n/
    __init__.py
    middleware.py
    service.py
    locales/{de,en,fr}.json
  templates/
    base.html
    home.html
    admin*.html
    auth_*.html
    recipe_*.html
    partials/*.html
  static/
    style.css
    *.css
    htmx.min.js
    security.js

alembic/
  env.py
  versions/20260303_0001_*.py ... 20260304_0016_*.py

tests/
  conftest.py
  test_*.py
  e2e/{conftest.py,test_beta_smoke.py,test_user_admin_journey.py}

docs/
  README_*.md
  QA/architecture/status docs
```

**Folder purpose**

- `app/`: Runtime application code.
- `app/routers/`: HTTP endpoint modules per domain.
- `app/services*.py`: Domain/business helpers and import/category logic.
- `app/translation_*.py`: Translation provider abstraction + orchestration.
- `app/i18n/`: Locale resolution and dictionary translation service.
- `alembic/`: DB schema versioning.
- `tests/`: Unit/integration/security/e2e test suites.
- `docs/`: Project and process documentation.

---

## 4) Runtime / Configuration

### Local start command

```bash
py -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
```

### Settings mechanism

- Configuration is centralized in `app/config.py` (`Settings`, pydantic-settings).
- `get_settings()` is `@lru_cache`-backed and used across modules.
- Environment source: `.env` (UTF-8), case-insensitive keys.

### Important ENV/settings keys (excerpt)

| Area | Keys (from `Settings`) |
|---|---|
| Core | `APP_NAME`, `APP_ENV`, `APP_URL`, `SECRET_KEY`, `ALGORITHM`, `TOKEN_EXPIRE_MINUTES` |
| DB/host/cookies | `DATABASE_URL`, `ALLOWED_HOSTS`, `COOKIE_SECURE`, `FORCE_HTTPS` |
| CSP/CSRF | `CSP_IMG_SRC`, `CSRF_COOKIE_NAME`, `CSRF_HEADER_NAME` |
| Upload | `MAX_UPLOAD_MB`, `MAX_CSV_UPLOAD_MB`, `ALLOWED_IMAGE_TYPES` |
| Mail | `MAIL_OUTBOX_PATH`, `MAIL_OUTBOX_EMAIL_CHANGE_PATH`, `SMTP_*`, `SMTP_FROM` |
| Translation | `TRANSLATEAPI_ENABLED`, `TRANSLATION_PROVIDER`, `TRANSLATE_SOURCE_LANG`, `TRANSLATE_TARGET_LANGS`, `TRANSLATE_AUTO_ON_PUBLISH`, `TRANSLATE_LAZY_ON_VIEW`, `TRANSLATE_MAX_RECIPES_PER_RUN`, `TRANSLATEAPI_*` |
| Security events | `SECURITY_EVENT_RETENTION_DAYS`, `SECURITY_EVENT_MAX_ROWS` |
| Seed/import | `ENABLE_KOCHWIKI_SEED`, `AUTO_SEED_KOCHWIKI`, `KOCHWIKI_CSV_PATH`, `IMPORT_DOWNLOAD_IMAGES` |

### Runtime behavior notes

- Proxy headers are enabled (`ProxyHeadersMiddleware`) and host filtering is conditional (`TrustedHostMiddleware` if `ALLOWED_HOSTS != ["*"]`).
- Static files are mounted at `/static`; production mode adds static cache headers.

---

## 5) HTTP / Routing Overview

Routers are registered in `app/main.py`:

- `auth.router`
- `recipes.router`
- `submissions.router`
- `admin.router`
- `translations.router`
- `legal.router`

### Route groups by concern

| Router | Concern | Examples |
|---|---|---|
| `auth.py` | Login, register, JWT cookie, account recovery/profile | `/login`, `/register`, `/logout`, `/auth/*`, `/me` |
| `recipes.py` | Discover, recipe CRUD, favorites/reviews, images, PDF, categories API | `/`, `/recipes/*`, `/favorites`, `/images/*`, `/categories` |
| `submissions.py` | Public submission and admin moderation queue | `/submit`, `/my-submissions`, `/admin/submissions/*` |
| `admin.py` | Admin dashboard, CSV import, category tools, image-change moderation | `/admin`, `/admin/import-*`, `/admin/categories*`, `/admin/image-change-*` |
| `translations.py` | Translation admin pages, queue/batch runs, diagnostics/audit/repair | `/admin/translations*` |
| `legal.py` | Legal pages | `/impressum`, `/copyright` |

### API docs

- FastAPI defaults apply; OpenAPI docs endpoints are available unless externally restricted (`/docs`, `/openapi.json`).

---

## 6) Authentication & Authorization

### Login/Register

- Login accepts email or username identifier (`_find_user_by_identifier` in `auth.py`).
- Register enforces password policy and optional username policy.
- JWT access token created via `create_access_token()` and set in `access_token` cookie.

### JWT cookie behavior

- Cookie key: `access_token`
- Value format: `Bearer <jwt>`
- Flags: `HttpOnly=True`, `SameSite=Lax`, `Secure=settings.resolved_cookie_secure`
- TTL: `max_age=60*60*24`

### CSRF model

- Middleware: `CSRFMiddleware` in `app/middleware.py`
- Cookie key default: `csrf_token`
- Header default: `X-CSRF-Token`
- For state-changing methods (`POST/PUT/PATCH/DELETE`), token match is required unless path is exempt (`/health`, `/healthz`, `/static` prefixes).
- `security.js` injects hidden `csrf_token` fields and sets HTMX request header.

### Role model and gates

- Roles: `guest`, `user`, `admin` (`User.role`).
- Core dependency guards:
  - `get_current_user` -> 401 if unauthenticated
  - `get_admin_user` -> 403 if non-admin
- Router-level enforcement is dependency-driven (server-side, not UI-only).

### Error handling and leak prevention

- In production mode (`APP_ENV=prod`), unhandled exceptions return generic error response.
- HTML 500 page hides trace in prod (`show_trace=False`).
- JSON 500 in prod returns only translated generic message (`error.internal`).
- Request ID is attached to responses and logs.

---

## 7) Core Domain: Recipes

### Primary domain entities (high-level)

- `Recipe`, `RecipeIngredient`, `Ingredient`, `Review`, `Favorite`, `RecipeImage`
- Accessory entities for moderation: `RecipeSubmission`, `SubmissionIngredient`, `SubmissionImage`, `RecipeImageChangeRequest`, `RecipeImageChangeFile`

### Recipe lifecycle and visibility

- Discover (`GET /`) queries published recipes only (`Recipe.is_published == True`).
- Admin direct publish path: `GET/POST /recipes/new` (admin dependency).
- Non-admin submission path is separated (`/submit`) and moderated before publish.

### Search/filter/sort/pagination

- Filters include title/category/difficulty/ingredient/image presence.
- Pagination defaults: `per_page=20`, allowed options `(10,20,40,80)`.
- Sorting allowlist: `date`, `prep_time`, `avg_rating`.
- Query constraints (FastAPI `Query`) are used for numeric bounds and patterns.

### Reviews and favorites

- Reviews: one review per user per recipe (`uq_reviews_user_recipe`).
- Favorites: one favorite per user per recipe (`uq_favorites_user_recipe`).
- Favorite toggle supports HTMX partial refresh.

### PDF export

- Endpoint: `GET /recipes/{id}/pdf` (authenticated, rate-limited).
- Implementation: `app/pdf_service.py` via ReportLab.
- Image embedding uses DB-stored primary image if available, with WebP -> PNG conversion fallback for PDF compatibility.

### Image rendering fallback order

1. Primary DB image (`/images/{id}`)
2. External fallback URL (`source_image_url`/`title_image_url`) via `/external-image` proxy redirect
3. Placeholder UI

### Upload validation (summary)

- Allowed MIME list from settings.
- Max size enforced (`MAX_UPLOAD_MB`).
- Magic-byte signature checks (JPEG/PNG/WebP).
- PIL decode/format verification.
- Filenames sanitized to generated UUID-based names.

---

## 8) Moderation Workflows

### Recipe submission moderation

- Public/user submission: `POST /submit` -> `recipe_submissions` status `pending`.
- Admin queue: `/admin/submissions` (filter + pagination).
- Admin actions:
  - Edit pending submission
  - Approve -> `publish_submission_as_recipe()` creates published `Recipe` (`source="submission"`, `source_uuid="submission:<id>"`)
  - Reject with reason

### Image-change moderation

- User image proposal endpoint: `POST /recipes/{id}/image-change-request`
- Admin queue and details:
  - `/admin/image-change-requests`
  - `/admin/image-change-requests/{id}`
- Admin approve copies proposed file into `recipe_images` and marks request approved.
- Admin reject requires note and marks request rejected.

### State model (implemented)

- Submission statuses: `pending`, `approved`, `rejected`
- Image-change statuses: `pending`, `approved`, `rejected`

---

## 9) Internationalization (i18n) & Translation System

### UI i18n

- Supported UI languages: `de`, `en`, `fr` (`SUPPORTED_LANGS`).
- Locale resolution order:
  1. `?lang=<code>`
  2. `lang` cookie
  3. `Accept-Language` header
  4. Default `de`
- Jinja global `t()` is registered in `app/views.py`.

### Recipe translation persistence

- Table: `recipe_translations` (`recipe_id`, `language`, translated fields, `source_hash`, `stale`, `quality_flag`).
- Table: `translation_batch_jobs` for async provider batch orchestration.
- Event hooks (`register_translation_event_hooks`) mark translations stale on recipe changes and can auto-translate on publish.

### Translation admin operations

- Main pages: `/admin/translations`, `/admin/translations/run`
- Operations:
  - Missing/stale sync run
  - Queue run for newest candidates
  - Per-recipe run
  - Batch start (`/admin/translations/batch/start`) and job monitoring
  - Provider test translation (`/admin/translations/test`)
  - DE audit (`/admin/translations/audit-de`) and DE repair (`/admin/translations/repair-de`)

### Provider model

- Provider abstraction in `translation_provider.py`.
- Providers:
  - `translateapi` (HTTP batch + polling)
  - `google_translators` (library fallback)
- Gating:
  - Translation run paths require `TRANSLATEAPI_ENABLED` true.
  - `translateapi` provider additionally requires API key.

### Consistency safeguards

- `source_hash` detects stale translations.
- DE audit heuristics identify likely language mismatch (`quality_flag=suspect_lang_mismatch`).

---

## 10) Security Controls

### Security headers

Headers applied by middleware (and reinforced in exception handlers):

| Header | Value |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | `geolocation=(), microphone=(), camera=()` |
| `Content-Security-Policy` | `default-src 'self'; img-src <CSP_IMG_SRC>; style-src 'self'; script-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'` |
| `Strict-Transport-Security` | Added in prod over HTTPS (`max-age=31536000; includeSubDomains`) |

### Additional controls

- Rate limiting via SlowAPI across auth, uploads, moderation, translation, PDF export routes.
- Trusted host validation enabled when `ALLOWED_HOSTS` is restrictive.
- Proxy header support enabled (reverse-proxy deployments).
- Open redirect prevention via `safe_redirect_path` (rejects external and malformed redirect targets).
- Request context middleware adds request IDs to logs and response headers.
- Security events are written to DB with retention and max-row pruning.

---

## 11) Database & Migrations

### ORM setup

- SQLAlchemy engine/session in `app/database.py`.
- SQLite dev tuning:
  - `journal_mode=WAL`
  - `synchronous=NORMAL`
  - `busy_timeout=30000`
  - `check_same_thread=False`, `timeout=30`

### Migration workflow

```bash
py -m alembic -c alembic.ini upgrade head
py -m alembic -c alembic.ini current
py -m alembic -c alembic.ini heads
```

### Current migration head

- Verified state: `20260304_0016 (head)` for both `current` and `heads`.

### Notes on SQLite locks

- Translation/admin flows include explicit handling for `database is locked` and return user-facing retry hints on affected pages.

---

## 12) Testing Strategy

### Test runner

```bash
py -m pytest -q
```

### Test suites present

- QA Roundup: `tests/test_qa_roundup.py`
- Aggressive user/admin flows: `tests/test_beta_aggressive_user_flow.py`, `tests/test_beta_aggressive_admin_flow.py`
- CSRF/Cookie: `tests/test_security_csrf_cookie.py`
- Upload validation: `tests/test_security_upload_validation.py`
- PDF security: `tests/test_security_pdf_export.py`
- i18n/XSS: `tests/test_security_i18n_xss.py`
- Search validation: `tests/test_security_search_validation.py`
- Session hygiene: `tests/test_security_session_hygiene.py`
- Redirect/Origin/Host: `tests/test_security_open_redirect.py`, `tests/test_security_headers_origin_host.py`
- Rate limits effective: `tests/test_security_rate_limits_effective.py`
- Error info leaks: `tests/test_security_error_info_leaks.py`
- Migration safety: `tests/test_db_migration_safety.py`
- Validation/content abuse: `tests/test_validation_content_abuse.py`
- Translation suites: `tests/test_translation_*`, `tests/test_translations_admin_diagnose.py`, `tests/test_recipe_translations.py`
- Encoding/i18n rendering: `tests/test_encoding_audit.py`, `tests/test_i18n*.py`
- E2E suites (2): `tests/e2e/test_beta_smoke.py`, `tests/e2e/test_user_admin_journey.py`

### Current status (verified)

- Tests total: **133**
- Passed: **133**
- Failed: **0**
- Fix iterations (last run): **1** (from recent hardening cycle)

### Warning status

- Cleanup progression: **11 -> 5 warnings**
- ResourceWarnings fixed: **6**
- Remaining warnings: **5 DeprecationWarnings** (Alembic/SQLAlchemy on Python 3.14)

### Common command set

```bash
# app
py -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload

# full regression
py -m pytest -q

# targeted key suites
py -m pytest -q tests/test_qa_roundup.py
py -m pytest -q tests/test_security_csrf_cookie.py tests/test_security_open_redirect.py
py -m pytest -q tests/test_translation_consistency.py tests/test_translation_batch_jobs.py
```

---

## 13) Known Issues / Technical Debt

- DeprecationWarnings remain from third-party stack (`alembic.config`, `sqlalchemy sqlite datetime adapter`) and are intentionally not patched in app logic.
- Some hardcoded legacy strings still contain mojibake artifacts (broken UTF-8 sequences) in parts of templates/services; functional behavior is unaffected but text quality is inconsistent.
- `debug=False` is fixed in app bootstrap; non-prod trace rendering is handled by custom exception path, but a dedicated dev-only debug switch could improve clarity.

---

## 14) Appendix

### How to reproduce main flows (quick)

1. Start app with Uvicorn on localhost.
2. Register/login as user and verify profile page (`/me`).
3. Submit recipe via `/submit`; verify it appears in `/my-submissions` as pending.
4. Login as admin; review and approve/reject in `/admin/submissions`.
5. Verify published recipes are visible in discover (`/`), pending submissions are not.
6. Open translation admin at `/admin/translations/run`; test provider config and queue run.
7. Open image-change queue `/admin/image-change-requests` and approve/reject requests.
8. Validate PDF export via `/recipes/{id}/pdf`.

### How to run regression/hardening

```bash
# full suite
py -m pytest -q

# migration sanity
py -m pytest -q tests/test_db_migration_safety.py

# core security/hardening suites
py -m pytest -q tests/test_security_*.py

# aggressive end-to-end integration suites
py -m pytest -q tests/test_beta_aggressive_user_flow.py tests/test_beta_aggressive_admin_flow.py
```

### Changelog of last hardening run (touched files)

- `app/main.py`
- `app/middleware.py`
- `app/translation_service.py`
- `app/routers/translations.py`
- `tests/e2e/conftest.py`

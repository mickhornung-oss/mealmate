# MealMate Architecture

This document summarizes the current technical architecture of the implemented system.

## 1) System Overview
MealMate is a server-rendered FastAPI application:
1. Browser sends requests to FastAPI.
2. Routers return HTML (Jinja2), JSON, or file responses.
3. HTMX updates selected UI fragments without a SPA framework.
4. SQLAlchemy manages relational persistence; Alembic manages schema migrations.

## 2) Request Flow
1. Request enters middleware chain:
   - `RequestContextMiddleware`
   - `SecurityHeadersMiddleware`
   - `HTTPSRedirectMiddleware`
   - `CSRFMiddleware`
   - `LanguageMiddleware`
   - `SlowAPIMiddleware`
2. Authentication and role checks are enforced by route dependencies.
3. Jinja templates render full pages or partials.
4. HTMX routes update partial UI sections (for example discover lists or favorite actions).

## 3) Authentication Flow
1. Login creates JWT (`sub=user_uid`) and sets `access_token` as `HttpOnly` cookie.
2. Dependencies resolve current user from cookie/header and validate token.
3. CSRF middleware sets `csrf_token` cookie for safe methods.
4. State-changing methods validate CSRF header/form token against cookie.
5. Logout clears auth cookie.

## 4) Moderation Flow
1. User/guest submits recipe via `/submit`.
2. Entry is stored in `recipe_submissions` with `pending` status.
3. Admin reviews queue at `/admin/submissions`.
4. Approve creates published `recipes` record (including ingredient/image transfer).
5. Reject marks submission as `rejected` and stores `admin_note`.
6. Discover shows only `recipes.is_published=True`.

## 5) Image Flow
1. Image rendering priority:
   - primary `recipe_images`
   - fallback `source_image_url` / `title_image_url`
   - placeholder
2. Admin can directly manage recipe images.
3. Non-admin users can only submit image change requests.
4. Admin approves/rejects image-change queue entries.

## 6) Data Model (Core)
- `users` - accounts, roles, identity metadata
- `recipes` - published recipe entities
- `recipe_submissions` - moderation queue
- `recipe_images` - direct image storage metadata
- `recipe_image_change_requests` / `recipe_image_change_files` - image moderation flow
- `reviews`, `favorites`, `ingredients`, `recipe_ingredients` - interaction and normalization
- `password_reset_tokens`, `security_events` - recovery and security traceability

## 7) Module Layout
- `app/main.py` - app bootstrap, middleware, routers, exception handlers
- `app/routers/` - endpoint groups (`auth`, `recipes`, `submissions`, `admin`, `translations`)
- `app/services.py` - stable service entry-points and compatibility wrappers
- `app/services_import.py` - CSV/KochWiki import domain logic
- `app/services_submission.py` - submission publishing and submission-ingredient transfer domain
- `app/services_runtime.py` - runtime infra helpers (upload validation, meta, token parsing)
- `app/translation_service.py` - translation domain orchestration entry-points
- `app/translation_batch_service.py` - external batch job orchestration/persistence
- `app/translation_batch_mutations.py` - explicit batch job and translation write/mutation handlers
- `app/security.py`, `app/middleware.py`, `app/rate_limit.py` - security and request controls
- `app/templates/` + `app/static/` - UI rendering layer
- `alembic/` - migration history
- `tests/` - unit, integration, and browser E2E coverage

## 8) Repository Structure (Simplified)
```text
app/
  main.py
  routers/
  templates/
  static/
  models.py
  services.py
  security.py
  middleware.py
alembic/
tests/
scripts/
docs/
tools/
```

## 9) Architecture Introspection Utilities
- `python -m tools.print_routes` - prints FastAPI routes as markdown table
- `python -m tools.dump_db_schema` - prints metadata-driven table/column overview

# Project Snapshot

Automatisch erzeugt fuer Diagnosezwecke, ohne Fachlogik-Aenderung.

## 1) Projektstruktur (relevante Ordner)

### backend/app
- `C:/Users/mickh/Desktop/Maschine/Schnittstellen und APIs/Abschluss Projekt/app`
    - `__init__.py`
    - `config.py`
    - `csv_import.py`
    - `database.py`
    - `dependencies.py`
    - `image_utils.py`
    - `logging_config.py`
    - `mailer.py`
    - `main.py`
    - `middleware.py`
    - `models.py`
    - `moderation_repair.py`
    - `pdf_service.py`
    - `rate_limit.py`
    - `security.py`
    - `security_events.py`
    - `services.py`
    - `views.py`
    - `i18n/`
      - `__init__.py`
      - `de.py`
      - `middleware.py`
      - `service.py`
      - `locales/`
        - `de.json`
        - `en.json`
        - `fr.json`
    - `routers/`
      - `__init__.py`
      - `admin.py`
      - `auth.py`
      - `recipes.py`
      - `submissions.py`
    - `services/`
    - `static/`
      - `htmx.min.js`
      - `security.js`
      - `style.css`
    - `templates/`
      - `admin.html`
      - `admin_image_change_request_detail.html`
      - `admin_image_change_requests.html`
      - `admin_submission_detail.html`
      - `admin_submissions.html`
      - `auth_change_email.html`
      - `auth_change_email_confirm.html`
      - `auth_forgot_password.html`
      - `auth_login.html`
      - `auth_register.html`
      - `auth_reset_password.html`
      - `base.html`
      - `error_404.html`
      - `error_500.html`
      - `favorites.html`
      - `home.html`
      - `me.html`
      - `my_recipes.html`
      - `my_submissions.html`
      - `recipe_detail.html`
      - `recipe_form.html`
      - `submit_recipe.html`
      - `partials/`
        - `favorite_button.html`
        - `recipe_card_image.html`
        - `recipe_images.html`
        - `recipe_list.html`

### migrations
- `C:/Users/mickh/Desktop/Maschine/Schnittstellen und APIs/Abschluss Projekt/alembic`
    - `env.py`
    - `script.py.mako`
    - `versions/`
      - `20260303_0001_initial_schema.py`
      - `20260303_0002_add_title_image_url.py`
      - `20260303_0003_seed_and_source_fields.py`
      - `20260303_0004_recipe_images_primary.py`
      - `20260303_0005_recipe_submissions.py`
      - `20260303_0006_add_recipe_is_published.py`
      - `20260303_0007_auth_recovery_fields.py`
      - `20260303_0008_email_change_token_field.py`
      - `20260303_0009_recipe_image_change_requests.py`

### tests
- `C:/Users/mickh/Desktop/Maschine/Schnittstellen und APIs/Abschluss Projekt/tests`
    - `conftest.py`
    - `test_auth_recovery.py`
    - `test_email_change.py`
    - `test_i18n.py`
    - `test_image_change_workflow.py`
    - `test_moderation_workflow.py`
    - `test_publish_guards_api.py`
    - `e2e/`
      - `conftest.py`
      - `test_user_admin_journey.py`

### tools/diagnostics
- `C:/Users/mickh/Desktop/Maschine/Schnittstellen und APIs/Abschluss Projekt/tools/diagnostics`

## 2) Routes Liste

| METHOD | PATH | ROUTER |
|---|---|---|
| GET | / | recipes |
| GET | /admin | admin |
| GET | /admin-only | auth |
| GET | /admin/image-change-files/{file_id} | admin |
| GET | /admin/image-change-requests | admin |
| GET | /admin/image-change-requests/{request_id} | admin |
| POST | /admin/image-change-requests/{request_id}/approve | admin |
| POST | /admin/image-change-requests/{request_id}/reject | admin |
| GET | /admin/import-example.csv | admin |
| POST | /admin/import-recipes | admin |
| GET | /admin/import-template.csv | admin |
| POST | /admin/recipes/{recipe_id}/delete | admin |
| POST | /admin/run-kochwiki-seed | admin |
| GET | /admin/submissions | submissions |
| POST | /admin/submissions/images/{image_id}/delete | submissions |
| POST | /admin/submissions/images/{image_id}/set-primary | submissions |
| GET | /admin/submissions/{submission_id} | submissions |
| POST | /admin/submissions/{submission_id}/approve | submissions |
| POST | /admin/submissions/{submission_id}/edit | submissions |
| POST | /admin/submissions/{submission_id}/reject | submissions |
| POST | /admin/users/{user_id}/role | admin |
| GET | /api/me | auth |
| GET | /auth/change-email | auth |
| GET | /auth/change-email/confirm | auth |
| POST | /auth/change-email/confirm | auth |
| POST | /auth/change-email/request | auth |
| POST | /auth/change-password | auth |
| GET | /auth/forgot-password | auth |
| POST | /auth/forgot-password | auth |
| GET | /auth/login | auth |
| POST | /auth/login | auth |
| GET | /auth/register | auth |
| POST | /auth/register | auth |
| GET | /auth/reset-password | auth |
| POST | /auth/reset-password | auth |
| GET | /categories | recipes |
| GET | /external-image | recipes |
| GET | /favorites | recipes |
| GET | /forgot-password | auth |
| POST | /forgot-password | auth |
| GET | /health | main |
| GET | /healthz | main |
| DELETE | /images/{image_id} | recipes |
| GET | /images/{image_id} | recipes |
| POST | /images/{image_id}/delete | recipes |
| POST | /images/{image_id}/set-primary | recipes |
| GET | /login | auth |
| POST | /login | auth |
| POST | /logout | auth |
| GET | /me | auth |
| GET | /my-recipes | recipes |
| GET | /my-submissions | submissions |
| POST | /profile/username | auth |
| POST | /recipes | recipes |
| GET | /recipes/new | recipes |
| POST | /recipes/new | recipes |
| GET | /recipes/{recipe_id} | recipes |
| POST | /recipes/{recipe_id}/delete | recipes |
| GET | /recipes/{recipe_id}/edit | recipes |
| POST | /recipes/{recipe_id}/edit | recipes |
| POST | /recipes/{recipe_id}/favorite | recipes |
| POST | /recipes/{recipe_id}/image-change-request | recipes |
| POST | /recipes/{recipe_id}/images | recipes |
| GET | /recipes/{recipe_id}/pdf | recipes |
| POST | /recipes/{recipe_id}/reviews | recipes |
| GET | /register | auth |
| POST | /register | auth |
| POST | /reviews/{review_id}/delete | recipes |
| GET | /submission-images/{image_id} | submissions |
| GET | /submit | submissions |
| POST | /submit | submissions |

## 3) Datenmodell Uebersicht

### users
- `id`: `INTEGER` (PK, NOT NULL)
- `user_uid`: `VARCHAR(36)` (NOT NULL)
- `email`: `VARCHAR(255)` (NOT NULL)
- `username`: `VARCHAR(30)`
- `username_normalized`: `VARCHAR(30)`
- `hashed_password`: `VARCHAR(255)` (NOT NULL)
- `role`: `VARCHAR(20)` (NOT NULL)
- `last_login_at`: `DATETIME`
- `last_login_ip`: `VARCHAR(64)`
- `last_login_user_agent`: `VARCHAR(200)`
- `created_at`: `DATETIME` (NOT NULL)

### recipes
- `id`: `INTEGER` (PK, NOT NULL)
- `title`: `VARCHAR(255)` (NOT NULL)
- `title_image_url`: `VARCHAR(1024)`
- `source`: `VARCHAR(50)` (NOT NULL)
- `source_uuid`: `VARCHAR(120)`
- `source_url`: `VARCHAR(1024)`
- `source_image_url`: `VARCHAR(1024)`
- `servings_text`: `VARCHAR(120)`
- `total_time_minutes`: `INTEGER`
- `is_published`: `BOOLEAN` (NOT NULL)
- `description`: `TEXT` (NOT NULL)
- `instructions`: `TEXT` (NOT NULL)
- `category`: `VARCHAR(120)` (NOT NULL)
- `prep_time_minutes`: `INTEGER` (NOT NULL)
- `difficulty`: `VARCHAR(30)` (NOT NULL)
- `creator_id`: `INTEGER` (NOT NULL) -> users.id
- `created_at`: `DATETIME` (NOT NULL)

### recipe_submissions
- `id`: `INTEGER` (PK, NOT NULL)
- `submitter_user_id`: `INTEGER` -> users.id
- `submitter_email`: `VARCHAR(255)`
- `title`: `VARCHAR(255)` (NOT NULL)
- `description`: `TEXT` (NOT NULL)
- `category`: `VARCHAR(120)`
- `difficulty`: `VARCHAR(30)` (NOT NULL)
- `prep_time_minutes`: `INTEGER`
- `servings_text`: `VARCHAR(120)`
- `instructions`: `TEXT` (NOT NULL)
- `status`: `VARCHAR(8)` (NOT NULL)
- `admin_note`: `TEXT`
- `reviewed_by_admin_id`: `INTEGER` -> users.id
- `reviewed_at`: `DATETIME`
- `created_at`: `DATETIME` (NOT NULL)

### reviews
- `id`: `INTEGER` (PK, NOT NULL)
- `recipe_id`: `INTEGER` (NOT NULL) -> recipes.id
- `user_id`: `INTEGER` (NOT NULL) -> users.id
- `rating`: `INTEGER` (NOT NULL)
- `comment`: `TEXT` (NOT NULL)
- `created_at`: `DATETIME` (NOT NULL)

### favorites
- `user_id`: `INTEGER` (PK, NOT NULL) -> users.id
- `recipe_id`: `INTEGER` (PK, NOT NULL) -> recipes.id
- `created_at`: `DATETIME` (NOT NULL)

### recipe_images
- `id`: `INTEGER` (PK, NOT NULL)
- `recipe_id`: `INTEGER` (NOT NULL) -> recipes.id
- `filename`: `VARCHAR(255)` (NOT NULL)
- `content_type`: `VARCHAR(50)` (NOT NULL)
- `data`: `BLOB` (NOT NULL)
- `is_primary`: `BOOLEAN` (NOT NULL)
- `created_at`: `DATETIME` (NOT NULL)

### recipe_image_change_requests
- `id`: `INTEGER` (PK, NOT NULL)
- `recipe_id`: `INTEGER` (NOT NULL) -> recipes.id
- `requester_user_id`: `INTEGER` -> users.id
- `status`: `VARCHAR(8)` (NOT NULL)
- `admin_note`: `TEXT`
- `reviewed_by_admin_id`: `INTEGER` -> users.id
- `created_at`: `DATETIME` (NOT NULL)
- `reviewed_at`: `DATETIME`

### recipe_image_change_files
- `id`: `INTEGER` (PK, NOT NULL)
- `request_id`: `INTEGER` (NOT NULL) -> recipe_image_change_requests.id
- `filename`: `VARCHAR(255)` (NOT NULL)
- `content_type`: `VARCHAR(50)` (NOT NULL)
- `data`: `BLOB` (NOT NULL)
- `created_at`: `DATETIME` (NOT NULL)

### password_reset_tokens
- `id`: `INTEGER` (PK, NOT NULL)
- `user_id`: `INTEGER` (NOT NULL) -> users.id
- `new_email_normalized`: `VARCHAR(255)`
- `token_hash`: `VARCHAR(64)` (NOT NULL)
- `created_at`: `DATETIME` (NOT NULL)
- `expires_at`: `DATETIME` (NOT NULL)
- `used_at`: `DATETIME`
- `created_ip`: `VARCHAR(64)`
- `created_user_agent`: `VARCHAR(200)`
- `purpose`: `VARCHAR(50)` (NOT NULL)

## 4) Auth und Settings

### ENV Key-Namen (ohne Werte)
- `ALGORITHM`
- `ALLOWED_HOSTS`
- `ALLOWED_IMAGE_TYPES`
- `APP_ENV`
- `APP_NAME`
- `APP_URL`
- `AUTO_SEED_KOCHWIKI`
- `COOKIE_SECURE`
- `CSP_IMG_SRC`
- `CSRF_COOKIE_NAME`
- `CSRF_HEADER_NAME`
- `DATABASE_URL`
- `ENABLE_KOCHWIKI_SEED`
- `FORCE_HTTPS`
- `IMPORT_DOWNLOAD_IMAGES`
- `KOCHWIKI_CSV_PATH`
- `LOG_LEVEL`
- `MAIL_OUTBOX_EMAIL_CHANGE_PATH`
- `MAIL_OUTBOX_PATH`
- `MAX_CSV_UPLOAD_MB`
- `MAX_UPLOAD_MB`
- `PASSWORD_RESET_TOKEN_MINUTES`
- `SECRET_KEY`
- `SECURITY_EVENT_MAX_ROWS`
- `SECURITY_EVENT_RETENTION_DAYS`
- `SEED_ADMIN_EMAIL`
- `SEED_ADMIN_PASSWORD`
- `SMTP_FROM`
- `SMTP_HOST`
- `SMTP_PASSWORD`
- `SMTP_PORT`
- `SMTP_USER`
- `TOKEN_EXPIRE_MINUTES`

### Auth/CSRF Konventionen
- Auth Cookie Name: `access_token`
- CSRF Header Name: `X-CSRF-Token` (konfigurierbar ueber `CSRF_HEADER_NAME`)
- CSRF Form Field Name: `csrf_token`

## 5) Templates

### Haupttemplates
- `home.html`
- `recipe_detail.html`
- `submit_recipe.html`
- `admin.html`
- `admin_submissions.html`
- `admin_image_change_requests.html`
- `me.html`
- `auth_login.html`
- `auth_register.html`
- `auth_forgot_password.html`
- `auth_reset_password.html`

### Wichtige Form Actions (fuer stabile E2E-Selektoren)
- `action="/admin/image-change-requests"`
- `action="/admin/image-change-requests/{{ image_change_request.id }}/approve"`
- `action="/admin/image-change-requests/{{ image_change_request.id }}/reject"`
- `action="/admin/import-recipes"`
- `action="/admin/recipes/{{ recipe.id }}/delete"`
- `action="/admin/submissions"`
- `action="/admin/submissions/images/{{ image.id }}/delete"`
- `action="/admin/submissions/images/{{ image.id }}/set-primary"`
- `action="/admin/submissions/{{ submission.id }}/approve"`
- `action="/admin/submissions/{{ submission.id }}/edit"`
- `action="/admin/submissions/{{ submission.id }}/reject"`
- `action="/admin/users/{{ user.id }}/role"`
- `action="/auth/change-email/confirm"`
- `action="/auth/change-email/request"`
- `action="/auth/change-password"`
- `action="/auth/forgot-password"`
- `action="/auth/reset-password"`
- `action="/images/{{ image.id }}/delete"`
- `action="/images/{{ image.id }}/set-primary"`
- `action="/login"`
- `action="/logout"`
- `action="/profile/username"`
- `action="/recipes/{{ recipe.id }}/delete"`
- `action="/recipes/{{ recipe.id }}/favorite"`
- `action="/recipes/{{ recipe.id }}/image-change-request"`
- `action="/recipes/{{ recipe.id }}/images"`
- `action="/recipes/{{ recipe.id }}/reviews"`
- `action="/register"`
- `action="/reviews/{{ review.id }}/delete"`
- `action="/submit"`
- `action="{% if form_mode == 'edit' %}/recipes/{{ recipe.id }}/edit{% else %}/recipes/new{% endif %}"`

### Gefundene Template IDs
- `id="card-image-{{ recipe.id }}"`
- `id="category_new"`
- `id="category_select"`
- `id="favorite-box"`
- `id="new-category-wrapper"`
- `id="recipe-images-section"`
- `id="recipe-list"`

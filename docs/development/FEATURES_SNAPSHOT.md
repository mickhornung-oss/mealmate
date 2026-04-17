# MealMate Features Snapshot

Aktueller Stand wurde aus `app/main.py`, `app/routers/*`, `app/models.py`, `app/templates/*`, `app/services.py` und `tests/*` abgeleitet.

## Core Architektur

Status: ✅
- FastAPI App bindet die Router `auth`, `recipes`, `submissions` und `admin` zentral in `app/main.py`.
- Frontend ist server-rendered mit Jinja2 und HTMX-Partials fuer Discover, Favorite und Bildbereiche.
- SQLAlchemy 2.0 + Alembic sind aktiv und `start.sh` fuehrt Migrationen vor App-Start aus.

## Auth & Accounts

Status: ✅
- Login mit E-Mail oder Username ist aktiv, Auth-Session liegt als JWT in `HttpOnly` Cookie `access_token`.
- CSRF-Schutz laeuft global ueber Middleware mit Cookie + Header/Form-Token fuer state-changing Requests.
- Profilfunktionen enthalten `user_uid`, Username-Update, Passwortwechsel, Forgot/Reset und E-Mail-Aenderung mit bestaetigtem Token.

## Rezepte

Status: ✅
- Discover (`/`) bietet Filter, Sortierung und Pagination und zeigt nur `is_published=True` Rezepte.
- Rezeptdetail zeigt Zutaten, Reviews, Favoriten-Button und PDF-Download ueber `/recipes/{id}/pdf`.
- Direkte Rezept-Erstellung (`/recipes/new`) ist admin-only, Edit/Delete bleibt fuer Owner/Admin auf publizierten Rezepten verfuegbar.

## Moderation

Status: ✅
- User/Gast reichen ueber `/submit` ein und erzeugen immer `recipe_submissions` mit Status `pending`.
- Admin-Queue unter `/admin/submissions` ermoeglicht Vorschau, Edit, Approve und Reject mit `admin_note`.
- Erst Approve ueberfuehrt in `recipes` und macht Einreichungen in Discover sichtbar.

## Bilder

Status: ✅
- Anzeige-Fallback ist implementiert als DB-Primary-Bild -> externe URL (`source_image_url`/`title_image_url`) -> Placeholder.
- Admin darf Rezeptbilder direkt hochladen und Primary setzen, normale User erzeugen nur pending Bildaenderungsantraege.
- Admin moderiert Bildaenderungen in `/admin/image-change-requests` mit Approve/Reject.

## Imports & Seed

Status: ⚠️
- Admin CSV Import mit Preview, Dry-Run, Insert-Only Default und optionalem Update ist vorhanden.
- Auto-Seed ist per Flags steuerbar (`ENABLE_KOCHWIKI_SEED`, `AUTO_SEED_KOCHWIKI`) und in Prod standardmaessig aus.
- CSV Import ist funktional, benoetigt fuer Beta aber weiterhin saubere Operator-Disziplin bei Update-Modus.

## i18n

Status: ✅
- Sprachaufloesung folgt `?lang` -> Cookie -> `Accept-Language` -> Default `de`.
- Lokale JSON-Dateien fuer `de`, `en`, `fr` sind eingebunden und ueber `t(...)` in Templates nutzbar.
- Navbar hat Language-Switch mit persistierendem Cookie.

## Security

Status: ✅
- Security-Header Middleware setzt CSP, XFO, nosniff, Referrer-Policy und optional HSTS in Prod.
- Rate Limits sind fuer Login, Register, Passwort- und Moderationspfade gesetzt.
- Upload-Validierung prueft MIME, Groesse und Magic-Bytes fuer Bilduploads.

## Logging & Ops

Status: ✅
- Request-ID Middleware setzt `X-Request-ID` und schreibt strukturierte Request-Logs.
- Healthchecks sind unter `/health` und `/healthz` ohne Login erreichbar.
- Deploy-Artefakte (`Dockerfile`, `docker-compose.yml`, `render.yaml`, `docs/deployment/DEPLOYMENT.md`) sind vorhanden.

## Tests

Status: ✅
- Unit/API Tests fuer Auth-Recovery, E-Mail-Change, Moderation, i18n und Bildworkflow existieren.
- E2E Browser-Suite (Playwright + pytest) fuer User- und Admin-Journeys liegt unter `tests/e2e/`.
- Ohne installiertes Playwright/Chromium werden E2E bewusst als `skipped` markiert statt den gesamten Testlauf zu brechen.

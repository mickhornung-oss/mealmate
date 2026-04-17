# Block 13 - Auth-/Permission-Contract-Hardening

Datum: 2026-04-17  
Status: Abgeschlossen (gruen)

## Ziel des Blocks
Mehrere zusammenhaengende Auth-/Permission-Bereiche in einem grossen Schnitt haerten:

1. Auth-/Permission-Entscheidungen expliziter machen  
2. 401/403/404-Semantik an kritischen Zugriffskanten konsolidieren  
3. Resource-Leakage in priorisierten Pfaden reduzieren  
4. Vertragskanten regressionssicher testen

## Gehaertete Bereiche

### 1) Zentrale AuthZ-Helfer (`app/dependencies.py`)
- Neue Helper eingefuehrt:
  - `ensure_admin_or_403(...)`
  - `ensure_owner_or_admin_or_404(...)`
- `get_admin_user(...)` nutzt jetzt `ensure_admin_or_403(...)`.
- Wirkung:
  - konsistenterer Admin-Contract an einem zentralen Ort.
  - klarere Wiederverwendung fuer Router mit gemischten Auth-/Permission-Entscheidungen.

### 2) Admin-only Image-Mutationspfade ohne Existenz-Leak fuer Non-Admin (`app/routers/recipes.py`)
- Kritische Endpunkte auf fruehen Admin-Check umgestellt:
  - `DELETE /images/{image_id}`
  - `POST /images/{image_id}/delete`
  - `POST /images/{image_id}/set-primary`
  - `POST /recipes/{recipe_id}/images` (konsistent ueber Helper statt inline Check)
- Wirkung:
  - fuer eingeloggte Non-Admin-Nutzer ist die Antwort fuer vorhandene und fehlende IDs konsistent `403`.
  - Existenz der Zielressource wird in diesen Admin-only Pfaden nicht mehr ueber 404-vs-403 differenzierbar.

### 3) Submission-Image-Zugriff mit expliziter Ownership-/Leakage-Regel (`app/routers/submissions.py`)
- `GET /submission-images/{image_id}` von optionalem Userkontext auf verpflichtende Auth umgestellt:
  - `Depends(get_current_user)` statt `get_current_user_optional`.
- Neuer Zugriffspfad:
  - `fetch_submission_image_for_user_or_404(...)`
  - admin: direkter Zugriff auf Bild-ID
  - normaler Nutzer: Query scoped auf eigene Submission (`submitter_user_id == current_user.id`)
- Wirkung:
  - `401` fuer nicht eingeloggte Zugriffe.
  - `404` fuer eingeloggte Nicht-Besitzer (Resource-Existenz wird maskiert).
  - `200` fuer Besitzer und Admin.

## Neue Vertrags-/Regressionstests

Datei: `tests/test_auth_permission_contracts.py`

- `test_recipe_image_delete_api_non_admin_returns_403_for_existing_and_missing`
  - prueft 403-Konsistenz fuer Existing-vs-Missing in Admin-only Delete API.
- `test_recipe_image_set_primary_form_non_admin_returns_403_for_existing_and_missing`
  - prueft 403-Konsistenz fuer Existing-vs-Missing im Form-Endpoint.
- `test_submission_image_requires_auth_and_masks_non_owner_as_404`
  - prueft 401 (unauth), 404 (non-owner), 200 (owner/admin).
- `test_submission_image_owner_query_does_not_load_foreign_rows`
  - prueft Zugriffsgrenze zwischen outsider/admin auf denselben Submission-Image-Pfad.

## Reale Verifikation

Ausgefuehrt:

1. `python -m compileall app tests`  
2. gezielte Regression:
   - `pytest -q tests/test_auth_permission_contracts.py tests/test_api_error_contracts.py tests/test_router_write_path_contracts.py tests/test_router_read_query_contracts.py tests/test_router_render_context_contracts.py`
   - Ergebnis: `25 passed`
3. Vollsuite:
   - `pytest -q` -> `163 passed, 4 skipped`
4. Warning-strict:
   - `pytest -q -W error` -> `163 passed, 4 skipped`
5. Health:
   - `/healthz` -> `200 {"status":"ok"}`

Hinweis:
- Die 4 Skips bleiben erwartete Playwright-Skips (lokal fehlende Browser-Binaries).

## Verhaltensgleichheit / bewusste Vereinheitlichungen

- Keine neuen Features, Rollen oder Policies.
- Keine Aenderung an Erfolgspfaden der gehaerteten Endpunkte.
- Bewusste Sicherheitsvereinheitlichung:
  - Submission-Image Non-Owner antwortet nun `404` (statt vorherigem `403`) zur Leakage-Reduktion.
  - Admin-only Image-Mutationspfade liefern fuer Non-Admin konsistent `403` unabhaengig von Ressourcenexistenz.

## Bewusst offen gelassen

- Keine globale Vereinheitlichung aller Auth-/Permission-Pfade in allen Routern; Fokus lag auf den kritischsten, API-/upload-nahen Kanten.
- Keine zusaetzliche HTML-spezifische Access-Denied-Seitenlogik fuer 401/403 im globalen Exception-Handling.
- Keine neue Rollen-/Policy-Engine.

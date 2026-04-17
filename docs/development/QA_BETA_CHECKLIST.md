# QA Beta Checklist

Diese Checkliste deckt manuelle Beta-Abnahme und die Aggressivtest-Suite ab.

## Vorbedingungen

1. App starten: `uvicorn app.main:app --reload`
2. Migrationen ausfuehren: `alembic upgrade head`
3. Mindestens ein Admin- und ein User-Konto vorhanden

## User Journey (manuell)

1. Registrieren auf `/register` und danach einloggen auf `/login`
2. Profilseite `/me`: Username setzen und Passwort wechseln
3. Passwort vergessen: `/auth/forgot-password` und Reset-Link nutzen
4. Rezept einreichen ueber `/submit`
5. Pruefen: Einreichung sichtbar unter `/my-submissions`, aber nicht auf `/`
6. Favorit toggeln auf `/recipes/{id}` und auf `/favorites` validieren
7. Review senden auf `/recipes/{id}` und Anzeige kontrollieren
8. PDF laden auf `/recipes/{id}/pdf`

Pass:
- Submission bleibt `pending` und erscheint nicht im Discover.
- Passwort-Flow, Favoriten, Reviews und PDF funktionieren.

Fail:
- Eingereichtes Rezept erscheint sofort live auf `/`.
- Passwort-Reset oder PDF liefert falsches Verhalten.

## Admin Journey (manuell)

1. Admin-Login auf `/login`
2. Moderation oeffnen: `/admin/submissions`
3. Pending Submission approven und Discover pruefen
4. Zweite Pending Submission rejecten mit Grund
5. Admin-Rezept direkt anlegen ueber `/recipes/new`
6. Bildaenderungen pruefen ueber `/admin/image-change-requests`

Pass:
- Approve macht Rezept sichtbar in Discover.
- Reject bleibt unsichtbar und speichert `admin_note`.
- Direkt erstelltes Admin-Rezept ist sofort sichtbar.

Fail:
- Pending/Rejected landet im Discover.
- Moderationsaktionen aendern den Status nicht.

## Sicherheitschecks (manuell)

1. CSRF: POST ohne Token muss `403` liefern
2. CSRF: POST mit Token muss normal funktionieren
3. Rate Limits: Login >5/min und Forgot/Reset >5/min fuehrt zu `429`
4. Rechtecheck: User darf nicht direkt publishen (`POST /recipes` -> `403`)
5. Regression: Discover zeigt nur `recipes.is_published = true`

Pass:
- Schutzmechanismen greifen mit korrekten Statuscodes.

Fail:
- POST ohne CSRF oder User-Direct-Publish wird akzeptiert.

## Aggressivtest Suite (automatisiert)

1. Komplett: `pytest -q`
2. User-Flow Integration: `pytest -q tests/test_beta_aggressive_user_flow.py`
3. Admin-Flow Integration: `pytest -q tests/test_beta_aggressive_admin_flow.py`
4. E2E Smoke: `pytest -q tests/e2e/test_beta_smoke.py`
5. Guard-Tests: `pytest -q tests/test_publish_guards_api.py`

Erwartung:
- Integrationstests sind gruen.
- E2E Smoke ist gruen oder sauber `skipped`, wenn Playwright/Browser fehlt.

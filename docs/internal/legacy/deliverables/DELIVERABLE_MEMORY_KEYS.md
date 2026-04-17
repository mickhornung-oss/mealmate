# Gedaechtnisschluessel Deliverable

## Betroffene Dateien

- docs/FEATURES_SNAPSHOT.md
- docs/QA_BETA_CHECKLIST.md
- docs/ROADMAP.md
- docs/BACKLOG.md
- docs/ARCHITECTURE.md
- CHANGELOG.md
- tools/__init__.py
- tools/print_routes.py
- tools/dump_db_schema.py

## docs/FEATURES_SNAPSHOT.md

`$lang
# MealMate Features Snapshot

Aktueller Stand wurde aus `app/main.py`, `app/routers/*`, `app/models.py`, `app/templates/*`, `app/services.py` und `tests/*` abgeleitet.

## Core Architektur

Status: âœ…
- FastAPI App bindet die Router `auth`, `recipes`, `submissions` und `admin` zentral in `app/main.py`.
- Frontend ist server-rendered mit Jinja2 und HTMX-Partials fuer Discover, Favorite und Bildbereiche.
- SQLAlchemy 2.0 + Alembic sind aktiv und `start.sh` fuehrt Migrationen vor App-Start aus.

## Auth & Accounts

Status: âœ…
- Login mit E-Mail oder Username ist aktiv, Auth-Session liegt als JWT in `HttpOnly` Cookie `access_token`.
- CSRF-Schutz laeuft global ueber Middleware mit Cookie + Header/Form-Token fuer state-changing Requests.
- Profilfunktionen enthalten `user_uid`, Username-Update, Passwortwechsel, Forgot/Reset und E-Mail-Aenderung mit bestaetigtem Token.

## Rezepte

Status: âœ…
- Discover (`/`) bietet Filter, Sortierung und Pagination und zeigt nur `is_published=True` Rezepte.
- Rezeptdetail zeigt Zutaten, Reviews, Favoriten-Button und PDF-Download ueber `/recipes/{id}/pdf`.
- Direkte Rezept-Erstellung (`/recipes/new`) ist admin-only, Edit/Delete bleibt fuer Owner/Admin auf publizierten Rezepten verfuegbar.

## Moderation

Status: âœ…
- User/Gast reichen ueber `/submit` ein und erzeugen immer `recipe_submissions` mit Status `pending`.
- Admin-Queue unter `/admin/submissions` ermoeglicht Vorschau, Edit, Approve und Reject mit `admin_note`.
- Erst Approve ueberfuehrt in `recipes` und macht Einreichungen in Discover sichtbar.

## Bilder

Status: âœ…
- Anzeige-Fallback ist implementiert als DB-Primary-Bild -> externe URL (`source_image_url`/`title_image_url`) -> Placeholder.
- Admin darf Rezeptbilder direkt hochladen und Primary setzen, normale User erzeugen nur pending Bildaenderungsantraege.
- Admin moderiert Bildaenderungen in `/admin/image-change-requests` mit Approve/Reject.

## Imports & Seed

Status: âš ï¸
- Admin CSV Import mit Preview, Dry-Run, Insert-Only Default und optionalem Update ist vorhanden.
- Auto-Seed ist per Flags steuerbar (`ENABLE_KOCHWIKI_SEED`, `AUTO_SEED_KOCHWIKI`) und in Prod standardmaessig aus.
- CSV Import ist funktional, benoetigt fuer Beta aber weiterhin saubere Operator-Disziplin bei Update-Modus.

## i18n

Status: âœ…
- Sprachaufloesung folgt `?lang` -> Cookie -> `Accept-Language` -> Default `de`.
- Lokale JSON-Dateien fuer `de`, `en`, `fr` sind eingebunden und ueber `t(...)` in Templates nutzbar.
- Navbar hat Language-Switch mit persistierendem Cookie.

## Security

Status: âœ…
- Security-Header Middleware setzt CSP, XFO, nosniff, Referrer-Policy und optional HSTS in Prod.
- Rate Limits sind fuer Login, Register, Passwort- und Moderationspfade gesetzt.
- Upload-Validierung prueft MIME, Groesse und Magic-Bytes fuer Bilduploads.

## Logging & Ops

Status: âœ…
- Request-ID Middleware setzt `X-Request-ID` und schreibt strukturierte Request-Logs.
- Healthchecks sind unter `/health` und `/healthz` ohne Login erreichbar.
- Deploy-Artefakte (`Dockerfile`, `docker-compose.yml`, `render.yaml`, `README_DEPLOY.md`) sind vorhanden.

## Tests

Status: âœ…
- Unit/API Tests fuer Auth-Recovery, E-Mail-Change, Moderation, i18n und Bildworkflow existieren.
- E2E Browser-Suite (Playwright + pytest) fuer User- und Admin-Journeys liegt unter `tests/e2e/`.
- Ohne installiertes Playwright/Chromium werden E2E bewusst als `skipped` markiert statt den gesamten Testlauf zu brechen.
```
ZEILEN-ERKLAERUNG
1. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
2. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
3. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
4. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
5. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
6. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
7. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
8. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
9. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
10. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
11. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
12. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
13. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
14. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
15. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
16. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
17. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
18. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
19. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
20. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
21. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
22. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
23. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
24. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
25. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
26. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
27. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
28. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
29. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
30. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
31. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
32. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
33. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
34. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
35. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
36. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
37. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
38. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
39. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
40. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
41. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
42. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
43. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
44. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
45. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
46. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
47. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
48. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
49. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
50. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
51. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
52. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
53. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
54. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
55. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
56. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
57. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
58. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
59. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
60. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
61. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
62. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
63. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
64. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
65. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
66. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
67. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
68. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
69. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
70. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
71. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
72. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.
73. Diese Zeile ist Bestandteil der Datei docs/FEATURES_SNAPSHOT.md.

## docs/QA_BETA_CHECKLIST.md

`$lang
# QA Beta Checklist

Diese Checkliste ist fuer manuelle Beta-Abnahme plus Referenz auf automatisierte Tests.

## Vorbedingungen

1. App startet lokal ohne Fehler (`uvicorn app.main:app --reload`).
2. DB ist migriert (`alembic upgrade head`).
3. Mindestens ein Admin- und ein User-Account sind vorhanden.

## User Journeys

### U1 Registrierung und Login

Schritte:
1. `/register` oeffnen und neuen Account anlegen.
2. Automatischen Redirect auf Discover pruefen.
3. Abmelden und mit gleicher Identitaet erneut einloggen.

Pass:
- Registrierung liefert keine Fehlerseite.
- Login mit korrekten Daten funktioniert.

Fail:
- Fehlermeldung trotz gueltiger Eingaben.
- Session-Cookie fehlt nach Login.

### U2 Profil, Username, Passwort

Schritte:
1. `/me` oeffnen und Username setzen oder aendern.
2. Passwort mit altem Passwort aendern.
3. Ausloggen und mit neuem Passwort einloggen.

Pass:
- Username wird persistent angezeigt.
- Altes Passwort funktioniert nicht mehr, neues Passwort funktioniert.

Fail:
- Username bleibt unveraendert.
- Passwortwechsel ohne altes Passwort moeglich.

### U3 Forgot und Reset

Schritte:
1. `/auth/forgot-password` nutzen.
2. Reset-Link aus DEV-Outbox oeffnen.
3. Neues Passwort setzen und einloggen.

Pass:
- Forgot Antwort bleibt generisch.
- Reset-Link funktioniert genau einmal.

Fail:
- Token mehrfach verwendbar.
- Reset ohne gueltigen Token moeglich.

### U4 Rezept einreichen, Favorit, Review, PDF

Schritte:
1. `/submit` ausfuellen und absenden.
2. Discover pruefen, ob das neue Rezept nicht sichtbar ist.
3. `/my-submissions` pruefen, ob Status `pending` sichtbar ist.
4. Ein publiziertes Rezept als Favorit markieren und wieder entfernen.
5. Review schreiben.
6. PDF-Link klicken.

Pass:
- Submission bleibt pending.
- Favorit und Review werden korrekt gespeichert.
- PDF liefert `application/pdf`.

Fail:
- Submission erscheint sofort in Discover.
- PDF-Endpoint gibt kein PDF zurueck.

## Admin Journeys

### A1 Submission Moderation

Schritte:
1. `/admin/submissions` oeffnen.
2. Eine pending Submission approven.
3. Eine weitere pending Submission mit Grund rejecten.
4. Discover pruefen.

Pass:
- Approve erzeugt sichtbares Rezept in Discover.
- Rejected Submission bleibt unsichtbar und hat `admin_note`.

Fail:
- Rejected Submission wird trotzdem angezeigt.
- Approve ohne Statuswechsel.

### A2 Admin Direct Publish

Schritte:
1. `/recipes/new` nutzen und Rezept erstellen.
2. Discover neu laden.

Pass:
- Rezept ist sofort sichtbar.

Fail:
- Rezept bleibt unsichtbar trotz erfolgreichem Submit.

### A3 Bildaenderungs-Moderation

Schritte:
1. `/admin/image-change-requests` oeffnen.
2. Pending Anfrage approven oder rejecten.
3. Rezeptdetail pruefen.

Pass:
- Approve setzt neues Primary-Bild.
- Reject aendert Rezeptbild nicht.

Fail:
- Status bleibt pending nach Aktion.
- Bild wird trotz Reject ersetzt.

## Sicherheitschecks

### S1 CSRF

Schritte:
1. Einen POST ohne CSRF Header/Field senden.
2. Gleichen POST mit gueltigem Token senden.

Pass:
- Ohne Token `403`.
- Mit Token normaler Erfolg.

Fail:
- POST ohne Token wird akzeptiert.

### S2 Rate Limit

Schritte:
1. Login mehrfach (>5/min pro IP) mit falschen Daten ausfuehren.
2. Passwort-Reset-Endpunkte analog mehrfach triggern.

Pass:
- Endpoint liefert `429` bei Ueberschreitung.

Fail:
- Kein `429` trotz klarer Limit-Ueberschreitung.

### S3 Zugriffskontrolle

Schritte:
1. Als normaler User `POST /recipes` ausfuehren.
2. Als User Admin-Seiten aufrufen.

Pass:
- Direct publish als User liefert `403`.
- Admin-Bereiche sind fuer User gesperrt.

Fail:
- User kann direkt publizieren.

## Regression Checks

1. Discover zeigt nur publizierte Rezepte.
2. Pending und rejected Submissions sind nur in Moderations-/Owner-Ansichten sichtbar.
3. Bild-Fallback bleibt DB -> externe URL -> Placeholder.

## Automatisierte Referenztests

1. `pytest -q` fuer kompletten Suite-Run.
2. `tests/test_publish_guards_api.py` prueft Publish-Guard und Discover-Filter.
3. `tests/e2e/test_user_admin_journey.py` prueft Ende-zu-Ende Journeys (bei installiertem Playwright).
```
ZEILEN-ERKLAERUNG
1. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
2. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
3. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
4. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
5. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
6. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
7. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
8. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
9. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
10. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
11. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
12. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
13. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
14. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
15. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
16. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
17. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
18. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
19. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
20. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
21. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
22. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
23. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
24. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
25. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
26. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
27. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
28. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
29. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
30. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
31. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
32. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
33. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
34. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
35. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
36. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
37. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
38. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
39. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
40. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
41. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
42. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
43. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
44. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
45. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
46. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
47. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
48. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
49. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
50. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
51. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
52. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
53. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
54. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
55. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
56. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
57. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
58. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
59. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
60. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
61. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
62. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
63. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
64. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
65. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
66. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
67. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
68. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
69. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
70. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
71. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
72. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
73. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
74. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
75. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
76. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
77. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
78. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
79. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
80. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
81. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
82. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
83. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
84. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
85. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
86. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
87. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
88. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
89. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
90. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
91. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
92. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
93. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
94. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
95. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
96. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
97. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
98. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
99. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
100. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
101. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
102. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
103. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
104. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
105. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
106. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
107. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
108. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
109. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
110. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
111. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
112. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
113. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
114. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
115. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
116. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
117. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
118. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
119. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
120. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
121. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
122. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
123. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
124. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
125. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
126. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
127. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
128. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
129. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
130. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
131. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
132. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
133. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
134. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
135. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
136. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
137. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
138. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
139. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
140. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
141. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
142. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
143. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
144. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
145. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
146. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
147. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
148. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
149. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
150. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
151. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
152. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
153. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
154. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
155. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
156. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
157. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
158. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
159. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
160. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
161. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
162. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
163. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
164. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
165. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
166. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
167. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
168. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
169. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
170. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
171. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.
172. Diese Zeile ist Bestandteil der Datei docs/QA_BETA_CHECKLIST.md.

## docs/ROADMAP.md

`$lang
# MealMate Roadmap

Diese Roadmap priorisiert Stabilitaet, Beta-Qualitaet und danach Produktreife.

## Phase 1: Blocker und Stabilitaet (P0)

Zieldefinition:
- Keine kritischen Publish- oder Rechteverletzungen mehr.
- Kernflows fuer User und Admin sind reproduzierbar testbar.

Aufgaben:
1. Publish-Guards dauerhaft absichern (User darf nie direkt publizieren).
2. Moderationsstatus in allen Listings und APIs konsistent erzwingen.
3. E2E Testlauf in lokaler Umgebung stabilisieren (Playwright installiert, reproduzierbar).
4. Fehlerseiten und Fehlermeldungen in Kernflows vereinheitlichen.

Definition of Done:
- `pytest -q` ist gruen.
- Manuelle QA fuer User/Admin Kernjourneys ist Pass.
- Kein bekannter P0 Bug offen.

## Phase 2: Beta Qualitaet (P1)

Zieldefinition:
- Produkt ist fuer externe Beta-Nutzer robust und nachvollziehbar.

Aufgaben:
1. Moderations-Dashboard Usability verbessern (bessere Filter, schnellere Queue-Aktionen).
2. CSV Import Report UX schaerfen (klare Fatal/Warn-Visualisierung).
3. Security Monitoring erweitern (mehr auditierbare Events ohne PII-Leak).
4. Testabdeckung fuer edge cases erhoehen (z. B. parallele Moderation, doppelte Aktionen).

Definition of Done:
- Keine offenen P1 Bugs mit reproduzierbarem Workaround.
- QA Beta Checklist komplett Pass.
- Beta-Dokumentation aktuell und fuer Tester nutzbar.

## Phase 3: UX und Polish (P2)

Zieldefinition:
- Bedienung ist bei grossem Datenbestand effizient und visuell konsistent.

Aufgaben:
1. Discover Performance bei vielen Rezepten verbessern (Query-Optimierungen, Caching wo sinnvoll).
2. Form UX vereinheitlichen (Inline-Feedback, bessere Fehlermeldungspositionierung).
3. Bilder-Workflow fuer User klarer machen (Status-Hinweise und Verlauf von Bildantraegen).
4. PDF Layout feiner abstimmen (Abstaende, optionale Bildskalierung).

Definition of Done:
- Nutzertests bestaetigen bessere Orientierung und geringere Klickwege.
- Keine regressiven Effekte auf Security und Moderation.

## Phase 4: Deploy, Staging, Monitoring (P2/P3)

Zieldefinition:
- Betrieb auf oeffentlicher Infrastruktur ist nachvollziehbar, messbar und wartbar.

Aufgaben:
1. Staging-Umgebung mit Postgres und realistischen Seed-Daten standardisieren.
2. Runtime Monitoring und Alerting vorbereiten (Fehlerquote, Response-Zeiten, Rate-Limit-Spikes).
3. Backup/Restore Prozess fuer produktive DB dokumentieren.
4. Release-Prozess mit Versionierung und Change-Kommunikation finalisieren.

Definition of Done:
- Staging kann jederzeit neu aufgebaut werden.
- Deploy-Ablauf ist als Checkliste dokumentiert und reproduzierbar.
- Monitoring deckt kritische Betriebsmetriken ab.
```
ZEILEN-ERKLAERUNG
1. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
2. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
3. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
4. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
5. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
6. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
7. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
8. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
9. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
10. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
11. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
12. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
13. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
14. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
15. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
16. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
17. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
18. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
19. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
20. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
21. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
22. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
23. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
24. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
25. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
26. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
27. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
28. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
29. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
30. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
31. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
32. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
33. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
34. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
35. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
36. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
37. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
38. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
39. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
40. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
41. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
42. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
43. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
44. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
45. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
46. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
47. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
48. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
49. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
50. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
51. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
52. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
53. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
54. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
55. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
56. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
57. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
58. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
59. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
60. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
61. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
62. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
63. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
64. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
65. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
66. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.
67. Diese Zeile ist Bestandteil der Datei docs/ROADMAP.md.

## docs/BACKLOG.md

`$lang
# MealMate Backlog

Dieses Backlog ist nach Prioritaet gruppiert und enthaelt konkrete Akzeptanzkriterien.

## P0 Blocker

### Karte P0-1: Playwright E2E in allen Dev-Setups sicher ausfuehrbar

Problem:
- E2E Tests werden ohne lokale Browser-Installation uebersprungen und koennen dadurch leicht vergessen werden.

Loesungsidee:
- Dev-Onboarding mit Pflichtschritt fuer `playwright install chromium` im Runbook verankern und per CI-Job erzwingen.

Akzeptanzkriterien:
- Ein CI-Job laeuft regelmaessig mit aktivem Browser und fuehrt E2E Tests aus.
- Lokale Fehlermeldung verweist klar auf fehlende Installation.

Tests:
- `pytest -q tests/e2e/test_user_admin_journey.py`

### Karte P0-2: Admin-Moderation bei gleichzeitigen Aktionen race-safe haerten

Problem:
- Gleichzeitige Approve/Reject Requests koennen zu inkonsistenten Statuswechseln fuehren, wenn Transaktionen kollidieren.

Loesungsidee:
- Statuswechsel mit expliziter optimistic oder pessimistic Sperrstrategie absichern.

Akzeptanzkriterien:
- Doppelte Approve/Reject Requests erzeugen keinen doppelten Publish.
- Konflikte liefern klaren `409` statt stiller Inkonsistenz.

Tests:
- Neue API-Tests mit parallelen Requests fuer denselben Submission- oder Image-Change-Datensatz.

## P1 Beta

### Karte P1-1: Moderations-Queue Such- und Filterqualitaet verbessern

Problem:
- Bei vielen pending Eintraegen fehlt ein schneller Zugriff auf relevante Datensaetze.

Loesungsidee:
- Filter um Titel- und Einreicher-Suche erweitern und Sorting-Optionen anbieten.

Akzeptanzkriterien:
- Admin kann Queue nach Status, Titel und Einreicher eingrenzen.
- Pagination bleibt korrekt und performant.

Tests:
- API Tests fuer Filterkombinationen plus manuelle QA in Admin-UI.

### Karte P1-2: CSV Import Fehlerrueckmeldungen pro Feld praezisieren

Problem:
- Importfehler sind teilweise nur als generische Zeilenwarnung sichtbar.

Loesungsidee:
- Fehlerobjekte um Feldname und erwartetes Format erweitern.

Akzeptanzkriterien:
- Report zeigt `row`, `field`, `reason`.
- Dry-Run und Real-Run nutzen dasselbe Validierungsmodell.

Tests:
- Unit-Tests fuer Parser und Validierungsreport.

### Karte P1-3: Security Event Auswertung fuer Admin sichtbar machen

Problem:
- Security Events werden gespeichert, sind aber nicht in einer Admin-Ansicht nutzbar.

Loesungsidee:
- Read-only Admin-Ansicht fuer letzte Login-Fehler, Passwort-Resets und relevante Account-Events.

Akzeptanzkriterien:
- Admin sieht paginierte Event-Liste ohne sensible Geheimnisse.
- Retention-Regeln bleiben aktiv.

Tests:
- API + Template Tests fuer Event-Ansicht und Zugriffsschutz.

## P2 Nice-to-have

### Karte P2-1: Discover Performance fuer grosse Datenmenge optimieren

Problem:
- Mit mehreren tausend Rezepten koennen Filterabfragen und Rendering spuerbar langsamer werden.

Loesungsidee:
- Query-Plan pruefen, zusaetzliche Indizes und ggf. aggregierte Materialisierung fuer Rating-Daten einsetzen.

Akzeptanzkriterien:
- Median Antwortzeit fuer Discover unter definierter Schwelle.
- Keine funktionale Regression bei Filtern und Pagination.

Tests:
- Benchmarkscripts plus Regressionstests fuer Filterergebnisse.

### Karte P2-2: Moderationsstatus fuer eigene Einreichungen feiner darstellen

Problem:
- User sehen den Status, aber ohne klaren Verlauf oder Zeitlinie.

Loesungsidee:
- Statushistorie kompakt im Bereich `my-submissions` darstellen.

Akzeptanzkriterien:
- User erkennen Pending/Approved/Rejected inkl. Zeit und Admin-Notiz.

Tests:
- Template Tests fuer Statusdarstellung.

## P3 Spaeter gross

### Karte P3-1: Objekt-Storage fuer Bilder statt DB-BLOBs

Problem:
- BLOB-Speicherung in der DB ist fuer grosse Bildmengen teuer und skaliert schlechter.

Loesungsidee:
- Storage-Adapter einfuehren und auf S3-kompatibles Backend migrieren.

Akzeptanzkriterien:
- Bildzugriff bleibt API-kompatibel.
- Migrationstool uebernimmt bestehende DB-Bilder in Object Storage.

Tests:
- Integrations-Tests mit Storage-Mock und Migrations-Tests.

### Karte P3-2: Vollwertige asynchrone Jobs fuer Import/PDF/Bildverarbeitung

Problem:
- Schwere Operationen laufen aktuell request-nah und koennen unter Last bremsen.

Loesungsidee:
- Hintergrundjobs mit Queue-System einfuehren.

Akzeptanzkriterien:
- Import und Bildverarbeitung laufen robust asynchron.
- UI zeigt Jobstatus und Ergebnisreport.

Tests:
- Worker-Tests, Retry-Tests und End-to-End Jobflow-Tests.
```
ZEILEN-ERKLAERUNG
1. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
2. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
3. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
4. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
5. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
6. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
7. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
8. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
9. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
10. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
11. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
12. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
13. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
14. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
15. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
16. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
17. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
18. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
19. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
20. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
21. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
22. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
23. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
24. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
25. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
26. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
27. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
28. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
29. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
30. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
31. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
32. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
33. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
34. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
35. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
36. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
37. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
38. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
39. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
40. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
41. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
42. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
43. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
44. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
45. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
46. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
47. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
48. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
49. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
50. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
51. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
52. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
53. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
54. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
55. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
56. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
57. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
58. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
59. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
60. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
61. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
62. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
63. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
64. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
65. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
66. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
67. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
68. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
69. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
70. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
71. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
72. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
73. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
74. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
75. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
76. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
77. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
78. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
79. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
80. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
81. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
82. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
83. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
84. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
85. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
86. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
87. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
88. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
89. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
90. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
91. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
92. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
93. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
94. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
95. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
96. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
97. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
98. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
99. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
100. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
101. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
102. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
103. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
104. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
105. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
106. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
107. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
108. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
109. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
110. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
111. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
112. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
113. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
114. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
115. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
116. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
117. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
118. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
119. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
120. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
121. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
122. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
123. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
124. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
125. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
126. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
127. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
128. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
129. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
130. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
131. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
132. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
133. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
134. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
135. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
136. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
137. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
138. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
139. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
140. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
141. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
142. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
143. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
144. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.
145. Diese Zeile ist Bestandteil der Datei docs/BACKLOG.md.

## docs/ARCHITECTURE.md

`$lang
# MealMate Architecture

Diese Datei beschreibt den aktuellen technischen Aufbau auf Basis des implementierten Codes.

## 1) Systemueberblick

MealMate ist eine server-rendered FastAPI Webanwendung:
1. Browser sendet Requests an FastAPI.
2. Router liefern HTML (Jinja2) oder API/Datei-Responses.
3. HTMX aktualisiert gezielte UI-Teile ohne SPA-Framework.
4. SQLAlchemy mappt auf relationale Tabellen, Migrationen laufen ueber Alembic.

## 2) Request Flow (Browser -> FastAPI -> Templates/HTMX)

1. Request trifft auf Middleware-Kette:
   - `RequestContextMiddleware`
   - `SecurityHeadersMiddleware`
   - `HTTPSRedirectMiddleware`
   - `CSRFMiddleware`
   - `LanguageMiddleware`
   - `SlowAPIMiddleware`
2. Auth und Rollen werden per Dependencies auf Routenebene erzwungen.
3. Jinja Templates rendern Vollseiten oder Partials.
4. HTMX Requests aktualisieren z. B. Favorite-Button, Discover-Liste oder Bild-Sections.

## 3) Auth Flow (JWT Cookie + CSRF)

1. Login erzeugt JWT mit `sub=user_uid` und setzt `access_token` als `HttpOnly` Cookie.
2. `get_current_user_optional` liest Cookie/Header, validiert Token und laedt User.
3. CSRF Middleware setzt `csrf_token` Cookie bei sicheren Methoden.
4. Bei POST/PUT/PATCH/DELETE wird Header/Form-Token gegen Cookie geprueft.
5. Logout loescht den Auth-Cookie.

## 4) Moderation Flow (Submission -> Pending -> Admin -> Published)

1. User/Gast reicht ueber `/submit` ein.
2. Datensatz landet in `recipe_submissions` mit Status `pending`.
3. Admin sieht Queue unter `/admin/submissions`.
4. Approve erstellt publiziertes `recipes` Objekt (inkl. Zutaten/Bilder-Transfer).
5. Reject setzt Status `rejected` und speichert `admin_note`.
6. Discover zeigt ausschliesslich `recipes.is_published=True`.

## 5) Bild Flow (Primary DB, URL, Placeholder, Change Request)

1. Anzeige priorisiert:
   - Primary `recipe_images`
   - `source_image_url` oder `title_image_url`
   - Placeholder
2. Admin kann Bilder direkt fuer Rezept setzen oder loeschen.
3. Normaler User kann nur `recipe_image_change_requests` erzeugen.
4. Admin moderiert Bildaenderungen in separater Queue.
5. Bei Approve wird neues Bild als Primary in `recipe_images` abgelegt.

## 6) Datenbankschema (Uebersicht)

Wichtige Kernobjekte:
1. `users` fuer Accounts, Rollen, Username, `user_uid` und Login-Metadaten.
2. `recipes` fuer publizierte Rezepte mit `is_published` und Source-Metadaten.
3. `recipe_submissions` fuer moderationspflichtige Einreichungen.
4. `recipe_images` fuer direkte Rezeptbilder.
5. `recipe_image_change_requests` + `recipe_image_change_files` fuer Bildmoderation.
6. `reviews`, `favorites`, `ingredients`, `recipe_ingredients` fuer Interaktion und Normalisierung.
7. `password_reset_tokens` und `security_events` fuer Recovery und Security-Audit.

## 7) Modulaufteilung

1. `app/main.py`:
   - App-Bootstrap, Middleware, Router-Registrierung, Fehlerhandler, Healthchecks.
2. `app/routers/`:
   - `auth.py`, `recipes.py`, `submissions.py`, `admin.py` mit Business-Endpunkten.
3. `app/services.py` und `app/csv_import.py`:
   - Import-, Normalisierungs- und Transferlogik.
4. `app/security.py`, `app/middleware.py`, `app/rate_limit.py`:
   - Sicherheits- und Limiting-Kern.
5. `app/templates/` + `app/static/`:
   - UI-Struktur und Frontend-Verhalten.
6. `alembic/`:
   - Schema-Migrationen.
7. `tests/`:
   - API/Unit und E2E Testabdeckung.

## 8) Ordnerstruktur (vereinfacht)

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

## 9) Mini-Tools fuer Architekturtransparenz

1. `python -m tools.print_routes`:
   - Gibt alle FastAPI-Routen als Markdown-Tabelle aus.
2. `python -m tools.dump_db_schema`:
   - Gibt Tabellen und Spalten aus `Base.metadata` als Markdown aus.
```
ZEILEN-ERKLAERUNG
1. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
2. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
3. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
4. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
5. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
6. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
7. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
8. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
9. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
10. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
11. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
12. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
13. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
14. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
15. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
16. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
17. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
18. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
19. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
20. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
21. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
22. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
23. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
24. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
25. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
26. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
27. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
28. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
29. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
30. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
31. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
32. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
33. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
34. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
35. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
36. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
37. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
38. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
39. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
40. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
41. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
42. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
43. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
44. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
45. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
46. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
47. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
48. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
49. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
50. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
51. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
52. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
53. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
54. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
55. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
56. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
57. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
58. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
59. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
60. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
61. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
62. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
63. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
64. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
65. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
66. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
67. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
68. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
69. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
70. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
71. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
72. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
73. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
74. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
75. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
76. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
77. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
78. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
79. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
80. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
81. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
82. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
83. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
84. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
85. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
86. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
87. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
88. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
89. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
90. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
91. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
92. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
93. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
94. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
95. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
96. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
97. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
98. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
99. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
100. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
101. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
102. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
103. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
104. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
105. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.
106. Diese Zeile ist Bestandteil der Datei docs/ARCHITECTURE.md.

## CHANGELOG.md

`$lang
# Changelog

Alle nennenswerten Aenderungen an MealMate werden hier dokumentiert.

## [Unreleased]

### Added
- Moderationsworkflow fuer Rezepteinreichungen mit Pending/Approve/Reject.
- Bildaenderungs-Moderation mit separater Admin-Queue.
- PDF Download pro Rezept.
- Auth-Verbesserungen mit Username-Login, Passwort-Recovery und E-Mail-Aenderung per Token.
- i18n Basis mit `de`, `en`, `fr` und Sprachaufloesung ueber Query/Cookie/Header.
- Playwright-basierte E2E Test-Suite unter `tests/e2e/`.
- Mini-Tools `tools.print_routes` und `tools.dump_db_schema`.

### Changed
- Discover zeigt nur publizierte Rezepte.
- Direkte Rezeptveroeffentlichung ist auf Admin begrenzt.
- Bildanzeige nutzt Fallback DB-Bild -> externe URL -> Placeholder.
- Security Header um konfigurierbares `CSP_IMG_SRC` erweitert.

### Fixed
- Publish-Bug korrigiert, damit User/Gast-Rezepte nicht mehr direkt live gehen.
- Moderations- und Sicherheitsregeln mit zusaetzlichen Tests abgesichert.

## [0.1.0-beta] (geplant)

### Zielbild
- Oeffentliche Beta mit stabilen User- und Admin-Flows.
- Reproduzierbarer Deploy auf Postgres-Umgebung.
- Vollstaendige QA-Abnahme gemaess `docs/QA_BETA_CHECKLIST.md`.
```
ZEILEN-ERKLAERUNG
1. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
2. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
3. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
4. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
5. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
6. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
7. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
8. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
9. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
10. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
11. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
12. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
13. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
14. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
15. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
16. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
17. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
18. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
19. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
20. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
21. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
22. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
23. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
24. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
25. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
26. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
27. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
28. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
29. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
30. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.
31. Diese Zeile ist Bestandteil der Datei CHANGELOG.md.

## tools/__init__.py

`$lang
"""Utility scripts package for project introspection commands."""
```
ZEILEN-ERKLAERUNG
1. Diese Zeile ist Bestandteil der Datei tools/__init__.py.

## tools/print_routes.py

`$lang
from __future__ import annotations

from collections.abc import Iterable

from fastapi.routing import APIRoute

from app.main import app


def _iter_dependency_calls(route: APIRoute) -> Iterable[object]:
    stack = list(route.dependant.dependencies)
    while stack:
        dependency = stack.pop()
        if dependency.call is not None:
            yield dependency.call
        stack.extend(dependency.dependencies)


def _is_admin_only(route: APIRoute) -> bool:
    for call in _iter_dependency_calls(route):
        name = getattr(call, "__name__", "")
        if name == "get_admin_user":
            return True
    return False


def _format_tags(route: APIRoute) -> str:
    if not route.tags:
        return "-"
    return ", ".join(str(tag) for tag in route.tags)


def _iter_route_rows() -> Iterable[tuple[str, str, str, str, str]]:
    collected: list[tuple[str, str, str, str, str]] = []
    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue
        methods = sorted(method for method in route.methods or set() if method not in {"HEAD", "OPTIONS"})
        tags = _format_tags(route)
        admin_only = "yes" if _is_admin_only(route) else "no"
        for method in methods:
            collected.append((method, route.path, route.name, tags, admin_only))
    collected.sort(key=lambda item: (item[1], item[0]))
    return collected


def main() -> None:
    print("| METHOD | PATH | NAME | TAGS | ADMIN_ONLY |")
    print("|---|---|---|---|---|")
    for method, path, name, tags, admin_only in _iter_route_rows():
        print(f"| {method} | {path} | {name} | {tags} | {admin_only} |")


if __name__ == "__main__":
    main()
```
ZEILEN-ERKLAERUNG
1. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
2. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
3. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
4. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
5. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
6. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
7. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
8. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
9. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
10. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
11. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
12. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
13. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
14. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
15. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
16. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
17. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
18. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
19. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
20. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
21. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
22. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
23. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
24. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
25. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
26. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
27. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
28. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
29. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
30. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
31. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
32. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
33. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
34. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
35. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
36. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
37. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
38. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
39. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
40. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
41. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
42. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
43. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
44. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
45. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
46. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
47. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
48. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
49. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
50. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
51. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
52. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
53. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
54. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.
55. Diese Zeile ist Bestandteil der Datei tools/print_routes.py.

## tools/dump_db_schema.py

`$lang
from __future__ import annotations

from sqlalchemy import Table

from app import models  # noqa: F401
from app.database import Base


def _column_type(column) -> str:
    try:
        return str(column.type)
    except Exception:
        return column.type.__class__.__name__


def _foreign_keys(column) -> str:
    if not column.foreign_keys:
        return "-"
    targets = sorted(fk.target_fullname for fk in column.foreign_keys)
    return ", ".join(targets)


def _print_table(table: Table) -> None:
    print(f"## {table.name}")
    print()
    print("| COLUMN | TYPE | NULLABLE | PK | FK |")
    print("|---|---|---|---|---|")
    for column in table.columns:
        name = column.name
        ctype = _column_type(column)
        nullable = "yes" if column.nullable else "no"
        primary = "yes" if column.primary_key else "no"
        foreign = _foreign_keys(column)
        print(f"| {name} | {ctype} | {nullable} | {primary} | {foreign} |")
    print()


def main() -> None:
    print("# Database Schema")
    print()
    tables = sorted(Base.metadata.tables.values(), key=lambda item: item.name)
    for table in tables:
        _print_table(table)


if __name__ == "__main__":
    main()
```
ZEILEN-ERKLAERUNG
1. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
2. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
3. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
4. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
5. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
6. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
7. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
8. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
9. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
10. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
11. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
12. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
13. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
14. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
15. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
16. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
17. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
18. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
19. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
20. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
21. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
22. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
23. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
24. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
25. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
26. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
27. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
28. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
29. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
30. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
31. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
32. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
33. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
34. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
35. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
36. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
37. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
38. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
39. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
40. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
41. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
42. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
43. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
44. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
45. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
46. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.
47. Diese Zeile ist Bestandteil der Datei tools/dump_db_schema.py.


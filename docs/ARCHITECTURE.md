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

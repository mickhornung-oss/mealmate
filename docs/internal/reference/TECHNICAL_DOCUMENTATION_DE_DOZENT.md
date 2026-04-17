# Kitchen Hell and Heaven  
## Technische Projektdokumentation

### Dokumentmetadaten
| Feld | Wert |
|---|---|
| Projektname | Kitchen Hell and Heaven |
| Version / Stand | Code- und Teststand gemäß Repository-Analyse |
| Datum | 2026-03-05 |
| Autor | Technische Ausarbeitung (Codex, aus Quellcode abgeleitet) |
| Zielgruppe | Dozent:innen, Entwickler:innen, QA-/Security-Engineers |

---

# 1 Projektübersicht

Kitchen Hell and Heaven ist eine serverseitig gerenderte Webanwendung zur Erfassung, Moderation, Veröffentlichung und Verwaltung von Kochrezepten.
Die Anwendung kombiniert klassische HTML-Seiten (Jinja2) mit HTMX-Interaktionen für partielle Updates, wodurch ein leichtgewichtiges Web-UI ohne großes Frontend-Framework realisiert wird.

Die funktionalen Schwerpunkte sind:

- rollenbasiertes Authentifizierungs- und Autorisierungssystem (Guest/User/Admin)
- moderierter Veröffentlichungsprozess für nutzergenerierte Inhalte
- Bildverwaltung mit Upload, Fallback-Strategie und Bild-Moderation
- Übersetzungsinfrastruktur für Rezeptinhalte (de/en/fr) mit Admin-Werkzeugen
- Sicherheits-Hardening für CSRF, Header, Uploads, Redirects und Fehlerbehandlung
- durchgängige automatisierte Testabdeckung (Funktionalität + Security + Regression)

Architekturziele:

- sichere Benutzerinteraktion
- moderierte Inhalte
- internationalisierte Oberfläche
- automatisierte Tests
- robuste Backend-Struktur

---

# 2 Technologie-Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic

## Frontend

- Jinja2 Templates
- HTMX
- CSS

## Datenbank

- SQLite (lokale Entwicklungsumgebung)
- PostgreSQL-fähig über SQLAlchemy-URL-Mapping (`postgresql+psycopg`)

## Testing

- pytest
- pytest-asyncio
- Playwright (E2E optional)

## Verwendete Kernbibliotheken (aus `requirements.txt`)

| Bereich | Bibliothek |
|---|---|
| ASGI Server | uvicorn, gunicorn |
| Auth/JWT | python-jose |
| Passwort-Hashing | pwdlib, argon2-cffi |
| Rate Limiting | slowapi |
| HTTP Client | httpx |
| PDF | reportlab |
| Bildverarbeitung | pillow |
| Parsing/Import | beautifulsoup4 |
| Übersetzung | translators |

---

# 3 Projektstruktur

```text
Schnittstellen und APIs/Abschluss Projekt/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ database.py
│  ├─ middleware.py
│  ├─ dependencies.py
│  ├─ models.py
│  ├─ translation_models.py
│  ├─ security.py
│  ├─ rate_limit.py
│  ├─ services.py
│  ├─ translation_service.py
│  ├─ translation_provider.py
│  ├─ i18n/
│  │  ├─ middleware.py
│  │  ├─ service.py
│  │  └─ locales/{de,en,fr}.json
│  ├─ routers/
│  │  ├─ auth.py
│  │  ├─ recipes.py
│  │  ├─ submissions.py
│  │  ├─ admin.py
│  │  ├─ translations.py
│  │  └─ legal.py
│  ├─ templates/
│  │  ├─ base.html
│  │  ├─ home.html
│  │  ├─ admin*.html
│  │  ├─ auth_*.html
│  │  └─ partials/*.html
│  └─ static/
│     ├─ style.css
│     ├─ security.js
│     └─ htmx.min.js
├─ alembic/
│  ├─ env.py
│  └─ versions/*.py
├─ tests/
│  ├─ conftest.py
│  ├─ test_*.py
│  └─ e2e/*.py
└─ docs/
   └─ *.md
```

Kurzerläuterung:

- `app/`: Laufzeitcode der Anwendung.
- `app/routers/`: HTTP-Endpunkte je Domänenbereich.
- `app/services*.py`: Geschäftslogik, Import, Kategorien, Hilfslogik.
- `app/translation_*.py`: Provider-Abstraktion und Übersetzungsorchestrierung.
- `app/i18n/`: UI-Lokalisierung und Sprachauflösung.
- `app/templates/`: serverseitiges Rendering.
- `app/static/`: CSS/JS/Assets.
- `alembic/`: Schema-Versionierung.
- `tests/`: Unit-, Integrations-, Security- und E2E-Tests.
- `docs/`: technische und organisatorische Projektdokumente.

---

# 4 Systemarchitektur

Die Anwendung ist als modulare, serverseitige Webarchitektur aufgebaut und trennt klar zwischen HTTP-Ebene, Domänenlogik, Persistenz und Darstellung.

## Schichtenmodell

1. Router Layer  
   Verantwortlich für Request-Validierung, Response-Typ, Zugriffskontrolle und Zusammensetzen des Seitentextkontexts.

2. Service Layer  
   Verantwortlich für domänenspezifische Regeln (z. B. Moderationsfreigaben, Übersetzungsqueue, Kategorisierung, Importvalidierung).

3. Persistence Layer  
   SQLAlchemy-Modelle plus Sessions/Transactions; Alembic für kontrollierte Schema-Evolution.

4. Presentation Layer  
   Jinja2-Templates und Partials; HTMX für punktuelle Teilaktualisierung ohne SPA-Architektur.

## Datenfluss (vereinfachter Request-Flow)

```text
Browser / HTMX
   ↓
FastAPI Router
   ↓
Dependencies (Auth, Admin-Gates, CSRF, i18n, Rate-Limit)
   ↓
Service Layer
   ↓
SQLAlchemy ORM / Session
   ↓
SQLite (lokal) / PostgreSQL (produktionsfähig)
   ↓
Jinja2 Response oder JSON Response
```

---

# 5 HTTP-Routing

Die Router werden zentral in `app/main.py` registriert:

- `auth.router`
- `recipes.router`
- `submissions.router`
- `admin.router`
- `translations.router`
- `legal.router`

## Router-Aufgaben

| Router | Aufgabe | Typische Pfade |
|---|---|---|
| Auth Router (`auth.py`) | Anmeldung, Registrierung, Session/Cookie, Profil, Passwort- und E-Mail-Recovery | `/login`, `/register`, `/logout`, `/auth/*`, `/me` |
| Recipe Router (`recipes.py`) | Discover, Rezept-CRUD, Favoriten, Reviews, PDF, Bildzugriff, Kategorien-API | `/`, `/recipes/*`, `/favorites`, `/images/*`, `/categories` |
| Submission Router (`submissions.py`) | Einreichungen und Moderation von Nutzer-Rezepten | `/submit`, `/my-submissions`, `/admin/submissions/*` |
| Admin Router (`admin.py`) | Admin-Dashboard, CSV-Import, Kategorie-Aufräumen, Bildänderungs-Moderation | `/admin`, `/admin/import-*`, `/admin/categories*`, `/admin/image-change-*` |
| Translation Router (`translations.py`) | Übersetzungs-Admin, Queue/Batch, Testübersetzung, Audit/Reparatur DE | `/admin/translations*` |
| Legal Router (`legal.py`) | Rechtstexte | `/impressum`, `/copyright` |

Hinweis: Die API-Dokumentation ist FastAPI-typisch verfügbar (sofern deploymentseitig nicht deaktiviert).

---

# 6 Authentifizierung und Autorisierung

## Rollenmodell

- Guest: nicht authentifiziert
- User: authentifizierter Standardnutzer
- Admin: erweiterte Verwaltungs- und Publikationsrechte

## Authentifizierung

- Login über E-Mail oder Username (serverseitige Identifier-Logik).
- JWT wird als HttpOnly-Cookie (`access_token`) gesetzt.
- Passwort-Hashing via Argon2 (`pwdlib`/`argon2-cffi`).

## CSRF-Schutz

- CSRF-Token-Cookie (konfigurierbarer Name, default `csrf_token`).
- Header-Validierung (`X-CSRF-Token`) für alle state-changing Methoden.
- Formular-Token-Unterstützung für klassische POST-Formularflüsse.
- HTMX wird über `security.js` mit CSRF-Headern versorgt.

## Session- und Recovery-Flows

- Passwort vergessen / Reset über zeitlich begrenzte, gehashte Token (`password_reset_tokens`).
- E-Mail-Änderung via Bestätigungslink und Tokenfluss.
- Passwortänderung mit Old/New-Validierung.
- Logout räumt Auth-Cookie serverseitig sauber ab.

## Autorisierung (serverseitig)

- Guards über Dependencies (`get_current_user`, `get_admin_user`).
- Admin-Endpunkte sind backendseitig geschützt, nicht nur UI-seitig ausgeblendet.
- Publishing-Rechte sind auf Adminpfade fokussiert; User/Guest gehen über Moderation.

---

# 7 Rezeptsystem

## Kernfunktionen

- Rezept anlegen
- Rezept anzeigen
- Rezept bearbeiten
- Rezept löschen

## Discover / Listing

- Filter: Titel, Kategorie (kanonisch), Schwierigkeit, Zutat, Bildfilter.
- Sortierung: Datum, Zubereitungszeit, Bewertung.
- Pagination mit validierten Grenzen.
- HTMX-Teilupdates für performante Listeninteraktion.

## Fachfeatures

- Favoriten pro User (Unique-Constraint auf User/Recipe).
- Reviews pro User und Rezept (eine Bewertung pro Nutzer/Rezept).
- PDF-Export pro Rezept (`/recipes/{id}/pdf`), mit eingebettetem DB-Bild wenn vorhanden.

## Kategorien

- Rohkategorie (`recipes.category`) bleibt erhalten.
- Kanonische Kategorie (`recipes.canonical_category`) steuert UI/Filter.
- Mapping-/Heuristik-Logik für Normalisierung plus Admin-Rebuild.

---

# 8 Moderationssystem

Moderation ist ein zentrales Sicherheits- und Qualitätskonzept.

## Rezept-Einreichungen

```text
Guest/User -> /submit -> recipe_submissions(status=pending)
Admin      -> prüft Queue -> approve/reject
approve    -> erstellt veröffentlichtes Rezept in recipes
reject     -> bleibt unveröffentlicht + admin_note
```

## Bildänderungen

```text
User schlägt Bild vor -> recipe_image_change_requests(status=pending)
Admin prüft Vorschlag -> approve/reject
approve -> Bild wird als recipe_images primary übernommen
```

## Admin-Entscheidungen

- Approve
- Reject (mit Begründung)
- Edit-Schritt vor Freigabe möglich (je nach Workflow-Kontext)

Zustände (implementiert): `pending`, `approved`, `rejected`.

---

# 9 Bildsystem

## Bildquellen und Fallback

Reihenfolge in der Darstellung:

1. Primärbild aus DB (`recipe_images`, `is_primary=True`)
2. Externe URL (`source_image_url`/`title_image_url`)
3. Placeholder

## Upload und Validierung

- MIME-Allowlist (konfigurierbar)
- Magic-Bytes-Prüfung (Dateisignatur)
- PIL-Decode/Format-Prüfung
- Größenlimit (`MAX_UPLOAD_MB`)
- serverseitige Dateinamensanitization

## Zugriff

- Bilder aus DB werden über dedizierte Image-Endpunkte ausgeliefert.
- CSP `img-src` ist konfigurierbar (`CSP_IMG_SRC`) und unterstützt externe Bildquellen kontrolliert.

---

# 10 Internationalisierung

## Unterstützte UI-Sprachen

- Deutsch (`de`)
- Englisch (`en`)
- Französisch (`fr`)

## i18n-Komponenten

- Locale-Middleware mit Priorität: Query `lang` -> Cookie -> Accept-Language -> Default `de`.
- Dictionary-Übersetzungen aus JSON-Dateien (`app/i18n/locales/*.json`).
- Jinja-Helper `t(...)` für Template-Texte.

## Rezept-Übersetzungen (Content-Level)

- Persistenz in `recipe_translations`.
- Source-Hash zur Erkennung veralteter Übersetzungen.
- Queue- und Batch-Läufe über Admin-Module.
- Diagnose- und Reparaturpfade für DE-Qualität (`quality_flag`, Audit/Repair-Routen).

---

# 11 Sicherheit

## Sicherheitsmechanismen

- CSRF-Schutz für state-changing Requests.
- JWT-Cookie-Auth mit HttpOnly/SameSite/Secure (env-abhängig).
- Rate-Limits über SlowAPI auf kritischen Endpunkten.
- TrustedHost-/Proxy-Unterstützung für Deployment hinter Reverse Proxy.
- Upload-Härtung gegen Content-Type-Spoofing.
- Open-Redirect-Schutz über sichere Redirect-Pfadvalidierung.

## Security Header (aktiv gesetzt)

| Header | Zweck |
|---|---|
| `Content-Security-Policy` | Ressourcenrestriktion inkl. `img-src` |
| `X-Frame-Options: DENY` | Clickjacking-Schutz |
| `X-Content-Type-Options: nosniff` | MIME-Sniffing-Verhinderung |
| `Referrer-Policy` | Referrer-Datenminimierung |
| `Permissions-Policy` | Browser-Feature-Einschränkung |
| `Strict-Transport-Security` | nur in HTTPS/Prod-Kontext |

## Fehlerbehandlung ohne Leak

- 500-Fehler liefern in Prod einen generischen Fehlertext statt Stacktrace.
- Stacktraces werden geloggt, aber nicht an Clients ausgeliefert.
- Security Header bleiben auch bei Fehlerantworten erhalten.

---

# 12 Datenbank und Migration

## ORM

- SQLAlchemy mit deklarativen Modellen (`app/models.py`, `app/translation_models.py`).
- Session-Management über zentrale DB-Schicht (`app/database.py`).

## Migration Tool

- Alembic
- Migrations in `alembic/versions/`

## Migrationstatus

- Verifiziert: `current == head == 20260304_0016`

## Datenmodell (Auszug fachlich relevanter Tabellen)

| Tabelle | Zweck |
|---|---|
| `users` | Accounts, Rollen, UID, Login-Metadaten |
| `recipes` | veröffentlichte Rezepte, Kategorie, Quelle, Sichtbarkeit |
| `recipe_submissions` | Moderations-Warteschlange für Einreichungen |
| `recipe_images` | Binärbilder zu Rezepten |
| `recipe_image_change_requests` | Moderation für Bildänderungen |
| `reviews` / `favorites` | Interaktionen pro User/Rezept |
| `password_reset_tokens` | Recovery- und E-Mail-Change-Tokenfluss |
| `security_events` | minimale Security-Audit-Events |
| `recipe_translations` | übersetzte Rezeptinhalte pro Sprache |
| `translation_batch_jobs` | Batch-Job-Status für externe Übersetzungen |
| `category_mappings` | kanonische Kategorien-Regeln |

---

# 13 Teststrategie

## Testframework

- pytest als zentrales Framework für Unit-, Integrations-, Security- und E2E-nahe Tests.

## Automatisierte Testbereiche

- QA-Roundup
- Security AuthZ
- CSRF/Cookie
- Upload Validation
- PDF Security
- i18n/XSS
- Search Validation
- Session Hygiene
- Redirect/Origin/Host
- Rate Limits effektiv
- Error Leak Tests
- Migration Safety
- Validation Abuse
- Moderation/Translation/Kategorie-spezifische Suiten
- E2E Smoke/Journey (Playwright-basiert, optional)

## Aktueller Status (verifiziert)

- Tests total: 133  
- Passed: 133  
- Failed: 0

## Warnings

- 11 -> 5 reduziert
- ResourceWarnings wurden bereinigt
- verbleibend: DeprecationWarnings (Alembic / SQLAlchemy)

---

# 14 Deployment und Ausführung

## Anwendung starten

```bash
py -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
```

## Tests ausführen

```bash
py -m pytest -q
```

## Migrationen prüfen

```bash
py -m alembic -c alembic.ini current
py -m alembic -c alembic.ini heads
```

Hinweis: Für Produktionsbetrieb sind ENV-Variablen (`APP_ENV=prod`, `SECRET_KEY`, `DATABASE_URL`, Cookie-/HTTPS-Settings, Mail/Translation-Keys) konsistent zu setzen.

---

# 15 Bekannte technische Punkte

- DeprecationWarnings aus Drittbibliotheken (insb. Alembic-Konfigurationspfadtrennung und SQLite-Datetime-Adapter in SQLAlchemy unter Python 3.14) bestehen weiterhin.
- Diese Warnungen sind aktuell nicht funktional blockerisch, sollten aber bei künftigen Dependency-Upgrades adressiert werden.
- Für robuste Produktionseinführung ist ein kontrollierter Upgrade-Pfad der Dependencies empfehlenswert (staging-first, warnings as errors optional in CI).

---

# 16 Zusammenfassung

Kitchen Hell and Heaven liegt als technisch sauber segmentierte FastAPI-Anwendung mit klarer Trennung von Router-, Service-, Persistenz- und Template-Ebene vor.
Die Plattform kombiniert moderierte Content-Workflows, robuste Security-Kontrollen, i18n plus Rezept-Übersetzungsinfrastruktur und umfassende automatisierte Tests.
Der derzeitige Regressionstand ist stabil (133/133 Tests grün), Migrationen sind synchron (`current == head`), und zentrale Hardening-Maßnahmen (CSRF, Header, Upload-Validierung, Error-Leak-Schutz) sind im Code verankert.
Damit ist eine belastbare Grundlage für weitere Iterationen in Richtung Deployment, Monitoring und didaktische Demonstration der Architektur vorhanden.

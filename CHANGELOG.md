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

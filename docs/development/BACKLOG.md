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

# Block 16 - Release Governance & Ship (Finaler Release-Cut)

Datum: 2026-04-17  
Status: Abgeschlossen (gruen, tag-ready)

## Ziel des Blocks
Finalen veroeffentlichungsfaehigen Zustand herstellen (kein weiterer Refactoring-Block):
1. Versioning und Release-Identitaet finalisieren
2. Changelog auf realen Stand bringen
3. Release-Governance und Release-Checklist verbindlich machen
4. Public-README final schaerfen
5. Repo-Sanity fuer finalen Release-Cut absichern
6. Vollvalidierung fuer Tag-Ready Zustand

## Umgesetzte Aenderungen

### 1) Versioning / Release-Identitaet
- Zielversion als erster stabiler Release gesetzt: `v1.0.0`.
- README explizit auf `v1.0.0` mit Release-Status ausgerichtet.
- FastAPI-App-Version bleibt konsistent bei `1.0.0` (bereits vorhanden, unveraendert).

### 2) Changelog (pflicht) erneuert
Datei:
- `CHANGELOG.md`

Umsetzung:
- auf Englisch konsolidiert
- Release-Eintrag fuer `v1.0.0` mit strukturierten Sektionen:
  - Added
  - Changed
  - Fixed
  - Internal
- Inhalte basieren auf den realen Audit-/Hardening-Bloecken 00-15.

### 3) Release Governance eingefuehrt
Neu:
- `docs/development/RELEASE.md`

Inhalte:
- SemVer-Regeln
- verbindlicher Release-Ablauf
- Definition, was als Release gilt
- Regeln fuer zukuenftige Releases und operative Mindestkanten

### 4) Release-Checklist eingefuehrt
Neu:
- `docs/development/RELEASE_CHECKLIST.md`

Inhalte:
- harte technische Gates (`compileall`, `pytest`, `-W error`, health, CI)
- Doku-Gates
- Repo-/Config-Hygiene-Gates
- manuelle Smoke-Gates
- expliziter Release-Decision-Checkpoint

### 5) README/Public-Readiness final geschaerft
Datei:
- `README.md`

Umsetzung:
- klare Projektidentitaet und Release-Status
- Quickstart/Config/Quality-Gates klar und kompakt
- Release-Governance-Verweise (Changelog/Release/Checklist)
- bekannte Grenzen knapp und ehrlich dokumentiert

### 6) Docs-Index konsolidiert
Datei:
- `docs/README.md`

Umsetzung:
- Release-Dokumente in den oeffentlichen Dokumentationsindex aufgenommen:
  - `development/RELEASE.md`
  - `development/RELEASE_CHECKLIST.md`

### 7) Testing-Doku auf CI-Realstand gezogen
Datei:
- `docs/development/TESTING.md`

Umsetzung:
- CI-Hinweis auf den realen strict-baseline Lauf korrigiert: `pytest -q -W error`.

### 8) Repo-Sanity-Clean
- lokale DB-/Temp-Artefakte im Root entfernt (`mealmate.db*`, `tmp_dbg.db`).
- `.gitignore`-Abdeckung fuer solche Artefakte bleibt aktiv.

## Reale Verifikation

Ausgefuehrt:
1. `python -m compileall app tests`
2. `pytest -q` -> `169 passed, 4 skipped`
3. `pytest -q -W error` -> `169 passed, 4 skipped`
4. Health-Check via TestClient: `GET /healthz` -> `200 {'status': 'ok'}`

Hinweis:
- Die 4 Skips sind erwartete Playwright-Skips bei lokal fehlenden Browser-Binaries.

## Verhaltensgleichheit
- Keine neuen Features.
- Keine API-Aenderung.
- Keine absichtliche Aenderung zentraler Erfolgspfade.
- Fokus ausschliesslich auf Release-Governance, Release-Artefakte und finalen Publish-Sanity-Stand.

## Ergebnis
Der Repository-Zustand ist als `v1.0.0`-Release-Cut fachlich tag-ready:
- Version identifiziert
- Changelog vorhanden
- Governance + Checklist vorhanden
- Public-Einstieg konsistent
- technische Gates real gruen
